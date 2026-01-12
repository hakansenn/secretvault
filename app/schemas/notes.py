from pydantic import BaseModel, Field
from datetime import datetime

class NoteCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1, max_length=10000)
    file_id: int | None = None

class NoteOut(BaseModel):
    id: int
    title: str
    content: str
    file_id: int | None
    created_at: datetime

    class Config:
        from_attributes = True
