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
try:
    from builtin_questions import BUILTIN_BANKS
except Exception:
    BUILTIN_BANKS = {}
try:
    from builtin_questions import BUILTIN_VIVA
except Exception:
    BUILTIN_VIVA = {}
try:
    from procedures import BUILTIN_PROCEDURES
except Exception:
    BUILTIN_PROCEDURES = {}

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
# Add a `user` column to separate Terry's and Alex's data (idempotent).
for _tbl in ("mcq_attempts", "viva_reviews"):
    try:
        c.execute(f"ALTER TABLE {_tbl} ADD COLUMN user TEXT DEFAULT 'Terry'")
    except Exception:
        pass  # column already exists
# Permanent cache of generated content, keyed by a hash of the PDF text.
# Once a document is generated, it is saved here forever — re-opening it loads
# from storage with ZERO API calls.
c.execute("""CREATE TABLE IF NOT EXISTS generated_content (
    doc_hash TEXT PRIMARY KEY, topic TEXT,
    viva_json TEXT, mcq_json TEXT, anki_text TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)""")
# Per-question feedback: a thumbs rating and a free-text note, keyed by a hash
# of the question text so it follows the question regardless of which bank/mode.
c.execute("""CREATE TABLE IF NOT EXISTS mcq_feedback (
    q_hash TEXT PRIMARY KEY, question_text TEXT,
    rating TEXT, note TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)""")
try:
    c.execute("ALTER TABLE mcq_feedback ADD COLUMN user TEXT DEFAULT 'Terry'")
except Exception:
    pass
c.execute("""CREATE TABLE IF NOT EXISTS library_notes (
    id INTEGER PRIMARY KEY, title TEXT, category TEXT, subtopic TEXT,
    content TEXT, uploaded_by TEXT DEFAULT 'Terry',
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)""")
c.execute("""CREATE TABLE IF NOT EXISTS procedures (
    id INTEGER PRIMARY KEY, name TEXT, steps_json TEXT,
    added_by TEXT DEFAULT 'Terry',
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)""")
conn.commit()

# ── Supabase (permanent cloud storage for the generated-content cache) ─────────
# If Supabase is configured and reachable, the cache lives there permanently and
# survives app restarts. If anything is missing or fails, we silently fall back
# to the local SQLite cache above, so the app ALWAYS works.
SUPABASE_ENABLED = False
supabase = None
try:
    _sb_url = st.secrets.get("SUPABASE_URL", "")
    _sb_key = st.secrets.get("SUPABASE_KEY", "")
    if _sb_url and _sb_key:
        from supabase import create_client
        supabase = create_client(_sb_url, _sb_key)
        # Probe once so a misconfiguration falls back instead of erroring later
        supabase.table("generated_content").select("doc_hash").limit(1).execute()
        SUPABASE_ENABLED = True
except Exception:
    SUPABASE_ENABLED = False
    supabase = None


def doc_fingerprint(pdf_text):
    """A stable hash of the document text — identifies a document uniquely."""
    return hashlib.sha256(pdf_text.encode("utf-8")).hexdigest()


def load_from_cache(doc_hash):
    """Return saved generation for this document, or None if not generated yet."""
    if SUPABASE_ENABLED:
        try:
            res = supabase.table("generated_content").select(
                "viva_json, mcq_json, anki_text"
            ).eq("doc_hash", doc_hash).limit(1).execute()
            if res.data:
                row = res.data[0]
                return {
                    "viva": json.loads(row["viva_json"]) if row.get("viva_json") else [],
                    "mcqs": json.loads(row["mcq_json"]) if row.get("mcq_json") else [],
                    "anki": row.get("anki_text") or "",
                }
            return None
        except Exception:
            pass  # fall through to SQLite
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
    if SUPABASE_ENABLED:
        try:
            supabase.table("generated_content").upsert({
                "doc_hash": doc_hash,
                "topic": topic,
                "viva_json": json.dumps(viva),
                "mcq_json": json.dumps(mcqs),
                "anki_text": anki,
            }).execute()
            return
        except Exception:
            pass  # fall through to SQLite
    c.execute(
        "INSERT OR REPLACE INTO generated_content "
        "(doc_hash, topic, viva_json, mcq_json, anki_text) VALUES (?,?,?,?,?)",
        (doc_hash, topic, json.dumps(viva), json.dumps(mcqs), anki)
    )
    conn.commit()


def seed_builtin_banks():
    """Load any baked-in banks into the cache so they appear everywhere automatically."""
    for name, questions in BUILTIN_BANKS.items():
        if not questions:
            continue
        # Stable hash from the bank NAME so re-runs don't create duplicates
        h = hashlib.sha256(("BUILTIN::" + name).encode("utf-8")).hexdigest()
        new_json = json.dumps(questions)
        if SUPABASE_ENABLED:
            try:
                res = supabase.table("generated_content").select(
                    "mcq_json").eq("doc_hash", h).limit(1).execute()
                existing = res.data[0]["mcq_json"] if res.data else None
                if existing != new_json:
                    supabase.table("generated_content").upsert({
                        "doc_hash": h, "topic": name,
                        "viva_json": json.dumps([]), "mcq_json": new_json, "anki_text": "",
                    }).execute()
                continue
            except Exception:
                pass  # fall through to SQLite for this bank
        existing = c.execute(
            "SELECT mcq_json FROM generated_content WHERE doc_hash=?", (h,)
        ).fetchone()
        if not existing or existing[0] != new_json:
            c.execute(
                "INSERT OR REPLACE INTO generated_content "
                "(doc_hash, topic, viva_json, mcq_json, anki_text) VALUES (?,?,?,?,?)",
                (h, name, json.dumps([]), new_json, "")
            )
    conn.commit()

seed_builtin_banks()


def list_builtin_viva():
    """Return {bank_name: [qa, …]} for baked-in viva banks that have content."""
    return {name: qs for name, qs in BUILTIN_VIVA.items() if qs}


def split_category(name):
    """Free-form hierarchy via a 'Category :: Subtopic' convention in the name.
    Returns (category, display_name). No separator -> 'Uncategorised'.
    If three+ parts, first is category and the rest joins as the display."""
    if name and " :: " in name:
        parts = [p.strip() for p in name.split(" :: ")]
        cat = parts[0] or "Uncategorised"
        disp = " :: ".join(parts[1:]) or name
        return cat, disp
    return "Uncategorised", name


def list_topics_with_viva():
    """Return [(topic, doc_hash, viva_count), …] for every saved doc that has viva."""
    rows = []
    if SUPABASE_ENABLED:
        try:
            res = supabase.table("generated_content").select(
                "topic, doc_hash, viva_json").execute()
            rows = [(r.get("topic"), r.get("doc_hash"), r.get("viva_json")) for r in res.data]
        except Exception:
            rows = []
    if not rows:
        rows = c.execute("SELECT topic, doc_hash, viva_json FROM generated_content").fetchall()
    out = []
    for topic, doc_hash, viva_json in rows:
        try:
            n = len(json.loads(viva_json)) if viva_json else 0
        except Exception:
            n = 0
        if n > 0:
            out.append((topic, doc_hash, n))
    return sorted(out, key=lambda x: x[0].lower())


