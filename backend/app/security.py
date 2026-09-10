"""
AIDE-OS Security Middleware
JWT Authentication, Security Headers, and Rate Limit Integration
"""
import os
import time
import logging
from typing import Optional, Callable
from functools import wraps

import jwt
from fastapi import Request, Response, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.config import get_settings

logger = logging.getLogger("aide-os.security")

cfg = get_settings()

# Security configuration
SECRET_KEY = getattr(cfg, "SECRET_KEY", os.getenv("SECRET_KEY", "aide-os-default-secret"))
ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

# Public endpoints that don't require authentication
PUBLIC_ENDPOINTS = {
    "/",
    "/health",
    "/api/v1/health",
    "/api/v1/categories",
    "/docs",
    "/redoc",
    "/openapi.json",
}

# Endpoints that are always public (no auth needed)
ALWAYS_PUBLIC_PATHS = [
    "/api/v1/health",
    "/api/v1/categories",
]


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Adds security headers to all responses.
    Implements CSP, HSTS, Referrer-Policy, X-Content-Type-Options, etc.
    """
    
    def __init__(self, app, csp_policy: str = None):
        super().__init__(app)
        self.csp_policy = csp_policy or (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://fonts.googleapis.com; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data: https:; "
            "connect-src 'self' https://omni-gadget.onrender.com; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "form-action 'self'"
        )
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # Security Headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        # HSTS (only in production with HTTPS)
        if request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
        
        # CSP
        response.headers["Content-Security-Policy"] = self.csp_policy
        
        # Remove server header
        response.headers.pop("Server", None)
        
        return response


class JWTAuthMiddleware(BaseHTTPMiddleware):
    """
    JWT-based authentication middleware.
    Validates Bearer tokens on protected endpoints.
    """
    
    def __init__(self, app, secret_key: str = SECRET_KEY, algorithm: str = ALGORITHM):
        super().__init__(app)
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.bearer_scheme = HTTPBearer(auto_error=False)
    
    def _is_public_endpoint(self, path: str) -> bool:
        """Check if endpoint is public (no auth required)."""
        # Exact matches
        if path in PUBLIC_ENDPOINTS:
            return True
        
        # Prefix matches for docs
        if path.startswith("/docs") or path.startswith("/redoc") or path.startswith("/openapi.json"):
            return True
        
        # Health and categories
        if path in ALWAYS_PUBLIC_PATHS:
            return True
        
        return False
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip auth for public endpoints
        if self._is_public_endpoint(request.url.path):
            return await call_next(request)
        
        # Skip auth for OPTIONS (CORS preflight)
        if request.method == "OPTIONS":
            return await call_next(request)
        
        # Extract Bearer token
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=401,
                content={"detail": "Missing or invalid Authorization header. Use 'Bearer <token>'."},
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        token = auth_header.split(" ")[1]
        
        try:
            # Decode and validate JWT
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Check expiration
            exp = payload.get("exp")
            if exp and exp < time.time():
                return JSONResponse(
                    status_code=401,
                    content={"detail": "Token has expired"},
                    headers={"WWW-Authenticate": "Bearer"}
                )
            
            # Attach user info to request state
            request.state.user_id = payload.get("sub")
            request.state.user_tier = payload.get("tier", "anonymous")
            request.state.user_scopes = payload.get("scopes", [])
            
        except jwt.ExpiredSignatureError:
            return JSONResponse(
                status_code=401,
                content={"detail": "Token has expired"},
                headers={"WWW-Authenticate": "Bearer"}
            )
        except jwt.InvalidTokenError as e:
            return JSONResponse(
                status_code=401,
                content={"detail": f"Invalid token: {str(e)}"},
                headers={"WWW-Authenticate": "Bearer"}
            )
        except Exception as e:
            logger.error("JWT validation error: %s", e)
            return JSONResponse(
                status_code=500,
                content={"detail": "Authentication error"}
            )
        
        return await call_next(request)


def create_access_token(data: dict, expires_delta: Optional[int] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    expire = time.time() + (expires_delta or TOKEN_EXPIRE_MINUTES * 60)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str) -> Optional[dict]:
    """Verify a JWT token and return payload if valid."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("exp") and payload["exp"] < time.time():
            return None
        return payload
    except jwt.InvalidTokenError:
        return None


# Dependency for protected endpoints
async def get_current_user(request: Request) -> dict:
    """FastAPI dependency to get current authenticated user."""
    if not hasattr(request.state, "user_id") or not request.state.user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return {
        "user_id": request.state.user_id,
        "tier": request.state.user_tier,
        "scopes": request.state.user_scopes,
    }


def require_scope(scope: str):
    """Dependency factory to require a specific scope."""
    async def scope_checker(user: dict = Depends(get_current_user)):
        if scope not in user.get("scopes", []):
            raise HTTPException(status_code=403, detail=f"Required scope: {scope}")
        return user
    return scope_checker


def require_tier(min_tier: str):
    """Dependency factory to require minimum tier."""
    tier_order = ["anonymous", "basic", "premium", "admin"]
    min_index = tier_order.index(min_tier) if min_tier in tier_order else 0
    
    async def tier_checker(user: dict = Depends(get_current_user)):
        user_tier = user.get("tier", "anonymous")
        user_index = tier_order.index(user_tier) if user_tier in tier_order else 0
        if user_index < min_index:
            raise HTTPException(status_code=403, detail=f"Required tier: {min_tier}")
        return user
    return tier_checker


# Admin-only dependency
require_admin = require_tier("admin")

# Premium+ dependency
require_premium = require_tier("premium")