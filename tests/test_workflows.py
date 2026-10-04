from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from milky_ai.domain import DeliveryChannel, DeliveryResult, GeneratedArtifact, MaterialBundle, RequestContext
from milky_ai.workflows import CustomerServiceWorkflow, EmailNotesWorkflow


class FakeArtifacts:
    def __init__(self, existing: GeneratedArtifact | None = None) -> None:
        self.existing = existing
        self.writes: list[GeneratedArtifact] = []

    async def get(self, **_: object) -> GeneratedArtifact | None:
        return self.existing

    async def put(self, *, artifact: GeneratedArtifact, **_: object) -> None:
        self.writes.append(artifact)


class FakeMaterials:
    def __init__(self) -> None:
        self.calls = 0

    async def collect(self, request: RequestContext) -> MaterialBundle:
        self.calls += 1
        return MaterialBundle(title=request.bvid, transcript="A useful transcript")


class FakeGenerator:
    def __init__(self) -> None:
        self.note_calls = 0
        self.support_calls = 0

    async def generate_notes(self, material: MaterialBundle) -> GeneratedArtifact:
        self.note_calls += 1
        return GeneratedArtifact(kind="notes_md", content=f"# {material.title}")

    async def answer_support(self, **_: object) -> str:
        self.support_calls += 1
        return "Grounded answer"


class FakeDelivery:
    def __init__(self) -> None:
        self.artifacts: list[GeneratedArtifact] = []

    async def deliver(self, *, channel: DeliveryChannel, artifact: GeneratedArtifact, **_: object) -> DeliveryResult:
        self.artifacts.append(artifact)
        return DeliveryResult(ok=True, channel=channel)


class FakeContext:
    async def for_user(self, user_id: int) -> str:
        return f"trusted user={user_id}"


class FakeKnowledge:
    async def search(self, query: str, *, limit: int = 6) -> list[str]:
        return [f"knowledge for {query}"][:limit]


class WorkflowTests(unittest.IsolatedAsyncioTestCase):
    async def test_email_notes_reuses_existing_artifact(self) -> None:
        existing = GeneratedArtifact(kind="notes_md", content="# Stored")
        artifacts = FakeArtifacts(existing)
        materials = FakeMaterials()
        generator = FakeGenerator()
        delivery = FakeDelivery()
        workflow = EmailNotesWorkflow(artifacts, materials, generator, delivery)

        result = await workflow.run(RequestContext("req-1", 42, "BVexample01"))

        self.assertTrue(result.ok)
        self.assertEqual(result.channel, DeliveryChannel.EMAIL)
        self.assertEqual(materials.calls, 0)
        self.assertEqual(generator.note_calls, 0)
        self.assertEqual(delivery.artifacts, [existing])

    async def test_email_notes_generates_and_persists_on_miss(self) -> None:
        artifacts = FakeArtifacts()
        materials = FakeMaterials()
        generator = FakeGenerator()
        delivery = FakeDelivery()
        workflow = EmailNotesWorkflow(artifacts, materials, generator, delivery)

        await workflow.run(RequestContext("req-2", 42, "BVexample02", page=2))

        self.assertEqual(materials.calls, 1)
        self.assertEqual(generator.note_calls, 1)
        self.assertEqual(len(artifacts.writes), 1)
        self.assertEqual(delivery.artifacts, artifacts.writes)

    async def test_customer_service_combines_retrieval_and_user_context(self) -> None:
        generator = FakeGenerator()
        delivery = FakeDelivery()
        workflow = CustomerServiceWorkflow(FakeContext(), FakeKnowledge(), generator, delivery)

        result = await workflow.run(RequestContext("req-3", 7, "BVcontext01"), "Where is my email?")

        self.assertTrue(result.ok)
        self.assertEqual(result.channel, DeliveryChannel.DM)
        self.assertEqual(generator.support_calls, 1)
        self.assertEqual(delivery.artifacts[0].kind, "customer_reply")


if __name__ == "__main__":
    unittest.main()
