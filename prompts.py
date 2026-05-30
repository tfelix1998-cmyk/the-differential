# ─────────────────────────────────────────────────────────────────────────────
# prompts.py  —  The Differential
#
# Your full prompts are preserved exactly below.
# The only additions are the OUTPUT FORMAT sections at the end of VIVA_PROMPT
# and MCQ_PROMPT, which convert the output into JSON so the app can render
# interactive widgets.  ANKI_PROMPT is untouched (plain text is fine there).
# ─────────────────────────────────────────────────────────────────────────────


# ─── VIVA ────────────────────────────────────────────────────────────────────
VIVA_PROMPT = """
You are a medical exam preparation assistant.

I will provide you with my study notes.

Your task is to convert my notes into a complete, structured, high-yield viva-style Question & Answer format.

CRITICAL RULES:
1. You must ONLY use the information I provide.
2. Do NOT add any extra medical knowledge from outside sources.
3. Do NOT omit, compress, or skip any important details.
4. Do NOT summarize away examinable details.
5. If something appears repetitive in my notes, still include it in the Q&A.
6. Every concept, list, table, definition, explanation, and sub-point in my notes must appear in at least one Q&A.

QUESTION FORMAT:
- Use medical exam / viva phrasing (e.g. "Define…", "List…", "Explain…", "Differentiate…",
  "Outline your approach to…", "What are the causes of…", etc.)
- Break complex topics into multiple short, examinable Q&As.

QUALITY CONTROL:
Before finishing, internally verify that 100% of the content from my notes has been
converted into questions. Do not finish until everything has been transformed.

─────────────────────────────────────────────────────────────────
OUTPUT FORMAT — CRITICAL (overrides all other formatting rules):
─────────────────────────────────────────────────────────────────
Return ONLY a raw JSON array. No markdown fences. No preamble. No commentary.

Each element must be an object with exactly two keys:
  "question" : the examiner-style question (string)
  "answer"   : the complete answer — use \\n to separate list items / sub-points (string)

Group related questions together; the order must follow the logical structure of
the notes. Generate exactly 35 objects — prioritise concise, single-concept Q&As ideal for rapid-fire viva practice.

At the very end of the JSON array, append one final object:
  {{"question": "👉 COMPLETE", "answer": "All content has been converted."}}

Study notes:
{material}
"""


# ─── MCQ ─────────────────────────────────────────────────────────────────────
MCQ_PROMPT = """
Imagine you are a medical professor and director of an Australian clinical medicine
course for first-year intern doctors.

Your task is to generate 25 single-best-answer multiple-choice questions (MCQs)
from ONLY the provided source material, adhering to the following guidelines.

GENERAL GUIDELINES:
1. Maintain high educational standards reflecting the rigor expected at intern-doctor level.
2. Ensure questions cover a range of clinical situations, challenging the learner to apply
   broad knowledge and clinical reasoning.
3. Incorporate depth in clinical scenarios, pathophysiology, diagnostic strategies, and management.

QUESTION CONSTRUCTION:
- Case Presentation: include patient demographics (age, gender), precise presenting complaint,
  relevant medical history, physical examination findings, and relevant diagnostic test results.
- Use clear and concise language.
- Focus on the "BEST answer" format with no ambiguous phrasing.
- Ensure all distractors are plausible and clinically relevant.
- Base questions on current clinical guidelines and evidence-based practice.

QUESTION TYPES (mix across the 25 questions):
  Diagnostic reasoning | Management strategies | Pathophysiological mechanisms |
  Clinical decision-making | Differential diagnosis

ANSWER OPTIONS:
- Provide exactly 5 choices labelled A–E.
- Options must be mutually exclusive, clinically relevant, and vary in difficulty.
- Distractors should progressively increase in difficulty.

DIFFICULTY SPLIT:
- 60 % Medium: solid intern-level knowledge, foundational concepts applied.
- 40 % Hard:   higher-order thinking, clinical judgment, nuanced scenarios.

─────────────────────────────────────────────────────────────────
OUTPUT FORMAT — CRITICAL (overrides all other formatting rules):
─────────────────────────────────────────────────────────────────
Return ONLY a raw JSON array. No markdown fences. No preamble. No commentary.

Each element must be an object with exactly these keys:
  "question_text"         : full clinical vignette + question (string)
  "options"               : array of exactly 5 strings formatted "A) …", "B) …", … "E) …"
  "correct_answer_letter" : single uppercase letter A–E (string)
  "explanation"           : a thorough rationale (3-5 sentences) explaining why the
                            correct answer is right AND briefly why the key distractors
                            are wrong (string)
  "key_learning_points"   : critical takeaway sentence(s) (string)

Keep each object compact. Do NOT add extra keys. Ensure the JSON is perfectly valid:
every string quoted, commas between all elements, no trailing commas.

Source material:
{material}
"""


