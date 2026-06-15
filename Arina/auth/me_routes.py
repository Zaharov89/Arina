from flask import Blueprint, jsonify, request
from sqlalchemy.exc import SQLAlchemyError

from Arina.auth.services import AuthTokenError, verify_auth_token
from Arina.database.session import get_session_factory


auth_me_bp = Blueprint("auth_me", __name__, url_prefix="/auth")


def get_access_token_from_request() -> str:
    auth_header = request.headers.get("Authorization", "")
    if auth_header.lower().startswith("bearer "):
        return auth_header[7:].strip()
    return ""


@auth_me_bp.route("/me", methods=["GET"])
def current_user_api():
    token = get_access_token_from_request()

    try:
        session_factory = get_session_factory()
        with session_factory() as session:
            result = verify_auth_token(session, token)

        return jsonify(
            {
                "status": "ok",
                "message": "Пользователь авторизован.",
                "data": {
                    "user_id": result["user_id"],
                    "email": result["email"],
                    "first_name": result["first_name"],
                    "last_name": result["last_name"],
                    "display_name": result["display_name"],
                    "is_active": result["is_active"],
                },
            }
        )
    except AuthTokenError as error:
        return jsonify({"status": "unauthorized", "message": str(error)}), 401
    except (RuntimeError, SQLAlchemyError, OSError) as error:
        return jsonify(
            {
                "status": "error",
                "message": "Не удалось проверить текущего пользователя.",
                "error": str(error),
            }
        ), 500
