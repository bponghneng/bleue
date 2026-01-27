"""Data types for Cape TUI components."""

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator


class CapeIssue(BaseModel):
    """Cape issue model matching Supabase schema."""

    id: int
    title: Optional[str] = None
    description: str = Field(..., min_length=1)
    status: Literal["pending", "started", "completed"] = "pending"
    assigned_to: Optional[
        Literal[
            "alleycat-1",
            "alleycat-2",
            "alleycat-3",
            "executor-1",
            "executor-2",
            "executor-3",
            "local-1",
            "local-2",
            "local-3",
            "tydirium-1",
            "tydirium-2",
            "tydirium-3",
            "xwing-1",
            "xwing-2",
            "xwing-3",
        ]
    ] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @field_validator("description")
    @classmethod
    def trim_description(cls, v: str) -> str:
        """Trim whitespace from description."""
        return v.strip()

    @field_validator("status", mode="before")
    @classmethod
    def default_status(cls, v):
        """Default missing status to pending."""
        return v if v else "pending"

    @classmethod
    def from_supabase(cls, row: dict) -> "CapeIssue":
        """Create CapeIssue from Supabase row."""
        return cls(**row)


class CapeComment(BaseModel):
    """Cape comment model matching Supabase schema."""

    id: Optional[int] = None
    issue_id: int
    comment: str = Field(..., min_length=1)
    raw: dict = Field(default_factory=dict)
    source: Optional[str] = None
    type: Optional[str] = None
    created_at: Optional[datetime] = None

    @field_validator("comment")
    @classmethod
    def trim_comment(cls, v: str) -> str:
        """Trim whitespace from comment."""
        return v.strip()
