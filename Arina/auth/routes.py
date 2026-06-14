from datetime import datetime

from flask import Blueprint, jsonify, redirect, render_template, request
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from Arina.auth.services import EmailAlreadyRegisteredError, ValidationError, register_user
from Arina.database.models import AccountActivationToken
from Arina.database.session import get_session_factory


auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


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
            ],
            "message": "Регистрация и подтверждение почты подключены к PostgreSQL.",
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
            session.commit()

        return render_template(
            "auth/activation_result.html",
            status="success",
            title="Почта подтверждена",
            message="Аккаунт активирован. Теперь можно пользоваться приложением.",
        )
    except (RuntimeError, SQLAlchemyError, OSError) as error:
        return jsonify(
            {
                "status": "error",
                "message": "Не удалось подтвердить аккаунт.",
                "error": str(error),
            }
        ), 500
