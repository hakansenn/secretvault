from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from app.core.config import settings
from app.core.errors import validation_exception_handler
from app.core.middleware import RequestIdMiddleware
from app.routers import auth, notes, files

from app.db.session import engine
from app.db.base import Base


app = FastAPI(title=settings.app_name)

Base.metadata.create_all(bind=engine)

app.add_middleware(RequestIdMiddleware)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(notes.router, prefix="/notes", tags=["notes"])
app.include_router(files.router, prefix="/files", tags=["files"])


@app.get("/health")
def health():
    return {"status": "ok", "env": settings.env}