def get_viva_for_hash(doc_hash):
    if SUPABASE_ENABLED:
        try:
            res = supabase.table("generated_content").select(
                "viva_json").eq("doc_hash", doc_hash).limit(1).execute()
            if res.data and res.data[0].get("viva_json"):
                return json.loads(res.data[0]["viva_json"])
            return []
        except Exception:
            pass
    row = c.execute("SELECT viva_json FROM generated_content WHERE doc_hash=?", (doc_hash,)).fetchone()
    if not row or not row[0]:
        return []
    try:
        return json.loads(row[0])
    except Exception:
        return []


def log_mcq_attempt(topic, question_text, selected, correct, is_correct, user):
    """Write an MCQ attempt to Supabase (if on) AND local SQLite."""
    if SUPABASE_ENABLED:
        try:
            supabase.table("mcq_attempts").insert({
                "topic": topic, "question_text": question_text,
                "selected_answer": selected, "correct_answer": correct,
                "is_correct": bool(is_correct), "user": user,
            }).execute()
        except Exception:
            pass
    try:
        c.execute("INSERT INTO mcq_attempts (topic,question_text,selected_answer,correct_answer,is_correct,user) VALUES (?,?,?,?,?,?)",
                  (topic, question_text, selected, correct, is_correct, user))
        conn.commit()
    except Exception:
        pass


def log_viva_review(topic, question_text, confidence, user):
    """Write a viva confidence rating to Supabase (if on) AND local SQLite."""
    if SUPABASE_ENABLED:
        try:
            supabase.table("viva_reviews").insert({
                "topic": topic, "question_text": question_text,
                "confidence": confidence, "user": user,
            }).execute()
        except Exception:
            pass
    try:
        c.execute("INSERT INTO viva_reviews (topic,question_text,confidence,user) VALUES (?,?,?,?)",
                  (topic, question_text, confidence, user))
        conn.commit()
    except Exception:
        pass


def fetch_attempts(user):
    """Return list of attempt dicts for a user: {topic, is_correct, timestamp}.
    Prefers Supabase, falls back to SQLite."""
    if SUPABASE_ENABLED:
        try:
            res = supabase.table("mcq_attempts").select(
                "topic, is_correct, created_at").eq("user", user).execute()
            return [{"topic": r.get("topic"), "is_correct": r.get("is_correct"),
                     "ts": r.get("created_at")} for r in res.data]
        except Exception:
            pass
    rows = c.execute("SELECT topic, is_correct, timestamp FROM mcq_attempts WHERE user=?", (user,)).fetchall()
    return [{"topic": t, "is_correct": ic, "ts": ts} for t, ic, ts in rows]


def fetch_viva(user):
    """Return list of viva review dicts: {topic, confidence, timestamp}."""
    if SUPABASE_ENABLED:
        try:
            res = supabase.table("viva_reviews").select(
                "topic, confidence, created_at").eq("user", user).execute()
            return [{"topic": r.get("topic"), "confidence": r.get("confidence"),
                     "ts": r.get("created_at")} for r in res.data]
        except Exception:
            pass
    rows = c.execute("SELECT topic, confidence, timestamp FROM viva_reviews WHERE user=?", (user,)).fetchall()
    return [{"topic": t, "confidence": cf, "ts": ts} for t, cf, ts in rows]


def clean_text(s):
    """Remove null bytes and other control characters Postgres rejects.
    Postgres cannot store \\u0000; PDF extraction sometimes emits these."""
    if not s:
        return s
    s = s.replace("\x00", "")
    return "".join(ch for ch in s if ch in ("\n", "\t", "\r") or ord(ch) >= 32)


def format_note_text(text):
    """Render notes readably while PRESERVING the author's line structure.
    Only ALL-CAPS lines become headings; everything else is shown verbatim
    (with its own line breaks kept). We do NOT invent bullets — that destroyed
    the structure of pasted/typed notes. Markdown shows line breaks via two
    trailing spaces."""
    if not text:
        return ""
    out = []
    for raw_line in text.split("\n"):
        line = raw_line.rstrip()
        stripped = line.strip()
        if not stripped:
            out.append("")  # blank line -> paragraph break
            continue
        # ALL-CAPS short lines -> headings (helps both pasted and extracted notes)
        letters = [ch for ch in stripped if ch.isalpha()]
        is_caps = letters and all(ch.isupper() for ch in letters) and len(stripped) <= 60
        if is_caps:
            out.append(f"\n#### {stripped}\n")
            continue
        # Keep the line exactly as written; two trailing spaces = hard line break in Markdown
        out.append(line + "  ")
    md = "\n".join(out)
    md = re.sub(r"\n{3,}", "\n\n", md)
    return md


def save_library_note(title, category, subtopic, content, uploaded_by):
    """Save a text note to the shared library (Supabase, with SQLite fallback)."""
    content = clean_text(content)
    title = clean_text(title)
    category = clean_text(category)
    subtopic = clean_text(subtopic)
    if SUPABASE_ENABLED:
        try:
            supabase.table("library_notes").insert({
                "title": title, "category": category, "subtopic": subtopic,
                "content": content, "uploaded_by": uploaded_by,
            }).execute()
            return True
        except Exception as e:
            # Surface the real reason instead of failing silently
            st.error(f"Supabase save failed: {e}")
            try:
                c.execute("INSERT INTO library_notes (title,category,subtopic,content,uploaded_by) VALUES (?,?,?,?,?)",
                          (title, category, subtopic, content, uploaded_by))
                conn.commit()
                st.warning("Saved to local storage only (will not persist across restarts).")
                return True
            except Exception as e2:
                st.error(f"Local save also failed: {e2}")
                return False
    try:
        c.execute("INSERT INTO library_notes (title,category,subtopic,content,uploaded_by) VALUES (?,?,?,?,?)",
                  (title, category, subtopic, content, uploaded_by))
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Save failed: {e}")
        return False


def list_library_notes():
    """Return list of note dicts: {id, title, category, subtopic, content, uploaded_by}."""
    if SUPABASE_ENABLED:
        try:
            res = supabase.table("library_notes").select(
                "id, title, category, subtopic, content, uploaded_by").order(
                "created_at", desc=True).execute()
            return res.data
        except Exception:
            pass
    rows = c.execute("SELECT id, title, category, subtopic, content, uploaded_by FROM library_notes ORDER BY id DESC").fetchall()
    return [{"id": r[0], "title": r[1], "category": r[2], "subtopic": r[3],
             "content": r[4], "uploaded_by": r[5]} for r in rows]


def delete_library_note(note_id):
    if SUPABASE_ENABLED:
        try:
            supabase.table("library_notes").delete().eq("id", note_id).execute()
            return
        except Exception:
            pass
    try:
        c.execute("DELETE FROM library_notes WHERE id=?", (note_id,))
        conn.commit()
    except Exception:
        pass


def list_user_procedures():
    """Return list of {id, name, steps(list), added_by} for user-added procedures."""
    rows = []
    if SUPABASE_ENABLED:
        try:
            res = supabase.table("procedures").select(
                "id, name, steps_json, added_by").order("name").execute()
            rows = res.data
        except Exception:
            rows = []
    if not rows:
        raw = c.execute("SELECT id, name, steps_json, added_by FROM procedures ORDER BY name").fetchall()
        rows = [{"id": r[0], "name": r[1], "steps_json": r[2], "added_by": r[3]} for r in raw]
    out = []
    for r in rows:
        try:
            steps = json.loads(r.get("steps_json") or "[]")
        except Exception:
            steps = []
        out.append({"id": r.get("id"), "name": r.get("name"),
                    "steps": steps, "added_by": r.get("added_by")})
    return out


