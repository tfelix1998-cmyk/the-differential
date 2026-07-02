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
    # EMED bank (Broad Topic - Pathology) - added to uq module
    try:
        from emed_questions import EMED_BANKS
    except Exception:
        EMED_BANKS = {}

    out = {}
    for t in ucfg.UQ_TOPICS:
        # Look up MCQ bank in whichever source has it (IMPORTED for original UQ, EMED for new topics)
        mcqs = []
        if t["mcq_bank"]:
            mcqs = IMPORTED_BANKS.get(t["mcq_bank"]) or EMED_BANKS.get(t["mcq_bank"]) or []
        if t["viva_source"] == "builtin":
            viva = BUILTIN_VIVA.get(t["viva_bank"], []) if t["viva_bank"] else []
        elif t["viva_source"] == "imported":
            viva = IMPORTED_VIVA.get(t["viva_bank"], []) if t["viva_bank"] else []
        else:
            viva = []  # EMED topics are MCQ-only
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
        p[topic_id] = {"mcq_attempts": {}, "viva_ratings": {}, "viva_marks": {}, "last_reviewed": None}
    tp = p[topic_id]
    tp.setdefault("viva_marks", {})  # backfill for progress saved before this field existed
    return tp


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


def _record_viva_marks(topic_id, q_key, scored, max_marks):
    tp = _topic_progress(topic_id)
    tp["viva_marks"][q_key] = {"scored": scored, "max": max_marks}
    tp["last_reviewed"] = _dt.date.today().isoformat()
    _mark_dirty()


