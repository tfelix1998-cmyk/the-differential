"""
stem_format.py — shared question-stem formatting for The Differential.

Two jobs:

1. `stem_html(text)` turns a raw stem into safe, well-spaced HTML.
2. Any run of lab values inside that stem is lifted out of the prose and
   rendered as a real table (Investigation / Result / Reference range) instead
   of being left as a run-on smear like:

       ...laboratory investigations show: * Hb: 130 (135-175) g/L * WCC: 21.1
       (4.0-11.0 x10*9/L) * PLT: 120 (150-400 x10*9/L) * Cr: 68 (60-110 pmol/L)
       Which one of the following is the most appropriate treatment?

Used by uq.py, and importable by app.py / psa.py / gsse.py so every module
formats stems the same way.

    from stem_format import stem_html, inject_stem_css
"""

import html
import re

# Lead-ins that introduce a block of results.
_LEADIN = re.compile(
    r'((?:his|her|their|the)?\s*(?:laboratory |lab |blood |initial |relevant |further )?'
    r'(?:investigations?|results?|tests?|bloods|blood tests|blood gas|'
    r'arterial blood gas|venous blood gas|biochemistry|full blood count)'
    r'\s*(?:reveal(?:ed|s)?|show(?:ed|s)?|demonstrate[sd]?|are as follows|is as follows|include)?'
    r'\s*:)',
    re.I,
)

# One "Name: value" entry. Stops at the next "Name:" or end of block.
# A lab NAME is letters/digits/spaces/hyphens, optionally followed by an
# all-letter abbreviation in brackets ("Parathyroid Hormone (PTH)").
# Critically it may NOT contain '/' or a bracketed number — otherwise
# "Creatinine: 380 pmol/L (60-110) eGFR: 16" gets split with "pmol/L (60-110)
# eGFR" mistaken for the next lab name.
_NAME = r"[A-Za-z0-9][A-Za-z0-9\s\-\+'\.]{0,30}?(?:\s*\([A-Za-z][A-Za-z\s\-]{0,12}\))?"

_ENTRY = re.compile(
    r'(?P<name>' + _NAME + r')'
    r'\s*:\s*'
    r'(?P<val>.+?)'
    r'(?=\s*[\*\u2022]?\s*' + _NAME + r'\s*:\s*[\d<>\-\.]|$)',
    re.S,
)

# A trailing/embedded reference range: "(135-175)", "(135-175 g/L)", "(>90)", "(< 7.5 mmol/day)"
_RANGE = re.compile(r'\(\s*([<>]?\s*[\d\.,]+(?:\s*[-–]\s*[\d\.,]+)?[^)]*)\)')

# A stem only gets a table if the run has at least this many entries — otherwise
# a single incidental "Temperature: 37.9" in prose would get torn into a table.
_MIN_ROWS = 3


def _split_result_and_range(val):
    """Split 'value (range)' into ('value', 'range'). Handles the three shapes
    seen in the banks:
        130 (135-175) g/L        -> result '130 g/L',      range '135-175'
        5.2 mmol/L (3.5-5.0)     -> result '5.2 mmol/L',   range '3.5-5.0'
        16 mL/min/1.73m2 (>90)   -> result '16 mL/min...', range '>90'
    """
    val = val.strip().rstrip('.,;')
    m = _RANGE.search(val)
    if not m:
        return _tidy(val), ""
    ref = m.group(1).strip()
    result = (val[: m.start()] + " " + val[m.end():]).strip()
    result, ref = _tidy(result), _tidy(ref)

    # Unit propagation. The banks write it on one side only:
    #   "Hb: 130 (135-175) g/L"   -> unit on the result
    #   "WCC: 21.1 (4.0-11.0 x10^9/L)" -> unit inside the range
    # Show it on both, so the table reads like a real results sheet.
    unit_re = re.compile(r'(?:[a-zA-Z%°µ][\w%/^·\.]*(?:/[\w\.^]+)*)\s*$')
    def _unit(s):
        s2 = re.sub(r'^[<>]?\s*[\d\.,\s\-–]+', '', s).strip()
        return s2 if s2 and re.search(r'[a-zA-Z%°]', s2) else ""

    ru, fu = _unit(result), _unit(ref)
    if ru and not fu and ref:
        ref = f"{ref} {ru}"
    elif fu and not ru and result:
        result = f"{result} {fu}"
    return result, ref