def save_user_procedure(name, steps, added_by):
    name = clean_text(name)
    steps = [clean_text(s) for s in steps if s.strip()]
    payload_steps = json.dumps(steps)
    if SUPABASE_ENABLED:
        try:
            supabase.table("procedures").insert({
                "name": name, "steps_json": payload_steps, "added_by": added_by,
            }).execute()
            return True
        except Exception as e:
            st.error(f"Save failed: {e}")
            return False
    try:
        c.execute("INSERT INTO procedures (name, steps_json, added_by) VALUES (?,?,?)",
                  (name, payload_steps, added_by))
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Save failed: {e}")
        return False


def delete_user_procedure(proc_id):
    if SUPABASE_ENABLED:
        try:
            supabase.table("procedures").delete().eq("id", proc_id).execute()
            return
        except Exception:
            pass
    try:
        c.execute("DELETE FROM procedures WHERE id=?", (proc_id,))
        conn.commit()
    except Exception:
        pass


def all_procedures():
    """Merge built-in procedures with user-added ones into a single dict-like list:
    [(name, steps, source, ref)]. source 'builtin' or 'user'."""
    items = []
    for name, steps in BUILTIN_PROCEDURES.items():
        items.append((name, steps, "builtin", name))
    for p in list_user_procedures():
        items.append((p["name"], p["steps"], "user", p["id"]))
    return items


def update_library_note(note_id, title, category, subtopic, content):
    """Update an existing note's fields. Cleans text for Postgres safety."""
    title = clean_text(title); category = clean_text(category)
    subtopic = clean_text(subtopic); content = clean_text(content)
    if SUPABASE_ENABLED:
        try:
            supabase.table("library_notes").update({
                "title": title, "category": category,
                "subtopic": subtopic, "content": content,
            }).eq("id", note_id).execute()
            return True
        except Exception as e:
            st.error(f"Update failed: {e}")
            return False
    try:
        c.execute("UPDATE library_notes SET title=?, category=?, subtopic=?, content=? WHERE id=?",
                  (title, category, subtopic, content, note_id))
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Update failed: {e}")
        return False


def list_topics_with_mcqs():
    """Return [(topic, doc_hash, mcq_count), …] for every saved doc that has MCQs."""
    rows = []
    if SUPABASE_ENABLED:
        try:
            res = supabase.table("generated_content").select(
                "topic, doc_hash, mcq_json").execute()
            rows = [(r.get("topic"), r.get("doc_hash"), r.get("mcq_json")) for r in res.data]
        except Exception:
            rows = []
    if not rows:
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


def q_hash(question_text):
    # Per-user hash so Terry and Alex keep separate feedback on the same question.
    user = st.session_state.get("current_user", "Terry")
    return hashlib.sha256((user + "::" + question_text).encode("utf-8")).hexdigest()


def load_feedback(question_text):
    """Return {'rating': ..., 'note': ...} for a question, or defaults."""
    h = q_hash(question_text)
    if SUPABASE_ENABLED:
        try:
            res = supabase.table("mcq_feedback").select(
                "rating, note").eq("q_hash", h).limit(1).execute()
            if res.data:
                return {"rating": res.data[0].get("rating") or "",
                        "note": res.data[0].get("note") or ""}
            return {"rating": "", "note": ""}
        except Exception:
            pass
    row = c.execute("SELECT rating, note FROM mcq_feedback WHERE q_hash=?", (h,)).fetchone()
    if row:
        return {"rating": row[0] or "", "note": row[1] or ""}
    return {"rating": "", "note": ""}


def save_feedback(question_text, rating, note):
    h = q_hash(question_text)
    user = st.session_state.get("current_user", "Terry")
    if SUPABASE_ENABLED:
        try:
            supabase.table("mcq_feedback").upsert({
                "q_hash": h, "question_text": question_text,
                "rating": rating, "note": note, "user": user,
            }).execute()
            return
        except Exception:
            pass
    try:
        c.execute("ALTER TABLE mcq_feedback ADD COLUMN user TEXT DEFAULT 'Terry'")
    except Exception:
        pass
    c.execute("INSERT OR REPLACE INTO mcq_feedback (q_hash, question_text, rating, note, user) VALUES (?,?,?,?,?)",
              (h, question_text, rating, note, user))
    conn.commit()


def render_feedback(mcq, key_prefix):
    """A 👍/👎 + notes panel for a question. Saves permanently."""
    qtext = mcq.get("question_text", "")
    fb = load_feedback(qtext)
    st.markdown("**Your feedback**")
    col_up, col_down, col_status = st.columns([1, 1, 4])
    with col_up:
        if st.button("👍", key=f"{key_prefix}_up"):
            save_feedback(qtext, "up", fb["note"])
            st.rerun()
    with col_down:
        if st.button("👎", key=f"{key_prefix}_down"):
            save_feedback(qtext, "down", fb["note"])
            st.rerun()
    with col_status:
        if fb["rating"] == "up":
            st.caption("Rated 👍")
        elif fb["rating"] == "down":
            st.caption("Rated 👎 — flagged to improve")
    note = st.text_area("Notes", value=fb["note"], key=f"{key_prefix}_note",
                        placeholder="Add a note to improve this question later…",
                        label_visibility="collapsed")
    if st.button("💾 Save note", key=f"{key_prefix}_savenote"):
        save_feedback(qtext, fb["rating"], note)
        st.success("Saved")


def get_mcqs_for_hash(doc_hash):
    if SUPABASE_ENABLED:
        try:
            res = supabase.table("generated_content").select(
                "mcq_json").eq("doc_hash", doc_hash).limit(1).execute()
            if res.data and res.data[0].get("mcq_json"):
                return json.loads(res.data[0]["mcq_json"])
            return []
        except Exception:
            pass
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
    raw = "\n\n".join(p.extract_text() for p in reader.pages if p.extract_text())
    return clean_text(raw)

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

def calculate_streak(user=None):
    if user:
        rows = c.execute("""SELECT DISTINCT date(timestamp) as d FROM (
            SELECT timestamp FROM mcq_attempts WHERE user=? UNION ALL
            SELECT timestamp FROM viva_reviews WHERE user=?
        ) ORDER BY d DESC""", (user, user)).fetchall()
    else:
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

def build_heatmap_html(days=182, user=None):
    today = date.today()
    activity = {}
    # Use the permanent (Supabase-first) data so history survives restarts
    try:
        all_events = []
        if user:
            all_events += [a.get("ts") for a in fetch_attempts(user) if a.get("ts")]
            all_events += [v.get("ts") for v in fetch_viva(user) if v.get("ts")]
        for ts in all_events:
            d_str = str(ts)[:10]  # YYYY-MM-DD
            activity[d_str] = activity.get(d_str, 0) + 1
    except Exception:
        activity = {}

    # Green gradient: more activity -> darker, richer green
    def cell_colour(cnt):
        if cnt <= 0:   return "#2E2A22"   # empty
        if cnt <= 2:   return "#9BE08B"   # light green (1-2)
        if cnt <= 5:   return "#5FC96F"   # medium (3-5)
        if cnt <= 9:   return "#2F9E41"   # dark (6-9)
        return "#176127"                  # darkest (10+)

    cells = []
    for i in range(days - 1, -1, -1):
        d = today - timedelta(days=i)
        cnt = activity.get(d.isoformat(), 0)
        color = cell_colour(cnt)
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
            st.session_state["viva_bank_name"] = None
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

