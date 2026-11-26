"""Advice for one check: Gemini 3.5 Flash-Lite writes it from the checked facts in data/diseases.json,
or we build it from those facts ourselves (the fallback) when Gemini is slow, out of quota, offline or unsafe.

Rules (from CLAUDE.md; the decision rule changed on 26 Nov 2026, decided by Nabil):
- CLIP answers first. Gemini looks at the photo and gives its own answer (gemini_label, gemini_name, gemini_sure)
  and a second opinion (`agrees`). final_answer() decides what the farmer sees:
    agrees yes / unsure                         -> CLIP's answer stays
    agrees no + gemini_sure high / medium:
        gemini_label is one of our 8            -> that disease becomes the answer ("second_check"); a second Gemini
                                                   call writes the advice from that disease's facts
        healthy / other                         -> "not in our list" with Gemini's words
    agrees no but it can't name it (sure low)   -> "not sure", label other_unknown
- Gemini may use only the given facts. No chemical names, no doses: every answer is checked, and an answer that
  breaks this rule is thrown away and replaced by the fallback.
- The farmer's photo is used for this one request only and never stored.
"""

import io
import json
import logging
import os
import re
import threading
import time
from collections import OrderedDict
from pathlib import Path
from typing import Literal

from PIL import Image
from pydantic import BaseModel, Field

log = logging.getLogger("safecrop.advice")

DEFAULT_MODEL = "gemini-3.5-flash-lite"
TIMEOUT_S = 20      # per try
TRIES = 2           # the first try + one retry
KEEP = 1000         # Gemini answers kept in memory, by (check_id, lang)
PHOTO_MAX_SIDE = 768

LANGS = {"en": "English", "bn": "Bangla (বাংলা), in simple words a farmer in Bangladesh uses"}
ASK_OFFICER = "Ask your local agriculture officer which product and dose to use."
ASK_OFFICER_BN = "কোন ওষুধ কতটুকু ব্যবহার করবেন, তা আপনার স্থানীয় কৃষি কর্মকর্তার কাছে জেনে নিন।"

# Common crop chemicals: neither the facts nor Gemini may name them (tests check diseases.json with the same list)
CHEMICALS = ["mancozeb", "metalaxyl", "chlorothalonil", "copper", "sulphur", "sulfur", "carbendazim", "propiconazole",
             "tebuconazole", "azoxystrobin", "difenoconazole", "captan", "imidacloprid", "thiamethoxam", "acetamiprid",
             "chlorpyrifos", "cypermethrin", "carbofuran", "fipronil", "cartap", "flonicamid", "diafenthiuron",
             "malathion", "dimethoate", "lambda", "emamectin", "chlorantraniliprole", "bordeaux"]
# a number followed by a unit, e.g. "2 g", "1.5 ml", "50%", "২ গ্রাম"
DOSE = re.compile(r"(\d+(\.\d+)?\s*(ml|g|gm|kg|mg|l|litre|liter|ppm|%)(?![a-z]))"
                  r"|([০-৯]+\s*(গ্রাম|মিলি|কেজি|লিটার|%))", re.IGNORECASE)


def unsafe_words(text):
    """Chemical names or doses found in a piece of text (empty list = safe)."""
    low = text.lower()
    found = [c for c in CHEMICALS if re.search(rf"\b{re.escape(c)}\b", low)]
    found += [m.group(0) for m in DOSE.finditer(text)]
    return found


OUR_IDS = ("potato_late_blight", "apple_scab", "rice_stem_borer", "black_gram_yellow_mosaic", "pear_leaf_spot",
           "grape_leaf_blight", "jute_mosaic", "jute_dieback")  # tests check these match diseases.json
OTHER_UNKNOWN = "other_unknown"
GeminiLabel = Literal[OUR_IDS + ("healthy", "other")]
NO_OPINION = {"gemini_label": None, "gemini_name": None, "gemini_sure": None}
ADVICE_TEXT = ("summary", "steps", "see_expert_when", "safety_note")


