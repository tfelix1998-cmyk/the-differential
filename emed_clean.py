"""
emed_clean.py — text repair for the EMED question banks.
=======================================================

The EMED banks were built by OCR'ing scanned material. OCR damage is
*systematic*, not random, so it can be repaired systematically. This module is
the repair layer. It is applied at LOAD TIME in uq.py, exactly like
emed_stem_overrides.py — so the 7.1 MB emed_questions.py never has to be
reopened or re-uploaded.

    from emed_clean import clean_banks
    EMED_BANKS = clean_banks(EMED_BANKS)

What it fixes
-------------
1. WORD-LEVEL OCR ERRORS (the big one). Tesseract confuses letter shapes in
   predictable pairs:
       l -> i    biood, piatelet, aicohol, pian, iliness, needie
       i -> l    patlent, oploid, blopsy, sigmold, thyrold
       l -> t    tesion, tymphoma, medicat, generat
       f -> t    tever, tracture, tunction, betore, satety
       rn -> m   tendemess, concems, moming, extemal, newbom, pemicious
       ll -> li  galistones, ampiciliin
   Fixed via an explicit, hand-checked dictionary (WORD_FIXES). A dictionary,
   not a rule engine: rule engines "correct" labour -> tabour. Every entry
   below was verified against the actual bank text.

2. SPURIOUS OPENING QUOTES. 1,300+ stray ' characters were inserted mid-
   sentence by the OCR ("struck 'on the right side of his head"). Removed —
   unless the sentence actually closes the quote, which is real speech.

3. MID-SENTENCE CAPITALS. "Which one of the following Is the most appropriate"
   (266 of these), "the causative agent In this patient's overdose".

4. SPACING / PUNCTUATION. "A70-year-old man" -> "A 70-year-old man",
   "clear.He is" -> "clear. He is", double spaces, space before punctuation.

5. UNITS. x10*9/L -> x10^9/L, and creatinine/urea/bilirubin reported in
   "pmol/L" -> "umol/L" (an OCR read of the mu, not real picomolar).

6. IMAGE OCR NOISE. Where a figure was OCR'd, the stem carries a run of
   garbage glyphs ("Z = z -_ I i . =-- 1 h a"). Runs of >= 5 junk tokens are
   stripped.

7. UNSERVABLE QUESTIONS ARE DROPPED. Two classes, both unanswerable:
     - "hollow" stems: the vignette lived in an image, so the stem is nothing
       but the lead-in ("Which one of the following is the most likely
       diagnosis?"). 91 of these.
     - questions whose CORRECT option OCR'd into garbage ('eco', 'vsp',
       'Hise', '11%,', 'om', 'of'), or that carry a blank option.
   An unanswerable question is worse than no question.

8. OPTION REPAIRS for the handful that are recoverable with certainty
   (the ASA-grade ladders, "Q fever").

Nothing here invents clinical content. Every fix is orthographic — a
mis-scanned character restored to what the source word must have been. Where a
word could not be recovered with certainty, the question is dropped, not
guessed at.
"""

import re
from functools import lru_cache

# ---------------------------------------------------------------------------
# 1. Word-level OCR dictionary
# ---------------------------------------------------------------------------
# Keys are lower-case. Matching is case-insensitive and whole-word; the
# replacement inherits the original word's capitalisation (see _fix_words).
#
# DELIBERATELY EXCLUDED (they look like errors but are correct as-is):
#   labour, intra-, statin, Horner, Osler, Holter, folic, ovale, Alport,
#   pulmonale, Dressler, Felty, Menten, linea, Weil, Snellen, Centor, conus,
#   arcus, metres, steppage, rousable, Darier — plus every acronym
#   (SpO2, MCV, ALS, SLE, PRN, GORD, ...).