def render_image(mcq):
    """Show an image above a question if it has a non-empty image_url."""
    url = (mcq.get("image_url") or "").strip()
    if url:
        try:
            st.image(url, use_container_width=True)
        except Exception:
            st.caption("(image could not be loaded)")

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🧠 The Differential")
    if SUPABASE_ENABLED:
        st.caption("🟢 Permanent storage active")
    else:
        st.caption("🟡 Local storage (temporary)")

    # ── Who's studying? Separates progress between users (banks stay shared) ──
    current_user = st.selectbox("👤 Studying as", ["Terry", "Alex"],
                                key="current_user")
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
        # Optional organisation: category + subtopic, used to file the content.
        gen_category = st.text_input("Category", placeholder="e.g. ICU Week 8", key="gen_category")
        gen_subtopic = st.text_input("Subtopic", placeholder="e.g. ARDS", key="gen_subtopic")
        if uploaded_file:
            with st.spinner("Reading PDF…"):
                pdf_text = extract_text_from_pdf(uploaded_file)
            # Build a hierarchical topic name when category/subtopic are given,
            # otherwise fall back to the filename.
            cat = gen_category.strip()
            sub = gen_subtopic.strip() or uploaded_file.name
            topic_name = f"{cat} :: {sub}" if cat else sub
            if pdf_text.strip():
                st.success(f"✅ {uploaded_file.name}")
                st.caption(f"{len(pdf_text):,} characters")
                if cat:
                    st.caption(f"Filed under: {cat} › {sub}")
                with st.expander("Preview"):
                    st.text(pdf_text[:1200] + ("…" if len(pdf_text) > 1200 else ""))
            else:
                st.warning("⚠️ No text found — scanned PDF? Try OCR first.")
    else:
        st.markdown("**📥 Import Existing Paper**")
        st.caption("Upload the questions, then the answer key.")
        imp_category = st.text_input("Category", placeholder="e.g. Past Papers 2024", key="imp_category")
        imp_subtopic = st.text_input("Subtopic", placeholder="e.g. Respiratory", key="imp_subtopic")
        q_file = st.file_uploader("Questions PDF", type=["pdf"], key="imp_q")
        a_file = st.file_uploader("Answer key PDF", type=["pdf"], key="imp_a")
        if q_file:
            with st.spinner("Reading questions…"):
                import_questions_text = extract_text_from_pdf(q_file)
            _icat = imp_category.strip()
            _isub = imp_subtopic.strip() or q_file.name
            topic_name = f"{_icat} :: {_isub}" if _icat else _isub
            if import_questions_text.strip():
                st.success(f"✅ Questions: {q_file.name} ({len(import_questions_text):,} chars)")
            else:
                st.error(f"⚠️ {q_file.name}: no readable text found. "
                         f"This is a scanned/image PDF — import needs selectable text. "
                         f"See the note below.")
        if a_file:
            with st.spinner("Reading answer key…"):
                import_answers_text = extract_text_from_pdf(a_file)
            if import_answers_text.strip():
                st.success(f"✅ Answers: {a_file.name} ({len(import_answers_text):,} chars)")
            else:
                st.error(f"⚠️ {a_file.name}: no readable text found (scanned/image PDF).")
        # If either file uploaded but produced no text, explain the dead-end clearly
        if (q_file or a_file) and not (import_questions_text.strip() or import_answers_text.strip()):
            st.warning("📄 These PDFs are scanned images, so there's no text to import. "
                       "Import only works on PDFs with selectable text. To use scanned papers, "
                       "you'll need to OCR them first or paste the text in another way.")

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
streak = calculate_streak(st.session_state.get("current_user", "Terry"))
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
tab_dash, tab_viva, tab_mcq, tab_anki, tab_mock, tab_library, tab_proc, tab_help = st.tabs(
    ["📈  Dashboard", "🗣️  Viva", "📝  MCQ", "🗂️  Anki", "🎯  Mock Exam", "📚  Library", "🩺  Procedures", "❓  How to use"]
)

