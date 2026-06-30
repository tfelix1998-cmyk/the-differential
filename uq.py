"""
uq.py
=====
Streamlit page for the UQ section of The Differential — UQ Critical Care
Module content (Emergency Medicine & Trauma / Anaesthesia & Pain Management /
Intensive Care) plus the Orthopaedic Trauma Framework viva.

Mount from app.py:
    from uq import render_uq
    render_uq(persist_get=uq_load_progress,
              persist_set=uq_save_progress,
              user=st.session_state.get("current_user", "Terry"))

Two sections (top nav), same shape as GSSE:
    📊 Dashboard  — stat cards, accuracy by section, recent sessions
    🗂️ Topics     — section > topic tree + study player (MCQs + Viva)

PERFORMANCE: each question is rendered inside @st.fragment, so answering one
question only reruns that question's fragment — not the whole 10-tab app.
"""

import os
import json
import datetime as _dt

import streamlit as st

import uq_config as ucfg

SECTION_ORDER = ucfg.SECTION_ORDER
_HERE = os.path.dirname(os.path.abspath(__file__))


# ---------------------------------------------------------------------------
# Data loading (cached — built once per session, not on every rerun)
# ---------------------------------------------------------------------------

@st.cache_data(show_spinner=False)
def _load_content():
    """Return {topic_id: {"mcq": [...], "viva": [...], "name", "section"}}."""
    from imported_questions import IMPORTED_BANKS, IMPORTED_VIVA
    try:
        from builtin_questions import BUILTIN_VIVA
    except Exception:
        BUILTIN_VIVA = {}

    out = {}
    for t in ucfg.UQ_TOPICS:
        mcqs = IMPORTED_BANKS.get(t["mcq_bank"], []) if t["mcq_bank"] else []
        if t["viva_source"] == "builtin":
            viva = BUILTIN_VIVA.get(t["viva_bank"], []) if t["viva_bank"] else []
        else:
            viva = IMPORTED_VIVA.get(t["viva_bank"], []) if t["viva_bank"] else []
        out[t["id"]] = {"mcq": mcqs, "viva": viva, "name": t["name"], "section": t["section"]}
    return out


def _topic_counts(content, topic_id):
    d = content.get(topic_id, {"mcq": [], "viva": []})
    return len(d["mcq"]), len(d["viva"])


# ---------------------------------------------------------------------------
# Progress + event log (session state; persisted via hooks)
# ---------------------------------------------------------------------------

def _progress():
    if "_uq_progress" not in st.session_state:
        st.session_state["_uq_progress"] = {}
    return st.session_state["_uq_progress"]


def _mark_dirty():
    """PERF NOTE: question cards run inside @st.fragment so answering a
    question only reruns that fragment, not the whole render_uq() body —
    which means the _flush() call at the bottom of render_uq() never
    executes during a fragment-only rerun. So we flush right here instead,
    using the persist hooks stashed by render_uq() at the top of the page.
    _flush() itself only writes if the dirty flag is set, so this is cheap."""
    st.session_state["_uq_dirty"] = True
    _flush(st.session_state.get("_uq_persist_set"),
           st.session_state.get("_uq_persist_user", "you"))


def _events():
    return _progress().setdefault("_events", [])


def _log_event(topic_id, kind, correct, total):
    evs = _events()
    evs.append({
        "ts": _dt.datetime.now().isoformat(timespec="seconds"),
        "topic_id": topic_id, "kind": kind,  # kind: "mcq" or "viva"
        "correct": int(correct), "total": int(total),
    })
    del evs[:-1000]


def _topic_progress(topic_id):
    p = _progress()
    if topic_id not in p:
        p[topic_id] = {"mcq_attempts": {}, "viva_ratings": {}, "last_reviewed": None}
    return p[topic_id]


def _record_mcq(topic_id, q_key, correct):
    tp = _topic_progress(topic_id)
    tp["mcq_attempts"][q_key] = {"correct": int(correct)}
    tp["last_reviewed"] = _dt.date.today().isoformat()
    _log_event(topic_id, "mcq", correct, 1)
    _mark_dirty()


def _record_viva(topic_id, q_key, confidence):
    tp = _topic_progress(topic_id)
    tp["viva_ratings"][q_key] = confidence
    tp["last_reviewed"] = _dt.date.today().isoformat()
    _log_event(topic_id, "viva", 1 if confidence >= 2 else 0, 1)
    _mark_dirty()


def _topic_mcq_accuracy(topic_id):
    tp = _progress().get(topic_id)
    if not tp or not tp.get("mcq_attempts"):
        return None
    vals = tp["mcq_attempts"].values()
    return sum(a["correct"] for a in vals) / len(vals)


