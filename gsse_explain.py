"""
gsse_explain.py — fill in the missing GSSE statement explanations with Gemini.

Finds every Type X statement with a blank explanation (~3,750 across ~1,030
questions) and generates a concise, exam-relevant explanation with Gemini
(same free-tier stack as emed_rewrite.py). Each generated explanation is tagged
(explanation_ai=True) so the app shows an "AI-generated · verify" badge and
nothing is trusted until you review it.

SAFETY / RESUMABILITY
  - Only fills BLANK explanations; never overwrites your existing ones.
  - Writes after every question (crash-safe). Re-run to resume where it stopped.
  - --limit N to sample first; --topic "Thorax" to do one topic.

USAGE
  pip install google-generativeai
  export GEMINI_API_KEY=...              # the key your app already uses
  python gsse_explain.py --limit 10      # sample, inspect the JSON
  python gsse_explain.py --topic Thorax  # one topic
  python gsse_explain.py                  # everything remaining
"""
import os, json, time, argparse

MODEL = os.environ.get("GSSE_EXPLAIN_MODEL", "gemini-2.0-flash")
SRC = "gsse_seed_questions.json"

SYSTEM = (
    "You are an examiner-level tutor for the RACS Generic Surgical Sciences Exam "
    "(GSSE), covering anatomy, physiology and pathology. Given a single true/false "
    "statement, its correct answer, and its topic, write a concise 1-3 sentence "
    "explanation of WHY it is true or false. Be precise, use correct anatomical/"
    "physiological terminology, and stay strictly factual. Do not restate the "
    "statement verbatim, do not add caveats or disclaimers, and output only the "
    "explanation text."
)

def load():
    d = json.load(open(SRC, encoding="utf-8"))
    return d, (d["questions"] if isinstance(d, dict) else d)

def blanks(q):
    return [s for s in (q.get("statements") or [])
            if not (s.get("explanation") and str(s["explanation"]).strip())]

def generate(model, prompt, tries=6):
    """Generate with backoff. Free-tier throttling (429/quota) waits and retries
    instead of skipping the statement."""
    for attempt in range(tries):
        try:
            r = model.generate_content(prompt)
            return (r.text or "").strip()
        except Exception as e:
            msg = str(e).lower()
            transient = any(k in msg for k in ("429", "rate", "quota", "resource", "exhaust", "503", "unavailable"))
            if transient and attempt < tries - 1:
                wait = min(60, 5 * (attempt + 1))
                print(f"    throttled, waiting {wait}s...")
                time.sleep(wait)
                continue
            raise

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--topic", default="")
    args = ap.parse_args()

    d, qs = load()
    targets = [q for q in qs if q.get("type") == "X" and blanks(q)
               and (args.topic.lower() in (q.get("topic_label", "").lower()) if args.topic else True)]
    total_blanks = sum(len(blanks(q)) for q in targets)
    print(f"{len(targets)} questions with blanks | {total_blanks} statements to explain")

    if not os.environ.get("GEMINI_API_KEY"):
        print("Set GEMINI_API_KEY to run. Nothing generated."); return
    import google.generativeai as genai
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    model = genai.GenerativeModel(MODEL, system_instruction=SYSTEM)

    done = 0
    stop = False
    for q in targets:
        stem = q.get("stem", "")
        topic = q.get("topic_label", "")
        for s in q["statements"]:
            if s.get("explanation") and str(s["explanation"]).strip():
                continue
            verdict = "TRUE" if s.get("answer") else "FALSE"
            full = f"{stem} {s['text']}".strip() if stem and stem.lower().startswith(("the", "a ", "an ")) else s["text"]
            prompt = (f"Topic: {topic}\nStatement: \"{full}\"\n"
                      f"Correct answer: {verdict}\n\nExplain why in 1-3 sentences.")
            try:
                text = generate(model, prompt)
                if len(text) < 15:
                    raise ValueError("empty")
                s["explanation"] = text
                s["explanation_ai"] = True
                done += 1
            except Exception as e:
                print(f"  ! skip ({e})")
                continue
            if args.limit and done >= args.limit:
                stop = True
                break
        json.dump(d, open(SRC, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        if stop:
            break
        time.sleep(0.4)
    print(f"Done. Generated {done} explanations (tagged explanation_ai). "
          f"Review them via the ✨ badge before trusting.")

if __name__ == "__main__":
    main()
