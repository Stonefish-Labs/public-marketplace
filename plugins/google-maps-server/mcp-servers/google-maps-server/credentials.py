"""
Google Maps API credentials management.
"""

from secrets_manager import secrets_manager

from fastmcp import Context


def get_api_key() -> str:
    """
    Get Google Maps API key from environment.

    Returns:
        str: The API key or None if not set

    """
    return secrets_manager.retrieve_secret("GOOGLE_MAPS_API_KEY")
    

async def get_api_key_from_user(ctx: Context) -> str:
    """Elicit Google Maps API key."""
    while True:
        key_result = await ctx.elicit(
            "Enter Google Maps API key:",
            response_type=str
        )

        action = getattr(key_result, "action", None)
        if action == "accept":
            cleaned_key = (getattr(key_result, "data", "") or "").strip()
            if len(cleaned_key) > 0:
                secrets_manager.store_secret("GOOGLE_MAPS_API_KEY", cleaned_key)
                return cleaned_key
        elif action == "decline":
            raise ValueError("API key required")
        elif action == "cancel":
            raise ValueError("Authentication cancelled")
        else:
            raise ValueError("Unexpected elicitation response")

        await ctx.info("❌ Invalid API key format. Enter a valid API key.")