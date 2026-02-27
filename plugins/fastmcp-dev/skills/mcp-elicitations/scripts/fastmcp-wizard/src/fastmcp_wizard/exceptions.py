class UrlElicitationRequiredError(Exception):
    """
    Raised when an elicitation workflow involves highly sensitive information
    (e.g., OAuth credentials, proprietary API keys) that must be handled
    out-of-band via URL Mode to maintain strict security boundaries.
    """
    pass

class McpError(Exception):
    """
    Base exception for handling protocol-level failures within the MCP elicitation flow.
    """
    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message
        super().__init__(self.message)
