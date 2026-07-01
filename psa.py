# ─────────────────────────────────────────────────────────────────────────────
#  psa.py  —  Prescribing Safety Assessment section for The Differential
# ─────────────────────────────────────────────────────────────────────────────
#  Renders + marks all 8 PSA item styles. Mount it from app.py with:
#
#      from psa import render_psa
#      ...
#      with tab_psa:
#          render_psa(c, conn, SUPABASE_ENABLED, supabase)
#
#  It reuses the app's existing theme (gold #5B62F2 on dark) and logs attempts to
#  a `psa_attempts` table (created here, idempotent) plus Supabase if enabled.
# ─────────────────────────────────────────────────────────────────────────────

import streamlit as st
from difflib import SequenceMatcher

try:
    from psa_questions import PSA_QUESTIONS
except Exception:
    PSA_QUESTIONS = {}

# ── Style metadata ────────────────────────────────────────────────────────────
STYLE_ORDER = ["PWS", "REV", "MAN", "COM", "CAL", "ADR", "TDM", "DAT"]
STYLE_META = {
    "PWS": {"name": "Prescribing",          "max": 10, "icon": "✍️"},
    "REV": {"name": "Prescription Review",   "max": 4,  "icon": "🔍"},
    "MAN": {"name": "Planning Management",    "max": 2,  "icon": "🧭"},
    "COM": {"name": "Providing Information",  "max": 2,  "icon": "💬"},
    "CAL": {"name": "Calculation Skills",     "max": 2,  "icon": "🧮"},
    "ADR": {"name": "Adverse Drug Reactions", "max": 2,  "icon": "⚠️"},
    "TDM": {"name": "Drug Monitoring",        "max": 2,  "icon": "📉"},
    "DAT": {"name": "Data Interpretation",    "max": 2,  "icon": "📊"},
}
SETTING_NAMES = {
    "MED": "Medicine", "SURG": "Surgery", "ELD": "Elderly care", "PED": "Paediatrics",
    "PSYCH": "Psychiatry", "O&G": "Obstetrics & Gynaecology", "GP": "General practice",
}

# ── Controlled vocab (Appendix I) ─────────────────────────────────────────────
ROUTES = ["PO", "IV", "IM", "SC", "INH", "NEB", "TOP", "SL", "PR", "PV", "buccal",
          "oromucosal", "intradermal", "intravitreal", "nasal", "nasogastric",
          "transdermal", "to left ear", "to right ear", "to both ears",
          "to left eye", "to right eye", "to both eyes"]
FREQUENCIES = ["as required", "once only", "daily", "nightly", "every 30 minutes",
               "every hour", "2-hrly", "3-hrly", "4-hrly", "6-hrly",
               "four times daily (6-hrly)", "8-hrly", "three times daily (8-hrly)",
               "three times daily (as directed)", "12-hrly", "twice daily (12-hrly)",
               "twice daily (as directed)", "every other day", "every 3 days",
               "every 4 days", "twice weekly", "three times weekly", "five times weekly",
               "weekly", "every 2 weeks", "every 4 weeks/monthly", "every 6 weeks",
               "every 8 weeks (2-monthly)", "every 12 weeks (3-monthly)", "m/r"]

# Frequency synonym map → canonical key for marking (order-insensitive)
_FREQ_CANON = {
    "od": "daily", "once daily": "daily", "daily": "daily",
    "bd": "12hrly", "bid": "12hrly", "twice daily": "12hrly", "12-hrly": "12hrly",
    "12 hrly": "12hrly", "twice daily (12-hrly)": "12hrly",
    "tds": "8hrly", "tid": "8hrly", "three times daily": "8hrly", "8-hrly": "8hrly",
    "three times daily (8-hrly)": "8hrly",
    "qds": "6hrly", "qid": "6hrly", "four times daily": "6hrly", "6-hrly": "6hrly",
    "four times daily (6-hrly)": "6hrly",
    "nocte": "nightly", "nightly": "nightly", "at night": "nightly",
    "prn": "as required", "as required": "as required",
    "stat": "once only", "once only": "once only",
    "4-hrly": "4hrly", "2-hrly": "2hrly", "3-hrly": "3hrly",
}
_ROUTE_CANON = {
    "po": "po", "oral": "po", "by mouth": "po", "orally": "po",
    "iv": "iv", "intravenous": "iv", "intravenously": "iv",
    "im": "im", "intramuscular": "im",
    "sc": "sc", "subcut": "sc", "subcutaneous": "sc",
    "inh": "inh", "inhaled": "inh", "inhalation": "inh",
    "neb": "neb", "nebulised": "neb", "nebulized": "neb",
    "top": "top", "topical": "top",
    "sl": "sl", "sublingual": "sl",
    "buccal": "buccal", "oromucosal": "buccal",
    "pr": "pr", "rectal": "pr", "pv": "pv", "vaginal": "pv",
}


