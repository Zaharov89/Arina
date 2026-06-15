import os
import secrets
from datetime import datetime, timedelta

from sqlalchemy import select, text
from sqlalchemy.orm import Session
from werkzeug.security import check_password_hash, generate_password_hash

from Arina.auth.services import ValidationError, sanitize_text, validate_email, validate_password
from Arina.database.models import User


class PasswordResetError(Exception):
    pass


def build_reset_link(token: str) -> str:
    base_url = os.getenv("ARINA_PUBLIC_BASE_URL", "http://localhost:5000").rstrip("/")
    return f"{base_url}/auth/reset-password/{token}"


def send_reset_email(email: str, reset_link: str) -> bool:
    import smtplib
    from email.message import EmailMessage

    smtp_host = os.getenv("ARINA_SMTP_HOST", "").strip()
    smtp_port = int(os.getenv("ARINA_SMTP_PORT", "587"))
    smtp_user = os.getenv("ARINA_SMTP_USER", "").strip()
    smtp_password = os.getenv("ARINA_SMTP_PASSWORD", "")
    smtp_from = os.getenv("ARINA_SMTP_FROM", smtp_user or "arina@example.local").strip()
    smtp_use_tls = os.getenv("ARINA_SMTP_USE_TLS", "true").lower() == "true"

    body = (
        "Здравствуйте!\n\n"
        "Для восстановления пароля в приложении Арина перейдите по ссылке:\n"
        f"{reset_link}\n\n"
        "Если вы не запрашивали восстановление пароля, просто проигнорируйте это письмо.\n"
    )

    if not smtp_host or not smtp_user or not smtp_password:
        print(f"[ARINA AUTH] SMTP не настроен. Ссылка восстановления для {email}: {reset_link}")
        return False

    message = EmailMessage()
    message["Subject"] = "Восстановление пароля в приложении Арина"
    message["From"] = smtp_from
    message["To"] = email
    message.set_content(body)

    with smtplib.SMTP(smtp_host, smtp_port, timeout=15) as smtp:
        if smtp_use_tls:
            smtp.starttls()
        smtp.login(smtp_user, smtp_password)
        smtp.send_message(message)

    return True


def request_password_reset(session: Session, raw_email: str) -> dict:
    email = sanitize_text(raw_email).lower()
    email_error = validate_email(email)
    if email_error:
        raise ValidationError({"email": email_error})

    user = session.scalar(select(User).where(User.email == email))
    if not user:
        return {"email_sent": False, "reset_link_dev": None}

    token = secrets.token_urlsafe(48)
    session.execute(
        text("INSERT INTO arina.password_reset_tokens (user_id, token, is_used, expires_at) VALUES (:user_id, :token, false, :expires_at)"),
        {"user_id": user.id, "token": token, "expires_at": datetime.now() + timedelta(hours=1)},
    )

    reset_link = build_reset_link(token)
    email_sent = send_reset_email(user.email, reset_link)
    return {"email_sent": email_sent, "reset_link_dev": None if email_sent else reset_link}


def validate_new_password(payload: dict) -> str:
    password = str(payload.get("password") or "")
    password_repeat = str(payload.get("password_repeat") or "")
    errors = {}

    password_error = validate_password(password)
    if password_error:
        errors["password"] = password_error

    password_repeat_error = validate_password(password_repeat)
    if password_repeat_error:
        errors["password_repeat"] = password_repeat_error
    elif password != password_repeat:
        errors["password_repeat"] = "Повторите пароль: пароль должен полностью совпадать."

    if errors:
        raise ValidationError(errors)

    return password


def is_old_password(session: Session, user: User, candidate: str) -> bool:
    if check_password_hash(user.password_hash, candidate):
        return True

    rows = session.execute(
        text("SELECT password_hash FROM arina.password_history WHERE user_id = :user_id ORDER BY created_at DESC LIMIT 10"),
        {"user_id": user.id},
    ).mappings()
    return any(check_password_hash(row["password_hash"], candidate) for row in rows)


def keep_last_ten_passwords(session: Session, user_id: int) -> None:
    session.execute(
        text("DELETE FROM arina.password_history WHERE id IN (SELECT id FROM arina.password_history WHERE user_id = :user_id ORDER BY created_at DESC OFFSET 10)"),
        {"user_id": user_id},
    )


def reset_password(session: Session, token: str, payload: dict) -> dict:
    new_password = validate_new_password(payload)
    token_row = session.execute(
        text("SELECT id, user_id, is_used, expires_at FROM arina.password_reset_tokens WHERE token = :token"),
        {"token": token},
    ).mappings().first()

    if not token_row:
        raise PasswordResetError("Ссылка восстановления пароля недействительна.")
    if token_row["is_used"]:
        raise PasswordResetError("Ссылка восстановления пароля уже была использована.")
    if token_row["expires_at"] < datetime.now():
        raise PasswordResetError("Срок действия ссылки восстановления пароля истёк.")

    user = session.get(User, token_row["user_id"])
    if not user:
        raise PasswordResetError("Пользователь не найден.")

    if is_old_password(session, user, new_password):
        raise ValidationError({"password": "Указанный пароль уже использовался ранее."})

    old_password_hash = user.password_hash
    user.password_hash = generate_password_hash(new_password)
    session.execute(text("INSERT INTO arina.password_history (user_id, password_hash) VALUES (:user_id, :password_hash)"), {"user_id": user.id, "password_hash": old_password_hash})
    session.execute(text("UPDATE arina.password_reset_tokens SET is_used = true, used_at = now() WHERE id = :id"), {"id": token_row["id"]})
    keep_last_ten_passwords(session, user.id)

    return {"user_id": user.id, "email": user.email}
