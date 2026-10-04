"""Structural interfaces at MilkyAi's service boundaries.

Production adapters are intentionally not included in this repository.
"""

from __future__ import annotations

from typing import Protocol, Sequence

from .domain import DeliveryChannel, DeliveryResult, GeneratedArtifact, MaterialBundle, RequestContext


class ArtifactStore(Protocol):
    async def get(self, *, bvid: str, page: int, kind: str) -> GeneratedArtifact | None:
        """Return a reusable artifact, if one exists."""

    async def put(self, *, request: RequestContext, artifact: GeneratedArtifact) -> None:
        """Persist a newly generated artifact."""


class MaterialService(Protocol):
    async def collect(self, request: RequestContext) -> MaterialBundle:
        """Return normalized video material for generation."""


class GenerationService(Protocol):
    async def generate_notes(self, material: MaterialBundle) -> GeneratedArtifact:
        """Generate a complete Markdown notes artifact."""

    async def answer_support(self, *, message: str, context: str, knowledge: Sequence[str]) -> str:
        """Generate one grounded customer-service response."""


class DeliveryService(Protocol):
    async def deliver(
        self,
        *,
        request: RequestContext,
        channel: DeliveryChannel,
        artifact: GeneratedArtifact,
    ) -> DeliveryResult:
        """Deliver an artifact using channel-specific semantics."""


class KnowledgeRetriever(Protocol):
    async def search(self, query: str, *, limit: int = 6) -> Sequence[str]:
        """Retrieve stable product knowledge relevant to a support question."""


class CustomerContextService(Protocol):
    async def for_user(self, user_id: int) -> str:
        """Render bounded, trusted context for the authenticated sender."""

