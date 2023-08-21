from flask_login import UserMixin

from typing import List
from typing import Optional
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship


class Base(DeclarativeBase):
    pass


class User(UserMixin, Base):
    __tablename__ = "user"
    email: Mapped[str] = mapped_column(String(300), primary_key=True)
    name: Mapped[str]

    def get_id(self):
        return self.email

    def is_active(self):
        return True

    def is_anonymous(self):
        return False


class Game(Base):
    __tablename__ = "game"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_email: Mapped[int] = mapped_column(ForeignKey("user.email"))
    score: Mapped[int]
    answers: Mapped[int]


class Question(Base):
    __tablename__ = "questions"
    filename: Mapped[str] = mapped_column(primary_key=True)
    correct_option: Mapped[str]
    false_option1: Mapped[str]
    false_option2: Mapped[str]
    false_option3: Mapped[str]
