"""Data types for Cape CLI workflow components.

Agent-specific models moved to cape.core.agents package.
"""

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator

# Deprecated - use cape.core.agents.claude.claude_models instead
# These aliases are provided for backward compatibility during migration
from cape.core.agents.claude import (
    ClaudeAgentPromptRequest as AgentPromptRequest,  # noqa: F401
)
from cape.core.agents.claude import (
    ClaudeAgentPromptResponse as AgentPromptResponse,  # noqa: F401
)
from cape.core.agents.claude import (
    ClaudeAgentResultMessage as ClaudeCodeResultMessage,  # noqa: F401
)
from cape.core.agents.claude import (
    ClaudeAgentTemplateRequest as AgentTemplateRequest,  # noqa: F401
)

# All slash commands used in the Cape workflow system
SlashCommand = Literal[
    "/implement",
    "/triage:classify",
    "/triage:chore",
    "/triage:bug",
    "/triage:feature",
    "/triage:find-plan-file",
]


class CapeIssue(BaseModel):
    """Cape issue model matching Supabase schema."""

    id: int
    title: Optional[str] = None
    description: str = Field(..., min_length=1)
    status: Literal["pending", "started", "completed"] = "pending"
    assigned_to: Optional[Literal["alleycat-1", "tydirium-1"]] = None
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