def _topic_viva_marks(topic_id):
    tp = _progress().get(topic_id)
    return tp.get("viva_marks", {}) if tp else {}


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
    font-size: 1.02rem; font-weight: 400; color: #1f2937;
    margin-bottom: 18px; line-height: 1.55;
}
.uq-stem p { margin: 0 0 10px; }
.uq-stem p:last-child { margin-bottom: 0; font-weight: 600; color: #111827; }
.uq-stem-list {
    margin: 4px 0 12px; padding: 10px 14px 10px 28px;
    background: #f8fafc; border-radius: 8px; list-style: disc;
}
.uq-stem-list li { margin: 2px 0; line-height: 1.5; }
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

import re as _re

_OPT_TAIL = _re.compile(
    r'(?:\s+(?:ox|ax|om|oe|ne|wm|nw|NW%|[A-Za-z]?%|\d+x|[A-Za-z]\d))+\s*$'
    r'|\s*[™©®%＋+]+\s*$'
)


def _clean_opt(o):
    """Defensive: strip trailing OCR marker junk from an option at render time,
    so even un-cleaned banks display tidily. Leaves the leading 'A) ' intact."""
    prev = None
    while prev != o:
        prev = o
        o = _OPT_TAIL.sub('', o).rstrip(' .,')
    return o


def _stem_html(text):
    """Convert a cleaned stem (plain text with blank-line paragraphs and
    '- ' bullet lines) into safe HTML, so lab-value lists render as a real
    bulleted list inside the styled stem div instead of a run-on with
    literal asterisks."""
    import html
    blocks = _re.split(r'\n\s*\n', (text or "").strip())
    out = []
    for blk in blocks:
        lines = [l.strip() for l in blk.splitlines() if l.strip()]
        if lines and all(l.startswith(("- ", "• ")) for l in lines):
            items = "".join(f"<li>{html.escape(l[2:].strip())}</li>" for l in lines)
            out.append(f'<ul class="uq-stem-list">{items}</ul>')
        else:
            out.append("<p>" + html.escape(" ".join(lines)) + "</p>")
    return "".join(out)


def _uq_opt_row_html(text, state):
    """state: 'correct' | 'wrong' | 'dim' | None"""
    cls = "opt-row"
    trailing = ""
    if state == "correct":
        cls += " opt-correct"
        trailing = ('<span style="margin-left:auto;font-weight:700;color:#FFFFFF;'
                    'background:#4CAF6D;padding:4px 12px;border-radius:20px;font-size:0.82rem;">Correct</span>')
    elif state == "wrong":
        cls += " opt-wrong"
        trailing = ('<span style="margin-left:auto;font-weight:700;color:#FFFFFF;'
                    'background:#E5534B;padding:4px 12px;border-radius:20px;font-size:0.82rem;">Your answer</span>')
    elif state == "dim":
        cls += " opt-dim"
    return f'<div class="{cls}"><span>{text}</span>{trailing}</div>'


def _uq_explanation_html(explanation, key_learning_points=None):
    if explanation:
        st.markdown(f'<div class="explanation-box"><h4>Explanation</h4><div>{explanation}</div></div>',
                     unsafe_allow_html=True)
    if key_learning_points:
        st.markdown(f'<div class="uq-klp">🎯 {key_learning_points}</div>', unsafe_allow_html=True)


@st.fragment
def _mcq_card(topic_id, mcq, number, key):
    """Render one MCQ. PERF: own fragment — answering only reruns this card.
    UX: answered state persists in session_state so the coloured result stays
    visible across Prev/Next and Question-Map navigation (matches GSSE)."""
    _inject_q_styles()
    st.markdown('<div class="uq-type-label">Single Best Answer</div>', unsafe_allow_html=True)
    img = (mcq.get("image_url") or "").strip()
    if img:
        try:
            st.image(img, use_container_width=True)
        except Exception:
            st.caption("(image could not be loaded)")
    st.markdown(f'<div class="uq-stem">{_stem_html(mcq["question_text"])}</div>',
                unsafe_allow_html=True)

    options = [_clean_opt(o) for o in (mcq.get("options") or [])]
    answered_key = f"{key}_answered"
    correct_letter = (mcq.get("correct_answer_letter") or "").strip().upper()

    def _show_result(picked_letter):
        for o in options:
            letter = o.strip()[0].upper() if o.strip() else None
            text = o[2:].strip() if len(o) > 2 else o
            if letter == correct_letter:
                state = "correct"
            elif letter == picked_letter:
                state = "wrong"
            else:
                state = "dim"
            st.markdown(_uq_opt_row_html(text, state), unsafe_allow_html=True)
        _uq_explanation_html(mcq.get("explanation"), mcq.get("key_learning_points"))

    if st.session_state.get(answered_key):
        _show_result(st.session_state.get(f"{key}_picked_letter"))
        return

    picked = st.radio("", options, key=f"{key}_opt", index=None,
                      label_visibility="collapsed",
                      format_func=lambda o: o[2:].strip() if len(o) > 2 else o)

    if st.button("Submit Answer", key=f"{key}_check", type="primary", use_container_width=True):
        picked_letter = picked.strip()[0].upper() if picked else None
        st.session_state[answered_key] = True
        st.session_state[f"{key}_picked_letter"] = picked_letter
        ok = picked_letter == correct_letter
        _show_result(picked_letter)
        _record_mcq(topic_id, key, ok)


@st.fragment
def _viva_card(topic_id, qa, number, key):
    """PERF: own fragment, same as _mcq_card. UX: matches the main Viva tab —
    collapsible expander (so a 70+ question list stays scannable), a text
    area to write your own answer before checking, manual marks entry, and
    a confidence rating, with both reflected in the expander's title badge."""
    _inject_q_styles()
    rating = _topic_viva_progress(topic_id).get(key)
    marks_rec = _topic_viva_marks(topic_id).get(key)
    badge = {1: " 🔴", 2: " 🟡", 3: " 🟢"}.get(rating, "")
    mark_badge = f" ✅ {marks_rec['scored']:g}/{marks_rec['max']:g}" if marks_rec else ""

    with st.expander(f"Q{number}: {qa['question']}{badge}{mark_badge}"):
        st.text_area("Your answer:", key=f"{key}_user", height=80,
                     placeholder="Type your answer before checking…",
                     label_visibility="collapsed")

        revealed_key = f"{key}_revealed"
        if st.button("Reveal answer", key=f"{key}_reveal"):
            st.session_state[revealed_key] = True

        if st.session_state.get(revealed_key):
            lines = qa["answer"].split("\n")
            bullets = "".join(f"<li>{l.strip()}</li>" for l in lines if l.strip())
            st.markdown(f'<div class="uq-viva-card"><ul>{bullets}</ul></div>', unsafe_allow_html=True)
            st.markdown("---")

            # ── Manual marks entry (same pattern as the main Viva tab) ──
            mcol1, mcol2, mcol3 = st.columns([1.3, 1.3, 1])
            with mcol1:
                max_default = marks_rec["max"] if marks_rec else 2.0
                max_marks_in = st.number_input(
                    "Out of how many marks?", min_value=0.0, step=0.5,
                    value=float(max_default), key=f"{key}_maxmarks")
            with mcol2:
                scored_default = marks_rec["scored"] if marks_rec else 0.0
                scored_in = st.number_input(
                    "Marks you scored", min_value=0.0, step=0.5,
                    value=float(scored_default), key=f"{key}_scoredmarks")
            with mcol3:
                st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)
                if st.button("Record marks", key=f"{key}_recordmarks"):
                    scored_clamped = min(scored_in, max_marks_in) if max_marks_in else scored_in
                    _record_viva_marks(topic_id, key, scored_clamped, max_marks_in)
                    st.rerun(scope="fragment")
            if marks_rec:
                st.caption(f"Recorded: {marks_rec['scored']:g} / {marks_rec['max']:g} marks for this question.")

            st.markdown("---")
            if rating is None:
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
                label = {1: "🔴 Hard", 2: "🟡 Good", 3: "🟢 Easy"}[rating]
                st.info(f"Logged: **{label}**")


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