# ── Marking helpers ───────────────────────────────────────────────────────────
def _norm_freq(s):
    if not s:
        return ""
    s = str(s).strip().lower()
    # strip a trailing "(...)" qualifier if a base term is present
    for k in sorted(_FREQ_CANON, key=len, reverse=True):
        if k in s:
            return _FREQ_CANON[k]
    return s.replace(" ", "")


def _norm_route(s):
    if not s:
        return ""
    s = str(s).strip().lower()
    s = s.replace("(", " ").replace(")", " ")
    for k in sorted(_ROUTE_CANON, key=len, reverse=True):
        if k in s:
            return _ROUTE_CANON[k]
    return s.replace(" ", "")


def _norm_dose(s):
    """Normalise a dose string to '<number><unit>' for comparison."""
    if not s:
        return ""
    s = str(s).strip().lower().replace(",", "")
    s = (s.replace("micrograms", "mcg").replace("microgram", "mcg")
           .replace("µg", "mcg").replace("ug", "mcg")
           .replace("milligrams", "mg").replace("milligram", "mg")
           .replace("grams", "g").replace("gram", "g")
           .replace("millilitres", "ml").replace("millilitre", "ml")
           .replace("units", "unit"))
    return s.replace(" ", "")


def _drug_score(user_drug, drug_set):
    """Best fuzzy match of the typed drug against the mark scheme → (score, matched_name)."""
    u = (user_drug or "").strip().lower()
    if not u:
        return 0, None
    best_score, best_name, best_ratio = 0, None, 0.0
    for entry in drug_set:
        name = entry["name"].lower()
        # substring containment (handles 'beclometasone' vs 'beclometasone dipropionate')
        contained = u in name or name in u or any(
            tok in name for tok in u.split() if len(tok) > 4)
        ratio = SequenceMatcher(None, u, name).ratio()
        if contained:
            ratio = max(ratio, 0.9)
        if ratio > best_ratio:
            best_ratio, best_score, best_name = ratio, entry["score"], entry["name"]
    if best_ratio >= 0.78:
        return best_score, best_name
    return 0, None


# ── DB ────────────────────────────────────────────────────────────────────────
def _ensure_table(c, conn):
    c.execute("""CREATE TABLE IF NOT EXISTS psa_attempts (
        id INTEGER PRIMARY KEY, item_id TEXT, style TEXT, setting TEXT,
        marks REAL, max_marks REAL, user TEXT DEFAULT 'Terry',
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)""")
    conn.commit()


def _log(c, conn, SUPABASE_ENABLED, supabase, item, marks, max_marks, user):
    if SUPABASE_ENABLED and supabase is not None:
        try:
            supabase.table("psa_attempts").insert({
                "item_id": item["id"], "style": item["type"],
                "setting": item.get("setting", ""), "marks": float(marks),
                "max_marks": float(max_marks), "user": user,
            }).execute()
        except Exception:
            pass
    try:
        c.execute("INSERT INTO psa_attempts (item_id,style,setting,marks,max_marks,user) "
                  "VALUES (?,?,?,?,?,?)",
                  (item["id"], item["type"], item.get("setting", ""),
                   float(marks), float(max_marks), user))
        conn.commit()
    except Exception:
        pass


# ── Small UI helpers ──────────────────────────────────────────────────────────
GOLD, CARD, BORDER, TXT, MUTE = "#5B62F2", "#FFFFFF", "#E2E6F5", "#1E2233", "#6B7290"


def _label(text):
    st.markdown(
        f'<p style="color:{MUTE};font-size:0.7rem;text-transform:uppercase;'
        f'letter-spacing:0.08em;font-weight:700;margin:0 0 6px 0;">{text}</p>',
        unsafe_allow_html=True)