WORD_FIXES = {
    # --- l -> i ------------------------------------------------------------
    "aicohol": "alcohol", "aicoholic": "alcoholic", "atcoholic": "alcoholic",
    "aithough": "although", "aliows": "allows", "anaigesia": "analgesia",
    "anaphyiaxis": "anaphylaxis", "anaphytaxis": "anaphylaxis",
    "animais": "animals", "ankie": "ankle", "ankte": "ankle",
    "antinuciear": "antinuclear", "antinuctear": "antinuclear",
    "appie": "apple", "avaitable": "available", "availabie": "available",
    "biadder": "bladder", "biast": "blast", "biasts": "blasts",
    "bieed": "bleed", "bieeding": "bleeding", "biepharitis": "blepharitis",
    "biock": "block", "biockade": "blockade", "biocker": "blocker",
    "biocking": "blocking", "biood": "blood", "boius": "bolus",
    "bubbie": "bubble", "bundie": "bundle", "bundte": "bundle",
    "caicification": "calcification", "caicium": "calcium",
    "catcium": "calcium", "ceils": "cells", "celis": "cells",
    "characteristicaily": "characteristically", "chioride": "chloride",
    "chiorine": "chlorine", "chiamydia": "chlamydia", "chitd": "child",
    "chotecystitis": "cholecystitis", "coaguiase": "coagulase",
    "coaguiation": "coagulation", "compiain": "complain",
    "compiains": "complains", "compiaint": "complaint",
    "compiaints": "complaints", "compieted": "completed",
    "compietion": "completion", "compiete": "complete", "compiex": "complex",
    "controlied": "controlled", "uncontrolied": "uncontrolled",
    "crystalioid": "crystalloid", "cutture": "culture", "cuttures": "cultures",
    "cytopiasm": "cytoplasm", "daity": "daily", "dectine": "decline",
    "distocation": "dislocation", "doubie": "double", "duliness": "dullness",
    "emoliients": "emollients", "epigiottis": "epiglottis",
    "epigiottitis": "epiglottitis", "erysipeias": "erysipelas",
    "evaiuate": "evaluate", "evoive": "evolve", "exophthaimos": "exophthalmos",
    "expiain": "explain", "exptain": "explain", "expioration": "exploration",
    "faiis": "falls", "falis": "falls", "femaies": "females",
    "fiags": "flags", "fiank": "flank", "fiexion": "flexion",
    "fiuid": "fluid", "freckiing": "freckling", "fuliness": "fullness",
    "furuncie": "furuncle", "galibladder": "gallbladder",
    "galistone": "gallstone", "galistones": "gallstones",
    "generaily": "generally", "gentie": "gentle", "giand": "gland",
    "gtucose": "glucose", "haemogiobin": "haemoglobin",
    "haemophitia": "haemophilia", "haimark": "hallmark",
    "halimark": "hallmark", "heaith": "health", "heipful": "helpful",
    "heips": "helps", "hoiding": "holding", "hospitai": "hospital",
    "hyperpiasia": "hyperplasia", "inciude": "include",
    "inciuding": "including", "inctuding": "including",
    "inhaied": "inhaled", "intervais": "intervals", "invoive": "involve",
    "irestyle": "lifestyle", "itseif": "itself", "leveis": "levels",
    "mainourished": "malnourished", "mainourishment": "malnourishment",
    "mainutrition": "malnutrition", "mantie": "mantle",
    "measies": "measles", "medicat": "medical", "meianoma": "melanoma",
    "metanoma": "melanoma", "middie": "middle", "midiine": "midline",
    "moiluscum": "molluscum", "moliuscum": "molluscum",
    "monocional": "monoclonal", "monoctonal": "monoclonal",
    "muitiple": "multiple", "multipie": "multiple", "multipte": "multiple",
    "muscie": "muscle", "myaigia": "myalgia", "myaigias": "myalgias",
    "neopiasm": "neoplasm", "needie": "needle", "needies": "needles",
    "neuraigia": "neuralgia", "nodutar": "nodular", "nucieus": "nucleus",
    "occiudes": "occludes", "ophthaimia": "ophthalmia",
    "osteomaiacia": "osteomalacia", "osteomyeiitis": "osteomyelitis",
    "otaigia": "otalgia", "overioad": "overload", "overtoad": "overload",
    "paiiiative": "palliative", "pailiative": "palliative",
    "paimar": "palmar", "paims": "palms", "paipable": "palpable",
    "painiess": "painless", "paintess": "painless", "paisy": "palsy",
    "palior": "pallor", "papilioma": "papilloma", "particies": "particles",
    "patelia": "patella", "pateliar": "patellar", "peivic": "pelvic",
    "peivis": "pelvis", "peopie": "people", "physiotogical": "physiological",
    "piace": "place", "piacental": "placental", "piain": "plain",
    "pian": "plan", "pians": "plans", "pianning": "planning",
    "piant": "plant", "piantar": "plantar", "piasma": "plasma",
    "piatelet": "platelet", "pieural": "pleural", "pieuritic": "pleuritic",
    "preciude": "preclude", "prophyiactic": "prophylactic",
    "prophyiaxis": "prophylaxis", "prophytaxis": "prophylaxis",
    "propelied": "propelled", "protonged": "prolonged",
    "puimonary": "pulmonary", "regardiess": "regardless",
    "reguiar": "regular", "reiease": "release", "reptacement": "replacement",
    "resoive": "resolve", "resoives": "resolves", "resuits": "results",
    "restiess": "restless", "reveais": "reveals", "saddie": "saddle",
    "saipingectomy": "salpingectomy", "salmonelia": "salmonella",
    "sandfiy": "sandfly", "scariet": "scarlet", "scteritis": "scleritis",
    "scterosis": "sclerosis", "shelifish": "shellfish",
    "shockabie": "shockable", "shouid": "should", "shouider": "shoulder",
    "sieep": "sleep", "sieeping": "sleeping", "sieeve": "sleeve",
    "siowly": "slowly", "smail": "small", "smaliness": "smallness",
    "spelis": "spells", "spinai": "spinal", "spondyiitis": "spondylitis",
    "staiks": "stalks", "stimutation": "stimulation",
    "stranguiated": "strangulated", "subtie": "subtle", "subtte": "subtle",
    "suitabie": "suitable", "superticially": "superficially",
    "swaliow": "swallow", "swetling": "swelling", "threshoid": "threshold",
    "toddier": "toddler", "transpiant": "transplant",
    "transtocation": "translocation", "tubercuiosis": "tuberculosis",
    "uicer": "ulcer", "uicerate": "ulcerate", "uinar": "ulnar",
    "uitrasound": "ultrasound", "uttrasound": "ultrasound",
    "uniess": "unless", "untess": "unless", "uniikely": "unlikely",
    "vaive": "valve", "vaives": "valves", "vaigus": "valgus",
    "vatvular": "valvular", "vuival": "vulval", "weekiy": "weekly",
    "whiist": "whilst", "whitiow": "whitlow", "windiass": "windlass",
    "wouid": "would", "yieid": "yield", "yleld": "yield",
    "withhoid": "withhold", "yearty": "yearly",

    # --- i -> l ------------------------------------------------------------
    "adenitls": "adenitis", "anecholc": "anechoic",
    "anisometropla": "anisometropia", "aithough2": "although",
    "blochemical": "biochemical", "blopsy": "biopsy", "calclum": "calcium",
    "calcull": "calculi", "circult": "circuit", "corticosterolds": "corticosteroids",
    "diplococcl": "diplococci", "dlagnosing": "diagnosing",
    "dysphagla": "dysphagia", "ectopla": "ectopia", "elther": "either",
    "emboll": "emboli", "fallure": "failure", "fluld": "fluid",
    "haemorrholds": "haemorrhoids", "hyperparathyroldism": "hyperparathyroidism",
    "kawasakl": "kawasaki", "latrogenic": "iatrogenic", "lleal": "ileal",
    "lleum": "ileum", "lodine": "iodine", "oploid": "opioid",
    "patlent": "patient", "patlents": "patients", "pationt": "patient",
    "pllot": "pilot", "quallfy": "qualify", "relles": "relies",
    "serlous": "serious", "sigmold": "sigmoid", "sterolds": "steroids",
    "stimull": "stimuli", "streptococcl": "streptococci",
    "survelllance": "surveillance", "thyrold": "thyroid", "tralt": "trait",
    "uveltis": "uveitis", "varlx": "varix", "walting": "waiting",

    # --- l -> t ------------------------------------------------------------
    "bacteriat": "bacterial", "basat": "basal", "commonty": "commonly",
    "contro": "control", "contrat": "control", "controt": "control",
    "familiat": "familial", "famitial": "familial", "genera": "general",
    "generat": "general", "individuats": "individuals", "internat": "internal",
    "ionicity": "tonicity", "itlegal": "illegal", "iteus": "ileus",
    "laterat": "lateral", "tateral": "lateral", "legisiation": "legislation",
    "levet": "level", "matles": "measles", "nodat": "nodal",
    "particularty": "particularly", "patate": "palate",
    "phenobarbitat": "phenobarbital", "pharyngeai": "pharyngeal",
    "pharyngeat": "pharyngeal", "prevatent": "prevalent",
    "radiat": "radial", "recreationat": "recreational", "seriat": "serial",
    "smatl": "small", "taceration": "laceration", "tamily": "family",
    "taparoscopy": "laparoscopy", "taryngeal": "laryngeal",
    "tayer": "layer", "tentigo": "lentigo", "ientigo": "lentigo",
    "tesion": "lesion", "tigation": "ligation", "tipase": "lipase",
    "tipoma": "lipoma", "tithium": "lithium", "tiver": "liver",
    "tupus": "lupus", "tymphatic": "lymphatic", "tymphoma": "lymphoma",
    "tysis": "lysis", "varicocete": "varicocele", "virat": "viral",
    "hydrocete": "hydrocele", "athietes": "athletes", "attruism": "altruism",
    "altrulsm": "altruism", "atzheimer": "alzheimer", "auteimmune": "autoimmune",
    "cholesterot": "cholesterol", "coton": "colon", "deceterations": "decelerations",
    "mataria": "malaria", "naphthatene": "naphthalene", "neutrophit": "neutrophil",
    "basophits": "basophils", "profite": "profile", "seriat2": "serial",

    # --- f -> t ------------------------------------------------------------
    "betore": "before", "briet": "brief", "caretul": "careful",
    "clett": "cleft", "contirms": "confirms", "deticiency": "deficiency",
    "detault": "default", "detined": "defined", "ditfuse": "diffuse",
    "difterent": "different", "dissatistaction": "dissatisfaction",
    "dystunction": "dysfunction", "eftusion": "effusion",
    "ineftective": "ineffective", "intarction": "infarction",
    "intections": "infections", "intective": "infective",
    "intittrate": "infiltrate", "intittrates": "infiltrates",
    "infittrate": "infiltrate", "infittrates": "infiltrates",
    "intlammation": "inflammation", "intormation": "information",
    "intusion": "infusion", "ibuproten": "ibuprofen",
    "liquetactive": "liquefactive", "moditied": "modified",
    "moditication": "modification", "pertorm": "perform",
    "pertormed": "performed", "pertusion": "perfusion",
    "preterence": "preference", "protessional": "professional",
    "reter": "refer", "reterral": "referral", "reterrals": "referrals",
    "reterred": "referred", "refiux": "reflux", "retlex": "reflex",
    "refiex": "reflex", "retief": "relief", "reliet": "relief",
    "satety": "safety", "sigiiticant": "significant",
    "signiticant": "significant", "specitic": "specific",
    "succes stully": "successfully", "successtully": "successfully",
    "tactors": "factors", "temale": "female", "tever": "fever",
    "tormation": "formation", "tracture": "fracture",
    "transter": "transfer", "transtuse": "transfuse",
    "tunction": "function", "tusions": "fusions", "wartarin": "warfarin",
    "griet": "grief", "trom": "from", "tron": "iron",

    # --- rn -> m -----------------------------------------------------------
    "altemative": "alternative", "amold": "arnold", "buming": "burning",
    "comeal": "corneal", "concem": "concern", "concems": "concerns",
    "concemed": "concerned", "conceming": "concerning",
    "discemible": "discernible", "extemal": "external",
    "fingemails": "fingernails", "fernur": "femur", "heartbum": "heartburn",
    "hemia": "hernia", "intemal": "internal", "moming": "morning",
    "movernent": "movement", "newbom": "newborn", "pattems": "patterns",
    "pemicious": "pernicious", "retum": "return", "tendemess": "tenderness",
    "govemment": "government",

    # --- doubled/merged letters and misc -----------------------------------
    "iliness": "illness", "ilinesses": "illnesses", "ampiciliin": "ampicillin",
    "amoxicitlin": "amoxicillin", "penicitlamine": "penicillamine",
    "deteroxamine": "desferrioxamine", "acetyicholine": "acetylcholine",
    "afebrite": "afebrile", "antiblotics": "antibiotics",
    "anglogram": "angiogram", "anglography": "angiography",
    "anomaious": "anomalous", "alrway": "airway", "awhite": "awhile",
    "bellefs": "beliefs", "cheice": "choice", "diverticulltis": "diverticulitis",
    "flelscher": "fleischer", "heimiich": "heimlich", "impiant": "implant",
    "laparescopic": "laparoscopic", "maliory": "mallory",
    "pneumethorax": "pneumothorax", "queensiand": "queensland",
    "recoliecting": "recollecting", "renai": "renal", "phiegm": "phlegm",
    "tightenings": "lightenings", "welll": "well", "weund": "wound",
    "branchial": "bronchial", "hbaic": "hba1c", "hbalc": "hba1c",
    "creck": "creek", "impase": "impasse", "jeg": "leg", "jeft": "left",
    "jung": "lung", "jymph": "lymph",
}

