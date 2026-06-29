"""
gsse.py
=======
Streamlit page for the GSSE section of The Differential.

Mount from app.py with a single line inside your tab/router, e.g.:

    import gsse
    gsse.render_gsse()

Views (driven by st.session_state):
    topics      -> Roadmap-style table of all topics, grouped by science
    subtopics   -> drill-down for one topic (sections, blocks, plan, last reviewed)
    study       -> question player for one subtopic (Type X / A / SPOT)

Progress is kept in st.session_state by default. To persist to SQLite/Supabase
(like the PSA module), pass getter/setter callables to render_gsse(); see
_load_progress / _save_progress.
"""

import os
import re
import json
import datetime as _dt

import streamlit as st

from gsse_config import (
    GSSE_TOPICS,
    GSSE_DOMAINS,
    get_topic,
    get_subtopic,
    topics_for_science,
    sections_of,
    science_of_subtopic,
)

# Question bank files (merge as many as you like; same schema as gsse_seed_questions.json)
GSSE_BANK_FILES = ["gsse_seed_questions.json"]

PLAN_OPTIONS = ["Not Started", "Beginner", "Intermediate", "Confident", "Mastered"]
SCIENCE_ORDER = ["ANATOMY", "PHYSIOLOGY", "PATHOLOGY"]

_HERE = os.path.dirname(os.path.abspath(__file__))


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

@st.cache_data(show_spinner=False)
def _load_questions():
    """Return (questions_list, index_by_subtopic_id)."""
    questions = []
    for fname in GSSE_BANK_FILES:
        path = os.path.join(_HERE, fname)
        if not os.path.exists(path):
            continue
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            questions.extend(data.get("questions", []))
        except Exception as e:  # noqa: BLE001
            st.warning(f"Could not load {fname}: {e}")
    index = {}
    for q in questions:
        index.setdefault(q.get("subtopic_id"), []).append(q)
    return questions, index


# ---------------------------------------------------------------------------
# Progress state (session by default; pluggable persistence)
# ---------------------------------------------------------------------------

def _progress():
    """Mutable per-user progress dict held in session_state.

    Shape:
        {
          "<subtopic_id>": {
              "plan": "Beginner",
              "last_reviewed": "2026-06-29",
              "attempts": {"<question_id>": {"correct": 3, "total": 5}}
          }
        }
    """
    if "_gsse_progress" not in st.session_state:
        st.session_state["_gsse_progress"] = {}
    return st.session_state["_gsse_progress"]


def _sub_progress(subtopic_id):
    p = _progress()
    if subtopic_id not in p:
        p[subtopic_id] = {"plan": "Not Started", "last_reviewed": None, "attempts": {}}
    return p[subtopic_id]


def _record_attempt(subtopic_id, question_id, correct, total):
    sp = _sub_progress(subtopic_id)
    sp["attempts"][question_id] = {"correct": correct, "total": total}
    sp["last_reviewed"] = _dt.date.today().isoformat()


def _subtopic_accuracy(subtopic_id):
    """Best-known accuracy fraction across attempted questions, or None."""
    sp = _progress().get(subtopic_id)
    if not sp or not sp["attempts"]:
        return None
    c = sum(a["correct"] for a in sp["attempts"].values())
    t = sum(a["total"] for a in sp["attempts"].values())
    return (c / t) if t else None


def _topic_completion(topic):
    """Blocks-weighted mean accuracy across the topic's subtopics (0..1)."""
    num = den = 0.0
    for st_ in topic["subtopics"]:
        acc = _subtopic_accuracy(st_["id"])
        if acc is None:
            continue
        w = st_["blocks"] or 0.5  # QBank rows have 0 blocks; give them a small weight
        num += acc * w
        den += w
    return (num / den) if den else 0.0


def _science_readiness(science):
    """Mean topic completion across a science (for the independent-pass bars)."""
    ts = topics_for_science(science)
    vals = [_topic_completion(t) for t in ts]
    answered = [v for v in vals if v > 0]
    return (sum(answered) / len(answered)) if answered else 0.0


# Optional persistence hooks ------------------------------------------------
# Wire these to your SQLite/Supabase layer if you want cross-session progress.
def _load_progress(persist_get):
    if persist_get and "_gsse_progress" not in st.session_state:
        try:
            st.session_state["_gsse_progress"] = persist_get() or {}
        except Exception:  # noqa: BLE001
            st.session_state["_gsse_progress"] = {}


