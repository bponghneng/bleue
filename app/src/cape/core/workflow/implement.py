"""Implementation functionality for workflow orchestration."""

import json
from logging import Logger
from typing import Dict, Optional

from cape.core.agent import execute_implement_plan
from cape.core.agents import AgentExecuteResponse
from cape.core.agents.claude import ClaudeAgentPromptResponse
from cape.core.workflow.shared import AGENT_IMPLEMENTOR


def parse_implement_output(output: str, logger: Logger) -> Optional[Dict]:
    """Log implementation output for debugging.

    This function no longer parses JSON. The plan file path is now discovered
    using the find-plan-file command in the workflow.

    Args:
        output: The raw output from the implementation
        logger: Logger instance

    Returns:
        Empty dict for backward compatibility (deprecated)
    """
    logger.debug("Implementation output logged")
    logger.debug(f"Output preview: {output[:200]}...")

    # Return empty dict for backward compatibility
    return {}


def implement_plan(
    plan_file: str, issue_id: int, adw_id: str, logger: Logger
) -> ClaudeAgentPromptResponse:
    """Implement the plan using configured provider.

    Uses the provider configured via CAPE_IMPLEMENT_PROVIDER environment variable.
    Defaults to Claude if not set.

    Args:
        plan_file: Path to the plan file to implement
        issue_id: Cape issue ID for tracking
        adw_id: Workflow ID for tracking
        logger: Logger instance

    Returns:
        Agent response with implementation results
    """
    # Use new execute_implement_plan helper which handles provider selection
    response: AgentExecuteResponse = execute_implement_plan(
        plan_file=plan_file,
        issue_id=issue_id,
        adw_id=adw_id,
        agent_name=AGENT_IMPLEMENTOR,
        logger=logger,
    )

    logger.debug(
        "implement response: success=%s, session_id=%s",
        response.success,
        response.session_id,
    )

    # Map AgentExecuteResponse to ClaudeAgentPromptResponse for compatibility
    return ClaudeAgentPromptResponse(
        output=response.output,
        success=response.success,
        session_id=response.session_id,
    )