# --- Glued words -----------------------------------------------------------
# The scan repeatedly welds a leading article onto the next word: "Achest
# X-ray is ordered", "Acorrected QT interval", "Asingle measurement".
# An explicit list, not a rule: a rule that splits "A" + known-word would also
# split Atopic, Aplastic, Avascular, Asystole, Aetiology and Atraumatic.
GLUED_FIXES = {
    "ablood": "a blood", "abrachial": "a brachial", "abuttonhole": "a buttonhole",
    "acentral": "a central", "acerebral": "a cerebral", "acervical": "a cervical",
    "achest": "a chest", "achild": "a child", "aclassical": "a classical",
    "aclosed": "a closed", "acombination": "a combination", "acommon": "a common",
    "acomplete": "a complete", "acomprehensive": "a comprehensive",
    "acompulsion": "a compulsion", "acomputed": "a computed",
    "aconcerned": "a concerned", "aconfounding": "a confounding",
    "acontinuous": "a continuous", "acontused": "a contused",
    "acorkscrew": "a corkscrew", "acorrected": "a corrected",
    "acrescendo": "a crescendo", "acrown": "a crown", "adense": "a dense",
    "adependent": "a dependent", "adetailed": "a detailed",
    "adiagnosis": "a diagnosis", "adiaphragm": "a diaphragm",
    "adifferentiating": "a differentiating", "adilatation": "a dilatation",
    "adirect": "a direct", "adiscussion": "a discussion", "agastric": "a gastric",
    "ageneral": "a general", "aheterozygous": "a heterozygous", "ahigh": "a high",
    "ahighly": "a highly", "ahistory": "a history", "ahoarse": "a hoarse",
    "ahydrocele": "a hydrocele", "akeloid": "a keloid", "alarge": "a large",
    "aleft": "a left", "alesion": "a lesion", "alipoma": "a lipoma",
    "aliver": "a liver", "alung": "a lung", "amajor": "a major", "amean": "a mean",
    "amedial": "a medial", "amedical": "a medical", "anarrow": "a narrow",
    "anasal": "a nasal", "anegative": "a negative", "aneonate": "a neonate",
    "aneurogenic": "a neurogenic", "anewborn": "a newborn", "anewer": "a newer",
    "anormal": "a normal", "anuclear": "a nuclear", "apanic": "a panic",
    "apatient": "a patient", "apelvic": "a pelvic", "aplan": "a plan",
    "apneumothorax": "a pneumothorax", "apositive": "a positive",
    "apotential": "a potential", "apreviously": "a previously",
    "aprimary": "a primary", "aprofessional": "a professional",
    "aproton": "a proton", "arapid": "a rapid", "arapidly": "a rapidly",
    "arecent": "a recent", "arectus": "a rectus", "arenal": "a renal",
    "areport": "a report", "areported": "a reported", "aretrograde": "a retrograde",
    "areview": "a review", "arupture": "a rupture", "aruptured": "a ruptured",
    "ascore": "a score", "aserum": "a serum", "asigmoid": "a sigmoid",
    "asignificant": "a significant", "asimple": "a simple", "asingle": "a single",
    "askin": "a skin", "aspontaneous": "a spontaneous", "asteady": "a steady",
    "astructured": "a structured", "asummary": "a summary",
    "asuspected": "a suspected", "aswelling": "a swelling",
    "asystematic": "a systematic", "aterm": "a term", "athorough": "a thorough",
    "athyroid": "a thyroid", "aunilateral": "a unilateral", "aurinary": "a urinary",
    "aurine": "a urine", "auseful": "a useful", "avaricocele": "a varicocele",
    "avenous": "a venous", "avexatious": "a vexatious", "aweekly": "a weekly",
    "awhite": "a white", "awide": "a wide",
    "anacceleration": "an acceleration", "anacute": "an acute",
    "anafebrile": "an afebrile", "anelevated": "an elevated",
    "anelevation": "an elevation", "anempty": "an empty",
    "anepidural": "an epidural", "anerect": "an erect", "anisolated": "an isolated",
    "annurse": "a nurse",
    "inadult": "in adult", "incases": "in cases", "inchildren": "in children",
    "inchronic": "in chronic", "indiabetic": "in diabetic",
    "inemergency": "in emergency", "ingeneral": "in general",
    "inrheumatoid": "in rheumatoid", "inyoung": "in young", "inthe": "in the",
    "inpatients": "in patients", "isa": "is a", "itis": "it is",
    "ofthe": "of the", "tothe": "to the", "itrisks": "it risks",
}
WORD_FIXES.update(GLUED_FIXES)

