# Advanced FastMCP Elicitation Architecture

When architecting complex, enterprise-grade AI interactions, you must look beyond basic UI rendering and adhere to strict protocol-level mechanics.

## 1. Interaction Modes and Security Boundaries

The MCP Elicitation standard dictates two distinct modes. You must choose the correct mode based on the security context of the data being gathered:

*   **Form Mode (In-Band):** Used for standard configuration, parameters, and metadata. The client renders the UI based on the JSON schema, and the submitted data is exposed directly to the client application and the LLM context.
*   **URL Mode (Out-of-Band):** Used STRICTLY for highly sensitive information such as OAuth credentials, passwords, or proprietary API keys. In this mode, the client redirects the user to an external secure web browser. The tokens never traverse the LLM's context window. 
    *   *Implementation:* If you detect a need for out-of-band secrets in a multi-step form, you MUST raise a `UrlElicitationRequiredError` to halt the FormWizard and securely initiate the OAuth flow.

## 2. Explicit Protocol Action Handling

Whenever `ctx.elicit()` is invoked, the user's interaction culminates in one of three standardized responses. You MUST explicitly handle all three via Python's pattern matching:

*   **Accept (`AcceptedElicitation`):** The user explicitly approves the submission. Extract the payload via the `.data` attribute.
*   **Decline (`DeclinedElicitation`):** The user actively refuses to provide the requested information. This is typically used to bypass optional fields. If the step is required, you must raise an error or halt.
*   **Cancel (`CancelledElicitation`):** The user explicitly aborts the entire operation. You MUST command the server to halt the tool execution entirely (e.g., by raising an exception or returning a specific abort state).

## 3. Background Tasks (Docket Integration)

For exceptionally complex forms involving extensive backend validation (e.g., provisioning infrastructure), the elicitation lifecycle may exceed standard network timeout thresholds.

FastMCP 3.0 introduces protocol-native background tasks powered by Docket (SEP-1686).
*   **Implementation:** Decorate your tool with `@mcp.tool(task=True)`.
*   **Mechanism:** Execution is offloaded to a distributed worker context. When `ctx.elicit()` is called, FastMCP utilizes Redis for distributed coordination, pausing the Docket worker and transmitting an `input_required` task status to the client.

## 4. Distinguishing Elicitation from MCP Apps

FastMCP 3 introduced "MCP Apps" (SEP-1865) via the `ui://` resource scheme to serve arbitrary HTML/JS in an iframe. 
*   **Rule:** Do NOT use MCP Apps for structured data gathering or multi-step forms. 
*   **Reasoning:** Elicitation schemas are natively understood by the LLM, and the structured JSON output is seamlessly integrated back into the agent's contextual awareness. Iframe interactions are opaque to the LLM. Use `ctx.elicit()` (Elicitation) for forms, and use MCP Apps solely for rich visualizations (like charts or dashboards).