# ---------------------------------------------------------------------------
# View: Module dashboard (NEW — sits between Topics-nav and the topic list)
# ---------------------------------------------------------------------------

SECTION_ICON_BG = {
    # falls back to a default indigo tile if a section isn't listed here
}
_DEFAULT_BG, _DEFAULT_FG = "#EEF0FE", "#5B62F2"

def _modules_view(content):
    hdr_l, hdr_r = st.columns([3, 2])
    with hdr_l:
        st.markdown("### Modules")
        st.caption("UQ Critical Care Module. Open a module to see its topics.")
    with hdr_r:
        search = st.text_input("Search for a module", key="_uq_module_search",
                                placeholder="🔍  Search for a module",
                                label_visibility="collapsed")
    search_norm = search.strip().lower() if search else ""

    total_mcq = sum(len(d["mcq"]) for d in content.values())
    total_viva = sum(len(d["viva"]) for d in content.values())
    events = _events()
    answered = len(events)
    total_q = sum(e["total"] for e in events)
    correct_q = sum(e["correct"] for e in events)
    overall_pct = round((correct_q / total_q) * 100, 1) if total_q else 0.0

    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#5B62F2,#7A80F7); border-radius:16px;
                padding:22px 26px; color:#FFFFFF; margin-bottom:20px;">
      <div style="font-size:0.8rem; opacity:0.85; text-transform:uppercase; letter-spacing:0.08em;">Overall Mastery</div>
      <div style="font-size:2.4rem; font-weight:800; margin:4px 0 14px;">{overall_pct}%</div>
      <div style="display:flex; gap:32px; flex-wrap:wrap;">
        <div><div style="font-size:1.2rem; font-weight:700;">{len(SECTION_ORDER)}</div>
             <div style="font-size:0.75rem; opacity:0.85;">Modules</div></div>
        <div><div style="font-size:1.2rem; font-weight:700;">{answered}</div>
             <div style="font-size:0.75rem; opacity:0.85;">Questions Answered</div></div>
        <div><div style="font-size:1.2rem; font-weight:700;">{total_mcq + total_viva}</div>
             <div style="font-size:0.75rem; opacity:0.85;">Total Bank Size</div></div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    sections = SECTION_ORDER
    if search_norm:
        sections = [sec for sec in sections if search_norm in sec.lower()]

    cols = st.columns(3)
    for i, sec in enumerate(sections):
        topics = ucfg.topics_for_section(sec)
        n_mcq = sum(_topic_counts(content, t["id"])[0] for t in topics)
        n_viva = sum(_topic_counts(content, t["id"])[1] for t in topics)
        accs = [a for a in (_topic_mcq_accuracy(t["id"]) for t in topics) if a is not None]
        comp = (sum(accs) / len(accs)) if accs else 0.0
        with cols[i % 3]:
            with st.container(border=True):
                st.markdown(f"""
                <div style="background:{_DEFAULT_BG}; border-radius:10px; padding:14px 16px; margin-bottom:10px;">
                  <span style="font-size:1.6rem;">{ucfg.SECTION_ICONS.get(sec, '📘')}</span>
                </div>
                <div style="font-weight:700; font-size:1.02rem; margin-bottom:2px;">{sec}</div>
                <div style="color:#6B7290; font-size:0.8rem; margin-bottom:10px;">
                  Mastery&nbsp;&nbsp;<span style="color:{_DEFAULT_FG}; font-weight:700;">{round(comp*100)}%</span>
                </div>
                """, unsafe_allow_html=True)
                st.progress(min(max(comp, 0.0), 1.0))
                st.markdown(f"""
                <div style="display:flex; justify-content:space-between; color:#6B7290;
                            font-size:0.78rem; margin:10px 0 14px;">
                  <span>📝 {n_mcq} MCQ</span>
                  <span>🗣️ {n_viva} viva</span>
                  <span>🗂️ {len(topics)} topics</span>
                </div>
                """, unsafe_allow_html=True)
                if st.button("Focused learning  →", key=f"open_module_{sec}", use_container_width=True):
                    st.session_state["_uq_module"] = sec
                    _go("topics")

    if search_norm and not sections:
        st.info(f"No modules match “{search}”.")


