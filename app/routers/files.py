from pathlib import Path
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.db.models import FileObject, User
from app.core.config import settings
from app.services.file_store import save_upload
import os


router = APIRouter()

@router.post("/upload", status_code=201)
def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        stored_name, size_bytes = save_upload(file.file, content_type=file.content_type or "")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    obj = FileObject(
        original_name=file.filename,
        content_type=file.content_type or "application/octet-stream",
        stored_name=stored_name,
        size_bytes=size_bytes,
        owner_id=user.id,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)

    return {
        "id": obj.id,
        "filename": obj.original_name,
        "content_type": obj.content_type,
        "size_bytes": obj.size_bytes,
    }

@router.get("/{file_id}")
def download_file(
    file_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    obj = db.query(FileObject).filter(FileObject.id == file_id).first()
    if not obj or obj.owner_id != user.id:
        raise HTTPException(status_code=404, detail="File not found")

    path = Path(settings.upload_dir) / obj.stored_name
    if not path.exists():
        raise HTTPException(status_code=404, detail="File missing on disk")

    return FileResponse(
        path=str(path),
        media_type=obj.content_type,
        filename=obj.original_name,
    )


@router.get("")
def list_files(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    rows = (
        db.query(FileObject)
        .filter(FileObject.owner_id == user.id)
        .order_by(FileObject.id.desc())
        .all()
    )
    return [
        {
            "id": r.id,
            "filename": r.original_name,
            "content_type": r.content_type,
            "size_bytes": r.size_bytes,
            "created_at": r.created_at,
        }
        for r in rows
    ]

@router.delete("/{file_id}", status_code=204)
def delete_file(
    file_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    obj = db.query(FileObject).filter(FileObject.id == file_id).first()
    if not obj or obj.owner_id != user.id:
        raise HTTPException(status_code=404, detail="File not found")

    path = Path(settings.upload_dir) / obj.stored_name

    db.delete(obj)
    db.commit()

    try:
        os.remove(path)
    except OSError:
        pass

    return