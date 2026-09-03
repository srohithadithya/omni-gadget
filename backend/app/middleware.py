"""
AIDE-OS — Session Middleware
Provides anonymous session persistence via HMAC-signed cookies.
No external dependencies — uses stdlib hashlib + hmac.
"""
import hashlib
import hmac
import uuid
import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

_COOKIE_NAME = "aide_session"
_HEADER_NAME = "X-Session-ID"
_MAX_AGE_SECONDS = 60 * 60 * 24 * 30  # 30 days


def _hmac_sign(session_id: str, secret: str) -> str:
    """Return hex HMAC-SHA256 of session_id."""
    return hmac.new(
        secret.encode("utf-8"),
        session_id.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def _hmac_verify(session_id: str, signature: str, secret: str) -> bool:
    """Constant-time comparison of computed vs provided signature."""
    expected = _hmac_sign(session_id, secret)
    return hmac.compare_digest(expected, signature)


class SessionMiddleware(BaseHTTPMiddleware):
    """
    ASGI middleware that:
    1. Reads ``aide_session`` cookie; validates its HMAC signature.
    2. If missing / invalid → generates a new UUID4 session_id.
    3. Sets the (signed) cookie on the response.
    4. Adds ``X-Session-ID`` header so the client can read the id.
    5. Stashes ``request.state.session_id`` for downstream handlers.
    """

    def __init__(self, app, secret_key: str = "aide-os-default-secret"):
        super().__init__(app)
        self.secret_key = secret_key

    async def dispatch(self, request: Request, call_next):
        # --- resolve session_id from cookie ---
        session_id = None
        cookie_header = request.cookies.get(_COOKIE_NAME)
        if cookie_header and "." in cookie_header:
            parts = cookie_header.split(".", 1)
            candidate_id, candidate_sig = parts[0], parts[1]
            if _hmac_verify(candidate_id, candidate_sig, self.secret_key):
                session_id = candidate_id

        if session_id is None:
            session_id = str(uuid.uuid4())

        # Stash on request state for endpoint access
        request.state.session_id = session_id

        # --- forward request ---
        response: Response = await call_next(request)

        # --- set signed cookie ---
        signature = _hmac_sign(session_id, self.secret_key)
        cookie_value = f"{session_id}.{signature}"
        response.set_cookie(
            key=_COOKIE_NAME,
            value=cookie_value,
            max_age=_MAX_AGE_SECONDS,
            httponly=True,
            samesite="lax",
        )

        # --- add header ---
        response.headers[_HEADER_NAME] = session_id

        return response
