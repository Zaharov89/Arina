import os
import uuid
from datetime import datetime

from flask import Blueprint, jsonify, render_template, request
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from Arina.auth.services import (
    AuthTokenError,
    EmailAlreadyRegisteredError,
    ValidationError,
    issue_token_pair,
    refresh_auth_token,
    register_user,
    verify_auth_token,
)
from Arina.database.models import AccountActivationToken, User
from Arina.database.session import get_session_factory


auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


def get_bearer_token() -> str:
    auth_header = request.headers.get("Authorization", "")
    if auth_header.lower().startswith("bearer "):
        return auth_header[7:].strip()

    payload = request.get_json(silent=True) or {}
    return str(payload.get("token") or "").strip()


def is_admin_delete_allowed() -> bool:
    configured_secret = os.getenv("ARINA_ADMIN_API_KEY", "").strip()
    if not configured_secret:
        return True

    request_secret = request.headers.get("X-Admin-Secret", "").strip()
    return request_secret == configured_secret


@auth_bp.route("/status")
def auth_status():
    return jsonify(
        {
            "status": "ready_for_registration",
            "module": "auth",
            "features": [
                "registration",
                "email_confirmation",
                "password_hashing",
                "input_validation",
                "delete_user",
                "verify_token",
                "refresh_token",
            ],
            "message": "Регистрация, подтверждение почты и JWT-токены подключены к PostgreSQL.",
        }
    )


@auth_bp.route("/register", methods=["GET"])
def register_page():
    return render_template("auth/register.html")


@auth_bp.route("/register", methods=["POST"])
def register_api():
    payload = request.get_json(silent=True) or {}

    try:
        session_factory = get_session_factory()
        with session_factory() as session:
            result = register_user(session, payload)
            session.commit()

        return jsonify(
            {
                "status": "created",
                "message": "Регистрация создана. Проверьте почту и подтвердите аккаунт по ссылке.",
                "data": result,
            }
        ), 201
    except ValidationError as error:
        return jsonify({"status": "validation_error", "errors": error.field_errors}), 400
    except EmailAlreadyRegisteredError as error:
        return jsonify({"status": "conflict", "errors": {"email": str(error)}}), 409
    except (RuntimeError, SQLAlchemyError, OSError) as error:
        return jsonify(
            {
                "status": "error",
                "message": "Ошибка регистрации. Проверьте подключение к БД и настройки SMTP.",
                "error": str(error),
            }
        ), 500


@auth_bp.route("/activate/<token>")
def activate_account(token: str):
    try:
        session_factory = get_session_factory()
        tokens = None

        with session_factory() as session:
            activation_token = session.scalar(
                select(AccountActivationToken).where(AccountActivationToken.token == token)
            )

            if not activation_token:
                return render_template(
                    "auth/activation_result.html",
                    status="error",
                    title="Ссылка не найдена",
                    message="Ссылка подтверждения недействительна или была удалена.",
                ), 404

            if activation_token.is_used:
                return render_template(
                    "auth/activation_result.html",
                    status="already_used",
                    title="Почта уже подтверждена",
                    message="Эта ссылка уже была использована. Можно переходить к входу в приложение.",
                )

            activation_token.is_used = True
            activation_token.used_at = datetime.now()
            activation_token.user.is_active = True
            session.flush()
            tokens = issue_token_pair(activation_token.user)
            session.commit()

        return render_template(
            "auth/activation_result.html",
            status="success",
            title="Почта подтверждена",
            message="Аккаунт активирован. Теперь можно пользоваться приложением.",
            tokens=tokens,
        )
    except (RuntimeError, SQLAlchemyError, OSError, AuthTokenError) as error:
        return jsonify(
            {
                "status": "error",
                "message": "Не удалось подтвердить аккаунт.",
                "error": str(error),
            }
        ), 500


@auth_bp.route("/users/<user_id>", methods=["DELETE"])
def delete_user(user_id: str):
    if not is_admin_delete_allowed():
        return jsonify(
            {
                "status": "forbidden",
                "message": "Удаление пользователя запрещено: неверный X-Admin-Secret.",
            }
        ), 403

    try:
        parsed_user_id = uuid.UUID(user_id)
    except ValueError:
        return jsonify(
            {
                "status": "validation_error",
                "errors": {"user_id": "Некорректный UUID пользователя."},
            }
        ), 400

    try:
        session_factory = get_session_factory()
        with session_factory() as session:
            user = session.get(User, parsed_user_id)
            if not user:
                return jsonify(
                    {
                        "status": "not_found",
                        "message": "Пользователь с таким id не найден.",
                    }
                ), 404

            deleted_user = {"user_id": str(user.id), "email": user.email}
            session.delete(user)
            session.commit()

        return jsonify(
            {
                "status": "deleted",
                "message": "Пользователь удалён из БД.",
                "data": deleted_user,
            }
        )
    except (RuntimeError, SQLAlchemyError, OSError) as error:
        return jsonify(
            {
                "status": "error",
                "message": "Не удалось удалить пользователя.",
                "error": str(error),
            }
        ), 500


@auth_bp.route("/verify_token", methods=["POST"])
def verify_token_api():
    token = get_bearer_token()

    try:
        session_factory = get_session_factory()
        with session_factory() as session:
            result = verify_auth_token(session, token)

        return jsonify(
            {
                "status": "valid",
                "message": "Токен действителен.",
                "data": result,
            }
        )
    except AuthTokenError as error:
        return jsonify(
            {
                "status": "invalid",
                "message": str(error),
            }
        ), 401
    except (RuntimeError, SQLAlchemyError, OSError) as error:
        return jsonify(
            {
                "status": "error",
                "message": "Не удалось проверить токен.",
                "error": str(error),
            }
        ), 500


@auth_bp.route("/refresh_token", methods=["POST"])
def refresh_token_api():
    payload = request.get_json(silent=True) or {}
    refresh_token = str(payload.get("refresh_token") or "").strip()

    try:
        session_factory = get_session_factory()
        with session_factory() as session:
            tokens = refresh_auth_token(session, refresh_token)

        return jsonify(
            {
                "status": "refreshed",
                "message": "Токены обновлены.",
                "data": tokens,
            }
        )
    except AuthTokenError as error:
        return jsonify(
            {
                "status": "invalid",
                "message": str(error),
            }
        ), 401
    except (RuntimeError, SQLAlchemyError, OSError) as error:
        return jsonify(
            {
                "status": "error",
                "message": "Не удалось обновить токен.",
                "error": str(error),
            }
        ), 500
