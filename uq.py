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

import html  # module-level: _explanation_paragraphs() needs html.escape
import html
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
    # LLP banks (Longitudinal Learning Plan, Units 3 & 4) — MCQ + VIVA.
    try:
        from llp_questions import LLP_BANKS, LLP_VIVA
    except Exception:
        LLP_BANKS, LLP_VIVA = {}, {}
    # EMED bank (Broad Topic - Pathology) - added to uq module
    try:
        from emed_questions import EMED_BANKS
    except Exception:
        EMED_BANKS = {}
    # Extra EMED banks (extracted practice questions). Merge by CONCATENATING
    # question lists — "Haematology - Anaemia" exists in both files, and a plain
    # dict update would silently drop the original questions.
    try:
        from emed_questions_extra import EMED_BANKS_EXTRA
        EMED_BANKS = dict(EMED_BANKS)
        for _k, _v in EMED_BANKS_EXTRA.items():
            EMED_BANKS[_k] = list(EMED_BANKS.get(_k, [])) + list(_v)
    except Exception:
        pass
    # Rewritten stems for image-dependent questions. Applied as an override map
    # so the 7.1 MB emed_questions.py never needs reopening.
    try:
        from emed_stem_overrides import STEM_OVERRIDES
        try:
            from emed_stem_overrides import ANSWER_OVERRIDES
        except Exception:
            ANSWER_OVERRIDES = {}
        try:
            from emed_stem_overrides import OPTION_OVERRIDES
        except Exception:
            OPTION_OVERRIDES = {}
        EMED_BANKS = dict(EMED_BANKS)
        for _bank in set(STEM_OVERRIDES) | set(ANSWER_OVERRIDES) | set(OPTION_OVERRIDES):
            if _bank not in EMED_BANKS:
                continue
            _qs = [dict(q) for q in EMED_BANKS[_bank]]
            for _i, _stem in STEM_OVERRIDES.get(_bank, {}).items():
                _i = int(_i)
                if 0 <= _i < len(_qs):
                    _qs[_i]["question_text"] = _stem
                    _qs[_i]["image_url"] = ""
            # Answer-key corrections: two questions stored an answer that
            # contradicted their own explanation (OCR mis-detection).
            for _i, _letter in ANSWER_OVERRIDES.get(_bank, {}).items():
                _i = int(_i)
                if 0 <= _i < len(_qs):
                    _qs[_i]["correct_answer_letter"] = _letter
            # Option repair: one question's options were shifted, with
            # explanation text spilled into the last two slots.
            for _i, _opts in OPTION_OVERRIDES.get(_bank, {}).items():
                _i = int(_i)
                if 0 <= _i < len(_qs):
                    _qs[_i]["options"] = list(_opts)
            EMED_BANKS[_bank] = _qs
    except Exception:
        pass
    # Repair the OCR damage, then drop what is left unservable.
    #
    # clean_banks() does BOTH, and it must be the only thing that drops. Every
    # index above (STEM/ANSWER/OPTION overrides) and every index inside it
    # (QUARANTINE, its own BROKEN list) is an index into the *unfiltered* bank.
    # Filter in two places and the second set of indices addresses the wrong
    # questions. So: apply all fixes, take one union of everything to drop,
    # filter once. QUARANTINE is therefore passed IN rather than applied here.
    try:
        from emed_clean import clean_banks
        try:
            from emed_stem_overrides import QUARANTINE
        except Exception:
            QUARANTINE = {}
        EMED_BANKS = clean_banks(EMED_BANKS, quarantine=QUARANTINE)
    except Exception:
        # Cleaner unavailable — fall back to the quarantine drop on its own, so
        # the module still loads (dirty, but servable).
        try:
            from emed_stem_overrides import QUARANTINE
            EMED_BANKS = dict(EMED_BANKS)
            for _bank, _drop in QUARANTINE.items():
                if _bank not in EMED_BANKS:
                    continue
                _bad = set(int(x) for x in _drop)
                EMED_BANKS[_bank] = [q for j, q in enumerate(EMED_BANKS[_bank])
                                     if j not in _bad]
        except Exception:
            pass

    out = {}
    for t in ucfg.UQ_TOPICS:
        # Look up MCQ bank in whichever source has it (IMPORTED for original UQ,
        # EMED for pathology topics, LLP for the Units 3 & 4 prescribing banks).
        mcqs = []
        if t["mcq_bank"]:
            mcqs = (IMPORTED_BANKS.get(t["mcq_bank"])
                    or EMED_BANKS.get(t["mcq_bank"])
                    or LLP_BANKS.get(t["mcq_bank"])
                    or [])
        if t["viva_source"] == "builtin":
            viva = BUILTIN_VIVA.get(t["viva_bank"], []) if t["viva_bank"] else []
        elif t["viva_source"] == "imported":
            viva = IMPORTED_VIVA.get(t["viva_bank"], []) if t["viva_bank"] else []
        elif t["viva_source"] == "llp":
            viva = LLP_VIVA.get(t["viva_bank"], []) if t["viva_bank"] else []
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
    # NOT guarded by a session_state flag. Streamlit rebuilds the element tree
    # each rerun, so a <style> that isn't re-emitted is dropped from the DOM —
    # and because _mcq_card is an @st.fragment, the style sits in the fragment's
    # own slot. With the old guard, question 1 rendered styled and every question
    # after it rendered naked (bare "Single Best Answer", unbolded lead-in).
    try:
        from stem_format import QUESTION_CSS
        st.markdown(QUESTION_CSS, unsafe_allow_html=True)
    except Exception:
        pass
    st.markdown("""
<style>
.uq-type-label {
    font-size: 0.72rem; font-weight: 600; letter-spacing: 0.08em;
    text-transform: uppercase; color: #9ca3af; margin-bottom: 14px;
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

/* Explanation body: the option-by-option critique, lifted out of the wall of
   prose into a real list. */
.explanation-body .expl-list {
    margin: 10px 0; padding: 10px 14px 10px 30px;
    background: #f8fafc; border-radius: 8px; list-style: disc;
}
.explanation-body .expl-list li { margin: 4px 0; line-height: 1.55; }

/* Take-home points. The thing you are meant to walk away with, so it is the
   loudest block on the card — not a grey footnote. */
.uq-klp {
    background: #fffbeb; border: 1px solid #fde68a; border-left: 4px solid #f59e0b;
    border-radius: 0 10px 10px 0; padding: 12px 16px 12px 18px; margin-top: 12px;
}
.uq-klp-h {
    font-size: 0.78rem; font-weight: 700; letter-spacing: .06em;
    text-transform: uppercase; color: #b45309; margin-bottom: 8px;
}
.uq-klp ul { margin: 0; padding-left: 20px; list-style: disc; }
.uq-klp li {
    margin: 6px 0; line-height: 1.55; font-size: 0.92rem;
    font-weight: 600; color: #78350f;
}
.uq-klp li::marker { color: #f59e0b; }
.uq-viva-card {
    background: #f9fafb; border-left: 3px solid #6366f1; border-radius: 0 8px 8px 0;
    padding: 14px 18px; margin: 8px 0; color: #1f2937;
}
.uq-viva-card ul { margin: 0; padding-left: 18px; }
.uq-viva-card li { margin: 4px 0; line-height: 1.5; }

/* ---------------------------------------------------------------------
   UNANSWERED options.
   Previously these rendered as a bare st.radio — flush, unpadded, no gap —
   so the state you actually read the question in was the cramped one, while
   the roomy .opt-row cards only appeared AFTER submitting. This styles the
   radio to match .opt-row so spacing is consistent before and after.
   --------------------------------------------------------------------- */
div[role="radiogroup"] {
    display: flex; flex-direction: column; gap: 10px;
    margin: 0 0 18px 0;
}
div[role="radiogroup"] > label {
    display: flex; align-items: flex-start; gap: 14px;
    background: #FFFFFF; border: 1.5px solid #E2E6F5;
    border-radius: 14px; padding: 16px 20px; margin: 0;
    cursor: pointer; transition: border-color .15s, background .15s;
    color: #1E2233; font-size: 0.97rem; line-height: 1.5;
    box-shadow: 0 1px 3px rgba(30,34,51,0.05);
}
div[role="radiogroup"] > label:hover {
    border-color: #5B62F2; background: #F7F8FF;
}
/* let long option text wrap instead of being clipped to one line */
div[role="radiogroup"] > label > div:last-child { white-space: normal; }

/* Answered rows: top-align so wrapped options don't push the pill off-centre */
.opt-row { align-items: flex-start !important; }

/* Explanation panel: real paragraph rhythm instead of one wall of text */
.explanation-box { margin-top: 18px; }
.explanation-box h4 {
    margin: 0 0 12px !important; font-size: 0.95rem; font-weight: 600;
}
.explanation-body p {
    margin: 0 0 12px; font-size: 0.93rem; line-height: 1.65; color: #1E2233;
}
.explanation-body p:last-child { margin-bottom: 0; }

@media (max-width: 640px) {
    div[role="radiogroup"] > label { padding: 14px 16px; }
    .explanation-box { padding: 16px 18px; }
}
</style>
""", unsafe_allow_html=True)


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
    """Delegate to the shared formatter (stem_format.py) so every module —
    UQ, GSSE, PSA — renders stems the same way, with lab-value runs lifted out
    of the prose into a real table. Falls back to the old inline renderer if
    the module is missing."""
    try:
        from stem_format import stem_html as _shared
        return _shared(text)
    except Exception:
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
        # NOTE: no trailing span here — app.py's `.opt-correct::after` already
        # renders the "Correct" pill. Adding one here printed it twice.
    elif state == "wrong":
        cls += " opt-wrong"
        trailing = ('<span style="margin-left:auto;font-weight:700;color:#FFFFFF;'
                    'background:#E5534B;padding:4px 12px;border-radius:20px;font-size:0.82rem;">Your answer</span>')
    elif state == "dim":
        cls += " opt-dim"
    return f'<div class="{cls}"><span>{text}</span>{trailing}</div>'


