"""
dashboard.py — the single, unified Study Dashboard for The Differential.
========================================================================

Before this, stats lived in four silos and the main Dashboard only ever saw
one of them (the standalone MCQ/Viva tabs). Every question answered inside the
GSSE, UQ, LLP and PSA modules was stored — permanently, in Supabase — but never
shown here. And the old dashboard read raw local SQLite, so a Streamlit Cloud
wipe showed zeros even though the data was safe in the cloud.

This module fixes both. `aggregate()` pulls from every source through the
Supabase-first fetch hooks the app already has, normalises them into one shape,
and `render()` draws the clean overview (exam countdown, accuracy, coverage,
trend, weak areas, continue-studying) from that single aggregate.

It owns NO storage of its own — it only reads. All persistence still happens in
the existing log_* / *_save_progress functions. The app wires its data hooks in
via render(hooks=...), so this file never imports app.py (no circular import).

Data sources it reads (all already permanent):
  - mcq_attempts   : standalone MCQ tab           (hooks["fetch_attempts"])
  - viva_reviews   : standalone Viva tab          (hooks["fetch_viva"])
  - {gsse,uq}_progress blobs : module practice     (hooks["module_events"])
  - psa_attempts   : PSA module                    (hooks["fetch_psa"])
"""

import datetime as _dt

import streamlit as st

try:
    from uq import split_category as _split_category
except Exception:
    def _split_category(s):
        s = s or "Uncategorised"
        return (s.split(" :: ", 1) + [""])[:2] if " :: " in s else ("Uncategorised", s)


# Design tokens — reuse the app's existing indigo system, don't invent a new one.
_INK = "#1E2233"
_MUTE = "#6B7290"
_PRIMARY = "#5B62F2"
_GREEN = "#4CAF6D"
_AMBER = "#B8860B"
_RED = "#E5534B"
_BORDER = "#E2E6F5"
_CARD = "#FFFFFF"
_WASH = "#EEF0FE"


def _acc_colour(pct):
    if pct >= 75:
        return _GREEN
    if pct >= 50:
        return _PRIMARY
    return _RED


def _day(ts):
    return str(ts)[:10] if ts else None


# Raw internal category names that should never reach the UI.
_LABEL_FIXES = {
    "__EMED_CUSTOM__": "EMED (custom)",
    "Uncategorised": "General",
    "": "General",
    None: "General",
}


def _pretty(label):
    """Turn a raw stored category/topic into something readable on the dashboard.
    Strips leading underscores/markers and maps known internal names."""
    if label in _LABEL_FIXES:
        return _LABEL_FIXES[label]
    s = str(label).strip()
    # e.g. "__EMED_CUSTOM__" -> already mapped; catch other __X__ forms
    if s.startswith("__") and s.endswith("__") and len(s) > 4:
        s = s[2:-2].replace("_", " ").title()
    return s or "General"


# ---------------------------------------------------------------------------
# Aggregation — the one place that reads every stat source
# ---------------------------------------------------------------------------

