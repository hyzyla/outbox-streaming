from pydantic import BaseModel


class TodoCreate(BaseModel):
    text: str


class Todo(BaseModel):
    id: int
    text: str

    class Config:
        orm_mode = True
