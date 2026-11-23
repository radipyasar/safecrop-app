"""Checks on backend/data/diseases.json: complete, sourced, and no chemical names or doses."""

import json
import re
from pathlib import Path

import pytest

DATA = Path(__file__).resolve().parents[1] / "data" / "diseases.json"
OUR_8 = ["potato_late_blight", "apple_scab", "rice_stem_borer", "black_gram_yellow_mosaic",
         "pear_leaf_spot", "grape_leaf_blight", "jute_mosaic", "jute_dieback"]
FIELDS = ["id", "kind", "crop", "name_en", "name_bn", "cause_type", "cause", "short", "signs", "do_now",
          "prevention", "see_expert_when", "sources", "checked"]
ASK_OFFICER = "ask your local agriculture officer which product and dose to use"
# common crop chemicals (names only; the app must never name them)
CHEMICALS = ["mancozeb", "metalaxyl", "chlorothalonil", "copper", "sulphur", "sulfur", "carbendazim", "propiconazole",
             "tebuconazole", "azoxystrobin", "difenoconazole", "captan", "imidacloprid", "thiamethoxam", "acetamiprid",
             "chlorpyrifos", "cypermethrin", "carbofuran", "fipronil", "cartap", "flonicamid", "diafenthiuron",
             "malathion", "dimethoate", "lambda", "emamectin", "chlorantraniliprole"]
DOSE = re.compile(r"\d+(\.\d+)?\s*(ml|g|gm|kg|mg|l|litre|liter|ppm|%)\b", re.IGNORECASE)


@pytest.fixture(scope="module")
def data():
    return json.loads(DATA.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def entries(data):
    return {e["id"]: e for e in data["entries"]}


def test_has_our_8_plus_healthy_and_unknown(data, entries):
    assert len(data["entries"]) == 10
    assert set(entries) == set(OUR_8) | {"healthy", "unknown"}


def test_every_entry_has_all_fields(entries):
    for e in entries.values():
        missing = [f for f in FIELDS if f not in e]
        assert not missing, f"{e['id']} is missing {missing}"


@pytest.mark.parametrize("disease_id", OUR_8)
def test_disease_entry_is_complete(entries, disease_id):
    e = entries[disease_id]
    assert e["name_en"] and e["name_bn"] and e["cause"] and e["short"] and e["see_expert_when"]
    assert 3 <= len(e["signs"]) <= 5
    assert e["do_now"] and e["prevention"]
    assert 1 <= len(e["sources"]) <= 3
    for s in e["sources"]:
        assert s["title"] and s["url"].startswith("https://")
    assert any(ASK_OFFICER in step.lower() for step in e["do_now"]), "must send the farmer to the officer for products"


def test_rice_stem_borer_is_marked_as_a_pest(entries):
    e = entries["rice_stem_borer"]
    assert e["kind"] == "pest"
    assert "not a disease" in e["cause"]


def test_no_chemical_names_or_doses(data):
    text = json.dumps(data["entries"], ensure_ascii=False).lower()
    found = [c for c in CHEMICALS if re.search(rf"\b{c}\b", text)]
    assert not found, f"chemical names found: {found}"
    assert not DOSE.search(text), f"looks like a dose: {DOSE.search(text).group(0)}"


def test_helpline_is_set(data):
    assert data["about"]["helpline"]["number"] == "16123"
