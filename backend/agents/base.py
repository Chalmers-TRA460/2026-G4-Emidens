from __future__ import annotations
from datetime import datetime, timezone
from enum import Enum
from typing import Protocol, runtime_checkable
from pydantic import BaseModel, Field


class AgentCapability(str, Enum):
    CARDIOLOGY     = "cardiology"
    RESEARCH       = "research"
    PHARMACEUTICAL = "pharmaceutical"

    @property
    def description(self) -> str:
        return {
            AgentCapability.CARDIOLOGY:     "Cardiac conditions, ECG interpretation, cardiology-specific drug use",
            AgentCapability.RESEARCH:       "Evidence grading, clinical studies, treatment guidelines",
            AgentCapability.PHARMACEUTICAL: "Drug dosing, adverse effects, drug-drug interactions, and contraindications",
        }[self]


class ClinicalContext(BaseModel):
    age_years:           int   | None = None
    weight_kg:           float | None = None
    active_conditions:   list[str]    = Field(default_factory=list)
    current_medications: list[str]    = Field(default_factory=list)
    renal_impairment:    bool         = False
    hepatic_impairment:  bool         = False


class Citation(BaseModel):
    source:     str
    section:    str
    location:   str
    confidence: float = Field(ge=0.0, le=1.0)


class TraceStep(BaseModel):
    agent:     str
    message:   str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def formatted_time(self) -> str:
        return self.timestamp.isoformat(timespec="milliseconds")

    @classmethod
    def from_messages(cls, agent: str, messages: list[str]) -> list[TraceStep]:
        now = datetime.now(timezone.utc)
        return [cls(agent=agent, message=m, timestamp=now) for m in messages]


class AgentRequest(BaseModel):
    query:            str
    task:             str | None      = None
    clinical_context: ClinicalContext = Field(default_factory=ClinicalContext)
    constraints:      list[str]       = Field(default_factory=list)


class AgentResponse(BaseModel):
    answer:           str
    citations:        list[Citation]
    confidence:       float           = Field(ge=0.0, le=1.0)
    reasoning_trace:  list[TraceStep]
    escalate:         bool            = False
    capability:       AgentCapability
    requested_inputs: list[str]       = Field(default_factory=list)


@runtime_checkable
class Agent(Protocol):
    async def __call__(self, request: AgentRequest) -> AgentResponse:
        ...