def _topic_viva_progress(topic_id):
    """Dict of {q_key: confidence} for viva questions rated in this topic."""
    tp = _progress().get(topic_id)
    return tp.get("viva_ratings", {}) if tp else {}


def _section_readiness(content, section):
    """Mean MCQ accuracy across topics in a section that have any attempts."""
    accs = []
    for t in ucfg.topics_for_section(section):
        a = _topic_mcq_accuracy(t["id"])
        if a is not None:
            accs.append(a)
    return (sum(accs) / len(accs)) if accs else 0.0


# ---------------------------------------------------------------------------
# Analytics
# ---------------------------------------------------------------------------

def _date_of(e):
    return _dt.date.fromisoformat(e["ts"][:10])


def _analytics(events, today=None):
    today = today or _dt.date.today()
    mcq_events = [e for e in events if e["kind"] == "mcq"]
    tot = sum(e["total"] for e in mcq_events)
    cor = sum(e["correct"] for e in mcq_events)
    viva_events = [e for e in events if e["kind"] == "viva"]
    days = {_date_of(e) for e in events}
    cur = today
    if cur not in days and (today - _dt.timedelta(days=1)) in days:
        cur = today - _dt.timedelta(days=1)
    streak = 0
    while cur in days:
        streak += 1; cur -= _dt.timedelta(days=1)
    return {
        "mcq_answered": len(mcq_events), "mcq_accuracy": (cor / tot) if tot else 0.0,
        "viva_reviewed": len(viva_events), "streak": streak,
    }


def _recent_sessions(events, limit=5):
    groups = {}
    for e in events:
        g = groups.setdefault((_date_of(e), e["topic_id"]), {"total": 0, "correct": 0, "n": 0, "kind": e["kind"]})
        g["total"] += e["total"]; g["correct"] += e["correct"]; g["n"] += 1
    rows = []
    for (d, tid), g in groups.items():
        topic = ucfg.get_topic(tid)
        name = topic["name"] if topic else tid
        acc = round((g["correct"] / g["total"]) * 100) if g["total"] else 0
        rows.append({"date": d, "name": name, "kind": g["kind"], "n": g["n"], "acc": acc})
    rows.sort(key=lambda r: r["date"], reverse=True)
    return rows[:limit]


def _relative_day(d):
    delta = (_dt.date.today() - d).days
    if delta <= 0: return "Today"
    if delta == 1: return "Yesterday"
    return f"{delta} days ago"


# ---------------------------------------------------------------------------
# Persistence hooks
# ---------------------------------------------------------------------------

def _ensure_loaded(persist_get, user):
    if st.session_state.get("_uq_loaded_user") != user:
        loaded = {}
        if persist_get:
            try:
                loaded = persist_get(user) or {}
            except Exception:
                loaded = {}
        st.session_state["_uq_progress"] = loaded
        st.session_state["_uq_loaded_user"] = user
        st.session_state["_uq_dirty"] = False


def _flush(persist_set, user):
    if persist_set and st.session_state.get("_uq_dirty"):
        try:
            persist_set(_progress(), user)
            st.session_state["_uq_dirty"] = False
        except Exception as e:
            st.warning(f"Could not save progress: {e}")


# ---------------------------------------------------------------------------
# Navigation helpers
# ---------------------------------------------------------------------------

def _go(view, topic_id=None):
    st.session_state["_uq_view"] = view
    if topic_id is not None:
        st.session_state["_uq_topic"] = topic_id
    st.rerun()


# ---------------------------------------------------------------------------
# Shared styling (parallels gsse.py's classes for visual consistency)
# ---------------------------------------------------------------------------

def _inject_q_styles():
    if st.session_state.get("_uq_styles_injected"):
        return
    st.markdown("""
<style>
.uq-type-label {
    font-size: 0.72rem; font-weight: 600; letter-spacing: 0.08em;
    text-transform: uppercase; color: #9ca3af; margin-bottom: 4px;
}
.uq-stem {
    font-size: 1.05rem; font-weight: 700; color: #111827;
    margin-bottom: 18px; line-height: 1.45;
}
.uq-result-ok  { color: #059669; font-weight: 600; }
.uq-result-bad { color: #dc2626; font-weight: 600; }
.uq-expl { font-size: 0.85rem; color: #6b7280; margin-top: 4px; line-height: 1.5; }
.uq-klp {
    background: #fffbeb; border-left: 3px solid #f59e0b; border-radius: 0 8px 8px 0;
    padding: 10px 14px; margin-top: 8px; font-size: 0.85rem; color: #78350f;
}
.uq-viva-card {
    background: #f9fafb; border-left: 3px solid #6366f1; border-radius: 0 8px 8px 0;
    padding: 14px 18px; margin: 8px 0; color: #1f2937;
}
.uq-viva-card ul { margin: 0; padding-left: 18px; }
.uq-viva-card li { margin: 4px 0; line-height: 1.5; }
</style>
""", unsafe_allow_html=True)
    st.session_state["_uq_styles_injected"] = True