# OCR turned 'µmol/L' into 'pmol/L' / 'mol/L' / 'jimol/L' throughout the banks.
# This can NOT be blanket-replaced: PTH really is reported in pmol/L. So the
# repair is analyte-specific — only for analytes that are always micromolar.
_MICROMOLAR = re.compile(r'^(creatinine|cr|urea|bilirubin|serum creatinine)$', re.I)


def _fix_units(name, s):
    if _MICROMOLAR.match(name.strip()):
        s = re.sub(r'\b(?:p|ji|u|j)?mol\s*/\s*L\b', 'µmol/L', s, flags=re.I)
    return s


def _tidy(s):
    s = re.sub(r'\s+', ' ', s).strip(' .,;')
    # common OCR artefacts in the source banks
    s = s.replace('x10*9', 'x10^9').replace('x 10°9', 'x10^9').replace('10°9', '10^9')
    return s


def _parse_labs(block):
    """Parse a candidate lab block into [(investigation, result, ref_range)]."""
    # Normalise the OCR'd scientific notation FIRST — the '*' inside 'x10*9/L'
    # is not a bullet, and splitting on it shreds the unit into 'x10 * 9/L'.
    block = re.sub(r'x\s*10\s*[\*°\^]\s*9', 'x10^9', block)
    block = block.replace('\u2022', '*')
    block = re.sub(r'\s*\*\s*', ' * ', block)
    rows = []
    for m in _ENTRY.finditer(block):
        name = _tidy(m.group('name').lstrip('* ').strip())
        val = m.group('val')
        if not name or not re.search(r'\d', val):
            continue
        # a "name" that is really a sentence is not a lab
        if len(name.split()) > 5 or len(name) > 34:
            continue
        result, ref = _split_result_and_range(val)
        if not result:
            continue
        result, ref = _fix_units(name, result), _fix_units(name, ref)
        rows.append((name, result, ref))
    return rows


def _table_html(rows):
    body = "".join(
        f'<tr><td class="lab-name">{html.escape(n)}</td>'
        f'<td class="lab-val">{html.escape(v)}</td>'
        f'<td class="lab-ref">{html.escape(r)}</td></tr>'
        for n, v, r in rows
    )
    return (
        '<table class="lab-table">'
        '<thead><tr><th>Investigation</th><th>Result</th>'
        '<th>Reference range</th></tr></thead>'
        f'<tbody>{body}</tbody></table>'
    )


def _extract_lab_block(text):
    """Find a lab run introduced by a lead-in. Returns (before, rows, tail) or None.

    The source stems run the question straight on after the final value:
        "... Cr: 68 (60-110 pmol/L) Which one of the following is..."
    so the question is split off BEFORE parsing. Cleaning it out afterwards was
    unreliable — it could land in either the result or the reference cell.
    """
    m = _LEADIN.search(text)
    if not m:
        return None
    before = text[: m.start()].strip()
    rest = text[m.end():].strip()

    # Split the trailing question (or any resumed prose sentence) off the block.
    tail = ""
    qm = re.search(
        r'\s((?:Which|What|Select|Choose|Calculate|Identify)\b.*)$', rest, re.S | re.I
    )
    if qm:
        rest, tail = rest[: qm.start()].strip(), qm.group(1).strip()

    rows = _parse_labs(rest)
    if len(rows) < _MIN_ROWS:
        return None
    return before, rows, tail


def stem_html(text):
    """Raw stem -> safe HTML, with any lab run rendered as a table."""
    text = (text or "").strip()
    if not text:
        return ""

    found = _extract_lab_block(text)
    if found:
        before, rows, tail = found
        parts = []
        if before:
            parts.append(_prose_html(before))
        parts.append(_table_html(rows))
        if tail:
            parts.append(_prose_html(tail, lead=True))
        return "".join(parts)

    return _prose_html(text)


