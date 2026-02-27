from fastmcp import FastMCP
from fastmcp.server.context import Context
from fastmcp.dependencies import CurrentContext
from pydantic import BaseModel, Field

from fastmcp_wizard import WizardManager, FormStep, UrlElicitationRequiredError

# Ensure you initialize the server
mcp = FastMCP("ProgressiveWizardService")

class InfrastructureConfig(BaseModel):
    instance_type: str = Field(description="EC2 instance type")
    volume_size: int = Field(ge=10, description="Volume size in GB")

@mcp.tool()
async def provision_infrastructure(ctx: Context = CurrentContext()) -> str:
    """
    A multi-step setup wizard that guides the user through provisioning infrastructure.
    """
    # 1. Initialize the WizardManager with a unique ID
    wizard = WizardManager("infra_provisioning_wizard")
    
    # 2. Add sequential steps using FormStep
    wizard.add_step(FormStep(
        step_id="environment",
        message="Select the target environment:",
        # Single-Select (Untitled) via array of strings
        schema=["development", "staging", "production"]
    ))
    
    wizard.add_step(FormStep(
        step_id="advanced_features",
        message="Select advanced features to enable:",
        # Multi-Select (Untitled) via nested array
        schema=[["monitoring", "auto_scaling", "load_balancer"]],
        # Progressive Disclosure: Only ask if environment is production
        condition=lambda data: data.get("environment") == "production"
    ))
    
    wizard.add_step(FormStep(
        step_id="config",
        message="Provide specific infrastructure sizing configuration:",
        # Complex BaseModel schema
        schema=InfrastructureConfig
    ))
    
    # 3. Execute the wizard
    # The WizardManager handles state persistence, routing, and Pydantic validation loops automatically.
    collected_data = await wizard.execute(ctx)
    
    # 4. Process the structured payload
    # `collected_data` contains dictionary keys matching your step_ids
    return f"Infrastructure successfully provisioned with config: {collected_data}"

if __name__ == "__main__":
    # Run the server
    mcp.run()
