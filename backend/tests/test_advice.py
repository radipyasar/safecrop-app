"""app/advice.py without the internet: a fake Gemini stands in for the real one (no key, no quota used)."""

import json
from pathlib import Path
from types import SimpleNamespace

import pytest
from google.genai import errors

from app.advice import ASK_OFFICER, OUR_IDS, Advisor, GeminiAdvice, facts_id, final_answer

FACTS = Path(__file__).resolve().parents[1] / "data" / "diseases.json"
GOOD = {"gemini_label": "potato_late_blight", "gemini_name": "potato leaf with dark wet patches", "gemini_sure": "high",
        "agrees": "yes", "summary": "SafeCrop thinks this is very likely Potato late blight. It spreads fast.",
        "steps": ["Check the field today.", "Pull out sick plants.", "Water the soil, not the leaves."],
        "see_expert_when": "If many plants have spots.",
        "safety_note": "Never spray without asking your local agriculture officer."}


def make_check(decision="sure", disease_id="potato_late_blight", name="Potato late blight", crop="potato",
               runner_up=None, level="L0", message=None, tip=None):
    return {"result": {"decision": decision, "reason": None, "disease_id": disease_id, "disease_name": name,
                       "crop": crop, "vote_share": 1.0, "confidence_words": "Very likely", "runner_up": runner_up,
                       "tip": tip, "best_similarity": 0.95},
            "photo_check": {"problem": "clean", "problem_words": "clear photo", "level": level, "sure": 0.9,
                            "level_sure": 0.9, "signs": [], "message": message, "fix_applied": None}}


class FakeGemini:
    """Answers with the given replies in order: a dict (a JSON answer) or an exception to raise."""

    def __init__(self, *replies):
        self.replies, self.calls = list(replies), []
        self.models = self

    def generate_content(self, model, contents, config):
        self.calls.append(contents)
        reply = self.replies.pop(0)
        if isinstance(reply, Exception):
            raise reply
        return SimpleNamespace(parsed=GeminiAdvice(**reply), text=json.dumps(reply))


def advisor_with(*replies):
    a = Advisor(FACTS, api_key="test-key-not-real")
    a._client = FakeGemini(*replies)
    return a


def test_gemini_answer_is_used():
    a = advisor_with(GOOD)
    out = a.advise("c1", make_check(), "en", photo=b"jpeg")
    assert out["source"] == "gemini" and out["agrees"] == "yes" and out["fallback_reason"] is None
    assert out["steps"] == GOOD["steps"]
    assert len(a._client.calls[0]) == 2  # the prompt + the photo


def test_answer_is_cached_by_check_and_language():
    a = advisor_with(GOOD, GOOD)
    a.advise("c1", make_check(), "en", photo=b"jpeg")
    again = a.advise("c1", make_check(), "en", photo=b"jpeg")
    assert again["cached"] is True and len(a._client.calls) == 1  # no second call to Gemini
    a.advise("c1", make_check(), "bn", photo=b"jpeg")
    assert len(a._client.calls) == 2  # another language is a new answer


def test_without_photo_agrees_is_unsure():
    a = advisor_with(GOOD)
    out = a.advise("c1", make_check(), "en", photo=None)
    assert out["agrees"] == "unsure" and len(a._client.calls[0]) == 1


def test_no_key_gives_fallback():
    a = Advisor(FACTS, api_key=None)
    out = a.advise("c1", make_check(), "en")
    assert out["source"] == "fallback" and out["fallback_reason"] == "no_key"
    assert ASK_OFFICER in out["safety_note"] and "16123" in out["safety_note"]
    assert 3 <= len(out["steps"]) <= 5


def test_one_retry_then_success():
    a = advisor_with(TimeoutError("timed out"), GOOD)
    out = a.advise("c1", make_check(), "en", photo=b"jpeg")
    assert out["source"] == "gemini" and len(a._client.calls) == 2


def test_two_failures_give_fallback():
    a = advisor_with(TimeoutError("timed out"), TimeoutError("timed out"))
    out = a.advise("c1", make_check(), "en", photo=b"jpeg")
    assert out["source"] == "fallback" and out["fallback_reason"] == "timeout"