def _explanation_paragraphs(text):
    """Split explanation prose into real <p> blocks and <ul> lists.

    Bank explanations arrive as one long run of text. Dumping that into a single
    <div> is what makes the answer panel a wall with no spacing. Split on blank
    lines (falling back to single newlines) so each idea gets its own block, and
    lift the option-by-option critique — which emed_clean marks with "* " — into
    a real bulleted list instead of leaving it inline.
    """
    text = (text or "").strip()
    if not text:
        return ""
    chunks = _re.split(r"\n\s*\n", text)
    if len(chunks) == 1:
        chunks = [c for c in text.split("\n") if c.strip()]

    out, bullets = [], []

    def flush():
        if bullets:
            out.append('<ul class="expl-list">'
                       + "".join(f"<li>{html.escape(b)}</li>" for b in bullets)
                       + "</ul>")
            bullets.clear()

    for c in chunks:
        c = c.strip()
        if not c:
            continue
        if c.startswith(("* ", "- ", "\u2022 ")):
            bullets.append(c[2:].strip())
            continue
        flush()
        out.append(f"<p>{html.escape(c)}</p>")
    flush()
    return "".join(out)


def _key_points_html(points):
    """The take-home panel. `points` may be a list or a legacy single string."""
    if not points:
        return ""
    if isinstance(points, str):
        items = [p.strip() for p in _re.split(r"\n+|(?:^|\s)[\*\u2022]\s+", points)
                 if p.strip()]
    else:
        items = [str(p).strip() for p in points if str(p).strip()]
    if not items:
        return ""
    lis = "".join(f"<li>{html.escape(p)}</li>" for p in items)
    return ('<div class="uq-klp">'
            '<div class="uq-klp-h">\U0001f4a1 Key points</div>'
            f'<ul>{lis}</ul></div>')


