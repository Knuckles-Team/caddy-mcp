# Caddy MCP Agent Specs

<!-- CONCEPT:CADDY-001 -->
<!-- CONCEPT:CADDY-002 -->
<!-- CONCEPT:CADDY-003 -->

This file acts as a machine-readable README for AI coding agents collaborating on this repository.

## Tech Stack & Architecture
- **Language**: Python >= 3.10
- **Ecosystem**: `agent-utilities` Dynamic Facade
- **MCP Server**: FastMCP (stdio and HTTP support)
- **Key Files**:
  - `caddy_mcp/mcp_server.py`: FastMCP entry points and tool registration.
  - `caddy_mcp/api_client.py`: API facade inheriting from custom domain modules.
  - `caddy_mcp/auth.py`: Credentials loading, credential validation, and authentication headers.

## Commands

### Quality & Linting
Run pre-commit hooks locally:
```bash
pre-commit run --all-files
```

### Execution & Run
Launch the FastMCP server in stdio mode:
```bash
python -m caddy_mcp.mcp_server
```

### Testing Suite
Execute the entire test suite:
```bash
pytest -v
```

## Project Structure

### File Tree
```text
.
├── .bumpversion.cfg
├── .gitignore
├── .pre-commit-config.yaml
├── AGENTS.md
├── CHANGELOG.md
├── LICENSE
├── README.md
├── pyproject.toml
├── requirements.txt
├── docs
│   ├── concepts.md
│   ├── index.md
│   └── overview.md
├── docker
│   └── compose.yml
├── prompts
│   └── main_agent.md
├── tests
│   ├── conftest.py
│   ├── test_api_client.py
│   ├── test_concept_parity.py
│   ├── test_init_dynamics.py
│   ├── test_mcp_server.py
│   └── test_startup.py
└── caddy_mcp
    ├── __init__.py
    ├── agent_server.py
    ├── api
    │   ├── api_client_base.py
    │   └── api_client_core.py
    ├── api_client.py
    ├── auth.py
    ├── mcp
    │   └── mcp_core.py
    └── mcp_server.py
```

## Concept Registry

| Concept ID | Name | Description |
|------------|------|-------------|
| `CONCEPT:CADDY-001` | Core API Client Operations | Dynamic API facade client integration |
| `CONCEPT:CADDY-002` | FastMCP Tools Execution | FastMCP tool registration and stdio handling |
| `CONCEPT:CADDY-003` | Identity & Gateway Security | Credential validation and SSL verification |
| `CONCEPT:ECO-4.0` | Ecosystem Compliance | Multi-package integration compliance standard |

---

## When Stuck
1. Check the local mock context implementation in `tests/conftest.py`.
2. Propose an Implementation Plan first before adding new endpoints.
