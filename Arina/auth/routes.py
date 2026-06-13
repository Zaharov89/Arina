from flask import Blueprint, jsonify

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/status")
def auth_status():
    return jsonify(
        {
            "status": "planned",
            "module": "auth",
            "features": [
                "registration",
                "login",
                "logout",
                "email_confirmation",
                "password_recovery",
                "jwt_or_session_auth",
            ],
            "message": "Авторизация и регистрация будут реализованы на следующем архитектурном этапе.",
        }
    )


@auth_bp.route("/register", methods=["GET", "POST"])
def register_placeholder():
    return jsonify(
        {
            "status": "planned",
            "endpoint": "/auth/register",
            "message": "Регистрация пока не реализована. Позже здесь будет REST API регистрации.",
        }
    ), 501


@auth_bp.route("/login", methods=["GET", "POST"])
def login_placeholder():
    return jsonify(
        {
            "status": "planned",
            "endpoint": "/auth/login",
            "message": "Авторизация пока не реализована. Позже здесь будет REST API входа.",
        }
    ), 501


@auth_bp.route("/activate/<token>")
def activate_account_placeholder(token: str):
    return jsonify(
        {
            "status": "planned",
            "endpoint": "/auth/activate/<token>",
            "token_received": bool(token),
            "message": "Активация аккаунта по ссылке из письма будет реализована позже.",
        }
    ), 501
