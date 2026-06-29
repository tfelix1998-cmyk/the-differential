"""
gsse_config.py
==============
Configuration for the GSSE module of The Differential.

TWO LAYERS, ONE MODULE
----------------------
1. STUDY STRUCTURE  (gsse_structure.json)
   The roadmap-style tree the user navigates and tracks progress against:
       science  >  topic  >  section  >  subtopic
   Questions attach to a SUBTOPIC (the leaf). This is the primary content model.

2. EXAM BLUEPRINT  (GSSE_CATEGORIES below)
   The RACS exam-question weighting, used only to assemble a representative mock
   paper. Each topic links to one or more blueprint codes via its
   "blueprint_codes" field, so a mock can be built from the study tree.

A subtopic_id ("topic-id/name-slug") is the join key: every question carries one,
and it resolves through its topic to a blueprint code and a science component.
"""

import json
import os
from collections import defaultdict

_HERE = os.path.dirname(os.path.abspath(__file__))
_STRUCTURE_PATH = os.path.join(_HERE, "gsse_structure.json")

with open(_STRUCTURE_PATH, encoding="utf-8") as _f:
    GSSE_STRUCTURE = json.load(_f)

GSSE_TOPICS = GSSE_STRUCTURE["topics"]

# ---------------------------------------------------------------------------
# Components (independently passed — fail one, fail the whole exam)
# ---------------------------------------------------------------------------

GSSE_DOMAINS = {
    "ANATOMY":    {"name": "Anatomy",    "independent_pass": True,
                   "paper": "Exam 1 (Anatomy)", "duration_min": 150,
                   "notes": "60 MCQs (all Type X) plus 20 image-based spots."},
    "PHYSIOLOGY": {"name": "Physiology", "independent_pass": True,
                   "paper": "Exam 2 (Pathology & Physiology)", "duration_min": 150,
                   "notes": "60 questions: 12 Type A, 48 Type X."},
    "PATHOLOGY":  {"name": "Pathology",  "independent_pass": True,
                   "paper": "Exam 2 (Pathology & Physiology)", "duration_min": 150,
                   "notes": "65 questions: 20 Type A, 45 Type X."},
}
# Note: study tree uses the key "science"; it maps 1:1 to these domain keys.

# ---------------------------------------------------------------------------
# Exam blueprint categories (RACS exam-question weights; sum 60/60/65)
# ---------------------------------------------------------------------------

GSSE_CATEGORIES = {
    # ANATOMY (60)
    "ANA-GEN": {"domain": "ANATOMY", "name": "General principles", "exam_weight": 4,  "weight_note": "Published breakdown"},
    "ANA-THX": {"domain": "ANATOMY", "name": "Thorax & Breast",    "exam_weight": 9,  "weight_note": "Published breakdown"},
    "ANA-ABD": {"domain": "ANATOMY", "name": "Abdomen",            "exam_weight": 9,  "weight_note": "Published breakdown"},
    "ANA-PEL": {"domain": "ANATOMY", "name": "Pelvis & Perineum",  "exam_weight": 7,  "weight_note": "Published breakdown"},
    "ANA-UL":  {"domain": "ANATOMY", "name": "Upper Limb",         "exam_weight": 9,  "weight_note": "Published breakdown"},
    "ANA-LL":  {"domain": "ANATOMY", "name": "Lower Limb",         "exam_weight": 9,  "weight_note": "Published breakdown"},
    "ANA-BCK": {"domain": "ANATOMY", "name": "Back & Spine",       "exam_weight": 0,  "weight_note": "No MCQ allocation (spots only)"},
    "ANA-NCK": {"domain": "ANATOMY", "name": "Neck",               "exam_weight": 5,  "weight_note": "Head & Neck share 10; split 5/5"},
    "ANA-HD":  {"domain": "ANATOMY", "name": "Head",               "exam_weight": 5,  "weight_note": "Head & Neck share 10; split 5/5"},
    "ANA-CNS": {"domain": "ANATOMY", "name": "Central Nervous System", "exam_weight": 3, "weight_note": "Published breakdown"},
    # PHYSIOLOGY (60) — RACS confirmed
    "PHY-CVS": {"domain": "PHYSIOLOGY", "name": "Cardiovascular",          "exam_weight": 10, "weight_note": "RACS confirmed"},
    "PHY-RES": {"domain": "PHYSIOLOGY", "name": "Respiratory",             "exam_weight": 10, "weight_note": "RACS confirmed"},
    "PHY-GIT": {"domain": "PHYSIOLOGY", "name": "Gastrointestinal",        "exam_weight": 10, "weight_note": "RACS confirmed"},
    "PHY-REN": {"domain": "PHYSIOLOGY", "name": "Urinary / Renal",         "exam_weight": 10, "weight_note": "RACS confirmed"},
    "PHY-END": {"domain": "PHYSIOLOGY", "name": "Endocrine",               "exam_weight": 5,  "weight_note": "RACS confirmed"},
    "PHY-MET": {"domain": "PHYSIOLOGY", "name": "Metabolism & Nutrition",  "exam_weight": 5,  "weight_note": "RACS confirmed"},
    "PHY-NEU": {"domain": "PHYSIOLOGY", "name": "Neurophysiology",         "exam_weight": 5,  "weight_note": "RACS confirmed"},
    "PHY-BLD": {"domain": "PHYSIOLOGY", "name": "Blood & Haemostasis",     "exam_weight": 5,  "weight_note": "RACS confirmed"},
    # PATHOLOGY (65) — published breakdown
    "PAT-GEN": {"domain": "PATHOLOGY", "name": "General pathology & tissue response", "exam_weight": 22, "weight_note": "Published breakdown"},
    "PAT-NEO": {"domain": "PATHOLOGY", "name": "Neoplasia",                "exam_weight": 12, "weight_note": "Published breakdown"},
    "PAT-GMB": {"domain": "PATHOLOGY", "name": "Genetics & molecular biology", "exam_weight": 11, "weight_note": "Inferred remainder (soft)"},
    "PAT-IMM": {"domain": "PATHOLOGY", "name": "Immunology",               "exam_weight": 6,  "weight_note": "Published breakdown"},
    "PAT-MIC": {"domain": "PATHOLOGY", "name": "Microbiology / antibiotics", "exam_weight": 4, "weight_note": "Published breakdown"},
    "PAT-PHA": {"domain": "PATHOLOGY", "name": "Pharmacology & therapeutics", "exam_weight": 4, "weight_note": "Published breakdown"},
    "PAT-STA": {"domain": "PATHOLOGY", "name": "Statistics",               "exam_weight": 4,  "weight_note": "Published breakdown"},
    "PAT-HAE": {"domain": "PATHOLOGY", "name": "Haematology & transfusion", "exam_weight": 2, "weight_note": "Published breakdown"},
    "PAT-SYS": {"domain": "PATHOLOGY", "name": "Systemic pathology (tag only)", "exam_weight": 0, "weight_note": "Folded into PAT-GEN"},
}