class GeminiAdvice(BaseModel):
    """The JSON shape Gemini must answer in (sent to Gemini as its response schema)."""
    gemini_label: GeminiLabel = Field(
        description="What YOU see in the photo: one of the 8 ids, 'healthy' (a healthy plant) or 'other' (anything "
                    "else: another crop, another problem, not a plant).")
    gemini_name: str = Field(description="Your own short words for what you see, e.g. 'pumpkin leaf with yellowing'.")
    gemini_sure: Literal["high", "medium", "low"] = Field(description="How sure you are of gemini_label.")
    agrees: Literal["yes", "no", "unsure"] = Field(
        description="Does the leaf in the photo look like the app's answer? 'unsure' if you cannot tell.")
    summary: str = Field(description="2 short sentences in plain words.")
    steps: list[str] = Field(description="3 to 5 short steps the farmer can do now, from the facts only.")
    see_expert_when: str = Field(description="One sentence: when to call an expert.")
    safety_note: str = Field(description="One sentence: no spray without asking the local agriculture officer.")


SYSTEM = """You help farmers in Bangladesh. A photo app (SafeCrop) has already looked at a leaf photo and given an answer
(APP ANSWER). You do two things: (A) give your own opinion of the photo, (B) write short, practical advice.

(A) Your own opinion. Look at the photo yourself before you read the app's answer.
- "gemini_label": what the photo shows. Use one of these ids only if the photo really shows it:
  potato_late_blight, apple_scab, rice_stem_borer (an insect pest of rice: dead hearts or white, empty rice heads),
  black_gram_yellow_mosaic, pear_leaf_spot, grape_leaf_blight, jute_mosaic, jute_dieback.
  Use "healthy" for a healthy plant, and "other" for anything else (another crop, another problem, not a plant).
- "gemini_name": your own short words for what you see, e.g. "pumpkin leaf with yellow patches" or
  "dry grass seed heads, not a crop leaf". Write it in English.
- "gemini_sure": "high", "medium" or "low": how sure you are of gemini_label and gemini_name.
- "agrees": "yes" if the photo matches the app's answer, "no" if it clearly does not, "unsure" if you cannot tell.
  Without a photo: agrees = "unsure", gemini_label = "other", gemini_name = "", gemini_sure = "low".

(B) Advice rules:
1. If agrees is "yes" or "unsure", write the advice about the app's answer, from FACTS.
   If agrees is "no", do NOT give advice for the app's answer: start the summary with what you see (gemini_name),
   say it may be a problem SafeCrop does not know, and make "show the leaf to your local agriculture officer" the first
   step. Give no treatment steps then.
2. Use ONLY the facts given in FACTS. Do not add any treatment, product or method that is not in the facts.
3. Never write a chemical name, a product name, a dose or an amount. For any spray or medicine write that the
   farmer should ask the local agriculture officer which product and dose to use.
4. Simple words, short sentences, no technical terms. Write everything in the requested language.
5. When agrees is "yes" or "unsure", start the summary by saying the app's answer in a natural sentence that fits
   the decision:
   sure -> "SafeCrop thinks this is very likely <answer>."; likely -> "SafeCrop thinks this is likely <answer>.";
   second_check -> "SafeCrop's second check thinks this is <answer>.";
   not_sure -> "SafeCrop is not sure. The closest match is <answer>."; healthy -> "This leaf looks healthy.";
   not_in_list -> "This may be a problem SafeCrop doesn't know yet." These English sentences only show the meaning:
   write them in the requested LANGUAGE. Never paste the confidence words in as they are.
   If the app is not sure or the photo has a problem, say so in the second sentence and make "take a clearer photo"
   one step.
"""


def photo_jpeg(img):
    """PIL image -> small JPEG bytes for Gemini (longest side at most 768 px). Never saved anywhere."""
    img = img.convert("RGB")
    img.thumbnail((PHOTO_MAX_SIDE, PHOTO_MAX_SIDE))
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85)
    return buf.getvalue()