# ---------------------------------------------------------------------------
# Question renderers — each wrapped in @st.fragment so answering one question
# never reruns the rest of the app.
# ---------------------------------------------------------------------------

@st.fragment
def _mcq_card(topic_id, mcq, number, key):
    _inject_q_styles()
    st.markdown(f"**Q{number}**")
    st.markdown('<div class="uq-type-label">Single Best Answer</div>', unsafe_allow_html=True)
    img = (mcq.get("image_url") or "").strip()
    if img:
        try:
            st.image(img, use_container_width=True)
        except Exception:
            st.caption("(image could not be loaded)")
    st.markdown(f'<div class="uq-stem">{mcq["question_text"]}</div>', unsafe_allow_html=True)

    options = mcq.get("options") or []
    picked = st.radio("", options, key=f"{key}_opt", index=None,
                      label_visibility="collapsed",
                      format_func=lambda o: o[2:].strip() if len(o) > 2 else o)

    if st.button("Check answer", key=f"{key}_check"):
        correct_letter = (mcq.get("correct_answer_letter") or "").strip().upper()
        picked_letter = picked.strip()[0].upper() if picked else None
        ok = picked_letter == correct_letter
        ans_text = next((o[2:].strip() for o in options
                         if o.strip()[0].upper() == correct_letter), correct_letter)
        st.markdown(
            f"<span class='{'uq-result-ok' if ok else 'uq-result-bad'}'>"
            f"{'✅ Correct' if ok else '❌ Incorrect'}</span> — <em>{ans_text}</em>",
            unsafe_allow_html=True)
        if mcq.get("explanation"):
            st.markdown(f'<div class="uq-expl">{mcq["explanation"]}</div>', unsafe_allow_html=True)
        if mcq.get("key_learning_points"):
            st.markdown(f'<div class="uq-klp">🎯 {mcq["key_learning_points"]}</div>',
                        unsafe_allow_html=True)
        _record_mcq(topic_id, key, ok)
    st.divider()


@st.fragment
def _viva_card(topic_id, qa, number, key):
    _inject_q_styles()
    st.markdown(f"**Q{number}**")
    st.markdown('<div class="uq-type-label">Viva</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="uq-stem">{qa["question"]}</div>', unsafe_allow_html=True)

    revealed_key = f"{key}_revealed"
    if st.button("Reveal answer", key=f"{key}_reveal"):
        st.session_state[revealed_key] = True

    if st.session_state.get(revealed_key):
        lines = qa["answer"].split("\n")
        bullets = "".join(f"<li>{l.strip()}</li>" for l in lines if l.strip())
        st.markdown(f'<div class="uq-viva-card"><ul>{bullets}</ul></div>', unsafe_allow_html=True)

        existing = _topic_viva_progress(topic_id).get(key)
        if existing is None:
            st.write("**Rate your confidence:**")
            c1, c2, c3 = st.columns(3)
            if c1.button("🔴 Hard", key=f"{key}_hard"):
                _record_viva(topic_id, key, 1)
                st.rerun(scope="fragment")
            if c2.button("🟡 Good", key=f"{key}_good"):
                _record_viva(topic_id, key, 2)
                st.rerun(scope="fragment")
            if c3.button("🟢 Easy", key=f"{key}_easy"):
                _record_viva(topic_id, key, 3)
                st.rerun(scope="fragment")
        else:
            label = {1: "🔴 Hard", 2: "🟡 Good", 3: "🟢 Easy"}[existing]
            st.info(f"Logged: **{label}**")
    st.divider()


# ---------------------------------------------------------------------------
# View: Dashboard
# ---------------------------------------------------------------------------

