import streamlit as st
from google import genai as genai_new
from google.genai import types
import PyPDF2
import sqlite3
import json
import re
import io
import os
import hashlib
import time
import pandas as pd
from datetime import date, timedelta

from prompts import VIVA_PROMPT, MCQ_PROMPT, ANKI_PROMPT, IMPORT_MCQ_PROMPT

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="The Differential", page_icon="🧠", layout="wide")

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* Text highlighting in gold when selecting */
::selection { background: #C9A84C; color: #141210; }

/* Metric cards */
[data-testid="metric-container"] {
    background: #1E1B16; border: 1px solid #2E2A22;
    border-radius: 12px; padding: 20px 24px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.4);
}
[data-testid="stMetricValue"] { font-size: 2rem !important; font-weight: 800; color: #C9A84C !important; }
[data-testid="stMetricLabel"] { font-size: 0.75rem !important; color: #8A8070; text-transform: uppercase; letter-spacing: 0.08em; }

/* Radio buttons */
.stRadio > label { font-weight: 600; color: #FAFAF8; margin-bottom: 8px; }
.stRadio > div { gap: 8px !important; }
.stRadio > div > label {
    border: 1.5px solid #2E2A22 !important; border-radius: 10px !important;
    padding: 14px 18px !important; background: #1E1B16 !important;
    color: #FAFAF8 !important; transition: border-color 0.15s, background 0.15s;
    font-size: 0.95rem; cursor: pointer; width: 100%;
}
.stRadio > div > label:hover { border-color: #C9A84C !important; background: #252015 !important; }

/* Buttons */
.stButton > button[kind="primary"] {
    background: #C9A84C !important; color: #141210 !important;
    border: none !important; border-radius: 8px !important;
    font-weight: 700 !important; padding: 10px 24px !important;
    transition: all 0.15s !important;
}
.stButton > button[kind="primary"]:hover {
    background: #D4B86A !important; transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(201,168,76,0.3) !important;
}
.stButton > button { border-radius: 8px !important; font-weight: 600 !important; }

/* Expanders */
.streamlit-expanderHeader {
    background: #1E1B16 !important; border: 1px solid #2E2A22 !important;
    border-radius: 10px !important; font-weight: 600 !important;
    padding: 12px 16px !important; color: #FAFAF8 !important;
}
.streamlit-expanderContent {
    background: #1E1B16 !important; border: 1px solid #2E2A22 !important;
    border-top: none !important; border-radius: 0 0 10px 10px !important;
    padding: 16px !important; color: #FAFAF8 !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] { gap: 4px; background: transparent; border-bottom: 1px solid #2E2A22; }
.stTabs [data-baseweb="tab"] { border-radius: 8px 8px 0 0 !important; font-weight: 600 !important; padding: 10px 20px !important; color: #8A8070 !important; }
.stTabs [aria-selected="true"] { color: #C9A84C !important; border-bottom: 2px solid #C9A84C !important; }

/* Progress bar */
.stProgress > div > div { background: #C9A84C !important; }

/* Text inputs */
.stTextArea textarea, .stTextInput input {
    background: #1E1B16 !important; border: 1.5px solid #2E2A22 !important;
    color: #FAFAF8 !important; border-radius: 8px !important;
}
.stTextArea textarea:focus, .stTextInput input:focus { border-color: #C9A84C !important; }

/* Dataframe */
[data-testid="stDataFrame"] { border: 1px solid #2E2A22 !important; border-radius: 10px !important; overflow: hidden; }

/* Sidebar */
[data-testid="stSidebar"] { background: #141210 !important; border-right: 1px solid #2E2A22; }

/* Divider */
hr { border-color: #2E2A22 !important; }

/* Heatmap */
.heatmap-grid { display: flex; flex-wrap: wrap; gap: 3px; margin: 12px 0; }
.heatmap-cell { width: 14px; height: 14px; border-radius: 3px; }

/* Streak badge */
.streak-badge {
    display: inline-flex; align-items: center; gap: 6px;
    background: #252015; border: 1px solid #C9A84C;
    border-radius: 20px; padding: 6px 14px;
    font-weight: 700; font-size: 0.95rem; color: #C9A84C;
}

/* Mode cards */
.mode-card {
    background: #1E1B16; border: 2px solid #2E2A22;
    border-radius: 16px; padding: 28px 24px;
    cursor: pointer; transition: all 0.2s;
    text-align: center;
}
.mode-card:hover { border-color: #C9A84C; background: #252015; }

/* Option rows in exam mode */
.opt-row {
    display: flex; align-items: center; gap: 14px;
    background: #1E1B16; border: 1.5px solid #2E2A22;
    border-radius: 12px; padding: 16px 20px;
    margin-bottom: 10px; cursor: pointer;
    transition: border-color 0.15s, background 0.15s;
    color: #FAFAF8; font-size: 0.97rem; line-height: 1.5;
}
.opt-row:hover { border-color: #C9A84C; background: #252015; }
.opt-correct { background: #1A3020 !important; border-color: #4CAF50 !important; }
.opt-wrong   { background: #2A1010 !important; border-color: #EF5350 !important; }
.opt-dim     { opacity: 0.45; }

.badge {
    min-width: 32px; height: 32px; border-radius: 8px;
    display: inline-flex; align-items: center; justify-content: center;
    font-weight: 700; font-size: 0.85rem; background: #2E2A22; color: #8A8070;
    flex-shrink: 0;
}
.badge-correct { background: #4CAF50 !important; color: #141210 !important; }
.badge-wrong   { background: #EF5350 !important; color: #FAFAF8 !important; }
.badge-gold    { background: #C9A84C !important; color: #141210 !important; }

/* ── Phase 3 polish ── */

/* Compact navigator buttons (the Items 1..N column) */
[data-testid="column"]:first-child .stButton > button {
    padding: 6px 8px !important;
    font-size: 0.82rem !important;
    font-family: monospace !important;
    text-align: left !important;
    border-radius: 6px !important;
    border: 1px solid #2E2A22 !important;
    background: #1A1813 !important;
    color: #C9B98A !important;
    margin-bottom: 2px !important;
    min-height: 0 !important;
    line-height: 1.2 !important;
}
[data-testid="column"]:first-child .stButton > button:hover {
    border-color: #C9A84C !important;
    background: #252015 !important;
    color: #FAFAF8 !important;
}

/* Tighter option rows with a subtle lift */
.opt-row {
    box-shadow: 0 1px 3px rgba(0,0,0,0.25);
}
.opt-correct { box-shadow: 0 0 0 1px #4CAF50 inset; }
.opt-wrong   { box-shadow: 0 0 0 1px #EF5350 inset; }

/* Radio options as clean cards in exam mode (pre-submission) */
.stRadio > div > label {
    box-shadow: 0 1px 3px rgba(0,0,0,0.25);
    line-height: 1.5 !important;
}

/* Expander as a quieter, flatter panel */
.streamlit-expanderHeader { font-size: 0.9rem !important; }

/* Reduce default vertical gaps between blocks for a denser, exam-like feel */
[data-testid="stVerticalBlock"] { gap: 0.6rem !important; }

/* Primary action buttons a touch chunkier */
.stButton > button[kind="primary"] { letter-spacing: 0.02em; }

/* Metric cards: subtle hover lift on dashboard */
[data-testid="metric-container"] { transition: transform 0.12s, border-color 0.12s; }
[data-testid="metric-container"]:hover { transform: translateY(-2px); border-color: #3A352B; }
</style>
""", unsafe_allow_html=True)

# ── Gemini ────────────────────────────────────────────────────────────────────
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
if not GEMINI_API_KEY:
    st.error("**API key missing.** Run: `export GEMINI_API_KEY='your-key'` then restart.")
    st.stop()

client = genai_new.Client(api_key=GEMINI_API_KEY)
MODEL = "gemini-2.5-flash"
FALLBACK_MODEL = "gemini-2.5-flash-lite"  # tried if the primary is overloaded

# ── Database ──────────────────────────────────────────────────────────────────
conn = sqlite3.connect("study_data.db", check_same_thread=False)
c = conn.cursor()
c.execute("""CREATE TABLE IF NOT EXISTS mcq_attempts (
    id INTEGER PRIMARY KEY, topic TEXT, question_text TEXT,
    selected_answer TEXT, correct_answer TEXT, is_correct BOOLEAN,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)""")
c.execute("""CREATE TABLE IF NOT EXISTS viva_reviews (
    id INTEGER PRIMARY KEY, topic TEXT, question_text TEXT,
    confidence INTEGER, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)""")
# Permanent cache of generated content, keyed by a hash of the PDF text.
# Once a document is generated, it is saved here forever — re-opening it loads
# from storage with ZERO API calls.
c.execute("""CREATE TABLE IF NOT EXISTS generated_content (
    doc_hash TEXT PRIMARY KEY, topic TEXT,
    viva_json TEXT, mcq_json TEXT, anki_text TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)""")
conn.commit()


def doc_fingerprint(pdf_text):
    """A stable hash of the document text — identifies a document uniquely."""
    return hashlib.sha256(pdf_text.encode("utf-8")).hexdigest()


def load_from_cache(doc_hash):
    """Return saved generation for this document, or None if not generated yet."""
    row = c.execute(
        "SELECT viva_json, mcq_json, anki_text FROM generated_content WHERE doc_hash=?",
        (doc_hash,)
    ).fetchone()
    if not row:
        return None
    viva_json, mcq_json, anki_text = row
    return {
        "viva": json.loads(viva_json) if viva_json else [],
        "mcqs": json.loads(mcq_json) if mcq_json else [],
        "anki": anki_text or "",
    }


def save_to_cache(doc_hash, topic, viva, mcqs, anki):
    """Persist a document's generated content permanently."""
    c.execute(
        "INSERT OR REPLACE INTO generated_content "
        "(doc_hash, topic, viva_json, mcq_json, anki_text) VALUES (?,?,?,?,?)",
        (doc_hash, topic, json.dumps(viva), json.dumps(mcqs), anki)
    )
    conn.commit()


def list_topics_with_mcqs():
    """Return [(topic, doc_hash, mcq_count), …] for every saved doc that has MCQs."""
    rows = c.execute("SELECT topic, doc_hash, mcq_json FROM generated_content").fetchall()
    out = []
    for topic, doc_hash, mcq_json in rows:
        try:
            n = len(json.loads(mcq_json)) if mcq_json else 0
        except Exception:
            n = 0
        if n > 0:
            out.append((topic, doc_hash, n))
    return sorted(out, key=lambda x: x[0].lower())


def get_mcqs_for_hash(doc_hash):
    row = c.execute("SELECT mcq_json FROM generated_content WHERE doc_hash=?", (doc_hash,)).fetchone()
    if not row or not row[0]:
        return []
    try:
        return json.loads(row[0])
    except Exception:
        return []

# ── Helpers ───────────────────────────────────────────────────────────────────
def extract_text_from_pdf(f):
    reader = PyPDF2.PdfReader(io.BytesIO(f.read()))
    return "\n\n".join(p.extract_text() for p in reader.pages if p.extract_text())

def call_gemini(prompt_template, material, max_retries=4):
    """
    Call Gemini with resilience:
      • Retries on rate limits (429) and 'model overloaded' (503).
      • If the primary model stays unavailable, falls back to the lite model.
    """
    prompt = prompt_template.format(material=material)
    models_to_try = [MODEL, FALLBACK_MODEL]

    for model_name in models_to_try:
        for attempt in range(max_retries):
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(temperature=0.0),
                )
                return response.text
            except Exception as e:
                msg = str(e).lower()
                is_rate_limit = "429" in msg or "quota" in msg or "resource_exhausted" in msg
                is_overloaded = "503" in msg or "unavailable" in msg or "high demand" in msg or "overloaded" in msg

                if (is_rate_limit or is_overloaded) and attempt < max_retries - 1:
                    # Back off: 8s, 16s, 24s … then on final attempt, fall through
                    # to the next model in the list.
                    time.sleep(8 * (attempt + 1))
                    continue
                # Out of retries for this model — break to try the fallback model
                if (is_rate_limit or is_overloaded) and model_name != models_to_try[-1]:
                    break
                raise
    # Should not reach here, but just in case
    raise RuntimeError("All models unavailable after retries.")

def parse_json(raw):
    """Parse JSON from model output, tolerating fences, stray text, and minor errors."""
    clean = re.sub(r"```(?:json)?", "", raw).replace("```", "").strip()

    # Attempt 1: parse as-is
    try:
        return json.loads(clean)
    except json.JSONDecodeError:
        pass

    # Attempt 2: isolate the array between the first [ and last ]
    start, end = clean.find("["), clean.rfind("]")
    if start != -1 and end != -1 and end > start:
        body = clean[start:end + 1]
        try:
            return json.loads(body)
        except json.JSONDecodeError:
            # Attempt 3: remove trailing commas before } or ] (a common model slip)
            repaired = re.sub(r",\s*([}\]])", r"\1", body)
            try:
                return json.loads(repaired)
            except json.JSONDecodeError:
                # Attempt 4: salvage — parse each complete {...} object individually
                # and keep the ones that are valid. Drops only the broken object(s).
                objs = []
                depth, obj_start = 0, None
                for idx, ch in enumerate(repaired):
                    if ch == "{":
                        if depth == 0:
                            obj_start = idx
                        depth += 1
                    elif ch == "}":
                        depth -= 1
                        if depth == 0 and obj_start is not None:
                            chunk = repaired[obj_start:idx + 1]
                            try:
                                objs.append(json.loads(chunk))
                            except json.JSONDecodeError:
                                pass  # skip the one broken object
                            obj_start = None
                if objs:
                    return objs
    raise json.JSONDecodeError("Could not parse model output", clean, 0)

def call_and_parse(prompt_template, material, attempts=2):
    """Call Gemini and parse JSON. If parsing fails, regenerate once more."""
    last_err = None
    for _ in range(attempts):
        raw = call_gemini(prompt_template, material)
        try:
            return parse_json(raw)
        except json.JSONDecodeError as e:
            last_err = e
            time.sleep(2)
            continue
    raise last_err

def fmt_time(seconds):
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    if h: return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"

def calculate_streak():
    rows = c.execute("""SELECT DISTINCT date(timestamp) as d FROM (
        SELECT timestamp FROM mcq_attempts UNION ALL SELECT timestamp FROM viva_reviews
    ) ORDER BY d DESC""").fetchall()
    if not rows: return 0
    streak, today = 0, date.today()
    for i, (d_str,) in enumerate(rows):
        d = date.fromisoformat(d_str)
        if d == today - timedelta(days=i): streak += 1
        else: break
    return streak

def build_heatmap_html(days=182):
    today = date.today()
    activity = {}
    for d_str, cnt in c.execute("""SELECT date(timestamp), COUNT(*) FROM (
        SELECT timestamp FROM mcq_attempts UNION ALL SELECT timestamp FROM viva_reviews
    ) GROUP BY date(timestamp)""").fetchall():
        activity[d_str] = cnt
    cells = []
    for i in range(days - 1, -1, -1):
        d = today - timedelta(days=i)
        cnt = activity.get(d.isoformat(), 0)
        color = ["#2E2A22","#C6E48B","#7BC96F","#239A3B","#196127"][min(cnt//3, 4)] if cnt else "#2E2A22"
        cells.append(f'<div class="heatmap-cell" style="background:{color}" title="{d.strftime("%b %d")}: {cnt}"></div>')
    return f'<div class="heatmap-grid">{"".join(cells)}</div>'

# Cap on PDF text sent to the model. 200k chars (~35-40 pages / a full lecture
# transcript) covers almost any single document while preventing a freak huge
# upload from blowing the token limit and failing the whole request.
MAX_CHARS = 200000

def generate_section(section, pdf_text, topic_name):
    """Generate ONE section on demand, save it to the cache, keep the others intact."""
    doc_hash = doc_fingerprint(pdf_text)
    material = pdf_text[:MAX_CHARS]
    try:
        if section == "viva":
            data = call_and_parse(VIVA_PROMPT, material)
            data = [q for q in data if q.get("question") != "👉 COMPLETE"]
            st.session_state["viva_data"] = data
            st.session_state["viva_revealed"] = {}
            st.session_state["viva_confidence_logged"] = {}
        elif section == "mcq":
            st.session_state["mcqs"] = call_and_parse(MCQ_PROMPT, material)
            st.session_state["mcq_submitted"] = {}
            st.session_state["mcq_mode"] = None
            st.session_state["mcq_exam_idx"] = 0
            st.session_state["exam_start_time"] = None
        elif section == "anki":
            st.session_state["anki_result"] = call_gemini(ANKI_PROMPT, material)
        st.session_state["gen_errors"] = []
    except Exception as e:
        st.session_state["gen_errors"] = [f"{section.upper()}: {e}"]

    # Persist all three (whatever is currently in state) so nothing is lost
    save_to_cache(
        doc_hash, topic_name,
        st.session_state.get("viva_data", []),
        st.session_state.get("mcqs", []),
        st.session_state.get("anki_result", ""),
    )

def call_gemini_two(prompt_template, questions, answers, max_retries=4):
    """Like call_gemini but for a prompt that takes separate questions + answers."""
    prompt = prompt_template.format(questions=questions[:MAX_CHARS], answers=answers[:MAX_CHARS])
    models_to_try = [MODEL, FALLBACK_MODEL]
    for model_name in models_to_try:
        for attempt in range(max_retries):
            try:
                resp = client.models.generate_content(
                    model=model_name, contents=prompt,
                    config=types.GenerateContentConfig(temperature=0.0),
                )
                return resp.text
            except Exception as e:
                msg = str(e).lower()
                transient = any(k in msg for k in ["429","quota","resource_exhausted","503","unavailable","high demand","overloaded"])
                if transient and attempt < max_retries - 1:
                    time.sleep(8 * (attempt + 1)); continue
                if transient and model_name != models_to_try[-1]:
                    break
                raise
    raise RuntimeError("All models unavailable after retries.")


def import_paper(questions_text, answers_text, topic_name, doc_hash):
    """Extract & reformat an existing paper into the MCQ structure, then cache it."""
    try:
        raw = call_gemini_two(IMPORT_MCQ_PROMPT, questions_text, answers_text)
        mcqs = parse_json(raw)
        st.session_state["mcqs"] = mcqs
        st.session_state["mcq_submitted"] = {}
        st.session_state["mcq_mode"] = None
        st.session_state["mcq_exam_idx"] = 0
        st.session_state["exam_start_time"] = None
        st.session_state["gen_errors"] = []
    except Exception as e:
        st.session_state["gen_errors"] = [f"Import: {e}"]
    # Save into the same cache structure (viva/anki stay empty for imported papers)
    save_to_cache(
        doc_hash, topic_name,
        st.session_state.get("viva_data", []),
        st.session_state.get("mcqs", []),
        st.session_state.get("anki_result", ""),
    )

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🧠 The Differential")
    st.markdown("---")

    app_mode = st.radio(
        "Mode",
        ["📝 Generate from notes", "📥 Import existing paper"],
        label_visibility="collapsed",
    )

    pdf_text = ""
    topic_name = "General"
    import_questions_text = ""
    import_answers_text = ""

    if app_mode == "📝 Generate from notes":
        st.markdown("**📄 Study Material**")
        uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"], label_visibility="collapsed")
        if uploaded_file:
            with st.spinner("Reading PDF…"):
                pdf_text = extract_text_from_pdf(uploaded_file)
            topic_name = uploaded_file.name
            if pdf_text.strip():
                st.success(f"✅ {uploaded_file.name}")
                st.caption(f"{len(pdf_text):,} characters")
                with st.expander("Preview"):
                    st.text(pdf_text[:1200] + ("…" if len(pdf_text) > 1200 else ""))
            else:
                st.warning("⚠️ No text found — scanned PDF? Try OCR first.")
    else:
        st.markdown("**📥 Import Existing Paper**")
        st.caption("Upload the questions, then the answer key.")
        q_file = st.file_uploader("Questions PDF", type=["pdf"], key="imp_q")
        a_file = st.file_uploader("Answer key PDF", type=["pdf"], key="imp_a")
        if q_file:
            with st.spinner("Reading questions…"):
                import_questions_text = extract_text_from_pdf(q_file)
            st.success(f"✅ Questions: {q_file.name}")
            topic_name = q_file.name
        if a_file:
            with st.spinner("Reading answer key…"):
                import_answers_text = extract_text_from_pdf(a_file)
            st.success(f"✅ Answers: {a_file.name}")

    st.markdown("---")
    st.markdown("**🗓️ Exam Countdown**")
    exam_date = st.date_input("Exam date", value=date.today() + timedelta(days=30),
                               min_value=date.today(), label_visibility="collapsed")
    days_left = (exam_date - date.today()).days
    urgency = "#4CAF50" if days_left > 14 else "#C9A84C" if days_left > 7 else "#EF5350"
    st.markdown(
        f'<div style="background:#1E1B16;border:1px solid #2E2A22;border-radius:12px;'
        f'text-align:center;padding:20px;">'
        f'<div style="font-size:2.8rem;font-weight:800;color:{urgency};">{days_left}</div>'
        f'<div style="color:#8A8070;font-size:0.75rem;text-transform:uppercase;letter-spacing:0.08em;">Days to Exam</div>'
        f'</div>', unsafe_allow_html=True
    )
    st.markdown("---")
    st.caption("Built with Streamlit + Gemini")

# ── On upload: load this document's saved content (if any). Never auto-generate. ──
# Each tab generates its own content on demand, so an upload costs zero API calls.
if pdf_text.strip() and st.session_state.get("current_doc") != doc_fingerprint(pdf_text):
    doc_hash = doc_fingerprint(pdf_text)
    cached = load_from_cache(doc_hash)

    st.session_state["current_doc"] = doc_hash
    st.session_state["viva_data"] = cached["viva"] if cached else []
    st.session_state["mcqs"] = cached["mcqs"] if cached else []
    st.session_state["anki_result"] = cached["anki"] if cached else ""
    # Reset per-document interaction state
    st.session_state["viva_revealed"] = {}
    st.session_state["viva_confidence_logged"] = {}
    st.session_state["mcq_submitted"] = {}
    st.session_state["mcq_mode"] = None
    st.session_state["mcq_exam_idx"] = 0
    st.session_state["exam_start_time"] = None
    st.session_state["gen_errors"] = []
    st.session_state["loaded_from_cache"] = bool(cached)
    st.rerun()

# ── Import mode: when both files are present, set up the document & load cache ──
import_ready = bool(import_questions_text.strip()) and bool(import_answers_text.strip())
if import_ready:
    combined = import_questions_text + "\n=====ANSWERS=====\n" + import_answers_text
    imp_hash = doc_fingerprint(combined)
    if st.session_state.get("current_doc") != imp_hash:
        cached = load_from_cache(imp_hash)
        st.session_state["current_doc"] = imp_hash
        st.session_state["mcqs"] = cached["mcqs"] if cached else []
        st.session_state["viva_data"] = cached["viva"] if cached else []
        st.session_state["anki_result"] = cached["anki"] if cached else ""
        st.session_state["mcq_submitted"] = {}
        st.session_state["mcq_mode"] = None
        st.session_state["mcq_exam_idx"] = 0
        st.session_state["exam_start_time"] = None
        st.session_state["gen_errors"] = []
        st.session_state["loaded_from_cache"] = bool(cached)
        st.session_state["is_imported"] = True
        st.rerun()

# ── Header ────────────────────────────────────────────────────────────────────
streak = calculate_streak()
col_title, col_streak = st.columns([4, 1])
with col_title:
    st.markdown("# 🧠 The Differential")
    st.caption("AI-powered study companion for final-year medicine.")
with col_streak:
    st.markdown(
        f'<div style="text-align:right;padding-top:12px;">'
        f'<span class="streak-badge">🔥 {streak} day streak</span></div>',
        unsafe_allow_html=True
    )

pdf_ready = bool(pdf_text.strip())
import_ready = bool(import_questions_text.strip()) and bool(import_answers_text.strip())

if pdf_ready and st.session_state.get("loaded_from_cache"):
    st.success("📂 Loaded from saved — no API calls used. This document was generated previously.")

# Show any generation errors persistently (until next successful generation)
if st.session_state.get("gen_errors"):
    for err in st.session_state["gen_errors"]:
        st.error(f"⚠️ Generation issue → {err}")

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab_dash, tab_viva, tab_mcq, tab_anki, tab_mock = st.tabs(
    ["📈  Dashboard", "🗣️  Viva", "📝  MCQ", "🗂️  Anki", "🎯  Mock Exam"]
)

# ═════════════════════════════════════════════════════════════════════════════
# DASHBOARD TAB
# ═════════════════════════════════════════════════════════════════════════════
with tab_dash:
    st.markdown("### Study Dashboard")

    total_mcqs   = c.execute("SELECT COUNT(*) FROM mcq_attempts").fetchone()[0]
    correct_mcqs = c.execute("SELECT COUNT(*) FROM mcq_attempts WHERE is_correct=1").fetchone()[0]
    accuracy     = (correct_mcqs / total_mcqs * 100) if total_mcqs else 0
    total_viva   = c.execute("SELECT COUNT(*) FROM viva_reviews").fetchone()[0]
    easy_n  = c.execute("SELECT COUNT(*) FROM viva_reviews WHERE confidence=3").fetchone()[0]
    good_n  = c.execute("SELECT COUNT(*) FROM viva_reviews WHERE confidence=2").fetchone()[0]
    hard_n  = c.execute("SELECT COUNT(*) FROM viva_reviews WHERE confidence=1").fetchone()[0]

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("MCQs Attempted",      total_mcqs)
    m2.metric("Correct Answers",     correct_mcqs)
    m3.metric("Overall Accuracy",    f"{accuracy:.1f}%")
    m4.metric("Viva Reviews",        total_viva)
    st.markdown("")

    st.markdown("#### 📅 Activity Heatmap")
    st.markdown(
        '<div style="background:#1E1B16;border:1px solid #2E2A22;border-radius:12px;padding:20px 24px;">'
        + build_heatmap_html() +
        '<div style="font-size:0.75rem;color:#8A8070;margin-top:6px;">⬜ None &nbsp; 🟩 1–2 &nbsp; 🟩 3–7 &nbsp; 🟩 8+</div>'
        '</div>', unsafe_allow_html=True
    )
    st.markdown("")

    col_l, col_r = st.columns(2)
    with col_l:
        st.markdown("#### 📈 MCQ Accuracy Over Time")
        history = c.execute("SELECT timestamp, is_correct FROM mcq_attempts ORDER BY timestamp ASC").fetchall()
        if history:
            daily = {}
            for ts, ok in history:
                d = ts.split(" ")[0]
                if d not in daily: daily[d] = [0, 0]
                daily[d][1] += 1
                if ok: daily[d][0] += 1
            df_acc = pd.DataFrame([{"date": d, "Accuracy (%)": v[0]/v[1]*100} for d, v in daily.items()]).set_index("date")
            st.line_chart(df_acc, height=220)
        else:
            st.markdown('<div style="background:#1E1B16;border:1px solid #2E2A22;border-radius:12px;padding:40px;text-align:center;color:#8A8070;">Attempt MCQs to see trends</div>', unsafe_allow_html=True)

    with col_r:
        st.markdown("#### 🧠 Viva Confidence")
        if total_viva:
            conf_df = pd.DataFrame({"Confidence": ["🔴 Hard","🟡 Good","🟢 Easy"], "Count": [hard_n, good_n, easy_n]}).set_index("Confidence")
            st.bar_chart(conf_df, height=220)
        else:
            st.markdown('<div style="background:#1E1B16;border:1px solid #2E2A22;border-radius:12px;padding:40px;text-align:center;color:#8A8070;">Rate viva confidence to see this</div>', unsafe_allow_html=True)

    st.markdown("#### 🗒️ Recent MCQ Attempts")
    recent = c.execute("SELECT timestamp, topic, is_correct FROM mcq_attempts ORDER BY timestamp DESC LIMIT 15").fetchall()
    if recent:
        rdf = pd.DataFrame(recent, columns=["Time","Topic","Correct"])
        rdf["Result"] = rdf["Correct"].map({1:"✅ Correct", 0:"❌ Incorrect"})
        st.dataframe(rdf[["Time","Topic","Result"]], use_container_width=True, hide_index=True)
    else:
        st.markdown('<div style="background:#1E1B16;border:1px solid #2E2A22;border-radius:12px;padding:30px;text-align:center;color:#8A8070;">No attempts yet</div>', unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════════════════════
# VIVA TAB
# ═════════════════════════════════════════════════════════════════════════════
with tab_viva:
    st.markdown("### Viva Voce")

    if not pdf_ready:
        st.info("👈 Viva is available in 'Generate from notes' mode. Switch mode in the sidebar.")
    elif not st.session_state.get("viva_data"):
        st.markdown("Generate viva questions for this document when you're ready.")
        if st.button("⚡ Generate Viva Questions", type="primary", key="gen_viva"):
            with st.spinner("Generating viva questions…"):
                generate_section("viva", pdf_text, topic_name)
            st.rerun()
    else:
        viva_data = st.session_state["viva_data"]
        if "viva_revealed" not in st.session_state: st.session_state["viva_revealed"] = {}
        if "viva_confidence_logged" not in st.session_state: st.session_state["viva_confidence_logged"] = {}

        total_q  = len(viva_data)
        reviewed = len(st.session_state["viva_confidence_logged"])

        col_p, col_cnt = st.columns([3, 1])
        with col_p: st.progress(reviewed / total_q if total_q else 0)
        with col_cnt: st.caption(f"{reviewed} / {total_q} reviewed")

        if reviewed:
            hard_v = sum(1 for v in st.session_state["viva_confidence_logged"].values() if v == 1)
            good_v = sum(1 for v in st.session_state["viva_confidence_logged"].values() if v == 2)
            easy_v = sum(1 for v in st.session_state["viva_confidence_logged"].values() if v == 3)
            st.markdown(
                f'<span style="background:#2A1010;color:#EF5350;padding:4px 12px;border-radius:20px;font-size:0.8rem;font-weight:600;margin-right:6px;">🔴 Hard: {hard_v}</span>'
                f'<span style="background:#2A1E10;color:#C9A84C;padding:4px 12px;border-radius:20px;font-size:0.8rem;font-weight:600;margin-right:6px;">🟡 Good: {good_v}</span>'
                f'<span style="background:#1A3020;color:#4CAF50;padding:4px 12px;border-radius:20px;font-size:0.8rem;font-weight:600;">🟢 Easy: {easy_v}</span>',
                unsafe_allow_html=True
            )
            st.markdown("")

        for i, qa in enumerate(viva_data):
            logged = st.session_state["viva_confidence_logged"].get(i)
            badge = {1:" 🔴", 2:" 🟡", 3:" 🟢"}.get(logged, "")
            with st.expander(f"Q{i+1}: {qa['question']}{badge}"):
                st.text_area("Your answer:", key=f"viva_user_{i}", height=80,
                             placeholder="Type your answer before revealing…")
                if st.button("Reveal Model Answer", key=f"reveal_{i}"):
                    st.session_state["viva_revealed"][i] = True
                if st.session_state["viva_revealed"].get(i):
                    lines = qa["answer"].split("\\n")
                    bullets = "".join(f"<li style='margin:4px 0;'>{l.strip()}</li>" for l in lines if l.strip())
                    st.markdown(
                        f'<div style="background:#1E1A10;border-left:4px solid #C9A84C;'
                        f'border-radius:0 8px 8px 0;padding:14px 18px;margin:8px 0;color:#FAFAF8;">'
                        f'<ul style="margin:0;padding-left:18px;">{bullets}</ul></div>',
                        unsafe_allow_html=True
                    )
                    st.markdown("---")
                    if logged is None:
                        st.write("**Rate your confidence:**")
                        c1, c2, c3 = st.columns(3)
                        def _log(idx, level):
                            c.execute("INSERT INTO viva_reviews (topic,question_text,confidence) VALUES (?,?,?)",
                                      (topic_name, st.session_state["viva_data"][idx]["question"], level))
                            conn.commit()
                            st.session_state["viva_confidence_logged"][idx] = level
                        if c1.button("🔴 Hard", key=f"hard_{i}"): _log(i, 1); st.rerun()
                        if c2.button("🟡 Good", key=f"good_{i}"): _log(i, 2); st.rerun()
                        if c3.button("🟢 Easy", key=f"easy_{i}"): _log(i, 3); st.rerun()
                    else:
                        label = {1:"🔴 Hard", 2:"🟡 Good", 3:"🟢 Easy"}[logged]
                        st.info(f"Logged: **{label}**")

# ═════════════════════════════════════════════════════════════════════════════
# MCQ TAB
# ═════════════════════════════════════════════════════════════════════════════
with tab_mcq:
    if not pdf_ready and not import_ready:
        st.info("👈 Upload a PDF (or import a paper) in the sidebar to begin.")
    elif not st.session_state.get("mcqs"):
        if import_ready:
            st.markdown("### 📥 Import Existing Paper")
            st.markdown("Both files loaded. Convert this paper into your interactive Qbank.")
            if st.button("⚡ Import & Convert Paper", type="primary", key="imp_mcq"):
                with st.spinner("Extracting questions and matching answers…"):
                    combined = import_questions_text + "\n=====ANSWERS=====\n" + import_answers_text
                    import_paper(import_questions_text, import_answers_text,
                                 topic_name, doc_fingerprint(combined))
                st.rerun()
        else:
            st.markdown("### 📝 MCQ Session")
            st.markdown("Generate clinical MCQs for this document when you're ready.")
            if st.button("⚡ Generate MCQs", type="primary", key="gen_mcq"):
                with st.spinner("Generating clinical MCQs…"):
                    generate_section("mcq", pdf_text, topic_name)
                st.rerun()
    else:
        mcqs = st.session_state["mcqs"]
        mode = st.session_state.get("mcq_mode")

        # ── MODE SELECTION SCREEN ─────────────────────────────────────────────
        if mode is None:
            st.markdown("### 📝 MCQ Session")
            src_word = "imported from" if st.session_state.get("is_imported") else "generated from"
            st.markdown(f"**{len(mcqs)} questions** {src_word} *{topic_name}*")
            st.markdown("")

            st.markdown(
                '<p style="color:#8A8070;font-size:0.9rem;text-transform:uppercase;'
                'letter-spacing:0.08em;font-weight:600;">Select Mode</p>',
                unsafe_allow_html=True
            )

            col_exam, col_review = st.columns(2)
            with col_exam:
                st.markdown(
                    '<div class="mode-card">'
                    '<div style="font-size:2rem;margin-bottom:12px;">⏱️</div>'
                    '<div style="font-size:1.1rem;font-weight:700;color:#FAFAF8;margin-bottom:8px;">Exam Mode</div>'
                    '<div style="color:#8A8070;font-size:0.875rem;line-height:1.5;">'
                    'One question at a time · Live timer · Simulate exam conditions</div>'
                    '</div>', unsafe_allow_html=True
                )
                if st.button("Start Exam Mode →", key="start_exam", type="primary", use_container_width=True):
                    st.session_state["mcq_mode"] = "exam"
                    st.session_state["mcq_exam_idx"] = 0
                    st.session_state["mcq_submitted"] = {}
                    st.session_state["mcq_marked"] = set()
                    st.session_state["exam_start_time"] = time.time()
                    st.rerun()

            with col_review:
                st.markdown(
                    '<div class="mode-card">'
                    '<div style="font-size:2rem;margin-bottom:12px;">📖</div>'
                    '<div style="font-size:1.1rem;font-weight:700;color:#FAFAF8;margin-bottom:8px;">Review Mode</div>'
                    '<div style="color:#8A8070;font-size:0.875rem;line-height:1.5;">'
                    'All questions visible · No timer · Submit and review explanations</div>'
                    '</div>', unsafe_allow_html=True
                )
                if st.button("Start Review Mode →", key="start_review", use_container_width=True):
                    st.session_state["mcq_mode"] = "review"
                    st.session_state["mcq_submitted"] = {}
                    st.rerun()

        # ── EXAM MODE (with question navigator + mark-for-review) ─────────────
        elif mode == "exam":
            submitted = st.session_state.get("mcq_submitted", {})
            idx = st.session_state.get("mcq_exam_idx", 0)
            marked = st.session_state.setdefault("mcq_marked", set())
            total = len(mcqs)
            elapsed = time.time() - st.session_state.get("exam_start_time", time.time())

            nav_col, main_col = st.columns([1, 5])

            # ── Question navigator ──
            with nav_col:
                st.markdown(
                    '<p style="color:#8A8070;font-size:0.7rem;text-transform:uppercase;'
                    'letter-spacing:0.08em;font-weight:700;margin-bottom:8px;">Items</p>',
                    unsafe_allow_html=True
                )
                for i in range(total):
                    done = i in submitted
                    is_mark = i in marked
                    if i == idx:
                        label = f"▸ {i+1}"
                    elif done:
                        label = f"✓ {i+1}"
                    elif is_mark:
                        label = f"⚑ {i+1}"
                    else:
                        label = f"  {i+1}"
                    if st.button(label, key=f"exnav_{i}", use_container_width=True):
                        st.session_state["mcq_exam_idx"] = i
                        st.rerun()

            with main_col:
                # Top bar
                pct = ((idx + 1) / total) * 100
                attempted = len(submitted)
                correct_n = sum(1 for v in submitted.values() if v["correct"])

                st.markdown(
                    f'<div style="display:flex;justify-content:space-between;align-items:center;'
                    f'background:#1E1B16;border:1px solid #2E2A22;border-radius:12px;'
                    f'padding:14px 20px;margin-bottom:16px;">'
                    f'<span style="font-weight:700;color:#C9A84C;font-size:1rem;">Item {idx+1} / {total}</span>'
                    f'<div style="flex:1;margin:0 20px;background:#2E2A22;border-radius:4px;height:6px;">'
                    f'<div style="width:{pct:.0f}%;background:#C9A84C;height:6px;border-radius:4px;transition:width 0.3s;"></div></div>'
                    f'<span style="font-weight:700;color:#8A8070;font-family:monospace;font-size:1rem;">⏱ {fmt_time(elapsed)}</span>'
                    f'</div>',
                    unsafe_allow_html=True
                )

                if attempted:
                    acc = correct_n / attempted * 100
                    st.markdown(
                        f'<div style="display:flex;gap:16px;margin-bottom:12px;">'
                        f'<span style="background:#1A3020;color:#4CAF50;padding:4px 12px;border-radius:20px;font-size:0.8rem;font-weight:600;">✅ {correct_n} correct</span>'
                        f'<span style="background:#2A1010;color:#EF5350;padding:4px 12px;border-radius:20px;font-size:0.8rem;font-weight:600;">❌ {attempted-correct_n} incorrect</span>'
                        f'<span style="background:#252015;color:#C9A84C;padding:4px 12px;border-radius:20px;font-size:0.8rem;font-weight:600;">📊 {acc:.0f}% accuracy</span>'
                        f'</div>', unsafe_allow_html=True
                    )

                mcq = mcqs[idx]
                correct_letter = mcq["correct_answer_letter"].strip().upper()
                is_submitted = idx in submitted

                # Mark for review toggle
                mark_label = "⚑ Unmark" if idx in marked else "⚑ Mark for review"
                if st.button(mark_label, key=f"exam_mark_{idx}"):
                    if idx in marked:
                        marked.discard(idx)
                    else:
                        marked.add(idx)
                    st.rerun()

                # Question stem — selectable for highlighting
                st.markdown(
                    f'<div style="background:#1E1B16;border:1px solid #2E2A22;border-radius:12px;'
                    f'padding:24px 28px;margin:12px 0 20px 0;user-select:text;cursor:text;">'
                    f'<span style="font-size:0.75rem;font-weight:700;color:#C9A84C;'
                    f'text-transform:uppercase;letter-spacing:0.08em;">Question {idx+1}</span>'
                    f'<p style="margin:12px 0 0 0;font-size:1.02rem;line-height:1.75;color:#FAFAF8;">'
                    f'{mcq["question_text"]}</p></div>',
                    unsafe_allow_html=True
                )

                if not is_submitted:
                    choice = st.radio("Answer", mcq["options"], key=f"exam_r_{idx}", index=None, label_visibility="collapsed")

                    col_prev, col_sub, col_skip = st.columns([1, 2, 1])
                    with col_prev:
                        if idx > 0:
                            if st.button("← Previous", key="ep"):
                                st.session_state["mcq_exam_idx"] = idx - 1; st.rerun()
                    with col_sub:
                        if st.button("Submit Answer", key="es", type="primary", use_container_width=True):
                            if choice:
                                is_correct = choice.strip()[0].upper() == correct_letter
                                c.execute("INSERT INTO mcq_attempts (topic,question_text,selected_answer,correct_answer,is_correct) VALUES (?,?,?,?,?)",
                                          (topic_name, mcq["question_text"], choice, correct_letter, is_correct))
                                conn.commit()
                                st.session_state["mcq_submitted"][idx] = {"choice": choice, "correct": is_correct}
                                st.rerun()
                            else:
                                st.warning("Select an answer first.")
                    with col_skip:
                        if idx < total - 1:
                            if st.button("Skip →", key="ek"):
                                st.session_state["mcq_exam_idx"] = idx + 1; st.rerun()
                else:
                    sub = submitted[idx]
                    chosen_letter = sub["choice"].strip()[0].upper()

                    for opt in mcq["options"]:
                        opt_letter = opt.strip()[0].upper()
                        opt_text = opt[2:].strip() if len(opt) > 2 else opt
                        if opt_letter == correct_letter:
                            row_cls, badge_cls, icon = "opt-row opt-correct", "badge badge-correct", "✓"
                        elif opt_letter == chosen_letter and not sub["correct"]:
                            row_cls, badge_cls, icon = "opt-row opt-wrong", "badge badge-wrong", "✗"
                        else:
                            row_cls, badge_cls, icon = "opt-row opt-dim", "badge", opt_letter
                        st.markdown(
                            f'<div class="{row_cls}"><span class="{badge_cls}">{icon}</span>'
                            f'<span>{opt_text}</span></div>',
                            unsafe_allow_html=True
                        )

                    if sub["correct"]:
                        st.markdown(
                            '<div style="background:#1A3020;border:1.5px solid #4CAF50;border-radius:12px;'
                            'padding:12px 18px;margin:16px 0;color:#81C784;font-weight:600;">✓ Correct</div>',
                            unsafe_allow_html=True
                        )
                    else:
                        st.markdown(
                            f'<div style="background:#1E1A10;border:1.5px solid #C9A84C;border-radius:12px;'
                            f'padding:12px 18px;margin:16px 0;color:#C9A84C;font-weight:600;">'
                            f'Correct answer: {correct_letter}</div>',
                            unsafe_allow_html=True
                        )

                    with st.expander("📖 Full explanation"):
                        st.markdown(f"**Explanation:** {mcq.get('explanation','')}")
                        if mcq.get("key_learning_points"):
                            st.markdown(f"**🎯 Key learning point:** {mcq.get('key_learning_points','')}")

                    col_p2, col_n2 = st.columns(2)
                    with col_p2:
                        if idx > 0:
                            if st.button("← Previous", key="ep2", use_container_width=True):
                                st.session_state["mcq_exam_idx"] = idx - 1; st.rerun()
                    with col_n2:
                        if idx < total - 1:
                            if st.button("Next →", key="en2", type="primary", use_container_width=True):
                                st.session_state["mcq_exam_idx"] = idx + 1; st.rerun()
                        else:
                            if st.button("🏁 Finish Session", key="ef", type="primary", use_container_width=True):
                                st.session_state["mcq_mode"] = "results"; st.rerun()

                st.markdown("---")
                if st.button("← Back to Mode Select", key="back_exam"):
                    st.session_state["mcq_mode"] = None
                    st.session_state["mcq_marked"] = set()
                    st.rerun()

        # ── REVIEW MODE ───────────────────────────────────────────────────────
        elif mode == "review":
            submitted = st.session_state.get("mcq_submitted", {})
            total = len(mcqs)
            attempted = len(submitted)
            correct_n = sum(1 for v in submitted.values() if v["correct"])

            st.markdown("### 📖 Review Mode")
            if attempted:
                st.info(f"**{attempted}/{total}** answered · **{correct_n}** correct · **{correct_n/attempted*100:.0f}%** accuracy")

            for i, mcq in enumerate(mcqs):
                correct_letter = mcq["correct_answer_letter"].strip().upper()
                is_submitted = i in submitted

                status = ""
                if i in submitted:
                    status = " ✅" if submitted[i]["correct"] else " ❌"

                st.markdown(
                    f'<div style="background:#1E1B16;border:1px solid #2E2A22;border-radius:12px;'
                    f'padding:20px 24px;margin-bottom:8px;user-select:text;cursor:text;">'
                    f'<span style="font-size:0.75rem;font-weight:700;color:#C9A84C;'
                    f'text-transform:uppercase;letter-spacing:0.08em;">Question {i+1}{status}</span>'
                    f'<p style="margin:10px 0 0 0;font-size:1rem;line-height:1.7;color:#FAFAF8;">'
                    f'{mcq["question_text"]}</p></div>',
                    unsafe_allow_html=True
                )

                if not is_submitted:
                    choice = st.radio("Answer", mcq["options"], key=f"rev_r_{i}", index=None, label_visibility="collapsed")
                    if st.button("Submit", key=f"rev_s_{i}"):
                        if choice:
                            is_correct = choice.strip()[0].upper() == correct_letter
                            c.execute("INSERT INTO mcq_attempts (topic,question_text,selected_answer,correct_answer,is_correct) VALUES (?,?,?,?,?)",
                                      (topic_name, mcq["question_text"], choice, correct_letter, is_correct))
                            conn.commit()
                            st.session_state["mcq_submitted"][i] = {"choice": choice, "correct": is_correct}
                            st.rerun()
                        else:
                            st.warning("Select an answer.")
                else:
                    sub = submitted[i]
                    chosen_letter = sub["choice"].strip()[0].upper()
                    for opt in mcq["options"]:
                        ol = opt.strip()[0].upper()
                        ot = opt[2:].strip() if len(opt) > 2 else opt
                        if ol == correct_letter:
                            rc, bc, ic = "opt-row opt-correct", "badge badge-correct", "✓"
                        elif ol == chosen_letter and not sub["correct"]:
                            rc, bc, ic = "opt-row opt-wrong", "badge badge-wrong", "✗"
                        else:
                            rc, bc, ic = "opt-row opt-dim", "badge", ol
                        st.markdown(f'<div class="{rc}"><span class="{bc}">{ic}</span><span>{ot}</span></div>', unsafe_allow_html=True)

                    with st.expander("📖 Explanation"):
                        st.markdown(f"**Explanation:** {mcq.get('explanation','')}")
                        if mcq.get("key_learning_points"):
                            st.markdown(f"**🎯 Key learning point:** {mcq.get('key_learning_points','')}")

                st.markdown('<hr style="margin:20px 0;">', unsafe_allow_html=True)

            st.markdown("---")
            if st.button("← Back to Mode Select", key="back_review"):
                st.session_state["mcq_mode"] = None; st.rerun()

        # ── RESULTS SCREEN ────────────────────────────────────────────────────
        elif mode == "results":
            submitted = st.session_state.get("mcq_submitted", {})
            total = len(mcqs)
            attempted = len(submitted)
            correct_n = sum(1 for v in submitted.values() if v["correct"])
            elapsed = time.time() - st.session_state.get("exam_start_time", time.time())
            acc = correct_n / attempted * 100 if attempted else 0

            st.markdown("### 🏁 Session Complete")
            r1, r2, r3, r4 = st.columns(4)
            r1.metric("Questions Attempted", f"{attempted}/{total}")
            r2.metric("Correct", correct_n)
            r3.metric("Accuracy", f"{acc:.1f}%")
            r4.metric("Time Taken", fmt_time(elapsed))

            if acc >= 80:
                st.success("🎉 Excellent! Above 80% — you're well prepared on this topic.")
            elif acc >= 60:
                st.warning("📚 Good effort — review the questions you got wrong.")
            else:
                st.error("🔄 Below 60% — revisit the source material and try again.")

            if st.button("🔄 Try Again", type="primary"):
                st.session_state["mcq_mode"] = None; st.rerun()

# ═════════════════════════════════════════════════════════════════════════════
# ANKI TAB
# ═════════════════════════════════════════════════════════════════════════════
with tab_anki:
    st.markdown("### 🗂️ Anki Cloze-Deletion Flashcards")

    if not pdf_ready:
        st.info("👈 Anki is available in 'Generate from notes' mode. Switch mode in the sidebar.")
    elif not st.session_state.get("anki_result"):
        st.markdown("Generate Anki cloze cards for this document when you're ready.")
        if st.button("⚡ Generate Anki Cards", type="primary", key="gen_anki"):
            with st.spinner("Generating Anki cards…"):
                generate_section("anki", pdf_text, topic_name)
            st.rerun()
    else:
        raw_anki = st.session_state["anki_result"]
        card_lines = [l for l in raw_anki.splitlines() if "|" in l]

        col_a1, col_a2 = st.columns([3, 1])
        with col_a1:
            st.markdown(
                f'<div style="background:#1E1B16;border:1px solid #2E2A22;border-radius:12px;padding:16px 24px;">'
                f'<span style="font-size:2rem;font-weight:800;color:#C9A84C;">{len(card_lines)}</span>'
                f'<span style="color:#8A8070;font-size:0.85rem;margin-left:8px;">cards generated</span>'
                f'</div>', unsafe_allow_html=True
            )
        with col_a2:
            st.download_button("⬇️ Download .txt", data=raw_anki, file_name="anki_cards.txt",
                               mime="text/plain", use_container_width=True)

        st.code(raw_anki, language=None)
        st.markdown(
            '<div style="background:#1E1B16;border:1px solid #2E2A22;border-radius:12px;padding:16px 24px;font-size:0.85rem;color:#8A8070;">'
            '📥 <strong style="color:#C9A84C;">How to import:</strong> Anki → File → Import → select .txt → '
            'separator <code>|</code> → note type <strong>Cloze</strong> → Import'
            '</div>', unsafe_allow_html=True
        )


# ═════════════════════════════════════════════════════════════════════════════
# MOCK EXAM TAB — build a custom exam from your saved topic pool (no API calls)
# ═════════════════════════════════════════════════════════════════════════════
with tab_mock:
    st.markdown("### 🎯 Mock Exam Builder")
    st.caption("Assemble a custom exam from topics you've already generated. No API calls — instant and free.")

    topics = list_topics_with_mcqs()

    # If a mock is currently running, render it; otherwise show the builder.
    mock_state = st.session_state.get("mock_running", False)

    if not mock_state:
        if not topics:
            st.info("You haven't generated any MCQs yet. Generate questions from a document first, then come back to build a mock exam.")
        else:
            total_available = sum(n for _, _, n in topics)
            st.markdown(
                f'<p style="color:#8A8070;font-size:0.9rem;text-transform:uppercase;'
                f'letter-spacing:0.08em;font-weight:600;">Choose Topics '
                f'({len(topics)} available · {total_available} questions total)</p>',
                unsafe_allow_html=True
            )

            # Topic selection checkboxes
            selected_hashes = []
            for topic, doc_hash, n in topics:
                short = topic if len(topic) <= 45 else topic[:42] + "…"
                if st.checkbox(f"{short}  ·  {n} Q", key=f"mock_pick_{doc_hash}"):
                    selected_hashes.append(doc_hash)

            st.markdown("---")

            # Pool size from selection
            pool = []
            for h in selected_hashes:
                pool.extend(get_mcqs_for_hash(h))
            pool_size = len(pool)

            col_n, col_mode = st.columns(2)
            with col_n:
                if pool_size > 0:
                    num_q = st.slider("Number of questions", min_value=1,
                                      max_value=pool_size, value=min(20, pool_size))
                else:
                    st.caption("Select at least one topic to continue.")
                    num_q = 0
            with col_mode:
                exam_style = st.radio("Mode", ["⏱️ Timed exam", "📖 Untimed review"],
                                      label_visibility="visible")

            st.markdown("")
            if pool_size > 0 and st.button("🎯 Start Mock Exam", type="primary", use_container_width=True):
                import random
                chosen = random.sample(pool, num_q)
                st.session_state["mock_questions"] = chosen
                st.session_state["mock_submitted"] = {}
                st.session_state["mock_idx"] = 0
                st.session_state["mock_marked"] = set()
                st.session_state["mock_running"] = True
                st.session_state["mock_timed"] = exam_style.startswith("⏱️")
                st.session_state["mock_start"] = time.time()
                st.rerun()

    else:
        # ── RUNNING MOCK EXAM ──────────────────────────────────────────────────
        mqs = st.session_state["mock_questions"]
        submitted = st.session_state["mock_submitted"]
        idx = st.session_state["mock_idx"]
        marked = st.session_state["mock_marked"]
        total = len(mqs)
        timed = st.session_state.get("mock_timed", True)
        elapsed = time.time() - st.session_state.get("mock_start", time.time())

        # ── Question navigator sidebar (UWorld-style) + main panel ──
        nav_col, main_col = st.columns([1, 5])

        with nav_col:
            st.markdown(
                '<p style="color:#8A8070;font-size:0.7rem;text-transform:uppercase;'
                'letter-spacing:0.08em;font-weight:700;margin-bottom:8px;">Items</p>',
                unsafe_allow_html=True
            )
            for i in range(total):
                # Status dot: answered=gold, marked=red ring, current=bracketed
                done = i in submitted
                is_mark = i in marked
                if i == idx:
                    label = f"▸ {i+1}"
                elif done:
                    label = f"✓ {i+1}"
                elif is_mark:
                    label = f"⚑ {i+1}"
                else:
                    label = f"  {i+1}"
                if st.button(label, key=f"nav_{i}", use_container_width=True):
                    st.session_state["mock_idx"] = i
                    st.rerun()

        with main_col:
            # Top bar: progress + timer
            attempted = len(submitted)
            correct_n = sum(1 for v in submitted.values() if v["correct"])
            pct = ((idx + 1) / total) * 100
            timer_html = (f'<span style="font-weight:700;color:#8A8070;font-family:monospace;font-size:1rem;">⏱ {fmt_time(elapsed)}</span>'
                          if timed else '<span style="color:#8A8070;font-size:0.85rem;">Untimed</span>')
            st.markdown(
                f'<div style="display:flex;justify-content:space-between;align-items:center;'
                f'background:#1E1B16;border:1px solid #2E2A22;border-radius:12px;'
                f'padding:14px 20px;margin-bottom:16px;">'
                f'<span style="font-weight:700;color:#C9A84C;font-size:1rem;">Item {idx+1} / {total}</span>'
                f'<div style="flex:1;margin:0 20px;background:#2E2A22;border-radius:4px;height:6px;">'
                f'<div style="width:{pct:.0f}%;background:#C9A84C;height:6px;border-radius:4px;"></div></div>'
                f'{timer_html}</div>',
                unsafe_allow_html=True
            )

            mcq = mqs[idx]
            correct_letter = mcq["correct_answer_letter"].strip().upper()
            is_sub = idx in submitted

            # Mark-for-review toggle
            mark_label = "⚑ Unmark" if idx in marked else "⚑ Mark for review"
            if st.button(mark_label, key=f"mock_mark_{idx}"):
                if idx in marked:
                    marked.discard(idx)
                else:
                    marked.add(idx)
                st.rerun()

            # Question stem (highlightable)
            st.markdown(
                f'<div style="background:#1E1B16;border:1px solid #2E2A22;border-radius:12px;'
                f'padding:24px 28px;margin:12px 0 20px 0;user-select:text;cursor:text;">'
                f'<p style="margin:0;font-size:1.02rem;line-height:1.75;color:#FAFAF8;">'
                f'{mcq["question_text"]}</p></div>',
                unsafe_allow_html=True
            )

            if not is_sub:
                choice = st.radio("Answer", mcq["options"], key=f"mock_r_{idx}",
                                  index=None, label_visibility="collapsed")
                if st.button("Submit Answer", key=f"mock_sub_{idx}", type="primary"):
                    if choice:
                        ok = choice.strip()[0].upper() == correct_letter
                        c.execute("INSERT INTO mcq_attempts (topic,question_text,selected_answer,correct_answer,is_correct) VALUES (?,?,?,?,?)",
                                  ("Mock Exam", mcq["question_text"], choice, correct_letter, ok))
                        conn.commit()
                        st.session_state["mock_submitted"][idx] = {"choice": choice, "correct": ok}
                        st.rerun()
                    else:
                        st.warning("Select an answer first.")
            else:
                sub = submitted[idx]
                chosen_letter = sub["choice"].strip()[0].upper()
                for opt in mcq["options"]:
                    ol = opt.strip()[0].upper()
                    ot = opt[2:].strip() if len(opt) > 2 else opt
                    if ol == correct_letter:
                        rc, bc, ic = "opt-row opt-correct", "badge badge-correct", "✓"
                    elif ol == chosen_letter and not sub["correct"]:
                        rc, bc, ic = "opt-row opt-wrong", "badge badge-wrong", "✗"
                    else:
                        rc, bc, ic = "opt-row opt-dim", "badge", ol
                    st.markdown(f'<div class="{rc}"><span class="{bc}">{ic}</span><span>{ot}</span></div>',
                                unsafe_allow_html=True)

                with st.expander("📖 Explanation"):
                    st.markdown(f"**Explanation:** {mcq.get('explanation','')}")
                    if mcq.get("key_learning_points"):
                        st.markdown(f"**🎯 Key learning point:** {mcq.get('key_learning_points','')}")

            # Navigation
            st.markdown("")
            cprev, cnext, cfin = st.columns(3)
            with cprev:
                if idx > 0 and st.button("← Previous", key="mock_prev", use_container_width=True):
                    st.session_state["mock_idx"] = idx - 1; st.rerun()
            with cnext:
                if idx < total - 1 and st.button("Next →", key="mock_next", use_container_width=True):
                    st.session_state["mock_idx"] = idx + 1; st.rerun()
            with cfin:
                if st.button("🏁 Finish", key="mock_fin", type="primary", use_container_width=True):
                    st.session_state["mock_finished"] = True
                    st.session_state["mock_running"] = False
                    st.rerun()

    # ── Results screen ──
    if st.session_state.get("mock_finished"):
        mqs = st.session_state.get("mock_questions", [])
        submitted = st.session_state.get("mock_submitted", {})
        total = len(mqs)
        attempted = len(submitted)
        correct_n = sum(1 for v in submitted.values() if v["correct"])
        elapsed = time.time() - st.session_state.get("mock_start", time.time())
        acc = correct_n / attempted * 100 if attempted else 0

        st.markdown("---")
        st.markdown("### 🏁 Mock Exam Complete")
        r1, r2, r3, r4 = st.columns(4)
        r1.metric("Attempted", f"{attempted}/{total}")
        r2.metric("Correct", correct_n)
        r3.metric("Accuracy", f"{acc:.1f}%")
        r4.metric("Time", fmt_time(elapsed))

        if acc >= 80:
            st.success("🎉 Excellent — above 80%.")
        elif acc >= 60:
            st.warning("📚 Solid — review what you missed.")
        else:
            st.error("🔄 Below 60% — worth another pass.")

        if st.button("🎯 Build Another Mock", type="primary"):
            for k in ["mock_finished", "mock_questions", "mock_submitted",
                      "mock_idx", "mock_marked", "mock_running", "mock_start"]:
                st.session_state.pop(k, None)
            st.rerun()