# Words that must never be touched even if they look like a fix key.
_PROTECTED = {
    "labour", "labours", "intra", "statin", "statins", "horner", "osler",
    "holter", "folic", "ovale", "alport", "pulmonale", "dressler", "felty",
    "menten", "linea", "weil", "snellen", "centor", "conus", "arcus",
    "metres", "metre", "steppage", "rousable", "darier", "novo", "von",
    "coli", "mol", "als", "sle", "spo", "mcv", "prn", "gord", "gaba",
}

_WORD_RE = re.compile(r"[A-Za-z][A-Za-z']*")


def _restore_case(src, repl):
    """Give `repl` the capitalisation pattern of `src`."""
    if src.isupper() and len(src) > 1:
        return repl.upper()
    if src[:1].isupper():
        return repl[:1].upper() + repl[1:]
    return repl


@lru_cache(maxsize=200000)
def _fix_word(w):
    low = w.lower()
    if low in _PROTECTED:
        return w
    repl = WORD_FIXES.get(low)
    return _restore_case(w, repl) if repl else w


def _fix_words(text):
    # NB: a single compiled alternation of all ~500 keys is *slower* here, not
    # faster — case-insensitive alternation of that width backtracks. Scanning
    # words and hitting a cached dict lookup wins.
    return _WORD_RE.sub(lambda m: _fix_word(m.group(0)), text)


# ---------------------------------------------------------------------------
# 2. Character / punctuation / spacing rules
# ---------------------------------------------------------------------------

# A spurious opening quote: whitespace, then ' or ", then a letter — with no
# closing quote before the end of the sentence. Real quoted speech ("he 'aches
# all over,' especially...") closes, so it is left alone.
_STRAY_OPEN = re.compile(r"(^|[\s(])[\u2018\u201c](?=[A-Za-z0-9])")
_CLOSING = re.compile(r"[\u2019\u201d]")

# Capitalised function words stranded mid-sentence by the OCR. Only fires when
# the PREVIOUS character is a lower-case letter — i.e. no sentence ended — so
# "His chest is clear. He is alert" is never touched.
_MIDCAP = re.compile(
    r"(?<=[a-z] )(Is|In|It|If|Of|On|At|By|As|To|Or|And|The|With|For|From|Was|Are|Has|Have|Not|But|That|This|Which|When)\b"
)
_MIDCAP_KEEP_TITLE = {"Which"}   # "…, Which one of the following" is still wrong

# Lowercase "i" and capital "I" are the same glyph in many scanned fonts, so the
# scan capitalises i-initial words mid-sentence: "head Injury", "raised
# Intracranial pressure", "Ischaemic changes". Only fires mid-sentence (after a
# lowercase letter + space), so sentence-initial words are untouched.
_MIDCAP_I = re.compile(r"(?<=[a-z] )(I[a-z]{2,})\b")
_MIDCAP_I_KEEP = {"Indian", "Irish", "Italian", "Islander", "Indigenous", "India",
                  "Ireland", "Italy", "International", "Institute", "Iraq", "Iran"}

# Image-OCR noise. Where a figure was scanned, Tesseract emits a long run of
# nonsense glyphs:
#     "...(image 1). Ae Lan ie ' a eee ae ee 5 mr; ' - Which one of the..."
# Detected by DENSITY, not by a fixed run length: a token is "junk" if it is
# punctuation-only, or a 1-2 letter fragment, or a short vowel-less string, or
# a word with punctuation embedded in it. Any window of >= 6 tokens that is
# >= 70% junk is dropped, and adjacent windows merge. A prose sentence never
# reaches that density; a scanned figure always does.
_PUNCT_ONLY = re.compile(r"^[^A-Za-z0-9]+$")
_FRAGMENT = re.compile(r"^[A-Za-z]{1,2}[^A-Za-z0-9]*$")
_NO_VOWEL = re.compile(r"^[bcdfghjklmnpqrstvwxz]{3,5}$", re.I)
_DIRTY = re.compile(r"^[A-Za-z]{1,6}[^\sA-Za-z0-9\-'\.,%/()]+[A-Za-z]*$")

