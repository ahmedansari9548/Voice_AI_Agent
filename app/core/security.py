import os
import secrets

from dotenv import load_dotenv
from fastapi import Request
from fastapi.responses import JSONResponse

load_dotenv()


async def api_key_middleware(request: Request, call_next):
    public_paths = {"/health", "/docs", "/openapi.json", "/redoc"}

    if request.url.path in public_paths:
        return await call_next(request)

    expected = os.getenv("API_KEY", "")
    provided = request.headers.get("X-API-Key", "")

    if not expected:
        return JSONResponse(
            status_code=503,
            content={
                "data": None,
                "error": {
                    "code": "CONFIGURATION_ERROR",
                    "message": "API key not configured",
                },
            },
        )

    if not secrets.compare_digest(provided, expected):
        return JSONResponse(
            status_code=401,
            content={
                "data": None,
                "error": {
                    "code": "UNAUTHORIZED",
                    "message": "Invalid or missing API key",
                },
            },
        )

    return await call_next(request)
