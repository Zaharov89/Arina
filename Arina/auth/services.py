import os
import re
import secrets
import smtplib
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from email.message import EmailMessage

import jwt
from sqlalchemy import select
from sqlalchemy.orm import Session
from werkzeug.security import generate_password_hash

from Arina.database.models import AccountActivationToken, Student, User

NAME_PATTERN = re.compile(r"^[A-Za-zА-Яа-яЁё]{1,60}$")
EMAIL_PATTERN = re.compile(r"^[A-Za-z0-9._%+-]{1,64}@[A-Za-z0-9.-]{1,190}\.[A-Za-z]{2,20}$")
SQL_HTML_DANGEROUS_PATTERN = re.compile(r"[<>{}\[\]`'\";\\]|--|/\*|\*/", re.IGNORECASE)
PASSWORD_DANGEROUS_PATTERN = re.compile(r"[<>{}\[\]`'\";\\]|--|/\*|\*/", re.IGNORECASE)
PASSWORD_HAS_UPPER = re.compile(r"[A-ZА-ЯЁ]")
PASSWORD_HAS_LOWER = re.compile(r"[a-zа-яё]")
PASSWORD_HAS_DIGIT = re.compile(r"\d")
PASSWORD_HAS_SPECIAL = re.compile(r"[^A-Za-zА-Яа-яЁё0-9]")
JWT_ALGORITHM = "HS256"


@dataclass(frozen=True)
class RegistrationData:
    child_first_name: str
    child_last_name: str
    email: str
    password: str
    password_repeat: str


class ValidationError(Exception):
    def __init__(self, field_errors: dict[str, str]):
        super().__init__("Validation failed")
        self.field_errors = field_errors


class EmailAlreadyRegisteredError(Exception):
    pass


class AuthTokenError(Exception):
    pass


def sanitize_text(value: object) -> str:
    return str(value or "").strip()


def has_injection_risk(value: str, password: bool = False) -> bool:
    pattern = PASSWORD_DANGEROUS_PATTERN if password else SQL_HTML_DANGEROUS_PATTERN
    return bool(pattern.search(value))


def validate_name(value: str, field_title: str) -> str | None:
    if not value:
        return f"{field_title}: обязательное поле."
    if has_injection_risk(value):
        return f"{field_title}: запрещены спецсимволы и HTML/SQL-конструкции."
    if not NAME_PATTERN.fullmatch(value):
        return f"{field_title}: только кириллица или латиница, от 1 до 60 символов, без пробелов и спецсимволов."
    return None


def validate_email(value: str) -> str | None:
    if not value:
        return "Почта: обязательное поле."
    if len(value) > 100:
        return "Почта: максимум 100 символов."
    if has_injection_risk(value):
        return "Почта: запрещены HTML/SQL-конструкции и опасные спецсимволы."
    if not EMAIL_PATTERN.fullmatch(value):
        return "Почта: укажите адрес в формате text@example.ru, только латиница."
    return None


def validate_password(value: str) -> str | None:
    if not value:
        return "Пароль: обязательное поле."
    if len(value) < 8 or len(value) > 20:
        return "Пароль: от 8 до 20 символов."
    if has_injection_risk(value, password=True):
        return "Пароль: запрещены символы и конструкции, опасные для SQL/HTML."
    if not PASSWORD_HAS_UPPER.search(value):
        return "Пароль: нужна минимум 1 заглавная буква."
    if not PASSWORD_HAS_LOWER.search(value):
        return "Пароль: нужна минимум 1 строчная буква."
    if not PASSWORD_HAS_DIGIT.search(value):
        return "Пароль: нужна минимум 1 цифра."
    if not PASSWORD_HAS_SPECIAL.search(value):
        return "Пароль: нужен минимум 1 спецсимвол."
    return None


def parse_registration_payload(payload: dict) -> RegistrationData:
    return RegistrationData(
        child_first_name=sanitize_text(payload.get("child_first_name")),
        child_last_name=sanitize_text(payload.get("child_last_name")),
        email=sanitize_text(payload.get("email")).lower(),
        password=str(payload.get("password") or ""),
        password_repeat=str(payload.get("password_repeat") or ""),
    )


def validate_registration_data(data: RegistrationData) -> None:
    errors = {}

    child_first_name_error = validate_name(data.child_first_name, "Имя ребёнка")
    if child_first_name_error:
        errors["child_first_name"] = child_first_name_error

    child_last_name_error = validate_name(data.child_last_name, "Фамилия ребёнка")
    if child_last_name_error:
        errors["child_last_name"] = child_last_name_error

    email_error = validate_email(data.email)
    if email_error:
        errors["email"] = email_error

    password_error = validate_password(data.password)
    if password_error:
        errors["password"] = password_error

    password_repeat_error = validate_password(data.password_repeat)
    if password_repeat_error:
        errors["password_repeat"] = password_repeat_error
    elif data.password != data.password_repeat:
        errors["password_repeat"] = "Повторите пароль: пароль должен полностью совпадать."

    if errors:
        raise ValidationError(errors)


def get_jwt_secret() -> str:
    secret = os.getenv("ARINA_JWT_SECRET") or os.getenv("ARINA_SECRET_KEY") or "arina-local-dev-secret"
    return secret


def get_access_token_minutes() -> int:
    return int(os.getenv("ARINA_ACCESS_TOKEN_MINUTES", "30"))


def get_refresh_token_days(remember_me: bool = True) -> int:
    if remember_me:
        return int(os.getenv("ARINA_REFRESH_TOKEN_DAYS", "30"))
    return int(os.getenv("ARINA_SESSION_REFRESH_TOKEN_DAYS", "1"))


