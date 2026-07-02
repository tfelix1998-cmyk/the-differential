"""
emed_rewrite.py  —  Australianise + de-image the broken EMED questions.

WHAT IT DOES
  Finds every EMED question that is image-dependent or has a missing vignette,
  and redrafts the STEM so it is answerable from text alone, using the findings
  already described in that question's explanation. Applies the "Australian
  clinical professor" brief (QLD Health / eTG / AMH alignment). It NEVER changes
  the options or the correct answer, and it keeps the original stem in
  `original_question_text`. Every rewritten question is flagged
  `needs_au_review=True` so nothing goes live until you approve it via the ⚑
  badge in the app.

SAFETY
  - Originals preserved (and git). Re-runnable. Checkpoints after every question
    so a crash never loses work (--resume skips ones already done).
  - Questions whose explanation contains no image description are SKIPPED and
    written to emed_unfixable.txt for you to handle manually (add image / delete).

USAGE
  pip install google-generativeai
  export GEMINI_API_KEY=...          # same key your app uses
  python emed_rewrite.py --limit 5   # dry sample first, inspect emed_questions.py
  python emed_rewrite.py             # full run (~256 questions)
  python emed_rewrite.py --resume    # continue after an interruption
"""
import os, re, io, json, time, argparse

MODEL = os.environ.get("EMED_MODEL", "gemini-2.0-flash")
SRC = "emed_questions.py"

PROFESSOR_BRIEF = """You are a medical professor and director of an Australian clinical medicine \
course for first-year intern doctors. You are reviewing a flagged single-best-answer question that \
was extracted by OCR from a practice bank and originally relied on an image the student can no \
longer see.

Your task: rewrite ONLY the question stem so it can be answered WITHOUT the image, by weaving the \
relevant findings (which are described in the provided explanation) into the stem in clean clinical \
prose. Align terminology, drug choices and thresholds to Australian practice (QLD Health, eTG, AMH). \
Do NOT change the clinical scenario, the options, or which option is correct. Do NOT add new findings \
that aren't supported by the explanation. Keep the lead-in question essentially as-is.

Return STRICT JSON only, no markdown: {"stem": "<rewritten stem>"}"""

def load_banks():
    ns = {}; exec(open(SRC, encoding="utf-8").read(), ns)
    return ns["EMED_BANKS"]

IMG = re.compile(r'\(\\*[a-z]*mage[^)]*\)|\(image[^)]*\)|\bimage\b|\(\\\\mace\)', re.I)
BARE = re.compile(r'^(which|what|the most)', re.I)
DESC = re.compile(r'(shows?|reveals?|demonstrat|appearance|x-ray|ct |mri|ecg|scan|photograph|image)', re.I)

def is_broken(q):
    t = q["question_text"]
    return bool(IMG.search(t)) or (len(t) < 170 and BARE.match(t.strip()))

def reconstructable(q):
    e = q.get("explanation", "")
    return len(e) > 250 and DESC.search(e)

def emit(banks):
    out = io.StringIO()
    out.write('"""emed_questions.py - EMED practice question bank (UQ section)."""\n\n')
    out.write("EMED_BANKS = {\n")
    for bank, qs in banks.items():
        out.write("    " + repr(bank) + ": [\n")
        for q in qs:
            out.write("        " + repr(q) + ",\n")
        out.write("    ],\n")
    out.write("}\n")
    open(SRC, "w", encoding="utf-8").write(out.getvalue())

def rewrite_stem(model, q):
    import google.generativeai as genai
    prompt = (f"{PROFESSOR_BRIEF}\n\nCURRENT STEM:\n{q['question_text']}\n\n"
              f"OPTIONS:\n{chr(10).join(q['options'])}\n\n"
              f"CORRECT ANSWER: {q['correct_answer_letter']}\n\n"
              f"EXPLANATION (contains the image findings):\n{q.get('explanation','')[:2500]}")
    resp = model.generate_content(prompt)
    txt = resp.text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    return json.loads(txt)["stem"].strip()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0, help="process at most N (0 = all)")
    ap.add_argument("--resume", action="store_true", help="skip already-rewritten questions")
    args = ap.parse_args()

    banks = load_banks()
    targets = [(bk, i) for bk, v in banks.items() for i, q in enumerate(v) if is_broken(q)]
    todo, unfixable = [], []
    for bk, i in targets:
        q = banks[bk][i]
        if args.resume and q.get("rewrite_status") in ("done", "seed_manual"):
            continue
        (todo if reconstructable(q) else unfixable).append((bk, i))

    with open("emed_unfixable.txt", "w", encoding="utf-8") as f:
        for bk, i in unfixable:
            f.write(f"{bk}  [idx {i}]  ::  {banks[bk][i]['question_text'][:120]}\n")
    print(f"{len(targets)} broken | {len(todo)} to rewrite | {len(unfixable)} unfixable (see emed_unfixable.txt)")

    if not os.environ.get("GEMINI_API_KEY"):
        print("Set GEMINI_API_KEY to run the rewrites. Nothing sent."); return
    import google.generativeai as genai
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    model = genai.GenerativeModel(MODEL)

    n = 0
    for bk, i in todo:
        if args.limit and n >= args.limit:
            break
        q = banks[bk][i]
        try:
            new = rewrite_stem(model, q)
            if len(new) < 40:
                raise ValueError("suspiciously short rewrite")
            q["original_question_text"] = q.get("original_question_text", q["question_text"])
            q["question_text"] = new
            q["needs_au_review"] = True
            q["rewrite_status"] = "done"
            emit(banks)                      # checkpoint every question
            n += 1
            print(f"[{n}] rewrote  {bk.split('EMED - ')[-1]}  idx {i}")
            time.sleep(1.2)                  # gentle rate-limit
        except Exception as e:
            print(f"  ! skipped idx {i} in {bk.split('EMED - ')[-1]}: {e}")
    print(f"Done. Rewrote {n}. All flagged needs_au_review — review via the ⚑ badge before trusting.")

if __name__ == "__main__":
    main()
