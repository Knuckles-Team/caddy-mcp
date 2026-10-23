"""CONCEPT:CD-OS.config.caddy Dynamic client facade orchestration and resource mappings."""

#!/usr/bin/env python
from caddy_mcp import __version__  # single source: package __init__
from caddy_mcp.api.api_client_config import Api as ConfigApi

__all__ = ["Api", "__version__"]


class Api(ConfigApi):
    pass