_WIN = 6
_DENSITY = 0.7

# str.translate is an order of magnitude cheaper than re.sub, and the same few
# thousand tokens recur across 2,500 questions, so the classification is cached.
_ALPHA_ONLY = {c: None for c in range(256) if not chr(c).isalpha()}


@lru_cache(maxsize=200000)
def _is_junk_tok(tok):
    if _PUNCT_ONLY.match(tok):
        return True
    if _FRAGMENT.match(tok):
        return True
    core = tok.translate(_ALPHA_ONLY)
    if core and _NO_VOWEL.match(core):
        return True
    if _DIRTY.match(tok):
        return True
    return False


@lru_cache(maxsize=200000)
def _alpha_len(tok):
    return len(tok.translate(_ALPHA_ONLY))


def _strip_line_noise(line):
    toks = line.split()
    if len(toks) < _WIN:
        return line
    junk = [_is_junk_tok(t) for t in toks]
    if sum(junk) < _WIN * _DENSITY:      # fast path: nothing dense enough
        return line
    drop = [False] * len(toks)
    for i in range(0, len(toks) - _WIN + 1):
        if sum(junk[i:i + _WIN]) / _WIN >= _DENSITY:
            for j in range(i, i + _WIN):
                drop[j] = True
    # keep real words that got caught at a window edge
    for i, t in enumerate(toks):
        if drop[i] and not junk[i] and _alpha_len(t) >= 4:
            drop[i] = False
    return " ".join(t for i, t in enumerate(toks) if not drop[i])


def _strip_image_noise(text):
    """Line by line — joining the whole thing on spaces would flatten the
    paragraph breaks and bullets that the explanation renderer depends on."""
    if "\n" not in text:
        return _strip_line_noise(text)
    return "\n".join(_strip_line_noise(l) for l in text.split("\n"))


# The scan sometimes catches the answer chip above the explanation:
#     "Melanoma 1% This patient presents with classic features of..."
_ANSWER_CHIP = re.compile(r"^[A-Z][A-Za-z /\-]{2,34}\s+\d{1,3}%\s+(?=[A-Z])")


def _strip_stray_quotes(text):
    def sub(m):
        # is there a closing quote within the next ~120 chars / same sentence?
        tail = text[m.end(): m.end() + 120]
        tail = re.split(r"(?<=[.?!])\s", tail)[0]
        if _CLOSING.search(tail):
            return m.group(0)          # real quoted speech — keep
        return m.group(1)              # spurious — drop the quote mark
    return _STRAY_OPEN.sub(sub, text)


# Analytes that are always micromolar; OCR read the mu as a p.
_MICROMOLAR = re.compile(
    r"\b(creatinine|urea|bilirubin|urate|cr)\b([^.;]{0,40}?)\bpmol\s*/\s*L",
    re.I,
)


# Precompiled: these run over every one of ~17,000 strings, and letting the re
# module re-look-up the pattern each time was measurable.
_U_TEN9   = re.compile(r"x\s*10\s*[\*\u00b0\^]\s*9")
_U_TEN9L  = re.compile(r"\bx\s*10\s*[\u00b0\*]\s*/\s*L")
_U_HBA1C  = re.compile(r"\bHbAIc\b|\bHbAlc\b")
_U_FEV1   = re.compile(r"\bFEV[Il|]\b")
_U_GKG    = re.compile(r"(\d(?:\.\d+)?)\s*9\s*/\s*kg\b")
_S_AGE1   = re.compile(r"\b(An?)(\d{1,3}-(?:year|month|week|day))\b")
_S_AGE2   = re.compile(r"([a-z])(\d{1,3}-(?:year|month|week|day)-old)\b")
_S_DOT    = re.compile(r"([a-z]{2})\.([A-Z])")
_S_COMMA  = re.compile(r"([a-z]),([A-Z])")
_S_PREPUN = re.compile(r"\s+([,.;:?!])")
_S_QBULL  = re.compile(r"[\u2018\u2019]\s*\+")
_S_SPACES = re.compile(r"[ \t]{2,}")
_S_NLPAD  = re.compile(r" *\n *")
_S_NLRUN  = re.compile(r"\n{3,}")
_S_SENTCAP = re.compile(r"(^|[.?!]\s+)([a-z])")
# Marker glyphs left stranded where _mark_bullets could not read them as the
# start of a point (followed by an acronym, or sitting inside image noise).
# Q/Y/G/9/2 are NOT stripped — those are real content when they are not markers.
_LONE_GLYPH = re.compile(r"(?<=\s)[@\u00a9\u00ae\u00b0\u25cf\u25aa\u2122](?=[\s\.,;:])")


def _fix_units(text):
    text = _U_TEN9.sub("x10^9", text)
    text = _U_TEN9L.sub("x10^9/L", text)
    text = _MICROMOLAR.sub(lambda m: f"{m.group(1)}{m.group(2)}umol/L", text)
    text = text.replace("mmoi/L", "mmol/L").replace("mmol/l", "mmol/L")
    text = _U_HBA1C.sub("HbA1c", text)
    text = _U_FEV1.sub("FEV1", text)
    text = _U_GKG.sub(r"\1 g/kg", text)   # "mannitol 19/kg" -> "1 g/kg"
    return text


def _fix_spacing(text):
    text = text.replace("|mage", "Image").replace("|", "l")
    text = _S_AGE1.sub(r"\1 \2", text)          # "A70-year-old"
    text = _S_AGE2.sub(r"\1 \2", text)          # "aged72-year-old"
    text = _S_DOT.sub(r"\1. \2", text)          # missing space after full stop
    text = _S_COMMA.sub(r"\1, \2", text)        # ... and after a comma
    text = _S_PREPUN.sub(r"\1", text)           # space BEFORE punctuation
    text = _S_QBULL.sub(" *", text)             # OCR bullet artefacts
    text = text.replace("\u2022", "*")
    text = _S_SPACES.sub(" ", text)             # collapse runs, keep para breaks
    text = _S_NLPAD.sub("\n", text)
    text = _S_NLRUN.sub("\n\n", text)
    return text.strip()


