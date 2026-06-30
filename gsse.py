"""
gsse.py
=======
Streamlit page for the GSSE section of The Differential.

Mount from app.py:
    import gsse
    gsse.render_gsse(persist_get=gsse_load_progress,
                     persist_set=gsse_save_progress,
                     user=st.session_state.get("current_user", "Terry"))

Three sections (top nav):
    📊 Dashboard  — stat cards, accuracy by subject, this-week chart, recent sessions
    ✍️ Practice   — SBA / MCQ practice with a tab per subject
    🗂️ Topics     — the roadmap tree (topic > section > subtopic) + question player

Progress is per-user in st.session_state, optionally persisted via the hooks above.
Built with native Streamlit components so it adapts to your app theme (light or dark).
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

GSSE_BANK_FILES = ["gsse_seed_questions.json"]
PLAN_OPTIONS = ["Not Started", "Beginner", "Intermediate", "Confident", "Mastered"]
SCIENCE_ORDER = ["ANATOMY", "PHYSIOLOGY", "PATHOLOGY"]
TYPE_LABEL = {"A": "SBA", "X": "Type X (T/F)", "SPOT": "Spot", "B": "Matching"}
_HERE = os.path.dirname(os.path.abspath(__file__))


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

@st.cache_data(show_spinner=False)
def _load_questions():
    questions = []
    for fname in GSSE_BANK_FILES:
        path = os.path.join(_HERE, fname)
        if not os.path.exists(path):
            continue
        try:
            with open(path, encoding="utf-8") as f:
                questions.extend(json.load(f).get("questions", []))
        except Exception as e:  # noqa: BLE001
            st.warning(f"Could not load {fname}: {e}")
    index = {}
    for q in questions:
        index.setdefault(q.get("subtopic_id"), []).append(q)
    return questions, index


def _questions_by_science(qindex):
    out = {s: [] for s in SCIENCE_ORDER}
    for sid, qs in qindex.items():
        sci = science_of_subtopic(sid)
        if sci in out:
            out[sci].extend(qs)
    return out


# ---------------------------------------------------------------------------
# Progress + event log (session state; persisted via hooks)
# ---------------------------------------------------------------------------

def _progress():
    if "_gsse_progress" not in st.session_state:
        st.session_state["_gsse_progress"] = {}
    return st.session_state["_gsse_progress"]


def _mark_dirty():
    st.session_state["_gsse_dirty"] = True


def _events():
    return _progress().setdefault("_events", [])


def _log_event(science, subtopic_id, correct, total):
    evs = _events()
    evs.append({
        "ts": _dt.datetime.now().isoformat(timespec="seconds"),
        "science": science, "subtopic_id": subtopic_id,
        "correct": int(correct), "total": int(total),
    })
    del evs[:-1000]  # keep the most recent 1000


def _sub_progress(subtopic_id):
    p = _progress()
    if subtopic_id not in p:
        p[subtopic_id] = {"plan": "Not Started", "last_reviewed": None, "attempts": {}}
    return p[subtopic_id]


def _record_attempt(subtopic_id, question_id, correct, total):
    sp = _sub_progress(subtopic_id)
    sp["attempts"][question_id] = {"correct": correct, "total": total}
    sp["last_reviewed"] = _dt.date.today().isoformat()
    _log_event(science_of_subtopic(subtopic_id), subtopic_id, correct, total)
    _mark_dirty()


def _subtopic_accuracy(subtopic_id):
    sp = _progress().get(subtopic_id)
    if not sp or not sp.get("attempts"):
        return None
    c = sum(a["correct"] for a in sp["attempts"].values())
    t = sum(a["total"] for a in sp["attempts"].values())
    return (c / t) if t else None


def _topic_completion(topic):
    num = den = 0.0
    for s in topic["subtopics"]:
        acc = _subtopic_accuracy(s["id"])
        if acc is None:
            continue
        w = s["blocks"] or 0.5
        num += acc * w
        den += w
    return (num / den) if den else 0.0


def _science_readiness(science):
    vals = [_topic_completion(t) for t in topics_for_science(science)]
    answered = [v for v in vals if v > 0]
    return (sum(answered) / len(answered)) if answered else 0.0


# ---------------------------------------------------------------------------
# Analytics (pure, NaN-safe)
# ---------------------------------------------------------------------------

def _date_of(e):
    return _dt.date.fromisoformat(e["ts"][:10])


def _analytics(events, today=None):
    today = today or _dt.date.today()
    tot = sum(e["total"] for e in events)
    cor = sum(e["correct"] for e in events)
    by = {}
    for sci in SCIENCE_ORDER:
        se = [e for e in events if e["science"] == sci]
        t = sum(e["total"] for e in se); c = sum(e["correct"] for e in se)
        by[sci] = (c / t) if t else 0.0
    week = []
    for i in range(6, -1, -1):
        day = today - _dt.timedelta(days=i)
        de = [e for e in events if _date_of(e) == day]
        t = sum(e["total"] for e in de); c = sum(e["correct"] for e in de)
        week.append({"day": day.strftime("%a"),
                     "accuracy": round((c / t) * 100) if t else 0,
                     "answered": len(de)})
    days = {_date_of(e) for e in events}
    cur = today
    if cur not in days and (today - _dt.timedelta(days=1)) in days:
        cur = today - _dt.timedelta(days=1)
    streak = 0
    while cur in days:
        streak += 1; cur -= _dt.timedelta(days=1)
    return {"answered": len(events), "overall": (cor / tot) if tot else 0.0,
            "by_science": by, "week": week, "streak": streak}


def _recent_sessions(events, limit=5):
    groups = {}
    for e in events:
        g = groups.setdefault((_date_of(e), e["science"]), {"total": 0, "correct": 0, "n": 0})
        g["total"] += e["total"]; g["correct"] += e["correct"]; g["n"] += 1
    rows = [{"date": d, "science": sci, "n": g["n"],
             "acc": round((g["correct"] / g["total"]) * 100) if g["total"] else 0}
            for (d, sci), g in groups.items()]
    rows.sort(key=lambda r: r["date"], reverse=True)
    return rows[:limit]


def _relative_day(d):
    delta = (_dt.date.today() - d).days
    if delta <= 0:
        return "Today"
    if delta == 1:
        return "Yesterday"
    return f"{delta} days ago"


# ---------------------------------------------------------------------------
# Persistence hooks
# ---------------------------------------------------------------------------

def _ensure_loaded(persist_get, user):
    if st.session_state.get("_gsse_loaded_user") != user:
        loaded = {}
        if persist_get:
            try:
                loaded = persist_get(user) or {}
            except Exception:  # noqa: BLE001
                loaded = {}
        st.session_state["_gsse_progress"] = loaded
        st.session_state["_gsse_loaded_user"] = user
        st.session_state["_gsse_dirty"] = False


def _flush(persist_set, user):
    if persist_set and st.session_state.get("_gsse_dirty"):
        try:
            persist_set(_progress(), user)
            st.session_state["_gsse_dirty"] = False
        except Exception as e:  # noqa: BLE001
            st.warning(f"Could not save progress: {e}")


# ---------------------------------------------------------------------------
# Navigation + marking helpers
# ---------------------------------------------------------------------------

def _go(view, topic_id=None, subtopic_id=None):
    st.session_state["_gsse_view"] = view
    if topic_id is not None:
        st.session_state["_gsse_topic"] = topic_id
    if subtopic_id is not None:
        st.session_state["_gsse_subtopic"] = subtopic_id
    st.rerun()


def _norm(s):
    return re.sub(r"\s+", " ", str(s).strip().lower())


def _option_letter(opt):
    m = re.match(r"\s*([A-Za-z])[\.\)]", opt)
    return m.group(1).upper() if m else None


# ---------------------------------------------------------------------------
# Question renderers (return (correct, total) on Check, else None)
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Question renderers (return (correct, total) on Check, else None)
# ---------------------------------------------------------------------------

# Shared CSS injected once per session
def _inject_q_styles():
    if st.session_state.get("_gsse_styles_injected"):
        return
    st.markdown("""
