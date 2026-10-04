"""Public architecture skeleton for MilkyAi.

This package is illustrative and is not the production application.
"""

from .domain import (
    DeliveryChannel,
    DeliveryResult,
    GeneratedArtifact,
    MaterialBundle,
    RequestContext,
)

__all__ = [
    "DeliveryChannel",
    "DeliveryResult",
    "GeneratedArtifact",
    "MaterialBundle",
    "RequestContext",
]