def clean_text(text):
    """Full repair pass over one piece of bank prose."""
    if not text:
        return text
    t = str(text)
    t = _ANSWER_CHIP.sub("", t)
    t = _strip_image_noise(t)
    t = _strip_stray_quotes(t)
    t = _fix_units(t)
    t = _fix_words(t)
    t = _LONE_GLYPH.sub("", t)
    t = _MIDCAP.sub(lambda m: m.group(1).lower(), t)
    t = _MIDCAP_I.sub(
        lambda m: m.group(1) if m.group(1) in _MIDCAP_I_KEEP else m.group(1).lower(), t)
    t = _fix_spacing(t)
    # sentence-initial capital after the repairs above
    t = _S_SENTCAP.sub(lambda m: m.group(1) + m.group(2).upper(), t)
    return t


# Trailing OCR marker junk on an option: "Baricitinib %", "Endoscopy %",
# "Carotid duplex ultrasound asK", "Vascular Parkinsonism oe".
_OPT_TAIL = re.compile(
    r"(?:\s+(?:ox|ax|om|oe|ne|wm|nw|as[A-Z]|o%|n%|[A-Za-z]?%|\d+x|[A-Za-z]\d))+\s*$"
    r"|\s*[\u2122\u00a9\u00ae%\uff0b+*]+\s*$"
)


def clean_option(opt):
    """Repair one option string. The 'A) ' prefix is preserved."""
    if not opt:
        return opt
    m = re.match(r"^\s*([A-Ea-e])[\)\.]\s*(.*)$", opt, re.S)
    prefix, body = (m.group(1).upper() + ") ", m.group(2)) if m else ("", opt)
    prev = None
    while prev != body:
        prev = body
        body = _OPT_TAIL.sub("", body).rstrip(" .,")
    body = clean_text(body)
    if body and body[0].islower() and not re.match(r"^[a-z]?[A-Z]", body):
        body = body[0].upper() + body[1:]
    return prefix + body


# ---------------------------------------------------------------------------
# 3. Unservable questions
# ---------------------------------------------------------------------------

# A stem with no clinical content: the vignette was in an image the OCR could
# not read, leaving only the lead-in. Detected rather than listed, so newly
# imported banks are covered too.
_STOP = set(
    "which one of the following is are was were most likely appropriate next "
    "best step in this patient patient's management diagnosis treatment "
    "initial would be to a an and for his her their about plan".split()
)


def _is_hollow(stem):
    t = (stem or "").strip()
    if len(t) > 150:
        return False
    words = [w for w in re.findall(r"[A-Za-z][A-Za-z\-']+", t.lower())
             if w not in _STOP and len(w) > 3]
    return len(words) <= 1


def _option_bodies(opts):
    return [re.sub(r"^\s*[A-Ea-e][\)\.]\s*", "", o or "").strip() for o in opts]


def _has_blank_option(opts):
    return any(not b for b in _option_bodies(opts))


# Questions whose CORRECT answer OCR'd into unrecoverable garbage. Hand-checked
# one by one; every one of these was verified to be unanswerable as stored.
# (bank, index)
BROKEN = {
    "UQ Critical Care Module :: EMED - Cardiology - Hypertension (MCQ)": [27],
    "UQ Critical Care Module :: EMED - Cardiology - Cardiac Arrhythmia (MCQ)": [12],
    "UQ Critical Care Module :: EMED - Cardiology - Valvular Heart Disease (MCQ)": [3],
    "UQ Critical Care Module :: EMED - Dermatology - Rashes / Other Dermatoses (MCQ)": [0, 45],
    "UQ Critical Care Module :: EMED - Dermatology - Melanoma (MCQ)": [0],
    "UQ Critical Care Module :: EMED - Endocrinology - Thyroid - Hyperthyroidism / Graves (MCQ)": [5, 8],
    "UQ Critical Care Module :: EMED - Endocrinology - Calcium / Parathyroid (MCQ)": [3],
    "UQ Critical Care Module :: EMED - Endocrinology - Thyroid Nodule / Cancer (MCQ)": [4],
    "UQ Critical Care Module :: EMED - Endocrinology - Adrenal - Addison / Insufficiency (MCQ)": [5],
    "UQ Critical Care Module :: EMED - Gynaecology - Cervical Screening / Cancer (MCQ)": [5],
    "UQ Critical Care Module :: EMED - Haematology - Anaemia (MCQ)": [25],
    "UQ Critical Care Module :: EMED - Hepatology - Alcoholic Liver Disease / Cirrhosis (MCQ)": [17],
    "UQ Critical Care Module :: EMED - Infectious Disease - Gastroenteritis / Food Poisoning (MCQ)": [6],
    "UQ Critical Care Module :: EMED - Gastroenterology - Inflammatory Bowel Disease (MCQ)": [6],
    "UQ Critical Care Module :: EMED - Neurology - Dementia (MCQ)": [10],
    "UQ Critical Care Module :: EMED - Neurology - Parkinson Disease (MCQ)": [9],
    "UQ Critical Care Module :: EMED - Psychiatry - Depression (MCQ)": [17],
    # index 0 is the raw OCR of the same TBI vignette that index 7 already
    # carries in clean, Australianised form ("B) head" vs "B) CT head").
    "UQ Critical Care Module :: EMED - Neurology - Traumatic Brain Injury (MCQ)": [0],
}

# Options that ARE recoverable with certainty — the ASA ladders and one
# truncated infectious-disease answer. Whole option list, replacing the stored one.
OPTION_FIXES = {
    "UQ Critical Care Module :: EMED - Obstetrics - General Obstetrics (MCQ)": {
        0: ["A) ASA I", "B) ASA II", "C) ASA III", "D) ASA IV", "E) ASA V"],
    },
    "UQ Critical Care Module :: EMED - Respiratory - COPD (MCQ)": {
        8: ["A) ASA I", "B) ASA II", "C) ASA III", "D) ASA IV", "E) ASA V"],
    },
    "UQ Critical Care Module :: EMED - Respiratory - Tuberculosis (MCQ)": {
        5: ["A) Legionnaires' disease",
            "B) Middle East respiratory syndrome",
            "C) Brucellosis",
            "D) Tuberculosis",
            "E) Q fever"],
    },
}


# ---------------------------------------------------------------------------
# 4. Entry point
# ---------------------------------------------------------------------------

