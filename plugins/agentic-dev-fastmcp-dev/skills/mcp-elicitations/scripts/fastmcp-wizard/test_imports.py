from fastmcp import FastMCP
from fastmcp.server.context import Context

# AcceptedElicitation / DeclinedElicitation / CancelledElicitation are NOT imported
# here. Use result.action ("accept" | "decline" | "cancel") checks instead — these
# classes are not reliably re-exported from fastmcp.server.elicitation across all
# FastMCP 3.x builds.

print("Imports successful")
