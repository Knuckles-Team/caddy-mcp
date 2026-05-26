from typing import Any
from caddy_mcp.api.api_client_base import ApiClientBase


class Api(ApiClientBase):
    def load_config(self, config: Any, config_adapter: str | None = None, force_reload: bool = False) -> dict:
        """Sets Caddy's configuration, overriding any previous configuration.

        Args:
            config: The configuration payload (dict or string).
            config_adapter: Optional config adapter name (e.g. 'caddyfile', 'json5').
            force_reload: If True, forces reload even if the config is identical.
        """
        headers = {}
        if config_adapter:
            if config_adapter == "caddyfile":
                headers["Content-Type"] = "text/caddyfile"
            else:
                headers["Content-Type"] = f"application/{config_adapter}"
        else:
            headers["Content-Type"] = "application/json"

        if force_reload:
            headers["Cache-Control"] = "must-revalidate"

        return self.request("POST", "/load", data=config, headers=headers)

    def stop_server(self) -> dict:
        """Gracefully shuts down the server and exits the process."""
        return self.request("POST", "/stop")

    def get_config(self, path: str = "") -> Any:
        """Exports Caddy's current configuration at the named path."""
        path = path.lstrip("/")
        return self.request("GET", f"/config/{path}")

    def post_config(self, path: str, config: Any, if_match: str | None = None) -> Any:
        """Sets or replaces object, or appends to array at the named path."""
        path = path.lstrip("/")
        headers = {}
        if if_match:
            headers["If-Match"] = if_match
        return self.request("POST", f"/config/{path}", data=config, headers=headers)

    def set_config(self, path: str, config: Any, if_match: str | None = None) -> Any:
        """Alias for post_config."""
        return self.post_config(path, config, if_match=if_match)

    def put_config(self, path: str, config: Any, if_match: str | None = None) -> Any:
        """Creates new object or inserts into array at the named path."""
        path = path.lstrip("/")
        headers = {}
        if if_match:
            headers["If-Match"] = if_match
        return self.request("PUT", f"/config/{path}", data=config, headers=headers)

    def patch_config(self, path: str, config: Any, if_match: str | None = None) -> Any:
        """Replaces an existing object or array element at the named path."""
        path = path.lstrip("/")
        headers = {}
        if if_match:
            headers["If-Match"] = if_match
        return self.request("PATCH", f"/config/{path}", data=config, headers=headers)

    def delete_config(self, path: str = "", if_match: str | None = None) -> Any:
        """Deletes the value at the named path."""
        path = path.lstrip("/")
        headers = {}
        if if_match:
            headers["If-Match"] = if_match
        return self.request("DELETE", f"/config/{path}", headers=headers)

    # @id configuration traversal support
    def get_id(self, id_path: str) -> Any:
        """GET config via @id tag. E.g. id_path='my_proxy/upstreams'"""
        id_path = id_path.lstrip("/")
        return self.request("GET", f"/id/{id_path}")

    def post_id(self, id_path: str, config: Any, if_match: str | None = None) -> Any:
        """POST config via @id tag."""
        id_path = id_path.lstrip("/")
        headers = {}
        if if_match:
            headers["If-Match"] = if_match
        return self.request("POST", f"/id/{id_path}", data=config, headers=headers)

    def put_id(self, id_path: str, config: Any, if_match: str | None = None) -> Any:
        """PUT config via @id tag."""
        id_path = id_path.lstrip("/")
        headers = {}
        if if_match:
            headers["If-Match"] = if_match
        return self.request("PUT", f"/id/{id_path}", data=config, headers=headers)

    def patch_id(self, id_path: str, config: Any, if_match: str | None = None) -> Any:
        """PATCH config via @id tag."""
        id_path = id_path.lstrip("/")
        headers = {}
        if if_match:
            headers["If-Match"] = if_match
        return self.request("PATCH", f"/id/{id_path}", data=config, headers=headers)

    def delete_id(self, id_path: str, if_match: str | None = None) -> Any:
        """DELETE config via @id tag."""
        id_path = id_path.lstrip("/")
        headers = {}
        if if_match:
            headers["If-Match"] = if_match
        return self.request("DELETE", f"/id/{id_path}", headers=headers)

    def adapt_config(self, config: Any, config_adapter: str = "caddyfile") -> Any:
        """Adapts a configuration to Caddy JSON without loading or running it."""
        headers = {}
        if config_adapter == "caddyfile":
            headers["Content-Type"] = "text/caddyfile"
        else:
            headers["Content-Type"] = f"application/{config_adapter}"
        return self.request("POST", "/adapt", data=config, headers=headers)

    def get_pki_ca(self, ca_id: str = "local") -> Any:
        """Returns information about a particular PKI app CA."""
        return self.request("GET", f"/pki/ca/{ca_id}")

    def get_pki_ca_certificates(self, ca_id: str = "local") -> Any:
        """Returns the certificate chain of a particular PKI app CA."""
        return self.request("GET", f"/pki/ca/{ca_id}/certificates")

    def get_reverse_proxy_upstreams(self) -> Any:
        """Returns the current status of the configured reverse proxy upstreams."""
        return self.request("GET", "/reverse_proxy/upstreams")

    def get_routes(self) -> dict:
        """Retrieve Caddy route mappings."""
        return self.request("GET", "/config/apps/http/servers")