# The source's own take-home points survived the scan as a lone quote glyph —
# it is what the emedici lightbulb bullet OCR'd to:
#     "...and decreased appetite. ' Management of cannabis withdrawal is..."
# Recover them as real bullets so the renderer can lift them into the Key
# Points panel instead of burying them in the last paragraph.
# The emedici take-home bullet is a small lightbulb icon. The scan resolved it
# to whatever glyph it looked most like, which turns out to be a handful:
#     "@" 850x   "Q" 794x   "©" 126x   "'" 83x   "G", "®", "°"
# All of them mean the same thing: a new take-home point starts here. A/I/X are
# deliberately NOT markers (real sentences start "A 40-year-old...", "X-ray..."),
# and "Q" is excluded before "fever" so Q fever survives.
# The emedici take-home bullet is a small lightbulb icon, and the scan resolved
# it to whatever glyph it happened to look like. Across the banks that is:
#     @ 767   Q 745   'Q 315   © 285   '@ 221   Y 206   9 180   '9 145   'Y 111
# plus G, ®, ° — often with a stray quote glyph in front. All of them mean the
# same thing: a new take-home point starts here.
#
# A/I/X are deliberately NOT markers (real sentences open "A 40-year-old...",
# "X-ray shows..."), "Q fever" is excluded, and a digit marker is ignored when
# it is really an enumeration ("Figure 2 Shows...", "Grade 2 Retinopathy").
_MARKER = re.compile(
    r"(?P<punct>[\.\,;:])?\s+[\u2018\u2019\u201c\u201d']?"
    r"(?P<m>[@\u00a9\u00ae\u00b0\u25cf\u25aa]|[QGY](?!\s*[Ff]ever)|[92])"
    r"\s+(?=[A-Z][a-z]{2,})"
)
_ENUM_CONTEXT = re.compile(
    r"\b(?:figure|fig|table|image|step|grade|type|stage|phase|class|point|option"
    r"|answer|day|week|month|year|level|line|part|section|item|no|number)\W*$",
    re.I,
)


def _mark_bullets(text):
    """Replace every take-home marker glyph with \\x01 at the start of a line."""
    out, last = [], 0
    for m in _MARKER.finditer(text):
        if m.group("m").isdigit() and _ENUM_CONTEXT.search(text[max(0, m.start() - 14):m.start()]):
            continue
        out.append(text[last:m.start()])
        out.append((m.group("punct") or ".") + "\n\x01")
        last = m.end()
    out.append(text[last:])
    return "".join(out)


_KP_LEAD = re.compile(
    r"^\s*[\u2018\u2019\u201c\u201d']?"
    r"(?:[@\u00a9\u00ae\u00b0\u25cf\u25aa]|[QGY](?!\s*[Ff]ever))\s+(?=[A-Z])"
)
_ORPHAN_QUOTE = re.compile(r"(?:(?<=\s)|^)[\u2018\u201c](?=\s)")

# In-body lists ("* Optional coverage - ...  + Required only for ... ") are run
# together into the paragraph by the scan. Lift them onto their own lines.
# Marked with "* ", NOT "- ": the renderer treats "- " lines as the take-home
# points, and a distractor list must not be mistaken for one.
_BODY_BULLET = re.compile(r"(?<=[\w\.\,\)])\s+[\*\+\u2022]\s+(?=[A-Z])")


def split_explanation(text):
    """-> (cleaned body, [recovered take-home points])

    Two different things in these banks look like a bullet, and conflating them
    is what puts "Antibiotics are not indicated" in the key points:

      * A bullet the OCR *recovered* from the lightbulb icon (@ / Q / © / ').
        These ARE the author's take-home points.
      * A bullet that was already "- " in the source. In the EXTRA banks those
        are the option-by-option critique — useful in the body, useless as a
        thing to remember.

    So the recovered ones are tagged with \\x01 (a char that cannot occur in the
    text) and pulled out before the body is cleaned; native "- " lines are left
    where they are.
    """
    raw = str(text or "")
    if not raw:
        return "", []
    t = _mark_bullets(raw)
    t = "\n".join(_KP_LEAD.sub("\x01", l) for l in t.split("\n"))
    t = _BODY_BULLET.sub("\n* ", t)
    t = _ORPHAN_QUOTE.sub("", t)
    lines = t.split("\n")
    kps = [l[1:].strip() for l in lines if l.startswith("\x01")]
    body = "\n".join(l for l in lines if not l.startswith("\x01"))
    return clean_text(body), [clean_text(k) for k in kps]


def clean_explanation(text):
    """The explanation body alone (take-home points removed)."""
    return split_explanation(text)[0]


# --- Key points ------------------------------------------------------------
# Only ~140 of 2,459 questions carry take-home points (36 in the bank, ~107
# recovered from the OCR'd bullet glyph). The rest have to be derived, and the
# explanations are formulaic enough to derive them from:
#
#   "The correct answer is X. <why>.  The incorrect options can be explained:
#    * distractor - why not  * distractor - why not
#    <closing paragraph of general principle>"
#
# The two things worth remembering are the OPENING claim and the CLOSING
# principle. The distractor list in between is scaffolding for this question
# only, so it is deliberately excluded.

_SENT_SPLIT = re.compile(r"(?<=[.!?])\s+(?=[A-Z(])")
_LEAD_IN = re.compile(
    r"^(?:the\s+)?correct\s+answer\s+is\s+(?:that\s+|option\s+[A-E][\)\.:,]?\s*|[A-E][\)\.:,]\s*)?",
    re.I,
)
_DISTRACTOR_CUE = re.compile(
    r"incorrect option|other options|remaining options|are incorrect|is incorrect"
    r"|would be inappropriate|not the (?:best|correct|most|first)"
    r"|(?:is|are) not indicated|(?:is|are) not appropriate|(?:is|would) not be"
    r"|not required|not necessary|does not address|would be premature",
    re.I,
)
# "Optimise sedation depth and adjust ventilator settings - optimising sedation
# is the first-line management for dyssynchrony."  An option quoted back, then
# adjudicated. Body material, not something to remember. A spaced em/en dash is
# the tell; "first-line" and other real hyphenates are never spaced.
_OPTION_CRITIQUE = re.compile(r"\s[\u2014\u2013]\s|^.{3,90}?\s-\s\S")
# A sentence that teaches something generalisable, rather than restating this
# particular vignette.
_TEACHING_CUE = re.compile(
    r"\b(?:should|must|first[- ]line|gold standard|mainstay|always|never|typically"
    r"|indicat\w+|suggest\w+|requir\w+|is defined|are defined|is associated"
    r"|risk of|management|treatment|diagnos\w+ is|characteris\w+|key\b|hallmark"
    r"|guideline|recommend\w+|contraindicat\w+|complication)\b",
    re.I,
)
# A sentence that just recaps the stem back at you.
_RECAP_CUE = re.compile(
    r"^(?:this (?:patient|case|man|woman|child|scenario)|the patient (?:is|has|presents)"
    r"|he |she )",
    re.I,
)
_KP_MIN = 40
_KP_MAX = 260


