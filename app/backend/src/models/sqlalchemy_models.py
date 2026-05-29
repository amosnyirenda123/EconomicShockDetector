from sqlalchemy import Column, ForeignKey, Integer, String, Float, Date, DateTime, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from core.sqlalchemy_connect import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    firstname = Column(String, nullable=False)
    lastname = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    password = Column(String, nullable=False)
    date_of_birth = Column(Date, nullable=False)

    chat_histories = relationship("ChatHistory", back_populates="user", cascade="all, delete-orphan")


class InputType(str, enum.Enum):
    single = "single"
    csv = "csv"


class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)  # user-defined name, e.g. "Morocco GDP Prediction 2026"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Input
    input_type = Column(Enum(InputType), nullable=False, default=InputType.single)
    input_data = Column(Text, nullable=True)        # JSON string for single input
    input_file_url = Column(String, nullable=True)  # URL for CSV uploads

    # Output
    output_type = Column(Enum(InputType), nullable=False, default=InputType.single)
    output_data = Column(Text, nullable=True)        # JSON string for single output
    output_file_url = Column(String, nullable=True)  # URL for CSV output

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user = relationship("User", back_populates="chat_histories")