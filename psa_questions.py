# ─────────────────────────────────────────────────────────────────────────────
#  psa_questions.py  —  Prescribing Safety Assessment item bank
# ─────────────────────────────────────────────────────────────────────────────
#  This file holds every PSA item. The interface (psa.py) reads PSA_QUESTIONS
#  and renders + marks each item according to its `type`.
#
#  Blueprint reference (marks per style):
#    PWS  Prescribing            10 marks  (5 drug + 5 dose/route/freq)
#    REV  Prescription Review     4 marks  (2 questions × 2)
#    MAN  Planning Management     2 marks  (single best of 5)
#    COM  Providing Information   2 marks  (single best of 5)
#    CAL  Calculation Skills      2 marks  (numeric answer)
#    ADR  Adverse Drug Reactions  2 marks  (single best of 5; subtypes A–D)
#    TDM  Drug Monitoring         2 marks  (single best of 5)
#    DAT  Data Interpretation     2 marks  (single best of 5)
#
#  SETTINGS:  MED  SURG  ELD  PED  PSYCH  O&G  GP
#
# ─────────────────────────────────────────────────────────────────────────────
#  SCHEMA  —  every item shares these keys:
#
#    "id":        unique string, e.g. "PWS-001"
#    "type":      one of PWS REV MAN COM CAL ADR TDM DAT
#    "setting":   one of MED SURG ELD PED PSYCH O&G GP
#    "diagnosis": free text (Appendix IV label is fine)
#    "age":       int        "sex": "M" | "F"
#    "stem": {                     # any subset; rendered in this order
#        "case_presentation": "...",
#        "on_examination":    "...",
#        "investigations":    "...",
#    },
#    "lead_in":   the request shown in the highlighted box
#
#  Then, per type:
#
#  ── PWS ──────────────────────────────────────────────────────────────────────
#    "form_type":  "general practice" | "once-only medicines"
#                  | "regular medicines" | "hospital IV fluid"
#    "drug_set":   [ {"name": "...", "score": 0-5}, ... ]   # drug-choice marks
#    "optimal":    {"dose": "200 micrograms", "route": "INH",
#                   "frequency": "twice daily (12-hrly)"}
#    "duration":   "28 days"          # GP forms only (optional)
#    "model_answer": "single best full prescription string"
#    "justification": "why this is the answer"
#
#  ── REV ──────────────────────────────────────────────────────────────────────
#    "prescriptions": [ {"medicine","dose","route","frequency"}, ... ]   # 6–10
#    "question_a":  {"prompt","n_select", "correct": [idx,...]}   # 0-based idx
#    "question_b":  {"prompt","n_select", "correct": [idx,...]}
#    "justification_a": "...", "justification_b": "..."
#
#  ── MAN / COM / ADR / TDM / DAT (single-best-answer) ──────────────────────────
#    "options":        [ "opt a", "opt b", "opt c", "opt d", "opt e" ]   # 5
#    "correct":        idx (0-based)
#    "justifications": [ "...", "...", "...", "...", "..." ]   # one per option
#    "adr_subtype":    "A" | "B" | "C" | "D"      # ADR only (optional)
#
#  ── CAL ──────────────────────────────────────────────────────────────────────
#    "answer":    float       "unit": "mL"
#    "tolerance": 0.01        # acceptable +/- around answer
#    "working":   "shown after submission"
# ─────────────────────────────────────────────────────────────────────────────