def _stem_card(item):
    """Render the clinical stem with header chips and case/exam/investigation blocks."""
    m = STYLE_META[item["type"]]
    sex = {"M": "man", "F": "woman"}.get(item.get("sex", ""), "patient")
    age = item.get("age", "")
    who = f"{age}-year-old {sex}" if age != "" else sex
    chips = (
        f'<span style="background:#EEF0FE;color:{GOLD};padding:3px 10px;border-radius:20px;'
        f'font-size:0.72rem;font-weight:700;">{m["icon"]} {m["name"]}</span>'
        f'<span style="background:#EEF0FE;color:{MUTE};padding:3px 10px;border-radius:20px;'
        f'font-size:0.72rem;font-weight:600;">{SETTING_NAMES.get(item.get("setting",""), item.get("setting",""))}</span>'
        f'<span style="background:#EEF0FE;color:{MUTE};padding:3px 10px;border-radius:20px;'
        f'font-size:0.72rem;font-weight:600;">{item.get("diagnosis","")}</span>'
    )
    blocks = ""
    stem = item.get("stem", {})
    for key, head in (("case_presentation", "Case presentation"),
                      ("on_examination", "On examination"),
                      ("investigations", "Investigations")):
        if stem.get(key):
            blocks += (
                f'<p style="margin:14px 0 2px 0;font-size:0.78rem;font-weight:700;color:{GOLD};">{head}</p>'
                f'<p style="margin:0;font-size:0.98rem;line-height:1.7;color:{TXT};">{stem[key]}</p>'
            )
    st.markdown(
        f'<div style="background:{CARD};border:1px solid {BORDER};border-radius:12px;'
        f'padding:22px 26px;margin:6px 0 12px 0;user-select:text;">'
        f'<div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:6px;">{chips}</div>'
        f'<p style="margin:10px 0 0 0;font-size:0.82rem;color:{MUTE};">A {who}</p>'
        f'{blocks}</div>',
        unsafe_allow_html=True)


def _lead_in_box(text):
    safe = text.replace("\n", "<br>")
    st.markdown(
        f'<div style="background:#EEF0FE;border:1.5px solid {GOLD};border-radius:10px;'
        f'padding:14px 18px;margin:0 0 16px 0;color:{GOLD};font-weight:600;'
        f'font-size:0.97rem;line-height:1.6;">{safe}</div>',
        unsafe_allow_html=True)


def _result_banner(marks, max_marks):
    pct = (marks / max_marks * 100) if max_marks else 0
    if pct >= 99:
        bg, bd, col, icon = "#EAF7EE", "#4CAF6D", "#2E9E58", "✓"
    elif pct > 0:
        bg, bd, col, icon = "#EEF0FE", GOLD, GOLD, "◑"
    else:
        bg, bd, col, icon = "#FCEDEC", "#E5534B", "#E5534B", "✗"
    st.markdown(
        f'<div style="background:{bg};border:1.5px solid {bd};border-radius:12px;'
        f'padding:12px 18px;margin:14px 0;color:{col};font-weight:700;font-size:1rem;">'
        f'{icon} {marks:g} / {max_marks:g} marks</div>',
        unsafe_allow_html=True)


# ── Per-style renderers ───────────────────────────────────────────────────────
# Each returns (marks, max_marks) when the item has been submitted, else None.

def _render_sba(item, kp):
    """MAN / COM / ADR / TDM / DAT — single best of five."""
    max_marks = STYLE_META[item["type"]]["max"]
    sub_key = f"{kp}_sub"
    if item.get("adr_subtype"):
        _label(f"ADR — Type {item['adr_subtype']}")
    _lead_in_box(item["lead_in"])
    options = item["options"]
    correct = item["correct"]

    if not st.session_state.get(sub_key):
        choice = st.radio("Options", options, key=f"{kp}_r", index=None,
                          label_visibility="collapsed")
        if st.button("Submit", key=f"{kp}_btn", type="primary"):
            if choice is None:
                st.warning("Select an option first.")
            else:
                st.session_state[sub_key] = options.index(choice)
                st.rerun(scope="fragment")
        return None

    chosen = st.session_state[sub_key]
    for i, opt in enumerate(options):
        if i == correct:
            bg, bd, icon = "#EAF7EE", "#4CAF6D", "✓"
        elif i == chosen:
            bg, bd, icon = "#FCEDEC", "#E5534B", "✗"
        else:
            bg, bd, icon = CARD, BORDER, chr(65 + i)
        just = ""
        if item.get("justifications") and i < len(item["justifications"]):
            just = (f'<p style="margin:6px 0 0 0;font-size:0.85rem;color:{MUTE};'
                    f'line-height:1.5;">{item["justifications"][i]}</p>')
        st.markdown(
            f'<div style="background:{bg};border:1px solid {bd};border-radius:10px;'
            f'padding:12px 16px;margin:6px 0;">'
            f'<span style="font-weight:700;color:{TXT};">{icon}&nbsp;&nbsp;{opt}</span>{just}</div>',
            unsafe_allow_html=True)
    marks = max_marks if chosen == correct else 0
    _result_banner(marks, max_marks)
    return marks, max_marks