def aggregate(user, hooks):
    """Return one normalised stats dict pulled from all sources.

    hooks is a dict of callables the app passes in:
        fetch_attempts(user) -> [{topic, is_correct, ts}]
        fetch_viva(user)     -> [{topic, confidence, ts}]
        module_events(user)  -> [{ts, topic_id, kind, correct, total, source}]
        fetch_psa(user)      -> [{style, marks, max_marks, ts}]  (optional)
        bank_total()         -> int total questions available (optional)
    Any missing hook is simply skipped, so the dashboard degrades gracefully.
    """
    # --- rows: one normalised record per answered item ---
    # {cat, topic, correct(0/1 or None), ts, kind}
    rows = []

    for a in (hooks.get("fetch_attempts", lambda u: [])(user) or []):
        cat, disp = _split_category(a.get("topic") or "Uncategorised")
        rows.append({"cat": cat, "topic": disp, "correct": 1 if a.get("is_correct") else 0,
                     "ts": a.get("ts"), "kind": "mcq"})

    for v in (hooks.get("fetch_viva", lambda u: [])(user) or []):
        cat, disp = _split_category(v.get("topic") or "Uncategorised")
        # Viva has no right/wrong; treat confidence>=2 (Good/Easy) as "on top of it"
        conf = v.get("confidence")
        rows.append({"cat": cat, "topic": disp,
                     "correct": (1 if (conf or 0) >= 2 else 0) if conf is not None else None,
                     "ts": v.get("ts"), "kind": "viva"})

    for e in (hooks.get("module_events", lambda u: [])(user) or []):
        # module events already carry {ts, topic_id, kind, correct, total, source}
        # source is the display category (e.g. "GSSE", "UQ", "LLP")
        n = max(int(e.get("total") or 1), 1)
        c = int(e.get("correct") or 0)
        cat = e.get("source") or e.get("cat") or "Modules"
        topic = e.get("topic_name") or e.get("topic_id") or "—"
        # expand into per-item rows so counts line up with the tab sources
        for i in range(n):
            rows.append({"cat": cat, "topic": topic,
                         "correct": 1 if i < c else 0,
                         "ts": e.get("ts"), "kind": e.get("kind") or "mcq"})

    for p in (hooks.get("fetch_psa", lambda u: [])(user) or []):
        mx = max(int(p.get("max_marks") or 1), 1)
        got = int(p.get("marks") or 0)
        rows.append({"cat": "PSA", "topic": p.get("style") or "PSA",
                     "correct": 1 if got >= mx else 0, "ts": p.get("ts"), "kind": "psa"})

    scored = [r for r in rows if r["correct"] is not None]
    total_answered = len(rows)
    total_scored = len(scored)
    total_correct = sum(r["correct"] for r in scored)
    accuracy = (total_correct / total_scored * 100) if total_scored else 0.0

    # --- per-category / per-topic accuracy ---
    cats = {}
    for r in scored:
        c = cats.setdefault(r["cat"], {"correct": 0, "total": 0, "topics": {}})
        c["correct"] += r["correct"]; c["total"] += 1
        t = c["topics"].setdefault(r["topic"], {"correct": 0, "total": 0})
        t["correct"] += r["correct"]; t["total"] += 1

    # --- weak areas: worst topics with a meaningful sample ---
    weak = []
    for cat, cv in cats.items():
        for tname, tv in cv["topics"].items():
            if tv["total"] >= 3:  # need a few attempts before calling it weak
                weak.append({"cat": _pretty(cat), "topic": _pretty(tname),
                             "pct": round(tv["correct"] / tv["total"] * 100),
                             "n": tv["total"]})
    weak.sort(key=lambda w: (w["pct"], -w["n"]))

    # --- daily trend + streak (needs timestamps) ---
    by_day = {}
    for r in scored:
        d = _day(r["ts"])
        if not d:
            continue
        slot = by_day.setdefault(d, [0, 0])
        slot[1] += 1
        slot[0] += r["correct"]
    days_sorted = sorted(by_day)
    raw_trend = [{"date": d, "acc": round(by_day[d][0] / by_day[d][1] * 100, 1),
                  "n": by_day[d][1]} for d in days_sorted]

    # Smoothed, volume-weighted trend so a 1-question day can't spike to 0/100.
    # For each active day we take a 7-day trailing window and compute accuracy
    # over the POOLED correct/total in that window (weights by volume), then
    # that's the smoothed value. Reads as a real trend, not day-to-day noise.
    trend = []
    for i, d in enumerate(days_sorted):
        d_date = _dt.date.fromisoformat(d)
        window_start = d_date - _dt.timedelta(days=6)
        wc = wt = 0
        for dd in days_sorted[max(0, i - 30):i + 1]:
            if _dt.date.fromisoformat(dd) >= window_start:
                wc += by_day[dd][0]; wt += by_day[dd][1]
        smooth = round(wc / wt * 100, 1) if wt else 0.0
        trend.append({"date": d, "acc": smooth,
                      "raw": raw_trend[i]["acc"], "n": raw_trend[i]["n"]})

    active_days = set(by_day.keys())
    today = _dt.date.today()
    cur = today
    if cur.isoformat() not in active_days and (today - _dt.timedelta(days=1)).isoformat() in active_days:
        cur = today - _dt.timedelta(days=1)  # today not done yet, streak still alive from yesterday
    streak = 0
    while cur.isoformat() in active_days:
        streak += 1
        cur -= _dt.timedelta(days=1)

    # --- continue-studying: recently touched categories under 100% ---
    recent = []
    for cat, cv in cats.items():
        pct = round(cv["correct"] / cv["total"] * 100) if cv["total"] else 0
        recent.append({"cat": _pretty(cat), "pct": pct, "n": cv["total"]})
    recent.sort(key=lambda r: r["n"], reverse=True)

    bank_total = hooks.get("bank_total", lambda: 0)() or 0

    # Per-area accuracy, cleaned and sorted worst-first (this IS the weak-areas
    # view — one list does both jobs, so render() needn't keep two).
    areas = []
    for cat, cv in cats.items():
        if cv["total"] >= 1:
            areas.append({"area": _pretty(cat),
                          "pct": round(cv["correct"] / cv["total"] * 100),
                          "n": cv["total"]})
    areas.sort(key=lambda a: (a["pct"], -a["n"]))

    return {
        "answered": total_answered,
        "scored": total_scored,
        "correct": total_correct,
        "accuracy": accuracy,
        "streak": streak,
        "cats": cats,
        "weak": weak,
        "areas": areas,
        "trend": trend,
        "continue": recent,
        "bank_total": bank_total,
        "coverage": (total_answered / bank_total * 100) if bank_total else 0.0,
    }


