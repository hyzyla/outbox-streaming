from sqlalchemy import Column, Integer, Text

from app.db import Base


class Todo(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'text': self.text,
        }
