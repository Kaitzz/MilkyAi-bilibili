"""Illustrative workflow orchestration using constructor-injected services."""

from __future__ import annotations

from dataclasses import dataclass

from .domain import DeliveryChannel, DeliveryResult, GeneratedArtifact, RequestContext
from .ports import (
    ArtifactStore,
    CustomerContextService,
    DeliveryService,
    GenerationService,
    KnowledgeRetriever,
    MaterialService,
)


@dataclass
class EmailNotesWorkflow:
    artifacts: ArtifactStore
    materials: MaterialService
    generator: GenerationService
    delivery: DeliveryService

    async def run(self, request: RequestContext) -> DeliveryResult:
        notes = await self.artifacts.get(bvid=request.bvid, page=request.page, kind="notes_md")
        if notes is None:
            material = await self.materials.collect(request)
            notes = await self.generator.generate_notes(material)
            await self.artifacts.put(request=request, artifact=notes)

        return await self.delivery.deliver(
            request=request,
            channel=DeliveryChannel.EMAIL,
            artifact=notes,
        )


@dataclass
class CustomerServiceWorkflow:
    context: CustomerContextService
    knowledge: KnowledgeRetriever
    generator: GenerationService
    delivery: DeliveryService

    async def run(self, request: RequestContext, message: str) -> DeliveryResult:
        trusted_context = await self.context.for_user(request.user_id)
        knowledge = await self.knowledge.search(message)
        reply = await self.generator.answer_support(
            message=message,
            context=trusted_context,
            knowledge=knowledge,
        )
        return await self.delivery.deliver(
            request=request,
            channel=DeliveryChannel.DM,
            artifact=GeneratedArtifact(kind="customer_reply", content=reply),
        )