# ---------------------------------------------------------------------------
# Small HTML helpers
# ---------------------------------------------------------------------------

def _donut(pct, colour, label, sub):
    """An SVG donut — no chart library, renders instantly."""
    pct = max(0, min(100, pct))
    r = 52
    circ = 2 * 3.14159 * r
    dash = circ * pct / 100
    return f"""
    <svg viewBox="0 0 140 140" style="width:150px;height:150px;">
      <circle cx="70" cy="70" r="{r}" fill="none" stroke="{_WASH}" stroke-width="16"/>
      <circle cx="70" cy="70" r="{r}" fill="none" stroke="{colour}" stroke-width="16"
              stroke-linecap="round" stroke-dasharray="{dash} {circ}"
              transform="rotate(-90 70 70)"/>
      <text x="70" y="66" text-anchor="middle" font-size="26" font-weight="800"
            fill="{_INK}" font-family="system-ui,sans-serif">{pct:.0f}%</text>
      <text x="70" y="88" text-anchor="middle" font-size="11" fill="{_MUTE}"
            font-family="system-ui,sans-serif">{sub}</text>
    </svg>"""


def _hero_card(title, value_html, donut_html, accent):
    return f"""
    <div style="background:{_CARD};border:1px solid {_BORDER};border-radius:18px;
                padding:26px 28px;display:flex;justify-content:space-between;
                align-items:center;height:100%;">
      <div>
        <div style="font-size:1.5rem;font-weight:800;color:{_INK};line-height:1.2;">{title}</div>
        <div style="margin-top:10px;">{value_html}</div>
      </div>
      <div>{donut_html}</div>
    </div>"""


def _stat_card(icon, label, value, foot=""):
    foot_html = (f'<div style="font-size:0.75rem;color:{_MUTE};margin-top:4px;">{foot}</div>'
                 if foot else "")
    return f"""
    <div style="background:{_CARD};border:1px solid {_BORDER};border-radius:14px;
                padding:16px 18px;height:100%;">
      <div style="display:flex;align-items:center;gap:10px;">
        <div style="font-size:1.3rem;">{icon}</div>
        <div style="font-size:0.78rem;color:{_MUTE};font-weight:600;
                    text-transform:uppercase;letter-spacing:0.04em;">{label}</div>
      </div>
      <div style="font-size:1.9rem;font-weight:800;color:{_INK};margin-top:8px;">{value}</div>
      {foot_html}
    </div>"""


# ---------------------------------------------------------------------------
# Render
# ---------------------------------------------------------------------------

