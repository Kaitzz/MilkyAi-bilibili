"""Small, implementation-independent contracts used by the public skeleton."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class DeliveryChannel(StrEnum):
    COMMENT = "comment"
    DM = "dm"
    EMAIL = "email"


@dataclass(frozen=True)
class RequestContext:
    request_id: str
    user_id: int
    bvid: str
    page: int = 1

    def __post_init__(self) -> None:
        if self.page < 1:
            raise ValueError("page must be at least 1")


@dataclass(frozen=True)
class MaterialBundle:
    title: str
    transcript: str
    language: str | None = None


@dataclass(frozen=True)
class GeneratedArtifact:
    kind: str
    content: str


@dataclass(frozen=True)
class DeliveryResult:
    ok: bool
    channel: DeliveryChannel
    reason: str | None = None

