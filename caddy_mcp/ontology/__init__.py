"""Caddy ontology contribution (CONCEPT:AU-KG.ontology.federation-provider-leg).

Data-only subpackage: it carries ``caddy.ttl`` (the ``owl:Ontology``
``http://knuckles.team/kg/caddy`` module) which the Arbora hub federates in via
the ``scion_sdk.ontology_providers`` entry-point. It holds no business logic
and no heavy imports so the hub can resolve it cheaply.
"""
