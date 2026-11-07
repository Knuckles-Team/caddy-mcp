"""Surface contracts: tool use, links, data locations and business roles."""

from scion_sdk.surface_contracts import (
    BusinessRole,
    DataLocation,
    Refusal,
    SurfaceLink,
    ToolStep,
    ToolUseContract,
)

CONTRACTS = (
    ToolUseContract(
        task="inspect-ingress-config",
        description="Read the live Caddy configuration, its HTTP routes and one node by @id.",
        steps=(
            ToolStep(
                tool="caddy_get_config",
                params=("path",),
                result=("config",),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the credential lacks access to the operation"
                    ),
                    Refusal(
                        "INVALID_ARGUMENT", "the upstream system rejects the input"
                    ),
                ),
            ),
            ToolStep(
                tool="caddy_get_routes",
                params=(),
                result=("servers", "routes"),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the credential lacks access to the operation"
                    ),
                    Refusal(
                        "INVALID_ARGUMENT", "the upstream system rejects the input"
                    ),
                ),
            ),
            ToolStep(
                tool="caddy_get_id",
                params=("id_path",),
                result=("config",),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the credential lacks access to the operation"
                    ),
                    Refusal(
                        "INVALID_ARGUMENT", "the upstream system rejects the input"
                    ),
                ),
            ),
        ),
    ),
    ToolUseContract(
        task="add-route",
        description="Add a route or a config node under a scoped path or @id, after validating a Caddyfile.",
        steps=(
            ToolStep(
                tool="caddy_get_config",
                params=("path",),
                result=("config",),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the credential lacks access to the operation"
                    ),
                    Refusal(
                        "INVALID_ARGUMENT", "the upstream system rejects the input"
                    ),
                ),
            ),
            ToolStep(
                tool="caddy_adapt_config",
                params=("config", "config_adapter"),
                result=("result", "warnings"),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the credential lacks access to the operation"
                    ),
                    Refusal(
                        "INVALID_ARGUMENT", "the upstream system rejects the input"
                    ),
                ),
            ),
            ToolStep(
                tool="caddy_post_config",
                params=("path", "config", "if_match", "confirm"),
                result=("result",),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the credential lacks access to the operation"
                    ),
                    Refusal(
                        "INVALID_ARGUMENT", "the upstream system rejects the input"
                    ),
                    Refusal(
                        "CONFIRMATION_REQUIRED",
                        "the caller has not confirmed the destructive call",
                    ),
                ),
            ),
            ToolStep(
                tool="caddy_post_id",
                params=("id_path", "config", "if_match", "confirm"),
                result=("result",),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the credential lacks access to the operation"
                    ),
                    Refusal(
                        "INVALID_ARGUMENT", "the upstream system rejects the input"
                    ),
                    Refusal(
                        "CONFIRMATION_REQUIRED",
                        "the caller has not confirmed the destructive call",
                    ),
                ),
            ),
            ToolStep(
                tool="caddy_set_config",
                params=("path", "config", "if_match", "confirm"),
                result=("result",),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the credential lacks access to the operation"
                    ),
                    Refusal(
                        "INVALID_ARGUMENT", "the upstream system rejects the input"
                    ),
                    Refusal(
                        "CONFIRMATION_REQUIRED",
                        "the caller has not confirmed the destructive call",
                    ),
                ),
            ),
            ToolStep(
                tool="caddy_get_routes",
                params=(),
                result=("servers", "routes"),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the credential lacks access to the operation"
                    ),
                    Refusal(
                        "INVALID_ARGUMENT", "the upstream system rejects the input"
                    ),
                ),
            ),
        ),
    ),
    ToolUseContract(
        task="change-route",
        description="Replace or patch an existing route, handler or @id node in place.",
        steps=(
            ToolStep(
                tool="caddy_get_id",
                params=("id_path",),
                result=("config",),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the credential lacks access to the operation"
                    ),
                    Refusal(
                        "INVALID_ARGUMENT", "the upstream system rejects the input"
                    ),
                ),
            ),
            ToolStep(
                tool="caddy_put_id",
                params=("id_path", "config", "if_match", "confirm"),
                result=("result",),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the credential lacks access to the operation"
                    ),
                    Refusal(
                        "INVALID_ARGUMENT", "the upstream system rejects the input"
                    ),
                    Refusal(
                        "CONFIRMATION_REQUIRED",
                        "the caller has not confirmed the destructive call",
                    ),
                ),
            ),
            ToolStep(
                tool="caddy_patch_id",
                params=("id_path", "config", "if_match", "confirm"),
                result=("result",),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the credential lacks access to the operation"
                    ),
                    Refusal(
                        "INVALID_ARGUMENT", "the upstream system rejects the input"
                    ),
                    Refusal(
                        "CONFIRMATION_REQUIRED",
                        "the caller has not confirmed the destructive call",
                    ),
                ),
            ),
            ToolStep(
                tool="caddy_put_config",
                params=("path", "config", "if_match", "confirm"),
                result=("result",),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the credential lacks access to the operation"
                    ),
                    Refusal(
                        "INVALID_ARGUMENT", "the upstream system rejects the input"
                    ),
                    Refusal(
                        "CONFIRMATION_REQUIRED",
                        "the caller has not confirmed the destructive call",
                    ),
                ),
            ),
            ToolStep(
                tool="caddy_patch_config",
                params=("path", "config", "if_match", "confirm"),
                result=("result",),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the credential lacks access to the operation"
                    ),
                    Refusal(
                        "INVALID_ARGUMENT", "the upstream system rejects the input"
                    ),
                    Refusal(
                        "CONFIRMATION_REQUIRED",
                        "the caller has not confirmed the destructive call",
                    ),
                ),
            ),
            ToolStep(
                tool="caddy_get_routes",
                params=(),
                result=("servers", "routes"),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the credential lacks access to the operation"
                    ),
                    Refusal(
                        "INVALID_ARGUMENT", "the upstream system rejects the input"
                    ),
                ),
            ),
        ),
    ),
    ToolUseContract(
        task="remove-route",
        description="Delete a route or config node by @id or config path, with confirmation.",
        steps=(
            ToolStep(
                tool="caddy_get_id",
                params=("id_path",),
                result=("config",),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the credential lacks access to the operation"
                    ),
                    Refusal(
                        "INVALID_ARGUMENT", "the upstream system rejects the input"
                    ),
                ),
            ),
            ToolStep(
                tool="caddy_delete_id",
                params=("id_path", "if_match", "confirm"),
                result=("result",),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the credential lacks access to the operation"
                    ),
                    Refusal(
                        "INVALID_ARGUMENT", "the upstream system rejects the input"
                    ),
                    Refusal(
                        "CONFIRMATION_REQUIRED",
                        "the caller has not confirmed the destructive call",
                    ),
                    Refusal("NOT_FOUND", "no node carries the @id"),
                ),
            ),
            ToolStep(
                tool="caddy_get_config",
                params=("path",),
                result=("config",),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the credential lacks access to the operation"
                    ),
                    Refusal(
                        "INVALID_ARGUMENT", "the upstream system rejects the input"
                    ),
                ),
            ),
            ToolStep(
                tool="caddy_delete_config",
                params=("path", "if_match", "confirm"),
                result=("result",),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the credential lacks access to the operation"
                    ),
                    Refusal(
                        "INVALID_ARGUMENT", "the upstream system rejects the input"
                    ),
                    Refusal(
                        "CONFIRMATION_REQUIRED",
                        "the caller has not confirmed the destructive call",
                    ),
                    Refusal("NOT_FOUND", "the config path does not exist"),
                ),
            ),
            ToolStep(
                tool="caddy_get_routes",
                params=(),
                result=("servers", "routes"),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the credential lacks access to the operation"
                    ),
                    Refusal(
                        "INVALID_ARGUMENT", "the upstream system rejects the input"
                    ),
                ),
            ),
        ),
    ),
    ToolUseContract(
        task="reload-whole-config",
        description="Validate a Caddyfile or JSON document and load it as the whole live configuration.",
        steps=(
            ToolStep(
                tool="caddy_get_config",
                params=("path",),
                result=("config",),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the credential lacks access to the operation"
                    ),
                    Refusal(
                        "INVALID_ARGUMENT", "the upstream system rejects the input"
                    ),
                ),
            ),
            ToolStep(
                tool="caddy_adapt_config",
                params=("config", "config_adapter"),
                result=("result",),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the credential lacks access to the operation"
                    ),
                    Refusal(
                        "INVALID_ARGUMENT", "the upstream system rejects the input"
                    ),
                ),
            ),
            ToolStep(
                tool="caddy_load_config",
                params=("config", "config_adapter", "force_reload", "confirm"),
                result=("result",),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the credential lacks access to the operation"
                    ),
                    Refusal(
                        "INVALID_ARGUMENT", "the upstream system rejects the input"
                    ),
                    Refusal(
                        "CONFIRMATION_REQUIRED",
                        "the caller has not confirmed the destructive call",
                    ),
                ),
            ),
            ToolStep(
                tool="caddy_get_routes",
                params=(),
                result=("servers", "routes"),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the credential lacks access to the operation"
                    ),
                    Refusal(
                        "INVALID_ARGUMENT", "the upstream system rejects the input"
                    ),
                ),
            ),
        ),
    ),
    ToolUseContract(
        task="stop-edge-proxy",
        description="Gracefully stop the live Caddy process. This takes the edge proxy offline.",
        steps=(
            ToolStep(
                tool="caddy_get_routes",
                params=(),
                result=("servers", "routes"),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the credential lacks access to the operation"
                    ),
                    Refusal(
                        "INVALID_ARGUMENT", "the upstream system rejects the input"
                    ),
                ),
            ),
            ToolStep(
                tool="caddy_stop_server",
                params=("confirm",),
                result=("result",),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the credential lacks access to the operation"
                    ),
                    Refusal(
                        "INVALID_ARGUMENT", "the upstream system rejects the input"
                    ),
                    Refusal(
                        "CONFIRMATION_REQUIRED",
                        "the caller has not confirmed the destructive call",
                    ),
                ),
            ),
        ),
    ),
    ToolUseContract(
        task="review-pki",
        description="Read the PKI authorities and the certificates they issued.",
        steps=(
            ToolStep(
                tool="caddy_get_pki_ca",
                params=("ca_id",),
                result=("id", "name", "root_certificate"),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the credential lacks access to the operation"
                    ),
                    Refusal(
                        "INVALID_ARGUMENT", "the upstream system rejects the input"
                    ),
                    Refusal("NOT_FOUND", "no CA has the id"),
                ),
            ),
            ToolStep(
                tool="caddy_get_pki_ca_certificates",
                params=("ca_id",),
                result=("certificates",),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the credential lacks access to the operation"
                    ),
                    Refusal(
                        "INVALID_ARGUMENT", "the upstream system rejects the input"
                    ),
                ),
            ),
        ),
    ),
    ToolUseContract(
        task="check-upstream-health",
        description="Read reverse-proxy upstream health and load.",
        steps=(
            ToolStep(
                tool="caddy_get_reverse_proxy_upstreams",
                params=(),
                result=("address", "num_requests", "fails"),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the credential lacks access to the operation"
                    ),
                    Refusal(
                        "INVALID_ARGUMENT", "the upstream system rejects the input"
                    ),
                ),
            ),
        ),
    ),
    ToolUseContract(
        task="scrape-diagnostics",
        description="Read Prometheus metrics, expvar and pprof profiles from the admin endpoint.",
        steps=(
            ToolStep(
                tool="caddy_get_metrics",
                params=(),
                result=("result",),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the credential lacks access to the operation"
                    ),
                    Refusal(
                        "INVALID_ARGUMENT", "the upstream system rejects the input"
                    ),
                ),
            ),
            ToolStep(
                tool="caddy_get_debug_vars",
                params=(),
                result=("result",),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the credential lacks access to the operation"
                    ),
                    Refusal(
                        "INVALID_ARGUMENT", "the upstream system rejects the input"
                    ),
                ),
            ),
            ToolStep(
                tool="caddy_get_debug_pprof",
                params=("profile", "params"),
                result=("result",),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the credential lacks access to the operation"
                    ),
                    Refusal(
                        "INVALID_ARGUMENT", "the upstream system rejects the input"
                    ),
                ),
            ),
        ),
    ),
    ToolUseContract(
        task="map-topology",
        description="Ingest servers, routes and upstreams into the knowledge graph.",
        steps=(
            ToolStep(
                tool="caddy_ingest_topology",
                params=(),
                result=("upstreams_listed", "servers_listed", "ingested"),
                refusals=(
                    Refusal(
                        "ACCESS_DENIED", "the credential lacks access to the operation"
                    ),
                    Refusal(
                        "INVALID_ARGUMENT", "the upstream system rejects the input"
                    ),
                ),
            ),
        ),
    ),
)