# ═════════════════════════════════════════════════════════════════════════════
# DASHBOARD TAB
# ═════════════════════════════════════════════════════════════════════════════
with tab_dash:
    du = st.session_state.get("current_user", "Terry")
    st.markdown(f"### Study Dashboard — {du}")

    total_mcqs   = c.execute("SELECT COUNT(*) FROM mcq_attempts WHERE user=?", (du,)).fetchone()[0]
    correct_mcqs = c.execute("SELECT COUNT(*) FROM mcq_attempts WHERE is_correct=1 AND user=?", (du,)).fetchone()[0]
    accuracy     = (correct_mcqs / total_mcqs * 100) if total_mcqs else 0
    total_viva   = c.execute("SELECT COUNT(*) FROM viva_reviews WHERE user=?", (du,)).fetchone()[0]
    easy_n  = c.execute("SELECT COUNT(*) FROM viva_reviews WHERE confidence=3 AND user=?", (du,)).fetchone()[0]
    good_n  = c.execute("SELECT COUNT(*) FROM viva_reviews WHERE confidence=2 AND user=?", (du,)).fetchone()[0]
    hard_n  = c.execute("SELECT COUNT(*) FROM viva_reviews WHERE confidence=1 AND user=?", (du,)).fetchone()[0]

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("MCQs Attempted",      total_mcqs)
    m2.metric("Correct Answers",     correct_mcqs)
    m3.metric("Overall Accuracy",    f"{accuracy:.1f}%")
    m4.metric("Viva Reviews",        total_viva)
    st.markdown("")

    # ── Performance by topic & category (the weak-spots tracker) ──
    attempts = fetch_attempts(du)
    if attempts:
        st.markdown("#### 📊 Performance by topic")
        st.caption("Accuracy per topic, grouped by category. Red = needs work, green = strong.")

        # Aggregate by category -> topic -> (correct, total)
        agg = {}
        for a in attempts:
            cat, disp = split_category(a.get("topic") or "Uncategorised")
            agg.setdefault(cat, {}).setdefault(disp, [0, 0])
            agg[cat][disp][1] += 1
            if a.get("is_correct"):
                agg[cat][disp][0] += 1

        def bar_colour(pct):
            if pct >= 75: return "#4CAF50"
            if pct >= 50: return "#C9A84C"
            return "#EF5350"

        for cat in sorted(agg.keys()):
            # Category-level totals
            c_correct = sum(v[0] for v in agg[cat].values())
            c_total = sum(v[1] for v in agg[cat].values())
            c_pct = (c_correct / c_total * 100) if c_total else 0
            st.markdown(
                f'<div style="margin-top:14px;font-weight:700;color:#C9A84C;">{cat} '
                f'<span style="color:#8A8070;font-weight:500;font-size:0.85rem;">'
                f'· {c_correct}/{c_total} ({c_pct:.0f}%)</span></div>',
                unsafe_allow_html=True
            )
            for topic in sorted(agg[cat].keys()):
                correct, tot = agg[cat][topic]
                pct = (correct / tot * 100) if tot else 0
                col = bar_colour(pct)
                st.markdown(
                    f'<div style="display:flex;align-items:center;gap:12px;margin:4px 0;">'
                    f'<div style="width:160px;font-size:0.85rem;color:#FAFAF8;overflow:hidden;'
                    f'text-overflow:ellipsis;white-space:nowrap;">{topic}</div>'
                    f'<div style="flex:1;background:#2E2A22;border-radius:6px;height:14px;position:relative;">'
                    f'<div style="width:{pct:.0f}%;background:{col};height:14px;border-radius:6px;"></div></div>'
                    f'<div style="width:70px;text-align:right;font-size:0.82rem;font-weight:600;color:{col};">'
                    f'{pct:.0f}% ({correct}/{tot})</div></div>',
                    unsafe_allow_html=True
                )
        st.markdown("")

        # ── Progress over time: rolling accuracy ──
        dated = [a for a in attempts if a.get("ts")]
        st.markdown("#### 📈 Accuracy over time")
        def _day(ts):
            return str(ts)[:10]
        by_day = {}
        for a in dated:
            d = _day(a["ts"])
            by_day.setdefault(d, [0, 0])
            by_day[d][1] += 1
            if a.get("is_correct"):
                by_day[d][0] += 1
        days_sorted = sorted(by_day.keys())

        if len(days_sorted) >= 2:
            rows = [{"Date": d, "Accuracy %": round(by_day[d][0] / by_day[d][1] * 100, 1)}
                    for d in days_sorted]
            try:
                df_prog = pd.DataFrame(rows).set_index("Date")
                st.line_chart(df_prog, height=220)
            except Exception:
                pass
        elif len(days_sorted) == 1:
            d = days_sorted[0]
            day_pct = round(by_day[d][0] / by_day[d][1] * 100, 1)
            st.info(f"📊 Today's accuracy: **{day_pct}%** ({by_day[d][0]}/{by_day[d][1]}). "
                    f"Come back tomorrow — the trend line appears once you've studied on 2+ days.")
        else:
            st.caption("Your accuracy trend will appear here once you've answered some MCQs.")
        st.markdown("")

    # ── Flagged questions: things you rated 👎 or left notes on ──
    def _load_flagged():
        if SUPABASE_ENABLED:
            try:
                res = supabase.table("mcq_feedback").select(
                    "question_text, rating, note").eq("user", du).execute()
                return [(r.get("question_text"), r.get("rating"), r.get("note"))
                        for r in res.data]
            except Exception:
                pass
        return c.execute("SELECT question_text, rating, note FROM mcq_feedback WHERE user=?", (du,)).fetchall()

    flagged = [f for f in _load_flagged()
               if (f[1] == "down") or (f[2] and f[2].strip())]
    if flagged:
        with st.expander(f"🚩 Flagged questions to improve ({len(flagged)})"):
            for qt, rating, note in flagged:
                tag = "👎" if rating == "down" else "📝"
                short = qt if len(qt) <= 110 else qt[:107] + "…"
                st.markdown(f"{tag} **{short}**")
                if note and note.strip():
                    st.caption(f"Note: {note}")
                st.markdown("")
    st.markdown("")

    st.markdown("#### 📅 Activity Heatmap")
    st.markdown(
        '<div style="background:#1E1B16;border:1px solid #2E2A22;border-radius:12px;padding:20px 24px;">'
        + build_heatmap_html(days=119, user=du) +
        '<div style="font-size:0.75rem;color:#8A8070;margin-top:10px;display:flex;align-items:center;gap:6px;">'
        'Less'
        '<span style="display:inline-block;width:12px;height:12px;border-radius:3px;background:#2E2A22;"></span>'
        '<span style="display:inline-block;width:12px;height:12px;border-radius:3px;background:#9BE08B;"></span>'
        '<span style="display:inline-block;width:12px;height:12px;border-radius:3px;background:#5FC96F;"></span>'
        '<span style="display:inline-block;width:12px;height:12px;border-radius:3px;background:#2F9E41;"></span>'
        '<span style="display:inline-block;width:12px;height:12px;border-radius:3px;background:#176127;"></span>'
        'More &nbsp;·&nbsp; darker = more questions that day'
        '</div>'
        '</div>', unsafe_allow_html=True
    )
    st.markdown("")

    col_l, col_r = st.columns(2)
    with col_l:
        st.markdown("#### 📈 MCQ Accuracy Over Time")
        history = c.execute("SELECT timestamp, is_correct FROM mcq_attempts WHERE user=? ORDER BY timestamp ASC", (du,)).fetchall()
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
    recent = c.execute("SELECT timestamp, topic, is_correct FROM mcq_attempts WHERE user=? ORDER BY timestamp DESC LIMIT 15", (du,)).fetchall()
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

    # ── Saved viva banks: baked-in banks AND anything you've generated ──
    builtin_viva = list_builtin_viva()
    cached_viva = list_topics_with_viva()  # [(topic, doc_hash, n), …]
    have_any_viva = bool(builtin_viva) or bool(cached_viva)
    if have_any_viva:
        with st.expander("📚 Load a saved viva bank", expanded=not st.session_state.get("viva_data")):
            # Unified entries: (category, display, source, ref, count)
            #   source "builtin" -> ref is the bank name; "cache" -> ref is doc_hash
            entries = []
            for full_name, qs in builtin_viva.items():
                cat, disp = split_category(full_name)
                entries.append((cat, disp, "builtin", full_name, len(qs)))
            for topic, doc_hash, n in cached_viva:
                cat, disp = split_category(topic)
                entries.append((cat, disp, "cache", doc_hash, n))

            cats = sorted({e[0] for e in entries})
            chosen_cat = st.selectbox("Category", ["All categories"] + cats, key="viva_cat_filter")

            shown = entries if chosen_cat == "All categories" else [e for e in entries if e[0] == chosen_cat]
            shown = sorted(shown, key=lambda e: (e[0].lower(), e[1].lower()))

            # Build labels; include category prefix when showing all
            label_map = {}
            labels = ["—"]
            for cat, disp, source, ref, n in shown:
                lbl = (f"{cat} › {disp} · {n} Q" if chosen_cat == "All categories"
                       else f"{disp} · {n} Q")
                # de-duplicate identical labels defensively
                if lbl in label_map:
                    lbl = f"{lbl} ({source})"
                label_map[lbl] = (source, ref, disp if chosen_cat != "All categories" else f"{cat} › {disp}")
                labels.append(lbl)

            pick_lbl = st.selectbox("Viva bank", labels,
                                    label_visibility="collapsed", key="viva_bank_pick")
            if pick_lbl != "—" and st.button("Load this viva bank", key="load_viva_bank"):
                source, ref, nice_name = label_map[pick_lbl]
                if source == "builtin":
                    st.session_state["viva_data"] = builtin_viva[ref]
                else:
                    st.session_state["viva_data"] = get_viva_for_hash(ref)
                st.session_state["viva_revealed"] = {}
                st.session_state["viva_confidence_logged"] = {}
                st.session_state["viva_bank_name"] = nice_name
                st.rerun()

    if not pdf_ready and not st.session_state.get("viva_data"):
        st.info("👈 Generate viva from a document in 'Generate from notes' mode, or load a saved viva bank above.")
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
                            vtopic = st.session_state.get("viva_bank_name") or topic_name
                            log_viva_review(vtopic, st.session_state["viva_data"][idx]["question"], level, st.session_state.get("current_user","Terry"))
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
    # ── Load a saved MCQ bank directly (categorised) ──
    mcq_topics = list_topics_with_mcqs()
    if mcq_topics and not st.session_state.get("mcqs"):
        with st.expander("📚 Load a saved MCQ bank", expanded=True):
            mcq_cats = {}
            for topic, doc_hash, n in mcq_topics:
                cat, disp = split_category(topic)
                mcq_cats.setdefault(cat, []).append((disp, topic, doc_hash, n))
            mcq_cat_pick = st.selectbox("Category",
                                        ["All categories"] + sorted(mcq_cats.keys()),
                                        key="mcq_cat_filter")
            shown = sorted(mcq_cats.keys()) if mcq_cat_pick == "All categories" else [mcq_cat_pick]
            choices = []
            for cat in shown:
                for disp, topic, doc_hash, n in sorted(mcq_cats[cat]):
                    choices.append((f"{cat} › {disp} · {n} Q", doc_hash))
            labels = ["—"] + [lbl for lbl, _ in choices]
            picked = st.selectbox("Bank", labels, label_visibility="collapsed", key="mcq_bank_pick")
            if picked != "—" and st.button("Load this MCQ bank", key="load_mcq_bank"):
                dh = dict((lbl, h) for lbl, h in choices)[picked]
                st.session_state["mcqs"] = get_mcqs_for_hash(dh)
                st.session_state["mcq_submitted"] = {}
                st.session_state["mcq_mode"] = None
                st.session_state["mcq_exam_idx"] = 0
                st.session_state["exam_start_time"] = None
                st.session_state["is_imported"] = False
                st.rerun()

    if not pdf_ready and not import_ready and not st.session_state.get("mcqs"):
        # More specific guidance if the user is mid-import
        if app_mode == "📥 Import existing paper":
            if (import_questions_text and not import_questions_text.strip()) or \
               (import_answers_text and not import_answers_text.strip()):
                st.info("📄 The uploaded PDF(s) have no readable text (scanned images), so there's "
                        "nothing to import. Import needs PDFs with selectable text.")
            elif bool(import_questions_text.strip()) ^ bool(import_answers_text.strip()):
                st.info("Almost there — import needs **both** a questions PDF *and* an answer key PDF "
                        "with readable text. Upload the missing one to continue.")
            else:
                st.info("👈 Upload both the questions PDF and the answer key PDF to import a paper.")
        else:
            st.info("👈 Upload a PDF, import a paper, or load a saved bank above to begin.")
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
                render_image(mcq)
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
                                log_mcq_attempt(topic_name, mcq["question_text"], choice, correct_letter, is_correct, st.session_state.get("current_user","Terry"))
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
                        st.markdown("---")
                        render_feedback(mcq, f"fb_exam_{idx}")

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

                render_image(mcq)
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
                            log_mcq_attempt(topic_name, mcq["question_text"], choice, correct_letter, is_correct, st.session_state.get("current_user","Terry"))
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
                        st.markdown("---")
                        render_feedback(mcq, f"fb_review_{i}")

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

            # Group topics by free-form category ("Category :: Name")
            mock_cats = {}
            for topic, doc_hash, n in topics:
                cat, disp = split_category(topic)
                mock_cats.setdefault(cat, []).append((disp, topic, doc_hash, n))

            cat_filter = st.selectbox("Filter by category",
                                      ["All categories"] + sorted(mock_cats.keys()),
                                      key="mock_cat_filter")
            shown_cats = sorted(mock_cats.keys()) if cat_filter == "All categories" else [cat_filter]

            # Topic selection checkboxes, grouped under category headers
            selected_hashes = []
            for cat in shown_cats:
                st.markdown(f"**{cat}**")
                for disp, topic, doc_hash, n in sorted(mock_cats[cat]):
                    short = disp if len(disp) <= 45 else disp[:42] + "…"
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
                if pool_size > 1:
                    num_q = st.slider("Number of questions", min_value=1,
                                      max_value=pool_size, value=min(20, pool_size))
                elif pool_size == 1:
                    num_q = 1
                    st.caption("1 question available.")
                else:
                    st.caption("Select at least one topic to continue.")
                    num_q = 0
            with col_mode:
                exam_style = st.radio("Mode", ["⏱️ Timed exam", "📖 Untimed review"],
                                      label_visibility="visible")
                secs_per_q = st.number_input(
                    "Seconds per question (timed mode)",
                    min_value=10, max_value=600, value=75, step=5,
                    help="Set this to mirror your real exam. e.g. a 60-min exam given over 75 min "
                         "for ~50 questions is about 90 seconds per question. The total time = "
                         "seconds × number of questions.")

            # Show the resulting total time so you can match your real exam
            if exam_style.startswith("⏱️") and pool_size > 0:
                total_secs = int(secs_per_q) * num_q
                mins = total_secs // 60
                st.caption(f"⏱ Total exam time: {mins} min {total_secs % 60} sec "
                           f"({num_q} questions × {int(secs_per_q)}s each)")

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
                st.session_state["mock_secs_per_q"] = int(secs_per_q)
                st.session_state["mock_limit"] = int(secs_per_q) * num_q
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
            # Countdown against the set limit (if one exists), else count up
            limit = st.session_state.get("mock_limit", 0)
            if timed and limit > 0:
                remaining = limit - elapsed
                if remaining <= 0:
                    timer_html = ('<span style="font-weight:700;color:#EF5350;font-family:monospace;'
                                  'font-size:1rem;">⏱ TIME UP</span>')
                else:
                    # gold normally, orange under 5 min, red under 1 min
                    tcol = "#C9A84C"
                    if remaining < 60:
                        tcol = "#EF5350"
                    elif remaining < 300:
                        tcol = "#E0913C"
                    timer_html = (f'<span style="font-weight:700;color:{tcol};font-family:monospace;'
                                  f'font-size:1rem;">⏱ {fmt_time(remaining)} left</span>')
            elif timed:
                timer_html = (f'<span style="font-weight:700;color:#8A8070;font-family:monospace;'
                              f'font-size:1rem;">⏱ {fmt_time(elapsed)}</span>')
            else:
                timer_html = '<span style="color:#8A8070;font-size:0.85rem;">Untimed</span>'
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

            # Time-up notice (does not force-end — you can keep going for practice)
            if timed and limit > 0 and (limit - elapsed) <= 0:
                st.warning("⏱ Time's up — in the real exam you'd stop here. "
                           "You can keep answering for practice; your result still records.")

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
            render_image(mcq)
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
                        log_mcq_attempt("Mock Exam", mcq["question_text"], choice, correct_letter, ok, st.session_state.get("current_user","Terry"))
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
                    st.markdown("---")
                    render_feedback(mcq, f"fb_mock_{idx}")

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