def _dashboard_view(content, user):
    a = _analytics(_events())
    total_mcq = sum(len(d["mcq"]) for d in content.values())
    total_viva = sum(len(d["viva"]) for d in content.values())

    st.markdown(f"### Welcome back, {user} 🥷")
    st.caption(f"{_dt.date.today():%A, %B %-d} · UQ Critical Care Module")

    c1, c2, c3, c4 = st.columns(4)
    with c1.container(border=True):
        st.metric("MCQ accuracy", f"{round(a['mcq_accuracy']*100)}%")
    with c2.container(border=True):
        st.metric("MCQs answered", f"{a['mcq_answered']}")
    with c3.container(border=True):
        st.metric("Viva reviewed", f"{a['viva_reviewed']}")
    with c4.container(border=True):
        st.metric("Day streak", f"{a['streak']}")

    st.write("")
    st.markdown("**Readiness by section**")
    cols = st.columns(len(SECTION_ORDER))
    for col, sec in zip(cols, SECTION_ORDER):
        r = _section_readiness(content, sec)
        with col.container(border=True):
            st.markdown(f"{ucfg.SECTION_ICONS.get(sec, '📘')} **{sec}**")
            st.progress(min(max(r, 0.0), 1.0), text=f"{round(r*100)}%")

    st.write("")
    st.markdown("**Recent sessions**")
    sessions = _recent_sessions(_events())
    if not sessions:
        st.caption("No sessions yet — answer some questions in Topics to see them here.")
    else:
        for s in sessions:
            with st.container(border=True):
                cols = st.columns([6, 1.5])
                kind_label = "MCQs" if s["kind"] == "mcq" else "Viva"
                cols[0].markdown(f"**{s['name']}** — {kind_label}  \n"
                                 f"<span style='color:gray;font-size:0.85em'>"
                                 f"{s['n']} questions · {_relative_day(s['date'])}</span>",
                                 unsafe_allow_html=True)
                cols[1].markdown(f"### {s['acc']}%")

    st.caption(f"Question bank: {total_mcq} MCQs · {total_viva} viva questions across "
               f"{len(ucfg.UQ_TOPICS)} topics")


# ---------------------------------------------------------------------------
# View: Topics tree
# ---------------------------------------------------------------------------

def _topics_view(content):
    st.markdown("### Topics")
    st.caption("UQ Critical Care Module, organised by section. Tap Study to practise a topic.")

    for sec in SECTION_ORDER:
        topics = ucfg.topics_for_section(sec)
        st.markdown(f"#### {ucfg.SECTION_ICONS.get(sec, '📘')} {sec}")
        for t in topics:
            n_mcq, n_viva = _topic_counts(content, t["id"])
            acc = _topic_mcq_accuracy(t["id"])
            c1, c2, c3 = st.columns([6, 2, 1.4])
            label = (f"{round(acc*100)}% MCQ" if acc is not None else "not started")
            c1.markdown(f"**{t['name']}**  \n"
                        f"<span style='color:gray;font-size:0.85em'>"
                        f"{n_mcq} MCQs · {n_viva} viva</span>",
                        unsafe_allow_html=True)
            c2.markdown(f"<span style='color:gray'>{label}</span>", unsafe_allow_html=True)
            if (n_mcq + n_viva) and c3.button("Study", key=f"uq_study_{t['id']}"):
                _go("study", topic_id=t["id"])
        st.write("")


def _study_view(content):
    tid = st.session_state.get("_uq_topic")
    topic = ucfg.get_topic(tid)
    if topic is None:
        _go("topics"); return

    top = st.columns([6, 2])
    top[0].markdown(f"### {ucfg.SECTION_ICONS.get(topic['section'], '📘')} "
                    f"{topic['section']} — {topic['name']}")
    if top[1].button("← Back"):
        _go("topics")

    d = content.get(tid, {"mcq": [], "viva": []})
    mcqs, vivas = d["mcq"], d["viva"]
    if not mcqs and not vivas:
        st.info("No questions in this topic yet.")
        return

    sub_tabs = []
    if mcqs: sub_tabs.append(f"📝 MCQs ({len(mcqs)})")
    if vivas: sub_tabs.append(f"🗣️ Viva ({len(vivas)})")
    tabs = st.tabs(sub_tabs)
    ti = 0
    if mcqs:
        with tabs[ti]:
            for n, mcq in enumerate(mcqs, 1):
                _mcq_card(tid, mcq, n, key=f"uqmcq_{tid}_{n}")
        ti += 1
    if vivas:
        with tabs[ti]:
            for n, qa in enumerate(vivas, 1):
                _viva_card(tid, qa, n, key=f"uqviva_{tid}_{n}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def render_uq(persist_get=None, persist_set=None, user=None):
    user = user or "you"
    st.session_state["_uq_persist_set"] = persist_set
    st.session_state["_uq_persist_user"] = user
    _ensure_loaded(persist_get, user)
    content = _load_content()

    nav = st.radio("section", ["📊 Dashboard", "🗂️ Topics"],
                   horizontal=True, label_visibility="collapsed", key="_uq_nav")

    if nav.endswith("Dashboard"):
        _dashboard_view(content, user)
    else:
        view = st.session_state.get("_uq_view", "topics")
        if view == "study":
            _study_view(content)
        else:
            _topics_view(content)

    _flush(persist_set, user)


if __name__ == "__main__":
    render_uq()
