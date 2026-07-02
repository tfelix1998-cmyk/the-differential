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
    """PERF NOTE: question cards run inside @st.fragment so answering a
    question only reruns that fragment, not the whole render_gsse() body —
    which means the _flush() call at the bottom of render_gsse() never
    executes during a fragment-only rerun. So we flush right here instead,
    using the persist hooks stashed by render_gsse() at the top of the page.
    _flush() itself only writes if the dirty flag is set, so this is cheap."""
    st.session_state["_gsse_dirty"] = True
    _flush(st.session_state.get("_gsse_persist_set"),
           st.session_state.get("_gsse_persist_user", "you"))


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
/* ---- T/F statements ---- */
.tf-stmt {
    font-size: 1rem;
    color: #1f2937;
    line-height: 1.5;
    font-weight: 500;
    margin: 2px 0 6px;
}
.tf-sep {
    border: none;
    border-top: 1px solid #eef0f5;
    margin: 10px 0;
}
/* ---- result badges ---- */
.q-result-ok  { color: #059669; font-weight: 600; }
.q-result-bad { color: #dc2626; font-weight: 600; }
.q-expl { font-size: 0.85rem; color: #6b7280; margin-top: 4px; }
</style>
""", unsafe_allow_html=True)
    st.session_state["_gsse_styles_injected"] = True


def _opt_row_html(text, state):
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


def _explanation_html(explanation, tags=None):
    if not explanation:
        return
    st.markdown(f'<div class="explanation-box"><h4>Explanation</h4><div>{explanation}</div></div>',
                unsafe_allow_html=True)
    if tags:
        pills = "".join(f'<span class="tag-pill">{t}</span>' for t in tags)
        st.markdown(f'<div style="margin-top:10px;">{pills}</div>', unsafe_allow_html=True)


def _render_typeX(q, key):
    _inject_q_styles()
    is_sr = "statement-reason" in (q.get("tags") or [])
    answered_key = f"{key}_answered"

    if is_sr:
        st.markdown('<div class="q-type-label">Statement &amp; Reason</div>', unsafe_allow_html=True)
        stmts = q.get("statements") or []
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

        def _sr_correct_idx():
            s_true = stmts[0]["answer"] if len(stmts) > 0 else False
            r_true = stmts[1]["answer"] if len(stmts) > 1 else False
            expl = q.get("explanation", "")
            if "S_TRUE_R_TRUE_EXPLAINS" in expl or "correctly explains" in expl:
                return 0
            elif "S_TRUE_R_TRUE_NOT_EXPLAINS" in expl or "does not correctly explain" in expl:
                return 1
            elif s_true and not r_true:
                return 2
            elif not s_true and r_true:
                return 3
            return 4

        def _show_sr_result(picked_sr):
            correct_opt = sr_options[_sr_correct_idx()]
            for opt in sr_options:
                if opt == correct_opt:
                    state = "correct"
                elif opt == picked_sr:
                    state = "wrong"
                else:
                    state = "dim"
                st.markdown(_opt_row_html(opt, state), unsafe_allow_html=True)
            _explanation_html(q.get("explanation"))

        if st.session_state.get(answered_key):
            _show_sr_result(st.session_state.get(f"{key}_picked_sr"))
            return None

        picked_sr = st.radio("", sr_options, key=f"{key}_sr", index=None, label_visibility="collapsed")
        if st.button("Submit Answer", key=f"{key}_check", type="primary", use_container_width=True):
            st.session_state[answered_key] = True
            st.session_state[f"{key}_picked_sr"] = picked_sr
            ok = picked_sr == sr_options[_sr_correct_idx()]
            _show_sr_result(picked_sr)
            return int(ok), 1
        return None

    else:
        st.markdown('<div class="q-type-label">True / False</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="q-stem">{q["stem"]}</div>', unsafe_allow_html=True)
        stmts = q.get("statements") or []

        def _show_tf_result(picks):
            correct = 0
            for i, stmt in enumerate(stmts):
                truth = "True" if stmt["answer"] else "False"
                ok = picks[i] == truth
                correct += int(ok)
                icon = "✅" if ok else ("⬜" if picks[i] is None else "❌")
                st.markdown(f"{icon} <strong>{stmt['text']}</strong> — <em>{truth}</em>", unsafe_allow_html=True)
                if stmt.get("explanation"):
                    st.markdown(f'<div class="q-expl">{stmt["explanation"]}</div>', unsafe_allow_html=True)
            st.info(f"Score: {correct}/{len(stmts)}")
            if q.get("explanation") and q["explanation"] != "See individual statement explanations above.":
                _explanation_html(q["explanation"])
            return correct

        if st.session_state.get(answered_key):
            _show_tf_result(st.session_state.get(f"{key}_picks", [None] * len(stmts)))
            return None

        picks = []
        for i, stmt in enumerate(stmts):
            st.markdown(f'<div class="tf-stmt">{i + 1}.&nbsp; {stmt["text"]}</div>',
                        unsafe_allow_html=True)
            choice = st.radio(
                "tf", ["True", "False"], key=f"{key}_s{i}", index=None,
                horizontal=True, label_visibility="collapsed",
            )
            picks.append(choice)
            if i < len(stmts) - 1:
                st.markdown('<hr class="tf-sep">', unsafe_allow_html=True)
        st.write("")

        if st.button("Submit Answer", key=f"{key}_check", type="primary", use_container_width=True):
            st.session_state[answered_key] = True
            st.session_state[f"{key}_picks"] = picks
            correct = _show_tf_result(picks)
            return correct, len(stmts)
        return None


def _render_typeA(q, key):
    _inject_q_styles()
    is_sr = "statement-reason" in (q.get("tags") or [])
    type_label = "Statement &amp; Reason" if is_sr else "Single Best Answer"
    st.markdown(f'<div class="q-type-label">{type_label}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="q-stem">{q["stem"]}</div>', unsafe_allow_html=True)

    opts = q.get("options") or []
    answered_key = f"{key}_answered"
    correct_letter = str(q.get("answer")).strip().upper()

    def _show_result(picked_letter):
        for o in opts:
            letter = _option_letter(o)
            text = re.sub(r"^[A-Za-z][\.\)]\s*", "", o)
            if letter == correct_letter:
                state = "correct"
            elif letter == picked_letter:
                state = "wrong"
            else:
                state = "dim"
            st.markdown(_opt_row_html(text, state), unsafe_allow_html=True)
        _explanation_html(q.get("explanation"))

    if st.session_state.get(answered_key):
        _show_result(st.session_state.get(f"{key}_picked_letter"))
        return None

    picked = st.radio("", opts, key=f"{key}_opt", index=None,
                      label_visibility="collapsed",
                      format_func=lambda o: re.sub(r"^\s*([A-Za-z])[\.\)]\s*", r"\1.  ", o))

    if st.button("Submit Answer", key=f"{key}_check", type="primary", use_container_width=True):
        picked_letter = _option_letter(picked) if picked else None
        st.session_state[answered_key] = True
        st.session_state[f"{key}_picked_letter"] = picked_letter
        ok = picked_letter == correct_letter
        _show_result(picked_letter)
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

    answered_key = f"{key}_answered"

    def _show_result(typed):
        accepted = {_norm(a) for a in ([q.get("answer")] + (q.get("accepted_answers") or [])) if a}
        ok = _norm(typed) in accepted
        st.markdown(
            f"<span class='{'q-result-ok' if ok else 'q-result-bad'}'>"
            f"{'✅ Correct' if ok else '❌ Incorrect'}</span> — answer: <em>{q.get('answer')}</em>",
            unsafe_allow_html=True)
        _explanation_html(q.get("explanation"))
        return ok

    if st.session_state.get(answered_key):
        typed = st.session_state.get(f"{key}_typed", "")
        st.text_input("Your answer:", value=typed, key=f"{key}_spot_ro", disabled=True)
        _show_result(typed)
        return None

    typed = st.text_input("Your answer:", key=f"{key}_spot")
    if st.button("Submit Answer", key=f"{key}_check", type="primary", use_container_width=True):
        st.session_state[answered_key] = True
        st.session_state[f"{key}_typed"] = typed
        ok = _show_result(typed)
        return int(ok), 1
    return None


_RENDERERS = {"X": _render_typeX, "A": _render_typeA, "SPOT": _render_spot, "B": _render_typeA}


@st.fragment
def _question_card(q, key_prefix, number):
    """Render one question; record the attempt if checked.
    PERF: this is its own fragment, so picking a radio option, ticking a T/F
    checkbox, or clicking Submit Answer only reruns this one question — not
    the rest of the page, the rest of GSSE, or the other 9 tabs in the app."""
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

def _q_type_label(q):
    """Human label for a question's type, used by the practice filter."""
    t = q.get("type")
    if t == "X":
        return "True / False"
    if t == "SPOT":
        return "Spot"
    if t == "B":
        return "Matching"
    if "statement-reason" in (q.get("tags") or []):
        return "Statement & Reason"
    return "Single Best Answer"


_TYPE_ORDER = ["Single Best Answer", "True / False", "Statement & Reason", "Matching", "Spot"]


def _practice_view(qindex):
    st.markdown("### GSSE Question Bank")
    st.caption("Practice questions by subject — pick the question types you want to drill.")

    by_sci = _questions_by_science(qindex)

    # ── Question-type filter (e.g. only SBA, or only T/F + S/R) ──
    all_qs = [q for s in SCIENCE_ORDER for q in by_sci[s]]
    present = [lbl for lbl in _TYPE_ORDER if any(_q_type_label(q) == lbl for q in all_qs)]
    counts = {lbl: sum(1 for q in all_qs if _q_type_label(q) == lbl) for lbl in present}
    chosen = st.multiselect(
        "Question types",
        options=present,
        default=present,
        format_func=lambda l: f"{l} ({counts[l]})",
        key="_gsse_type_filter",
        help="Deselect a type to hide it. Leave one selected to drill just that format.",
    )
    chosen = set(chosen) if chosen else set(present)

    def _keep(qs):
        return [q for q in qs if _q_type_label(q) in chosen]

    tabs = st.tabs([f"{GSSE_DOMAINS[s]['name']} ({len(_keep(by_sci[s]))})" for s in SCIENCE_ORDER])
    for tab, sci in zip(tabs, SCIENCE_ORDER):
        with tab:
            qs = _keep(by_sci[sci])
            if not qs:
                st.info("No questions of the selected type(s) here yet.")
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
    # ── Header: title + search ──
    hdr_l, hdr_r = st.columns([3, 2])
    with hdr_l:
        st.markdown("### Topics")
        st.caption("Three components are passed independently — readiness is shown per component.")
    with hdr_r:
        search = st.text_input("Search for a module", key="_gsse_topic_search",
                                placeholder="🔍  Search for a module",
                                label_visibility="collapsed")
    search_norm = _norm(search) if search else ""

    # ── Overall summary strip ──
    all_topics = [t for sci in SCIENCE_ORDER for t in topics_for_science(sci)]
    total_topics = len(all_topics)
    mastered = sum(1 for t in all_topics if _topic_completion(t) >= 0.8)
    total_q = sum(len(qindex.get(s["id"], [])) for t in all_topics for s in t["subtopics"])
    events = _events()
    answered = len(events)
    correct = sum(1 for e in events if e.get("correct") == e.get("total") and e.get("total"))
    overall_pct = round((sum(e["correct"] for e in events) / sum(e["total"] for e in events)) * 100, 1) \
        if sum(e["total"] for e in events) else 0.0

    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#5B62F2,#7A80F7); border-radius:16px;
                padding:22px 26px; color:#FFFFFF; margin-bottom:20px;">
      <div style="font-size:0.8rem; opacity:0.85; text-transform:uppercase; letter-spacing:0.08em;">Overall Mastery</div>
      <div style="font-size:2.4rem; font-weight:800; margin:4px 0 14px;">{overall_pct}%</div>
      <div style="display:flex; gap:32px; flex-wrap:wrap;">
        <div><div style="font-size:1.2rem; font-weight:700;">{mastered} / {total_topics}</div>
             <div style="font-size:0.75rem; opacity:0.85;">Modules Mastered</div></div>
        <div><div style="font-size:1.2rem; font-weight:700;">{answered} / {total_q}</div>
             <div style="font-size:0.75rem; opacity:0.85;">Questions Answered</div></div>
        <div><div style="font-size:1.2rem; font-weight:700;">{correct}</div>
             <div style="font-size:0.75rem; opacity:0.85;">Fully Correct</div></div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Module cards, grouped by science ──
    SCI_COLOR = {
        "ANATOMY":    ("#EEF0FE", "#5B62F2"),
        "PHYSIOLOGY": ("#EAF7EE", "#2E9E58"),
        "PATHOLOGY":  ("#FDEFEA", "#E07A3F"),
    }
    for sci in SCIENCE_ORDER:
        topics = topics_for_science(sci)
        if search_norm:
            topics = [t for t in topics if search_norm in _norm(t["name"])]
        if not topics:
            continue
        bg, fg = SCI_COLOR.get(sci, ("#EEF0FE", "#5B62F2"))
        st.markdown(f"#### {GSSE_DOMAINS[sci]['name']}")
        cols = st.columns(3)
        for i, t in enumerate(topics):
            n_q = sum(len(qindex.get(s["id"], [])) for s in t["subtopics"])
            n_answered = sum(len(_sub_progress(s["id"])["attempts"]) for s in t["subtopics"])
            comp = _topic_completion(t)
            stub = " · stub" if t.get("racs_completeness_stub") else ""
            with cols[i % 3]:
                with st.container(border=True):
                    st.markdown(f"""
                    <div style="background:{bg}; border-radius:10px; padding:14px 16px; margin-bottom:10px;">
                      <span style="font-size:1.6rem;">{t['icon']}</span>
                    </div>
                    <div style="font-weight:700; font-size:1.02rem; margin-bottom:2px;">{t['name']}</div>
                    <div style="color:#6B7290; font-size:0.8rem; margin-bottom:10px;">
                      Mastery&nbsp;&nbsp;<span style="color:{fg}; font-weight:700;">{round(comp*100)}%</span>
                    </div>
                    """, unsafe_allow_html=True)
                    st.progress(min(max(comp, 0.0), 1.0))
                    st.markdown(f"""
                    <div style="display:flex; justify-content:space-between; color:#6B7290;
                                font-size:0.78rem; margin:8px 0 4px;">
                      <span>❓ {n_answered} / {n_q}</span>
                      <span>✅ {n_answered} / {n_q}</span>
                      <span>🗂️ {len(t['subtopics'])} sub{stub}</span>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button("Focused learning  →", key=f"open_{t['id']}", use_container_width=True):
                        _go("subtopics", topic_id=t["id"])
        st.write("")

    if search_norm and not any(
        _norm(t["name"]).find(search_norm) >= 0 for t in all_topics
    ):
        st.info(f"No modules match “{search}”.")



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

    # ── Controls: search / sort / type filter ──
    all_types_present = sorted({
        q.get("type") for s in topic["subtopics"] for q in qindex.get(s["id"], [])
    } - {None})
    type_options = [TYPE_LABEL.get(t, t) for t in all_types_present]
    filter_choices = ["All question types"] + type_options
    if len(type_options) > 1:
        filter_choices.append("Mixed (2+ types)")

    c_search, c_sort, c_filter = st.columns([2.2, 1.4, 2])
    with c_search:
        search = st.text_input("Search topics", key=f"_gsse_sub_search_{topic['id']}",
                                placeholder="🔍  Search subtopics",
                                label_visibility="collapsed")
    with c_sort:
        sort_by = st.selectbox("Sort by", ["Order", "Name (A–Z)", "Progress", "% Correct"],
                                key=f"_gsse_sub_sort_{topic['id']}", label_visibility="collapsed")
    with c_filter:
        type_pick = st.selectbox("Question type", filter_choices,
                                  key=f"_gsse_sub_typefilter_{topic['id']}",
                                  label_visibility="collapsed")

    search_norm = _norm(search) if search else ""

    # ── Build rows ──
    rows = []
    for section, subs in sections_of(topic["id"]).items():
        for s in subs:
            qs = qindex.get(s["id"], [])
            n_q = len(qs)
            sp = _sub_progress(s["id"])
            n_answered = len(sp["attempts"])
            acc = _subtopic_accuracy(s["id"])
            types_here = sorted({TYPE_LABEL.get(q.get("type"), q.get("type")) for q in qs} - {None})
            rows.append({
                "section": section, "sub": s, "n_q": n_q,
                "n_answered": n_answered, "acc": acc, "types": types_here,
            })

    if search_norm:
        rows = [r for r in rows if search_norm in _norm(r["sub"]["name"])]
    if type_pick == "Mixed (2+ types)":
        rows = [r for r in rows if len(r["types"]) > 1]
    elif type_pick != "All question types":
        rows = [r for r in rows if type_pick in r["types"]]

    if sort_by == "Name (A–Z)":
        rows.sort(key=lambda r: r["sub"]["name"])
    elif sort_by == "Progress":
        rows.sort(key=lambda r: (r["n_answered"] / r["n_q"]) if r["n_q"] else 0, reverse=True)
    elif sort_by == "% Correct":
        rows.sort(key=lambda r: (r["acc"] if r["acc"] is not None else -1), reverse=True)

    if not rows:
        st.info("No subtopics match your search/filter.")
        return

    # ── Table header ──
    h = st.columns([4, 2, 1.6, 2.2, 1.4])
    h[0].markdown("**Topic**")
    h[1].markdown("**Progress**")
    h[2].markdown("**% Correct**")
    h[3].markdown("**Question Type**")
    h[4].markdown("**Start**")
    st.markdown('<hr style="margin:4px 0 8px;">', unsafe_allow_html=True)

    last_section = None
    for r in rows:
        s, n_q, n_answered, acc, types_here = r["sub"], r["n_q"], r["n_answered"], r["acc"], r["types"]
        if topic["sections"] != ["General"] and r["section"] != last_section:
            st.markdown(f"**{r['section']}**")
            last_section = r["section"]

        c1, c2, c3, c4, c5 = st.columns([4, 2, 1.6, 2.2, 1.4])
        c1.write(f"{s['code']}. {s['name']}")

        with c2:
            st.progress(min(n_answered / n_q, 1.0) if n_q else 0.0,
                        text=f"{n_answered}/{n_q}" if n_q else "no questions")

        with c3:
            if acc is None:
                c3.markdown("<span style='color:#6B7290;'>—</span>", unsafe_allow_html=True)
            else:
                pct = round(acc * 100)
                color = "#4CAF6D" if pct >= 80 else ("#B8860B" if pct >= 50 else "#E5534B")
                c3.markdown(f"<span style='color:{color}; font-weight:700;'>{pct}%</span>",
                            unsafe_allow_html=True)

        with c4:
            pills = "".join(
                f'<span class="tag-pill" style="font-size:0.72rem; padding:3px 10px; margin-right:4px;">{t}</span>'
                for t in types_here
            ) or "<span style='color:#6B7290;'>—</span>"
            c4.markdown(pills, unsafe_allow_html=True)

        with c5:
            if n_q:
                label = "Resume" if n_answered else "Start"
                if c5.button(label, key=f"study_{s['id']}", use_container_width=True):
                    _go("study", subtopic_id=s["id"])
            else:
                c5.markdown("<span style='color:#6B7290; font-size:0.85em;'>—</span>",
                            unsafe_allow_html=True)



def _study_view(qindex):
    sid = st.session_state.get("_gsse_subtopic")
    topic, sub = get_subtopic(sid)
    if sub is None:
        _go("topics"); return

    qs = qindex.get(sid, [])
    if not qs:
        st.info("No questions in this subtopic yet.")
        return

    # Reset the pointer whenever we land on a new subtopic
    if st.session_state.get("_gsse_qidx_subtopic") != sid:
        st.session_state["_gsse_qidx"] = 0
        st.session_state["_gsse_qidx_subtopic"] = sid
    idx = max(0, min(st.session_state.get("_gsse_qidx", 0), len(qs) - 1))
    st.session_state["_gsse_qidx"] = idx
    q = qs[idx]
    qid = q.get("id", f"study-{idx}")

    flagged = st.session_state.setdefault(f"_gsse_flagged_{sid}", set())
    sp = _sub_progress(sid)
    attempts = sp["attempts"]

    main_col, side_col = st.columns([3, 1], gap="large")

    with main_col:
        top = st.columns([1, 5, 2.2])
        if top[0].button("←", key="study_back", help="Back to topic"):
            _go("subtopics", topic_id=topic["id"])
        top[1].markdown(f"### {topic['icon']} {sub['name']}")
        is_flagged = qid in flagged
        if top[2].button("🚩 Flagged" if is_flagged else "⚑ Flag for review",
                          key=f"flag_{sid}_{qid}", use_container_width=True):
            flagged.symmetric_difference_update({qid})
            st.rerun()

        with st.container(border=True):
            renderer = _RENDERERS.get(q.get("type"), _render_typeA)
            result = renderer(q, key=f"study_{sid}_{qid}")
            if result is not None:
                c, t = result
                _record_attempt(sid, qid, c, t)

        st.write("")
        nav = st.columns([1, 1, 3, 1, 1])
        if nav[0].button("⟵ Prev", disabled=(idx == 0), use_container_width=True):
            st.session_state["_gsse_qidx"] = idx - 1
            st.rerun()
        nav[2].markdown(f"<div style='text-align:center;color:#6B7290;font-size:0.85rem;padding-top:8px;'>"
                         f"Question {idx + 1} of {len(qs)}</div>", unsafe_allow_html=True)
        if nav[4].button("Next ⟶", disabled=(idx == len(qs) - 1), use_container_width=True):
            st.session_state["_gsse_qidx"] = idx + 1
            st.rerun()

    with side_col:
        answered = [(q2.get("id", f"study-{i}"), attempts.get(q2.get("id", f"study-{i}")))
                    for i, q2 in enumerate(qs)]
        answered = [(qid2, a) for qid2, a in answered if a is not None]
        n_correct = sum(1 for _, a in answered if a["correct"] == a["total"])
        n_incorrect = len(answered) - n_correct
        acc = round(n_correct / len(answered) * 100) if answered else 0

        st.markdown(f"""
        <div style="background:#FFFFFF;border:1px solid #E2E6F5;border-radius:14px;padding:18px 20px;">
          <div style="font-weight:700;color:#5B62F2;margin-bottom:12px;">Quiz Progress</div>
          <div style="display:flex;justify-content:space-between;font-size:0.85rem;color:#6B7290;margin-bottom:6px;">
            <span>Question:</span><strong style="color:#1E2233;">{idx + 1} / {len(qs)}</strong>
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
        for row_start in range(0, len(qs), n_cols):
            row_qs = qs[row_start:row_start + n_cols]
            mcols = st.columns(n_cols)
            for j, q2 in enumerate(row_qs):
                i2 = row_start + j
                qid2 = q2.get("id", f"study-{i2}")
                a2 = attempts.get(qid2)
                if a2 is not None:
                    status = "✓" if a2["correct"] == a2["total"] else "✕"
                elif qid2 in flagged:
                    status = "🚩"
                else:
                    status = ""
                label = f"{status}{i2 + 1}" if status else str(i2 + 1)
                if mcols[j].button(label, key=f"map_{sid}_{i2}", use_container_width=True,
                                   type="primary" if i2 == idx else "secondary"):
                    st.session_state["_gsse_qidx"] = i2
                    st.rerun()

        st.caption("✓ correct · ✕ incorrect · 🚩 flagged")



# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def render_gsse(persist_get=None, persist_set=None, user=None):
    user = user or "you"
    st.session_state["_gsse_persist_set"] = persist_set
    st.session_state["_gsse_persist_user"] = user
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