def _save_progress(persist_set):
    if persist_set:
        try:
            persist_set(_progress())
        except Exception as e:  # noqa: BLE001
            st.warning(f"Could not save progress: {e}")


# ---------------------------------------------------------------------------
# Navigation helpers
# ---------------------------------------------------------------------------

def _go(view, topic_id=None, subtopic_id=None):
    st.session_state["_gsse_view"] = view
    if topic_id is not None:
        st.session_state["_gsse_topic"] = topic_id
    if subtopic_id is not None:
        st.session_state["_gsse_subtopic"] = subtopic_id
    st.rerun()


# ---------------------------------------------------------------------------
# Marking (pure-ish logic)
# ---------------------------------------------------------------------------

def _norm(s):
    return re.sub(r"\s+", " ", str(s).strip().lower())


def _option_letter(opt):
    m = re.match(r"\s*([A-Za-z])[\.\)]", opt)
    return m.group(1).upper() if m else None


# ---------------------------------------------------------------------------
# View: topics table
# ---------------------------------------------------------------------------

def _topics_view(qindex):
    st.subheader("GSSE — Topics")
    st.caption(
        "Three components are passed independently — fail any one and you fail "
        "the whole exam. Readiness is shown per component."
    )

    # per-component readiness
    cols = st.columns(3)
    for col, sci in zip(cols, SCIENCE_ORDER):
        r = _science_readiness(sci)
        col.metric(GSSE_DOMAINS[sci]["name"], f"{r*100:.0f}%")
        col.progress(min(max(r, 0.0), 1.0))

    st.divider()

    for sci in SCIENCE_ORDER:
        st.markdown(f"### {GSSE_DOMAINS[sci]['name']}")
        for t in topics_for_science(sci):
            n_q = sum(len(qindex.get(s["id"], [])) for s in t["subtopics"])
            comp = _topic_completion(t)
            c1, c2, c3, c4, c5 = st.columns([5, 1.4, 1.4, 2, 1.4])
            stub = " · stub" if t.get("racs_completeness_stub") else ""
            c1.markdown(f"{t['icon']} **{t['name']}**  \n"
                        f"<span style='color:gray;font-size:0.85em'>"
                        f"{len(t['subtopics'])} subtopics · {n_q} questions{stub}</span>",
                        unsafe_allow_html=True)
            c2.markdown(f"<span style='color:gray'>{t['study_weight_pct']}%</span>",
                        unsafe_allow_html=True)
            c3.markdown(f"<span style='color:gray'>{t['blocks_total']} blk</span>",
                        unsafe_allow_html=True)
            c4.progress(min(max(comp, 0.0), 1.0))
            if c5.button("Open", key=f"open_{t['id']}"):
                _go("subtopics", topic_id=t["id"])
        st.write("")


# ---------------------------------------------------------------------------
# View: subtopics for a topic
# ---------------------------------------------------------------------------

def _subtopics_view(qindex):
    topic = get_topic(st.session_state.get("_gsse_topic"))
    if topic is None:
        _go("topics")
        return

    top = st.columns([6, 2])
    top[0].subheader(f"{topic['icon']} {topic['name']}")
    if top[1].button("← Back to topics"):
        _go("topics")

    if topic.get("note"):
        st.caption(topic["note"])

    grouped = sections_of(topic["id"])
    for section, subs in grouped.items():
        if topic["sections"] != ["General"]:
            st.markdown(f"**{section}**")
        for s in subs:
            sp = _sub_progress(s["id"])
            n_q = len(qindex.get(s["id"], []))
            acc = _subtopic_accuracy(s["id"])
            c1, c2, c3, c4, c5 = st.columns([5, 1, 2, 2, 1.4])
            c1.write(f"{s['code']}. {s['name']}")
            c2.markdown(f"<span style='color:gray'>{s['blocks']} blk</span>",
                        unsafe_allow_html=True)
            # plan status selector (persists in session)
            new_plan = c3.selectbox(
                "plan", PLAN_OPTIONS, index=PLAN_OPTIONS.index(sp["plan"]),
                key=f"plan_{s['id']}", label_visibility="collapsed",
            )
            if new_plan != sp["plan"]:
                sp["plan"] = new_plan
            label = (f"{acc*100:.0f}% · {n_q} q" if acc is not None
                     else (f"{n_q} q" if n_q else "no q yet"))
            c4.markdown(f"<span style='color:gray'>{label}</span>",
                        unsafe_allow_html=True)
            if n_q:
                if c5.button("Study", key=f"study_{s['id']}"):
                    _go("study", subtopic_id=s["id"])
            else:
                c5.markdown("<span style='color:gray;font-size:0.85em'>—</span>",
                            unsafe_allow_html=True)
        st.write("")