def test_fallback_is_not_cached():
    a = advisor_with(TimeoutError("x"), TimeoutError("x"), GOOD)
    assert a.advise("c1", make_check(), "en")["source"] == "fallback"
    assert a.advise("c1", make_check(), "en")["source"] == "gemini"  # a later try can still get Gemini


def test_quota_used_up_gives_fallback_without_retry():
    a = advisor_with(errors.ClientError(429, {"error": {"message": "quota"}}), GOOD)
    out = a.advise("c1", make_check(), "en", photo=b"jpeg")
    assert out["source"] == "fallback" and out["fallback_reason"] == "quota"
    assert len(a._client.calls) == 1


def test_advice_with_a_chemical_or_dose_is_dropped():
    for bad in ("Spray mancozeb on the leaves.", "Mix 2 g in one litre of water."):
        a = advisor_with({**GOOD, "steps": [bad, "Pull out sick plants.", "Check the field."]})
        out = a.advise("c1", make_check(), "en", photo=b"jpeg")
        assert out["source"] == "fallback" and out["fallback_reason"] == "unsafe"


def test_safety_sentence_is_added_when_missing():
    a = advisor_with({**GOOD, "safety_note": "Be careful."})
    out = a.advise("c1", make_check(), "en", photo=b"jpeg")
    assert out["safety_note"].endswith(ASK_OFFICER)


def test_retake_never_calls_gemini():
    a = advisor_with(GOOD)
    out = a.advise("c1", make_check("retake", None, None, None, tip="Hold the phone steady."), "en")
    assert out["source"] == "fallback" and out["fallback_reason"] == "retake" and not a._client.calls
    assert out["steps"][0] == "Hold the phone steady."


@pytest.mark.parametrize("decision,disease_id,expected", [
    ("sure", "apple_scab", "apple_scab"), ("likely", "jute_mosaic", "jute_mosaic"),
    ("not_sure", "jute_dieback", "jute_dieback"), ("healthy", "healthy_potato", "healthy"),
    ("not_in_list", "other_grape_esca", "unknown"), ("retake", None, None)])
def test_facts_for_each_decision(decision, disease_id, expected):
    assert facts_id({"decision": decision, "disease_id": disease_id}) == expected


@pytest.mark.parametrize("check,words", [
    (make_check("healthy", "healthy_potato", "Healthy potato leaf"), "looks healthy"),
    (make_check("not_in_list", "other_grape_esca", "Grape esca", "grape"), "doesn't know yet"),
    (make_check("not_sure", "jute_dieback", "Jute dieback", "jute",
                runner_up={"disease_id": "healthy_grape", "disease_name": "Healthy grape leaf", "vote_share": 0.6},
                tip="Take a clearer photo."), "not sure"),
    (make_check("likely", "jute_mosaic", "Jute mosaic", "jute", tip="Your photo is blurry."), "likely Jute mosaic"),
])
def test_fallback_wording_for_each_decision(check, words):
    out = Advisor(FACTS, api_key=None).advise("c1", check, "en")
    assert words in out["summary"]
    assert 3 <= len(out["steps"]) <= 5


def test_prompt_keeps_clips_answer_and_facts():
    a = Advisor(FACTS, api_key=None)
    text = a.prompt(make_check(), "bn", has_photo=True)
    assert "Potato late blight" in text and "Bangla" in text and "16123" in text
    assert "sources" not in text  # links are for people, not for Gemini


# ------------------------------------------------------------------ 26 Nov: Gemini's own answer + the decision rule
def gemini_says(label, name, sure, agrees="no", **extra):
    return {**GOOD, "gemini_label": label, "gemini_name": name, "gemini_sure": sure, "agrees": agrees,
            "summary": "This looks like something else. SafeCrop may not know this problem.",
            "steps": ["Show the leaf to your local agriculture officer.", "Take a clear photo of one leaf."], **extra}


SECOND = {**GOOD, "summary": "SafeCrop's second check thinks this is Jute mosaic. It spreads by insects.",
          "steps": ["Pull out sick jute plants.", "Keep weeds down.", "Check the field each week."]}


def test_our_ids_match_the_facts():
    ids = [e["id"] for e in json.loads(FACTS.read_text(encoding="utf-8"))["entries"] if e["kind"] in ("disease", "pest")]
    assert sorted(ids) == sorted(OUR_IDS)


