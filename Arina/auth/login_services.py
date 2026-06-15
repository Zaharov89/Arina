from sqlalchemy import select
from sqlalchemy.orm import Session
from werkzeug.security import check_password_hash

from Arina.auth.services import build_user_payload, issue_token_pair, sanitize_text, validate_email
from Arina.database.models import User


class LoginError(Exception):
    pass


def login_user(session: Session, payload: dict) -> dict:
    login = sanitize_text(payload.get("login")).lower()
    password = str(payload.get("password") or "")
    remember_me = bool(payload.get("remember_me"))

    if validate_email(login) or not password:
        raise LoginError("Логин или пароль не верный")

    user = session.scalar(select(User).where(User.email == login))
    if not user or not check_password_hash(user.password_hash, password):
        raise LoginError("Логин или пароль не верный")

    if not user.is_active:
        raise LoginError("Аккаунт не активирован. Подтвердите почту по ссылке из письма.")

    tokens = issue_token_pair(user, remember_me=remember_me)
    return {
        **build_user_payload(user),
        **tokens,
    }
