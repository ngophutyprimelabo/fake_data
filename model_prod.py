from datetime import datetime, timedelta
from typing import Optional

from core.database import Base
from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, column_property, mapped_column, relationship
from sqlalchemy.sql import func, select, text


class CategoryGroup(Base):
    __tablename__ = "app_categorygroup"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    label: Mapped[str] = mapped_column(String(255), nullable=False)
    order: Mapped[int] = mapped_column(Integer, nullable=False)
    category_group_id: Mapped[str] = mapped_column(String(255), nullable=False)
    display_mode_id: Mapped[int] = mapped_column(Integer, nullable=False)
    model_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)


class ChatConversation(Base):
    __tablename__ = "app_chatconversation"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("auth_user.id"), nullable=False)
    topic: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(6), nullable=False)
    model_id: Mapped[int] = mapped_column(Integer, ForeignKey("app_chatmodel.id"), nullable=False, index=True)
    is_delete: Mapped[bool] = mapped_column(Boolean, nullable=False)
    file_upload_type: Mapped[int] = mapped_column(Integer, nullable=False)
    thread_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    vector_store_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    user = relationship("AuthUser", foreign_keys=[user_id])
    model = relationship("ChatModel", foreign_keys=[model_id])


class ChatMessage(Base):
    __tablename__ = "app_chatmessage"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    conversation_id: Mapped[int] = mapped_column(Integer, ForeignKey("app_chatconversation.id"), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    is_bot: Mapped[bool] = mapped_column(Boolean, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(6), nullable=False)
    chat_parameter: Mapped[dict] = mapped_column(JSON, nullable=False, default={})
    bad_reason: Mapped[str] = mapped_column(Text, nullable=False, default="")
    is_bad: Mapped[bool] = mapped_column(Boolean, nullable=False)
    is_good: Mapped[bool] = mapped_column(Boolean, nullable=False)
    corrected_document_name: Mapped[str] = mapped_column(String(255), nullable=False)
    corrected_document_page: Mapped[str] = mapped_column(String(255), nullable=False)
    corrected_document_title: Mapped[str] = mapped_column(String(255), nullable=False)

    conversation = relationship("ChatConversation", foreign_keys=[conversation_id])


class ChatModel(Base):
    __tablename__ = "app_chatmodel"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    order: Mapped[int] = mapped_column(Integer, nullable=False)
    is_eval: Mapped[bool] = mapped_column(Boolean, nullable=False)
    is_return_markdown: Mapped[bool] = mapped_column(Boolean, nullable=False)
    text_explain: Mapped[str] = mapped_column(Text, nullable=False, default="")
    is_single_conversation: Mapped[bool] = mapped_column(Boolean, nullable=False)
    is_summary_menu: Mapped[bool] = mapped_column(Boolean, nullable=False)
    is_premise_statement: Mapped[bool] = mapped_column(Boolean, nullable=False)
    premise_statement: Mapped[str] = mapped_column(Text, nullable=False, default="")
    premise_statement_response: Mapped[str] = mapped_column(Text, nullable=False, default="")
    output_screen_type: Mapped[str] = mapped_column(String(255), nullable=False)


class ChatParameter(Base):
    __tablename__ = "app_chatparameter"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[str] = mapped_column(String(255), nullable=False)
    option: Mapped[dict] = mapped_column(JSON, nullable=False)
    order: Mapped[int] = mapped_column(Integer, nullable=False)
    cols: Mapped[int] = mapped_column(Integer, nullable=False)
    label: Mapped[str] = mapped_column(String(255), nullable=False)
    required: Mapped[bool] = mapped_column(Boolean, nullable=False)
    local_storage: Mapped[bool] = mapped_column(Boolean, nullable=False)
    category_group_id: Mapped[str] = mapped_column(String(255), nullable=False)
    main_category_id: Mapped[str] = mapped_column(String(255), nullable=False)


class ChatParameterGroup(Base):
    __tablename__ = "app_chatparametergroup"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    label: Mapped[str] = mapped_column(String(255), nullable=False)
    order: Mapped[int] = mapped_column(Integer, nullable=False)
    model_id: Mapped[int] = mapped_column(Integer, ForeignKey("app_chatmodel.id"), nullable=False, index=True)
    category_group_id: Mapped[str] = mapped_column(String(255), nullable=False)
    main_category_id: Mapped[str] = mapped_column(String(255), nullable=False)

    model = relationship("ChatModel", foreign_keys=[model_id])


class AuthUser(Base):
    __tablename__ = "auth_user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    password: Mapped[str] = mapped_column(String(128), nullable=False)
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime(6), nullable=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, nullable=False)
    username: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    first_name: Mapped[str] = mapped_column(String(150), nullable=False)
    last_name: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str] = mapped_column(String(254), nullable=False)
    is_staff: Mapped[bool] = mapped_column(Boolean, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False)
    date_joined: Mapped[datetime] = mapped_column(DateTime(6), nullable=False)