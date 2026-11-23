"""The JSON shapes the API sends back (they also make the /docs test page show every field)."""

from typing import Literal

from pydantic import BaseModel, Field


class Health(BaseModel):
    status: str = Field(examples=["ok"])
    model_loaded: bool = Field(description="true once CLIP and the database are loaded and warmed up")
    version: str


class PhotoCheck(BaseModel):
    problem: str = Field(description="clean, gaussian_noise, low_light, jpeg_compression, motion_blur or defocus_blur")
    problem_words: str = Field(description="the problem in plain words, e.g. 'hand-shake blur'")
    level: Literal["L0", "L1", "L2", "L3"] = Field(description="how bad: L0 clean ... L3 severe")
    sure: float = Field(description="how sure the photo check is about the problem (0-1)")
    level_sure: float = Field(description="how sure it is about the level (0-1)")
    signs: list[str] = Field(description="plain-word signs outside the range of our clean photos")
    message: str | None = Field(description="warning for the farmer, or null when the photo looks fine")
    fix_applied: str | None = Field(description="'resample' when a blocky photo was smoothed before CLIP, else null")


class Guess(BaseModel):
    disease_id: str
    disease_name: str
    vote_share: float


class Result(BaseModel):
    decision: Literal["sure", "likely", "not_sure", "healthy", "not_in_list", "retake"]
    reason: str | None = Field(description="why: not_a_leaf, too_unclear, healthy_or_other_unclear, weak_vote or null")
    disease_id: str | None = Field(description="the answer to show (null for retake); for 'healthy' and "
                                               "'not_in_list' a label such as healthy_potato")
    disease_name: str | None
    crop: str | None
    vote_share: float = Field(description="share of the 5-picture vote won by the shown answer (0-1)")
    confidence_words: str = Field(examples=["Very likely"])
    runner_up: Guess | None = Field(description="the next best guess (for option C: the healthy / look-alike label)")
    tip: str | None = Field(description="what to do next, e.g. how to retake a clearer photo")
    best_similarity: float = Field(description="similarity of the closest database picture (low = maybe not a leaf)")


class Neighbour(BaseModel):
    disease_id: str
    disease_name: str
    thumb_url: str = Field(description="clean 200 x 200 thumbnail, e.g. /static/thumbs/apple_scab_001.jpg")
    similarity: float


class Timing(BaseModel):
    read: float = Field(description="ms to open the upload and cut the 224 x 224 square")
    photo_check: float
    embed: float = Field(description="ms for CLIP")
    search: float = Field(description="ms for the database search, vote and decision")
    total: float


class CheckResponse(BaseModel):
    check_id: str
    photo_check: PhotoCheck
    result: Result
    neighbours: list[Neighbour]
    timing_ms: Timing


class Advice(BaseModel):
    source: Literal["gemini", "fallback"] = Field(description="who wrote the advice")
    agrees: Literal["yes", "no", "unsure"] = Field(description="Gemini's second opinion on CLIP's answer "
                                                               "(always 'unsure' for the fallback or without a photo)")
    summary: str
    steps: list[str] = Field(description="3-5 short steps")
    see_expert_when: str
    safety_note: str
    lang: Literal["en", "bn"] = Field(description="language of the text (the fallback is always English)")
    fallback_reason: str | None = Field(description="no_key, quota, timeout, error, client_error, unsafe, retake "
                                                    "or null when Gemini answered")
    cached: bool = Field(description="true when the same check + language was answered before")
    timing_ms: float | None = None


class Source(BaseModel):
    title: str
    url: str


class DiseaseSummary(BaseModel):
    id: str
    kind: Literal["disease", "pest"]
    group: Literal["A", "B"] = Field(description="A = info-rich, B = info-scarce")
    crop: str
    name_en: str
    name_bn: str
    short: str
    thumb_url: str | None = Field(description="clean thumbnail of one of our photos")


class DiseaseDetail(DiseaseSummary):
    cause_type: str
    cause: str
    signs: list[str]
    do_now: list[str]
    prevention: list[str]
    see_expert_when: str
    looks_like: list[str]
    sources: list[Source]
    photos: list[str] = Field(description="up to 6 clean thumbnails of our photos of this disease")
    photo_credit: str | None = Field(description="where our photos come from, with the licence")
    helpline: str = Field(examples=["16123"])
