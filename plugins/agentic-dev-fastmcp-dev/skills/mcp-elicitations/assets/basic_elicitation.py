from fastmcp import FastMCP
from fastmcp.server.context import Context
from fastmcp.dependencies import CurrentContext
from pydantic import BaseModel, Field

# Version-safe: check result.action ("accept" | "decline" | "cancel") instead of
# importing AcceptedElicitation / DeclinedElicitation / CancelledElicitation, which
# are not reliably re-exported from fastmcp.server.elicitation across all 3.x builds.

mcp = FastMCP("RichElicitationDemo")

class ResourceConfig(BaseModel):
    name: str = Field(description="Name of the resource")
    tags: list[str] = Field(default_factory=list, description="Tags to apply")

@mcp.tool()
async def configure_resource(ctx: Context = CurrentContext()) -> str:
    """
    Demonstrates a native, single-turn rich elicitation in FastMCP 3.
    """
    # Trigger a rich UI form for the user
    result = await ctx.elicit(
        message="Please configure the new resource.",
        # Using a BaseModel generates a complex composite form.
        # Alternatively, use `[["tag1", "tag2"]]` for a multi-select,
        # or `["prod", "dev"]` for a single-select dropdown.
        response_type=ResourceConfig
    )

    # Handle the three protocol action states via result.action (version-safe)
    if result.action == "accept":
        # result.data is automatically validated against the Pydantic schema;
        # FastMCP unmarshalls the dictionary into the BaseModel instance.
        config_data: ResourceConfig = result.data
        return f"Resource {config_data.name} configured with tags {config_data.tags}."

    elif result.action == "decline":
        return "Resource configuration was declined. Applying default parameters..."

    elif result.action == "cancel":
        return "Operation explicitly cancelled by the user."

    else:
        return "Unknown protocol error during elicitation."

if __name__ == "__main__":
    mcp.run()