def _render_cal(item, kp):
    """CAL — numeric answer within tolerance."""
    max_marks = STYLE_META["CAL"]["max"]
    sub_key = f"{kp}_sub"
    _lead_in_box(item["lead_in"])
    if not st.session_state.get(sub_key):
        col1, col2 = st.columns([3, 1])
        with col1:
            val = st.number_input("Answer", key=f"{kp}_num", value=None,
                                  step=0.01, format="%.4f", label_visibility="collapsed",
                                  placeholder="Enter your numeric answer")
        with col2:
            st.markdown(f'<div style="padding:8px 0;color:{GOLD};font-weight:700;">'
                        f'{item.get("unit","")}</div>', unsafe_allow_html=True)
        if st.button("Submit", key=f"{kp}_btn", type="primary"):
            if val is None:
                st.warning("Enter an answer first.")
            else:
                st.session_state[sub_key] = float(val)
                st.rerun(scope="fragment")
        return None

    given = st.session_state[sub_key]
    tol = item.get("tolerance", 0.01)
    ok = abs(given - item["answer"]) <= tol
    marks = max_marks if ok else 0
    _result_banner(marks, max_marks)
    st.markdown(
        f'<div style="background:{CARD};border:1px solid {BORDER};border-radius:10px;'
        f'padding:12px 16px;margin:6px 0;">'
        f'<p style="margin:0;color:{TXT};">Your answer: <b>{given:g} {item.get("unit","")}</b></p>'
        f'<p style="margin:4px 0 0 0;color:{GOLD};">Correct answer: '
        f'<b>{item["answer"]:g} {item.get("unit","")}</b></p></div>',
        unsafe_allow_html=True)
    with st.expander("📖 Working", expanded=not ok):
        st.markdown(item.get("working", ""))
    return marks, max_marks


def _render_rev(item, kp):
    """REV — two questions, tick prescriptions in column A and B (4 marks)."""
    max_marks = STYLE_META["REV"]["max"]
    sub_key = f"{kp}_sub"
    _lead_in_box(item["lead_in"])

    presc = item["prescriptions"]
    qa, qb = item["question_a"], item["question_b"]

    # Current prescription table
    rows = ""
    for i, p in enumerate(presc):
        rows += (
            f'<tr style="border-top:1px solid {BORDER};">'
            f'<td style="padding:8px 10px;color:{TXT};">{p["medicine"]}</td>'
            f'<td style="padding:8px 10px;color:{MUTE};">{p["dose"]}</td>'
            f'<td style="padding:8px 10px;color:{MUTE};">{p["route"]}</td>'
            f'<td style="padding:8px 10px;color:{MUTE};">{p["frequency"]}</td></tr>')
    st.markdown(
        f'<div style="background:{CARD};border:1px solid {BORDER};border-radius:10px;'
        f'overflow:hidden;margin-bottom:14px;"><table style="width:100%;border-collapse:collapse;'
        f'font-size:0.9rem;"><thead><tr style="background:#EEF0FE;">'
        f'<th style="padding:8px 10px;text-align:left;color:{GOLD};">Medicine</th>'
        f'<th style="padding:8px 10px;text-align:left;color:{GOLD};">Dose</th>'
        f'<th style="padding:8px 10px;text-align:left;color:{GOLD};">Route</th>'
        f'<th style="padding:8px 10px;text-align:left;color:{GOLD};">Frequency</th>'
        f'</tr></thead><tbody>{rows}</tbody></table></div>',
        unsafe_allow_html=True)

    names = [p["medicine"] for p in presc]

    if not st.session_state.get(sub_key):
        st.markdown(f'**Question A** — {qa["prompt"]}')
        sel_a = st.multiselect(f"Select {qa['n_select']}", names, key=f"{kp}_a",
                               label_visibility="collapsed", placeholder="Select prescription(s)")
        st.markdown(f'**Question B** — {qb["prompt"]}')
        sel_b = st.multiselect(f"Select {qb['n_select']}", names, key=f"{kp}_b",
                               label_visibility="collapsed", placeholder="Select prescription(s)")
        if st.button("Submit", key=f"{kp}_btn", type="primary"):
            st.session_state[sub_key] = {
                "a": [names.index(x) for x in sel_a],
                "b": [names.index(x) for x in sel_b],
            }
            st.rerun(scope="fragment")
        return None

    sub = st.session_state[sub_key]

    def _score(selected, correct):
        # Strict: full 2 marks only if the selected set exactly matches.
        # Partial 1 mark if all selections are correct but some were missed
        # (no wrong selections). Zero if any wrong selection.
        sset, cset = set(selected), set(correct)
        if sset == cset:
            return 2
        if sset and sset.issubset(cset):
            return 1
        return 0

    ma, mb = _score(sub["a"], qa["correct"]), _score(sub["b"], qb["correct"])

    for letter, q, sel, sc, just in (
        ("A", qa, sub["a"], ma, item.get("justification_a", "")),
        ("B", qb, sub["b"], mb, item.get("justification_b", "")),
    ):
        chosen = ", ".join(names[i] for i in sel) or "— nothing selected —"
        answer = ", ".join(names[i] for i in q["correct"])
        col = "#2E9E58" if sc == 2 else (GOLD if sc == 1 else "#E5534B")
        st.markdown(
            f'<div style="background:{CARD};border:1px solid {BORDER};border-radius:10px;'
            f'padding:12px 16px;margin:8px 0;">'
            f'<p style="margin:0;font-weight:700;color:{GOLD};">Question {letter} '
            f'<span style="color:{col};">({sc}/2)</span></p>'
            f'<p style="margin:6px 0 2px 0;color:{MUTE};font-size:0.85rem;">{q["prompt"]}</p>'
            f'<p style="margin:4px 0 0 0;color:{TXT};">You selected: {chosen}</p>'
            f'<p style="margin:2px 0 0 0;color:{GOLD};">Correct: {answer}</p>'
            f'<p style="margin:8px 0 0 0;color:{MUTE};font-size:0.85rem;line-height:1.5;">{just}</p>'
            f'</div>', unsafe_allow_html=True)

    marks = ma + mb
    _result_banner(marks, max_marks)
    return marks, max_marks