# ---------------------------------------------------------------------------
# Question types
# ---------------------------------------------------------------------------

GSSE_QUESTION_TYPES = {
    "X":    {"name": "Multiple true/false (Type X)", "uses_statements": True,  "in_blueprint": True},
    "A":    {"name": "Single best answer (Type A)",  "uses_statements": False, "in_blueprint": True},
    "SPOT": {"name": "Anatomy spot",                 "uses_statements": False, "in_blueprint": True, "anatomy_only": True},
    "B":    {"name": "Extended matching (Type B)",   "uses_statements": False, "in_blueprint": False},
}

GSSE_MOCK_BLUEPRINT = {
    "ANATOMY":    {"paper": "Exam 1", "duration_min": 150, "mcq_total": 60, "spot_total": 20, "type_split": {"X": 60, "SPOT": 20}},
    "PHYSIOLOGY": {"paper": "Exam 2", "duration_min": 150, "mcq_total": 60, "type_split": {"A": 12, "X": 48}},
    "PATHOLOGY":  {"paper": "Exam 2", "duration_min": 150, "mcq_total": 65, "type_split": {"A": 20, "X": 45}},
}

# ---------------------------------------------------------------------------
# Indexes + helpers
# ---------------------------------------------------------------------------

_TOPIC_BY_ID = {t["id"]: t for t in GSSE_TOPICS}
_SUBTOPIC_BY_ID = {st["id"]: (t, st) for t in GSSE_TOPICS for st in t["subtopics"]}


def topics_for_science(science):
    return [t for t in GSSE_TOPICS if t["science"] == science]


def get_topic(topic_id):
    return _TOPIC_BY_ID.get(topic_id)


def get_subtopic(subtopic_id):
    """Return (topic, subtopic) or (None, None)."""
    return _SUBTOPIC_BY_ID.get(subtopic_id, (None, None))


def sections_of(topic_id):
    t = _TOPIC_BY_ID[topic_id]
    return {sec: [st for st in t["subtopics"] if st["section"] == sec] for sec in t["sections"]}


def blueprint_codes_for_subtopic(subtopic_id):
    """Which RACS exam-blueprint category/categories a subtopic feeds."""
    t, _ = get_subtopic(subtopic_id)
    return t["blueprint_codes"] if t else []


def science_of_subtopic(subtopic_id):
    t, _ = get_subtopic(subtopic_id)
    return t["science"] if t else None


def study_blocks_by_science():
    out = defaultdict(float)
    for t in GSSE_TOPICS:
        out[t["science"]] += sum(st["blocks"] for st in t["subtopics"])
    return dict(out)


def validate():
    """Structural integrity checks."""
    errs = []
    # unique subtopic ids
    ids = [st["id"] for t in GSSE_TOPICS for st in t["subtopics"]]
    if len(ids) != len(set(ids)):
        errs.append("duplicate subtopic ids")
    # every blueprint_code is real
    for t in GSSE_TOPICS:
        for code in t["blueprint_codes"]:
            if code not in GSSE_CATEGORIES:
                errs.append(f"{t['id']}: unknown blueprint code {code}")
    # exam blueprint reconciles
    for dom, total in {"ANATOMY": 60, "PHYSIOLOGY": 60, "PATHOLOGY": 65}.items():
        s = sum(v["exam_weight"] for v in GSSE_CATEGORIES.values() if v["domain"] == dom)
        if s != total:
            errs.append(f"{dom} blueprint sums to {s}, expected {total}")
    return errs


if __name__ == "__main__":
    print(f"Topics: {len(GSSE_TOPICS)}   Subtopics: {len(_SUBTOPIC_BY_ID)}")
    for sci in ("ANATOMY", "PHYSIOLOGY", "PATHOLOGY"):
        ts = topics_for_science(sci)
        print(f"  {sci:<11} topics={len(ts):>2}  study blocks={study_blocks_by_science().get(sci, 0)}")
    errs = validate()
    print("validate:", "OK" if not errs else errs)
