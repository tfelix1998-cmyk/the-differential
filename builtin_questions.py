# ═════════════════════════════════════════════════════════════════════════════
# builtin_questions.py — your permanent, baked-in question banks
#
# Questions added here are loaded into the app automatically on startup, appear
# in the MCQ tab AND the Mock Exam builder, survive every restart, and cost ZERO
# API calls. This is where you put your curated, high-yield, reusable sets.
#
# ─────────────────────────────────────────────────────────────────────────────
# HOW TO ADD A BANK
# ─────────────────────────────────────────────────────────────────────────────
# 1. Generate questions however you like (e.g. in a separate Claude / AI Studio
#    chat, refining them until they're high quality).
# 2. Ask for output in EXACTLY this JSON structure (one object per question):
#
#    {
#      "question_text": "Full clinical vignette and the question.",
#      "options": ["A) ...", "B) ...", "C) ...", "D) ...", "E) ..."],
#      "correct_answer_letter": "C",
#      "explanation": "Why C is correct and why the others are wrong.",
#      "key_learning_points": "One concise takeaway.",
#      "image_url": ""        ←  OPTIONAL. A public image URL (ECG, X-ray, etc.)
#                                or leave as "" / omit entirely if no image.
#    }
#
# 3. Paste the list of objects under a new entry in BUILTIN_BANKS below, giving
#    it a clear topic name (this is what shows in the app).
#
# RULES:
#   • Every string must be in double quotes, commas between items, no trailing comma.
#   • options can have 4 or 5 entries — whatever the question needs.
#   • Only use your own questions, university past papers, or openly-licensed
#     material. For images, use openly-licensed sources (Wikimedia Commons,
#     Radiopaedia free cases, open-access journals).
# ═════════════════════════════════════════════════════════════════════════════


BUILTIN_BANKS = {

    # ── Example bank — delete or replace with your own ────────────────────────
    "Example Bank (Endocrine)": [
        {
            "question_text": (
                "A 13-year-old girl is brought to clinic for a yearly physical. She "
                "feels well but has not started puberty. BP is 152/91 mmHg. Exam shows "
                "a lack of secondary sexual characteristics and a blind vagina. Labs "
                "reveal hypokalaemia with low testosterone and oestradiol. Karyotype is "
                "46,XY. This patient most likely has a deficiency of which enzyme?"
            ),
            "options": [
                "A) 5 alpha-reductase",
                "B) 11 beta-hydroxylase",
                "C) 17 alpha-hydroxylase",
                "D) 20,22-desmolase",
                "E) 21-hydroxylase",
            ],
            "correct_answer_letter": "C",
            "explanation": (
                "17 alpha-hydroxylase deficiency reduces cortisol and sex steroids, "
                "driving ACTH and mineralocorticoid excess — causing hypertension and "
                "hypokalaemia with absent puberty. 21-hydroxylase and 11 beta-hydroxylase "
                "deficiencies cause virilisation (opposite picture); 5 alpha-reductase "
                "deficiency does not cause hypertension; 20,22-desmolase deficiency is "
                "typically fatal early."
            ),
            "key_learning_points": (
                "17 alpha-hydroxylase deficiency = hypertension + hypokalaemia + absent "
                "puberty (the 'hypertensive' form of CAH)."
            ),
            "image_url": "",
        },
        # ← add more question objects here, separated by commas
    ],

    # ── Add your own banks below, following the same pattern ──────────────────
    # "Cardiology Past Paper 2024": [ { ... }, { ... } ],
    # "Antibiotics High-Yield":     [ { ... }, { ... } ],

}