<style>
/* ---- type label above question ---- */
.q-type-label {
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #9ca3af;
    margin-bottom: 4px;
}
/* ---- question stem ---- */
.q-stem {
    font-size: 1.05rem;
    font-weight: 700;
    color: #111827;
    margin-bottom: 18px;
    line-height: 1.45;
}
/* ---- SR section labels ---- */
.q-sr-label {
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #3b82f6;
    margin-top: 10px;
    margin-bottom: 2px;
}
.q-sr-text {
    font-size: 1rem;
    font-weight: 700;
    color: #111827;
    margin-bottom: 10px;
    line-height: 1.4;
}
/* ---- T/F grid ---- */
.tf-header {
    display: grid;
    grid-template-columns: 52px 52px 1fr;
    font-size: 0.8rem;
    font-weight: 600;
    color: #6b7280;
    margin-bottom: 4px;
    padding-left: 2px;
}
.tf-row {
    display: grid;
    grid-template-columns: 52px 52px 1fr;
    align-items: center;
    padding: 8px 0;
    border-bottom: 1px solid #f3f4f6;
}
.tf-stmt {
    font-size: 0.9rem;
    color: #1f2937;
    line-height: 1.4;
}
/* ---- result badges ---- */
.q-result-ok  { color: #059669; font-weight: 600; }
.q-result-bad { color: #dc2626; font-weight: 600; }
.q-expl { font-size: 0.85rem; color: #6b7280; margin-top: 4px; }
</style>
""", unsafe_allow_html=True)
    st.session_state["_gsse_styles_injected"] = True


def _render_typeX(q, key):
    _inject_q_styles()
    is_sr = "statement-reason" in (q.get("tags") or [])

    if is_sr:
        # --- Statement & Reason layout ---
        st.markdown('<div class="q-type-label">Statement &amp; Reason</div>', unsafe_allow_html=True)
        stmts = q.get("statements") or []
        # First statement = S, second = R
        s_text = stmts[0]["text"] if len(stmts) > 0 else ""
        r_text = stmts[1]["text"] if len(stmts) > 1 else ""
        st.markdown('<div class="q-sr-label">Statement (S):</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="q-sr-text">S: {s_text}</div>', unsafe_allow_html=True)
        st.markdown('<div class="q-sr-label">Reason (R):</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="q-sr-text">R: {r_text}</div>', unsafe_allow_html=True)

        sr_options = [
            "S is true, R is true and is a valid explanation of S",
            "S is true, R is true but is NOT a valid explanation of S",
            "S is true, R is false",
            "S is false, R is true",
            "Both S and R are false",
        ]
        picked_sr = st.radio("", sr_options, key=f"{key}_sr", index=None,
                             label_visibility="collapsed")

        if st.button("Check answer", key=f"{key}_check"):
            # Work out correct SR option from statement answers
            s_true = stmts[0]["answer"] if len(stmts) > 0 else False
            r_true = stmts[1]["answer"] if len(stmts) > 1 else False
            # Overall explanation field encodes the verdict for SR questions
            expl = q.get("explanation", "")
            if "S_TRUE_R_TRUE_EXPLAINS" in expl or "correctly explains" in expl:
                correct_idx = 0
            elif "S_TRUE_R_TRUE_NOT_EXPLAINS" in expl or "does not correctly explain" in expl:
                correct_idx = 1
            elif s_true and not r_true:
                correct_idx = 2
            elif not s_true and r_true:
                correct_idx = 3
            else:
                correct_idx = 4
            correct_opt = sr_options[correct_idx]
            ok = picked_sr == correct_opt
            st.markdown(
                f"<span class='{'q-result-ok' if ok else 'q-result-bad'}'>"
                f"{'✅ Correct' if ok else '❌ Incorrect'}</span> — "
                f"<em>{correct_opt}</em>",
                unsafe_allow_html=True)
            if q.get("explanation"):
                st.markdown(f'<div class="q-expl">{q["explanation"]}</div>',
                            unsafe_allow_html=True)
            return int(ok), 1
        return None

    else:
        # --- True / False multi-statement layout ---
        st.markdown('<div class="q-type-label">True / False</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="q-stem">{q["stem"]}</div>', unsafe_allow_html=True)

        stmts = q.get("statements") or []
        picks = []
        st.markdown(
            '<div class="tf-header"><div>True</div><div>False</div><div></div></div>',
            unsafe_allow_html=True)
        for i, stmt in enumerate(stmts):
            col_t, col_f, col_text = st.columns([1, 1, 8])
            t_sel = col_t.checkbox("T", key=f"{key}_s{i}_T", label_visibility="collapsed")
            f_sel = col_f.checkbox("F", key=f"{key}_s{i}_F", label_visibility="collapsed")
            col_text.markdown(
                f'<div class="tf-stmt">{stmt["text"]}</div>', unsafe_allow_html=True)
            # Enforce mutual exclusivity via pick logic
            if t_sel and f_sel:
                pick = None  # conflicting
            elif t_sel:
                pick = "True"
            elif f_sel:
                pick = "False"
            else:
                pick = None
            picks.append(pick)

        if st.button("Check answer", key=f"{key}_check"):
            correct = 0
            for i, stmt in enumerate(stmts):
                truth = "True" if stmt["answer"] else "False"
                ok = picks[i] == truth
                correct += int(ok)
                icon = "✅" if ok else ("⬜" if picks[i] is None else "❌")
                st.markdown(
                    f"{icon} <strong>{stmt['text']}</strong> — "
                    f"<em>{truth}</em>",
                    unsafe_allow_html=True)
                if stmt.get("explanation"):
                    st.markdown(f'<div class="q-expl">{stmt["explanation"]}</div>',
                                unsafe_allow_html=True)
            st.info(f"Score: {correct}/{len(stmts)}")
            if q.get("explanation") and q["explanation"] != "See individual statement explanations above.":
                st.markdown(f'<div class="q-expl">{q["explanation"]}</div>',
                            unsafe_allow_html=True)
            return correct, len(stmts)
        return None


def _render_typeA(q, key):
    _inject_q_styles()
    is_sr = "statement-reason" in (q.get("tags") or [])
    type_label = "Statement &amp; Reason" if is_sr else "Single Best Answer"

    st.markdown(f'<div class="q-type-label">{type_label}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="q-stem">{q["stem"]}</div>', unsafe_allow_html=True)

    # Strip "A. " prefixes from options for display, keep full for matching
    opts = q.get("options") or []
    display_opts = [re.sub(r"^[A-Za-z][\.\)]\s*", "", o) for o in opts]

    picked = st.radio("", opts, key=f"{key}_opt", index=None,
                      label_visibility="collapsed",
                      format_func=lambda o: re.sub(r"^[A-Za-z][\.\)]\s*", "", o))

    if st.button("Check answer", key=f"{key}_check"):
        ok = (_option_letter(picked) if picked else None) == str(q.get("answer")).strip().upper()
        ans_text = next((re.sub(r"^[A-Za-z][\.\)]\s*", "", o) for o in opts
                         if _option_letter(o) == str(q.get("answer")).strip().upper()), q.get("answer"))
        st.markdown(
            f"<span class='{'q-result-ok' if ok else 'q-result-bad'}'>"
            f"{'✅ Correct' if ok else '❌ Incorrect'}</span> — <em>{ans_text}</em>",
            unsafe_allow_html=True)
        if q.get("explanation"):
            st.markdown(f'<div class="q-expl">{q["explanation"]}</div>',
                        unsafe_allow_html=True)
        return int(ok), 1
    return None


def _render_spot(q, key):
    _inject_q_styles()
    st.markdown('<div class="q-type-label">Spot Diagnosis</div>', unsafe_allow_html=True)
    img = q.get("image")
    if img:
        path = os.path.join(_HERE, img)
        if os.path.exists(path):
            st.image(path, use_container_width=True)
        else:
            st.warning(f"Image not found: {img}")
    st.markdown(f'<div class="q-stem">{q["stem"]}</div>', unsafe_allow_html=True)
    typed = st.text_input("Your answer:", key=f"{key}_spot")
    if st.button("Check answer", key=f"{key}_check"):
        accepted = {_norm(a) for a in ([q.get("answer")] + (q.get("accepted_answers") or [])) if a}
        ok = _norm(typed) in accepted
        st.markdown(
            f"<span class='{'q-result-ok' if ok else 'q-result-bad'}'>"
            f"{'✅ Correct' if ok else '❌ Incorrect'}</span> — answer: <em>{q.get('answer')}</em>",
            unsafe_allow_html=True)
        if q.get("explanation"):
            st.markdown(f'<div class="q-expl">{q["explanation"]}</div>',
                        unsafe_allow_html=True)
        return int(ok), 1
    return None


_RENDERERS = {"X": _render_typeX, "A": _render_typeA, "SPOT": _render_spot, "B": _render_typeA}


def _question_card(q, key_prefix, number):
    """Render one question; record the attempt if checked."""
    flag = "  ·  ⚑ *verify vs AU guidelines*" if q.get("needs_au_review") else ""
    st.markdown(f"**Q{number}**{flag}")
    renderer = _RENDERERS.get(q.get("type"), _render_typeA)
    result = renderer(q, key=f"{key_prefix}_{q.get('id', number)}")
    if result is not None:
        c, t = result
        _record_attempt(q.get("subtopic_id"), q.get("id", f"{key_prefix}-{number}"), c, t)
    st.divider()


# ---------------------------------------------------------------------------
# View: Dashboard
# ---------------------------------------------------------------------------

def _dashboard_view(qindex, user):
    import pandas as pd
    import altair as alt

    a = _analytics(_events())
    total_q = sum(len(v) for v in qindex.values())

    st.markdown(f"### Welcome back, {user} 🥷")
    st.caption(f"{_dt.date.today():%A, %B %-d} · GSSE Preparation")

    c1, c2, c3, c4 = st.columns(4)
    with c1.container(border=True):
        st.metric("Overall accuracy", f"{round(a['overall']*100)}%")
    with c2.container(border=True):
        st.metric("Questions answered", f"{a['answered']}")
    with c3.container(border=True):
        st.metric("Day streak", f"{a['streak']}")
    with c4.container(border=True):
        st.metric("Question bank", f"{total_q}")

    left, right = st.columns(2)
    with left:
        st.markdown("**Accuracy by subject**")
        df = pd.DataFrame({"Subject": [GSSE_DOMAINS[s]["name"] for s in SCIENCE_ORDER],
                           "Accuracy": [round(a["by_science"][s]*100) for s in SCIENCE_ORDER]})
        chart = (alt.Chart(df).mark_bar(color="#5b6ef5", cornerRadiusTopLeft=4, cornerRadiusTopRight=4)
                 .encode(x=alt.X("Subject:N", sort=None, title=None),
                         y=alt.Y("Accuracy:Q", title=None, scale=alt.Scale(domain=[0, 100])))
                 .properties(height=240))
        st.altair_chart(chart, use_container_width=True, theme="streamlit")
    with right:
        st.markdown("**Progress this week**")
        dfw = pd.DataFrame(a["week"])
        chart = (alt.Chart(dfw).mark_bar(color="#34c38f", cornerRadiusTopLeft=4, cornerRadiusTopRight=4)
                 .encode(x=alt.X("day:N", sort=None, title=None),
                         y=alt.Y("accuracy:Q", title=None, scale=alt.Scale(domain=[0, 100])))
                 .properties(height=240))
        st.altair_chart(chart, use_container_width=True, theme="streamlit")

    st.markdown("**Recent sessions**")
    sessions = _recent_sessions(_events())
    if not sessions:
        st.caption("No sessions yet — answer some questions in Practice or Topics to see them here.")
    else:
        for s in sessions:
            with st.container(border=True):
                cols = st.columns([6, 1.5])
                cols[0].markdown(f"**{GSSE_DOMAINS[s['science']]['name']} practice**  \n"
                                 f"<span style='color:gray;font-size:0.85em'>"
                                 f"{s['n']} questions · {_relative_day(s['date'])}</span>",
                                 unsafe_allow_html=True)
                cols[1].markdown(f"### {s['acc']}%")


# ---------------------------------------------------------------------------
# View: Practice (SBA / MCQ by subject)
# ---------------------------------------------------------------------------

def _practice_view(qindex):
    st.markdown("### GSSE Question Bank")
    st.caption("Practice questions by subject — single-best-answer, true/false and spots.")

    by_sci = _questions_by_science(qindex)
    tabs = st.tabs([f"{GSSE_DOMAINS[s]['name']} ({len(by_sci[s])})" for s in SCIENCE_ORDER])
    for tab, sci in zip(tabs, SCIENCE_ORDER):
        with tab:
            qs = by_sci[sci]
            if not qs:
                st.info("No questions here yet.")
                continue
            answered = sum(
                1 for q in qs
                if q.get("id") in _progress().get(q.get("subtopic_id"), {}).get("attempts", {})
            )
            st.progress(answered / len(qs), text=f"{answered}/{len(qs)} answered")
            for n, q in enumerate(qs, 1):
                _question_card(q, key_prefix=f"prac_{sci}", number=n)


# ---------------------------------------------------------------------------
# View: Topics tree
# ---------------------------------------------------------------------------

def _topics_view(qindex):
    st.markdown("### Topics")
    st.caption("Three components are passed independently — readiness is shown per component.")

    cols = st.columns(3)
    for col, sci in zip(cols, SCIENCE_ORDER):
        r = _science_readiness(sci)
        with col.container(border=True):
            st.metric(GSSE_DOMAINS[sci]["name"], f"{round(r*100)}%")
            st.progress(min(max(r, 0.0), 1.0))

    st.write("")
    for sci in SCIENCE_ORDER:
        st.markdown(f"#### {GSSE_DOMAINS[sci]['name']}")
        for t in topics_for_science(sci):
            n_q = sum(len(qindex.get(s["id"], [])) for s in t["subtopics"])
            comp = _topic_completion(t)
            c1, c2, c3 = st.columns([6, 2, 1.4])
            stub = " · stub" if t.get("racs_completeness_stub") else ""
            c1.markdown(f"{t['icon']} **{t['name']}**  \n"
                        f"<span style='color:gray;font-size:0.85em'>"
                        f"{len(t['subtopics'])} subtopics · {n_q} questions{stub}</span>",
                        unsafe_allow_html=True)
            c2.progress(min(max(comp, 0.0), 1.0))
            if c3.button("Open", key=f"open_{t['id']}"):
                _go("subtopics", topic_id=t["id"])
        st.write("")


def _subtopics_view(qindex):
    topic = get_topic(st.session_state.get("_gsse_topic"))
    if topic is None:
        _go("topics"); return

    top = st.columns([6, 2])
    top[0].markdown(f"### {topic['icon']} {topic['name']}")
    if top[1].button("← Back to topics"):
        _go("topics")
    if topic.get("note"):
        st.caption(topic["note"])

    for section, subs in sections_of(topic["id"]).items():
        if topic["sections"] != ["General"]:
            st.markdown(f"**{section}**")
        for s in subs:
            sp = _sub_progress(s["id"])
            n_q = len(qindex.get(s["id"], []))
            acc = _subtopic_accuracy(s["id"])
            c1, c2, c3, c4 = st.columns([5, 2, 2, 1.4])
            c1.write(f"{s['code']}. {s['name']}")
            new_plan = c2.selectbox("plan", PLAN_OPTIONS, index=PLAN_OPTIONS.index(sp["plan"]),
                                    key=f"plan_{s['id']}", label_visibility="collapsed")
            if new_plan != sp["plan"]:
                sp["plan"] = new_plan
                _mark_dirty()
            label = (f"{round(acc*100)}% · {n_q} q" if acc is not None
                     else (f"{n_q} q" if n_q else "no q yet"))
            c3.markdown(f"<span style='color:gray'>{label}</span>", unsafe_allow_html=True)
            if n_q:
                if c4.button("Study", key=f"study_{s['id']}"):
                    _go("study", subtopic_id=s["id"])
            else:
                c4.markdown("<span style='color:gray;font-size:0.85em'>—</span>",
                            unsafe_allow_html=True)
        st.write("")


def _study_view(qindex):
    sid = st.session_state.get("_gsse_subtopic")
    topic, sub = get_subtopic(sid)
    if sub is None:
        _go("topics"); return

    top = st.columns([6, 2])
    top[0].markdown(f"### {topic['icon']} {topic['name']} — {sub['name']}")
    if top[1].button("← Back"):
        _go("subtopics", topic_id=topic["id"])

    qs = qindex.get(sid, [])
    if not qs:
        st.info("No questions in this subtopic yet.")
        return
    st.caption(f"{len(qs)} question(s) · {GSSE_DOMAINS[science_of_subtopic(sid)]['name']} component")
    for n, q in enumerate(qs, 1):
        _question_card(q, key_prefix="study", number=n)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def render_gsse(persist_get=None, persist_set=None, user=None):
    user = user or "you"
    _ensure_loaded(persist_get, user)
    _, qindex = _load_questions()

    nav = st.radio("section", ["📊 Dashboard", "🗂️ Topics"],
                   horizontal=True, label_visibility="collapsed", key="_gsse_nav")

    if nav.endswith("Dashboard"):
        _dashboard_view(qindex, user)
    else:
        view = st.session_state.get("_gsse_view", "topics")
        if view == "subtopics":
            _subtopics_view(qindex)
        elif view == "study":
            _study_view(qindex)
        else:
            _topics_view(qindex)

    _flush(persist_set, user)


if __name__ == "__main__":
    render_gsse()
