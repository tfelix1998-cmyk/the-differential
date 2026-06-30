"""
uq_config.py
============
Configuration for the UQ module of The Differential — UQ Critical Care Module
content (Emergency Medicine & Trauma / Anaesthesia & Pain Management /
Intensive Care) plus the Orthopaedic Trauma Framework viva, organised the same
way as GSSE:
    section  >  topic   (leaf — questions attach here)

Question content itself lives elsewhere and is NOT duplicated here:
  - MCQ banks:  imported_questions.IMPORTED_BANKS
  - Viva banks: imported_questions.IMPORTED_VIVA
  - Orthopaedic Trauma Framework viva: builtin_questions.BUILTIN_VIVA

This module only defines the navigable tree and the bank-name lookups that
join a topic to its question bank(s). Bank names follow the convention used
throughout imported_questions.py:
    "<Course> :: <Section> - <Topic> (MCQ|VIVA)"
"""

import re

_COURSE = "UQ Critical Care Module"

# (section, topic name) pairs, in the order of the original unit outline.
# Each pair has both an MCQ bank and a VIVA bank in imported_questions.py.
_UQ_BANKS = [
    ("Emergency Medicine and Trauma", "Emergency Medicine, Care and Triage"),
    ("Emergency Medicine and Trauma", "Anaphylaxis"),
    ("Emergency Medicine and Trauma", "Toxicology"),
    ("Emergency Medicine and Trauma", "Emergency Mental Health Presentations"),
    ("Emergency Medicine and Trauma", "Major Trauma"),
    ("Emergency Medicine and Trauma", "The Breathless Patient"),
    ("Emergency Medicine and Trauma", "Chest Pain"),
    ("Emergency Medicine and Trauma", "Arrhythmia"),
    ("Emergency Medicine and Trauma", "Altered Level of Consciousness"),
    ("Emergency Medicine and Trauma", "Stroke and Subarachnoid Haemorrhage"),
    ("Emergency Medicine and Trauma", "Traumatic Brain Injury"),
    ("Emergency Medicine and Trauma", "Procedures"),
    ("Emergency Medicine and Trauma", "Principles of Ultrasound in Critical Care"),
    ("Anaesthesia and Pain Management", "Introduction to Anaesthesia"),
    ("Anaesthesia and Pain Management", "Preoperative Anaesthetic Assessment"),
    ("Anaesthesia and Pain Management", "Postoperative Nausea and Vomiting"),
    ("Anaesthesia and Pain Management", "Maintaining Anaesthesia"),
    ("Anaesthesia and Pain Management", "Perioperative Fluid Therapy"),
    ("Anaesthesia and Pain Management", "Managing Acute Pain"),
    ("Anaesthesia and Pain Management", "Local and Regional Anaesthesia"),
    ("Intensive Care", "Introduction to the Intensive Care Unit"),
    ("Intensive Care", "The Deteriorating Patient"),
    ("Intensive Care", "Basic and Advanced Life Support"),
    ("Intensive Care", "Ethical Considerations in Critical Care"),
    ("Intensive Care", "Death and Organ Donation"),
    ("Intensive Care", "Arterial Blood Gas Interpretation"),
    ("Intensive Care", "Breathing"),
    ("Intensive Care", "Doctor and Wellbeing"),
]

SECTION_ORDER = [
    "Emergency Medicine and Trauma",
    "Anaesthesia and Pain Management",
    "Intensive Care",
    "Orthopaedics",
]

SECTION_ICONS = {
    "Emergency Medicine and Trauma": "🚑",
    "Anaesthesia and Pain Management": "💉",
    "Intensive Care": "🫁",
    "Orthopaedics": "🦴",
}


def _slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def _build_topics():
    topics = []
    for section, topic_name in _UQ_BANKS:
        topics.append({
            "id": f"{_slug(section)}/{_slug(topic_name)}",
            "name": topic_name,
            "section": section,
            "mcq_bank": f"{_COURSE} :: {section} - {topic_name} (MCQ)",
            "viva_bank": f"{_COURSE} :: {section} - {topic_name} (VIVA)",
            "viva_source": "imported",  # imported_questions.IMPORTED_VIVA
        })
    # Orthopaedics — single viva-only topic; content lives in builtin_questions.py
    topics.append({
        "id": "orthopaedics/orthopaedic-trauma-framework",
        "name": "Orthopaedic Trauma Framework",
        "section": "Orthopaedics",
        "mcq_bank": None,
        "viva_bank": "Orthopaedic Trauma Framework (Viva)",
        "viva_source": "builtin",  # builtin_questions.BUILTIN_VIVA
    })
    return topics


UQ_TOPICS = _build_topics()
_TOPIC_BY_ID = {t["id"]: t for t in UQ_TOPICS}


def sections():
    return SECTION_ORDER


def topics_for_section(section):
    return [t for t in UQ_TOPICS if t["section"] == section]


def get_topic(topic_id):
    return _TOPIC_BY_ID.get(topic_id)


def all_topic_ids():
    return [t["id"] for t in UQ_TOPICS]


if __name__ == "__main__":
    print(f"Sections: {len(SECTION_ORDER)}   Topics: {len(UQ_TOPICS)}")
    for sec in SECTION_ORDER:
        ts = topics_for_section(sec)
        print(f"  {sec:<35} topics={len(ts)}")
