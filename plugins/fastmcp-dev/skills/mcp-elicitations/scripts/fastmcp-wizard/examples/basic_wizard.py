import asyncio
from fastmcp import FastMCP
from fastmcp.server.context import Context
from fastmcp.dependencies import CurrentContext
from pydantic import BaseModel, Field

from fastmcp_wizard import WizardManager, FormStep

mcp = FastMCP("WizardDemo")

class ProfileDetails(BaseModel):
    age: int = Field(ge=18, description="User must be at least 18 years old.")
    bio: str

@mcp.tool()
async def deploy_user_profile(ctx: Context = CurrentContext()) -> str:
    """
    Interactive tool that uses Progressive Disclosure to gather user details.
    """
    wizard = WizardManager("profile_wizard")
    
    # Step 1: Scalar String
    wizard.add_step(FormStep(
        step_id="username",
        message="What is the new username?",
        schema=str
    ))
    
    # Step 2: Single-Select Dropdown (Untitled)
    wizard.add_step(FormStep(
        step_id="role",
        message="Select the primary role for the user:",
        schema=["admin", "editor", "viewer"]
    ))
    
    # Step 3: Multi-Select Checklist (Progressively disclosed only for admins)
    wizard.add_step(FormStep(
        step_id="permissions",
        message="Select the administrative permissions:",
        schema=[["read_logs", "write_db", "delete_users"]],
        condition=lambda data: data.get("role") == "admin"
    ))
    
    # Step 4: Complex BaseModel with validation
    wizard.add_step(FormStep(
        step_id="details",
        message="Please provide additional profile details:",
        schema=ProfileDetails
    ))
    
    try:
        collected_data = await wizard.execute(ctx)
        return f"Wizard completed successfully. Data gathered:\n{collected_data}"
    except Exception as e:
        return f"Wizard aborted or failed: {str(e)}"

if __name__ == "__main__":
    mcp.run()