PSA_QUESTIONS = {

    # ═══════════════════════════════════════════════════════════════════════════
    "PWS": [
        {
            "id": "PWS-001",
            "type": "PWS",
            "setting": "GP",
            "diagnosis": "Hypersensitivity/allergy",
            "age": 19, "sex": "M",
            "stem": {
                "case_presentation": (
                    "A 19-year-old man presents to his GP with worsening breathlessness "
                    "and a nocturnal cough. PMH. Eczema, allergic rhinitis, "
                    "exercise-induced wheeze. DH. Clobetasone butyrate 0.05% TOP to joint "
                    "flexures 12-hrly, salbutamol 200 micrograms INH as required."
                ),
                "on_examination": (
                    "Temperature 37.0°C, HR 115/min and rhythm regular, BP 126/82 mmHg, "
                    "RR 24/min, O2 sat 97% breathing air. Able to talk in complete "
                    "sentences. Wheeze on auscultation. PEFR 430 L/min (60% of expected)."
                ),
                "investigations": (
                    "He is found to have a high probability of asthma and booked into the "
                    "respiratory clinic for closely-controlled monitoring of symptoms and a "
                    "series of lung function tests."
                ),
            },
            "lead_in": (
                "Write a prescription for ONE drug that is most appropriate to prevent his "
                "nocturnal symptoms.\n(use the general practice prescription form provided)"
            ),
            "form_type": "general practice",
            "drug_set": [
                {"name": "beclometasone dipropionate",        "score": 5},
                {"name": "budesonide",                        "score": 5},
                {"name": "fluticasone propionate",            "score": 5},
                {"name": "ciclesonide",                       "score": 4},
                {"name": "mometasone furoate",                "score": 4},
                {"name": "formoterol/budesonide",             "score": 3},
                {"name": "salmeterol/fluticasone propionate", "score": 3},
                {"name": "aminophylline",                     "score": 2},
                {"name": "zafirlukast",                        "score": 2},
                {"name": "sodium cromoglicate",               "score": 1},
                {"name": "prednisolone",                      "score": 0},
                {"name": "salbutamol",                        "score": 0},
            ],
            "optimal": {"dose": "200 micrograms", "route": "INH",
                        "frequency": "twice daily (12-hrly)"},
            "duration": "28 days",
            "model_answer": "beclometasone dipropionate 200 micrograms INH twice daily (12-hrly)",
            "justification": (
                "Poorly controlled asthma (nocturnal symptoms, reliever use, reduced PEFR) "
                "warrants a regular inhaled corticosteroid as a preventer. A short-acting "
                "beta2-agonist alone does not control underlying inflammation, and systemic "
                "steroids are not first-line maintenance."
            ),
        },
    ],

    # ═══════════════════════════════════════════════════════════════════════════
    "REV": [
        {
            "id": "REV-001",
            "type": "REV",
            "setting": "MED",
            "diagnosis": "Cardiology symptoms/signs",
            "age": 57, "sex": "M",
            "stem": {
                "case_presentation": (
                    "A 57-year-old man is admitted to hospital with a lower respiratory "
                    "tract infection, which is worsening despite commencing a course of "
                    "antibiotics. He also reports having a sore mouth. PMH. COPD, ischaemic "
                    "heart disease. DH. In addition to clarithromycin 500 mg PO 12-hrly "
                    "(day 4 of a 7-day course), his current regular medicines are listed."
                ),
                "on_examination": "HR 110/min and rhythm regular.",
            },
            "lead_in": "Review the current prescription and answer both questions below.",
            "prescriptions": [
                {"medicine": "amoxicillin",                "dose": "500 mg",         "route": "oral (PO)",     "frequency": "three times daily (8-hrly)"},
                {"medicine": "aspirin",                    "dose": "75 mg",          "route": "oral (PO)",     "frequency": "daily"},
                {"medicine": "beclometasone dipropionate", "dose": "200 micrograms", "route": "inhaled (INH)", "frequency": "twice daily (12-hrly)"},
                {"medicine": "furosemide",                 "dose": "40 mg",          "route": "oral (PO)",     "frequency": "daily"},
                {"medicine": "isosorbide mononitrate m/r", "dose": "30 mg",          "route": "oral (PO)",     "frequency": "twice daily (as directed)"},
                {"medicine": "ramipril",                   "dose": "5 mg",           "route": "oral (PO)",     "frequency": "daily"},
                {"medicine": "salmeterol",                 "dose": "50 micrograms",  "route": "inhaled (INH)", "frequency": "twice daily (12-hrly)"},
                {"medicine": "theophylline m/r (Nuelin SA)", "dose": "350 mg",       "route": "oral (PO)",     "frequency": "twice daily (12-hrly)"},
            ],
            "question_a": {
                "prompt": "Select the TWO prescriptions that are most likely to be a cause of his sore mouth.",
                "n_select": 2,
                "correct": [0, 2],
            },
            "question_b": {
                "prompt": "Select the ONE prescription that is most likely to interact with clarithromycin to cause tachycardia.",
                "n_select": 1,
                "correct": [7],
            },
            "justification_a": (
                "Inhaled corticosteroids (beclometasone) predispose to oral candidiasis, and "
                "broad-spectrum antibiotics (amoxicillin) can cause candidal overgrowth — both "
                "present as a sore mouth."
            ),
            "justification_b": (
                "Clarithromycin inhibits theophylline metabolism, raising plasma theophylline "
                "concentrations and causing toxicity, including tachycardia."
            ),
        },
    ],

    # ═══════════════════════════════════════════════════════════════════════════
    "MAN": [
        {
            "id": "MAN-001",
            "type": "MAN",
            "setting": "ELD",
            "diagnosis": "Infections of respiratory tract",
            "age": 70, "sex": "F",
            "stem": {
                "case_presentation": (
                    "A 70-year-old woman is admitted to hospital with worsening "
                    "breathlessness and a cough productive of green sputum. PMH. "
                    "Hypertension. DH. Amlodipine 5 mg PO daily, salbutamol 200 micrograms "
                    "INH as required, amoxicillin 500 mg PO 8-hrly for 5 days. SH. "
                    "Long-standing smoker."
                ),
                "on_examination": (
                    "Temperature 36.8°C, HR 96/min and rhythm regular, BP 170/92 mmHg, "
                    "RR 22/min, O2 sat 96% breathing air. Widespread expiratory wheeze."
                ),
                "investigations": (
                    "CXR shows hyper-expansion of the lung fields and some old scarring at "
                    "the left apex."
                ),
            },
            "lead_in": "Select the most appropriate management option at this stage.",
            "options": [
                "atenolol 50 mg PO",
                "furosemide 50 mg IV",
                "hydrocortisone 100 mg IV",
                "oxygen 35% via venturi mask",
                "salbutamol 5 mg NEB",
            ],
            "correct": 4,
            "justifications": [
                "No indication; would worsen reversible airways obstruction and is relatively contra-indicated in the acute setting.",
                "No evidence of fluid overload or pulmonary oedema.",
                "A short course of oral corticosteroid is indicated; IV is unnecessary for an exacerbation of this severity.",
                "Oxygen at this concentration is potentially hazardous, and saturations are adequate.",
                "Infective exacerbation of COPD with widespread wheeze — a nebulised bronchodilator relieves bronchospasm.",
            ],
        },
    ],

    # ═══════════════════════════════════════════════════════════════════════════
    "COM": [
        {
            "id": "COM-001",
            "type": "COM",
            "setting": "SURG",
            "diagnosis": "Coagulation disorders",
            "age": 36, "sex": "M",
            "stem": {
                "case_presentation": (
                    "A 36-year-old man is assessed on the medical admissions unit for a "
                    "suspected DVT in his left calf following recent orthopaedic surgery to "
                    "his knee. DH. Enoxaparin sodium 100 mg SC daily (commenced on arrival). "
                    "A Doppler ultrasound scan confirms a DVT in the lower left leg. He is "
                    "advised to take warfarin sodium 3 mg PO daily for 3 months."
                ),
            },
            "lead_in": "Select the most important information option that should be provided for the patient.",
            "options": [
                "warfarin sodium 3 mg tablets are blue",
                "warfarin sodium is better tolerated if taken in the evening",
                "warfarin sodium therapy reduces the risk of a second DVT",
                "warfarin sodium may increase his likelihood of bleeding",
                "weekly blood tests will be required throughout treatment",
            ],
            "correct": 3,
            "justifications": [
                "True (colour-coding aids dose recognition) but not the most important safety message.",
                "Reasonable for adherence, but the time of day does not materially affect tolerability.",
                "True, but warning about bleeding risk is more important to convey.",
                "Warfarin carries a significant bleeding risk, reduced by regular INR monitoring — the key safety message.",
                "Frequent tests are needed early, but become less frequent once the INR is stable; not the most important point.",
            ],
        },
    ],

    # ═══════════════════════════════════════════════════════════════════════════
    "CAL": [
        {
            "id": "CAL-001",
            "type": "CAL",
            "setting": "PED",
            "diagnosis": "Neurology symptoms/signs",
            "age": 0, "sex": "M",
            "stem": {
                "case_presentation": (
                    "A 2-month-old boy in the paediatric emergency department requires a "
                    "dose of midazolam to be administered buccally for status epilepticus. "
                    "The dose of buccal midazolam is 300 microgram/kg (max 2.5 mg), repeated "
                    "once if necessary after 10 minutes. Weight 5.0 kg. Midazolam oromucosal "
                    "solution is available as a 5 mg/mL solution."
                ),
            },
            "lead_in": "What volume (mL) of midazolam oromucosal solution should the patient be given for the first dose?",
            "answer": 0.3,
            "unit": "mL",
            "tolerance": 0.01,
            "working": (
                "Dose = 300 micrograms × 5 kg = 1500 micrograms (1.5 mg). "
                "Concentration = 5 mg/mL. Volume = 1.5 / 5 = 0.3 mL."
            ),
        },
    ],

    # ═══════════════════════════════════════════════════════════════════════════
    "ADR": [
        {
            "id": "ADR-001",
            "type": "ADR",
            "setting": "ELD",
            "diagnosis": "Oncology symptoms/signs",
            "age": 67, "sex": "M",
            "adr_subtype": "A",
            "stem": {
                "case_presentation": (
                    "A 67-year-old man has started to take morphine sulfate 10 mg PO 4-hrly "
                    "for pain associated with a gastric carcinoma."
                ),
            },
            "lead_in": "Select the adverse effect that is most likely to be caused by this treatment.",
            "options": [
                "diarrhoea",
                "drowsiness",
                "palpitations",
                "pruritis",
                "sweating",
            ],
            "correct": 1,
            "justifications": [
                "Morphine causes constipation, not diarrhoea.",
                "Morphine acts on opioid receptors to depress neurotransmission and commonly causes drowsiness.",
                "Palpitations are not a common opioid effect.",
                "Itching can follow opioid use but is much less common than drowsiness.",
                "Sweating can occur but is far less common than drowsiness as an adverse effect.",
            ],
        },
    ],

    # ═══════════════════════════════════════════════════════════════════════════
    "TDM": [
        {
            "id": "TDM-001",
            "type": "TDM",
            "setting": "ELD",
            "diagnosis": "Bacterial infection",
            "age": 71, "sex": "F",
            "stem": {
                "case_presentation": (
                    "A 71-year-old woman is admitted to the respiratory ward with severe "
                    "community-acquired pneumonia. She has been coughing up thick green "
                    "sputum for 2 days."
                ),
                "on_examination": (
                    "Temperature 36.8°C, RR 20/min. Dullness to percussion and crackles at "
                    "the right lung base."
                ),
                "investigations": (
                    "CXR confirms right lower lobe pneumonia. Treatment with co-amoxiclav "
                    "(amoxicillin 1 g/clavulanic acid 200 mg) 1.2 g IV 8-hrly is initiated."
                ),
            },
            "lead_in": "Select the most appropriate option to monitor for beneficial effects of this prescription within the first 3 days of treatment.",
            "options": [
                "chest auscultation",
                "chest X-ray",
                "heart rate",
                "respiratory rate",
                "review of sputum colour",
            ],
            "correct": 3,
            "justifications": [
                "Auscultatory findings take several days to resolve.",
                "Radiographic appearance is unlikely to resolve in the early stages of treatment.",
                "Heart rate is not a good indicator of treatment success.",
                "Successful treatment improves gas exchange and reduces the respiratory rate — an early, objective marker.",
                "Sputum colour is a poor guide to the success of treatment for pneumonia.",
            ],
        },
    ],

    # ═══════════════════════════════════════════════════════════════════════════
    "DAT": [
        {
            "id": "DAT-001",
            "type": "DAT",
            "setting": "ELD",
            "diagnosis": "Neurology symptoms/signs",
            "age": 72, "sex": "M",
            "stem": {
                "case_presentation": (
                    "A 72-year-old man is admitted to hospital with epileptic seizures that "
                    "have been increasing in frequency. PMH. Epilepsy following a head "
                    "injury sustained 5 weeks previously. He was discharged 4 weeks ago "
                    "taking phenytoin sodium capsules 200 mg PO daily, but switched 2 weeks "
                    "ago when he was able to tolerate liquids. His wife confirms excellent "
                    "adherence to his phenytoin."
                ),
                "investigations": (
                    "serum phenytoin (3 weeks ago) 45 µmol/L (40–80), "
                    "serum phenytoin (now) 32 µmol/L (40–80)."
                ),
            },
            "lead_in": "Select the most appropriate decision option with regard to the phenytoin sodium prescription based on these data.",
            "options": [
                "discontinue phenytoin sodium",
                "phenytoin sodium 200 mg PO daily",
                "phenytoin sodium 250 mg PO daily",
                "phenytoin sodium 300 mg PO daily",
                "phenytoin sodium 400 mg PO daily",
            ],
            "correct": 2,
            "justifications": [
                "There is no reason to discontinue phenytoin treatment.",
                "Concentration is sub-therapeutic and will keep falling unless the dose is increased.",
                "100 mg of phenytoin sodium is approximately equivalent to 92 mg phenytoin base; a cautious dose increase with careful monitoring is appropriate when switching from liquid to tablets.",
                "A 50% increase to 300 mg daily is likely to be too much, risking toxicity.",
                "A 100% increase to 400 mg daily is likely to be too much, risking toxicity.",
            ],
        },
    ],
}
