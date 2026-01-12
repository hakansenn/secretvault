from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

def http_error(request: Request, status_code: int, code: str, message: str, details=None):
    payload = {
        "error": {
            "code": code,
            "message": message,
            "details": details or [],
            "path": str(request.url.path),
        }
    }
    return JSONResponse(status_code=status_code, content=payload)

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Pydantic/Request validation hatalarını tek formatta döndür
    details = exc.errors()
    return http_error(
        request,
        status_code=422,
        code="validation_error",
        message="Request validation failed",
        details=details,
    )
