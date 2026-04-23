from __future__ import annotations
from enum import Enum
from typing import Protocol, runtime_checkable
from pydantic import BaseModel, Field


class AgentCapability(str, Enum):
    CARDIOLOGY  = "cardiology"
    RESEARCH    = "research"
    REGULATORY  = "regulatory"
    DRUG_DOSING = "drug_dosing"

    @property
    def description(self) -> str:
        return {
            AgentCapability.CARDIOLOGY:  "Cardiac conditions, ECG interpretation, cardiology-specific drug use",
            AgentCapability.RESEARCH:    "Evidence grading, clinical studies, treatment guidelines",
            AgentCapability.REGULATORY:  "Swedish regulations, FASS, contraindications, legal constraints",
            AgentCapability.DRUG_DOSING: "Precise dosing calculations, renal/hepatic adjustments",
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


class AgentRequest(BaseModel):
    query:            str
    clinical_context: ClinicalContext = Field(default_factory=ClinicalContext)
    constraints:      list[str]       = Field(default_factory=list)


class AgentResponse(BaseModel):
    answer:          str
    citations:       list[Citation]
    confidence:      float           = Field(ge=0.0, le=1.0)
    reasoning_trace: list[str]
    escalate:        bool            = False
    capability:      AgentCapability


@runtime_checkable
class Agent(Protocol):
    async def __call__(self, request: AgentRequest) -> AgentResponse:
        ...