def load_facts(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return data["about"], {e["id"]: e for e in data["entries"]}


def facts_id(result):
    """Which diseases.json entry belongs to a check result (None for a retake)."""
    d = result["decision"]
    if d == "retake":
        return None
    if d == "healthy":
        return "healthy"
    if d == "not_in_list" or result["disease_id"] not in OUR_IDS:
        return "unknown"
    return result["disease_id"]  # sure / likely / not_sure / second_check: one of our 8


def clip_final(r):
    """The final answer when CLIP's answer stays."""
    return {"source": "clip", **{k: r.get(k) for k in ("decision", "reason", "disease_id", "disease_name", "crop",
                                                         "confidence_words")}}


def final_answer(r, a, facts):
    """The decision rule (26 Nov 2026). r: CLIP's result. a: Gemini's cleaned answer (or None). -> final answer."""
    if a is None or a["agrees"] != "no":
        return clip_final(r)
    label, name, sure = a.get("gemini_label"), (a.get("gemini_name") or "").strip(), a.get("gemini_sure")
    if sure not in ("high", "medium") or not label or not name or label == r.get("disease_id"):
        # "no", but it can't name it (or names the same thing it said no to)
        return {"source": "gemini", "decision": "not_sure", "reason": "second_check_unknown",
                "disease_id": OTHER_UNKNOWN, "disease_name": name or "Unknown", "crop": None,
                "confidence_words": "Not sure"}
    if label in OUR_IDS:
        e = facts[label]
        return {"source": "gemini", "decision": "second_check", "reason": None, "disease_id": label,
                "disease_name": e["name_en"], "crop": e["crop"], "confidence_words": "From our second check"}
    return {"source": "gemini", "decision": "not_in_list", "reason": "second_check_other", "disease_id": OTHER_UNKNOWN,
            "disease_name": name, "crop": None, "confidence_words": "Not in our list"}


def as_result(final, clip_result):
    """A final 'second_check' answer in the shape of a check result, so the advice is written about it."""
    return {**final, "vote_share": 0.0, "runner_up": None, "tip": None,
            "best_similarity": clip_result.get("best_similarity"), "first_check": clip_result.get("disease_name")}


class Advisor:
    """Loaded once at start-up. advise() is safe to call from several requests at once."""

    def __init__(self, facts_path, api_key=None, model=None):
        self.about, self.facts = load_facts(facts_path)
        self.api_key = api_key
        self.model = model or DEFAULT_MODEL
        self._client = None
        self._cache = OrderedDict()
        self._lock = threading.Lock()

    @classmethod
    def from_env(cls, facts_path):
        return cls(facts_path, api_key=os.getenv("GEMINI_API_KEY") or None, model=os.getenv("GEMINI_MODEL"))

    # ---------- public ----------

    def advise(self, check_id, check, lang="en", photo=None):
        """check: what /api/check remembered (result, photo_check ...). photo: JPEG bytes or None.
        Returns the /api/advice answer; never raises because of Gemini."""
        lang = lang if lang in LANGS else "en"
        t0 = time.perf_counter()
        with self._lock:
            cached = self._cache.get((check_id, lang))
        if cached:
            return {**cached, "cached": True, "timing_ms": round((time.perf_counter() - t0) * 1000, 1)}

        r = check["result"]
        answer, why = None, None
        if facts_id(r) is None:
            why = "retake"  # nothing to advise about; the fallback tells the farmer how to retake
        elif not self.api_key:
            why = "no_key"
        else:
            answer, why = self._ask_gemini(check, lang, photo)

        if answer is None:
            out = {**self.fallback(check), "fallback_reason": why, **NO_OPINION, "final": clip_final(r)}
        else:
            final = final_answer(r, answer, self.facts)
            out = {"source": "gemini", **answer, "lang": lang, "fallback_reason": None, "final": final}
            if final["decision"] == "second_check":
                # Gemini named one of our 8: write the advice again, from THAT disease's facts
                second = {**check, "result": as_result(final, r)}
                again, why2 = self._ask_gemini(second, lang, None)
                if again is None:
                    fb = self.fallback(second)
                    out.update({k: fb[k] for k in ADVICE_TEXT}, source="fallback", lang=fb["lang"],
                               fallback_reason=why2)
                else:
                    out.update({k: again[k] for k in ADVICE_TEXT})
            if out["source"] == "gemini":
                with self._lock:
                    self._cache[(check_id, lang)] = out
                    while len(self._cache) > KEEP:
                        self._cache.popitem(last=False)
        return {**out, "cached": False, "timing_ms": round((time.perf_counter() - t0) * 1000, 1)}

    def fallback(self, check):
        """The same answer shape, built only from diseases.json (always English, 'agrees' is unsure)."""
        r, pc = check["result"], check["photo_check"]
        fid = facts_id(r)
        helpline = self.about["helpline"]["number"]
        safety = f"Do not use any spray or medicine without advice. {ASK_OFFICER} Krishi Call Centre: {helpline}."
        base = {"source": "fallback", "agrees": "unsure", "lang": "en", "safety_note": safety}

        if fid is None:
            tip = r.get("tip") or "Take a new photo of one leaf, close up, in good light."
            return {**base, "summary": "SafeCrop can't read this photo. A clearer photo gives a much better answer.",
                    "steps": [tip, "Hold the phone steady and tap the leaf on the screen to focus.",
                              "Take the photo in daylight, but not in harsh direct sun.",
                              "Fill most of the picture with one leaf."],
                    "see_expert_when": f"If you are worried about your crop, call the Krishi Call Centre at {helpline}."}

        e = self.facts[fid]
        name, crop = r.get("disease_name") or e["name_en"], r.get("crop")
        runner = (r.get("runner_up") or {}).get("disease_name")
        d = r["decision"]
        if d == "second_check":
            first = r.get("first_check")
            was = f" (the closest picture match was {first})" if first else ""
            summary = f"SafeCrop's second check thinks this is {name}{was}. {e['short']}"
        elif d == "sure":
            summary = f"SafeCrop thinks this is very likely {name}. {e['short']}"
        elif d == "likely":
            also = f", but it could also be {runner}" if runner else ""
            summary = f"SafeCrop thinks this is likely {name}{also}. {e['short']}"
        elif d == "not_sure":
            also = f", or it could be {runner}" if runner else ""
            summary = f"SafeCrop is not sure. The closest match is {name}{also}. Take a clearer photo to check."
        elif d == "healthy":
            summary = f"This {crop + ' ' if crop else ''}leaf looks healthy. Keep checking your plants."
        else:  # not_in_list
            summary = (f"This may be a problem SafeCrop doesn't know yet. It looks most like {name}, "
                       "which is not one of the 8 problems SafeCrop covers.")

        steps = list(e["do_now"])
        if d in ("likely", "not_sure") and r.get("tip"):
            steps.insert(0, r["tip"])
        elif pc.get("message") and d != "healthy":
            steps.insert(0, pc["message"])
        steps += [p for p in e["prevention"] if len(steps) < 3]
        return {**base, "summary": summary, "steps": steps[:5], "see_expert_when": e["see_expert_when"]}

    # ---------- Gemini ----------

    def _client_once(self):
        if self._client is None:
            from google import genai  # imported here so the server starts even without the package
            self._client = genai.Client(api_key=self.api_key)
        return self._client

    def prompt(self, check, lang, has_photo):
        r, pc = check["result"], check["photo_check"]
        e = self.facts[facts_id(r)]
        facts = {k: e[k] for k in ("name_en", "kind", "cause", "short", "signs", "do_now", "prevention",
                                   "see_expert_when", "looks_like")}
        app_answer = {
            "decision": r["decision"], "confidence_words": r["confidence_words"],
            "answer": r.get("disease_name"), "crop": r.get("crop"),
            "could_also_be": (r.get("runner_up") or {}).get("disease_name"),
            "note": {"healthy": "The app thinks the leaf is healthy.",
                     "not_in_list": "The app thinks this is a problem it does not cover; tell the farmer to ask an expert.",
                     "not_sure": "The app is NOT sure; the answer is only the closest match.",
                     "second_check": "A second, closer look at the photo found this answer. The app's first check "
                                     f"(picture comparison) said {r.get('first_check')}. Write the advice about this "
                                     "answer.",
                     }.get(r["decision"]),
        }
        photo = {"problem": pc["problem_words"], "level": pc["level"], "warning": pc.get("message")}
        return (f"LANGUAGE: {LANGS[lang]}\n"
                f"APP ANSWER: {json.dumps(app_answer, ensure_ascii=False)}\n"
                f"PHOTO CHECK (L0 clean ... L3 very unclear): {json.dumps(photo, ensure_ascii=False)}\n"
                f"FACTS: {json.dumps(facts, ensure_ascii=False)}\n"
                f"HELPLINE: Krishi Call Centre {self.about['helpline']['number']}\n"
                f"PHOTO: {'attached' if has_photo else 'none (answer agrees = unsure)'}")

    def _ask_gemini(self, check, lang, photo):
        """-> (answer dict, None) or (None, why it failed)."""
        from google.genai import errors, types

        contents = [self.prompt(check, lang, photo is not None)]
        if photo is not None:
            contents.append(types.Part.from_bytes(data=photo, mime_type="image/jpeg"))
        config = types.GenerateContentConfig(
            system_instruction=SYSTEM, temperature=0.2, max_output_tokens=800,
            response_mime_type="application/json", response_schema=GeminiAdvice,
            http_options=types.HttpOptions(timeout=TIMEOUT_S * 1000))

        why = "error"
        for attempt in range(1, TRIES + 1):
            try:
                resp = self._client_once().models.generate_content(model=self.model, contents=contents, config=config)
                parsed = resp.parsed if isinstance(resp.parsed, GeminiAdvice) else GeminiAdvice.model_validate_json(resp.text)
                return self._clean(parsed, lang, photo is not None)
            except errors.ClientError as e:  # 4xx: bad key, quota used up ... a retry won't help
                why = "quota" if getattr(e, "code", None) == 429 else "client_error"
                log.warning("Gemini refused (try %d): %s %s", attempt, getattr(e, "code", "?"), type(e).__name__)
                break
            except UnsafeAdvice as e:
                why = "unsafe"
                log.warning("Gemini advice dropped (try %d): it named %s", attempt, e)
                break
            except Exception as e:  # timeout, 5xx, bad JSON, no internet
                why = "timeout" if "timeout" in type(e).__name__.lower() or "timed out" in str(e).lower() else "error"
                log.warning("Gemini failed (try %d): %s", attempt, type(e).__name__)
        return None, why

    def _clean(self, a, lang, has_photo):
        steps = [s.strip() for s in a.steps if s and s.strip()][:5]
        if not a.summary.strip() or not steps:
            raise ValueError("empty advice")
        out = {"agrees": a.agrees if has_photo else "unsure", "summary": a.summary.strip(), "steps": steps,
               "see_expert_when": a.see_expert_when.strip(), "safety_note": a.safety_note.strip()}
        if has_photo:  # Gemini's own answer only counts when it saw the photo
            out.update(gemini_label=a.gemini_label, gemini_name=a.gemini_name.strip()[:120], gemini_sure=a.gemini_sure)
        else:
            out.update(NO_OPINION)
        bad = unsafe_words(" ".join([out["summary"], *steps, out["see_expert_when"], out["safety_note"],
                                     out["gemini_name"] or ""]))
        if bad:
            raise UnsafeAdvice(", ".join(sorted(set(bad))))
        must = ASK_OFFICER_BN if lang == "bn" else ASK_OFFICER
        if not any(w in out["safety_note"].lower() for w in ("officer", "কর্মকর্তা", "অফিসার")):
            out["safety_note"] = f"{out['safety_note']} {must}".strip()
        return out, None


class UnsafeAdvice(Exception):
    """Gemini's answer named a chemical or a dose."""
