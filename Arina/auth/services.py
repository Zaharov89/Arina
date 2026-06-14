import os
import re
import secrets
import smtplib
from dataclasses import dataclass
from email.message import EmailMessage

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
        is_active=False,
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

    token_value = secrets.token_urlsafe(48)
    activation_token = AccountActivationToken(user_id=user.id, token=token_value, is_used=False)
    session.add(activation_token)
    session.flush()

    activation_link = create_activation_link(token_value)
    email_sent = send_activation_email(data.email, data.child_first_name, activation_link)

    return {
        "user_id": str(user.id),
        "student_id": str(student.id),
        "email": user.email,
        "is_active": user.is_active,
        "activation_email_sent": email_sent,
        "activation_link_dev": None if email_sent else activation_link,
    }
