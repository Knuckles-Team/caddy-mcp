"""CONCEPT:CD-OS.config.caddy Dynamic client facade orchestration and resource mappings."""

#!/usr/bin/env python
from importlib.metadata import version as _v

from caddy_mcp.api.api_client_config import Api as ConfigApi

__version__ = _v("caddy-mcp")

__all__ = ["Api", "__version__"]


class Api(ConfigApi):
    pass
