"""
SQLAlchemy ORM models for the Baker Compliant AI database.
"""

import uuid
import json
from datetime import datetime
from typing import List
from sqlalchemy import (
    create_engine, Column, String, Text, Boolean, DateTime, ForeignKey, JSON, Integer
)
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

def generate_uuid():
    """Generate a UUID string."""
    return str(uuid.uuid4())


class User(Base):
    """ORM model for the 'users' table."""
    __tablename__ = 'users'

    id = Column(String, primary_key=True, default=generate_uuid)
    azure_user_id = Column(String, unique=True, nullable=False)
    email = Column(String, nullable=False)
    display_name = Column(String, nullable=False)
    role = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    last_login_at = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    custom_gpts = relationship("CustomGpt", back_populates="user", cascade="all, delete-orphan")
    threads = relationship("Thread", back_populates="user")
    messages = relationship("Message", back_populates="user")


class CustomGpt(Base):
    """ORM model for the 'custom_gpts' table."""
    __tablename__ = 'custom_gpts'

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    system_prompt = Column(Text, nullable=False)
    specialization = Column(String, nullable=False)
    color = Column(String, default='blue')
    icon = Column(String, default='Brain')
    mcp_tools_enabled = Column(JSON, default={})
    is_active = Column(Boolean, default=True)
    
    user_id = Column(String, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    user = relationship("User", back_populates="custom_gpts")
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class Thread(Base):
    """ORM model for chat threads."""
    __tablename__ = 'threads'

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    custom_gpt_id = Column(String, ForeignKey('custom_gpts.id'), nullable=False)
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    last_message = Column(String, nullable=True)
    message_count = Column(Integer, default=0)
    is_archived = Column(Boolean, default=False)
    tags = Column(String, default='[]')  # JSON array of strings
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="threads")
    messages = relationship("Message", back_populates="thread", cascade="all, delete-orphan")


class Message(Base):
    """ORM model for chat messages."""
    __tablename__ = 'messages'

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    thread_id = Column(String, ForeignKey('threads.id'), nullable=False)
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    content = Column(Text, nullable=False)
    role = Column(String, nullable=False)
    custom_gpt_id = Column(String, ForeignKey('custom_gpts.id'))
    
    # AI metadata
    confidence_score = Column(String)  # REAL in SQL, but using String for compatibility
    model_used = Column(String)
    processing_time_ms = Column(String)  # INTEGER in SQL, but using String for compatibility
    
    # Compliance
    compliance_flags = Column(Text, default='[]')  # JSON array of strings
    sec_compliant = Column(Boolean, default=True)
    human_review_required = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    thread = relationship("Thread", back_populates="messages")
    user = relationship("User")
    
    @property
    def compliance_flags_list(self) -> List[str]:
        """Get compliance_flags as a Python list."""
        try:
            return json.loads(self.compliance_flags) if self.compliance_flags else []
        except (json.JSONDecodeError, TypeError):
            return []
