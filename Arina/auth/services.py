"""Future authentication services.

Planned responsibilities:
- password hashing and verification;
- account activation token generation;
- email sending for confirmation links;
- access/refresh token creation if JWT is selected;
- user session helpers if session auth is selected.
"""


class AuthNotImplementedError(NotImplementedError):
    """Raised when future authentication functionality is called too early."""


def create_activation_link(user_id: int, token: str) -> str:
    """Build a future account activation link."""
    if not user_id or not token:
        raise ValueError("user_id and token are required")

    return f"/auth/activate/{token}"
