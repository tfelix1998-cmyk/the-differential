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

    "ICU & Respiratory (ARDS) — Bank 1": [
        {
            "question_text": "A 23 year old male with a history of severe acute respiratory distress syndrome (ARDS) secondary to bacterial pneumonia is being managed in the intensive care unit. Despite optimal mechanical ventilation settings and neuromuscular blockade, his oxygenation remains poor with a PaO2/FiO2 ratio of 80 mmHg. The decision is made to place the patient in the prone position. What is the primary physiological rationale for this intervention?",
            "options": [
                "A) To enhance the clearance of respiratory secretions",
                "B) To reduce the risk of ventilator-associated pneumonia",
                "C) To decrease the work of breathing and respiratory muscle fatigue",
                "D) To increase the functional residual capacity and improve V/Q matching",
            ],
            "correct_answer_letter": "D",
            "explanation": "Prone positioning in patients with severe ARDS recruits collapsed alveoli in the dependent (posterior) regions of the lungs. This leads to a more homogeneous distribution of ventilation, increases functional residual capacity, and matches ventilation to the persistent perfusion of dorsal lung regions, thereby improving ventilation-perfusion (V/Q) matching and reducing intrapulmonary shunt.",
            "key_learning_points": "Prone positioning in severe ARDS improves oxygenation primarily by recruiting dependent dorsal lung regions, increasing functional residual capacity, and optimizing ventilation-perfusion matching.",
            "image_url": "",
        },
        {
            "question_text": "A 24 year old male presents to the emergency department following a high-speed motor vehicle collision. He sustained multiple fractures and a flail chest. On examination, he is tachypneic, hypoxic, and demonstrates decreased breath sounds on the left side. A chest X-ray reveals bilateral pulmonary infiltrates. He is intubated and mechanically ventilated due to worsening respiratory failure. Despite optimal fluid management and supportive care, his oxygenation does not improve significantly. Which of the following interventions is most likely to reduce mortality with trauma-related acute respiratory distress syndrome (ARDS)?",
            "options": [
                "A) Immediate administration of high-dose corticosteroids",
                "B) Initiation of inhaled nitric oxide therapy",
                "C) Lung-protective ventilation strategies",
                "D) Aggressive fluid resuscitation with crystalloids",
            ],
            "correct_answer_letter": "C",
            "explanation": "Lung-protective ventilation strategies, which involve using low tidal volumes (6 mL/kg of predicted body weight) and keeping plateau airway pressures below 30 cm H2O, have been shown to reduce mortality in patients with ARDS. This approach minimizes ventilator-induced lung injury (VILI) such as volutrauma and barotrauma.",
            "key_learning_points": "Lung-protective ventilation with low tidal volumes reduces mortality in patients with ARDS by minimizing ventilator-induced lung injury.",
            "image_url": "",
        },
        {
            "question_text": "A 24 year old woman is admitted to the intensive care unit with severe dyspnoea, hypoxaemia, and bilateral pulmonary infiltrates on chest X-ray. She has a history of systemic lupus erythematosus and recently underwent a caesarean section due to preeclampsia. She is diagnosed with acute respiratory distress syndrome (ARDS). Which of the following pathophysiological mechanisms is primarily responsible for the hypoxaemia observed?",
            "options": [
                "A) Decreased alveolar ventilation",
                "B) Ventilation-perfusion mismatch",
                "C) Right-to-left cardiac shunt",
                "D) Hypoventilation due to respiratory muscle fatigue",
            ],
            "correct_answer_letter": "B",
            "explanation": "In ARDS, alveolar flooding and atelectasis lead to non-ventilated alveoli that continue to be perfused. This severe ventilation-perfusion (V/Q) mismatch (specifically, an intrapulmonary shunt) is the primary pathophysiological mechanism responsible for the hypoxemia.",
            "key_learning_points": "The primary mechanism of hypoxemia in ARDS is intrapulmonary shunt, which represents a severe form of ventilation-perfusion (V/Q) mismatch.",
            "image_url": "",
        },
        {
            "question_text": "A 43 year old male with a history of hypertension and diabetes presents to the emergency department with a one-week history of fever, cough, and progressive shortness of breath. He tested positive for SARS-CoV-2 via RT-PCR. On examination, he is tachypneic with a respiratory rate of 30 breaths per minute, hypoxic with an oxygen saturation of 88% on room air, and has diffuse bilateral crackles on auscultation. Chest X-ray reveals bilateral pulmonary infiltrates. Laboratory tests show elevated D-dimer levels and lymphopenia. He is diagnosed with acute respiratory distress syndrome (ARDS) secondary to COVID-19. Which of the following management strategies is most appropriate for this patient?",
            "options": [
                "A) Immediate intubation and mechanical ventilation with high tidal volumes",
                "B) Conservative fluid management and prone positioning",
                "C) Administration of oral systemic corticosteroids",
                "D) Initiation of broad-spectrum antibiotics without further investigation",
            ],
            "correct_answer_letter": "B",
            "explanation": "Conservative fluid management helps minimize pulmonary edema, and prone positioning (even awake self-proning) improves V/Q matching and oxygenation in patients with acute respiratory distress syndrome (ARDS) secondary to COVID-19. In contrast, high tidal volumes are harmful, and immediate intubation is avoided if non-invasive strategies can safely maintain oxygenation.",
            "key_learning_points": "Management of ARDS emphasizes conservative fluid management to reduce pulmonary edema and prone positioning to optimize ventilation-perfusion matching.",
            "image_url": "",
        },
        {
            "question_text": "A 45 year old male with acute respiratory distress syndrome (ARDS) is being managed in the intensive care unit. He is currently on mechanical ventilation with a positive end-expiratory pressure (PEEP) of 8 cm H2O. Despite optimisation of ventilator settings, his oxygenation remains suboptimal with a PaO2/FiO2 ratio of 150. The attending physician decides to perform a recruitment manoeuvre. Which of the following is the most appropriate next step in the management of this patient?",
            "options": [
                "A) Increase the PEEP to 20 cm H2O while maintaining the current tidal volume",
                "B) Perform a sustained inflation by applying 30 cm H2O for 30 seconds",
                "C) Increase the inspiratory flow rate to maximise alveolar recruitment",
                "D) Temporarily increase the FiO2 to 100% before and during the manoeuvre",
            ],
            "correct_answer_letter": "D",
            "explanation": "Alveolar recruitment maneuvers carry risks of transient desaturation and hemodynamic instability. Standard practice involves temporarily increasing the fraction of inspired oxygen (FiO2) to 100% before and during the maneuver to prevent profound hypoxemia during the procedure.",
            "key_learning_points": "Pre-oxygenation with 100% FiO2 is important prior to performing alveolar recruitment maneuvers to protect the patient against transient desaturation.",
            "image_url": "",
        },
        {
            "question_text": "A 62 year old man is brought to the emergency department by ambulance after being found unconscious in his home by a neighbour. His son reports that the patient had been complaining of a severe headache and nausea for the past day. The home was noted to have a faulty gas heater. On examination, he is confused with a GCS of 13 (E4, V4, M5). His vital signs are: heart rate 110 bpm, blood pressure 105/60 mmHg, respiratory rate 22/min, and temperature 37.1C. Pulse oximetry reads 98% on 15L/min oxygen via a non-rebreather mask. An arterial blood gas shows a pH of 7.25, pCO2 30 mmHg, pO2 350 mmHg, and lactate of 5.5 mmol/L. His carboxyhaemoglobin level is 30%. An ECG shows sinus tachycardia with non-specific ST segment depression. What is the most appropriate next step in this patient's management?",
            "options": [
                "A) Continue high-flow normobaric oxygen and admit to a medical ward",
                "B) Arrange for urgent hyperbaric oxygen therapy",
                "C) Administer intravenous sodium bicarbonate to correct the acidosis",
                "D) Request an urgent cardiology consultation for possible myocardial infarction",
            ],
            "correct_answer_letter": "B",
            "explanation": "This patient has severe carbon monoxide (CO) poisoning, as indicated by altered mental status (GCS of 13), a carboxyhemoglobin (COHb) level of 30%, severe lactic acidosis, and ECG evidence of myocardial ischemia. Hyperbaric oxygen (HBO) therapy is indicated for patients with severe CO poisoning (such as those with COHb levels > 25%, neurological symptoms, cardiac ischemia, or severe acidosis) to accelerate the elimination of CO and reduce the risk of long-term cognitive and neurological deficits.",
            "key_learning_points": "Hyperbaric oxygen therapy is indicated in severe carbon monoxide poisoning presenting with carboxyhemoglobin levels > 25%, altered mental status, or myocardial ischemia.",
            "image_url": "",
        },
        {
            "question_text": "A 63 year old male with a history of chronic anaemia secondary to myelodysplastic syndrome receives a red blood cell transfusion. Within 6 hours post-transfusion, he develops acute onset dyspnoea, hypoxemia, and bilateral pulmonary infiltrates on chest X-ray. There is no evidence of circulatory overload. His blood pressure is stable, and there is no fever or signs of anaphylaxis. Which of the following is the most likely diagnosis?",
            "options": [
                "A) Transfusion-Related Acute Lung Injury (TRALI)",
                "B) Transfusion-Associated Circulatory Overload (TACO)",
                "C) Anaphylactic transfusion reaction",
                "D) Acute hemolytic transfusion reaction",
            ],
            "correct_answer_letter": "A",
            "explanation": "Transfusion-Related Acute Lung Injury (TRALI) is characterized by acute respiratory distress and bilateral pulmonary infiltrates on chest X-ray occurring within 6 hours of a blood product transfusion in the absence of evidence of circulatory overload (which would suggest TACO).",
            "key_learning_points": "TRALI presents as acute hypoxemic respiratory failure with bilateral pulmonary infiltrates within 6 hours of transfusion without signs of volume overload.",
            "image_url": "",
        },
        {
            "question_text": "A 68 year old man is being managed in the intensive care unit for severe necrotising pancreatitis. He required intubation and mechanical ventilation for three weeks and underwent a percutaneous tracheostomy 18 days ago. He is now haemodynamically stable and is being weaned from ventilation, tolerating periods of spontaneous breathing. During a routine check, the ICU registrar measures the tracheostomy cuff pressure and finds it to be 48 cmH2O. The pressure is immediately adjusted to the target range. What is the most significant long-term complication associated with prolonged periods of excessive cuff pressure?",
            "options": [
                "A) Tracheo-oesophageal fistula",
                "B) Aspiration pneumonia",
                "C) Tracheal stenosis",
                "D) Tracheoinnominate artery fistula",
            ],
            "correct_answer_letter": "C",
            "explanation": "Prolonged excessive cuff pressure (> 30 cm H2O) exceeds the perfusion pressure of the tracheal mucosal capillaries, leading to mucosal ischemia, necrosis, and subsequent scarring and fibrosis. The most common significant long-term complication of this process is tracheal stenosis.",
            "key_learning_points": "Prolonged elevation of tracheostomy cuff pressures can cause mucosal ischemia and necrosis, leading to tracheal stenosis as a long-term complication.",
            "image_url": "",
        },
        {
            "question_text": "A 68 year old woman is admitted to the intensive care unit with urosepsis. She has a background of type 2 diabetes and hypertension. On examination, she is drowsy and peripherally cool. Her blood pressure is 85/45 mmHg despite intravenous fluid resuscitation and a noradrenaline infusion at 10 microg/min. Her respiratory rate is 32 breaths per minute with an oxygen saturation of 91% on a non-rebreather mask. An arterial blood gas analysis shows a severe metabolic acidosis. A decision is made to proceed with endotracheal intubation and mechanical ventilation for impending respiratory failure and airway protection. Which of the following intravenous induction agents is the most appropriate choice for this patient's rapid sequence induction?",
            "options": [
                "A) Propofol",
                "B) Thiopentone",
                "C) Ketamine",
                "D) Midazolam",
            ],
            "correct_answer_letter": "C",
            "explanation": "In a patient with profound distributive shock (sepsis), induction agents like propofol and thiopentone can cause severe vasodilation and myocardial depression, precipitating cardiovascular collapse. Ketamine is preferred because it maintains sympathetic tone, offering a more stable hemodynamic profile in hemodynamically compromised patients.",
            "key_learning_points": "Ketamine is a preferred induction agent for rapid sequence intubation in shocked or hemodynamically unstable patients because it preserves sympathetic drive.",
            "image_url": "",
        },
        {
            "question_text": "A 72 year old male with a history of chronic obstructive pulmonary disease (COPD) and heart failure is admitted to the intensive care unit for acute hypoxemic respiratory failure secondary to severe pneumonia. He is intubated and placed on mechanical ventilation. Despite initial settings to minimise lung injury, the patient's oxygenation status deteriorates, and the ventilator is adjusted to increase tidal volume to 10 mL/kg of predicted body weight and positive end-expiratory pressure (PEEP) to 18 cm H2O. After 48 hours, the patient develops worsening bilateral pulmonary infiltrates and a decrease in lung compliance. Which of the following ventilator adjustments is most likely to have contributed to the development of ventilator-induced lung injury?",
            "options": [
                "A) Increase in respiratory rate",
                "B) Increase in PEEP",
                "C) Increase in tidal volume",
                "D) Decrease in FiO2",
            ],
            "correct_answer_letter": "C",
            "explanation": "High tidal volumes (such as 10 mL/kg of predicted body weight) cause overdistension of the alveoli (volutrauma), which is a major contributor to ventilator-induced lung injury (VILI). Standard lung-protective ventilation targets low tidal volumes of 6 mL/kg to avoid this complication.",
            "key_learning_points": "High tidal volumes contribute directly to ventilator-induced lung injury through alveolar overdistension and volutrauma.",
            "image_url": "",
        },
    ],

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


