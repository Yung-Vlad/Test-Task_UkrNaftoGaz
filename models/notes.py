from pydantic import BaseModel


class NoteModel(BaseModel):
    header: str | bytes
    text: str | bytes
    tags: str | bytes | None


class NoteInternalModel(NoteModel):
    created_time: str


class NoteUpdateModel(NoteModel):
    id: int


class NoteUpdateInternalModel(NoteUpdateModel):
    last_edit_time: str
    last_edit_user: int
