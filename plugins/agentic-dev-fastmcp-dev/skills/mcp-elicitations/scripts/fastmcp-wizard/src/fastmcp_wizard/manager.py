from typing import Any, Dict, List
from fastmcp.server.context import Context

# Version-safe: check result.action ("accept" | "decline" | "cancel") instead of
# importing AcceptedElicitation / DeclinedElicitation / CancelledElicitation, which
# are not reliably re-exported from fastmcp.server.elicitation across all 3.x builds.

from pydantic import ValidationError

from .models import FormStep
from .exceptions import McpError

class WizardManager:
    """
    Stateful orchestration layer for handling multi-step, progressive disclosure
    forms over the stateless MCP protocol.
    """
    def __init__(self, wizard_id: str):
        self.wizard_id = wizard_id
        self.steps: List[FormStep] = []

    def add_step(self, step: FormStep) -> "WizardManager":
        """Registers a sequential form step to the wizard."""
        self.steps.append(step)
        return self

    async def execute(self, ctx: Context) -> Dict[str, Any]:
        """
        Executes the progressive disclosure workflow, preserving state across
        distributed sessions and handling validation loops.
        """
        # Retrieve persisted data from previous turns in the distributed session
        session_data = await ctx.get_state(self.wizard_id) or {}
        if not isinstance(session_data, dict):
            session_data = {}

        for step in self.steps:
            # Step bypass via progressive disclosure evaluation
            if step.step_id in session_data:
                continue
            if step.condition and not step.condition(session_data):
                continue
            
            # Implementation of self-correcting validation loop
            current_message = step.message
            while True:
                try:
                    # Trigger the dynamic UI rendering via FastMCP elicitation
                    result = await ctx.elicit(
                        message=current_message,
                        response_type=step.schema
                    )
                    
                    # Version-safe action dispatch via result.action string
                    if result.action == "accept":
                        # Store the successfully validated and accepted data
                        session_data[step.step_id] = result.data
                        await ctx.set_state(self.wizard_id, session_data)
                        break  # Exit the self-correcting loop and move to next step

                    elif result.action == "decline":
                        if step.is_required:
                            raise McpError(code=-32600, message=f"Required step '{step.step_id}' declined.")
                        break  # Skip recording data, move to next step

                    elif result.action == "cancel":
                        # FastMCP protocol expects graceful exits or specific signaling for cancellations.
                        raise McpError(code=-32000, message="Workflow aborted by user cancellation.")

                    else:
                        # Handle unexpected elicitation responses
                        raise McpError(code=-32603, message="Internal error: Received unknown elicitation action.")
                            
                except ValidationError as ve:
                    # Self-correcting loop: Intercept ValidationError and re-prompt user
                    # Augment original message with explicit validation failures
                    error_details = "\\n".join(f"- {err.get('loc', [''])[0]}: {err.get('msg', 'Invalid')}" for err in ve.errors())
                    current_message = f"{step.message}\n\nValidation Error(s):\n{error_details}\n\nPlease correct your input."
                    # Continue the while True loop to re-elicit
        
        # Clean up state upon successful completion to allow rerunning
        await ctx.set_state(self.wizard_id, {})
        return session_data
