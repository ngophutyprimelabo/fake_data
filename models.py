from datetime import datetime, timedelta
from typing import Optional
from connect import Base

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func, text


class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    external_id: Mapped[int] = mapped_column(
        Integer, unique=True, index=True, nullable=False
    )
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.external_id"), nullable=False
    )
    topic: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    model_id: Mapped[int] = mapped_column(Integer, nullable=False)

    user = relationship("User", foreign_keys=[user_id], backref="conversations")
    messages = relationship(
        "Message",
        primaryjoin="Conversation.external_id==Message.conversation_id",
        lazy="dynamic",
        backref="conversation",
    )

    @property
    def count_messages(self):
        thirty_days_ago = func.date_sub(func.now(), text("INTERVAL 1 MONTH"))
        return self.messages.filter(Message.created_at >= thirty_days_ago).count()


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    external_id: Mapped[int] = mapped_column(
        Integer, unique=True, index=True, nullable=False
    )
    conversation_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("conversations.external_id"), nullable=False
    )
    message: Mapped[str] = mapped_column(Text, nullable=False)
    is_bot: Mapped[bool] = mapped_column(Boolean, nullable=False)
    sender_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.external_id"), nullable=False
    )
    chat_parameter: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)


class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )


class MessageTag(Base):
    __tablename__ = "message_tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    message_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("messages.external_id", ondelete="CASCADE"), nullable=False
    )
    tag_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("tags.id", ondelete="CASCADE"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    external_id: Mapped[int] = mapped_column(
        Integer, unique=True, index=True, nullable=False
    )
    external_id_delete_flag: Mapped[bool] = mapped_column(Boolean, nullable=False)
    username: Mapped[Optional[str]] = mapped_column(
        String(150), ForeignKey("personnels.external_username"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    personnel = relationship(
        "Personnel", foreign_keys=[username], backref="conversations"
    )


class Personnel(Base):
    __tablename__ = "personnels"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    external_username: Mapped[str] = mapped_column(
        String(255), nullable=False, index=True, unique=True
    )
    entry_year: Mapped[Optional[int]] = mapped_column(Integer)
    department_code: Mapped[str] = mapped_column(
        String(5), ForeignKey("organizations.external_department_code"), nullable=False
    )
    branch_code: Mapped[Optional[str]] = mapped_column(String(3))
    head_office_name: Mapped[Optional[str]] = mapped_column(String(255))
    branch_name: Mapped[Optional[str]] = mapped_column(String(255))
    section_name: Mapped[Optional[str]] = mapped_column(String(255))
    sales_office_name: Mapped[Optional[str]] = mapped_column(String(255))
    organization_type: Mapped[Optional[str]] = mapped_column(String(255))
    employee_type: Mapped[Optional[str]] = mapped_column(String(255))
    role_type: Mapped[Optional[str]] = mapped_column(String(255))
    is_organization_head: Mapped[Optional[str]] = mapped_column(String(255))
    is_department_head: Mapped[Optional[str]] = mapped_column(String(255))


class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    external_department_code: Mapped[str] = mapped_column(
        String(5), nullable=False, index=True
    )
    external_division_code: Mapped[str] = mapped_column(String(3), nullable=False)
    external_section_code: Mapped[str] = mapped_column(String(2), nullable=False)
    field: Mapped[Optional[str]] = mapped_column(String(255))
    field_detail: Mapped[Optional[str]] = mapped_column(String(255))
    region: Mapped[Optional[str]] = mapped_column(String(255))
    branch: Mapped[Optional[str]] = mapped_column(String(255))
    abbreviation: Mapped[Optional[str]] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )


class Userprompt(Base):
    __tablename__ = "userprompts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    external_id: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    user_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.external_id"), nullable=True
    )