def render(user, hooks):
    import pandas as pd

    stats = aggregate(user, hooks)

    # ---- Header: greeting + exam countdown (the hero) ----
    exam_key = f"_exam_date_{user}"
    saved_exam = hooks.get("get_exam_date", lambda u: None)(user)
    hr = _dt.datetime.now().hour
    greeting = ("Good morning" if hr < 12 else
                "Good afternoon" if hr < 18 else "Good evening")
    head_l, head_r = st.columns([3, 2])
    with head_l:
        st.markdown(
            f"<div style='font-size:1.9rem;font-weight:800;color:{_INK};line-height:1.15;'>"
            f"{greeting}, {user} 👋</div>"
            f"<div style='color:{_MUTE};margin-top:2px;'>Here's where your revision stands.</div>",
            unsafe_allow_html=True)
    with head_r:
        default = None
        if saved_exam:
            try:
                default = _dt.date.fromisoformat(saved_exam)
            except Exception:
                default = None
        exam_date = st.date_input("🎯 Exam date", value=default,
                                  key=exam_key, format="DD/MM/YYYY")
        if exam_date and exam_date.isoformat() != (saved_exam or ""):
            hooks.get("set_exam_date", lambda u, d: None)(user, exam_date.isoformat())
        if exam_date:
            days = (exam_date - _dt.date.today()).days
            if days >= 0:
                st.markdown(
                    f"<div style='text-align:right;'><span style='font-size:2rem;font-weight:800;"
                    f"color:{_PRIMARY};'>{days}</span> "
                    f"<span style='color:{_MUTE};'>days to your exam</span></div>",
                    unsafe_allow_html=True)
            else:
                st.markdown(f"<div style='text-align:right;color:{_MUTE};'>exam date passed</div>",
                            unsafe_allow_html=True)

    # ---- Empty state ----
    if stats["answered"] == 0:
        st.info("No practice logged yet. Answer questions in any module — GSSE, UQ, "
                "LLP, PSA, or the MCQ tab — and your progress lands here automatically.")
        return

    st.write("")

    # ---- Hero row: accuracy + coverage donuts ----
    h1, h2 = st.columns(2)
    with h1:
        acc = stats["accuracy"]
        st.markdown(_hero_card(
            "Percentage correct",
            f"<span style='font-size:1.4rem;font-weight:700;color:{_MUTE};'>"
            f"({stats['correct']}/{stats['scored']})</span>",
            _donut(acc, _acc_colour(acc), "", "correct"),
            _PRIMARY), unsafe_allow_html=True)
    with h2:
        cov = stats["coverage"]
        bank = stats["bank_total"]
        st.markdown(_hero_card(
            "Question bank usage",
            f"<span style='font-size:1.4rem;font-weight:700;color:{_MUTE};'>"
            f"({stats['answered']}/{bank})</span>" if bank else
            f"<span style='color:{_MUTE};'>{stats['answered']} answered</span>",
            _donut(cov, _GREEN, "", "covered"),
            _GREEN), unsafe_allow_html=True)

    st.write("")

    # ---- Stat cards ----
    s1, s2, s3, s4 = st.columns(4)
    with s1:
        st.markdown(_stat_card("📝", "Answered", f"{stats['answered']:,}"), unsafe_allow_html=True)
    with s2:
        st.markdown(_stat_card("🎯", "Accuracy", f"{stats['accuracy']:.0f}%"), unsafe_allow_html=True)
    with s3:
        st.markdown(_stat_card("🔥", "Day streak", f"{stats['streak']}",
                               "consecutive study days"), unsafe_allow_html=True)
    with s4:
        n_cats = len(stats["cats"])
        st.markdown(_stat_card("🗂️", "Areas touched", f"{n_cats}"), unsafe_allow_html=True)

    st.write("")

    # ---- Trend line (smoothed, volume-weighted) ----
    st.markdown("#### Accuracy over time")
    trend = stats["trend"]
    if len(trend) >= 2:
        st.caption("7-day rolling average, weighted by questions answered — so a "
                   "light day doesn't swing the line.")
        df = pd.DataFrame(
            [{"Date": t["date"], "Accuracy %": t["acc"]} for t in trend]
        ).set_index("Date")
        st.line_chart(df, height=260, color=_PRIMARY)
    elif len(trend) == 1:
        st.info(f"Today's accuracy: **{trend[0]['acc']:.0f}%** "
                f"({trend[0]['n']} answered). The trend line appears once you've "
                f"studied on two or more days.")
    else:
        st.caption("Answer some questions to start the trend line.")

    st.write("")
    st.write("")

    # ---- Weak Areas — one clean panel (merged; worst-first) ----
    # This replaces the old two side-by-side lists (which showed the same data
    # sorted two ways). One roomy list, full labels, category context on hover.
    st.markdown("#### Weak areas")
    st.caption("Every area you've practised, lowest accuracy first — revise from the top down.")
    areas = stats.get("areas", [])
    if areas:
        st.markdown('<div style="background:{c};border:1px solid {b};border-radius:16px;'
                    'padding:22px 26px;">'.format(c=_CARD, b=_BORDER),
                    unsafe_allow_html=True)
        rows_html = []
        for a in areas:
            col = _acc_colour(a["pct"])
            rows_html.append(
                f'<div style="display:flex;align-items:center;gap:16px;margin:14px 0;">'
                f'  <div style="width:230px;font-size:0.92rem;color:{_INK};font-weight:600;'
                f'       overflow:hidden;text-overflow:ellipsis;white-space:nowrap;" '
                f'       title="{a["area"]}">{a["area"]}</div>'
                f'  <div style="flex:1;background:{_BORDER};border-radius:8px;height:14px;">'
                f'    <div style="width:{a["pct"]}%;background:{col};height:14px;border-radius:8px;'
                f'         transition:width .3s;"></div></div>'
                f'  <div style="width:96px;text-align:right;font-size:0.9rem;font-weight:700;color:{col};">'
                f'    {a["pct"]}% <span style="color:{_MUTE};font-weight:500;font-size:0.8rem;">'
                f'({a["n"]})</span></div>'
                f'</div>')
        st.markdown("".join(rows_html) + "</div>", unsafe_allow_html=True)
    else:
        st.caption("No scored questions yet — answer some and your weakest areas surface here.")

    return stats
