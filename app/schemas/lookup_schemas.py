"""
Pydantic schemas for lookup tables
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class FunctionBase(BaseModel):
    name: str
    description: Optional[str] = None
    is_active: bool = True

class FunctionCreate(FunctionBase):
    pass

class FunctionUpdate(FunctionBase):
    name: Optional[str] = None

class Function(FunctionBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class PlatformBase(BaseModel):
    name: str
    description: Optional[str] = None
    is_active: bool = True

class PlatformCreate(PlatformBase):
    pass

class PlatformUpdate(PlatformBase):
    name: Optional[str] = None

class Platform(PlatformBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class PriorityBase(BaseModel):
    name: str
    level: int
    description: Optional[str] = None
    color_code: Optional[str] = None
    is_active: bool = True

class PriorityCreate(PriorityBase):
    pass

class PriorityUpdate(PriorityBase):
    name: Optional[str] = None
    level: Optional[int] = None

class Priority(PriorityBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class StatusBase(BaseModel):
    name: str
    description: Optional[str] = None
    color_code: Optional[str] = None
    is_active: bool = True

class StatusCreate(StatusBase):
    pass

class StatusUpdate(StatusBase):
    name: Optional[str] = None

class Status(StatusBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