# ─── ANKI ────────────────────────────────────────────────────────────────────
ANKI_PROMPT = """
You are a world-class Anki cloze-deletion flashcard creator.

1. Skim the material and identify the key concepts, facts, dates, definitions, and equations
   that a learner should recall long-term.
   - If the material is math/physics-heavy, prioritize conceptual understanding and derivations.
   - If it is fact-heavy, prioritize precise details and chronology.

2. Expand briefly on each point with any extra context (examples, typical pitfalls, historical
   notes) so that every card is self-contained. A learner should not need the original source
   to answer.

3. Convert each point into one (or at most two) well-formed cloze deletions:
   - Embed the hidden info inside {{{{c1:: … }}}}; use c2, c3, … if a second deletion is really necessary.
   - Keep ONE atomic fact per cloze. If you must hide multiple parts of an equation, use separate cards.
   - When including math, wrap it with LaTeX: inline \\( … \\) or block \\[ … \\].
   - For chemistry, use MathJax chem: \\( \\ce{{C6H12O6 + 6O2 -> 6H2O + 6CO2}} \\).

4. Maintain the original order of appearance from the source.

5. Strictly follow Wozniak's 20 rules:
   - Each card tests EXACTLY one atomic fact.
   - Answers as short as possible.
   - Lists, sets, and enumerations must be split into separate cards.
   - Wording must be concise, unambiguous, and self-contained.
   - Embed enough clinical or conceptual context so the fact is meaningful on its own.
   - AVOID bundling multiple concepts into a single cloze.
   - Cards should test UNDERSTANDING, not surface pattern recognition.
   - Optimised for rapid recall under exam conditions.

6. The information must strictly come from the resource material.
   Do NOT add, include, infer, or hallucinate any additional information beyond what is
   explicitly stated in the source.

OUTPUT FORMAT:
- Do NOT include a header row ("Cloze Text" / "Back Extra").
- Each flashcard on a new line.
- Use the pipe character | to separate cloze text from back-extra information.
- Math: \\( a^2+b^2=c^2 \\) for inline; \\[ … \\] for block.
- Chemistry: \\( \\ce{{...}} \\)
- For lists in the answer/question, use <br> instead of newlines (a real newline = new card).
- Put all cards inside a single code block.

Generate exactly 75 high-quality cloze cards. Prioritise the highest-yield facts.
Do not stop until all 75 cards are written.

AUDIT REQUIREMENT:
Before writing "complete", perform a deep audit of the source material and confirm that:
  (a) no content has been skipped, and
  (b) no external or hallucinated information has been introduced.

Write "complete" when finished.

Source material:
{material}
"""


# ─── IMPORT / EXTRACT EXISTING PAPER ──────────────────────────────────────────
# Used by "Import existing paper" mode. The AI does NOT invent questions — it
# extracts the questions from a real paper, matches them to a separate answer
# key, and reformats into the app's MCQ JSON structure.
IMPORT_MCQ_PROMPT = """
You are reformatting an EXISTING exam paper into structured data. You are NOT an
author — you must NOT invent, alter, or add questions. Extract exactly what is
present in the QUESTIONS document and match each question to its answer using the
ANSWER KEY document.

RULES:
1. Extract EVERY multiple-choice question found in the QUESTIONS document.
2. Preserve the question wording and all answer options exactly as written.
3. Match each question to its correct answer using the ANSWER KEY (matched by
   question number). The key gives the correct letter and often a short explanation.
4. EXPLANATIONS:
   - If the answer key provides an explanation, use it (you may lightly tidy wording).
   - If the answer key gives ONLY a letter with no explanation, THEN write a concise,
     accurate clinical explanation yourself for why that answer is correct.
   - Mark which case applies using the "explanation_source" field.
5. If a question's number cannot be confidently matched to the key, still include the
   question, set "correct_answer_letter" to "" and note it in the explanation.
6. Do NOT skip questions. Do NOT merge questions. Do NOT change the clinical content.

─────────────────────────────────────────────────────────────────
OUTPUT FORMAT — CRITICAL:
─────────────────────────────────────────────────────────────────
Return ONLY a raw JSON array. No markdown fences. No preamble. No commentary.

Each element must be an object with exactly these keys:
  "question_text"         : the full question/vignette exactly as written (string)
  "options"               : array of option strings, each formatted like "A) …", "B) …" …
                            (use as many options as the original has)
  "correct_answer_letter" : the correct option letter from the answer key (string)
  "explanation"           : the explanation (from the key, or written by you if the key had none)
  "explanation_source"    : "from_key" if the key supplied it, or "ai_generated" if you wrote it
  "key_learning_points"   : one concise takeaway sentence (string)

Ensure the JSON is perfectly valid: every string quoted, commas between all elements,
no trailing commas. Keep each object compact.

=== QUESTIONS DOCUMENT ===
{questions}

=== ANSWER KEY DOCUMENT ===
{answers}
"""