# ---------------------------------------------------------------------------
# View: Topics tree (now filtered to the selected module; back button added)
# ---------------------------------------------------------------------------

def _topics_view(content):
    active_section = st.session_state.get("_uq_module")
    top = st.columns([6, 2])
    with top[0]:
        if active_section:
            st.markdown(f"### {ucfg.SECTION_ICONS.get(active_section, '📘')} {active_section}")
            st.caption("Tap Study to practise a topic.")
        else:
            st.markdown("### Topics")
            st.caption("UQ Critical Care Module, organised by section. Tap Study to practise a topic.")
    with top[1]:
        if active_section and st.button("← Back to modules"):
            st.session_state["_uq_module"] = None
            st.rerun()

    sections_to_show = [active_section] if active_section else SECTION_ORDER

    # ── Controls: search / sort / type filter ──
    c_search, c_sort, c_filter = st.columns([2.2, 1.4, 2])
    with c_search:
        search = st.text_input("Search topics", key=f"_uq_topic_search_{active_section or 'all'}",
                                placeholder="🔍  Search topics",
                                label_visibility="collapsed")
    with c_sort:
        sort_by = st.selectbox("Sort by", ["Order", "Name (A–Z)", "Progress", "% Correct"],
                                key=f"_uq_topic_sort_{active_section or 'all'}", label_visibility="collapsed")
    with c_filter:
        type_filter = st.multiselect("Question type", ["MCQ only", "MCQ + Viva", "Viva only"],
                                      key=f"_uq_topic_typefilter_{active_section or 'all'}",
                                      placeholder="Filter by question type",
                                      label_visibility="collapsed")
    search_norm = search.strip().lower() if search else ""

    # ── Build rows ──
    rows = []
    for sec in sections_to_show:
        for t in ucfg.topics_for_section(sec):
            n_mcq, n_viva = _topic_counts(content, t["id"])
            acc = _topic_mcq_accuracy(t["id"])
            tp = _topic_progress(t["id"])
            n_answered = len(tp["mcq_attempts"])
            kind = "MCQ + Viva" if (n_mcq and n_viva) else ("MCQ only" if n_mcq else ("Viva only" if n_viva else "—"))
            rows.append({"section": sec, "topic": t, "n_mcq": n_mcq, "n_viva": n_viva,
                         "n_answered": n_answered, "acc": acc, "kind": kind})

    if search_norm:
        rows = [r for r in rows if search_norm in r["topic"]["name"].lower()]
    if type_filter:
        rows = [r for r in rows if r["kind"] in type_filter]

    if sort_by == "Name (A–Z)":
        rows.sort(key=lambda r: r["topic"]["name"])
    elif sort_by == "Progress":
        rows.sort(key=lambda r: (r["n_answered"] / r["n_mcq"]) if r["n_mcq"] else 0, reverse=True)
    elif sort_by == "% Correct":
        rows.sort(key=lambda r: (r["acc"] if r["acc"] is not None else -1), reverse=True)

    if not rows:
        st.info("No topics match your search/filter.")
        return

    h = st.columns([4, 2, 1.6, 2.2, 1.4])
    h[0].markdown("**Topic**")
    h[1].markdown("**Progress**")
    h[2].markdown("**% Correct**")
    h[3].markdown("**Question Type**")
    h[4].markdown("**Start**")
    st.markdown('<hr style="margin:4px 0 8px;">', unsafe_allow_html=True)

    last_section = None
    for r in rows:
        t, n_mcq, n_viva, n_answered, acc, kind = (
            r["topic"], r["n_mcq"], r["n_viva"], r["n_answered"], r["acc"], r["kind"])
        if not active_section and r["section"] != last_section:
            st.markdown(f"**{ucfg.SECTION_ICONS.get(r['section'], '📘')} {r['section']}**")
            last_section = r["section"]

        c1, c2, c3, c4, c5 = st.columns([4, 2, 1.6, 2.2, 1.4])
        c1.write(t["name"])

        with c2:
            st.progress(min(n_answered / n_mcq, 1.0) if n_mcq else 0.0,
                        text=f"{n_answered}/{n_mcq}" if n_mcq else "no MCQs")

        with c3:
            if acc is None:
                c3.markdown("<span style='color:#6B7290;'>—</span>", unsafe_allow_html=True)
            else:
                pct = round(acc * 100)
                color = "#4CAF6D" if pct >= 80 else ("#B8860B" if pct >= 50 else "#E5534B")
                c3.markdown(f"<span style='color:{color}; font-weight:700;'>{pct}%</span>",
                            unsafe_allow_html=True)

        with c4:
            pills = ""
            if n_mcq:
                pills += f'<span class="tag-pill" style="font-size:0.72rem; padding:3px 10px; margin-right:4px;">MCQ ({n_mcq})</span>'
            if n_viva:
                pills += f'<span class="tag-pill" style="font-size:0.72rem; padding:3px 10px;">Viva ({n_viva})</span>'
            c4.markdown(pills or "<span style='color:#6B7290;'>—</span>", unsafe_allow_html=True)

        with c5:
            if (n_mcq + n_viva):
                label = "Resume" if n_answered else "Start"
                if c5.button(label, key=f"uq_study_{t['id']}", use_container_width=True):
                    _go("study", topic_id=t["id"])
            else:
                c5.markdown("<span style='color:#6B7290; font-size:0.85em;'>—</span>", unsafe_allow_html=True)



