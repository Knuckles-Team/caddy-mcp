"""CONCEPT:AU-ECO.messaging.native-backend-abstraction Unified ecosystem initialization dynamic check."""

import importlib
import inspect
from typing import Any

__version__ = "0.32.0"
__all__: list[str] = []

CORE_MODULES = ["caddy_mcp.api_client"]
OPTIONAL_MODULES = {
    "caddy_mcp.mcp_server": "mcp",
}


def _expose_members(module):
    for name, obj in inspect.getmembers(module):
        if (inspect.isclass(obj) or inspect.isfunction(obj)) and not name.startswith(
            "_"
        ):
            globals()[name] = obj
            if name not in __all__:
                __all__.append(name)


for module_name in CORE_MODULES:
    module = importlib.import_module(module_name)
    _expose_members(module)

_loaded_optional_modules: dict[str, Any] = {}


def _import_module_safely(module_name: str):
    try:
        return importlib.import_module(module_name)
    except ImportError:
        return None


# Availability flags map to the substring identifying their optional module.
_AVAILABILITY_FLAGS = {
    "_MCP_AVAILABLE": "mcp_server",
    "_AGENT_AVAILABLE": "agent_server",
}

_MISSING = object()


def _optional_module_available(substring: str) -> bool:
    module_name = next((k for k in OPTIONAL_MODULES if substring in k), None)
    if module_name is None:
        return False
    return _import_module_safely(module_name) is not None


def _load_optional_module_attribute(module_name: str, name: str) -> Any:
    """Lazily import ``module_name`` and return its ``name`` attribute, or ``_MISSING``."""
    if module_name not in _loaded_optional_modules:
        module = _import_module_safely(module_name)
        if module is not None:
            _loaded_optional_modules[module_name] = module
            _expose_members(module)

    module = _loaded_optional_modules.get(module_name)
    if module is not None and hasattr(module, name):
        return getattr(module, name)
    return _MISSING


def __getattr__(name: str) -> Any:
    if name in _AVAILABILITY_FLAGS:
        return _optional_module_available(_AVAILABILITY_FLAGS[name])

    for module_name in OPTIONAL_MODULES:
        value = _load_optional_module_attribute(module_name, name)
        if value is not _MISSING:
            return value

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    return sorted(list(globals().keys()) + __all__)