# ═════════════════════════════════════════════════════════════════════════════
# BUILTIN_VIVA — baked-in VIVA (open Q&A) banks
#
# Viva questions are open-ended, not multiple choice. Each object has just:
#   {
#     "question": "What is the management of a tension pneumothorax?",
#     "answer": "Immediate needle decompression...\nThen chest drain...\n..."
#   }
#
# In the model answer, use \n to separate points — each line becomes a bullet
# in the app's reveal panel.
#
# These appear in the Viva tab via a picker, load instantly, and cost no API calls.
# ═════════════════════════════════════════════════════════════════════════════

BUILTIN_VIVA = {

    # ── Example viva bank — delete or replace with your own ───────────────────
    "Example Viva (Trauma)": [
        {
            "question": "Outline your immediate approach to a haemodynamically unstable trauma patient.",
            "answer": (
                "Use a structured ATLS primary survey: A-E.\n"
                "Airway with C-spine control — assess patency, protect the cervical spine.\n"
                "Breathing — exclude tension pneumothorax, open chest wound, massive haemothorax.\n"
                "Circulation — control external haemorrhage, two large-bore IVs, assess for shock.\n"
                "Disability — GCS, pupils, glucose.\n"
                "Exposure — fully expose while preventing hypothermia.\n"
                "Treat life threats as you find them, before moving on."
            ),
        },
        # ← add more {"question": ..., "answer": ...} objects here
    ],

    # "Antibiotics Viva": [ { "question": ..., "answer": ... } ],

}