def _uq_explanation_html(explanation, key_learning_points=None):
    if explanation:
        st.markdown(f'<div class="explanation-box"><h4>Explanation</h4>'
                    f'<div class="explanation-body">{_explanation_paragraphs(explanation)}</div></div>',
                     unsafe_allow_html=True)
    kp = _key_points_html(key_learning_points)
    if kp:
        st.markdown(kp, unsafe_allow_html=True)


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

    try:
        from stem_format import options_container
        _oc = options_container(st, key)
    except Exception:
        _oc = st.container()
    with _oc:
        picked = st.radio("", options, key=f"{key}_opt", index=None,
                      label_visibility="collapsed",
                      format_func=lambda o: _re.sub(r"^\s*([A-Za-z])[\.\)]\s*", r"\1.  ", o))

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

def _emed_broad_groups(content):
    """Group EMED topics into {broad_system: [(topic_id, subtopic_name, n_mcq)]}.
    EMED topic names look like 'Cardiology - Hypertension'."""
    groups = {}
    for t in ucfg.topics_for_section("EMED"):
        broad, _, path = t["name"].partition(" - ")
        n_mcq = _topic_counts(content, t["id"])[0]
        groups.setdefault(broad.strip(), []).append(
            (t["id"], (path.strip() or broad.strip()), n_mcq))
    for b in groups:
        groups[b].sort(key=lambda x: x[1])
    return groups


