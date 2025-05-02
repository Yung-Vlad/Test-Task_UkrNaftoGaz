from pydantic import BaseModel


class NoteModel(BaseModel):
    header: str | bytes
    text: str | bytes
    tags: str | bytes | None


class NoteUpdateModel(NoteModel):
    id: int