def test_gemini_agrees_keeps_clips_answer():
    out = advisor_with(GOOD).advise("c1", make_check(), "en", photo=b"jpeg")
    assert out["final"]["source"] == "clip" and out["final"]["disease_id"] == "potato_late_blight"
    assert out["gemini_label"] == "potato_late_blight" and out["gemini_sure"] == "high"


def test_gemini_unsure_keeps_clips_answer():
    out = advisor_with(gemini_says("jute_mosaic", "jute leaf", "high", agrees="unsure")).advise(
        "c1", make_check(), "en", photo=b"jpeg")
    assert out["final"]["source"] == "clip" and out["final"]["decision"] == "sure"


def test_override_shows_geminis_disease_with_its_facts():
    a = advisor_with(gemini_says("jute_mosaic", "jute leaf with yellow mosaic", "medium"), SECOND)
    out = a.advise("c1", make_check(), "en", photo=b"jpeg")
    f = out["final"]
    assert f["source"] == "gemini" and f["decision"] == "second_check" and f["disease_id"] == "jute_mosaic"
    assert f["disease_name"] == "Jute mosaic" and f["crop"] == "jute"
    assert out["summary"] == SECOND["summary"] and out["agrees"] == "no"
    second = a._client.calls[1]
    assert len(second) == 1 and "Jute mosaic" in second[0] and "second_check" in second[0]  # its facts, no photo


def test_override_advice_falls_back_to_that_diseases_facts():
    a = advisor_with(gemini_says("jute_mosaic", "jute leaf with yellow mosaic", "high"), TimeoutError("x"),
                     TimeoutError("x"))
    out = a.advise("c1", make_check(), "en", photo=b"jpeg")
    assert out["final"]["disease_id"] == "jute_mosaic" and out["source"] == "fallback"
    assert "second check thinks this is Jute mosaic" in out["summary"] and "Potato late blight" in out["summary"]


def test_override_to_something_else_is_not_in_our_list_with_geminis_words():
    out = advisor_with(gemini_says("other", "pumpkin leaf with yellowing", "high")).advise(
        "c1", make_check(), "en", photo=b"jpeg")
    f = out["final"]
    assert f["decision"] == "not_in_list" and f["disease_id"] == "other_unknown"
    assert f["disease_name"] == "pumpkin leaf with yellowing" and f["reason"] == "second_check_other"
    assert out["summary"].startswith("This looks like something else")  # Gemini's "no" advice, no second call


def test_healthy_from_gemini_is_also_not_in_our_list():
    f = advisor_with(gemini_says("healthy", "healthy rice plant", "medium")).advise(
        "c1", make_check(), "en", photo=b"jpeg")["final"]
    assert f["decision"] == "not_in_list" and f["disease_name"] == "healthy rice plant"


@pytest.mark.parametrize("label,name,sure", [("other", "something odd", "low"), ("other", "", "high"),
                                             ("potato_late_blight", "potato leaf", "high")])
def test_no_but_cant_name_it_gives_other_unknown(label, name, sure):
    f = advisor_with(gemini_says(label, name, sure)).advise("c1", make_check(), "en", photo=b"jpeg")["final"]
    assert f["source"] == "gemini" and f["decision"] == "not_sure" and f["disease_id"] == "other_unknown"
    assert f["reason"] == "second_check_unknown"


def test_without_photo_gemini_has_no_answer_of_its_own():
    out = advisor_with(gemini_says("other", "pumpkin leaf", "high")).advise("c1", make_check(), "en", photo=None)
    assert out["agrees"] == "unsure" and out["gemini_label"] is None and out["final"]["source"] == "clip"


def test_fallback_keeps_clips_answer():
    out = Advisor(FACTS, api_key=None).advise("c1", make_check(), "en")
    assert out["final"] == final_answer(make_check()["result"], None, {}) and out["final"]["source"] == "clip"


def test_a_chemical_in_geminis_words_is_dropped():
    out = advisor_with(gemini_says("other", "leaf sprayed with mancozeb", "high")).advise(
        "c1", make_check(), "en", photo=b"jpeg")
    assert out["source"] == "fallback" and out["fallback_reason"] == "unsafe"