# ═════════════════════════════════════════════════════════════════════════════
# LIBRARY TAB — shared text-notes library; read + generate questions from notes
# ═════════════════════════════════════════════════════════════════════════════
with tab_library:
    st.markdown("### 📚 Library")
    st.caption("Shared notes for Terry & Alex. Upload extracts the text (the original PDF stays on your device). No API cost to store or read.")

    lib_user = st.session_state.get("current_user", "Terry")

    # ── Upload a new note ──
    with st.expander("➕ Add a note to the library", expanded=False):
        lib_cat = st.text_input("Category", placeholder="e.g. ICU Week 8", key="lib_cat")
        lib_sub = st.text_input("Subtopic / title", placeholder="e.g. ARDS", key="lib_sub")

        add_method = st.radio("Add by", ["📄 Upload PDF", "⌨️ Paste / type text"],
                              horizontal=True, key="lib_add_method")

        if add_method == "📄 Upload PDF":
            lib_file = st.file_uploader("Upload a PDF (text will be extracted)", type=["pdf"], key="lib_upload")
            if st.button("💾 Save to library", key="lib_save", type="primary"):
                if not lib_file:
                    st.warning("Please attach a PDF first.")
                else:
                    with st.spinner("Extracting text…"):
                        try:
                            text = extract_text_from_pdf(lib_file)
                        except Exception as e:
                            text = ""
                            st.error(f"Could not read PDF: {e}")
                    st.caption(f"Extracted {len(text)} characters.")
                    if text.strip():
                        title = lib_sub.strip() or lib_file.name
                        ok = save_library_note(title, lib_cat.strip(), lib_sub.strip(), text, lib_user)
                        if ok:
                            st.success(f"✅ Saved “{title}” to the library. Scroll down to see it.")
                        else:
                            st.error("Could not save the note (see error above).")
                    else:
                        st.warning("⚠️ No text extracted — likely a scanned/image PDF. Text-only library needs selectable text.")
        else:
            pasted = st.text_area("Paste or type your notes here",
                                  height=260, key="lib_paste",
                                  placeholder="Paste your notes — you control the formatting exactly.")
            if st.button("💾 Save to library", key="lib_save_paste", type="primary"):
                if not pasted.strip():
                    st.warning("Please paste or type some text first.")
                elif not lib_sub.strip():
                    st.warning("Please add a Subtopic / title.")
                else:
                    title = lib_sub.strip()
                    ok = save_library_note(title, lib_cat.strip(), lib_sub.strip(), pasted, lib_user)
                    if ok:
                        st.success(f"✅ Saved “{title}” to the library. Scroll down to see it.")
                    else:
                        st.error("Could not save the note (see error above).")

    st.markdown("---")

    # ── Browse notes (list, grouped by category) ──
    notes = list_library_notes()
    if not notes:
        st.info("No notes yet. Add your first note above.")
    else:
        # Category filter
        cats = sorted({(n.get("category") or "Uncategorised") for n in notes})
        cat_pick = st.selectbox("Filter by category", ["All categories"] + cats, key="lib_cat_filter")
        shown = notes if cat_pick == "All categories" else [n for n in notes if (n.get("category") or "Uncategorised") == cat_pick]

        st.caption(f"{len(shown)} note(s)")

        for n in shown:
            nid = n.get("id")
            title = n.get("title") or "Untitled"
            cat = n.get("category") or "Uncategorised"
            by = n.get("uploaded_by") or "?"
            header = f"{cat} › {title}  ·  added by {by}"
            with st.expander(header):
                content = n.get("content") or ""
                edit_key = f"lib_editing_{nid}"
                editing = st.session_state.get(edit_key, False)

                if editing:
                    # ── Edit mode ──
                    e_cat = st.text_input("Category", value=cat if cat != "Uncategorised" else "",
                                          key=f"lib_ecat_{nid}")
                    e_title = st.text_input("Subtopic / title", value=title, key=f"lib_etitle_{nid}")
                    e_content = st.text_area("Note text", value=content, height=360,
                                             key=f"lib_econtent_{nid}")
                    cs, cc = st.columns(2)
                    with cs:
                        if st.button("💾 Save changes", key=f"lib_savedit_{nid}", type="primary"):
                            ok = update_library_note(nid, e_title.strip(), e_cat.strip(),
                                                     e_title.strip(), e_content)
                            if ok:
                                st.session_state[edit_key] = False
                                st.success("Saved.")
                                st.rerun()
                    with cc:
                        if st.button("Cancel", key=f"lib_canceledit_{nid}"):
                            st.session_state[edit_key] = False
                            st.rerun()
                else:
                    # ── Read mode ──
                    show_raw = st.toggle("Show raw text", key=f"lib_raw_{nid}", value=False)
                    if show_raw:
                        st.text_area("Note text", value=content, height=300,
                                     key=f"lib_read_{nid}", label_visibility="collapsed")
                    else:
                        st.markdown(format_note_text(content))

                    # Generate questions straight from this note
                    st.markdown("**Generate from this note:**")
                    g1, g2, g3 = st.columns(3)
                    topic_for_gen = f"{cat} :: {title}" if cat and cat != "Uncategorised" else title
                    with g1:
                        if st.button("📝 MCQs", key=f"lib_gen_mcq_{nid}"):
                            with st.spinner("Generating MCQs…"):
                                generate_section("mcq", content, topic_for_gen)
                            st.success("MCQs generated — see the MCQ & Mock Exam tabs.")
                    with g2:
                        if st.button("🗣️ Viva", key=f"lib_gen_viva_{nid}"):
                            with st.spinner("Generating viva…"):
                                generate_section("viva", content, topic_for_gen)
                            st.success("Viva generated — see the Viva tab picker.")
                    with g3:
                        if st.button("🗂️ Anki", key=f"lib_gen_anki_{nid}"):
                            with st.spinner("Generating Anki cards…"):
                                generate_section("anki", content, topic_for_gen)
                            st.success("Anki generated — see the Anki tab.")

                    # Edit + Delete row
                    st.markdown("---")
                    ec1, ec2 = st.columns(2)
                    with ec1:
                        if st.button("✏️ Edit note", key=f"lib_edit_{nid}"):
                            st.session_state[edit_key] = True
                            st.rerun()
                    with ec2:
                        if by == lib_user:
                            if st.button("🗑️ Delete this note", key=f"lib_del_{nid}"):
                                delete_library_note(nid)
                                st.rerun()
                        else:
                            st.caption(f"Only {by} can delete.")


