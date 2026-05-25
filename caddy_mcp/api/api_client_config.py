from caddy_mcp.api.api_client_base import ApiClientBase


class Api(ApiClientBase):
    def get_config(self, path: str = "") -> dict:
        """Get Caddy configuration."""
        return self.request("GET", f"/config/{path}")

    def set_config(self, path: str, config: dict) -> dict:
        """Set Caddy configuration."""
        return self.request("POST", f"/config/{path}", data=config)

    def delete_config(self, path: str) -> dict:
        """Delete Caddy configuration."""
        return self.request("DELETE", f"/config/{path}")

    def load_config(self, config_str: str, config_type: str = "json") -> dict:
        """Load a complete Caddy configuration."""
        headers = {
            "Content-Type": "application/json" if config_type == "json" else "text/yaml"
        }
        return self.request("POST", "/load", data=config_str)

    def get_routes(self) -> dict:
        """Retrieve Caddy route mappings."""
        return self.request("GET", "/config/apps/http/servers")
