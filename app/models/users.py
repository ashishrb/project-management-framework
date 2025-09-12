"""
User model for authentication and RBAC
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(200), nullable=True)
    role = Column(String(50), nullable=False, default="guest")  # guest, owner, portfolio, admin
    password_hash = Column(String(255), nullable=False)
    password_salt = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)