def _render_pws(item, kp):
    """PWS — write a prescription (5 drug + 5 dose/route/freq = 10 marks).

    Drug choice is auto-scored against the mark scheme. The dose/route/frequency
    mark is capped at the drug score (per the manual) and provisionally
    auto-scored against the optimal answer; a stepper lets you confirm/adjust
    the final dosage mark so edge cases aren't silently mis-marked.
    """
    max_marks = STYLE_META["PWS"]["max"]
    sub_key = f"{kp}_sub"
    _lead_in_box(item["lead_in"])

    st.markdown(
        f'<p style="color:{MUTE};font-size:0.8rem;margin:0 0 8px 0;">'
        f'Prescription form: <b style="color:{GOLD};">{item.get("form_type","")}</b></p>',
        unsafe_allow_html=True)

    if not st.session_state.get(sub_key):
        drug = st.text_input("Drug (approved name)", key=f"{kp}_drug",
                             placeholder="e.g. beclometasone dipropionate")
        c1, c2, c3 = st.columns(3)
        with c1:
            dose = st.text_input("Dose", key=f"{kp}_dose", placeholder="e.g. 200 micrograms")
        with c2:
            route = st.selectbox("Route", [""] + ROUTES, key=f"{kp}_route")
        with c3:
            freq = st.selectbox("Frequency", [""] + FREQUENCIES, key=f"{kp}_freq")
        dur = None
        if item.get("form_type") == "general practice":
            dur = st.text_input("Duration of treatment", key=f"{kp}_dur",
                                placeholder="e.g. 28 days")
        if st.button("Submit", key=f"{kp}_btn", type="primary"):
            if not drug.strip():
                st.warning("Enter a drug first.")
            else:
                st.session_state[sub_key] = {"drug": drug, "dose": dose,
                                             "route": route, "freq": freq, "dur": dur}
                st.rerun(scope="fragment")
        return None

    sub = st.session_state[sub_key]
    drug_mark, matched = _drug_score(sub["drug"], item["drug_set"])

    # Provisional dosage auto-score (capped at drug mark)
    opt = item.get("optimal", {})
    fields_ok = sum([
        _norm_dose(sub["dose"]) == _norm_dose(opt.get("dose", "")) and opt.get("dose"),
        _norm_route(sub["route"]) == _norm_route(opt.get("route", "")) and opt.get("route"),
        _norm_freq(sub["freq"]) == _norm_freq(opt.get("frequency", "")) and opt.get("frequency"),
    ])
    auto_dose = round(drug_mark * fields_ok / 3) if drug_mark else 0

    st.markdown(
        f'<div style="background:{CARD};border:1px solid {BORDER};border-radius:10px;'
        f'padding:14px 18px;margin:6px 0;">'
        f'<p style="margin:0;color:{TXT};">Your prescription: <b>{sub["drug"]} {sub["dose"]} '
        f'{sub["route"]} {sub["freq"]}{(" — " + sub["dur"]) if sub.get("dur") else ""}</b></p>'
        f'<p style="margin:8px 0 0 0;color:{GOLD};">Drug choice: <b>{drug_mark}/5</b>'
        f'{(" (matched: " + matched + ")") if matched else " (not in mark scheme / not indicated)"}</p>'
        f'</div>', unsafe_allow_html=True)

    st.markdown(f'<p style="color:{MUTE};font-size:0.82rem;margin:12px 0 4px 0;">'
                f'Dosage mark (max {drug_mark}, capped at the drug score). '
                f'Auto-suggested <b style="color:{GOLD};">{auto_dose}</b> — adjust if needed.</p>',
                unsafe_allow_html=True)
    dose_mark = st.number_input("Dosage mark", min_value=0, max_value=max(drug_mark, 0),
                                value=min(auto_dose, drug_mark), step=1,
                                key=f"{kp}_dosemark", label_visibility="collapsed")

    st.markdown(
        f'<div style="background:#EEF0FE;border:1px solid {GOLD};border-radius:10px;'
        f'padding:12px 16px;margin:10px 0;">'
        f'<p style="margin:0;color:{GOLD};font-weight:700;">Model answer</p>'
        f'<p style="margin:4px 0 0 0;color:{TXT};">{item.get("model_answer","")}'
        f'{(" — for " + item["duration"]) if item.get("duration") else ""}</p>'
        f'<p style="margin:8px 0 0 0;color:{MUTE};font-size:0.85rem;line-height:1.5;">'
        f'{item.get("justification","")}</p></div>', unsafe_allow_html=True)

    with st.expander("📋 Full drug mark scheme"):
        for e in sorted(item["drug_set"], key=lambda x: -x["score"]):
            st.markdown(f"- **{e['score']}** — {e['name']}")

    rec_key = f"{kp}_recorded"
    if rec_key in st.session_state:
        marks = st.session_state[rec_key]
        _result_banner(marks, max_marks)
        return marks, max_marks

    if st.button("✓ Record mark", key=f"{kp}_record", type="primary"):
        st.session_state[rec_key] = drug_mark + dose_mark
        st.rerun(scope="fragment")
    st.caption("Confirm once you're happy with the dosage mark.")
    return None


