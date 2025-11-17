"""Provider-agnostic agent execution facade.

This module provides a backward-compatible facade over the agent registry,
maintaining the original API while delegating to the new abstraction layer.

For new code, prefer importing from cape.core.agents directly:
    from cape.core.agents import get_agent, AgentExecuteRequest
"""

import logging
from typing import Callable, Optional

from cape.core.agents import AgentExecuteRequest, AgentExecuteResponse, get_agent
from cape.core.agents.claude import execute_claude_template
from cape.core.agents.claude_models import (
    ClaudeAgentPromptRequest,
    ClaudeAgentPromptResponse,
    ClaudeAgentTemplateRequest,
)
from cape.core.notifications import insert_progress_comment, make_progress_comment_handler

_DEFAULT_LOGGER = logging.getLogger(__name__)


def _get_issue_logger(adw_id: str) -> logging.Logger:
    """Return logger bound to a specific workflow or fall back to module logger."""
    issue_logger = logging.getLogger(f"cape_{adw_id}")
    return issue_logger if issue_logger.handlers else _DEFAULT_LOGGER


def prompt_claude_code(request: ClaudeAgentPromptRequest) -> ClaudeAgentPromptResponse:
    """Execute Claude Code with the given prompt configuration.

    Legacy function for backward compatibility. Prefer using get_agent()
    and AgentExecuteRequest directly for new code.

    Args:
        request: Claude-specific prompt request

    Returns:
        Claude-specific prompt response
    """
    # Map ClaudeAgentPromptRequest to AgentExecuteRequest
    agent_request = AgentExecuteRequest(
        prompt=request.prompt,
        issue_id=request.issue_id,
        adw_id=request.adw_id,
        agent_name=request.agent_name,
        model=request.model,
        output_path=request.output_file,
        provider_options={"dangerously_skip_permissions": request.dangerously_skip_permissions},
    )

    # Create progress comment handler
    logger = _get_issue_logger(request.adw_id)
    handler = make_progress_comment_handler(request.issue_id, request.adw_id, logger)

    # Get agent and execute
    agent = get_agent("claude")
    response = agent.execute_prompt(agent_request, stream_handler=handler)

    # Insert final progress comment if successful
    if response.success and response.raw_output_path:
        insert_progress_comment(
            request.issue_id, f"Output saved to: {response.raw_output_path}", logger
        )

    # Map AgentExecuteResponse to ClaudeAgentPromptResponse
    return ClaudeAgentPromptResponse(
        output=response.output, success=response.success, session_id=response.session_id
    )


def execute_template(request: ClaudeAgentTemplateRequest) -> ClaudeAgentPromptResponse:
    """Execute a Claude Code template with slash command and arguments.

    Legacy function for backward compatibility. Delegates to Claude provider
    template helper.

    Args:
        request: Claude-specific template request

    Returns:
        Claude-specific prompt response
    """
    return execute_claude_template(request)


def execute_agent_prompt(
    request: AgentExecuteRequest,
    provider: Optional[str] = None,
    *,
    stream_handler: Optional[Callable[[str], None]] = None
) -> AgentExecuteResponse:
    """Execute agent prompt with specified or default provider.

    This is the new provider-agnostic API for agent execution.
    Use stream_handler for notifications and progress tracking.

    Args:
        request: Provider-agnostic execution request
        provider: Optional provider name (defaults to "claude")
        stream_handler: Optional callback for streaming output

    Returns:
        Provider-agnostic execution response

    Example:
        from cape.core.agent import execute_agent_prompt
        from cape.core.agents import AgentExecuteRequest
        from cape.core.notifications import make_progress_comment_handler

        request = AgentExecuteRequest(
            prompt="/implement plan.md",
            issue_id=123,
            adw_id="adw-456",
            agent_name="implementor"
        )
        handler = make_progress_comment_handler(123, "adw-456", logger)
        response = execute_agent_prompt(request, stream_handler=handler)
    """
    agent = get_agent(provider)
    return agent.execute_prompt(request, stream_handler=stream_handler)
