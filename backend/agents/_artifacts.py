from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


class GuidelineChunk(BaseModel):
    chunk_id:     str
    doc_id:       int
    heading_path: str
    text:         str
    score:        float


class GuidelinesArtifact(BaseModel):
    kind:    Literal["guidelines"] = "guidelines"
    query:   str
    results: list[GuidelineChunk]


class FassChunk(BaseModel):
    chunk_id:       str
    doc_folder:     str
    lakemedel:      str
    substans:       str | None = None
    beredningsform: str
    section:        str
    atc_code:       str
    content:        str
    score:          float


class FassArtifact(BaseModel):
    kind:    Literal["fass"] = "fass"
    query:   str
    results: list[FassChunk]


class DrugLabelArtifact(BaseModel):
    kind:      Literal["drug_label"] = "drug_label"
    drug_name: str
    sections:  dict[str, str]


class PubMedAbstractSection(BaseModel):
    label: str | None = None
    text:  str


class PubMedItem(BaseModel):
    pmid:     str
    title:    str
    year:     int | None              = None
    journal:  str | None              = None
    authors:  list[str]               = []
    abstract: list[PubMedAbstractSection] = []
    url:      str


class PubMedArtifact(BaseModel):
    kind:    Literal["pubmed"] = "pubmed"
    query:   str
    results: list[PubMedItem]
