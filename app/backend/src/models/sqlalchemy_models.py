from sqlalchemy import Column, ForeignKey, Integer, String, Date, DateTime, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from core.sqlalchemy_connect import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    firstname = Column(String(100), nullable=False)
    lastname = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    date_of_birth = Column(Date, nullable=False)

    chat_histories = relationship("ChatHistory", back_populates="user", cascade="all, delete-orphan")


class InputType(str, enum.Enum):
    single = "single"
    csv = "csv"


class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Input
    input_type = Column(Enum(InputType), nullable=False, default=InputType.single)
    input_data = Column(Text, nullable=True)
    input_file_url = Column(String(500), nullable=True)

    # Output
    output_type = Column(Enum(InputType), nullable=False, default=InputType.single)
    output_data = Column(Text, nullable=True)
    output_file_url = Column(String(500), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user = relationship("User", back_populates="chat_histories")