def _prose_html(text, lead=False):
    """Paragraphs and '- ' bullet lists. `lead` bolds it (the actual question)."""
    blocks = re.split(r'\n\s*\n', text.strip())
    out = []
    for blk in blocks:
        lines = [l.strip() for l in blk.splitlines() if l.strip()]
        if not lines:
            continue
        if all(l.startswith(("- ", "• ", "* ")) for l in lines):
            items = "".join(
                f"<li>{html.escape(l[2:].strip())}</li>" for l in lines
            )
            out.append(f'<ul class="uq-stem-list">{items}</ul>')
        else:
            cls = ' class="stem-lead"' if lead else ""
            out.append(f"<p{cls}>" + html.escape(" ".join(lines)) + "</p>")
    return "".join(out)


# Shared question CSS for EVERY module (UQ, GSSE, PSA).
#
# Previously the option/explanation styling lived inside uq.py's
# _inject_q_styles(), so GSSE and PSA never received it — their options stayed
# flush and unpadded, and their explanations rendered as one wall of text.
QUESTION_CSS = """
<style>
/* ---- Unanswered options: style st.radio to match the answered .opt-row cards.
   Without this the state you actually READ the question in is the cramped one. */
div[role="radiogroup"] {
    display: flex; flex-direction: column; gap: 10px; margin: 0 0 18px 0;
}
div[role="radiogroup"] > label {
    display: flex; align-items: flex-start; gap: 14px;
    background: #FFFFFF; border: 1.5px solid #E2E6F5;
    border-radius: 14px; padding: 16px 20px; margin: 0;
    cursor: pointer; transition: border-color .15s, background .15s;
    color: #1E2233; font-size: 0.97rem; line-height: 1.5;
    box-shadow: 0 1px 3px rgba(30,34,51,0.05);
}
div[role="radiogroup"] > label:hover { border-color: #5B62F2; background: #F7F8FF; }
div[role="radiogroup"] > label > div:last-child { white-space: normal; }

.opt-row { align-items: flex-start !important; }

/* ---- Explanation: real paragraph rhythm, not one block ---- */
.explanation-box { margin-top: 18px; }
.explanation-box h4 { margin: 0 0 12px !important; font-size: 0.95rem; font-weight: 600; }
.explanation-body p {
    margin: 0 0 12px; font-size: 0.93rem; line-height: 1.65; color: #1E2233;
}
.explanation-body p:last-child { margin-bottom: 0; }

/* ---- Lab results table ---- */
.lab-table {
    width: 100%; border-collapse: separate; border-spacing: 0;
    margin: 16px 0 18px; font-size: 0.9rem;
    border: 1px solid #E2E6F5; border-radius: 12px; overflow: hidden;
    background: #FFFFFF;
}
.lab-table thead th {
    text-align: left; font-weight: 600; color: #1E2233;
    background: #F7F8FF; padding: 12px 16px;
    border-bottom: 1px solid #E2E6F5; font-size: 0.85rem;
}
.lab-table td { padding: 12px 16px; border-bottom: 1px solid #EEF0FA; }
.lab-table tbody tr:last-child td { border-bottom: none; }
.lab-name { font-weight: 600; color: #1E2233; }
.lab-val  { font-weight: 600; color: #1E2233; white-space: nowrap; }
.lab-ref  { color: #6B7290; white-space: nowrap; }
.stem-lead { font-weight: 600; color: #111827; }

/* ---- PSA case sections ---- */
.psa-sec { margin: 14px 0 2px 0; font-size: 0.78rem; font-weight: 700;
           color: #8A6D3B; letter-spacing: .02em; }
.psa-body { margin: 0; font-size: 0.98rem; line-height: 1.7; color: #1E2233; }

@media (max-width: 640px) {
    div[role="radiogroup"] > label { padding: 14px 16px; }
    .lab-table { font-size: 0.82rem; }
    .lab-table thead th, .lab-table td { padding: 9px 10px; }
    .lab-val, .lab-ref { white-space: normal; }
}
</style>
"""