def _tidy_point(s):
    # clean_text() again: a point may come from a bank's own
    # key_learning_points field, which has never been through the repair pass.
    s = clean_text(str(s or "")).strip()
    s = _LEAD_IN.sub("", s).strip(" -*\u2013\u2014")
    if not s:
        return ""
    s = s[:1].upper() + s[1:]
    if s[-1] not in ".!?":
        s += "."
    return s


def _sentences(block):
    return [s.strip() for s in _SENT_SPLIT.split(block) if s.strip()]


def _looks_like_critique(point, opt_heads):
    """True if this 'take-home point' is really an option being knocked down.

    The lightbulb marker is not used exclusively for take-homes — in some
    questions the same glyph precedes the option-by-option rationale. The
    reliable tell is that the line OPENS with one of this question's own
    options ("Cranial X-ray would delay definitive management...").
    """
    if _DISTRACTOR_CUE.search(point) or _OPTION_CRITIQUE.search(point):
        return True
    head = " ".join(re.findall(r"[a-z]+", point.lower())[:3])
    return bool(head) and head in opt_heads


def derive_key_points(body, recovered=None, options=None):
    """Take-home points for one explanation. `recovered` wins if non-empty."""
    opt_heads = set()
    for o in (options or []):
        words = re.findall(r"[a-z]+", re.sub(r"^\s*[A-Ea-e][\)\.]\s*", "", o).lower())
        if len(words) >= 2:
            opt_heads.add(" ".join(words[:3]))

    if recovered:
        pts = [p for p in (_tidy_point(b) for b in recovered)
               if len(p) >= _KP_MIN and not _looks_like_critique(p, opt_heads)]
        if pts:
            return pts[:4]
    if not body:
        return []

    # Fall back to the prose. Every bullet line is skipped — in these banks a
    # bullet is an option critique, which teaches nothing once you leave the
    # question. Score what is left on how much it generalises.
    sents = _sentences(" ".join(
        l for l in body.split("\n") if not l.lstrip().startswith(("*", "-", "\u2022"))
    ).strip())
    if not sents:
        return []

    scored = []
    n = len(sents)
    for i, s in enumerate(sents):
        if _DISTRACTOR_CUE.search(s) or _OPTION_CRITIQUE.search(s):
            continue
        p = _tidy_point(s)
        if not (_KP_MIN <= len(p) <= _KP_MAX):
            continue
        score = 0
        if _TEACHING_CUE.search(p):
            score += 3
        if i >= n * 0.6:            # the closing principle
            score += 2
        if i == 0:                  # names the answer
            score += 2
        if _RECAP_CUE.match(p):     # just restates the vignette
            score -= 3
        scored.append((score, i, p))

    if not scored:
        return []
    best = sorted(scored, key=lambda x: (-x[0], x[1]))[:3]
    seen, out = set(), []
    for _, i, p in sorted(best, key=lambda x: x[1]):
        k = p.lower()[:60]
        if k not in seen:
            seen.add(k)
            out.append(p)
    return out


# Some stems lost their leading article to the scan entirely:
#     "72-year-old man presents to his GP with..."
_BARE_AGE = re.compile(r"^(\d{1,3})(-year-old|-month-old|-week-old|-day-old)\b")


def _restore_stem_article(stem):
    m = _BARE_AGE.match(stem or "")
    if not m:
        return stem
    art = "An" if m.group(1)[0] == "8" or m.group(1) in ("11", "18") else "A"
    return f"{art} {stem}"


def clean_question(q):
    """Repair one question dict. Returns a NEW dict; the original is untouched."""
    q = dict(q)
    q["question_text"] = _restore_stem_article(clean_text(q.get("question_text", "")))
    q["options"] = [clean_option(o) for o in (q.get("options") or [])]

    body, recovered = split_explanation(q.get("explanation", ""))

    # A key_learning_points value already in the bank always wins.
    existing = q.get("key_learning_points")
    if existing:
        parts = (re.split(r"\n+|(?:^|\s)[\*\u2022]\s+", existing)
                 if isinstance(existing, str) else [str(x) for x in existing])
        pts = [p for p in (_tidy_point(x) for x in parts) if p]
    else:
        pts = derive_key_points(body, recovered, q["options"])

    q["explanation"] = body
    q["key_learning_points"] = pts
    return q


def clean_banks(banks, quarantine=None, stats=None):
    """Repair every EMED bank, then drop the unservable questions.

    IMPORTANT — this does the dropping for the WHOLE pipeline, including the
    existing QUARANTINE list from emed_stem_overrides. Every index (QUARANTINE,
    BROKEN, OPTION_FIXES, and the STEM/ANSWER/OPTION overrides applied upstream)
    is an index into the *unfiltered* bank. Filter in two places and the second
    set of indices points at the wrong questions. So: fix everything first,
    take one union of everything to drop, filter once.

        EMED_BANKS = clean_banks(EMED_BANKS, quarantine=QUARANTINE)

    `stats` — pass a dict to receive counts (handy in the debug panel).
    """
    quarantine = quarantine or {}
    dropped = hollow_n = blank_n = 0
    out = {}
    for bank, questions in banks.items():
        drop = set(int(x) for x in quarantine.get(bank, []))
        drop |= set(BROKEN.get(bank, []))
        fixes = OPTION_FIXES.get(bank, {})
        kept = []
        for i, q in enumerate(questions):
            if i in drop:
                dropped += 1
                continue
            if i in fixes:
                q = dict(q)
                q["options"] = list(fixes[i])
            q = clean_question(q)
            # Judge servability on the CLEANED text: "D) %" only becomes a
            # blank option once the trailing OCR marker is stripped.
            if _is_hollow(q.get("question_text")):
                hollow_n += 1
                dropped += 1
                continue
            if _has_blank_option(q.get("options") or []):
                blank_n += 1
                dropped += 1
                continue
            kept.append(q)
        out[bank] = kept
    if stats is not None:
        stats.update(dropped=dropped, hollow=hollow_n, blank=blank_n,
                     kept=sum(len(v) for v in out.values()))
    return out