def _render_item(item, kp):
    _stem_card(item)
    t = item["type"]
    if t == "PWS":
        return _render_pws(item, kp)
    if t == "REV":
        return _render_rev(item, kp)
    if t == "CAL":
        return _render_cal(item, kp)
    return _render_sba(item, kp)


# ── Section practice flow ─────────────────────────────────────────────────────
def _run_section(style, c, conn, SUPABASE_ENABLED, supabase, user):
    items = PSA_QUESTIONS.get(style, [])
    meta = STYLE_META[style]
    idx_key = f"psa_{style}_idx"
    res_key = f"psa_{style}_results"
    idx = st.session_state.get(idx_key, 0)
    results = st.session_state.setdefault(res_key, {})

    head_l, head_r = st.columns([4, 1])
    with head_l:
        st.markdown(f"### {meta['icon']} {meta['name']}")
    with head_r:
        if st.button("← Sections", key=f"psa_back_{style}"):
            st.session_state["psa_section"] = None
            st.rerun()

    if not items:
        st.info("No items in this section yet. Add them to psa_questions.py "
                f'under "{style}" and they will appear here.')
        return

    idx = max(0, min(idx, len(items) - 1))
    st.session_state[idx_key] = idx

    main_col, side_col = st.columns([3, 1], gap="large")

    with main_col:
        item = items[idx]
        kp = f"psa_{style}_{idx}"

        @st.fragment
        def _item_panel(item, kp, results, res_key):
            """PERF: own fragment — submitting an answer (radio pick, number
            entry, matching, or the PWS record-mark flow) only reruns this
            panel, not the whole 10-tab app."""
            outcome = _render_item(item, kp)
            if outcome is not None and item["id"] not in results:
                marks, maxm = outcome
                results[item["id"]] = {"marks": marks, "max": maxm}
                _log(c, conn, SUPABASE_ENABLED, supabase, item, marks, maxm, user)

        _item_panel(item, kp, results, res_key)

        st.write("")
        nav = st.columns([1, 1, 3, 1, 1])
        if nav[0].button("⟵ Prev", disabled=(idx == 0), use_container_width=True, key=f"psa_{style}_prev"):
            st.session_state[idx_key] = idx - 1
            st.rerun()
        nav[2].markdown(f"<div style='text-align:center;color:#6B7290;font-size:0.85rem;padding-top:8px;'>"
                         f"Item {idx + 1} of {len(items)}</div>", unsafe_allow_html=True)
        if nav[4].button("Next ⟶", disabled=(idx == len(items) - 1), use_container_width=True,
                          type="primary", key=f"psa_{style}_next"):
            st.session_state[idx_key] = idx + 1
            st.rerun()

    with side_col:
        n_answered = len(results)
        got = sum(r["marks"] for r in results.values())
        poss = sum(r["max"] for r in results.values())
        pct = round(got / poss * 100) if poss else 0

        st.markdown(f"""
        <div style="background:#FFFFFF;border:1px solid #E2E6F5;border-radius:14px;padding:18px 20px;">
          <div style="font-weight:700;color:#5B62F2;margin-bottom:12px;">Quiz Progress</div>
          <div style="display:flex;justify-content:space-between;font-size:0.85rem;color:#6B7290;margin-bottom:6px;">
            <span>Item:</span><strong style="color:#1E2233;">{idx + 1} / {len(items)}</strong>
          </div>
          <div style="display:flex;justify-content:space-between;font-size:0.85rem;color:#6B7290;margin-bottom:6px;">
            <span>Answered:</span><strong style="color:#1E2233;">{n_answered} / {len(items)}</strong>
          </div>
          <div style="display:flex;justify-content:space-between;font-size:0.85rem;color:#6B7290;margin-bottom:6px;">
            <span>Marks:</span><strong style="color:#4CAF6D;">{got:g} / {poss:g}</strong>
          </div>
          <div style="display:flex;justify-content:space-between;font-size:0.85rem;color:#6B7290;">
            <span>Score:</span><strong style="color:#1E2233;">{pct}%</strong>
          </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div style="font-weight:700;color:#5B62F2;margin:18px 0 8px;">Item Map</div>',
                     unsafe_allow_html=True)
        n_cols = 5
        for row_start in range(0, len(items), n_cols):
            row = list(range(row_start, min(row_start + n_cols, len(items))))
            mcols = st.columns(n_cols)
            for j, i2 in enumerate(row):
                res2 = results.get(items[i2]["id"])
                if res2 is not None:
                    status = "✓" if res2["marks"] >= res2["max"] else ("◑" if res2["marks"] > 0 else "✕")
                else:
                    status = ""
                label = f"{status}{i2 + 1}" if status else str(i2 + 1)
                if mcols[j].button(label, key=f"psa_map_{style}_{i2}", use_container_width=True,
                                   type="primary" if i2 == idx else "secondary"):
                    st.session_state[idx_key] = i2
                    st.rerun()

        st.caption("✓ full marks · ◑ partial · ✕ no marks")

def _style_stats(c, user):
    """Per-style lifetime stats from the DB: distinct items answered + total marks."""
    stats = {}
    try:
        rows = c.execute(
            "SELECT style, COUNT(DISTINCT item_id), COALESCE(SUM(marks),0), COALESCE(SUM(max_marks),0) "
            "FROM psa_attempts WHERE user=? GROUP BY style", (user,)
        ).fetchall()
        for style, n, got, poss in rows:
            stats[style] = {"answered": n, "got": got, "poss": poss}
    except Exception:
        pass
    return stats


# ── Landing page ──────────────────────────────────────────────────────────────
def _landing(c, conn, user):
    st.markdown("### 💊 Prescribing Safety Assessment")
    st.caption("8 item styles · 200 marks · 120 minutes. Choose a section to practise.")

    stats = _style_stats(c, user)
    total_answered = sum(s["answered"] for s in stats.values())
    total_got = sum(s["got"] for s in stats.values())
    total_poss = sum(s["poss"] for s in stats.values())
    overall_pct = round((total_got / total_poss) * 100, 1) if total_poss else 0.0
    total_items = sum(len(PSA_QUESTIONS.get(style, [])) for style in STYLE_ORDER)

    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#5B62F2,#7A80F7); border-radius:16px;
                padding:22px 26px; color:#FFFFFF; margin-bottom:20px;">
      <div style="font-size:0.8rem; opacity:0.85; text-transform:uppercase; letter-spacing:0.08em;">Overall Score</div>
      <div style="font-size:2.4rem; font-weight:800; margin:4px 0 14px;">{overall_pct}%</div>
      <div style="display:flex; gap:32px; flex-wrap:wrap;">
        <div><div style="font-size:1.2rem; font-weight:700;">{total_answered} / {total_items}</div>
             <div style="font-size:0.75rem; opacity:0.85;">Items Attempted</div></div>
        <div><div style="font-size:1.2rem; font-weight:700;">{total_got:g} / {total_poss:g}</div>
             <div style="font-size:0.75rem; opacity:0.85;">Marks Earned</div></div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    c_search, c_sort = st.columns([2.4, 1.4])
    with c_search:
        search = st.text_input("Search sections", key="psa_landing_search",
                                placeholder="🔍  Search sections", label_visibility="collapsed")
    with c_sort:
        sort_by = st.selectbox("Sort by", ["Order", "Name (A–Z)", "Progress", "% Correct"],
                                key="psa_landing_sort", label_visibility="collapsed")
    search_norm = search.strip().lower() if search else ""

    rows = []
    for style in STYLE_ORDER:
        meta = STYLE_META[style]
        n = len(PSA_QUESTIONS.get(style, []))
        s = stats.get(style, {"answered": 0, "got": 0, "poss": 0})
        pct = (s["got"] / s["poss"] * 100) if s["poss"] else None
        rows.append({"style": style, "meta": meta, "n": n, "answered": s["answered"], "pct": pct})

    if search_norm:
        rows = [r for r in rows if search_norm in r["meta"]["name"].lower()]
    if sort_by == "Name (A–Z)":
        rows.sort(key=lambda r: r["meta"]["name"])
    elif sort_by == "Progress":
        rows.sort(key=lambda r: (r["answered"] / r["n"]) if r["n"] else 0, reverse=True)
    elif sort_by == "% Correct":
        rows.sort(key=lambda r: (r["pct"] if r["pct"] is not None else -1), reverse=True)

    if not rows:
        st.info("No sections match your search.")
        return

    h = st.columns([3.4, 2, 1.6, 1.6, 1.4])
    h[0].markdown("**Section**")
    h[1].markdown("**Progress**")
    h[2].markdown("**% Correct**")
    h[3].markdown("**Marks**")
    h[4].markdown("**Start**")
    st.markdown('<hr style="margin:4px 0 8px;">', unsafe_allow_html=True)

    for r in rows:
        style, meta, n, answered, pct = r["style"], r["meta"], r["n"], r["answered"], r["pct"]
        c1, c2, c3, c4, c5 = st.columns([3.4, 2, 1.6, 1.6, 1.4])
        c1.write(f"{meta['icon']} {meta['name']}")
        with c2:
            st.progress(min(answered / n, 1.0) if n else 0.0,
                        text=f"{answered}/{n}" if n else "no items")
        with c3:
            if pct is None:
                c3.markdown("<span style='color:#6B7290;'>—</span>", unsafe_allow_html=True)
            else:
                pctr = round(pct)
                color = "#4CAF6D" if pctr >= 80 else ("#B8860B" if pctr >= 50 else "#E5534B")
                c3.markdown(f"<span style='color:{color}; font-weight:700;'>{pctr}%</span>",
                            unsafe_allow_html=True)
        c4.write(f"{meta['max']} / item")
        with c5:
            if n:
                label = "Resume" if answered else "Start"
                if c5.button(label, key=f"psa_open_{style}", use_container_width=True):
                    st.session_state["psa_section"] = style
                    st.session_state[f"psa_{style}_idx"] = 0
                    st.rerun()
            else:
                c5.markdown("<span style='color:#6B7290; font-size:0.85em;'>—</span>", unsafe_allow_html=True)

# ── Public entry point ────────────────────────────────────────────────────────
def render_psa(c, conn, SUPABASE_ENABLED=False, supabase=None):
    _ensure_table(c, conn)
    user = st.session_state.get("current_user", "Terry")
    section = st.session_state.get("psa_section")
    if section in STYLE_META:
        _run_section(section, c, conn, SUPABASE_ENABLED, supabase, user)
    else:
        _landing(c, conn, user)