# ---------------------------------------------------------------------------
# View: study / question player
# ---------------------------------------------------------------------------

def _render_typeX(q, key):
    st.write(q["stem"])
    answers = []
    for i, stmt in enumerate(q["statements"]):
        choice = st.radio(stmt["text"], ["True", "False"], key=f"{key}_s{i}",
                          horizontal=True, index=None)
        answers.append(choice)
    if st.button("Check", key=f"{key}_check"):
        correct = 0
        for i, stmt in enumerate(q["statements"]):
            picked = answers[i]
            truth = "True" if stmt["answer"] else "False"
            ok = (picked == truth)
            correct += int(ok)
            icon = "✅" if ok else ("⬜" if picked is None else "❌")
            st.markdown(f"{icon} **{stmt['text']}** — *{truth}*")
            if stmt.get("explanation"):
                st.caption(stmt["explanation"])
        st.info(f"Score: {correct}/{len(q['statements'])}")
        if q.get("explanation"):
            st.caption(q["explanation"])
        return correct, len(q["statements"])
    return None


def _render_typeA(q, key):
    st.write(q["stem"])
    options = q.get("options") or []
    picked = st.radio("Select one:", options, key=f"{key}_opt", index=None)
    if st.button("Check", key=f"{key}_check"):
        picked_letter = _option_letter(picked) if picked else None
        ok = (picked_letter == str(q.get("answer")).strip().upper())
        st.markdown(("✅ Correct" if ok else "❌ Incorrect")
                    + f" — answer: **{q.get('answer')}**")
        if q.get("explanation"):
            st.caption(q["explanation"])
        return int(ok), 1
    return None


def _render_spot(q, key):
    img = q.get("image")
    if img:
        path = os.path.join(_HERE, img)
        if os.path.exists(path):
            st.image(path, use_container_width=True)
        else:
            st.warning(f"Image not found: {img} (drop the file into the repo and "
                       f"set the correct relative path).")
    st.write(q["stem"])
    typed = st.text_input("Your answer:", key=f"{key}_spot")
    if st.button("Check", key=f"{key}_check"):
        accepted = [q.get("answer")] + (q.get("accepted_answers") or [])
        ok = _norm(typed) in {_norm(a) for a in accepted if a}
        st.markdown(("✅ Correct" if ok else "❌ Incorrect")
                    + f" — answer: **{q.get('answer')}**")
        if q.get("explanation"):
            st.caption(q["explanation"])
        return int(ok), 1
    return None


_RENDERERS = {"X": _render_typeX, "A": _render_typeA, "SPOT": _render_spot, "B": _render_typeA}


def _study_view(qindex):
    sid = st.session_state.get("_gsse_subtopic")
    topic, sub = get_subtopic(sid)
    if sub is None:
        _go("topics")
        return

    top = st.columns([6, 2])
    top[0].subheader(f"{topic['icon']} {topic['name']} — {sub['name']}")
    if top[1].button("← Back"):
        _go("subtopics", topic_id=topic["id"])

    questions = qindex.get(sid, [])
    if not questions:
        st.info("No questions in this subtopic yet.")
        return

    st.caption(f"{len(questions)} question(s) · "
               f"{GSSE_DOMAINS[science_of_subtopic(sid)]['name']} component")

    for n, q in enumerate(questions, 1):
        with st.container(border=True):
            st.markdown(f"**Q{n}** · `{q.get('type')}`"
                        + ("  ·  ⚑ verify against AU guidelines"
                           if q.get("needs_au_review") else ""))
            renderer = _RENDERERS.get(q.get("type"), _render_typeA)
            result = renderer(q, key=f"q_{q.get('id', n)}")
            if result is not None:
                correct, total = result
                _record_attempt(sid, q.get("id", f"{sid}-{n}"), correct, total)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def render_gsse(persist_get=None, persist_set=None):
    """Render the GSSE section. Optionally pass persistence callables:
        persist_get() -> dict   (load saved progress once per session)
        persist_set(dict)       (save current progress)
    """
    _load_progress(persist_get)
    _, qindex = _load_questions()

    view = st.session_state.get("_gsse_view", "topics")
    if view == "subtopics":
        _subtopics_view(qindex)
    elif view == "study":
        _study_view(qindex)
    else:
        _topics_view(qindex)

    _save_progress(persist_set)


if __name__ == "__main__":
    render_gsse()