def _emed_selector_view(content):
    """UWorld-style test builder: expandable systems -> subtopics with counts and
    checkboxes, then start a combined quiz across everything selected."""
    st.markdown("### 🩺 Build a set")
    st.caption("Choose systems and subtopics, then start a combined quiz.")

    groups = _emed_broad_groups(content)
    def is_sel(tid):
        return st.session_state.get(f"_emed_cb_{tid}", False)
    all_tids = [tid for subs in groups.values() for tid, _, n in subs if n]
    sel_ids = [tid for tid in all_tids if is_sel(tid)]
    total_q = sum(_topic_counts(content, tid)[0] for tid in sel_ids)

    # ── action bar ──
    bar = st.columns([3, 1.3, 1.7])
    bar[0].markdown(f"**{len(sel_ids)} subtopics · {total_q} questions selected**")
    if bar[1].button("Clear all", use_container_width=True, disabled=not sel_ids):
        for tid in all_tids:
            st.session_state[f"_emed_cb_{tid}"] = False
        st.rerun()
    if bar[2].button(f"▶ Start quiz ({total_q})", type="primary",
                     use_container_width=True, disabled=not total_q):
        combined = []
        for broad in sorted(groups):
            for tid, _, n in groups[broad]:
                if is_sel(tid):
                    combined += content.get(tid, {}).get("mcq", [])
        st.session_state["_emed_combined"] = combined
        st.session_state["_emed_combined_name"] = f"{len(sel_ids)} subtopics · {total_q} Qs"
        _go("study", topic_id="__EMED_CUSTOM__")

    search = st.text_input("s", key="_emed_sel_search",
                           placeholder="🔍  Search systems / subtopics",
                           label_visibility="collapsed")
    sn = search.strip().lower() if search else ""
    st.markdown("<hr style='margin:6px 0 12px;'>", unsafe_allow_html=True)

    broads = sorted(groups)
    if sn:
        broads = [b for b in broads
                  if sn in b.lower() or any(sn in p.lower() for _, p, _ in groups[b])]
    if not broads:
        st.info("No systems match your search.")
        return

    cols = st.columns(2)
    for i, broad in enumerate(broads):
        subs = groups[broad]
        if sn and sn not in broad.lower():
            subs = [s for s in subs if sn in s[1].lower()]
        broad_total = sum(n for _, _, n in subs)
        n_here = sum(1 for tid, _, n in subs if is_sel(tid))
        with cols[i % 2]:
            title = f"{broad}  ·  {broad_total} Qs" + (f"   ✓ {n_here}" if n_here else "")
            with st.expander(title, expanded=bool(sn)):
                if st.button("Select all in this system", key=f"_emed_all_{broad}",
                             use_container_width=True):
                    for tid, _, n in groups[broad]:
                        if n:
                            st.session_state[f"_emed_cb_{tid}"] = True
                    st.rerun()
                for tid, path, n in subs:
                    st.checkbox(f"{path}  ({n})", key=f"_emed_cb_{tid}", disabled=(n == 0))


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

    if active_section == "EMED":
        _emed_selector_view(content)
        return

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

    # Combined EMED set built from the selector
    if tid == "__EMED_CUSTOM__":
        mcqs = st.session_state.get("_emed_combined", [])
        name = st.session_state.get("_emed_combined_name", "Custom set")
        top = st.columns([6, 2])
        top[0].markdown(f"### 🩺 EMED — {name}")
        if top[1].button("← Back to builder"):
            _go("topics")
        if not mcqs:
            st.info("No questions selected. Go back and pick some subtopics.")
            return
        _mcq_study_panel("__EMED_CUSTOM__", mcqs)
        return

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
