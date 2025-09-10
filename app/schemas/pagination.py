"""
Pagination Schemas for GenAI Metrics Dashboard
Standardized pagination across all API endpoints
"""
from typing import Generic, TypeVar, Optional, List, Any
from pydantic import BaseModel, Field, validator
from fastapi import Query

T = TypeVar('T')

class PaginationParams(BaseModel):
    """Standard pagination parameters"""
    page: int = Field(1, ge=1, description="Page number (1-based)")
    size: int = Field(20, ge=1, le=100, description="Page size (max 100)")
    sort_by: Optional[str] = Field(None, description="Field to sort by")
    sort_order: str = Field("asc", regex="^(asc|desc)$", description="Sort order")
    
    @validator('page')
    def validate_page(cls, v):
        if v < 1:
            raise ValueError('Page must be >= 1')
        return v
    
    @validator('size')
    def validate_size(cls, v):
        if v < 1 or v > 100:
            raise ValueError('Size must be between 1 and 100')
        return v

class PaginationMeta(BaseModel):
    """Pagination metadata"""
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Page size")
    total: int = Field(..., description="Total number of items")
    pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Whether there is a next page")
    has_prev: bool = Field(..., description="Whether there is a previous page")
    next_page: Optional[int] = Field(None, description="Next page number")
    prev_page: Optional[int] = Field(None, description="Previous page number")

class PaginatedResponse(BaseModel, Generic[T]):
    """Standardized paginated response"""
    data: List[T] = Field(..., description="List of items")
    meta: PaginationMeta = Field(..., description="Pagination metadata")
    links: Optional[dict] = Field(None, description="Navigation links")

def create_pagination_meta(
    page: int,
    size: int,
    total: int
) -> PaginationMeta:
    """Create pagination metadata"""
    pages = (total + size - 1) // size  # Ceiling division
    
    return PaginationMeta(
        page=page,
        size=size,
        total=total,
        pages=pages,
        has_next=page < pages,
        has_prev=page > 1,
        next_page=page + 1 if page < pages else None,
        prev_page=page - 1 if page > 1 else None
    )

def create_paginated_response(
    data: List[T],
    page: int,
    size: int,
    total: int,
    base_url: str = None
) -> PaginatedResponse[T]:
    """Create a paginated response with navigation links"""
    meta = create_pagination_meta(page, size, total)
    
    links = None
    if base_url:
        links = {
            "first": f"{base_url}?page=1&size={size}",
            "last": f"{base_url}?page={meta.pages}&size={size}",
            "self": f"{base_url}?page={page}&size={size}"
        }
        
        if meta.has_next:
            links["next"] = f"{base_url}?page={meta.next_page}&size={size}"
        
        if meta.has_prev:
            links["prev"] = f"{base_url}?page={meta.prev_page}&size={size}"
    
    return PaginatedResponse(
        data=data,
        meta=meta,
        links=links
    )

# Query parameter helpers
def get_pagination_params(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    sort_by: Optional[str] = Query(None, description="Field to sort by"),
    sort_order: str = Query("asc", regex="^(asc|desc)$", description="Sort order")
) -> PaginationParams:
    """Get pagination parameters from query string"""
    return PaginationParams(
        page=page,
        size=size,
        sort_by=sort_by,
        sort_order=sort_order
    )

# Database pagination helpers
def apply_pagination(query, page: int, size: int, sort_by: str = None, sort_order: str = "asc"):
    """Apply pagination to SQLAlchemy query"""
    # Apply sorting
    if sort_by:
        if sort_order == "desc":
            query = query.order_by(getattr(query.column_descriptions[0]['entity'], sort_by).desc())
        else:
            query = query.order_by(getattr(query.column_descriptions[0]['entity'], sort_by).asc())
    
    # Apply pagination
    offset = (page - 1) * size
    return query.offset(offset).limit(size)

def get_total_count(query) -> int:
    """Get total count for pagination"""
    return query.count()