# ═════════════════════════════════════════════════════════════════════════════
# PROCEDURES TAB — two-phase procedural-skills practice
#   Phase 1: tick off the steps as you run through them
#   Phase 2: write the steps from memory, then reveal and compare
# ═════════════════════════════════════════════════════════════════════════════
with tab_proc:
    st.markdown("### 🩺 Procedural Skills")
    st.caption("Practise OSCE procedures two ways: tick-the-steps, or write them from memory and compare. "
               "Checklists are study aids — always defer to your local clinical guidelines and supervisor.")

    procs = all_procedures()

    # ── Add your own procedure ──
    with st.expander("➕ Add your own procedure"):
        np_name = st.text_input("Procedure name (use 'Category :: Name' to group it)",
                                placeholder="e.g. Catheters & Tubes :: Chest Drain", key="np_name")
        np_steps = st.text_area("Steps — one per line, in order", height=200,
                                placeholder="Wash hands\nIntroduce yourself\nConfirm patient identity\n...",
                                key="np_steps")
        if st.button("💾 Save procedure", key="np_save", type="primary"):
            steps = [s for s in (np_steps or "").split("\n") if s.strip()]
            if not np_name.strip():
                st.warning("Please give the procedure a name.")
            elif len(steps) < 2:
                st.warning("Please add at least two steps (one per line).")
            else:
                if save_user_procedure(np_name.strip(), steps, current_user):
                    st.success(f"✅ Saved “{np_name.strip()}”. Select it below.")
                    st.rerun()

    if not procs:
        st.info("No procedures yet. Add one above.")
    else:
        # ── Category filter + procedure picker ──
        proc_cats = {}
        for name, steps, source, ref in procs:
            cat, disp = split_category(name)
            proc_cats.setdefault(cat, []).append((disp, name, steps, source, ref))

        cat_pick = st.selectbox("Category", ["All categories"] + sorted(proc_cats.keys()),
                                key="proc_cat_filter")
        shown_cats = sorted(proc_cats.keys()) if cat_pick == "All categories" else [cat_pick]

        choices = []
        for cat in shown_cats:
            for disp, name, steps, source, ref in sorted(proc_cats[cat]):
                label = f"{cat} › {disp}" if cat_pick == "All categories" else disp
                choices.append((label, name, steps, source, ref))

        labels = ["—"] + [c[0] for c in choices]
        picked_label = st.selectbox("Procedure", labels, key="proc_pick")

        if picked_label != "—":
            _, pname, psteps, psource, pref = next(c for c in choices if c[0] == picked_label)

            mode = st.radio("Practice mode",
                            ["✅ Phase 1 — Tick the steps", "✍️ Phase 2 — Write from memory"],
                            key=f"proc_mode_{pref}")

            st.markdown(f"#### {split_category(pname)[1]}")
            st.caption(f"{len(psteps)} steps")

            if mode.startswith("✅"):
                # ── Phase 1: checklist ──
                done = 0
                for i, step in enumerate(psteps):
                    if st.checkbox(f"**{i+1}.** {step}", key=f"p1_{pref}_{i}"):
                        done += 1
                st.markdown("---")
                pct = (done / len(psteps) * 100) if psteps else 0
                st.progress(pct / 100, text=f"{done}/{len(psteps)} steps ticked ({pct:.0f}%)")
                if done == len(psteps) and len(psteps) > 0:
                    st.success("✅ All steps complete — nicely done.")
            else:
                # ── Phase 2: write from memory, then reveal ──
                st.caption("Write out the steps in order from memory, then reveal the checklist to compare.")
                st.text_area("Your steps", height=260, key=f"p2_input_{pref}",
                             placeholder="1. ...\n2. ...\n3. ...")
                if st.button("👁️ Reveal model checklist", key=f"p2_reveal_{pref}"):
                    st.session_state[f"p2_revealed_{pref}"] = True
                if st.session_state.get(f"p2_revealed_{pref}"):
                    st.markdown("---")
                    st.markdown("**Model checklist:**")
                    for i, step in enumerate(psteps):
                        st.markdown(f"**{i+1}.** {step}")
                    st.info("Compare against your own list — note any steps you missed or had out of order. "
                            "Self-assessment only; nothing is recorded.")

            # Delete (user-added only, by the person who added it)
            if psource == "user":
                st.markdown("---")
                up = next((p for p in list_user_procedures() if p["id"] == pref), None)
                if up and up.get("added_by") == current_user:
                    if st.button("🗑️ Delete this procedure", key=f"proc_del_{pref}"):
                        delete_user_procedure(pref)
                        st.rerun()