LINKS = (
    SurfaceLink(
        task="inspect-ingress-config",
        tools=("caddy_get_config", "caddy_get_routes", "caddy_get_id"),
        prompts=(
            "caddy-mcp-operator",
            "caddy-mcp-ingress-administrator",
            "caddy-mcp-platform-observer",
        ),
        skills=("caddy-mcp-operations",),
    ),
    SurfaceLink(
        task="add-route",
        tools=(
            "caddy_get_config",
            "caddy_adapt_config",
            "caddy_post_config",
            "caddy_post_id",
            "caddy_set_config",
            "caddy_get_routes",
        ),
        prompts=("caddy-mcp-operator", "caddy-mcp-ingress-administrator"),
        skills=("caddy-mcp-operations", "caddy-route-manager"),
    ),
    SurfaceLink(
        task="change-route",
        tools=(
            "caddy_get_id",
            "caddy_put_id",
            "caddy_patch_id",
            "caddy_put_config",
            "caddy_patch_config",
            "caddy_get_routes",
        ),
        prompts=("caddy-mcp-operator", "caddy-mcp-ingress-administrator"),
        skills=("caddy-mcp-operations", "caddy-route-manager"),
    ),
    SurfaceLink(
        task="remove-route",
        tools=(
            "caddy_get_id",
            "caddy_delete_id",
            "caddy_get_config",
            "caddy_delete_config",
            "caddy_get_routes",
        ),
        prompts=("caddy-mcp-operator", "caddy-mcp-ingress-administrator"),
        skills=("caddy-mcp-operations", "caddy-route-manager"),
    ),
    SurfaceLink(
        task="reload-whole-config",
        tools=(
            "caddy_get_config",
            "caddy_adapt_config",
            "caddy_load_config",
            "caddy_get_routes",
        ),
        prompts=("caddy-mcp-operator", "caddy-mcp-ingress-administrator"),
        skills=("caddy-mcp-operations",),
    ),
    SurfaceLink(
        task="stop-edge-proxy",
        tools=("caddy_get_routes", "caddy_stop_server"),
        prompts=("caddy-mcp-operator", "caddy-mcp-ingress-administrator"),
        skills=("caddy-mcp-operations",),
    ),
    SurfaceLink(
        task="review-pki",
        tools=("caddy_get_pki_ca", "caddy_get_pki_ca_certificates"),
        prompts=("caddy-mcp-operator", "caddy-mcp-platform-observer"),
        skills=("caddy-mcp-observability",),
    ),
    SurfaceLink(
        task="check-upstream-health",
        tools=("caddy_get_reverse_proxy_upstreams",),
        prompts=("caddy-mcp-operator", "caddy-mcp-platform-observer"),
        skills=("caddy-mcp-observability",),
    ),
    SurfaceLink(
        task="scrape-diagnostics",
        tools=("caddy_get_metrics", "caddy_get_debug_vars", "caddy_get_debug_pprof"),
        prompts=("caddy-mcp-operator", "caddy-mcp-platform-observer"),
        skills=("caddy-mcp-observability",),
    ),
    SurfaceLink(
        task="map-topology",
        tools=("caddy_ingest_topology",),
        prompts=("caddy-mcp-operator", "caddy-mcp-platform-observer"),
        skills=("caddy-mcp-observability",),
    ),
)

LOCATIONS = (
    DataLocation(
        name="caddy-config",
        holds=("ReverseProxy", "Route"),
        instance="CADDY_URL",
        read_tool="caddy_get_routes",
        federation_key="routeId",
    ),
    DataLocation(
        name="caddy-upstreams",
        holds=("Upstream",),
        instance="CADDY_URL",
        read_tool="caddy_get_reverse_proxy_upstreams",
        federation_key="upstreamAddress",
    ),
    DataLocation(
        name="caddy-pki",
        holds=("CertificateAuthority",),
        instance="CADDY_URL",
        read_tool="caddy_get_pki_ca",
    ),
)

ROLES = (
    BusinessRole(
        name="ingress administrator",
        description="Publish, change and retire service routes on the edge proxy on request.",
        tasks=(
            "inspect-ingress-config",
            "add-route",
            "change-route",
            "remove-route",
            "reload-whole-config",
            "stop-edge-proxy",
        ),
    ),
    BusinessRole(
        name="platform observer",
        description="Report edge-proxy health, certificate state and topology without changing anything.",
        tasks=(
            "inspect-ingress-config",
            "review-pki",
            "check-upstream-health",
            "scrape-diagnostics",
            "map-topology",
        ),
    ),
)
