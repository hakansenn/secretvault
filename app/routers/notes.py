from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models import Note, User
from app.core.deps import get_current_user
from app.schemas.notes import NoteCreate, NoteOut
from fastapi import HTTPException
from app.db.models import FileObject

router = APIRouter()

@router.get("", response_model=list[NoteOut])
def list_notes(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    notes = (
        db.query(Note)
        .filter(Note.owner_id == user.id)
        .order_by(Note.id.desc())
        .all()
    )
    return notes

@router.post("", response_model=NoteOut, status_code=201)
def create_note(
    payload: NoteCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if payload.file_id is not None:
        f = db.query(FileObject).filter(FileObject.id == payload.file_id).first()
        if not f or f.owner_id != user.id:
            raise HTTPException(status_code=400, detail="Invalid file_id")

    note = Note(
        title=payload.title,
        content=payload.content,
        owner_id=user.id,
        file_id=payload.file_id,
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    return note