def _mcq_study_panel(tid, mcqs):
    """Paginated single-question MCQ view with a Quiz Progress + Question Map
    side panel, matching gsse.py's _study_view."""
    if st.session_state.get("_uq_qidx_topic") != tid:
        st.session_state["_uq_qidx"] = 0
        st.session_state["_uq_qidx_topic"] = tid
    idx = max(0, min(st.session_state.get("_uq_qidx", 0), len(mcqs) - 1))
    st.session_state["_uq_qidx"] = idx
    mcq = mcqs[idx]
    qkey = f"uqmcq_{tid}_{idx + 1}"

    flagged = st.session_state.setdefault(f"_uq_flagged_{tid}", set())
    tp = _topic_progress(tid)
    attempts = tp["mcq_attempts"]

    main_col, side_col = st.columns([3, 1], gap="large")

    with main_col:
        top = st.columns([5, 2.2])
        top[0].markdown(f"**Q{idx + 1}**")
        is_flagged = qkey in flagged
        if top[1].button("🚩 Flagged" if is_flagged else "⚑ Flag for review",
                          key=f"uq_flag_{tid}_{idx}", use_container_width=True):
            flagged.symmetric_difference_update({qkey})
            st.rerun()

        with st.container(border=True):
            _mcq_card(tid, mcq, idx + 1, key=qkey)

        st.write("")
        nav = st.columns([1, 1, 3, 1, 1])
        if nav[0].button("⟵ Prev", disabled=(idx == 0), use_container_width=True, key="uq_mcq_prev"):
            st.session_state["_uq_qidx"] = idx - 1
            st.rerun()
        nav[2].markdown(f"<div style='text-align:center;color:#6B7290;font-size:0.85rem;padding-top:8px;'>"
                         f"Question {idx + 1} of {len(mcqs)}</div>", unsafe_allow_html=True)
        if nav[4].button("Next ⟶", disabled=(idx == len(mcqs) - 1), use_container_width=True, key="uq_mcq_next"):
            st.session_state["_uq_qidx"] = idx + 1
            st.rerun()

    with side_col:
        answered = [(f"uqmcq_{tid}_{i + 1}", attempts.get(f"uqmcq_{tid}_{i + 1}")) for i in range(len(mcqs))]
        answered = [(k, a) for k, a in answered if a is not None]
        n_correct = sum(1 for _, a in answered if a["correct"])
        n_incorrect = len(answered) - n_correct
        acc = round(n_correct / len(answered) * 100) if answered else 0

        st.markdown(f"""
        <div style="background:#FFFFFF;border:1px solid #E2E6F5;border-radius:14px;padding:18px 20px;">
          <div style="font-weight:700;color:#5B62F2;margin-bottom:12px;">Quiz Progress</div>
          <div style="display:flex;justify-content:space-between;font-size:0.85rem;color:#6B7290;margin-bottom:6px;">
            <span>Question:</span><strong style="color:#1E2233;">{idx + 1} / {len(mcqs)}</strong>
          </div>
          <div style="display:flex;justify-content:space-between;font-size:0.85rem;color:#6B7290;margin-bottom:6px;">
            <span>Correct:</span><strong style="color:#4CAF6D;">{n_correct}</strong>
          </div>
          <div style="display:flex;justify-content:space-between;font-size:0.85rem;color:#6B7290;margin-bottom:6px;">
            <span>Incorrect:</span><strong style="color:#E5534B;">{n_incorrect}</strong>
          </div>
          <div style="display:flex;justify-content:space-between;font-size:0.85rem;color:#6B7290;">
            <span>Accuracy:</span><strong style="color:#1E2233;">{acc}%</strong>
          </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div style="font-weight:700;color:#5B62F2;margin:18px 0 8px;">Question Map</div>',
                     unsafe_allow_html=True)
        n_cols = 5
        for row_start in range(0, len(mcqs), n_cols):
            row = list(range(row_start, min(row_start + n_cols, len(mcqs))))
            mcols = st.columns(n_cols)
            for j, i2 in enumerate(row):
                qkey2 = f"uqmcq_{tid}_{i2 + 1}"
                a2 = attempts.get(qkey2)
                if a2 is not None:
                    status = "✓" if a2["correct"] else "✕"
                elif qkey2 in flagged:
                    status = "🚩"
                else:
                    status = ""
                label = f"{status}{i2 + 1}" if status else str(i2 + 1)
                if mcols[j].button(label, key=f"uq_map_{tid}_{i2}", use_container_width=True,
                                   type="primary" if i2 == idx else "secondary"):
                    st.session_state["_uq_qidx"] = i2
                    st.rerun()

        st.caption("✓ correct · ✕ incorrect · 🚩 flagged")


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
            _mcq_study_panel(tid, mcqs)
        ti += 1
    if vivas:
        with tabs[ti]:
            ratings = _topic_viva_progress(tid)
            marks = _topic_viva_marks(tid)
            reviewed = len(ratings)
            marks_scored_sum = sum(m["scored"] for m in marks.values())
            marks_max_sum = sum(m["max"] for m in marks.values())

            col_p, col_cnt, col_marks = st.columns([2.3, 1, 1])
            with col_p:
                st.progress(reviewed / len(vivas) if vivas else 0)
            with col_cnt:
                st.caption(f"{reviewed} / {len(vivas)} reviewed")
            with col_marks:
                st.markdown(
                    f'<div style="background:#EEF0FE;border-radius:10px;padding:6px 14px;text-align:center;">'
                    f'<div style="color:#5B62F2;font-size:0.7rem;font-weight:600;text-transform:uppercase;'
                    f'letter-spacing:0.05em;">Your Marks</div>'
                    f'<div style="color:#1E2233;font-size:1.3rem;font-weight:700;">'
                    f'{marks_scored_sum:g} / {marks_max_sum:g}</div></div>',
                    unsafe_allow_html=True)

            if reviewed:
                hard_v = sum(1 for v in ratings.values() if v == 1)
                good_v = sum(1 for v in ratings.values() if v == 2)
                easy_v = sum(1 for v in ratings.values() if v == 3)
                st.markdown(
                    f'<span style="background:#FCEDEC;color:#E5534B;padding:4px 12px;border-radius:20px;'
                    f'font-size:0.8rem;font-weight:600;margin-right:6px;">🔴 Hard: {hard_v}</span>'
                    f'<span style="background:#FFF6E5;color:#B8860B;padding:4px 12px;border-radius:20px;'
                    f'font-size:0.8rem;font-weight:600;margin-right:6px;">🟡 Good: {good_v}</span>'
                    f'<span style="background:#EAF7EE;color:#4CAF6D;padding:4px 12px;border-radius:20px;'
                    f'font-size:0.8rem;font-weight:600;">🟢 Easy: {easy_v}</span>',
                    unsafe_allow_html=True)
            st.write("")

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
        elif st.session_state.get("_uq_module"):
            _topics_view(content)
        else:
            _modules_view(content)

    _flush(persist_set, user)


if __name__ == "__main__":
    render_uq()