def get_token_user_id(payload: dict) -> int:
    try:
        return int(payload.get("sub"))
    except (TypeError, ValueError) as error:
        raise AuthTokenError("В токене некорректный id пользователя.") from error


def create_jwt_token(user: User, token_type: str, expires_delta: timedelta) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user.id),
        "email": user.email,
        "type": token_type,
        "is_active": bool(user.is_active),
        "iat": now,
        "exp": now + expires_delta,
        "jti": secrets.token_urlsafe(16),
    }
    return jwt.encode(payload, get_jwt_secret(), algorithm=JWT_ALGORITHM)


def issue_token_pair(user: User, remember_me: bool = True) -> dict:
    if not user.is_active:
        raise AuthTokenError("Пользователь не активирован. Сначала подтвердите почту.")

    refresh_token_days = get_refresh_token_days(remember_me=remember_me)
    access_token = create_jwt_token(user, "access", timedelta(minutes=get_access_token_minutes()))
    refresh_token = create_jwt_token(user, "refresh", timedelta(days=refresh_token_days))

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "Bearer",
        "remember_me": remember_me,
        "access_token_expires_minutes": get_access_token_minutes(),
        "refresh_token_expires_days": refresh_token_days,
    }


def decode_jwt_token(token: str, expected_type: str | None = None) -> dict:
    if not token:
        raise AuthTokenError("Токен не передан.")

    try:
        payload = jwt.decode(token, get_jwt_secret(), algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError as error:
        raise AuthTokenError("Срок действия токена истёк.") from error
    except jwt.InvalidTokenError as error:
        raise AuthTokenError("Токен недействителен.") from error

    token_type = payload.get("type")
    if expected_type and token_type != expected_type:
        raise AuthTokenError(f"Ожидался токен типа {expected_type}, получен {token_type}.")

    return payload


def verify_auth_token(session: Session, token: str) -> dict:
    payload = decode_jwt_token(token, expected_type="access")
    user = session.get(User, get_token_user_id(payload))

    if not user:
        raise AuthTokenError("Пользователь из токена не найден.")
    if not user.is_active:
        raise AuthTokenError("Пользователь не активирован.")

    return {
        "valid": True,
        "user_id": user.id,
        "email": user.email,
        "is_active": user.is_active,
        "token_payload": {
            "type": payload.get("type"),
            "exp": payload.get("exp"),
            "iat": payload.get("iat"),
        },
    }


def refresh_auth_token(session: Session, refresh_token: str, remember_me: bool = True) -> dict:
    payload = decode_jwt_token(refresh_token, expected_type="refresh")
    user = session.get(User, get_token_user_id(payload))

    if not user:
        raise AuthTokenError("Пользователь из refresh-токена не найден.")
    if not user.is_active:
        raise AuthTokenError("Пользователь не активирован.")

    return issue_token_pair(user, remember_me=remember_me)


def create_activation_link(token: str) -> str:
    public_base_url = os.getenv("ARINA_PUBLIC_BASE_URL", "http://localhost:5000").rstrip("/")
    return f"{public_base_url}/auth/activate/{token}"


def send_activation_email(email: str, child_first_name: str, activation_link: str) -> bool:
    smtp_host = os.getenv("ARINA_SMTP_HOST", "").strip()
    smtp_port = int(os.getenv("ARINA_SMTP_PORT", "587"))
    smtp_user = os.getenv("ARINA_SMTP_USER", "").strip()
    smtp_password = os.getenv("ARINA_SMTP_PASSWORD", "")
    smtp_from = os.getenv("ARINA_SMTP_FROM", smtp_user or "arina@example.local").strip()
    smtp_use_tls = os.getenv("ARINA_SMTP_USE_TLS", "true").lower() == "true"

    if not smtp_host or not smtp_user or not smtp_password:
        print(f"[ARINA AUTH] SMTP не настроен. Ссылка подтверждения для {email}: {activation_link}")
        return False

    message = EmailMessage()
    message["Subject"] = "Подтверждение регистрации в приложении Арина"
    message["From"] = smtp_from
    message["To"] = email
    message.set_content(
        f"Здравствуйте!\n\n"
        f"Добро пожаловать в приложение Арина.\n"
        f"Для ребёнка {child_first_name} создана учётная запись.\n\n"
        f"Подтвердите почту, перейдя по ссылке:\n{activation_link}\n\n"
        f"Если вы не регистрировались в приложении, просто проигнорируйте это письмо.\n"
    )

    with smtplib.SMTP(smtp_host, smtp_port, timeout=15) as smtp:
        if smtp_use_tls:
            smtp.starttls()
        smtp.login(smtp_user, smtp_password)
        smtp.send_message(message)

    return True


def register_user(session: Session, payload: dict) -> dict:
    data = parse_registration_payload(payload)
    validate_registration_data(data)

    existing_user = session.scalar(select(User).where(User.email == data.email))
    if existing_user:
        raise EmailAlreadyRegisteredError("Пользователь с такой почтой уже зарегистрирован.")

    user = User(
        email=data.email,
        password_hash=generate_password_hash(data.password),
        is_active=True,
        is_admin=False,
    )
    session.add(user)
    session.flush()

    student = Student(
        user_id=user.id,
        name=data.child_first_name,
        last_name=data.child_last_name,
        class_number=1,
    )
    session.add(student)
    session.flush()

    return {
        "user_id": user.id,
        "student_id": student.id,
        "email": user.email,
        "is_active": user.is_active,
        "activation_email_sent": False,
        "activation_link_dev": None,
        "auto_activated": True,
    }
