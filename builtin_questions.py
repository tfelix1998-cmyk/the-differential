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

    "Orthopaedic Trauma Framework (Viva)": [
        {
            "question": "What is the overarching purpose of the 8-box trauma framework?",
            "answer": "To provide a systematic, safe way to approach any orthopaedic problem (a \"safety net\" or \"helicopter view\").\nTo outline exactly what knowledge is required and demonstrate your clinical thought process for exams (exams test thought process, not just knowledge).\nIf you can visualise and articulate this framework, you are guaranteed to be a safe doctor.",
        },
        {
            "question": "How are the roles divided among the medical team in the framework's colour-coding?",
            "answer": "Green boxes: Crucial for medical students and House Officers (HOs) to know.\nOrange boxes: Areas where residents and consultants focus.",
        },
        {
            "question": "List the 8 boxes of the trauma framework in chronological order.",
            "answer": "Box 1: Stabilisation\nBox 2: History\nBox 3: Examination\nBox 4: Initial Investigations\nBox 5: Acute Management\nBox 6: Advanced Imaging\nBox 7: Definitive Management (Operative vs Non-operative)\nBox 8: Post-operative Review",
        },
        {
            "question": "What are the three broad clinical scenarios (and their subsets) covered using this framework?",
            "answer": "1. Trauma: Closed/isolated injury, Poly trauma (multiple injuries), Spine injury, Open fracture.\n2. Chronic pain: Joint pain, Back pain.\n3. Infection: Soft tissue infection, Joint infection, Bone infection.",
        },
        {
            "question": "What is the first and most crucial step for managing every trauma patient?",
            "answer": "Stabilise the patient and ensure they are alive by applying ATLS (Acute Trauma Life Support) principles.",
        },
        {
            "question": "How can you quickly tell if a patient in the clinic is less likely to require full ATLS resuscitation?",
            "answer": "If the patient is able to communicate and walk into the clinic.",
        },
        {
            "question": "What general demographic and social history points must be gathered for a trauma patient?",
            "answer": "Age, gender, race, occupation.\nSmoking and drinking history (smoking increases the risk of surgery complications).\nSports, recreation, and hobbies (to understand functional demands and what they can no longer do after injury).\nHandedness (crucial for upper limb injuries; a non-dominant arm may be a factor determining whether surgery should be avoided).",
        },
        {
            "question": "What standard medical history points must be collected?",
            "answer": "Past medical history (including PMH causing brittle bones), past surgical history, and drug allergies.",
        },
        {
            "question": "What does the keyword \"mechanical fall\" imply when presenting a trauma history?",
            "answer": "It implies the patient tripped and fell with absolutely no underlying medical conditions causing the fall.\nIt guarantees you have ruled out pre-fall, intra-fall, and post-fall symptoms (e.g., no chest pain, no shortness of breath, no seizures, no weakness).\nIt signals to the surgeon that the patient is medically ready for any intervention or surgery if needed.",
        },
        {
            "question": "What is \"prodromal pain\" and why is it considered a red flag in a trauma history?",
            "answer": "Prodromal pain refers to pain that occurs before the fall.\nIt is a red flag because it suggests an underlying primary pathology (e.g., metastatic cancer growing at the site) that weakened the bone and caused the fall. It is particularly important to ask elderly patients.",
        },
        {
            "question": "Why is asking about the severity of pain or using the full \"SOCRATES\" method less crucial in an acute trauma setting?",
            "answer": "Because it is obvious the patient fell down and has pain from the acute injury; the onset and aggravating/relieving factors are self-evident and less relevant than in a chronic pain setting.",
        },
        {
            "question": "If an elderly patient suffers a fracture from a simple fall, what underlying risk factors should you elicit in the history?",
            "answer": "Osteoporosis.\nUse of medications like steroids (which cause secondary osteoporosis and brittle bones).",
        },
        {
            "question": "What are the four main things you must look for and report when examining any trauma patient?",
            "answer": "Open fracture (Is blood coming out?)\nTenting of the skin (Impending open fracture)\nNeurovascular status\nSecondary survey",
        },
        {
            "question": "Define an open fracture and explain why it is a critical finding.",
            "answer": "An open fracture is a fracture where the bone is associated with a breach in the skin (blood coming out).\nIt is serious because bacteria can enter through the wound and cause a major infection.",
        },
        {
            "question": "Define \"tenting\" and explain its significance as a surgical emergency.",
            "answer": "Tenting means the broken bone is poking against the skin from underneath, placing the skin under very high pressure.\nThe high pressure prevents blood flow to that area of skin, causing it to become necrotic and tear, eventually creating an open wound (an impending open fracture).",
        },
        {
            "question": "How should you specifically test for neurovascular status in the upper limb?",
            "answer": "Nerves: Check the median nerve, ulnar nerve, and radial nerve (or axillary nerve for a shoulder dislocation).\nArtery: Check the radial pulse.",
        },
        {
            "question": "How should you specifically test for neurovascular status in the lower limb?",
            "answer": "Arteries: Check the dorsalis pedis pulse and posterior tibial pulse. (You must be specific about which artery you are checking).",
        },
        {
            "question": "Explain the \"downstream river\" concept when checking neurovascular status.",
            "answer": "If a distal (downstream) pulse is present and strong, there is no need to check the proximal (upstream) pulses because everything is flowing smoothly.\nExample: If the radial pulse or dorsalis pedis is good, there is no need to separately check the brachial or popliteal pulse. The same applies to distal nerve function.",
        },
        {
            "question": "What is a \"secondary survey\" in a trauma examination and why is it necessary?",
            "answer": "It involves systematically checking for pain or injury elsewhere in the body (e.g., facial compression, chest compression, pelvic compression).\nIt is necessary because the patient may be so overwhelmed by the pain of their primary injury (e.g., a broken hand) that they neglect to report other injuries.",
        },
        {
            "question": "Define Compartment Syndrome.",
            "answer": "Increased pressure within a limited osteofascial space that compromises the perfusion and function of the tissue within it.\nThe compartment pressure exceeds the systolic blood pressure.",
        },
        {
            "question": "What is the physiological mechanism and timeline of damage in compartment syndrome?",
            "answer": "The fracture causes swelling and haematoma formation -> the compartment becomes very tight -> no blood can enter -> ischaemia -> necrosis of muscles and nerves.\nIrreversible damage occurs within 8 hours, making it an orthopaedic emergency.",
        },
        {
            "question": "In which anatomical locations does compartment syndrome most commonly occur and why?",
            "answer": "Distal areas with very tight osteofascial spaces: the forearm, tibia (calf), and foot/ankle.\nIt is less likely proximally (like the hip or shoulder) because there is more space and fat for the blood and swelling to expand into.",
        },
        {
            "question": "Can compartment syndrome happen in an open fracture? Explain why.",
            "answer": "Yes, it can still occur.\nFor example, the calf has four separate compartments. Even if the fascia is breached in one compartment (causing an open fracture), the other intact compartments are not decompressed and can still develop raised pressure leading to compartment syndrome.",
        },
        {
            "question": "List the classical \"Six Ps\" of compartment syndrome.",
            "answer": "1. Pain out of proportion\n2. Paraesthesia (abnormal sensation due to nerve ischaemia)\n3. Paralysis (nerve affected so muscle cannot move)\n4. Pulselessness (compartment pressure > systolic BP)\n5. Pallor (pale, no new blood entering)\n6. Poikilothermia / Cold (no new blood entering)",
        },
        {
            "question": "Which of the 6 Ps is the most crucial sign and why?",
            "answer": "\"Pain out of proportion\" is the earliest and most important sign. Even with analgesia, the patient will have severe pain.\nIf you wait for the other Ps (like pulselessness or paralysis) to appear, the tissues are already dead and it is too late.",
        },
        {
            "question": "How do you physically assess a patient to provoke the pain of compartment syndrome?",
            "answer": "By passive stretching of the muscles in the affected compartment (Note: passive means you are moving the joint for the patient).\nExample: To test the calf (posterior compartment), passively dorsiflex the ankle. To test the anterior compartment, passively plantar flex the ankle.",
        },
        {
            "question": "What visual and tactile signs on the limb indicate building pressure from compartment syndrome?",
            "answer": "The limb feels very tight, looks shiny, skin wrinkles disappear, and blood blisters may be present.",
        },
        {
            "question": "What are the immediate management steps if you suspect compartment syndrome?",
            "answer": "Remove any external pressure immediately (cut and remove cast, backslab, or dressings).\nPlace the limb at the level of the heart. (Do NOT elevate, as elevation reduces arterial blood flow and worsens ischemia; do NOT lower it either).\nAlert the senior immediately.",
        },
        {
            "question": "What is the definitive surgical treatment for compartment syndrome, and how does it differ from a fasciectomy?",
            "answer": "Fasciotomy (cutting open the fascia to release the pressure).\nIt differs from a fasciectomy, which means removing the fascia completely (like an appendicectomy removes the appendix, while a laparotomy just cuts open the abdomen).",
        },
        {
            "question": "What are the two main categories of initial investigations in trauma?",
            "answer": "Bloods and Imaging (X-ray is the most important).",
        },
        {
            "question": "What does it mean to get \"orthogonal views\" on an X-ray, and why is this required?",
            "answer": "It means getting two views that are perpendicular to each other (e.g., AP and lateral).\nRequired because a fracture may only be visible on one 2D plane. You also need actuals of the entire bone, including one joint above and one joint below, to ensure no associated injuries are missed. Special views are a bonus.",
        },
        {
            "question": "What is the primary purpose of ordering pre-op bloods, an ECG, and a Chest X-ray in an acute trauma patient?",
            "answer": "Not to look for infection, but to check the patient's readiness and safety for surgery (e.g., checking FBC, PT/INR for coagulation status, and assessing heart/lung status).",
        },
        {
            "question": "What specific blood tests should be ordered to investigate \"secondary osteoporosis\" in an elderly patient who fell?",
            "answer": "Vitamin D, calcium panel, thyroid function tests (TFTs), and liver function tests (LFTs) to rule out underlying medical causes of brittle bones.",
        },
        {
            "question": "What is the very first priority in the acute management of a trauma patient?",
            "answer": "Provide pain relief (analgesia) based on the WHO pain ladder (stepwise approach from non-opioids to strong opioids).",
        },
        {
            "question": "What does \"M&R\" stand for, and what does it involve?",
            "answer": "M&R = Manipulation and Reduction.\nIt involves pulling the bone out to length (traction) and forcefully manipulating it back into alignment. It must be done under sedation (patient is sleepy, not fully awake).",
        },
        {
            "question": "Which fractures generally cannot be manipulated and reduced in the A&E?",
            "answer": "Clavicle fractures (no practical way to manipulate) and proximal humerus fractures (too many fragments).",
        },
        {
            "question": "Why must you temporarily stabilise a fracture immediately after reducing it?",
            "answer": "To prevent the fracture from flopping around, which causes further pain, increases swelling, risks tearing arteries, and increases the risk of compartment syndrome.",
        },
        {
            "question": "Why is a backslab used acutely instead of a more stable full cast?",
            "answer": "A backslab is half-circumferential, allowing room for the acute swelling to expand.\nA full cast is fully circumferential; it restricts swelling, increases pressure, and causes compartment syndrome. Stability is consciously sacrificed acutely to prevent compartment syndrome.",
        },
        {
            "question": "When is a backslab usually converted to a full cast?",
            "answer": "At approximately 2 weeks, once the swelling has resolved, to maximise stability and maintain fracture position during healing.",
        },
        {
            "question": "What is the general rule for determining the correct length of a backslab?",
            "answer": "The backslab must be long enough to adequately cover the injury, ensuring the fracture sits securely in the middle of the slab.",
        },
        {
            "question": "Outline the temporary stabilisation options for Upper Limb injuries.",
            "answer": "Clavicle fracture / Shoulder dislocation / ACJ dislocation: Arm sling.\nProximal humerus: Collar and cuff (uses gravity to pull the arm down and aid reduction).\nHumeral shaft: U-slab (goes from top of shoulder down into the axilla; non-circumferential).\nDistal humerus / Elbow dislocation / Forearm shaft: Above elbow backslab.\nDistal radius: Below elbow backslab (avoids unnecessary elbow immobilisation to prevent stiffness).\nMetacarpal fractures: Intrinsic plus splint (positions hand optimally to prevent stiffness).\nScaphoid / Thumb-side: Thumb spica splint.\nLittle finger side: Ulnar gutter splint.\nFingers: Body splint (buddy strapping) or Mallet splint.",
        },
        {
            "question": "Outline the temporary stabilisation options for Lower Limb injuries.",
            "answer": "Pelvic fractures: Pelvic binder (reduces pelvic volume to prevent blood loss).\nProximal hip / Neck of femur fractures: Bed rest and traction (though traction is less common now; cannot use a backslab here).\nFemoral shaft: Thomas splint (a form of traction).\nDistal femur / Patella / Proximal tibia: Above knee backslab.\nTibia shaft / Distal tibia / Ankle: Below knee backslab.\nToes: Buddy splint.",
        },
        {
            "question": "Why are bed-bound hip fracture patients at high risk for Deep Vein Thrombosis (DVT), and how does Virchow's Triad apply?",
            "answer": "Bed rest and non-weight bearing status lead to venous stasis.\nVirchow's triad (Stasis, Hypercoagulability, Endothelial injury) contributes to DVT formation.",
        },
        {
            "question": "Explain the fatal pathway of an unmanaged DVT.",
            "answer": "DVT forms -> embolus travels back to the right side of the heart -> pumped into pulmonary circulation -> Pulmonary Embolism -> lung dies -> patient cannot breathe -> death.",
        },
        {
            "question": "How do you prevent DVT in an immobilised trauma patient?",
            "answer": "Pharmacological: Anticoagulant medications (e.g., LMWH).\nNon-pharmacological: Calf pumps (intermittent pneumatic compression) to maintain venous blood flow and prevent stasis.",
        },
        {
            "question": "What two clinical steps must you perform immediately after applying a backslab?",
            "answer": "Recheck and document the neurovascular status (to ensure a nerve or vessel was not trapped during manipulation).\nRepeat the X-ray to assess the alignment after reduction.",
        },
        {
            "question": "When is a CT scan indicated in orthopaedic trauma?",
            "answer": "When the fracture is near a joint (intra-articular fractures or suspected intra-articular extension) to provide axial, sagittal, and coronal views for better 3D reconstruction and surgical planning.",
        },
        {
            "question": "When is an MRI indicated in orthopaedic trauma?",
            "answer": "To identify \"occult fractures\" when the X-ray and CT are normal, but clinical suspicion remains high (e.g., elderly patient with severe hip pain after a fall).\nTo evaluate soft tissue injuries (e.g., ACL tears in young patients).",
        },
        {
            "question": "What is the clinical danger of missing an occult fracture if advanced imaging is not done?",
            "answer": "If the patient is discharged and allowed to weight-bear, the undetected occult fracture can propagate into a complete, displaced fracture, turning a minor injury into a major surgery.",
        },
        {
            "question": "What three groups of factors influence the decision for surgery?",
            "answer": "Patient factors: Age, smoking status (chronic smoker), comorbidities, functional demand, handedness (dominant vs non-dominant arm).\nInjury factors: Fracture classification, severity of displacement.\nSurgeon factors: The surgeon's training and specific experience (different surgeons may treat the same injury differently).",
        },
        {
            "question": "At what point in the 8-box framework do fracture classifications (e.g., Garden's classification) become relevant?",
            "answer": "Only in Box 7, when deciding on definitive management. You do not need to know complex classifications to properly manage the patient in the first five boxes.",
        },
        {
            "question": "What specific components are assessed during the post-operative review of a patient?",
            "answer": "Vitals, the operated limb, dressings, neurovascular status (same nerves/vessels checked pre-op), drain output (if any), and post-operative notes.",
        },
        {
            "question": "What are the four main components you will find in every surgical/operative note?",
            "answer": "The Title: Surgery being performed.\nSurgical Findings: What they found inside during surgery.\nThe Story: Detailed account of what the surgeon did.\nPost-operative Instructions: Orders to execute (vitals monitoring, diet, analgesia, antibiotics, physio, weight-bearing status, discharge plan).",
        },
        {
            "question": "What does it mean to prescribe \"prophylactic antibiotics\" post-operatively?",
            "answer": "P for Prevention: It is given routinely after open surgery when there is NO active infection yet, simply to prevent one from developing (e.g., IV Cefazolin, or Clindamycin if allergic).",
        },
        {
            "question": "Define the different post-operative weight-bearing (WB) statuses.",
            "answer": "Non-weight bearing (NWB): Do not put any weight on the limb.\nPartial weight bearing (PWB): Some weight is allowed.\nToe touch weight bearing (TTWB): Only the toes touch the ground.\nWeight bearing as tolerated (WBAT): Patient can step fully on the leg as much as their pain allows.",
        },
        {
            "question": "How do you check the vascular status (pulses) if a patient's limb is wrapped in a full cast?",
            "answer": "You cannot feel a pulse through a cast. You must either cut a window in the cast to access the skin, or use an ultrasound Doppler device directly on the skin to detect the pulse.",
        },
        {
            "question": "Describe the roles of the Multidisciplinary Team (MDT) involved in post-operative orthopaedic discharge.",
            "answer": "Physiotherapists (PT): Rehabilitation, gait training, range of motion.\nMedical Social Worker (MSW): Discharge planning and sorting social concerns.\nCommunity Hospital (CH): Step-down care facility providing aggressive twice-daily physio to get patients walking, keeping them away from acute hospital infections.\nTransitional Care Facility (TCF): A less intensive step-down facility for stable patients with a clear discharge plan who are just waiting for caregiver approval or home arrangements.",
        },
        {
            "question": "Outline the overall \"journey\" of a fracture.",
            "answer": "Achieve Reduction (Closed or Open).\nMaintain Reduction (Temporary, then Definitive).\nHealing (God heals the fracture over time).\nComplications (if any arise).",
        },
        {
            "question": "Differentiate between Closed Reduction and Open Reduction.",
            "answer": "Closed Reduction (M&R): Manipulation and reduction performed without cutting open the skin. Done in the A&E under sedation.\nOpen Reduction: The skin is cut open to manually align the bones. This can only be done in the operating theatre.",
        },
        {
            "question": "What does ORIF stand for?",
            "answer": "Open Reduction Internal Fixation (cutting the skin open to reduce the bone, then fixing it with metal implants inside the body).",
        },
        {
            "question": "How is the reduction maintained temporarily vs. definitively?",
            "answer": "Temporary (Acute phase): Externally via backslab, traction, or an external fixator.\nDefinitive: Externally (via a full cast or external ring fixator) or Internally (via metal implants like plates, screws, or IM rods).",
        },
        {
            "question": "What is an External Fixator and when is it typically used?",
            "answer": "Metal pins inserted into the bone that connect to external rods outside the body.\nMostly used temporarily in open fractures or poly trauma for \"damage control surgery\".\nRarely used definitively (e.g., in a diabetic or renal failure patient with an ankle fracture where internal metal carries an extreme risk of infection).",
        },
        {
            "question": "What is Percutaneous Pinning?",
            "answer": "A hybrid fixation where wires are inserted through the skin into the bone (leaving some metal sticking out).\nCommonly used in paediatric fractures (e.g., supracondylar or lateral condyle fractures) and pulled out after about 6 weeks.",
        },
        {
            "question": "List the four phases of fracture healing.",
            "answer": "Haematoma formation.\nSoft callus formation.\nHard callus formation (calcium deposited, visible on X-ray).\nRemodelling (occurs over many years).",
        },
        {
            "question": "How long does it take for a hard callus to form, and what is its clinical significance?",
            "answer": "Takes approximately 4-6 weeks.\nOnce hard callus is visible on an X-ray, radiological union is confirmed. The fracture is stable enough that the cast can be removed and the patient can start weight-bearing as tolerated.",
        },
        {
            "question": "Is bone remodelling possible in adults, and how does it affect the threshold for surgery compared to children?",
            "answer": "Yes, adults remodel, but children (who are skeletally immature) have a much greater remodelling potential.\nChildren can tolerate much higher deviations from normal alignment without surgery because the bone will grow and straighten itself (the threshold not to do surgery is very high).\nAdults have poor remodelling potential, meaning their threshold to require surgery for misaligned fractures is much lower.",
        },
        {
            "question": "List the common complications of fractures and fracture surgeries.",
            "answer": "Non-union: Fracture does not heal.\nMalunion: Fracture heals in a crooked/angulated position, leading to deformity.\nInfection: High risk whenever the skin is cut or metal is placed inside.\nImplant failure: The metal hardware breaks.\nPeri-implant fracture: Fracture occurs in the bone adjacent to the metal implant.\nSecondary osteoarthritis: Occurs later if the fracture involved a joint.",
        },
        {
            "question": "What are the main causes of fracture non-union?",
            "answer": "Instability: Too much movement, wrong implant chosen, or insufficient screws.\nPoor biology: E.g., the patient is a chronic smoker, resulting in poor blood supply and impaired healing.",
        },
        {
            "question": "Provide an example of a malunion deformity.",
            "answer": "Cubitus varus deformity of the elbow, resulting from the malunion of a childhood supracondylar fracture.",
        },
        {
            "question": "Why do peri-implant fractures occur?",
            "answer": "The bone right next to a rigid metal implant becomes a \"stress riser\" (the weakest point). If the patient falls again, the bone is most vulnerable to breaking at that exact spot.",
        },
        {
            "question": "How is a severe malunion treated surgically?",
            "answer": "Via an Osteotomy (cutting the bone to straighten it, then fixing it with a new metal implant).",
        },
        {
            "question": "How often should a patient in a cast be followed up in the clinic?",
            "answer": "Approximately every 2 weeks to take repeat X-rays and ensure the fracture hasn't shifted. If it shifts, surgery may be considered.",
        },
        {
            "question": "What defines a polytrauma patient?",
            "answer": "A patient who has sustained injuries to more than one organ system (e.g., head/neck, face, thorax, abdomen/pelvis, extremities, spine). It represents a huge spectrum of severity.",
        },
        {
            "question": "What are the major causes and timelines of early death in polytrauma patients?",
            "answer": "50% die from Traumatic Brain Injury (TBI).\n30% die from massive bleeding (can bleed to death within 6 hours).\n10% die from subsequent multi-organ failure (MOF).",
        },
        {
            "question": "What is the \"Triad of Death\" in polytrauma?",
            "answer": "Hypothermia (managed with a bear hugger).\nAcidosis (from anaerobic respiration, monitored via lactate and ABG).\nCoagulopathy (clotting factors go haywire, monitored via PT/INR).",
        },
        {
            "question": "What is ATLS, and what is the orthopaedic surgeon's primary role during the resuscitation phase?",
            "answer": "ATLS (Acute Trauma Life Support) addresses ABCDEs to stabilise the patient and prevent the triad of death.\nThe orthopaedic role primarily focuses on managing bleeding (applying a pelvic binder) and protecting the spine (applying a C-collar and initiating spinal nursing).",
        },
        {
            "question": "List the specific ATLS measures and adjuncts used for a crashing polytrauma patient.",
            "answer": "Airway: Intubation to secure a patent airway.\nBreathing: Chest tubes to clear lung fluid/blood.\nCirculation: Two large-bore IV cannulas, urinary catheter (to check output), massive transfusion protocol, and a pelvic binder.",
        },
        {
            "question": "What history format is used when evaluating a polytrauma patient rapidly?",
            "answer": "AMPLE history (Allergies, Medications, Past medical history, Last meal, Events/mechanism of injury).",
        },
        {
            "question": "What is a \"log roll\" and why is it performed?",
            "answer": "Rolling the patient's entire body as one single unit to examine the back without twisting the spine.\nIt requires 4 people: one at the head providing inline traction, and three along the body turning it together.\nIt is done because the patient is in a C-collar/spinal nursing. During the roll, a Digital Rectal Exam (DRE) is performed to check anal tone.",
        },
        {
            "question": "Why is a Digital Rectal Exam (DRE) crucial in polytrauma?",
            "answer": "To check for loss of anal tone (loose anal sphincter), which indicates Cauda Equina Syndrome or severe spinal cord injury.",
        },
        {
            "question": "What consists of the standard polytrauma X-ray and CT screening series?",
            "answer": "X-ray series: Cervical spine, Chest X-ray, Pelvis AP.\nCT series: CT Brain, CT Cervical spine, CT Thorax/Abdomen/Pelvis (CT-TAP) to check for internal bleeding.",
        },
        {
            "question": "How does a pelvic binder work, and where is it placed?",
            "answer": "It is placed centered on the greater trochanters.\nIt pushes the bones together to reduce the overall volume of the pelvis, preventing the pelvic bowl from expanding. This allows a venous blood clot to form and tamponade (stop) the venous bleeding.",
        },
        {
            "question": "Why are pelvic fractures so dangerous in terms of blood loss?",
            "answer": "The pelvis can hold and lose 3 to 5 litres of blood.\n90% of this bleeding is venous (the veins adhere to the sacral brim and tear when the bone shifts). 10% is arterial spurting.",
        },
        {
            "question": "If a patient with a pelvic binder is still crashing from a suspected 10% arterial bleed, what is the next step?",
            "answer": "Pelvic binder is insufficient for arterial bleeds; the patient requires an angiogram and embolisation of the bleeding artery.",
        },
        {
            "question": "Can the massive blood clot formed in the pelvis after a fracture cause a pulmonary embolism?",
            "answer": "No, because the blood clot forms outside the vein (extravascular haematoma). It cannot travel into the venous circulation.",
        },
        {
            "question": "Aside from a pelvic binder, what are other ways to stabilise the pelvis and stop bleeding?",
            "answer": "C-clamp, temporary external fixation in the operating theatre, or packing the pelvis with surgical sponges by general surgeons.",
        },
        {
            "question": "What does \"spinal nursing\" involve, and why is it done?",
            "answer": "The patient is nursed completely flat and is not allowed to bend, sit up, or twist.\nDone to immobilise a potentially fractured spine and protect the spinal cord/nerve roots from catastrophic injury (like paralysis).",
        },
        {
            "question": "Describe the \"Early Total Care\" (ETC) philosophy (Bone, 1989).",
            "answer": "All fractures are definitively fixed internally from day one. Advantage is immediate stabilisation, but the disadvantage is that long surgeries can overly stress an already crashing patient.",
        },
        {
            "question": "Describe the \"Damage Control Surgery\" (DCS) philosophy (2002).",
            "answer": "Temporarily stabilise all fractures first (e.g., using external fixators quickly).\nSend the patient to the HDU/ICU for a few days to stabilise their physiology (monitor vitals, clear lactate/ABG, correct triad of death).\nPerform definitive internal fixation only once the patient is completely stable.",
        },
        {
            "question": "Describe the \"Early Appropriate Care\" (EAC) philosophy (2011).",
            "answer": "A middle-ground approach. If the patient is physiologically well and stable, you fix everything definitively early. If they are crashing, you default to damage control surgery.",
        },
        {
            "question": "During the ICU stabilisation phase of Damage Control Surgery, what must be actively managed/prevented?",
            "answer": "Continuous monitoring of vitals and ABG/lactate.\nPrevention of pressure sores (regular log-roll turning).\nDVT prophylaxis.\nInfection prevention for any open wounds (prophylactic antibiotics).",
        },
        {
            "question": "How do you confirm a polytrauma patient is physiologically ready to return to the OR for definitive surgery?",
            "answer": "They are not acidotic, not hypothermic, not coagulopathic, vitals are stable, and the patient is alert enough to give a \"thumbs up\".",
        },
        {
            "question": "How does the initial management of a spine fracture differ from other fractures?",
            "answer": "The framework remains the same, but you immediately apply a C-collar and initiate spinal nursing upon arrival to protect the spinal cord.",
        },
        {
            "question": "What advanced imaging is required for a suspected spine fracture and why?",
            "answer": "MRI of the whole spine: To look for soft tissue/spinal cord compression, epidural haematomas (which can't be seen on CT), and contiguous fractures.\nCT of the specific spine region: For detailed fracture pattern analysis and surgical planning.",
        },
        {
            "question": "What is a \"contiguous fracture\" in spine trauma?",
            "answer": "A secondary fracture located at a completely different level of the spine (e.g., the patient complains of neck pain, but the MRI reveals an additional fracture in the lumbar spine).",
        },
        {
            "question": "What does the ASIA score assess, and what is its primary clinical use?",
            "answer": "ASIA (American Spinal Injury Association) assesses motor function (testing specific myotomes on a 0-5 scale) and sensation (dermatomes) to grade spinal cord injuries.\nIt is primarily used academically/for research to compare outcomes, rather than for daily clinical decision-making.",
        },
        {
            "question": "List the specific Cervical (Upper Limb) myotomes tested in the ASIA score.",
            "answer": "C5: Elbow flexors\nC6: Wrist extensors\nC7: Elbow extensors\nC8: Finger flexors\nT1: Finger abductors",
        },
        {
            "question": "List the specific Lumbar (Lower Limb) myotomes tested in the ASIA score.",
            "answer": "L2: Hip flexors\nL3: Knee extensors\nL4: Ankle dorsiflexors\nL5: Great toe extensors\nS1: Ankle plantar flexors",
        },
        {
            "question": "Briefly define the ASIA Impairment Scale grades (A through E).",
            "answer": "ASIA A: Complete injury (no motor or sensory function below injury level).\nASIA B: Incomplete (sensory preserved, but motor is zero).\nASIA C: Incomplete (motor present, but >50% of muscles below injury are grade <3).\nASIA D: Incomplete (motor present, and >50% of muscles below injury are grade 3 or above).\nASIA E: Normal motor and sensory function.",
        },
        {
            "question": "What two scoring systems are used by surgeons to decide between operative vs. non-operative management for spine injuries?",
            "answer": "TLICS score (Thoracolumbar Injury Classification and Severity Score) for the lumbar spine.\nSubaxial score for the cervical spine.\nBoth base their surgical decision on fracture morphology, ligament integrity, and neurological status.",
        },
        {
            "question": "What makes an open fracture an absolute orthopaedic emergency?",
            "answer": "The skin is breached (blood comes out), meaning bacteria can immediately walk inside and cause a severe bone infection.",
        },
        {
            "question": "What is the single most important factor in reducing infection risk after an open fracture?",
            "answer": "Early administration of prophylactic antibiotics. Start them immediately in the A&E; do not wait for the consultant or for wound cultures.",
        },
        {
            "question": "What standard prophylactic medications are given immediately in the A&E for an open fracture?",
            "answer": "IV Cefazolin (or Clindamycin if penicillin allergic) + Analgesia + IM Anti-tetanus.",
        },
        {
            "question": "What specific antibiotics are added for open fractures exposed to specific high-risk environments?",
            "answer": "Sea water contamination (Vibrio): Add Doxycycline.\nFresh water/pond contamination (Aeromonas): Add Ciprofloxacin.\nSoil/farming contamination (Anaerobes): Add Metronidazole (Flagyl).",
        },
        {
            "question": "What are the two stages of surgical management for an open fracture?",
            "answer": "Surgery 1 (Acute/Damage Control): Wound debridement, washout, application of a negative pressure (VAC) dressing, and temporary stabilisation (backslab or Ex-fix).\nSurgery 2 (Definitive): Internalise the fixation (put metal inside) and provide soft tissue coverage (skin graft or skin flap).",
        },
        {
            "question": "What is \"debridement\" and \"degloving\"?",
            "answer": "Debridement: The surgical removal of all dead, non-viable, and unhealthy tissue from the wound to prevent infection.\nDegloving: When skin and soft tissue are violently lifted off the underlying structures (this tissue is usually non-viable and must be debrided, often leaving a large hole).",
        },
        {
            "question": "What is a Negative Pressure Dressing (VAC dressing)?",
            "answer": "A temporary vacuum dressing applied to the wound after acute debridement when the defect is too large to close primarily.",
        },
        {
            "question": "Why is an External Fixator (Ex-fix) highly advantageous for the acute management of open fractures?",
            "answer": "It holds the bones rigid from the outside without needing bulky bandages, providing nurses and doctors with easy, direct access to inspect and clean the open wound.",
        },
        {
            "question": "What is the difference between a Skin Graft and a Skin Flap regarding blood supply and surgical technique?",
            "answer": "Skin Graft: Does NOT have its own blood supply. It relies purely on the diffusion of nutrients from a healthy underlying muscle bed. Easier and faster to do.\nSkin Flap: Has its own blood supply (artery and vein). Requires complex microsurgery to anastomose the vessels to the local blood supply.",
        },
        {
            "question": "Compare the quality and indications for Skin Grafts vs. Skin Flaps.",
            "answer": "Skin Graft: Poorer quality, high risk of shrinking/contracture. Used only on areas with a good soft tissue bed. NEVER used over exposed bone or over joints.\nSkin Flap: Better quality, minimal contracture. Specifically used to cover joints (e.g., knee/patella) and exposed bone.",
        },
        {
            "question": "Why must you NEVER use a skin graft over an exposed joint or exposed bone?",
            "answer": "Bone lacks surface vascularity, so it cannot nourish a graft via diffusion (the graft will die).\nOver a joint, a graft acts like cheap clothing in a wash - it shrinks and contracts, leading to severe joint stiffness and a permanently restricted range of motion.",
        },
        {
            "question": "Is perfect anatomical reduction necessary during the definitive fixation of a mid-shaft open tibia fracture?",
            "answer": "No. For mid-shaft fractures, perfect reduction is not strictly necessary. The internal metal rod secures everything sufficiently, and the primary focus shifts to ensuring proper soft tissue coverage.",
        },
        {
            "question": "Despite the presence of an open wound, why is a backslab still applied in the A&E?",
            "answer": "To prevent the broken bones from flopping around, which causes severe pain, tears vessels, increases bleeding, and raises the risk of compartment syndrome.",
        },
        {
            "question": "Outline the application of the framework to a 52-year-old active male who suffered a mechanical fall onto an outstretched hand while skateboarding.",
            "answer": "Box 1 (Stabilisation): Patient is talking to you, therefore ATLS stable.\nBox 2 (History): Mechanical fall confirmed (no pre/intra/post fall symptoms); no red flags; 52yo active male.\nBox 3 (Examine): No open wound (blood), no tenting, NV intact (median/ulnar/radial nerves, radial pulse), no tense compartments. Secondary survey done.\nBox 4 (Investigations): AP and lateral wrist X-rays show a comminuted distal radius fracture displaced posterolaterally.\nBox 5 (Acute management): Analgesia (WHO ladder), M&R under sedation, apply a below-elbow backslab, recheck NV status, repeat X-ray.\nBox 6 (Advanced imaging): CT scan of the wrist is ordered because the fracture is intra-articular (near the joint), requiring 3D reconstruction for planning.\nBox 7 (Definitive management): Surgery (ORIF) chosen based on patient factors (active, 52yo, dominant arm).\nBox 8 (Post-op review): Assess vitals, dressings, NV status, execute post-op orders from the surgical note.",
        },
        {
            "question": "How do you determine on a lateral wrist X-ray if the distal radius fragment has displaced anteriorly or posteriorly?",
            "answer": "Locate the thumb on the X-ray, which marks the anterior (palmar/volar) side.\nIf the broken fragment shifts away from the thumb side, it is posteriorly (dorsally) displaced.",
        },
        {
            "question": "What does the radiological term \"comminuted\" mean?",
            "answer": "It means the fracture is broken into multiple small fragments or pieces.",
        },
        {
            "question": "What specific type of backslab is used for a distal radius fracture and why?",
            "answer": "A below-elbow backslab. It is sufficient to stabilise the wrist while intentionally avoiding unnecessary immobilisation of the elbow (which would lead to elbow stiffness).",
        },
        {
            "question": "Why was a CT scan required for this specific distal radius fracture?",
            "answer": "Because the fracture extended into the wrist joint (intra-articular). CT provides necessary 3D detail for the surgeon to plan the precise reconstruction of the joint surface.",
        },
    ],

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
# ── Imported banks (auto-generated from revision notes) ──
try:
    from imported_questions import IMPORTED_BANKS, IMPORTED_VIVA
    BUILTIN_BANKS.update(IMPORTED_BANKS)
    BUILTIN_VIVA.update(IMPORTED_VIVA)
except Exception:
    pass
