"""Keep docs pushes separate from guarded package publication."""

from fnmatch import fnmatchcase
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = "ed8ea8ac5989cbc883c149843b311aeecb44e6a2"


def _workflow(name):
    return yaml.safe_load((ROOT / ".github/workflows" / name).read_text())


def _push_matches(workflow, ref):
    # PyYAML's YAML 1.1 reader represents the Actions "on" key as True.
    push = workflow[True]["push"]
    kind, name = ref.removeprefix("refs/").split("/", 1)
    filters = push.get({"heads": "branches", "tags": "tags"}[kind], [])
    return any(fnmatchcase(name, pattern) for pattern in filters)


def test_release_hook_inherits_catalogue_policy():
    config = yaml.safe_load((ROOT / ".pre-commit-config.yaml").read_text())
    matches = [
        (repo, hook)
        for repo in config["repos"]
        for hook in repo["hooks"]
        if hook["id"] == "dependency-readiness"
    ]
    assert len(matches) == 1
    repo, hook = matches[0]
    assert repo["repo"] == "https://github.com/Knuckles-Team/pipelines"
    assert repo["rev"] == "main"
    assert hook == {"id": "dependency-readiness"}


def test_development_skill_is_source_backed():
    skill = (ROOT / "caddy_mcp/skills/caddy-mcp-development/SKILL.md").read_text()
    for fragment in (
        "caddy_mcp/__init__.py",
        "caddy_mcp/mcp/mcp_config.py",
        "CADDY_URL",
        "CADDY_TOKEN",
        "Rapid delivery: the 5-minute contract",
        "tests/test_mcp_server.py",
        "spec_dashboard_enabled",
    ):
        assert fragment in skill
