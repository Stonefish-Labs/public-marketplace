import json
import keyring

# Note: Linux needs libsecret to use this.
# Note2: Windows has a limit of 2560 characters for the password.



class MCPSecretsManager:
    """MCP Secrets Manager for secure keyring-based secret storage."""

    def __init__(self, server_name=None):
        """Initialize the secrets manager for a specific MCP server.

        Args:
            server_name: The name of the MCP server (e.g., 'findmy-server', 'google-maps-server')
        """
        if server_name:
            self._initalize_manager(server_name)
            
    def _initalize_manager(self, server_name):
        self.server_name = server_name
        self.service_name = f"com.mcp.{self.server_name}"

    def _serialize_secret_content(self, content):
        """Serialize secret content - use JSON prefix for complex types, direct string for simple strings"""
        if isinstance(content, (dict, list)):
            return "JSON:" + json.dumps(content)
        else:
            # For strings and other simple types, store directly
            return str(content)

    def _deserialize_secret_content(self, serialized_content):
        """Deserialize secret content - handle JSON prefix or return as-is"""
        if serialized_content and serialized_content.startswith("JSON:"):
            return json.loads(serialized_content[5:])
        else:
            return serialized_content

    def _serialize_index_content(self, index_set):
        """Serialize index set as JSON list"""
        return json.dumps(list(index_set))

    def _deserialize_index_content(self, serialized_index):
        """Deserialize index from JSON list to set"""
        if serialized_index:
            try:
                data = json.loads(serialized_index)
                return set(data) if isinstance(data, list) else set()
            except json.JSONDecodeError:
                return set()
        return set()

    def store_secret(self, secret_name, content):
        """Store a secret in the keyring for this server.

        Args:
            secret_name: Name of the secret
            content: The secret content (string, dict, or list)
        """
        username = secret_name
        # Serialize content for storage (with JSON prefix for complex types)
        serialized_content = self._serialize_secret_content(content)
        # Store the content in the keychain
        keyring.set_password(self.service_name, username, serialized_content)
        # Update the index of secrets for this server
        self._update_secret_index(secret_name)

    def retrieve_secret(self, secret_name):
        """Retrieve a secret from the keyring for this server.

        Args:
            secret_name: Name of the secret to retrieve

        Returns:
            The secret content, or None if not found
        """
        username = secret_name
        # Retrieve the content from the keychain
        serialized_content = keyring.get_password(self.service_name, username)
        return self._deserialize_secret_content(serialized_content)

    def delete_secret(self, secret_name):
        """Delete a secret from the keyring for this server.

        Args:
            secret_name: Name of the secret to delete
        """
        username = secret_name
        keyring.delete_password(self.service_name, username)
        # Remove from the index
        self._remove_from_secret_index(secret_name)

    def list_secrets(self):
        """List all secret names for this server.

        Returns:
            List of secret names
        """
        index = self._get_secret_index()
        return list(index) if index else []

    def initialize(self, server_name):
        """Initialize the secrets manager for a specific MCP server.

        Args:
            server_name: The name of the MCP server (e.g., 'findmy-server', 'google-maps-server')
        """
        self._initalize_manager(server_name)

    def _get_secret_index(self):
        """Get the index of all secrets for this server"""
        index_username = "__secret_index__"
        index_data = keyring.get_password(self.service_name, index_username)
        return self._deserialize_index_content(index_data)

    def _update_secret_index(self, secret_name):
        """Update the index to include a new secret"""
        index = self._get_secret_index()
        index.add(secret_name)  # Add to set
        index_username = "__secret_index__"
        keyring.set_password(self.service_name, index_username, self._serialize_index_content(index))

    def _remove_from_secret_index(self, secret_name):
        """Remove a secret from the index"""
        index = self._get_secret_index()
        index.discard(secret_name)  # Remove from set (safe if not present)
        if index:  # If there are still secrets, update the index
            index_username = "__secret_index__"
            keyring.set_password(self.service_name, index_username, self._serialize_index_content(index))
        else:  # If no secrets left, remove the index entirely
            index_username = "__secret_index__"
            try:
                keyring.delete_password(self.service_name, index_username)
            except Exception:
                pass  # Index might not exist, that's fine
        
    def _delete_all_secrets(self):
        """Delete all secrets for this server"""
        index = self._get_secret_index()
        for secret_name in index:
            self.delete_secret(secret_name)
        # Finally, delete the index
        try:
            keyring.delete_password(self.service_name, "__secret_index__")
        except Exception:
            pass  # Index might not exist, that's fine

    def clear_server_secrets(self):
        """Clear all secrets for this server"""
        self._delete_all_secrets()


def get_secrets_manager(server_name):
    """Create a new secrets manager instance for the given server.

    Args:
        server_name: The name of the MCP server (e.g., 'findmy-server', 'google-maps-server')

    Returns:
        A new MCPSecretsManager instance
    """
    return MCPSecretsManager(server_name)


# Global static instance
secrets_manager = MCPSecretsManager()



def test_create():
    manager = MCPSecretsManager("example_server")
    manager.store_secret("example_secret", "secret_value")
    print(manager.retrieve_secret("example_secret"))
    print(manager.list_secrets())
    manager.clear_server_secrets()
    print(manager.list_secrets())

if __name__ == "__main__":
    test_create()