# Back-compat: uq.py imports LAB_TABLE_CSS.
LAB_TABLE_CSS = QUESTION_CSS


def inject_question_css(st):
    """Inject the shared question CSS once per session. Pass in streamlit."""
    if st.session_state.get("_question_css_injected"):
        return
    st.markdown(QUESTION_CSS, unsafe_allow_html=True)
    st.session_state["_question_css_injected"] = True


# alias kept so existing callers keep working
inject_stem_css = inject_question_css


def explanation_paragraphs(text):
    """Split explanation prose into real <p> blocks.

    Shared by uq.py and gsse.py — both previously dumped the whole explanation
    into a single <div>, producing a wall of text with no spacing.
    """
    text = (text or "").strip()
    if not text:
        return ""
    chunks = re.split(r"\n\s*\n", text)
    if len(chunks) == 1:
        chunks = [c for c in text.split("\n") if c.strip()]
    return "".join(f"<p>{html.escape(c.strip())}</p>" for c in chunks if c.strip())


# --- PSA -------------------------------------------------------------------
# PSA stems are ONE long run: "...PMH: COPD... DH: salbutamol... O/E: T 37.1,
# HR 112, BP 116/72... Ix: Na 140, K 4.2, urea 7.2, creatinine 85; CXR ...".
# Split it into labelled sections, and lift the Ix values into a table.
# PSA carries no reference ranges, so that table is two columns, not three.
_PSA_SEC = re.compile(
    r'\b(PMH|DH|SH|FH|O/E|Ix|Obs|Allergies|PC|HPC)\s*[:\u2013-]\s*', re.I)
_PSA_LABEL = {
    "pc": "Presenting complaint", "hpc": "History", "pmh": "Past medical history",
    "dh": "Drug history", "sh": "Social history", "fh": "Family history",
    "o/e": "On examination", "obs": "Observations", "ix": "Investigations",
    "allergies": "Allergies",
}


def _psa_labs(text):
    """'Na 140, K 4.2, urea 7.2, creatinine 85; CXR hyperinflated' ->
    ([(name, value)], trailing_prose)."""
    rows, prose = [], []
    for part in re.split(r'[;,]', text):
        p = part.strip()
        if not p:
            continue
        m = re.match(r'^([A-Za-z][A-Za-z0-9 \-\+/\(\)]{0,24}?)\s+'
                     r'([<>]?\s*[\d\.]+(?:\s*[-/]\s*[\d\.]+)?\s*[A-Za-z%/\^\.]*)$', p)
        if m and re.search(r'\d', m.group(2)):
            rows.append((_tidy(m.group(1)), _tidy(m.group(2))))
        else:
            prose.append(p)
    return rows, "; ".join(prose)


def psa_case_html(text):
    """Render a PSA case_presentation as labelled sections with a results table."""
    text = (text or "").strip()
    if not text:
        return ""
    parts = _PSA_SEC.split(text)
    out = []
    if parts[0].strip():
        out.append(f'<p class="psa-body">{html.escape(parts[0].strip())}</p>')
    for i in range(1, len(parts) - 1, 2):
        tag = parts[i].lower()
        body = parts[i + 1].strip().strip(".;, ")
        label = _PSA_LABEL.get(tag, tag.upper())
        out.append(f'<p class="psa-sec">{html.escape(label)}</p>')
        if tag == "ix":
            rows, prose = _psa_labs(body)
            if len(rows) >= 3:
                cells = "".join(
                    f'<tr><td class="lab-name">{html.escape(n)}</td>'
                    f'<td class="lab-val">{html.escape(v)}</td></tr>'
                    for n, v in rows)
                out.append('<table class="lab-table"><thead><tr>'
                           '<th>Investigation</th><th>Result</th></tr></thead>'
                           f'<tbody>{cells}</tbody></table>')
                if prose:
                    out.append(f'<p class="psa-body">{html.escape(prose)}</p>')
                continue
        out.append(f'<p class="psa-body">{html.escape(body)}</p>')
    return "".join(out)
