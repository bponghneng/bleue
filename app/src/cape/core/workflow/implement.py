"""Implementation functionality for workflow orchestration."""

from logging import Logger

from cape.core.agent import execute_implement_plan
from cape.core.agents import AgentExecuteResponse
from cape.core.workflow.shared import AGENT_IMPLEMENTOR
from cape.core.workflow.types import ImplementData, StepResult


def implement_plan(
    plan_file: str, issue_id: int, adw_id: str, logger: Logger
) -> StepResult[ImplementData]:
    """Implement the plan using configured provider.

    Uses the provider configured via CAPE_IMPLEMENT_PROVIDER environment variable.
    Defaults to Claude if not set.

    Args:
        plan_file: Path to the plan file to implement
        issue_id: Cape issue ID for tracking
        adw_id: Workflow ID for tracking
        logger: Logger instance

    Returns:
        StepResult with ImplementData containing output and optional session_id
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

    if not response.success:
        return StepResult.fail(response.output)

    return StepResult.ok(ImplementData(output=response.output, session_id=response.session_id))
