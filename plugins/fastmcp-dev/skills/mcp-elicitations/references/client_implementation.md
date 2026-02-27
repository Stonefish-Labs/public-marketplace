# FastMCP Client Elicitation Handler

When building an MCP client that connects to a FastMCP 3.x server utilizing `ctx.elicit()` or the `FormWizard`, your client MUST implement an `elicitation_handler`. This handler is responsible for intercepting the server's input request and rendering the appropriate UI controls or CLI prompts to the user.

## Client-Side Handler (Full Fallback Example)

The following is a comprehensive, console-based fallback handler that demonstrates how to parse the `response_type` schema and collect all expected inputs before returning the data.

```python
from fastmcp.client.elicitation import ElicitResult

async def elicitation_handler(message: str, response_type: type | None, params: dict, context) -> ElicitResult | object:
    """
    A robust, console-based fallback handler for FastMCP 3 Elicitation.
    
    Parameters:
    - message (str): The prompt to display to the user.
    - response_type (type | None): The Pydantic model or scalar type derived from the JSON schema. None means no response is needed (Pure Action).
    - params (dict): Raw MCP parameters including the raw JSON schema.
    - context: Request context metadata.
    """
    print(f"\nServer asks: {message}")

    # Pure Action Elicitation (No schema, just acknowledgment)
    if response_type is None:
        user = input("Press Enter to Accept (or type 'cancel' to abort): ").strip()
        if user.lower() == "cancel":
            return ElicitResult(action="cancel")
        return ElicitResult(action="accept")

    # Complex Structured Form (Dataclass or BaseModel fields)
    if hasattr(response_type, "__dataclass_fields__") or hasattr(response_type, "model_fields"):
        fields = getattr(response_type, "__dataclass_fields__", getattr(response_type, "model_fields", {}))
        values = {}
        
        for name in fields:
            user = input(f"  {name}: ").strip()
            if user.lower() == "cancel":
                return ElicitResult(action="cancel")
            values[name] = user
            
        # Unmarshall and return the populated schema instance implicitly
        return response_type(**values)

    # Scalar Input (Single value)
    user = input("Your response: ").strip()
    if not user:
        return ElicitResult(action="decline")
    
    # Return instantiated scalar wrapper implicitly
    return response_type(value=user)
```

## Response Actions

When your client handler completes, it must explicitly signal one of the following states back to the server:

| Return Type | Protocol Effect |
|---|---|
| `response_type(...)` | **Implicit Accept**: The server parses the returned object as a successful `AcceptedElicitation`. |
| `ElicitResult(action="accept", content=data)` | **Explicit Accept**: Alternative explicit declaration. Use when returning unmarshalled primitive structures. |
| `ElicitResult(action="decline")` | **User Declined**: The server will receive a `DeclinedElicitation` and must proceed accordingly (e.g., skip an optional field). |
| `ElicitResult(action="cancel")` | **User Cancelled**: The server will receive a `CancelledElicitation` and MUST halt the operation immediately. |