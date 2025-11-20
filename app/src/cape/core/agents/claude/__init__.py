"""Claude Code agent provider for CAPE."""

from .claude import (
    ClaudeAgent,
    check_claude_installed,
    execute_claude_template,
    iter_assistant_items,
)
from .claude_models import (
    ClaudeAgentPromptRequest,
    ClaudeAgentPromptResponse,
    ClaudeAgentResultMessage,
    ClaudeAgentTemplateRequest,
)

__all__ = [
    "ClaudeAgent",
    "check_claude_installed",
    "execute_claude_template",
    "iter_assistant_items",
    "ClaudeAgentPromptRequest",
    "ClaudeAgentPromptResponse",
    "ClaudeAgentResultMessage",
    "ClaudeAgentTemplateRequest",
]