# ═════════════════════════════════════════════════════════════════════════════
# HELP TAB — how the site works, for Terry, Alex, or anyone new
# ═════════════════════════════════════════════════════════════════════════════
with tab_help:
    st.markdown("### ❓ How to use The Differential")
    st.caption("A quick guide for anyone using this study tool.")

    st.markdown("""
**The Differential** is a study tool for medical exams. You give it material (lecture
notes, or curated question banks), and it helps you drill that material as multiple-choice
questions, viva (spoken-style) questions, and Anki flashcards — and tracks how you're doing.

#### 👤 First: pick who you are
Use the **"Studying as"** selector in the sidebar (Terry or Alex). Your scores, ratings,
and progress are tracked separately. The question banks themselves are shared.

#### 🗂️ The two ways to get questions
1. **Generate from notes** *(uses the AI — counts toward daily limits)*
   In the sidebar, choose "Generate from notes", optionally add a Category and Subtopic,
   upload a PDF, then open the MCQ / Viva / Anki tab and press the Generate button. The AI
   reads your notes and writes questions from them.
2. **Saved banks** *(instant, free, no AI)*
   Curated question sets that are built into the app, plus anything you've generated before.
   Load them from the picker at the top of the MCQ and Viva tabs. These cost nothing and
   load instantly.

#### 📚 The tabs
- **Dashboard** — your stats: accuracy, performance by topic (red = needs work), progress over time, and any questions you flagged.
- **Viva** — spoken-exam-style Q&A. Read the question, think/say your answer, reveal the model answer, then rate your confidence (Hard / Good / Easy).
- **MCQ** — multiple-choice. Exam mode (timed, with a question navigator and mark-for-review) or review mode. You can also leave 👍/👎 feedback and notes on each question.
- **Anki** — exports cloze-deletion flashcards you can import into the Anki app.
- **Mock Exam** — build a custom exam by picking topics from your saved banks. Instant, no AI cost.
- **Library** — shared reference notes. Upload a PDF or paste text; it stores the text (the original PDF stays on your device). You can read notes here and generate questions straight from them.
- **Procedures** — practise OSCE procedural skills two ways: Phase 1 ticks off the steps as a checklist; Phase 2 hides them so you write the steps from memory then reveal and compare. You can add your own procedures too.

#### 🏷️ Categories
When uploading or naming a bank, you can file things under a **Category** and **Subtopic**
(e.g. "ICU Week 8" › "ARDS"). The MCQ, Viva, and Mock Exam tabs let you filter by category.

#### ✅ Strengths
- Turns your own notes into practice questions quickly.
- Saved banks and the library are free and instant (no AI cost).
- Tracks weak topics so you know what to revise.
- Works on any device through the web link; data is saved permanently.

#### ⚠️ Limitations (honest)
- **AI questions are only as good as the notes given**, and the AI can occasionally make
  mistakes or include something slightly off — always sanity-check against a trusted source.
- **Generating questions uses a daily free AI quota.** If generation fails or is slow, it's
  usually the quota or a busy server — saved banks and the library don't have this problem.
- **The library stores text only** — original formatting, images, and diagrams from PDFs are
  not preserved. Keep your original files elsewhere (e.g. Google Drive) for the pristine version.
- **Scanned/image PDFs won't work** for generation or the library — the text must be selectable.
- This tool **supports** your study; it isn't a source of truth. Use your guidelines and
  textbooks as the authority.

#### 🆘 If something doesn't work
- Check the sidebar shows **🟢 Permanent storage active**.
- If a generation fails, wait a moment and try again (likely a busy server or quota), or use a saved bank.
- Generated content and uploads are saved automatically — you don't need to do anything to keep them.
""")
