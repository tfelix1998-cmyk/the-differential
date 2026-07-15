"""
llp_questions.py — LLP (Longitudinal Learning Plan) banks for the UQ module.
===========================================================================

Bank keys follow the module convention exactly:

    UQ Critical Care Module :: LLP - <Topic> (MCQ)
    UQ Critical Care Module :: LLP - <Topic> (VIVA)

The " :: " separator matters — split_category() parses on it. Do not rename a
bank key once it is live: seed_builtin_banks() hashes the name into
generated_content, and a rename leaves a stale row behind.

Content is written from Terry's own LLP unit notes (Australian: QLD Health,
eTG, AMH, THANZ). Populated so far:

    Unit 4 Safe Prescribing - Anticoagulation and Antiplatelets   35 MCQ + viva
    Unit 3 Safe Prescribing - Inpatient Diabetes Management       35 MCQ + viva

The remaining six topics from the LLP list are declared with empty banks, so
they appear in the module at 0 questions and are ready to fill.
"""

_C = "UQ Critical Care Module"

# Topic names, in unit order. uq_config imports this so the two files cannot
# drift apart.
LLP_TOPICS = [
    "Unit 3 Acutely Unwell Patient - Altered Level of Consciousness",
    "Unit 3 Ward Call - Endocrine Presentations",
    "Unit 3 Safe Prescribing - Inpatient Diabetes Management",
    "Unit 3 Multimorbidity and Whole Patient Care - Back on the Road Again",
    "Unit 4 Acutely Unwell Patient - The Breathless Patient",
    "Unit 4 Ward Call - Renal Presentations",
    "Unit 4 Safe Prescribing - Anticoagulation and Antiplatelets",
    "Unit 4 Multimorbidity and Whole Person Care - In the Midst of Life",
]

_ANTICOAG = "Unit 4 Safe Prescribing - Anticoagulation and Antiplatelets"
_INSULIN = "Unit 3 Safe Prescribing - Inpatient Diabetes Management"


def _q(stem, opts, ans, expl, points):
    return {
        "question_text": stem,
        "options": [f"{chr(65 + i)}) {o}" for i, o in enumerate(opts)],
        "correct_answer_letter": ans,
        "explanation": expl,
        "key_learning_points": points,
        "image_url": "",
        "source_page": "",
        "source_type": "llp",
    }


# ===========================================================================
# UNIT 4 — ANTICOAGULATION AND ANTIPLATELETS (MCQ)
# ===========================================================================

_ANTICOAG_MCQ = [

    _q("A 68-year-old man is admitted to the medical ward with acute decompensated heart failure. On examination he has bilateral pitting oedema to the mid-calf and bibasal crackles. Baseline bloods show a platelet count of 42 x 10^9/L, haemoglobin 115 g/L and a creatinine clearance of 45 mL/min. The team is completing the Queensland Adult VTE Risk Assessment Tool.\n\nWhich one of the following is an absolute contraindication to pharmacological VTE prophylaxis in this patient?",
       ["Age of 68 years",
        "Creatinine clearance of 45 mL/min",
        "Platelet count of 42 x 10^9/L",
        "Acute decompensated heart failure",
        "Bilateral pitting lower limb oedema"],
       "C",
       "Thrombocytopenia with a platelet count below 50 x 10^9/L is an absolute contraindication to pharmacological VTE prophylaxis. At 42 x 10^9/L this patient is below that threshold, and the bleeding risk outweighs the thrombotic benefit. Mechanical prophylaxis should be used instead.\n"
       "* Age alone is a VTE risk factor, not a contraindication.\n"
       "* A CrCl of 45 mL/min requires no dose adjustment for either UFH or LMWH — adjustment starts below 30 mL/min.\n"
       "* Decompensated heart failure requiring admission is an indication for prophylaxis, not a reason to withhold it, and the oedema is a consequence of it.",
       ["Platelets below 50 x 10^9/L is an absolute contraindication to pharmacological VTE prophylaxis.",
        "When pharmacological prophylaxis is contraindicated, mechanical prophylaxis should still be offered.",
        "Mild to moderate renal impairment is not a contraindication — it is a dose-adjustment consideration."]),

    _q("A 28-year-old woman presents to the antenatal clinic at 10 weeks gestation. She has a mechanical mitral valve replaced three years ago for rheumatic heart disease and takes warfarin. She asks about her ongoing anticoagulation.\n\nWhich one of the following statements is correct?",
       ["Warfarin is preferred throughout pregnancy because it does not cross the placenta",
        "Pregnancy is an absolute contraindication to warfarin because of teratogenicity",
        "Warfarin should be switched immediately to rivaroxaban",
        "Warfarin can be continued through all three trimesters without monitoring",
        "Warfarin need only be withheld in the third trimester"],
       "B",
       "Warfarin crosses the placenta and is teratogenic (fetal warfarin syndrome), and it also carries a risk of fetal haemorrhage. Pregnancy is listed as an absolute contraindication.\n"
       "This does not mean she goes unanticoagulated — a mechanical mitral valve is a high thrombotic risk. Therapeutic LMWH is the standard alternative, and management belongs with a specialist obstetric/cardiology team.\n"
       "* DOACs are not approved in pregnancy either, so rivaroxaban is not an escape route.\n"
       "* Warfarin does cross the placenta, and the risk is not limited to the third trimester (the teratogenic window is first-trimester).",
       ["Pregnancy is an absolute contraindication to warfarin.",
        "DOACs are also not used in pregnancy; therapeutic LMWH is the standard alternative.",
        "A mechanical mitral valve still requires anticoagulation in pregnancy — the agent changes, not the indication."]),

    _q("An 82-year-old woman is discharged from the orthopaedic ward after a right total hip replacement. Three weeks later she presents with pleuritic chest pain and breathlessness, and a CTPA confirms a segmental pulmonary embolism. Her discharge summary shows no post-discharge chemical VTE prophylaxis was prescribed.\n\nThis scenario represents which one of the following recognised preventable incidents?",
       ["Concomitant therapeutic and prophylactic prescription",
        "Anticoagulant omission on discharge resulting in PE",
        "Out-of-hours anticoagulation dosing error",
        "Drug interaction leading to major bleeding",
        "Under-anticoagulation due to poor patient compliance"],
       "B",
       "Anticoagulant omission on discharge resulting in PE is one of the named major preventable incidents in anticoagulant prescribing. Major orthopaedic surgery requires extended prophylaxis well beyond the inpatient stay — up to 5 weeks after total hip replacement.\n"
       "Safe transition of care requires the prophylaxis plan to be documented, prescribed, and communicated to the GP. The VTE Prevention Clinical Care Standard makes this explicit (Quality Statement 7: communicate the discharge plan within 48 hours).\n"
       "* The other options are all real preventable incidents, but none of them describes what happened here: nothing was prescribed at all.",
       ["Omission of prophylaxis at discharge is a leading preventable cause of post-operative PE.",
        "Total hip replacement requires extended prophylaxis — up to 5 weeks — not just while an inpatient.",
        "The VTE prevention plan must be communicated to the GP or ongoing clinician within 48 hours of discharge."]),

    _q("A 45-year-old man is admitted to the trauma ward after a motor vehicle accident. He underwent an urgent craniotomy and evacuation of an extradural haematoma four days ago. He is bedbound. He has no active bleeding and his platelets are 160 x 10^9/L. The team wishes to start pharmacological VTE prophylaxis.\n\nHow long must elapse after a high bleeding risk neurosurgical procedure before pharmacological prophylaxis can be considered?",
       ["24 hours", "48 hours", "7 days", "2 weeks", "4 weeks"],
       "D",
       "Surgical procedures with a high bleeding risk — head and neck surgery, neurosurgery, eye surgery — are an absolute contraindication to pharmacological VTE prophylaxis within the preceding two weeks.\n"
       "At four days post-craniotomy this patient is squarely within that window. He is nevertheless bedbound and at high VTE risk, so mechanical prophylaxis should be applied in the interim and his risk reassessed (the standard requires reassessment at intervals no longer than 7 days, or whenever the clinical condition changes).",
       ["Pharmacological VTE prophylaxis is absolutely contraindicated within 2 weeks of high bleeding risk surgery.",
        "Neurosurgery, head and neck surgery and eye surgery are the named high bleeding risk procedures.",
        "Use mechanical prophylaxis while pharmacological prophylaxis is contraindicated, and reassess at least every 7 days."]),

    _q("A 74-year-old man with chronic kidney disease and poorly controlled hypertension is admitted with acute cholecystitis. His blood pressure is 235/125 mmHg. His platelet count is 180 x 10^9/L and haemoglobin 130 g/L.\n\nAt what blood pressure threshold does uncontrolled hypertension become an absolute contraindication to pharmacological VTE prophylaxis?",
       ["140/90 mmHg or higher", "160/100 mmHg or higher", "180/110 mmHg or higher",
        "200/110 mmHg or higher", "230/120 mmHg or higher"],
       "E",
       "Uncontrolled systolic hypertension at or above 230/120 mmHg is an absolute contraindication to pharmacological VTE prophylaxis. At this pressure the risk of haemorrhagic stroke and other major bleeding is prohibitive.\n"
       "This is a contraindication that can be reversed: it is not a permanent bar. Once the blood pressure is controlled below the threshold, prophylaxis should be reassessed and started. In the meantime, mechanical prophylaxis applies.",
       ["Uncontrolled hypertension at or above 230/120 mmHg is an absolute contraindication to pharmacological VTE prophylaxis.",
        "This contraindication is reversible — reassess once the blood pressure is controlled."]),

    _q("A 62-year-old man had a large anterior myocardial infarction six months ago. A routine echocardiogram shows an ejection fraction of 30%, severe apical dyskinesis, left mural dilatation, and a well-formed mural thrombus at the left ventricular apex. He is in sinus rhythm.\n\nHow are left mural dilatation and mural thrombus classified in the indications for anticoagulation?",
       ["Contraindications to anticoagulation",
        "Indications for antiplatelet therapy only",
        "Indications for primary prevention of thromboembolism",
        "Indications for emergency thrombolysis",
        "Situations in which anticoagulation has no proven role"],
       "C",
       "Left mural dilatation and mural thrombus sit under the primary prevention indications for anticoagulation, alongside AF, mechanical heart valves and post-CVA stroke prevention.\n"
       "The mechanism is Virchow's triad in miniature: a dilated, dyskinetic ventricle produces stasis, thrombus forms on the damaged endocardium, and anticoagulation is given to prevent that thrombus embolising to the brain or systemic circulation.\n"
       "* Antiplatelet therapy alone is inadequate for an established mural thrombus.\n"
       "* Thrombolysis has no role here — the thrombus is not causing acute arterial occlusion.",
       ["Left mural dilatation and mural thrombus are primary prevention indications for anticoagulation.",
        "Ventricular stasis and endocardial injury drive thrombus formation — two of the three limbs of Virchow's triad.",
        "Antiplatelet therapy is not a substitute for anticoagulation in an established mural thrombus."]),

    _q("An intern is categorising a patient's antithrombotic medications on the ward round. The patient takes aspirin, clopidogrel, apixaban and subcutaneous enoxaparin.\n\nWhich one of the following classifications is correct?",
       ["Aspirin and clopidogrel are oral anticoagulants; apixaban is an antiplatelet",
        "Enoxaparin is an oral direct thrombin inhibitor; apixaban is a parenteral anticoagulant",
        "Clopidogrel is an antiplatelet; apixaban is an oral direct-acting factor Xa inhibitor; enoxaparin is a parenteral Xa inhibitor",
        "Aspirin is a thrombolytic; clopidogrel is an oral anticoagulant; apixaban is a direct thrombin inhibitor",
        "Enoxaparin is a thrombolytic; apixaban is a vitamin K antagonist"],
       "C",
       "Clopidogrel is an antiplatelet (P2Y12 inhibitor). Apixaban is a DOAC and a direct-acting oral factor Xa inhibitor, as is rivaroxaban; dabigatran is the direct thrombin inhibitor in that class. Enoxaparin is a parenteral (subcutaneous) LMWH acting principally on factor Xa.\n"
       "Getting the classes right is not an academic exercise: it is how you avoid prescribing two agents from the same class, and how you know which reversal agent applies when the patient bleeds.",
       ["Apixaban and rivaroxaban are oral factor Xa inhibitors; dabigatran is the oral direct thrombin inhibitor.",
        "Enoxaparin and dalteparin are parenteral LMWHs acting on factor Xa.",
        "Knowing the class prevents duplicate prescribing and determines which reversal agent applies."]),

    _q("A 72-year-old man is brought to the resuscitation bay with severe epistaxis and haematemesis. He has non-valvular AF and takes dabigatran. His thrombin time is markedly prolonged. The emergency physician gives idarucizumab.\n\nWhich one of the following describes the mode of action of idarucizumab?",
       ["An essential cofactor in the synthesis of factors II, VII, IX and X",
        "A humanised monoclonal antibody that binds dabigatran and its metabolites to form a stable inactive complex",
        "It combines with heparin to form a stable inactive complex",
        "An active site inhibitor of factor Xa",
        "An oral direct thrombin inhibitor"],
       "B",
       "Idarucizumab is a humanised monoclonal antibody that binds dabigatran and its metabolites with very high affinity, forming a stable inactive complex and reversing the anticoagulant effect.\n"
       "It is specific to dabigatran and does nothing for warfarin or heparin.\n"
       "* Option A describes vitamin K (phytomenadione), which reverses vitamin K antagonists.\n"
       "* Option C describes protamine, which reverses heparin.\n"
       "* Option E describes dabigatran itself.",
       ["Idarucizumab (Praxbind) is the specific reversal agent for dabigatran.",
        "It binds dabigatran with high affinity to form an inactive complex.",
        "Vitamin K reverses warfarin; protamine reverses heparin — the agents are not interchangeable."]),

    _q("A 45-year-old woman has an elective laparoscopic cholecystectomy. Two weeks later she develops calf pain and swelling, and an ultrasound confirms a distal DVT in the left calf, attributed to the surgery.\n\nAccording to the THANZ guidance, what is the recommended duration of oral anticoagulation for a distal DVT caused by a major provoking factor that is no longer present?",
       ["6 weeks", "3 months", "6 months", "12 months", "Indefinitely"],
       "A",
       "A distal DVT caused by a major provoking factor that has resolved is treated with 6 weeks of oral anticoagulation (THANZ: strong recommendation, moderate evidence).\n"
       "The logic is that distal DVT has a lower risk of propagation and recurrence than proximal DVT, and once the provoking factor is gone the ongoing risk falls away. A shorter course limits the patient's cumulative bleeding exposure.\n"
       "* 3 months applies to distal DVT that was unprovoked or has persisting risk factors, and to proximal DVT or PE provoked by surgery or trauma that is no longer present.",
       ["Provoked distal DVT with a resolved major provoking factor: 6 weeks of anticoagulation.",
        "Unprovoked distal DVT, or persisting risk factors: 3 months.",
        "All proximal DVT and PE should receive at least 3 months."]),

    _q("A 50-year-old man presents with right calf pain. A Doppler ultrasound shows a distal DVT. He has had no recent surgery, trauma, immobility, or other identifiable provoking factor.\n\nWhat is the recommended duration of oral anticoagulation?",
       ["6 weeks", "3 months", "6 months", "12 months", "Indefinitely"],
       "B",
       "An unprovoked distal DVT — or one with persisting risk factors — is treated for 3 months (THANZ: strong recommendation, moderate evidence).\n"
       "Because there is no reversible cause, the baseline risk of recurrence is higher than for a provoked event, so the 6-week course used for provoked distal DVT is extended to 3 months.",
       ["Unprovoked distal DVT, or distal DVT with persisting risk factors: 3 months of oral anticoagulation.",
        "The absence of a reversible provoking factor is what drives the longer duration."]),

    _q("A 58-year-old woman with active metastatic breast cancer on chemotherapy is diagnosed with an acute proximal DVT and segmental PE. Her platelets are 150 x 10^9/L and her renal function is normal.\n\nWhat is the recommended treatment and duration?",
       ["Warfarin for 3 months",
        "Aspirin monotherapy for at least 6 months",
        "Therapeutic LMWH, apixaban or rivaroxaban for at least 6 months",
        "Clopidogrel for 12 months",
        "UFH infusion for 6 weeks, then cease"],
       "C",
       "Cancer-associated VTE is treated with therapeutic LMWH, apixaban or rivaroxaban for at least 6 months (THANZ: strong recommendation, high evidence).\n"
       "Active malignancy is a persistent, strongly prothrombotic state, so treatment is longer than the standard 3 months. LMWH and the two named DOACs outperform warfarin in this population.\n"
       "* Aspirin monotherapy should be avoided for DVT/PE unless anticoagulation genuinely cannot be used.",
       ["Cancer-associated VTE: therapeutic LMWH, apixaban or rivaroxaban for at least 6 months.",
        "Warfarin is not the preferred agent in cancer-associated thrombosis.",
        "Aspirin monotherapy is not adequate treatment for DVT or PE."]),

    _q("An 80-year-old man weighing 75 kg is admitted with an infective exacerbation of COPD. His creatinine clearance is 65 mL/min. He has no contraindications to anticoagulation and needs pharmacological VTE prophylaxis.\n\nWhich one of the following is a correct standard medical VTE prophylaxis regimen?",
       ["Enoxaparin 20 mg subcutaneously once daily",
        "Dalteparin 5000 units subcutaneously once daily",
        "Unfractionated heparin 5000 units subcutaneously once weekly",
        "Rivaroxaban 20 mg orally once daily",
        "Apixaban 5 mg orally twice daily"],
       "B",
       "The standard medical prophylaxis options are dalteparin 5000 units subcut daily, enoxaparin 40 mg subcut daily, or UFH 5000 units subcut every 8 to 12 hours.\n"
       "* Enoxaparin 20 mg daily is the reduced dose for CrCl 15 to 29 mL/min — his renal function does not call for it.\n"
       "* UFH must be given 8 to 12 hourly; once weekly is meaningless.\n"
       "* Rivaroxaban 20 mg daily and apixaban 5 mg twice daily are treatment doses, not prophylactic doses. The prophylactic DOAC doses (rivaroxaban 10 mg daily, apixaban 2.5 mg twice daily) are used after hip and knee replacement, not for general medical patients.",
       ["Standard medical prophylaxis: dalteparin 5000 units daily, enoxaparin 40 mg daily, or UFH 5000 units 8-12 hourly.",
        "Enoxaparin 20 mg daily is the renally reduced dose, not the standard dose.",
        "Rivaroxaban 20 mg daily and apixaban 5 mg BD are treatment, not prophylactic, doses."]),

    _q("A 55-year-old woman is scheduled for an elective laparoscopic hemicolectomy tomorrow morning. Her baseline bloods and renal function are normal. You are asked to prescribe her perioperative enoxaparin prophylaxis.\n\nWhat is the standard surgical VTE prophylaxis regimen for enoxaparin?",
       ["20 mg subcutaneously 2 hours preoperatively, then 20 mg daily",
        "40 mg subcutaneously 12 hours preoperatively, then 40 mg daily",
        "40 mg subcutaneously 2 hours preoperatively, then 40 mg twice daily",
        "80 mg subcutaneously once daily starting 24 hours postoperatively",
        "1 mg/kg subcutaneously twice daily starting preoperatively"],
       "B",
       "Surgical prophylaxis with enoxaparin is 40 mg subcut 12 hours preoperatively, then 40 mg daily thereafter.\n"
       "The 12-hour gap matters: it gives cover through the procedure while allowing the anticoagulant effect to fall far enough by the time of skin incision to avoid intraoperative bleeding. Compare UFH, which is given 2 hours preoperatively because of its much shorter half-life.\n"
       "* 1 mg/kg twice daily is a treatment dose, not prophylaxis.",
       ["Surgical enoxaparin prophylaxis: 40 mg subcut 12 hours preoperatively, then 40 mg daily.",
        "UFH surgical prophylaxis: 5000 units subcut 2 hours preoperatively, then 8-12 hourly.",
        "The preoperative timing differs by agent because the half-lives differ."]),

    _q("A 65-year-old man is having an elective total knee replacement. His creatinine clearance is above 80 mL/min. The orthopaedic team plans oral rivaroxaban for post-operative VTE prophylaxis.\n\nWhat is the correct dose, initiation timing and duration?",
       ["10 mg once daily, starting 6 to 10 hours after surgery, for a maximum of 2 weeks",
        "10 mg once daily, starting 1 to 2 hours after surgery, for a maximum of 5 weeks",
        "20 mg once daily, starting 12 to 24 hours after surgery, for a maximum of 5 weeks",
        "2.5 mg twice daily, starting 6 to 10 hours after surgery, for a maximum of 10 to 14 days",
        "15 mg twice daily, starting 24 hours after surgery, for a maximum of 6 weeks"],
       "A",
       "Rivaroxaban for orthopaedic prophylaxis is 10 mg once daily, started 6 to 10 hours after surgery once haemostasis is established. Duration is 2 weeks after total knee replacement and up to 5 weeks after total hip replacement.\n"
       "The delay to first dose is deliberate — starting too early risks wound haematoma.\n"
       "* 2.5 mg twice daily is the apixaban prophylactic dose.\n"
       "* 20 mg daily and 15 mg twice daily are rivaroxaban treatment doses.",
       ["Rivaroxaban orthopaedic prophylaxis: 10 mg once daily, starting 6-10 hours post-op.",
        "Duration: 2 weeks for TKR, up to 5 weeks for THR.",
        "The first dose waits until haemostasis is established."]),

    _q("A 70-year-old woman undergoes an elective total hip replacement. Her renal function is normal. The surgeon requests apixaban for VTE prophylaxis.\n\nWhat is the correct dose, initiation timing and duration?",
       ["2.5 mg twice daily, starting 12 to 24 hours after surgery, for a maximum of 32 to 38 days",
        "5 mg twice daily, starting 6 to 10 hours after surgery, for a maximum of 5 weeks",
        "2.5 mg once daily, starting 24 hours after surgery, for a maximum of 10 to 14 days",
        "10 mg twice daily, starting 12 to 24 hours after surgery, for a maximum of 32 to 38 days",
        "2.5 mg twice daily, starting 6 to 10 hours after surgery, for a maximum of 10 to 14 days"],
       "A",
       "Apixaban for orthopaedic prophylaxis is 2.5 mg twice daily, started 12 to 24 hours after surgery. Duration is 32 to 38 days after total hip replacement, and 10 to 14 days after total knee replacement.\n"
       "Note the contrast with rivaroxaban, which starts earlier (6 to 10 hours) and is dosed once daily. Mixing up the two is a classic prescribing error.\n"
       "* 5 mg twice daily and 10 mg twice daily are apixaban treatment doses.",
       ["Apixaban orthopaedic prophylaxis: 2.5 mg twice daily, starting 12-24 hours post-op.",
        "Duration: 32-38 days for THR, 10-14 days for TKR.",
        "Rivaroxaban starts at 6-10 hours and is once daily; apixaban starts at 12-24 hours and is twice daily."]),

    _q("A 79-year-old man with stage 4 chronic kidney disease is admitted with a severe urinary tract infection. He weighs 70 kg and his creatinine clearance is 22 mL/min. The team wants to prescribe enoxaparin for VTE prophylaxis.\n\nWhat is the correct prophylactic enoxaparin dose for this patient?",
       ["40 mg subcutaneously once daily",
        "40 mg subcutaneously twice daily",
        "20 mg subcutaneously once daily",
        "1 mg/kg subcutaneously twice daily",
        "Enoxaparin is contraindicated at this creatinine clearance"],
       "C",
       "For a CrCl of 15 to 29 mL/min, prophylactic enoxaparin must be reduced to 20 mg subcut daily. LMWH is partly renally cleared, so at standard dose it accumulates and the bleeding risk climbs.\n"
       "Two contrasts worth holding onto: dalteparin requires no dose reduction in this range, and UFH requires no reduction at any level of renal function.\n"
       "* Enoxaparin is not contraindicated until CrCl falls below 15 mL/min — at that point LMWH should not be used at all and UFH is preferred.",
       ["CrCl 15-29 mL/min: reduce prophylactic enoxaparin to 20 mg subcut daily.",
        "Dalteparin needs no reduction in that range; UFH needs no reduction at any CrCl.",
        "LMWH is contraindicated below a CrCl of 15 mL/min."]),

    _q("An 83-year-old woman with end-stage kidney disease is admitted with urosepsis. Her creatinine clearance is 10 mL/min and she is not on dialysis. The intern is about to prescribe enoxaparin 20 mg subcut daily for VTE prophylaxis.\n\nWhat is the most appropriate action?",
       ["Proceed with enoxaparin 20 mg daily, as it is already the reduced dose",
        "Change to dalteparin 2500 units subcutaneously daily",
        "Do not use LMWH — prescribe UFH or seek specialist advice",
        "Change to apixaban 2.5 mg twice daily",
        "Proceed with enoxaparin 40 mg daily and monitor anti-Xa levels"],
       "C",
       "Below a CrCl of 15 mL/min, LMWH should not be used at all — neither enoxaparin nor dalteparin, and dose reduction does not rescue it. Clearance is so prolonged that accumulation becomes unpredictable.\n"
       "UFH requires no renal adjustment because it is cleared hepatically and by the reticuloendothelial system, which makes it the agent of choice in severe renal failure.\n"
       "* Apixaban is contraindicated for prophylaxis below a CrCl of 25 mL/min, and rivaroxaban below 15 mL/min.",
       ["LMWH is contraindicated when CrCl is below 15 mL/min — dose reduction does not make it safe.",
        "UFH requires no renal dose adjustment and is preferred in severe renal failure.",
        "Prophylactic apixaban is contraindicated below CrCl 25 mL/min; rivaroxaban below 15 mL/min."]),

    _q("A 72-year-old woman is admitted for elective total hip replacement. Her serum creatinine is 165 micromol/L, giving a creatinine clearance of 22 mL/min. The registrar asks you to prescribe post-operative VTE prophylaxis using a DOAC.\n\nWhich one of the following is correct?",
       ["Rivaroxaban is contraindicated; apixaban 2.5 mg twice daily may be used with caution",
        "Apixaban is contraindicated; rivaroxaban 10 mg once daily may be used with caution",
        "Both apixaban and rivaroxaban are contraindicated",
        "Both may be used at standard doses without caution",
        "Dabigatran 150 mg twice daily is preferred"],
       "B",
       "In the CrCl 15 to 24 mL/min band, apixaban is contraindicated for VTE prophylaxis, while rivaroxaban 10 mg once daily may be used with caution. Rivaroxaban only becomes contraindicated below a CrCl of 15 mL/min or on dialysis.\n"
       "The two agents are not interchangeable at the bottom of the renal range, and this is the band where they diverge. Above CrCl 25 mL/min both are usable (apixaban 2.5 mg BD, rivaroxaban 10 mg daily), with caution between 25 and 29.",
       ["CrCl 15-24 mL/min: apixaban is contraindicated for prophylaxis; rivaroxaban 10 mg daily may be used with caution.",
        "Apixaban prophylaxis is contraindicated below CrCl 25 mL/min.",
        "Rivaroxaban prophylaxis is contraindicated below CrCl 15 mL/min or on dialysis."]),

    _q("A 42-year-old man with a BMI of 45 kg/m2 is admitted after a high-velocity motor vehicle crash with multiple lower limb fractures. He is at high risk of VTE and his renal function is normal.\n\nWhat is the recommended LMWH prophylaxis strategy for a patient with a BMI of 41 to 60?",
       ["Standard dose LMWH (enoxaparin 40 mg subcut daily)",
        "Seek specialist advice, as DOACs are preferred",
        "Adjusted LMWH: dalteparin 5000 units subcut twice daily (or 50 units/kg daily), or enoxaparin 40 mg subcut twice daily (or 0.5 mg/kg daily)",
        "Unfractionated heparin 5000 units subcut once daily",
        "Enoxaparin 20 mg subcut once daily"],
       "C",
       "For a BMI of 41 to 60, adjusted-dose LMWH is recommended regardless of whether the VTE risk is low, moderate or high: dalteparin 5000 units subcut BD or 50 units/kg daily, or enoxaparin 40 mg subcut BD or 0.5 mg/kg daily.\n"
       "Obese patients have an increased volume of distribution and do not follow a predictable dose-response relationship, so standard prophylactic doses are unlikely to be sufficient once BMI reaches 40.\n"
       "* Between BMI 30 and 40, standard dosing is acceptable at low or moderate VTE risk, with adjusted dosing considered only at high risk.\n"
       "* Above BMI 60, seek specialist advice.",
       ["BMI 41-60: use adjusted-dose LMWH at any VTE risk level.",
        "BMI 30-40: standard dose at low/moderate risk; consider adjusted dose at high risk.",
        "BMI above 60: seek specialist advice."]),

    _q("An 88-year-old frail woman is admitted after a mechanical fall with fractured pubic rami. She is bedbound and cachectic, weighing 42 kg. Her renal function is normal for her age.\n\nWhat is the recommended pharmacological VTE prophylaxis for a patient weighing less than 50 kg?",
       ["Standard enoxaparin 40 mg subcut daily",
        "Withhold all chemical prophylaxis, as the bleeding risk is too high",
        "Consider dalteparin 2500 units subcut daily or enoxaparin 20 mg subcut daily",
        "Apixaban 5 mg twice daily",
        "Unfractionated heparin 5000 units subcut every 8 hours"],
       "C",
       "In patients under 50 kg the evidence for LMWH is limited and careful clinical observation is needed. Consider dalteparin 2500 units subcut daily or enoxaparin 20 mg subcut daily — half the standard dose.\n"
       "A low volume of distribution means standard doses risk over-anticoagulation. But low body weight is not a contraindication: she is bedbound with a fracture, so withholding prophylaxis entirely would leave a high-risk patient unprotected.",
       ["Weight under 50 kg: consider enoxaparin 20 mg daily or dalteparin 2500 units daily.",
        "Extremes of body weight are a dose-adjustment issue, not a reason to withhold prophylaxis.",
        "Careful clinical observation is required, as the evidence base at weight extremes is limited."]),

    _q("A 75-year-old man weighing 80 kg presents with ischaemic chest pain and is diagnosed with an NSTEMI. His serum creatinine is 210 micromol/L, giving a creatinine clearance of 24 mL/min. The cardiology registrar asks you to prescribe therapeutic anticoagulation.\n\nWhich one of the following is the correct choice?",
       ["Enoxaparin 80 mg (1 mg/kg) subcutaneously twice daily",
        "Enoxaparin 40 mg subcutaneously once daily",
        "Unfractionated heparin: 60 units/kg IV bolus, then 12 units/kg/hr infusion",
        "Enoxaparin 120 mg (1.5 mg/kg) subcutaneously once daily",
        "Apixaban 5 mg twice daily"],
       "C",
       "Therapeutic enoxaparin is not recommended when kidney function is below 30 mL/min — UFH should be used instead. The NSTEMI UFH regimen is 60 units/kg IV bolus (maximum 5000 units), then 12 units/kg/hr infusion (maximum 1000 units/hr), titrated to APTT.\n"
       "Note the nuance for enoxaparin in ACS: doses generally stay at 1 mg/kg BD for the first 48 hours even with mildly impaired kidney function, with adjustment considered after that. But at a CrCl of 24 mL/min this patient is well past 'mild', and enoxaparin is contraindicated from the outset.\n"
       "* Apixaban has no role in the acute anticoagulation of NSTEMI.",
       ["Therapeutic enoxaparin is contraindicated when CrCl is below 30 mL/min — use UFH.",
        "NSTEMI UFH dose: 60 units/kg IV bolus (max 5000 units), then 12 units/kg/hr (max 1000 units/hr).",
        "Between CrCl 30-50 mL/min, continue monitoring kidney function and consider anti-Xa levels."]),

    _q("A 60-year-old man is admitted with a left femoral DVT. Before starting therapeutic enoxaparin, the intern performs a baseline clinical review.\n\nWhich one of the following baseline tests is used to screen for heparin-induced thrombocytopenia?",
       ["International normalised ratio (INR)",
        "Activated partial thromboplastin time (APTT)",
        "Platelet count on the full blood count",
        "Alanine aminotransferase (ALT)",
        "Creatinine clearance"],
       "C",
       "The platelet count on the FBC is the screening test for HIT. A baseline value is essential — HIT is diagnosed by a fall from baseline, so without one there is nothing to compare against.\n"
       "Seek advice if the baseline platelet count is already low (below 100 x 10^9/L), or if the haemoglobin is low.\n"
       "* INR is required if prescribing warfarin.\n"
       "* APTT is the monitoring test for IV UFH.\n"
       "* Kidney function determines LMWH dosing, and LFTs matter if there is cirrhosis or varices — but neither screens for HIT.",
       ["The baseline platelet count screens for HIT and provides the reference for later falls.",
        "Seek advice if the baseline platelet count is below 100 x 10^9/L.",
        "Baseline tests before anticoagulation: FBC, coagulation profile, kidney function, LFTs, and INR if prescribing warfarin."]),

    _q("A 55-year-old woman is started on therapeutic subcutaneous enoxaparin for a proximal DVT. The team is planning routine platelet monitoring to screen for HIT.\n\nWhat is the correct frequency of platelet monitoring for a patient on LMWH?",
       ["Daily",
        "At baseline, then at least three times per week from day 4 to day 14",
        "Every 4 to 6 hours",
        "Weekly for 6 weeks",
        "No platelet monitoring is required for LMWH — only for UFH"],
       "B",
       "For LMWH, platelets are checked at baseline and then at least three times per week from day 4 to day 14 (or until LMWH is stopped, whichever comes first). That window is chosen because HIT typically develops 5 to 10 days into therapy.\n"
       "Daily monitoring is reserved for UFH treatment, where the risk of HIT is roughly eight times higher than with LMWH.\n"
       "* HIT does occur with LMWH — less often than with UFH, but the risk is not zero, so monitoring is still required.",
       ["LMWH: platelets at baseline, then at least 3 times per week from day 4 to day 14.",
        "UFH treatment: platelets daily.",
        "HIT typically develops 5-10 days into heparin therapy; UFH carries about 8 times the risk of LMWH."]),

    _q("A 68-year-old man is started on warfarin as an inpatient for newly diagnosed atrial fibrillation.\n\nWhat is the recommended test and frequency of monitoring?",
       ["APTT, twice daily until stable",
        "INR, daily until therapeutic and stabilised",
        "Anti-Xa levels, once weekly",
        "Platelet count, three times per week",
        "INR, once every 6 months"],
       "B",
       "All inpatients initiated on warfarin need daily INR until it is therapeutic and stable. If a patient is admitted already on warfarin, monitor daily until stable, then every 2 to 3 days.\n"
       "Warfarin has a narrow therapeutic index and a highly variable dose response, which is exactly why frequent monitoring during initiation is non-negotiable.\n"
       "* APTT monitors IV UFH; anti-Xa monitors LMWH in selected patients; platelet counts screen for HIT on heparins.",
       ["Inpatients started on warfarin: daily INR until therapeutic and stable.",
        "Admitted already on warfarin: daily until stable, then every 2-3 days.",
        "Warfarin has a narrow therapeutic index and a variable dose-response — hence the frequent monitoring."]),

    _q("A 32-year-old woman at 24 weeks gestation is admitted with a DVT and started on therapeutic enoxaparin 1 mg/kg twice daily. The obstetric team requests anti-Xa monitoring.\n\nWhen should anti-Xa monitoring start, and when should the sample be taken relative to the dose?",
       ["After the first dose, with a sample 1 hour post-dose",
        "After the third or fourth dose, with a sample 4 hours post-dose",
        "After 14 days, with a sample 12 hours post-dose",
        "Daily, with a sample immediately before the next dose",
        "Anti-Xa monitoring is contraindicated in pregnancy — monitor APTT instead"],
       "B",
       "Anti-Xa monitoring starts after the third or fourth dose, with the sample taken 4 hours after the subcutaneous dose (aligned with local phlebotomy times).\n"
       "The timing is not arbitrary: steady state is reached after 3 to 4 doses, and 4 hours post-dose captures the peak level. Sample earlier and you are not at steady state; sample at trough and you are measuring the wrong thing.\n"
       "Anti-Xa is indicated in pregnancy, at extremes of body weight, and when eGFR is below 50 mL/min — all three are situations where the dose-response is unpredictable. For enoxaparin 1 mg/kg BD, the target peak is 0.5 to 1 unit/mL.",
       ["Anti-Xa: start after the 3rd or 4th dose, sample 4 hours post-dose (peak).",
        "Indications for anti-Xa monitoring: pregnancy, extremes of body weight, eGFR below 50 mL/min.",
        "Enoxaparin 1 mg/kg BD target peak anti-Xa: 0.5-1 unit/mL."]),

    _q("A 60-year-old man is receiving an IV unfractionated heparin infusion for an acute pulmonary embolism. The nurse asks how often the APTT should be checked.\n\nWhat is the correct frequency?",
       ["Every 12 hours until stable, then daily",
        "Every 4 to 6 hours until within range for 2 consecutive readings, then daily",
        "Once daily from initiation",
        "Every 2 hours indefinitely",
        "Only if clinical signs of bleeding occur"],
       "B",
       "APTT is checked every 4 to 6 hours until it is within range on two consecutive readings, then daily.\n"
       "UFH has a short half-life and a famously variable dose-response, so frequent checks are needed during titration. Once two consecutive readings are therapeutic, the infusion has stabilised and daily checks suffice.\n"
       "Remember that platelets also need checking daily on UFH, to screen for HIT.",
       ["IV UFH: APTT every 4-6 hours until in range on 2 consecutive readings, then daily.",
        "IV UFH also requires daily platelet counts to screen for HIT.",
        "Seek advice if platelets fall below 100 x 10^9/L or drop more than 30% from baseline."]),

    _q("A 69-year-old man is being discharged on rivaroxaban 20 mg once daily for long-term VTE treatment. The ward pharmacist asks you to counsel him on how to take it.\n\nWhat is the correct administration advice?",
       ["Take on an empty stomach, at least 1 hour before or 2 hours after meals",
        "Take with food",
        "Take with water only, avoiding dairy products within 4 hours",
        "Take at least 4 hours apart from any other oral medication",
        "Food has no effect on the absorption of rivaroxaban"],
       "B",
       "Rivaroxaban at the 15 mg and 20 mg doses should be taken with food to optimise absorption. Bioavailability at these doses is food-dependent, and taking it on an empty stomach risks subtherapeutic anticoagulation.\n"
       "This is a genuine point of difference from apixaban, which has no food requirement — worth being specific about at discharge, because the consequence of getting it wrong is a treatment failure that will not be obvious until the patient re-presents with a clot.",
       ["Rivaroxaban 15 mg and 20 mg doses must be taken with food to optimise absorption.",
        "Apixaban has no food requirement.",
        "Taking rivaroxaban on an empty stomach risks subtherapeutic anticoagulation."]),

    _q("A 54-year-old man with alcohol-related decompensated cirrhosis and known oesophageal varices is admitted with a new proximal DVT. The intern is preparing to prescribe anticoagulation.\n\nWhat is the recommended action?",
       ["Start therapeutic warfarin immediately without baseline bloods",
        "Prescribe low-dose aspirin instead, as it is safer",
        "Seek clinical advice before prescribing anticoagulants",
        "Double the standard DOAC dose to overcome hepatic impairment",
        "Anticoagulants are absolutely contraindicated — no treatment can be given"],
       "C",
       "Known cirrhotic liver disease or oesophageal varices means seeking advice before prescribing any anticoagulant. This is why LFTs are part of the baseline panel.\n"
       "Cirrhosis is a genuinely difficult balance: these patients bleed (varices, thrombocytopenia from hypersplenism, impaired factor synthesis) and clot (reduced synthesis of protein C, protein S and antithrombin). Neither risk cancels the other, and the choice of agent and dose needs specialist input.\n"
       "* Note that severe liver disease is also listed as a general absolute contraindication to anticoagulation — which is precisely why this needs a specialist decision rather than a reflex prescription.",
       ["Cirrhosis or oesophageal varices: seek specialist advice before prescribing any anticoagulant.",
        "Cirrhotic patients are simultaneously at higher risk of bleeding and of clotting.",
        "LFTs are part of the baseline panel before anticoagulation for exactly this reason."]),

    _q("A 66-year-old woman on rivaroxaban 20 mg daily for AF is admitted with persistent gross haematuria. She is haemodynamically stable (BP 125/80 mmHg, HR 78/min). Her haemoglobin has fallen from 135 g/L to 118 g/L. She has not required transfusion.\n\nHow is this bleeding classified, and what is the appropriate management?",
       ["Minor bleeding — local haemostatic measures and continue rivaroxaban",
        "Moderate bleeding — cease rivaroxaban, inform senior staff, consult haematology, provide haemodynamic support, and consider rescue therapy or platelets if indicated",
        "Severe bleeding — activate the massive transfusion protocol and give idarucizumab",
        "Minor bleeding — withhold one dose and restart the next day",
        "Moderate bleeding — perform emergency haemodialysis to clear the rivaroxaban"],
       "B",
       "Moderate bleeding is non-trivial bleeding with a haemoglobin fall of less than 20 g/L, or requiring fewer than two units of red cells. Her drop is 17 g/L and she has had no transfusion, so she is moderate — not severe, and certainly not minor.\n"
       "Management: escalate to senior staff, cease or withhold the anticoagulant, consult haematology, apply mechanical compression, support haemodynamically, and consider rescue therapy. Consider platelets if the count is below 70 x 10^9/L or she is on a concurrent antiplatelet.\n"
       "* Idarucizumab reverses dabigatran, not rivaroxaban.\n"
       "* Rivaroxaban is highly protein-bound and is not removed by haemodialysis.",
       ["Moderate bleeding: Hb fall below 20 g/L, or fewer than 2 units of red cells transfused.",
        "Severe bleeding: Hb fall of 20 g/L or more, 2 or more units transfused, bleeding at a critical site, or haemodynamic instability.",
        "Rivaroxaban and apixaban cannot be cleared by haemodialysis."]),

    _q("A 62-year-old man requires urgent reversal of IV unfractionated heparin during emergency coronary artery bypass grafting. The anaesthetist is preparing protamine sulphate. His history includes a vasectomy 10 years ago and type 2 diabetes managed with Protophane (isophane) insulin for 15 years.\n\nWhy is this patient at high risk of protamine-induced anaphylaxis?",
       ["His age and sex",
        "His long-term protamine-containing insulin and his previous vasectomy",
        "The concurrent use of unfractionated heparin",
        "The rate of intraoperative blood loss",
        "His normal renal function"],
       "B",
       "Patients at risk of protamine anaphylaxis are those who have previously received protamine, are on long-term protamine-containing insulin (such as Protophane), have had a vasectomy, or are allergic to fish or shellfish. This patient has two of those four.\n"
       "The mechanism is prior sensitisation: isophane insulins contain protamine to delay absorption, and vasectomy can provoke anti-protamine antibodies through disruption of the blood-testis barrier.\n"
       "In clinically significant bleeding the benefit of protamine usually still outweighs the risk — but these patients may need antihistamine and corticosteroid premedication and a MET trolley immediately available.",
       ["Protamine anaphylaxis risk: prior protamine exposure, protamine-containing (isophane) insulin, vasectomy, or fish/shellfish allergy.",
        "Protamine fully reverses UFH; it reverses LMWH only partially (around 60-80%).",
        "In significant bleeding the benefit usually outweighs the risk, but premedicate and have a MET trolley ready."]),

    _q("A 75-year-old man on apixaban 5 mg twice daily is admitted with a traumatic subdural haematoma after a fall. He is obtunded with a GCS of 9. His last apixaban dose was three hours ago. Neurosurgery requires reversal before an emergency craniotomy.\n\nWhich one of the following is the recommended approach?",
       ["Give idarucizumab intravenously",
        "Perform urgent haemodialysis to clear the apixaban",
        "Give Prothrombinex, consider tranexamic acid, and discuss recombinant activated factor VIIa with a haematologist",
        "Give high-dose protamine sulphate",
        "Give activated charcoal immediately"],
       "C",
       "There is no readily available specific antidote for apixaban or rivaroxaban in Australia — andexanet alfa is not TGA-approved. Management of critical bleeding therefore relies on prohaemostatic agents: Prothrombinex, tranexamic acid, and recombinant activated factor VIIa (NovoSeven) discussed with a haematologist if the patient is critical.\n"
       "* Idarucizumab is specific to dabigatran.\n"
       "* Protamine reverses heparins.\n"
       "* Apixaban is highly protein-bound and not dialysable.\n"
       "* Activated charcoal is only useful within 2 hours of ingestion, and here the dose was 3 hours ago — and in an obtunded patient going to theatre, charcoal carries a real aspiration risk.",
       ["There is no widely available specific antidote for apixaban or rivaroxaban in Australia.",
        "Critical Xa-inhibitor bleeding: Prothrombinex, tranexamic acid, and consider recombinant factor VIIa on haematology advice.",
        "Apixaban and rivaroxaban are not dialysable; activated charcoal only helps within 2 hours of ingestion."]),

    _q("An 80-year-old woman on dabigatran 110 mg twice daily for AF presents after vomiting fresh blood. She is hypotensive (BP 85/50 mmHg) and tachycardic (HR 115/min). Her last dose was four hours ago.\n\nWhich one of the following is the correct approach?",
       ["Give Prothrombinex and start haemodialysis as first-line therapy",
        "Give idarucizumab intravenously, and consider haemodialysis, which can remove up to 65% of dabigatran",
        "Give activated charcoal and high-dose protamine sulphate",
        "Give vitamin K and proceed to emergency endoscopy without reversal",
        "Transfuse platelets and fresh frozen plasma only"],
       "B",
       "Dabigatran has a specific reversal agent — idarucizumab — and it should be given immediately in life-threatening bleeding. Unlike the oral Xa inhibitors, dabigatran has low protein binding, so haemodialysis can remove up to 65% of the circulating drug and is a genuine option.\n"
       "* Activated charcoal would only help within 2 hours of ingestion; her last dose was 4 hours ago.\n"
       "* Protamine reverses heparin and vitamin K reverses warfarin — neither touches dabigatran.",
       ["Idarucizumab is first-line for life-threatening dabigatran-associated bleeding.",
        "Haemodialysis removes up to 65% of dabigatran (low protein binding) — unlike apixaban or rivaroxaban.",
        "Activated charcoal is only useful within 2 hours of ingestion."]),

    _q("An 81-year-old woman with non-valvular AF is being started on a DOAC for stroke prevention. She has hypertension and osteoarthritis. She weighs 58 kg and her serum creatinine is 145 micromol/L, giving a creatinine clearance of 32 mL/min.\n\nWhich one of the following is the correct choice and dose?",
       ["Rivaroxaban 20 mg once daily with food",
        "Apixaban 5 mg twice daily",
        "Apixaban 2.5 mg twice daily",
        "Dabigatran 150 mg twice daily",
        "Rivaroxaban is contraindicated at this level of renal function"],
       "C",
       "Apixaban in AF is reduced to 2.5 mg twice daily when CrCl is 25 mL/min or above AND the patient has at least two of: age 80 or older, body weight 60 kg or less, creatinine above 133 micromol/L. She meets all three (81 years, 58 kg, creatinine 145), and her CrCl of 32 is above 25 — so she takes the reduced dose.\n"
       "* Rivaroxaban at CrCl 31 to 49 mL/min is 15 mg once daily with food, not 20 mg — and it is not contraindicated until CrCl falls below 15.\n"
       "* Dabigatran would be 110 mg twice daily here (CrCl 30 to 50 mL/min is one of the criteria for the lower dose), not 150 mg.",
       ["Apixaban in AF: reduce to 2.5 mg BD if CrCl 25+ AND at least 2 of age 80+, weight 60 kg or less, creatinine above 133 micromol/L.",
        "Rivaroxaban in AF: 20 mg daily with food if CrCl 50+; 15 mg daily with food if CrCl 31-49.",
        "Dabigatran in AF: 110 mg BD if aged 75+, CrCl 30-50, or high bleeding risk."]),

    _q("A 72-year-old man on warfarin for non-valvular AF is scheduled for an elective laparoscopic hemicolectomy, a high bleeding risk procedure. He has hypertension, type 2 diabetes and stable ischaemic heart disease, and has never had a stroke or TIA. His CHA2DS2-VA score is 3.\n\nWhat is his thromboembolic risk stratum, and is perioperative bridging recommended?",
       ["High risk — bridging is recommended",
        "Moderate risk — assess case by case",
        "Low risk — bridging is not recommended",
        "High risk — bridging is not recommended",
        "Low risk — bridging is recommended"],
       "C",
       "AF patients with a CHA2DS2-VA score of 3 or less and no prior stroke or TIA are low risk (under 5% annual thromboembolic risk), and bridging is not recommended.\n"
       "Bridging is not a free good. In low-risk patients it substantially increases perioperative major bleeding without a meaningful reduction in stroke — and this is major abdominal surgery.\n"
       "* Moderate risk would be a CHA2DS2-VA of 4 or 5, or a score below 4 with a prior stroke/TIA/peripheral embolism more than 3 months ago.\n"
       "* High risk would be a score of 6 or more, a stroke or TIA in the last 3 months, or rheumatic valvular disease.",
       ["AF with CHA2DS2-VA 3 or less and no prior stroke/TIA: low risk, bridging not recommended.",
        "Moderate risk: CHA2DS2-VA 4-5. High risk: CHA2DS2-VA 6 or more, stroke/TIA within 3 months, or rheumatic valvular disease.",
        "Bridging low-risk patients increases bleeding without reducing stroke."]),

    _q("A 60-year-old man on rivaroxaban 20 mg once daily for an unprovoked proximal DVT is being transitioned to long-term warfarin at his own request.\n\nHow should the transition be managed?",
       ["Stop rivaroxaban and start warfarin immediately; check the INR in 5 days",
        "Overlap warfarin with rivaroxaban until the INR is therapeutic, testing the INR immediately before the next rivaroxaban dose",
        "Stop rivaroxaban, wait 48 hours, then start warfarin",
        "Give therapeutic UFH while starting warfarin",
        "Stop rivaroxaban and start warfarin once the PT is prolonged"],
       "B",
       "Overlap warfarin with rivaroxaban until the INR is therapeutic, and take the INR sample immediately before the next rivaroxaban dose.\n"
       "Two things are happening at once. First, warfarin takes several days to work because it must wait for existing clotting factors to be cleared — so an overlap is needed to avoid a subtherapeutic window. Second, rivaroxaban itself prolongs the INR, so a sample taken at peak would overstate the warfarin effect and you would stop the overlap too early. Sampling at trough minimises that interference.\n"
       "* Note the contrast with dabigatran to warfarin: the INR is unreliable until dabigatran has been ceased for at least 48 hours.",
       ["DOAC to warfarin: overlap until the INR is therapeutic.",
        "Take the INR immediately before the next DOAC dose (trough) to minimise the DOAC's effect on the reading.",
        "After dabigatran, the INR is unreliable until it has been ceased for at least 48 hours."]),

    _q("A 70-year-old woman on therapeutic subcutaneous enoxaparin for a PE develops worsening renal function and needs to be switched to an intravenous unfractionated heparin infusion.\n\nWhen should the UFH infusion be started, and is a bolus required?",
       ["Immediately, with a full 80 units/kg bolus",
        "10 to 12 hours after the last enoxaparin dose, and generally without a bolus",
        "1 to 2 hours after the last enoxaparin dose, with a full bolus",
        "24 hours after the last enoxaparin dose, with a full bolus",
        "Only once the anti-Xa level is undetectable"],
       "B",
       "When switching from LMWH to an IV UFH infusion, cease the LMWH and start the infusion 10 to 12 hours after the last dose — that is, when the next LMWH dose would have been due.\n"
       "A bolus is generally not required when switching from another anticoagulant, because the patient is already anticoagulated; giving one stacks the two agents and risks bleeding. The exception is when thrombosis risk is unusually high.\n"
       "* Compare the reverse direction: switching from a UFH infusion to LMWH, start the LMWH 1 to 2 hours after the infusion stops, because UFH clears quickly.",
       ["LMWH to UFH infusion: start 10-12 hours after the last LMWH dose (when the next dose was due).",
        "A bolus is generally NOT required when switching from another anticoagulant.",
        "UFH infusion to LMWH: start LMWH 1-2 hours after the infusion is ceased."]),
]


# ===========================================================================
# UNIT 3 — INPATIENT DIABETES MANAGEMENT (MCQ)
# ===========================================================================

_INSULIN_MCQ = [

    _q("A 45-year-old woman attends her GP for a routine check. She has a family history of type 2 diabetes but no symptoms. A fasting plasma glucose taken after an 8-hour fast is 7.2 mmol/L.\n\nWhich one of the following is the most appropriate interpretation?",
       ["She can be definitively diagnosed with diabetes on this single reading",
        "An HbA1c must be performed, and diabetes can only be diagnosed if it is 6.5% or above",
        "A repeat fasting glucose or an alternative diagnostic test is required to confirm the diagnosis in this asymptomatic patient",
        "An oral glucose tolerance test is the only acceptable confirmatory method",
        "She is not diabetic, as her fasting glucose is below 11.1 mmol/L"],
       "C",
       "Her fasting glucose of 7.2 mmol/L is above the diagnostic threshold of 7 mmol/L — but she is asymptomatic, and a single abnormal result in an asymptomatic person needs confirmation, either by repeating the same test or by a different validated test.\n"
       "The diagnostic criteria are: HbA1c 6.5% or above; fasting plasma glucose 7 mmol/L or above (fasting means at least 8 hours); OGTT 2-hour glucose 11.1 mmol/L or above; or classic hyperglycaemic symptoms plus a random glucose of 11.1 mmol/L or above.\n"
       "Note the asymmetry: it is the presence of symptoms that allows a single random glucose to be diagnostic. Without symptoms, confirm.",
       ["Fasting plasma glucose threshold for diabetes: 7 mmol/L or above, after at least 8 hours fasting.",
        "HbA1c threshold: 6.5% or above. OGTT 2-hour threshold: 11.1 mmol/L or above.",
        "An asymptomatic patient with one abnormal result requires a confirmatory test."]),

    _q("A 28-year-old man is brought to the emergency department after 48 hours of worsening illness. He has profound lethargy, persistent nausea, repeated vomiting and generalised abdominal pain. His BGL is 22.0 mmol/L.\n\nWhich one of the following is correct?",
       ["His nausea, vomiting and abdominal pain are hyperosmolar symptoms caused by osmotic diuresis",
        "The abdominal pain and vomiting point towards ketoacidosis",
        "Significant weight loss in this patient would reflect insulin resistance",
        "Polyuria, thirst and polydipsia are described as ketoacidotic symptoms",
        "This presentation is typical of uncomplicated type 2 diabetes"],
       "B",
       "Nausea, vomiting and abdominal pain are the symptoms that suggest ketoacidosis, and in a young patient with a BGL of 22 mmol/L that is the working diagnosis until proven otherwise. He needs fingerprick ketones and a venous blood gas now.\n"
       "The vocabulary matters here:\n"
       "* Polyuria, thirst and polydipsia are the hyperosmolar symptoms — they reflect hyperglycaemia and the resulting osmotic diuresis.\n"
       "* Weight loss reflects severe insulin deficiency, not resistance.\n"
       "* Nausea, vomiting and abdominal pain are the ketoacidotic symptoms.",
       ["Hyperosmolar symptoms: polyuria, thirst, polydipsia (osmotic diuresis).",
        "Ketoacidosis symptoms: nausea, vomiting, and abdominal pain.",
        "Weight loss at presentation reflects severe insulin deficiency."]),

    _q("A 31-year-old man is admitted with new-onset hyperglycaemia and the team is trying to determine whether he has type 1 or type 2 diabetes.\n\nWhich one of the following statements about the adjunctive tests is correct?",
       ["Absence of islet cell autoantibodies definitively rules out type 1 diabetes",
        "A low C-peptide measured with a matched glucose is consistent with loss of beta cell mass",
        "Genetic testing for MODY is indicated in older patients with positive autoantibodies",
        "CT abdomen is the primary imaging modality used to screen for MODY",
        "A high C-peptide confirms autoimmune type 1 diabetes"],
       "B",
       "C-peptide is co-secreted with endogenous insulin, so it is a marker of remaining beta cell function. A LOW C-peptide, interpreted alongside a matched glucose, is consistent with loss of beta cell mass and supports type 1 diabetes.\n"
       "The four adjunctive tests: autoantibodies (GAD, IA2, ZnT8) confirm islet cell autoimmunity; C-peptide with matched glucose assesses beta cell mass; genetic testing is considered in a YOUNGER patient with NEGATIVE antibodies and a suggestive family history (MODY); and anatomical imaging such as CT abdomen is for suspected pancreatic neoplasm.\n"
       "* Detection of antibodies confirms autoimmunity — but their absence does not definitively exclude type 1, so the clinical picture still governs.",
       ["Low C-peptide (with matched glucose) is consistent with loss of beta cell mass.",
        "Autoantibodies: GAD, IA2, ZnT8. Detection confirms islet cell autoimmunity.",
        "MODY genetic testing: younger patient, NEGATIVE antibodies, suggestive family history."]),

    _q("A consultant asks why it matters to record the specific subtype of diabetes a patient has.\n\nWhich one of the following is correct?",
       ["Correct subtyping gives type 1 patients access to fully subsidised SGLT2 inhibitors",
        "Subtyping is only relevant for epidemiological monitoring and does not alter prescribing",
        "Patients with type 1 diabetes require insulin and, once correctly identified, can register with the NDSS and access subsidised continuous glucose monitoring",
        "All patients with type 2 diabetes must start insulin at diagnosis",
        "Patients with type 1 diabetes can be safely managed on sulfonylureas if registered with the NDSS"],
       "C",
       "Getting the subtype right has three concrete consequences: it determines therapy (type 1 needs insulin; type 2 may be managed with non-insulin agents that have cardiac, renal or weight benefits), it enables NDSS registration for the right supplies and support, and it gives type 1 patients access to subsidised continuous glucose monitoring.\n"
       "* Sulfonylureas need functional beta cells to work — they are useless in type 1 diabetes, where beta cells have been destroyed.\n"
       "* Type 2 diabetes is not an automatic indication for insulin at diagnosis.",
       ["Correct subtyping determines therapy, NDSS registration, and access to subsidised CGM.",
        "Type 1 diabetes requires insulin — sulfonylureas need functional beta cells and cannot substitute.",
        "Type 2 diabetes does not require insulin at diagnosis."]),

    _q("An intern is reviewing hospital statistics on diabetes for a clinical improvement committee.\n\nWhich one of the following is correct?",
       ["Diabetes affects about 2% of Australians over 25, and rates are static",
        "Diabetes prevalence in the Aboriginal and Torres Strait Islander population is lower than in the general population",
        "About 5% of hospitalised patients have diabetes",
        "Diabetes is associated with a longer length of stay, on average about 2 days longer than in non-diabetic patients",
        "Oral agents are the leading cause of prescribing errors, while insulin is low risk"],
       "D",
       "Diabetes is associated with a length of stay roughly 2 days longer than in patients without diabetes.\n"
       "The other figures: it affects 7.4% of Australians over 25 and is rising by about 0.8% per year; prevalence is higher (14% or more) in the Aboriginal and Torres Strait Islander population; around 25% of hospitalised patients have diabetes; and there is roughly one undiagnosed person for every diagnosed person with type 2 diabetes.\n"
       "* Insulin is a HIGH-risk medication and a leading cause of medication prescribing errors — which is the whole reason this unit exists.",
       ["About 25% of hospitalised patients have diabetes, and they stay about 2 days longer.",
        "Prevalence is 7.4% in Australians over 25, and 14% or more in Aboriginal and Torres Strait Islander people.",
        "Insulin is a high-risk medication and a leading cause of prescribing errors."]),

    _q("A 58-year-old man with chronic kidney disease and severe anaemia has an HbA1c of 8.0%.\n\nWhich one of the following is correct regarding HbA1c, its interpretation and its limitations?",
       ["His average plasma glucose can be estimated as (2 x HbA1c) - 6, which gives 10 mmol/L",
        "HbA1c is a large fraction of haemoglobin formed by a rapid, insulin-dependent enzymatic process",
        "HbA1c remains fully reliable in abnormal cell turnover, pregnancy and renal disease",
        "Fructosamine reflects glycaemic control over the preceding 6 to 8 weeks",
        "In pregnancy, haemodilution causes HbA1c to be falsely elevated"],
       "A",
       "The rule of thumb for average glucose is (2 x HbA1c) - 6. For an HbA1c of 8.0%, that gives (2 x 8) - 6 = 10 mmol/L.\n"
       "But note the trap embedded in this stem: this patient has CKD and severe anaemia, so his HbA1c is unreliable in the first place. HbA1c is a non-enzymatic glycation product reflecting roughly 3 months of glycaemia (about 50% from the past month), and it is unreliable in abnormal red cell turnover, haemoglobinopathies, renal and liver disease, and pregnancy (haemodilution lowers it).\n"
       "* Fructosamine is the alternative when HbA1c cannot be trusted, and it reflects the preceding 2 to 3 weeks.",
       ["Average glucose estimate: (2 x HbA1c) - 6.",
        "HbA1c is unreliable in abnormal cell turnover, haemoglobinopathies, renal/liver disease and pregnancy.",
        "Fructosamine is the alternative marker and reflects the preceding 2-3 weeks."]),

    _q("A 50-year-old man is newly diagnosed with type 2 diabetes. His HbA1c is 7.5% and his renal and hepatic function are normal. The team is starting first-line therapy.\n\nWhich one of the following is correct?",
       ["Start metformin 1000 mg twice daily immediately; it works by increasing pancreatic insulin secretion",
        "Start metformin 500 mg daily or twice daily with food; it reduces hepatic gluconeogenesis, gives about a 1% HbA1c reduction, and is weight neutral",
        "Start metformin XR 2 g daily immediately; it carries a high risk of severe hypoglycaemia",
        "Start gliclazide 40 mg twice daily as the preferred Australian first-line agent",
        "Start metformin 500 mg daily; it is contraindicated in normal liver function"],
       "B",
       "Metformin is first line. Start at 500 mg once or twice daily with food, and uptitrate slowly to a maximum of 2 g/day. Its mechanism is reduced hepatic gluconeogenesis with improved insulin sensitivity.\n"
       "Its virtues are that it is cheap, gives a moderate glycaemic benefit (about 1% HbA1c reduction), is weight neutral, and carries no risk of hypoglycaemia — because it does not force insulin secretion.\n"
       "* 2 g/day is the maximum, not the starting dose; starting there guarantees GI intolerance.\n"
       "* Sulfonylureas — not metformin — stimulate insulin secretion and cause hypoglycaemia and weight gain.",
       ["Metformin: start 500 mg od or bd with food, uptitrate slowly to a maximum of 2 g/day.",
        "MOA: reduces hepatic gluconeogenesis and improves insulin sensitivity.",
        "Weight neutral, ~1% HbA1c reduction, no hypoglycaemia risk."]),

    _q("A 72-year-old woman with type 2 diabetes and chronic kidney disease has an eGFR that has fallen to 28 mL/min/1.73m2. She takes metformin IR 1 g twice daily.\n\nWhat is the most appropriate action?",
       ["Continue metformin 1 g twice daily, as her eGFR is above 15",
        "Reduce metformin to 500 mg twice daily (1 g/day)",
        "Stop metformin, as her eGFR is below 30",
        "Switch to metformin XR 2 g once daily, which is safer in renal impairment",
        "Continue the current dose and withhold only if severe liver disease develops"],
       "C",
       "Metformin must be stopped once eGFR falls below 30 mL/min/1.73m2 — it is contraindicated. Her eGFR is 28.\n"
       "The renal ladder: above 45, up to 2 g/day; 30 to 45, up to 1 g/day; below 30, stop.\n"
       "The concern is lactic acidosis. The absolute risk is low, but the mortality when it happens is high, which is why the threshold is treated as a hard stop rather than a suggestion. Severe liver disease is also a contraindication.",
       ["Metformin renal dosing: eGFR above 45, up to 2 g/day; eGFR 30-45, up to 1 g/day; eGFR below 30, STOP.",
        "Metformin is contraindicated in severe liver disease.",
        "The risk driving these limits is lactic acidosis — low absolute risk, high mortality."]),

    _q("A 65-year-old man with type 2 diabetes on metformin is admitted for an elective coronary angiogram with intravenous contrast, and an inguinal hernia repair later in the same admission.\n\nWhich one of the following is correct regarding his metformin?",
       ["Continue it throughout both procedures, as the risk of lactic acidosis is negligible",
        "Withhold it on the day of surgery, and also for the contrast study, because contrast-induced renal impairment can precipitate lactic acidosis, which carries a high mortality",
        "Withhold it for 72 hours before the contrast study but continue it through the hernia repair",
        "Double the dose before surgery to prevent stress hyperglycaemia",
        "Stop it only if his baseline eGFR is below 15 mL/min"],
       "B",
       "Metformin must be withheld for acute kidney injury, for CT contrast, and pre-operatively (on the same day).\n"
       "The common thread is anything that could acutely drop renal clearance. Contrast can precipitate acute kidney injury; metformin then accumulates; and although lactic acidosis is rare, its mortality is high enough that the precaution is worth taking.\n"
       "* 72 hours is the withholding period for SGLT2 inhibitors before a procedure (to avoid euglycaemic DKA), not for metformin.",
       ["Withhold metformin for AKI, for CT contrast, and on the day of surgery.",
        "The concern is accumulation causing lactic acidosis if renal clearance acutely falls.",
        "72 hours pre-procedure is the SGLT2 inhibitor rule, not the metformin rule."]),

    _q("A 78-year-old man is admitted with a urinary tract infection. He has type 2 diabetes, mild cognitive impairment, and a baseline eGFR of 35 mL/min/1.73m2. His home medications include glibenclamide 10 mg daily.\n\nWhy is glibenclamide particularly hazardous in this patient?",
       ["It is short-acting and carries no hypoglycaemia risk, but causes lactic acidosis in renal impairment",
        "It is a long-acting, renally cleared sulfonylurea with the highest risk of prolonged hypoglycaemia, especially in older patients with renal impairment",
        "It causes significant weight loss and volume depletion",
        "It only secretes insulin when the BGL is above 15 mmol/L",
        "It doubles the risk of heart failure hospitalisation compared to other sulfonylureas"],
       "B",
       "Glibenclamide should be avoided: it is long-acting, renally cleared, and carries the highest hypoglycaemia risk of the sulfonylureas. Every feature of this patient compounds that — he is old, renally impaired, cognitively impaired (so may not recognise or report hypos), and acutely unwell.\n"
       "Gliclazide and glipizide are the safer choices in older patients and renal impairment, though glucose monitoring is still required.\n"
       "* Sulfonylureas cause weight GAIN, not loss, and act in a glucose-INDEPENDENT manner — which is precisely why they cause hypoglycaemia.\n"
       "* Increased heart failure hospitalisation is a saxagliptin (DPP4 inhibitor) concern.",
       ["Avoid glibenclamide: long-acting, renally cleared, highest hypoglycaemia risk.",
        "Sulfonylureas act glucose-INDEPENDENTLY — hence hypoglycaemia and weight gain.",
        "Gliclazide and glipizide are safer in older patients and renal impairment."]),

    _q("You are writing discharge prescriptions for patients starting sulfonylureas.\n\nWhich one of the following dosing regimens is correct?",
       ["Gliclazide IR 80 mg once daily at night",
        "Gliclazide IR 40 to 160 mg twice daily, with breakfast and dinner",
        "Gliclazide MR 30 to 120 mg twice daily, with meals",
        "Glipizide 5 to 20 mg once daily at night",
        "Glimepiride 1 to 4 mg twice daily, with breakfast and dinner"],
       "B",
       "Gliclazide IR is 40 to 160 mg twice daily, taken with breakfast and dinner — dosed with meals, because it drives insulin secretion regardless of glucose and would otherwise cause hypoglycaemia.\n"
       "The rest of the ladder: gliclazide MR 30 to 120 mg DAILY (the modified-release formulation is the whole point); glipizide 5 to 20 mg twice daily; glimepiride 1 to 4 mg daily.\n"
       "Note that the IR/MR distinction changes the frequency — a classic transcription error on discharge.",
       ["Gliclazide IR: 40-160 mg BD with breakfast and dinner. Gliclazide MR: 30-120 mg daily.",
        "Glipizide: 5-20 mg BD. Glimepiride: 1-4 mg daily.",
        "Sulfonylureas are dosed with meals because they act glucose-independently."]),

    _q("A 62-year-old man with type 2 diabetes and heart failure with reduced ejection fraction is admitted with mild fluid overload. The team wants to optimise his diabetes medications to help his heart failure.\n\nWhich one of the following correctly describes the most appropriate class?",
       ["DPP4 inhibitors — they inhibit SGLT2 in the proximal tubule and reduce heart failure hospitalisation",
        "GLP-1R agonists — they stimulate PPAR-gamma, promoting fluid excretion",
        "SGLT2 inhibitors — they inhibit SGLT2 in the proximal tubule, offering cardiac and renal benefit, but carry a rare risk of euglycaemic DKA",
        "Thiazolidinediones — they stimulate beta cells to release insulin and reduce myocardial strain",
        "SGLT2 inhibitors — they act on the distal tubule to increase glucose reabsorption and cause frequent hypoglycaemia"],
       "C",
       "SGLT2 inhibitors (empagliflozin, dapagliflozin) inhibit SGLT2 in the PROXIMAL tubule, which is responsible for 80 to 90% of glucose reabsorption. They lower the plasma glucose threshold for urinary glucose excretion.\n"
       "Their benefits go well beyond glycaemia: cardiac benefit (including in heart failure with or without diabetes), renal benefit (slowing diabetic nephropathy), modest weight loss of 2 to 3 kg, and a mild diuretic and BP-lowering effect. Their glycaemic effect is actually weak (about 0.5% HbA1c).\n"
       "Adverse effects: volume depletion, genitourinary infections, and rare euglycaemic DKA.\n"
       "* Thiazolidinediones (which do act on PPAR-gamma) cause fluid retention and are contraindicated in heart failure — the opposite of what he needs.",
       ["SGLT2 inhibitors act on the PROXIMAL tubule (80-90% of glucose reabsorption).",
        "Benefits: cardiac (including heart failure), renal, modest weight loss, mild diuresis. Weak glycaemic effect (~0.5%).",
        "Adverse effects: volume depletion, genitourinary infection, rare euglycaemic DKA."]),

    _q("An intern is preparing a discharge summary for a patient with type 2 diabetes and chronic kidney disease. The consultant wants to start an SGLT2 inhibitor.\n\nWhich one of the following is correct?",
       ["Dapagliflozin is PBS-subsidised as first-line monotherapy and can be started down to an eGFR of 15",
        "Empagliflozin is contraindicated if the eGFR is below 30, and dapagliflozin should not be started if the eGFR is below 25",
        "Ertugliflozin is preferred because it met its primary cardiovascular endpoint and is safe to an eGFR of 15",
        "SGLT2 inhibitors can be prescribed on the PBS concurrently with a GLP-1R agonist",
        "PBS subsidy requires an HbA1c above 9.0% despite triple oral therapy"],
       "B",
       "The renal thresholds differ by agent: do not START dapagliflozin below an eGFR of 25; empagliflozin is contraindicated below 30; ertugliflozin is contraindicated below 45.\n"
       "PBS rules: SGLT2 inhibitors are NOT subsidised as monotherapy. HbA1c must be above 7.0% despite monotherapy, and they must be combined with metformin, a sulfonylurea, or insulin. They cannot be co-prescribed with a GLP-1R agonist on the PBS (though a private script is possible).\n"
       "* Ertugliflozin is safe but did NOT meet significance for its primary cardiovascular endpoint — it is not the preferred agent.",
       ["Renal limits: dapagliflozin do not start below eGFR 25; empagliflozin contraindicated below 30; ertugliflozin below 45.",
        "PBS: not subsidised as monotherapy; requires HbA1c above 7.0% despite monotherapy.",
        "SGLT2 inhibitor and GLP-1R agonist cannot be co-prescribed on the PBS."]),

    _q("A 60-year-old woman on empagliflozin is admitted with acute cholecystitis and is scheduled for cholecystectomy in three days. She is nil by mouth and undergoing bowel preparation.\n\nWhat are the withholding rules for her SGLT2 inhibitor?",
       ["Continue it up to the morning of surgery to control stress hyperglycaemia",
        "Withhold it now for acute illness and prolonged fasting, and ensure it is stopped 72 hours before her procedure to limit the risk of euglycaemic DKA",
        "Withhold it only on the day of surgery — bowel prep does not affect it",
        "Withhold it for 24 hours post-operatively but continue it while fasting",
        "Withhold it only if she develops hypoglycaemia"],
       "B",
       "SGLT2 inhibitors MUST be withheld for acute serious illness, for prolonged fasting or bowel prep, and for 72 hours before a procedure — all to limit the risk of euglycaemic DKA. This patient triggers all three.\n"
       "The danger of euglycaemic DKA is that the BGL looks reassuring. In a fasting or acutely unwell patient the drug keeps driving glycosuria and ketogenesis while the glucose stays near-normal, so the diagnosis is missed unless ketones are actually checked.",
       ["Withhold SGLT2 inhibitors for acute serious illness, prolonged fasting or bowel prep, and 72 hours pre-procedure.",
        "The risk is euglycaemic DKA — the BGL can be normal while the patient is profoundly ketotic.",
        "Check ketones, not just glucose, in an unwell patient on an SGLT2 inhibitor."]),

    _q("A 55-year-old man with obesity, type 2 diabetes and established coronary artery disease has an HbA1c of 8.5% despite metformin 1 g twice daily. The team adds a GLP-1R agonist.\n\nWhich one of the following is correct?",
       ["They block DPP4 enzymes, causing weight loss and a 5% HbA1c reduction",
        "They stimulate insulin secretion glucose-independently, carry a high hypoglycaemia risk, and can be co-prescribed with DPP4 inhibitors on the PBS",
        "They act by glucose-dependent stimulation of insulin secretion, blunting of glucagon, slowed gastric emptying and reduced appetite; semaglutide and dulaglutide have proven cardiovascular benefit",
        "Dulaglutide requires a weekly uptitration schedule starting at 0.25 mg",
        "Oral semaglutide is widely available and PBS-subsidised in Australia"],
       "C",
       "GLP-1R agonists act by four mechanisms: glucose-DEPENDENT stimulation of insulin secretion (which is why they do not cause hypoglycaemia, unlike sulfonylureas), blunting of glucagon secretion, slowed gastric emptying, and centrally mediated appetite reduction.\n"
       "Benefits: cardiovascular benefit (particularly non-fatal stroke, shown for semaglutide and dulaglutide), significant weight loss, and a moderate-to-high glycaemic effect (about 2% HbA1c reduction). Main downside is that they are injectable.\n"
       "* It is semaglutide, not dulaglutide, that needs uptitration (0.25 mg to 1 mg weekly over 8 weeks) to reduce GI upset; dulaglutide 1.5 mg weekly needs none.\n"
       "* DPP4 inhibitors must be STOPPED when a GLP-1R agonist is started — the mechanisms overlap.",
       ["GLP-1RA MOA: glucose-dependent insulin secretion, blunted glucagon, slowed gastric emptying, reduced appetite.",
        "Benefits: ~2% HbA1c reduction, weight loss, cardiovascular benefit (semaglutide, dulaglutide).",
        "Stop DPP4 inhibitors when starting a GLP-1R agonist. Semaglutide needs uptitration; dulaglutide does not."]),

    _q("A 54-year-old woman with type 2 diabetes on weekly semaglutide has mild diabetic retinopathy and is admitted with severe acute pyelonephritis.\n\nWhich one of the following is correct?",
       ["Semaglutide is contraindicated in any patient with diabetic retinopathy because it damages the optic nerve",
        "Semaglutide should be continued during severe acute illness as it has no gastrointestinal side effects",
        "Semaglutide is contraindicated if there is a personal or family history of medullary thyroid carcinoma",
        "Semaglutide can be continued perioperatively and a weekly dose due immediately post-op must be given on time regardless",
        "Her retinopathy risk is increased because semaglutide causes severe hypoglycaemia"],
       "C",
       "A personal or family history of medullary thyroid carcinoma is an absolute contraindication to GLP-1R agonists.\n"
       "The cautions — as distinct from contraindications — are prior pancreatitis, diabetic retinopathy (the higher retinopathy rate with semaglutide is thought to reflect rapid glucose lowering, not direct toxicity), and eGFR below 30.\n"
       "In hospital: STOP GLP-1R agonists in severe illness or acute GI illness — which applies to this patient with severe pyelonephritis. Perioperatively they can be continued, but a weekly dose falling immediately post-op may be delayed by up to 3 days.",
       ["Absolute contraindication to GLP-1RA: personal or family history of medullary thyroid carcinoma.",
        "Cautions: prior pancreatitis, diabetic retinopathy, eGFR below 30.",
        "Stop GLP-1RA in severe illness or acute GI illness; post-op weekly doses may be delayed up to 3 days."]),

    _q("A 67-year-old woman with type 2 diabetes and heart failure with reduced ejection fraction takes metformin and saxagliptin.\n\nWhat is the key safety concern with saxagliptin in this patient?",
       ["It causes lactic acidosis in heart failure",
        "It is associated with an increased risk of heart failure hospitalisation",
        "It causes rapid weight gain of 5 to 10 kg in the first month",
        "It carries a high risk of euglycaemic diabetic ketoacidosis",
        "It routinely causes severe hypoglycaemia"],
       "B",
       "Saxagliptin is associated with an increased risk of heart failure hospitalisation — a class-specific concern that singles it out among the gliptins, and directly relevant in a patient who already has HFrEF.\n"
       "DPP4 inhibitors as a class are otherwise fairly benign but fairly unimpressive: weak glycaemic effect (about 0.5% HbA1c), weight neutral, no cardiac or renal benefit. Adverse effects include upper respiratory tract infections, headache and rare pancreatitis.\n"
       "* Lactic acidosis belongs to metformin; euglycaemic DKA to SGLT2 inhibitors; severe hypoglycaemia to sulfonylureas and insulin.",
       ["Saxagliptin: increased risk of heart failure hospitalisation.",
        "DPP4 inhibitors: weak HbA1c effect (~0.5%), weight neutral, no cardiorenal benefit.",
        "Adverse effects of gliptins: URTI, headache, rare pancreatitis."]),

    _q("An inpatient with type 2 diabetes has severe renal impairment (eGFR 20 mL/min/1.73m2). The team wants to prescribe a DPP4 inhibitor.\n\nWhich one of the following is correct?",
       ["Linagliptin 5 mg daily can be prescribed without dose reduction",
        "Sitagliptin 100 mg daily is preferred as it is safe at any level of renal impairment",
        "Vildagliptin 50 mg twice daily needs no dose adjustment in severe renal impairment",
        "All DPP4 inhibitors are contraindicated once the eGFR falls below 30",
        "Linagliptin must be reduced to 2.5 mg daily"],
       "A",
       "Linagliptin is the outlier among the gliptins: it is safe at any level of renal impairment and requires NO dose reduction, because it is cleared predominantly by a non-renal route.\n"
       "Every other gliptin — sitagliptin, vildagliptin, saxagliptin, alogliptin — requires dose reduction in CKD stages 3 to 5.\n"
       "That property makes linagliptin genuinely useful in the inpatient setting: it is one of the few non-insulin agents that can be continued in severe renal impairment, and it may be used in selected patients with mild hyperglycaemia.",
       ["Linagliptin 5 mg daily: safe at any level of renal impairment, no dose reduction.",
        "All other gliptins require dose reduction in CKD 3-5.",
        "Linagliptin may be used in selected inpatients with mild hyperglycaemia."]),

    _q("A 58-year-old man with type 2 diabetes, severe chronic kidney disease and NYHA class III heart failure has an HbA1c of 8.2%. The team is considering pioglitazone.\n\nWhich one of the following is correct?",
       ["Pioglitazone is safe here, as it reduces fluid retention and improves contractility",
        "Pioglitazone is contraindicated because it is renally cleared and needs a 75% dose reduction",
        "Pioglitazone should not be used because it causes fluid retention, oedema and weight gain, and is contraindicated in heart failure",
        "Pioglitazone is first-line in heart failure because of its lipid effects",
        "Pioglitazone is preferred because it carries no fracture risk in older adults"],
       "C",
       "Pioglitazone must not be used in heart failure. Thiazolidinediones stimulate PPAR-gamma, producing insulin sensitisation and a moderate glycaemic benefit (about 1% HbA1c), but their adverse effect profile is the problem: weight gain, fluid retention, oedema, heart failure and fractures.\n"
       "The one thing that would have made it attractive here — it can be used in renal failure without dose reduction — is completely outweighed by the heart failure contraindication.\n"
       "It is rarely initiated in contemporary practice, and this patient is precisely why.",
       ["Pioglitazone is contraindicated in heart failure.",
        "Adverse effects: weight gain, fluid retention, oedema, heart failure, fractures.",
        "It needs no dose reduction in renal impairment — but that does not rescue it in a patient with heart failure."]),

    _q("A 61-year-old man with type 2 diabetes has inadequate control despite optimal metformin and dapagliflozin. The consultant decides to start insulin.\n\nWhich one of the following is correct about starting insulin in type 2 diabetes?",
       ["Insulin is always started as a full basal-bolus regimen on day one",
        "Patients typically start with basal insulin plus ongoing oral therapies and/or a GLP-1R agonist",
        "All oral agents must be stopped the day insulin is started",
        "Sulfonylureas should be doubled when insulin is started",
        "Once insulin is started it can never be stopped"],
       "B",
       "Insulin in type 2 diabetes is introduced stepwise. The usual starting point is basal insulin, with oral therapies and/or a GLP-1R agonist continued. From there a patient may progress to pre-mixed or basal-bolus insulin.\n"
       "Sulfonylureas are the exception to 'continue the orals' — they are often STOPPED once quick-acting insulin is introduced, because stacking two agents that both drive insulin action markedly increases hypoglycaemia risk. Doubling them would be dangerous.\n"
       "Insulin is also not necessarily permanent: a newly diagnosed patient with uncontrolled diabetes may be stabilised on insulin, and once glucotoxicity resolves, non-insulin therapies can be introduced and insulin withdrawn.",
       ["Insulin in T2DM is stepwise: start with basal insulin plus ongoing orals and/or a GLP-1RA.",
        "Sulfonylureas are often stopped once quick-acting insulin is introduced, to reduce hypoglycaemia.",
        "Insulin can be withdrawn later in patients stabilised after acute glucotoxicity."]),

    _q("A 22-year-old woman with type 1 diabetes is admitted, and you are explaining the physiology of her insulin regimen to a medical student.\n\nWhich one of the following is correct?",
       ["Type 1 patients are insulin-resistant and can be managed on oral agents without DKA risk",
        "Insulin is split into basal (about 50% of the total daily dose) to prevent fasting hyperglycaemia and ketosis, and bolus/prandial (40 to 60% of TDD) to prevent post-prandial hyperglycaemia",
        "Basal insulin should only be given if the BGL is above 15 mmol/L",
        "Carbohydrate counting uses a fixed ratio of 10 units of rapid insulin per 10 g of carbohydrate",
        "Pre-mixed twice-daily insulin is the only recommended mode of delivery in type 1 diabetes"],
       "B",
       "Type 1 diabetes is ABSOLUTE insulin deficiency from T-cell mediated destruction of beta cells, so insulin is mandatory and DKA follows its omission.\n"
       "Delivery is split into basal insulin (roughly 50% of the total daily dose), which prevents fasting hyperglycaemia and ketosis, and bolus/prandial insulin (40 to 60% of TDD depending on carbohydrate intake), which covers meals.\n"
       "* Basal insulin must NEVER be withheld because the BGL looks acceptable — its job is to suppress ketogenesis, not to correct a number. Withholding it is how inpatients develop DKA.\n"
       "* The insulin-to-carbohydrate ratio is individualised (a typical example is 1 unit per 15 g of carbohydrate), not fixed.",
       ["Type 1 diabetes is absolute insulin deficiency — insulin is mandatory to prevent DKA.",
        "TDD split: ~50% basal, 40-60% bolus/prandial.",
        "Basal insulin must never be missed, regardless of the BGL — it suppresses ketogenesis."]),

    _q("During a teaching session, the pharmacist asks you to describe the profile of the ultra-rapid-acting insulin Fiasp (modified aspart).\n\nWhich one of the following is correct?",
       ["Onset 30 minutes, peak 2 to 3 hours, duration 6 to 8 hours",
        "Onset 5 to 15 minutes, peak 30 to 90 minutes, duration 3 hours; given at the start of a meal or up to 20 minutes after starting",
        "Onset 10 to 15 minutes, peak 60 to 90 minutes, duration 3 to 5 hours; given immediately pre-meal",
        "No peak, onset 1 to 2 hours, duration 24 hours",
        "Must be taken exactly 30 minutes before a meal"],
       "B",
       "Fiasp (ultra-rapid aspart): onset 5 to 15 minutes, peak 30 to 90 minutes, duration 3 hours. The clinically distinctive feature is the timing — it can be given at the start of the meal or even up to 20 minutes after starting, which is a genuine advantage in patients with unpredictable intake.\n"
       "* Option A describes short-acting neutral insulin (Actrapid, Humulin R): onset 30 min, peak 2-3 h, duration 6-8 h, given within 30 min pre-meal.\n"
       "* Option C describes rapid-acting insulin (Novorapid, Humalog, Apidra): onset 10-15 min, peak 60-90 min, duration 3-5 h, given immediately pre-meal.\n"
       "* Option D describes long-acting glargine.",
       ["Fiasp (ultra-rapid): onset 5-15 min, peak 30-90 min, duration 3 h. Start of meal, or up to 20 min after.",
        "Rapid-acting (Novorapid, Humalog, Apidra): onset 10-15 min, peak 60-90 min, duration 3-5 h, immediately pre-meal.",
        "Short-acting (Actrapid): onset 30 min, peak 2-3 h, duration 6-8 h, within 30 min pre-meal."]),

    _q("A resident asks about the difference between intermediate-acting isophane insulin (Protaphane) and long-acting glargine 300 units/mL (Toujeo).\n\nWhich one of the following is correct?",
       ["Protaphane has an onset of 30 minutes, peaks at 1 hour and lasts 3 hours",
        "Toujeo (glargine 300 u/mL) has an onset of 1 to 6 hours, no peak, lasts 24 to 36 hours and is given daily",
        "Optisulin (glargine 100 u/mL) peaks at 6 to 8 hours and lasts 36 to 48 hours",
        "Levemir (detemir) is a rapid-acting insulin given immediately pre-meal",
        "Protaphane has no peak and lasts exactly 24 to 36 hours"],
       "B",
       "Toujeo (glargine 300 u/mL): onset 1 to 6 hours, NO peak, duration 24 to 36 hours, dosed daily.\n"
       "The key contrast is that isophane (Protaphane) DOES have a peak — onset 1 to 3 hours, peak 4 to 12 hours, duration 16 to 24 hours — which is why it can cause hypoglycaemia at an awkward time of day, and why it has largely been superseded as a basal insulin. It remains useful in gestational diabetes and prednisone-induced hyperglycaemia, where a peaking profile is actually what you want.\n"
       "* Optisulin (glargine 100 u/mL) has no peak and lasts 24 hours.\n"
       "* Detemir (Levemir) is long-acting, commonly twice daily, with a peak at 6 to 8 hours.",
       ["Toujeo (glargine 300 u/mL): onset 1-6 h, no peak, duration 24-36 h, daily.",
        "Optisulin (glargine 100 u/mL): onset 1-2 h, no peak, duration 24 h, daily.",
        "Protaphane (isophane): onset 1-3 h, PEAK 4-12 h, duration 16-24 h — useful in gestational diabetes and steroid-induced hyperglycaemia."]),

    _q("A 70-year-old man says he takes 'Humalog Mix' at home but cannot remember which one. The pharmacist warns you about the risk of error with similar-sounding insulins.\n\nWhich one of the following correctly describes Ryzodeg?",
       ["It contains short-acting neutral insulin and isophane, and must be taken within 30 minutes pre-meal",
        "It contains quick-acting aspart and long-acting degludec; onset 10 to 15 minutes, peak 75 minutes, duration over 24 hours, given with the largest meal once or twice daily",
        "Humalog Mix 25 contains quick-acting aspart and long-acting detemir",
        "All pre-mixed insulins contain only long-acting insulin and can be given at bedtime",
        "Novomix 30/70 has an onset of 30 to 60 minutes and is given within 30 minutes pre-meal"],
       "B",
       "Ryzodeg is aspart (quick-acting) plus degludec (ultra-long-acting): onset 10 to 15 minutes, peak 75 minutes, duration over 24 hours, given with the largest meal once or twice daily.\n"
       "The critical safety principle in this stem is the one the pharmacist raised: Humalog, Humulin R, Humulin NPH, Humalog Mix 25, Humalog Mix 50 and Humulin 25/75 all sound alike and have completely different actions. ALWAYS confirm with the patient which insulin they actually take.\n"
       "* Every pre-mixed insulin contains a rapid or short-acting component, so they must be dosed WITH MEALS and never at bedtime.",
       ["Ryzodeg: aspart + degludec; onset 10-15 min, peak 75 min, duration over 24 h; with the largest meal.",
        "Pre-mixed insulins contain a quick-acting component and must be dosed with meals, NEVER at bedtime.",
        "Similar-sounding insulins are a major error source — always confirm the exact product with the patient."]),

    _q("A ward nurse asks you to clarify practical points of insulin administration for a newly diagnosed patient.\n\nWhich one of the following is correct?",
       ["Use a long needle (8 to 12 mm) to ensure the insulin reaches intramuscular tissue",
        "Inject into the exact same spot on the abdomen each time to improve absorption",
        "Cloudy insulins such as Protaphane and some mixes must be gently rolled before use, whereas modern clear insulins do not",
        "Basal insulin should be withheld if the patient is fasting",
        "Clear insulins such as Novorapid must be vigorously shaken before injection"],
       "C",
       "Cloudy insulins (Protaphane, some pre-mixed insulins) are suspensions and must be gently ROLLED before use to redistribute them. Modern clear insulins do not need rolling — and never shaking, which can damage the insulin protein.\n"
       "The other practice points: insulin is subcutaneous only (abdomen usually, or thigh, upper arm, buttock); avoid long needles (4 to 5 mm is right — long needles risk intramuscular injection and erratic absorption); rotate injection sites to prevent lipohypertrophy and glycaemic variability.\n"
       "* Basal insulin must NOT be withheld when fasting. That is precisely when it is needed to suppress ketogenesis — withholding it is a route to DKA.",
       ["Cloudy insulins must be gently rolled; clear insulins need no rolling and must never be shaken.",
        "Use 4-5 mm needles, subcutaneous only, and rotate sites to prevent lipohypertrophy.",
        "Never withhold basal insulin because a patient is fasting."]),

    _q("An intern is reviewing BGL monitoring frequencies across the ward.\n\nWhich one of the following is correct?",
       ["Most non-critically ill inpatients with diabetes need one BGL check daily, at bedtime",
        "Overnight (0200h) BGL checks are never indicated because they disrupt sleep",
        "Women with gestational diabetes target fasting readings of 5.0 mmol/L or below and 2-hour post-prandial readings of 6.7 mmol/L or below",
        "Patients on an intravenous insulin infusion need BGL monitoring every 4 hours",
        "Patients with stable glycaemic control must have hourly BGL checks throughout admission"],
       "C",
       "Gestational diabetes targets are tighter than for non-pregnant patients: fasting 5.0 mmol/L or below, and 2-hour post-prandial 6.7 mmol/L or below.\n"
       "The rest of the monitoring picture: most non-critically ill inpatients have BGL checks 4 times daily (pre-meals and bedtime); an 0200h check is appropriate when looking for nocturnal hypoglycaemia; patients on an insulin infusion need HOURLY checks unless a senior doctor specifies otherwise; and patients with stable control may not need in-hospital checks at all, since they are disruptive.",
       ["Gestational diabetes: fasting 5.0 mmol/L or below; 2-hour post-prandial 6.7 mmol/L or below.",
        "Standard inpatient monitoring: 4 times daily (pre-meals and bedtime).",
        "IV insulin infusion: hourly BGL monitoring."]),

    _q("A 20-year-old man with type 1 diabetes and a fractured femur uses a continuous glucose monitor.\n\nWhich one of the following is correct about CGM?",
       ["Flash CGM (Freestyle Libre 2) is worn on the arm for 14 days and is fully compatible with existing insulin pumps",
        "Real-time CGM (Dexcom G6) is worn on the abdomen for 10 days, connects automatically by Bluetooth, and is compatible with certain insulin pumps",
        "All adults with type 1 diabetes in Australia receive CGM entirely free of charge",
        "Real-time CGM requires manual scanning every 2 hours to prevent data loss",
        "CGM measures venous blood glucose directly"],
       "B",
       "Real-time CGM (Dexcom G6): worn on the abdomen for 10 days, automatic Bluetooth connectivity to a smartphone, hypo alarms and customisable alerts, and compatible with certain insulin pumps.\n"
       "* Flash/intermittently-scanned CGM (Freestyle Libre 2): worn on the arm for 14 days, stores 8 hours of data, requires SCANNING to retrieve it, and is INCOMPATIBLE with existing insulin pumps.\n"
       "* CGM measures INTERSTITIAL glucose, not blood glucose — which is why there is a lag behind rapidly changing blood glucose.\n"
       "* Subsidy in Australia (type 1 only): free if under 21, pregnant or pre-conception, or holding a concession card; all other adults with type 1 pay a copayment of about $32/month.",
       ["Real-time CGM (Dexcom G6): abdomen, 10 days, auto Bluetooth, pump-compatible.",
        "Flash CGM (Freestyle Libre 2): arm, 14 days, requires scanning, NOT pump-compatible.",
        "CGM measures interstitial glucose, not blood glucose. Free for T1DM if under 21, pregnant, or concessional."]),

    _q("The registrar is setting glycaemic targets for new admissions.\n\nWhat is the recommended target glucose range for most non-pregnant hospitalised patients, and why is hypoglycaemia so strongly avoided?",
       ["4.0 to 7.0 mmol/L; hypoglycaemia causes permanent insulin resistance",
        "5.0 to 10.0 mmol/L; hypoglycaemia is associated with rebound hyperglycaemia, falls, delirium, cardiac events and increased nursing workload",
        "8.0 to 12.0 mmol/L; hypoglycaemia is harmless in hospitalised patients",
        "3.0 to 8.0 mmol/L; hypoglycaemia only needs treatment if the patient is symptomatic",
        "Exactly 6.0 mmol/L for all patients including the frail elderly"],
       "B",
       "The typical inpatient target for non-pregnant patients is 5.0 to 10.0 mmol/L — deliberately not tight, because the harms of hypoglycaemia in hospital outweigh the marginal benefit of near-normal glucose over a short admission.\n"
       "Hypoglycaemia (BGL below 4 mmol/L) causes rebound hyperglycaemia after treatment, falls, delirium, cardiac events (ACS, arrhythmias, pulmonary oedema), and consumes substantial nursing time.\n"
       "Targets must still be individualised — tighter in pregnancy, looser in the frail elderly or those prone to hypoglycaemia.\n"
       "Hyperglycaemia is not benign either: above 11 mmol/L it is associated with poor wound healing, delayed surgical recovery, more infections and longer stays.",
       ["Inpatient target for non-pregnant patients: 5.0-10.0 mmol/L.",
        "Hypoglycaemia is below 4 mmol/L: rebound hyperglycaemia, falls, delirium, cardiac events.",
        "Hyperglycaemia above 11 mmol/L: poor wound healing, infection, delayed recovery, longer stay."]),

    _q("A 54-year-old man with type 1 diabetes is admitted with a severe soft tissue infection. His BGL has been persistently above 17.0 mmol/L.\n\nWhich one of the following is correct?",
       ["Hyperglycaemia only matters above 25 mmol/L, and ketones need checking only if the patient is comatose",
        "Hyperglycaemia above 11 mmol/L is associated with poor wound healing, delayed recovery, longer stay and infection; ketones should be checked in an unwell patient with a BGL above 16 mmol/L",
        "Ketones should be measured on urine strips, as urine testing is more accurate and quicker than fingerprick",
        "Ketosis only occurs in type 1 diabetes; type 2 patients never develop DKA",
        "Patients on SGLT2 inhibitors have no risk of ketosis during acute illness"],
       "B",
       "Ketones should be measured in any unwell patient with diabetes and a BGL above 16 mmol/L. Hyperglycaemia above 11 mmol/L is associated with poor wound healing, delayed recovery and reoperation, more hospital-acquired infections, longer stays, and dehydration with electrolyte disturbance.\n"
       "* FINGERPRICK ketones are more accurate and respond faster than urinary ketones, and are the preferred modality.\n"
       "* DKA is more likely in type 1, but significant ketosis and DKA DO occur in type 2 patients.\n"
       "* SGLT2 inhibitors frequently produce ketosis and carry a specific risk of EUGLYCAEMIC ketoacidosis during fasting or acute illness — the BGL will not warn you.",
       ["Check ketones in an unwell patient with diabetes and a BGL above 16 mmol/L.",
        "Fingerprick ketones are preferred over urinary ketones — more accurate and faster.",
        "DKA can occur in type 2 diabetes, and SGLT2 inhibitors can cause euglycaemic DKA."]),

    _q("An unwell 35-year-old woman with type 1 diabetes has a fingerprick ketone reading of 1.8 mmol/L.\n\nWhat is the interpretation and the next step?",
       ["Normal; no action required",
        "Potential DKA; interpret in clinical context and send a venous blood gas to check for acidosis",
        "Definitive DKA; start the DKA protocol immediately without a blood gas",
        "More ketones than normal; ensure adequate hydration and repeat in 2 hours with no further investigation",
        "An emergency requiring immediate ICU admission before any blood tests"],
       "B",
       "A ketone level of 1.6 to 3.0 mmol/L indicates POTENTIAL DKA: interpret it in the clinical context and send a venous blood gas.\n"
       "The ketone ladder: below 0.6 is normal (no action); 0.6 to 1.5 means more ketones than normal (hydrate, recheck in 2 hours); 1.6 to 3.0 means potential DKA (send a VBG); above 3.0 means probably in DKA (send a VBG and get senior help).\n"
       "DKA is not diagnosed on ketones alone. The Queensland pathway requires the VBG to confirm acidosis: pH below 7.35 AND bicarbonate below 15 AND an elevated anion gap AND ketones above 1. Note that the BGL may be normal or elevated — so a reassuring glucose does not exclude it.",
       ["Ketone ladder: below 0.6 normal; 0.6-1.5 hydrate and recheck in 2 h; 1.6-3.0 potential DKA (send VBG); above 3.0 probable DKA (VBG + senior help).",
        "DKA diagnosis requires a VBG: pH below 7.35, HCO3 below 15, elevated anion gap, and ketones above 1.",
        "The BGL may be normal in DKA — ketones and the gas make the diagnosis, not the glucose."]),

    _q("An insulin-naive 80 kg man with type 2 diabetes is admitted with a soft tissue infection, and the team starts a subcutaneous basal-bolus regimen using the weight-based method.\n\nWhat are the calculated starting doses?",
       ["Basal 40 units; bolus 10 units with meals",
        "Basal 20 units; bolus 6 to 7 units with meals",
        "Basal 80 units; bolus 80 units with meals",
        "Basal 10 units; bolus 20 units with meals",
        "Basal 32 units; bolus 12 units with meals"],
       "B",
       "The weight-based method for an insulin-naive patient is:\n"
       "* Basal (e.g. Optisulin) = weight / 4. For 80 kg: 80 / 4 = 20 units daily.\n"
       "* Bolus (e.g. Novorapid) = weight / 12, with each meal. For 80 kg: 80 / 12 = 6.7, so 6 to 7 units with meals.\n"
       "Round to whole units, and when in doubt round DOWN — the cost of a hypo in hospital is greater than the cost of a few hours of mild hyperglycaemia.\n"
       "* Option D inverts basal and bolus, which is the error that actually hurts people.",
       ["Insulin-naive weight-based starting doses: basal = weight / 4; bolus = weight / 12 with each meal.",
        "Round to whole units, and round down when uncertain.",
        "Do not invert the basal and bolus calculations."]),

    _q("A 68-year-old woman with type 2 diabetes is admitted with pneumonia. At home she takes Novomix 30 (pre-mixed insulin) 36 units twice daily. The registrar converts her to basal-bolus during the acute admission to reduce hypoglycaemia risk.\n\nWhat is the converted regimen?",
       ["Optisulin 18 units daily and Novorapid 6 units with meals",
        "Optisulin 36 units daily and Novorapid 12 units with meals",
        "Novorapid 36 units daily and Optisulin 12 units with meals",
        "Optisulin 72 units daily and Novorapid 24 units with meals",
        "Optisulin 36 units daily and Novorapid 36 units with meals"],
       "B",
       "The conversion is: take the total daily dose, split it 50:50 into basal and bolus, then divide the bolus by three across meals.\n"
       "Her TDD is 36 units BD = 72 units/day. Split 50:50 gives 36 units basal and 36 units bolus. The bolus divided by 3 meals gives 12 units per meal.\n"
       "So: Optisulin 36 units daily, Novorapid 12 units with breakfast, lunch and dinner.\n"
       "* Option A halves the TDD before splitting — a 50% underdose.\n"
       "* Option E fails to divide the bolus across meals, tripling it.\n"
       "The reason for converting at all is that pre-mixed insulin carries a higher risk of hypoglycaemia in hospital, where meals are unpredictable and patients are often nil by mouth.",
       ["Pre-mixed to basal-bolus: calculate TDD, split 50:50, divide the bolus by 3 across meals.",
        "Novomix 36 units BD = 72 TDD -> Optisulin 36 daily + Novorapid 12 with each meal.",
        "Pre-mixed insulin is converted in hospital because unpredictable intake makes it a hypoglycaemia risk."]),

    _q("A 25-year-old woman with type 1 diabetes has a total daily insulin dose of 25 units and mild hyperglycaemia. You want to calculate her correction factor to prescribe supplemental insulin.\n\nUsing the rule of thumb, how much will 1 unit of rapid-acting insulin lower her BGL?",
       ["1 mmol/L", "2 mmol/L", "4 mmol/L", "10 mmol/L", "25 mmol/L"],
       "C",
       "The correction factor rule of thumb is 100 divided by the total daily dose. Here, 100 / 25 = 4, so 1 unit should lower her BGL by about 4 mmol/L above target.\n"
       "This is the insulin sensitivity factor, and it is the basis for prescribing supplemental (correctional) insulin on top of her usual bolus orders.\n"
       "Two practical points: prescribe the SAME quick-acting insulin she normally uses (if she is on Humalog, correct with Humalog), and be cautious in insulin-sensitive type 1 patients, especially with a TDD below 30 units — if in doubt, round down to a lower scale.",
       ["Correction factor rule of thumb: 100 / total daily dose = mmol/L drop per unit.",
        "Prescribe supplemental insulin using the patient's usual quick-acting insulin brand.",
        "Be cautious in insulin-sensitive type 1 patients (TDD below 30 units) — round down if unsure."]),

    _q("The registrar asks you to prepare a standing-order intravenous insulin infusion and appropriate intravenous fluids for a non-critically ill patient who is nil by mouth.\n\nWhich one of the following is correct?",
       ["100 units Actrapid in 100 mL sodium chloride 0.9%; give no fluids, to avoid overload",
        "50 units Actrapid added to 49.5 mL sodium chloride 0.9% (total volume 50 mL); co-administer glucose 3.3% + sodium chloride 0.3% 1 L at 125 mL/hr, or glucose 5% at 100 to 125 mL/hr with separate saline",
        "50 units Novorapid in 1 L of water; co-administer glucose 10% at 150 mL/hr",
        "10 units Actrapid in 500 mL of dextrose; co-administer saline at 50 mL/hr",
        "50 units Actrapid in 50 mL sodium chloride 0.9%; give fluids only if the BGL falls below 2.0 mmol/L"],
       "B",
       "The Queensland Health standing order is 50 units of Actrapid added to 49.5 mL of sodium chloride 0.9%, to a total volume of 50 mL — a concentration of 1 unit/mL.\n"
       "The IV insulin chart does NOT include fluid orders, so they must be prescribed separately. Glucose-containing fluid must be co-administered to every patient on a routine insulin infusion, because if the insulin line keeps running and the glucose line blocks, the patient becomes profoundly hypoglycaemic.\n"
       "With normal renal and cardiac function: glucose 3.3% + sodium chloride 0.3% 1 L at 125 mL/hr, or glucose 5% at 100 to 125 mL/hr with maintenance saline through a separate line. Where fluid must be restricted (heart failure, renal failure), use glucose 10% at 42 to 50 mL/hr.",
       ["Standing order: 50 units Actrapid in 49.5 mL sodium chloride 0.9% = 50 mL total, 1 unit/mL.",
        "Glucose-containing fluid MUST be co-administered with a routine insulin infusion, and ordered separately.",
        "Fluid-restricted patients: glucose 10% at 42-50 mL/hr."]),

    _q("A patient who normally takes Optisulin 45 units daily at home is started on an intravenous insulin infusion. His BGL at 14:00 is 12.5 mmol/L.\n\nWhat is the correct infusion rate, and what should happen to his home basal insulin?",
       ["2 units/hour; stop the home basal insulin immediately",
        "3 units/hour; continue the home basal insulin at its usual dose and time as a top-up",
        "1 unit/hour; withhold the home basal insulin",
        "5 units/hour; double the home basal insulin",
        "0 units/hour; suspend the infusion, as the BGL is in target range"],
       "B",
       "His usual basal dose is 45 units/day, which is above 40 — so the higher-regimen column applies. For a BGL of 12.5 mmol/L (the 10.1 to 15 band), that gives 3 units/hour. (Regimen 1, for patients on 40 units or less, would give 2 units/hour.)\n"
       "The home basal insulin should be CONTINUED at its usual dose and time. The infusion then acts as a titratable top-up on a stable background, which makes it far easier to wean the infusion later without leaving the patient uncovered — a common cause of rebound hyperglycaemia and DKA when infusions are stopped.\n"
       "Make it explicit to nursing staff that the patient is receiving BOTH IV and subcutaneous insulin, so neither is missed or assumed to be an error.",
       ["Check whether the usual basal dose exceeds 40 units/day — it selects the infusion regimen column.",
        "BGL 10.1-15: 2 units/hr on regimen 1; 3 units/hr if usual basal is above 40 units/day.",
        "Continue the usual basal insulin during the infusion — it makes weaning the infusion safe."]),

    _q("A patient on an intravenous insulin infusion has a BGL of 3.8 mmol/L.\n\nWhat is the correct action?",
       ["Continue the infusion at 0.5 units/hour and recheck in 1 hour",
        "Suspend the insulin infusion, continue the dextrose infusion, treat the hypoglycaemia, and recheck the glucose in 15 minutes",
        "Stop both the insulin and the dextrose infusions and recheck in 4 hours",
        "Increase the dextrose rate but continue the insulin unchanged",
        "Give a stat dose of subcutaneous rapid-acting insulin to stabilise the level"],
       "B",
       "For a BGL of 0 to 5 mmol/L on an insulin infusion: SUSPEND the insulin infusion and CONTINUE the dextrose. If the glucose is below 4 mmol/L, treat the hypoglycaemia. Recheck the glucose in 15 minutes.\n"
       "The two halves of that instruction matter equally. Suspending the insulin stops the fall; continuing the dextrose is what actually brings the glucose back up. Stopping the dextrose as well — option C — removes the very thing correcting the hypoglycaemia and is a genuine harm.\n"
       "The 15-minute recheck is much shorter than the usual hourly monitoring, because the situation is unstable and you need to know quickly whether it is resolving.",
       ["BGL 0-5 mmol/L on an insulin infusion: suspend the insulin, CONTINUE the dextrose, treat if below 4, recheck in 15 minutes.",
        "Never stop the dextrose infusion when treating hypoglycaemia — it is what is correcting it.",
        "Routine monitoring on an IV insulin infusion is hourly; after a hypo, recheck at 15 minutes."]),
]


# ===========================================================================
# UNIT 4 — ANTICOAGULATION AND ANTIPLATELETS (VIVA)
# ===========================================================================

def _v(question, answer):
    return {"question": question, "answer": answer}


_ANTICOAG_VIVA = [
    _v("What are the primary clinical indications for anticoagulants and antiplatelet agents?",
       "Primary prevention and treatment of thromboembolic events: atrial fibrillation; venous thromboembolism including PE and DVT; mechanical heart valves; left mural dilatation and mural thrombus; acute coronary syndromes; stroke prevention; peripheral arterial disease; and stroke secondary to AF."),
    _v("What are the general absolute contraindications to anticoagulation?",
       "Active bleeding, recent haemorrhagic stroke, severe liver disease, and pregnancy (specifically for warfarin)."),
    _v("Why is anticoagulation classified as high-risk therapy?",
       "It is a delicate balance between the risk of thrombosis and the risk of bleeding, and the margin for error is small. Careless or inappropriate use causes avoidable morbidity and mortality. Anticoagulation is the single most frequent cause of preventable drug harm — either actual bleeds or inadvertent thromboemboli."),
    _v("Name the major preventable incidents associated with anticoagulant prescribing.",
       "Anticoagulant omission on discharge resulting in PE; out-of-hours dosing errors, often by prescribers who do not know the patient; significant drug-drug interactions leading to bleeds; admissions with bleeding from inadvertent over-anticoagulation; concomitant therapeutic and prophylactic prescriptions on the same chart; and under-anticoagulation leading to emboli."),
    _v("List the antiplatelet agents.",
       "Aspirin (acetylsalicylic acid); clopidogrel (Plavix); prasugrel (Effient); ticagrelor (Brilinta); and dipyridamole (Persantin, Asasantin)."),
    _v("Classify the oral anticoagulants.",
       "DOACs — factor Xa inhibitors: apixaban (Eliquis) and rivaroxaban (Xarelto); direct thrombin inhibitor: dabigatran (Pradaxa). Vitamin K antagonists: warfarin (Coumadin, Marevan)."),
    _v("Classify the parenteral anticoagulants.",
       "Unfractionated heparin — subcut for prophylaxis, IV infusion for treatment. Xa inhibitors — enoxaparin (Clexane), dalteparin (Fragmin) and fondaparinux, all subcut. Direct thrombin inhibitors — bivalirudin and argatroban, both IV. Danaparoid — subcut for prophylaxis, IV for treatment."),
    _v("What is Virchow's triad, and how does it relate to thrombus formation?",
       "Venous thrombus formation and propagation arise from abnormalities in three areas: a hypercoagulable state, endothelial injury, and circulatory stasis. Most hospital VTE risk factors map onto one or more of these."),
    _v("What proportion of hospitalised patients have VTE risk factors?",
       "About 50 to 75% of people admitted to hospital have at least one risk factor for VTE, and 40% have three or more. Hospitalised patients are more likely to develop VTE during or shortly after their stay than people in the community."),
    _v("Outline the seven Quality Statements of the VTE Prevention Clinical Care Standard.",
       "1. Assess and document VTE risk within 24 hours of admission. 2. Develop a VTE prevention plan balancing thrombosis risk against bleeding risk. 3. Inform and partner with patients, tailoring information to their risks and needs. 4. Document and communicate the plan to all clinicians involved. 5. Use appropriate prevention — medicines and/or mechanical methods per locally endorsed guidelines. 6. Reassess risk and monitor for complications at intervals no longer than every 7 days, when the clinical condition changes, and on discharge. 7. Provide a discharge plan containing prophylaxis and follow-up, communicated to the GP within 48 hours of discharge."),
    _v("What must be reviewed when undertaking a VTE risk assessment?",
       "VTE risk; contraindications to prophylaxis; baseline tests (full blood count, renal function, and a coagulation profile if a coagulation disorder is suspected); and special considerations for pharmacological prophylaxis such as weight, renal function and patient preference."),
    _v("What are the absolute contraindications to pharmacological VTE prophylaxis?",
       "Already therapeutically anticoagulated; active major bleeding (2 or more units of blood products transfused in 24 hours); clinically significant bleeding within the last 48 hours; platelets below 50 x 10^9/L; inherited or acquired bleeding disorders such as haemophilia; high bleeding risk surgery (head and neck, neurosurgery, eye) within the last 2 weeks; recent gastrointestinal, genitourinary or CNS bleeding; an intracranial or spinal lesion judged high risk of bleeding; uncontrolled hypertension of 230/120 mmHg or higher; active peptic ulcer or ulcerative GI disease; and severe hepatic disease or acute liver failure."),
    _v("What are the standard VTE prophylaxis doses for medical patients?",
       "Dalteparin 5000 units subcut daily; enoxaparin 40 mg subcut daily; or unfractionated heparin 5000 units subcut every 8 to 12 hours."),
    _v("What are the standard VTE prophylaxis doses for surgical patients?",
       "Dalteparin 5000 units subcut the evening before the operation then 5000 units daily; or 2500 units subcut 1 to 2 hours preoperatively, repeated 12 hours later, then 5000 units daily. Enoxaparin 40 mg subcut 12 hours preoperatively, then 40 mg daily. UFH 5000 units subcut 2 hours preoperatively, then 5000 units every 8 to 12 hours."),
    _v("What prophylaxis is used after total hip or total knee replacement?",
       "Rivaroxaban 10 mg daily, starting 6 to 10 hours after surgery once haemostasis is established — maximum 5 weeks for THR, 2 weeks for TKR. Apixaban 2.5 mg twice daily, starting 12 to 24 hours after surgery — maximum 32 to 38 days for THR, 10 to 14 days for TKR. Aspirin 100 mg daily may be reasonable in selected patients without additional VTE risk factors, usually combined with mechanical methods."),
    _v("What are the advantages of LMWH over UFH for prophylaxis?",
       "Fewer bleeds, fewer VTE events, and less heparin-induced thrombocytopenia — the HIT risk with UFH is roughly eight times that with LMWH."),
    _v("Outline the renal dose adjustments for UFH and LMWH prophylaxis.",
       "CrCl 30 to 50 mL/min: no adjustment for either. CrCl 15 to 29 mL/min: no adjustment for UFH; enoxaparin must be reduced to 20 mg subcut daily; dalteparin needs no adjustment. CrCl below 15 mL/min: no adjustment for UFH; LMWH must not be used."),
    _v("What are the DOAC prophylaxis doses in renal impairment?",
       "Rivaroxaban: CrCl 30 to 50 mL/min — 10 mg daily; CrCl 25 to 29 and 15 to 24 mL/min — 10 mg daily with caution; below 15 mL/min or dialysis — contraindicated. Apixaban: CrCl 30 to 50 mL/min — 2.5 mg twice daily; CrCl 25 to 29 mL/min — 2.5 mg twice daily with caution; CrCl 15 to 24 mL/min and below — contraindicated."),
    _v("How does obesity change VTE prophylaxis dosing?",
       "Obese patients (BMI 30 or above) have increased VTE risk and do not follow a predictable dose-response; standard doses are unlikely to be sufficient at a BMI of 40 or above. BMI 30 to 40: standard LMWH at low or moderate risk, consider adjusted LMWH at high risk. BMI 41 to 60: adjusted LMWH at any risk level — dalteparin 5000 units subcut twice daily or 50 units/kg daily, or enoxaparin 40 mg subcut twice daily or 0.5 mg/kg daily. BMI above 60: seek specialist advice."),
    _v("What prophylaxis is recommended for patients under 50 kg?",
       "Evidence for LMWH at the extremes of weight is limited and careful observation is required. Consider dalteparin 2500 units subcut daily or enoxaparin 20 mg subcut daily."),
    _v("How effective is anticoagulation in treating VTE?",
       "It is highly effective, preventing thrombus extension or recurrence by at least 80%. The central aim is to prevent pulmonary embolism."),
    _v("Give the dosing, administration and monitoring for rivaroxaban in VTE treatment.",
       "15 mg twice daily for 3 weeks, then 20 mg once daily for the duration of treatment, with the option to reduce to 10 mg daily long-term if there is clinical equipoise. Oral, and must be taken with food to optimise absorption. Routine therapeutic drug monitoring is not required."),
    _v("Give the dosing, administration and monitoring for apixaban in VTE treatment.",
       "10 mg twice daily for 7 days, then 5 mg twice daily for the duration of treatment, with the option to reduce to 2.5 mg twice daily long-term if there is clinical equipoise. Oral. Routine therapeutic drug monitoring is not required."),
    _v("Give the dosing, administration and monitoring for enoxaparin in VTE treatment.",
       "1 mg/kg subcut twice daily, or 1.5 mg/kg subcut once daily. Dose adjustment may be needed in renal impairment or at the extremes of body weight, and anti-Xa levels may be indicated in those same situations."),
    _v("Give the dosing, administration and monitoring for unfractionated heparin in VTE treatment.",
       "Bolus 80 units/kg, then an infusion at 18 units/kg/hr, titrated against the target APTT using the VTE treatment nomogram. Given IV. Monitor APTT per the nomogram at least daily, and platelets daily to screen for HIT. If the patient has used heparin before, use the dose previously required."),
    _v("Give the dosing, administration and monitoring for warfarin in VTE treatment.",
       "5 mg daily for the first 4 days, guided by the warfarin nomogram and INR, then clinical judgement. Requires bridging with LMWH or UFH until the INR is above 2.0. Maintenance is titrated to a target INR of 2.0 to 3.0."),
    _v("What are the general rules for duration of anticoagulation in VTE?",
       "Individualised, but as a general rule all patients with proximal DVT or PE should receive at least 3 months of anticoagulation, and provoked distal DVT can be treated for 6 to 12 weeks."),
    _v("Summarise the THANZ recommendations on VTE treatment duration.",
       "Distal DVT with a major provoking factor no longer present: 6 weeks. Distal DVT unprovoked or with persisting risk factors: 3 months. Proximal DVT or PE provoked by major surgery or trauma no longer present: 3 months. DVT or PE provoked by active cancer: therapeutic LMWH, apixaban or rivaroxaban for at least 6 months. For patients continuing extended anticoagulation, a therapeutic or low-dose DOAC is preferred over warfarin. Aspirin monotherapy should be avoided unless anticoagulation cannot be used at all."),
    _v("What is the prevalence and clinical significance of atrial fibrillation?",
       "AF has an estimated prevalence of 2 to 4% in developed countries, is often asymptomatic, and becomes more common with age. Patients with AF have higher mortality than the general population, largely from thromboembolic complications such as stroke."),
    _v("Explain the CHA2DS2-VA score.",
       "C — congestive heart failure (1 point): recent signs, symptoms or admission for decompensated heart failure, including HFrEF and HFpEF, or moderate to severe LV systolic impairment. H — hypertension (1), regardless of whether the BP is currently elevated. A2 — age 75 or older (2). D — diabetes (1). S2 — prior stroke, TIA or systemic thromboembolism (2). V — vascular disease (1): prior MI, peripheral arterial disease, or complex aortic plaque on imaging. A — age 65 to 74 (1)."),
    _v("How does CHA2DS2-VA relate to CHA2DS2-VASc?",
       "CHA2DS2-VA is a sexless modification of CHA2DS2-VASc. The CHA2DS2-VASc score is identical but adds one further point if the patient is female. To estimate the annual stroke risk, the CHA2DS2-VASc score is the one to calculate."),
    _v("What are the treatment recommendations based on the CHA2DS2-VA score?",
       "Score of 2 or more: oral anticoagulation is recommended unless contraindicated. Score of 1: consider anticoagulation. Score of 0: anticoagulation is not recommended in non-valvular AF, unless DC cardioversion is planned. Antiplatelet agents are not recommended as an alternative to anticoagulation for stroke prevention in non-valvular AF, because they have been shown to be ineffective."),
    _v("What clinical factors should be weighed when assessing bleeding risk in AF?",
       "Proximity to treatment or resuscitation facilities; the reversibility of the anticoagulant and the patient's acceptability of reversal agents on cultural or social grounds; the ability to conduct therapeutic drug monitoring; and contraindications to specific agents."),
    _v("What are the recognised bleeding risk factors in AF?",
       "History of major bleeding; labile INR (time in therapeutic range below 60%); advanced age; heavy alcohol use; impaired renal function; and concomitant medicines including antiplatelet agents and NSAIDs."),
    _v("Give the DOAC doses for stroke prevention in AF.",
       "Rivaroxaban: CrCl 50 mL/min or above — 20 mg daily with food; CrCl 31 to 49 — 15 mg daily with food; CrCl 15 to 30 — specialist opinion; below 15 — contraindicated. Apixaban: CrCl 25 mL/min or above with no more than one of (age 80 or older, weight 60 kg or less, creatinine above 133 micromol/L) — 5 mg twice daily; with at least two of those factors — 2.5 mg twice daily; CrCl below 25 — contraindicated. Dabigatran: under 75 with CrCl above 50 and low bleeding risk — 150 mg twice daily; if 75 or older, CrCl 30 to 50, or high bleeding risk — 110 mg twice daily; CrCl below 30 — contraindicated."),
    _v("When is warfarin preferred over a DOAC for stroke prevention in AF?",
       "For valvular AF — mechanical heart valves, or moderate to severe mitral stenosis. It may also be preferred where there are contraindications to DOACs, or where the risk profile favours warfarin: the need for reversibility, monitoring capability, distance from urgent medical care, or suspected poor compliance."),
    _v("What are the key antiplatelet recommendations in acute coronary syndrome?",
       "Aspirin 300 mg orally initially, dissolved or chewed, then 100 to 150 mg daily, for all patients with ACS in the absence of hypersensitivity (strong recommendation, evidence IA). Dual antiplatelet therapy with a P2Y12 inhibitor in addition to aspirin: ticagrelor 180 mg then 90 mg twice daily, or clopidogrel 300 to 600 mg then 75 mg daily (strong, IA)."),
    _v("Outline the anticoagulation dosing for NSTEMI.",
       "Enoxaparin 1 mg/kg subcut twice daily, generally kept at that dose for the first 48 hours even with mildly impaired kidney function, with adjustment considered thereafter. If CrCl is 30 to 50 mL/min, continue monitoring kidney function and consider anti-Xa levels. If kidney function is below 30 mL/min enoxaparin is contraindicated — use UFH instead: 60 units/kg IV bolus (maximum 5000 units), then 12 units/kg/hr (maximum 1000 units/hr)."),
    _v("Outline the anticoagulation dosing for primary PCI in STEMI.",
       "Decisions should always be made with the interventional cardiologist. UFH 70 to 100 units/kg IV bolus when no GP IIb/IIIa inhibitor is planned, or 50 to 70 units/kg with one — continue as an infusion if PCI is delayed. Bivalirudin 0.75 mg/kg IV bolus then 1.75 mg/kg/hr for up to 4 hours after the procedure. Enoxaparin 0.5 mg/kg IV bolus, with an extra 1 mg/kg subcut twice daily if PCI is delayed."),
    _v("How is antithrombotic therapy managed post-PCI in a patient needing long-term anticoagulation?",
       "Weigh bleeding risk against stent thrombosis risk, and use risk-reduction strategies such as smoking cessation and a proton pump inhibitor. Triple therapy (DOAC + P2Y12 inhibitor + aspirin) should be as short as possible, with cardiologist input. Where DAPT is combined with oral anticoagulation, use low-dose aspirin 100 mg and clopidogrel 75 mg — ticagrelor should not be used."),
    _v("Give the post-PCI drug combination timelines for patients on long-term oral anticoagulation.",
       "ACS + PCI: DOAC + P2Y12 + aspirin for less than 1 week, then DOAC + P2Y12 up to 12 months, then DOAC + a single antiplatelet (preferably the P2Y12) long-term. Medically treated ACS: DOAC + a single antiplatelet (preferably the P2Y12) up to 12 months, then DOAC alone. Chronic coronary syndrome + PCI: DOAC + P2Y12 + aspirin for less than 1 week, then DOAC + P2Y12 up to 6 months, then DOAC alone."),
    _v("What is the dual pathway regimen for coronary or peripheral arterial disease?",
       "From the COMPASS trial: rivaroxaban 2.5 mg twice daily combined with aspirin 100 mg daily. This reduces major cardiovascular events — the composite of stroke, myocardial infarction and cardiovascular death — in stable coronary and/or peripheral arterial disease, compared with aspirin alone."),
    _v("What anticoagulation is required for mechanical heart valves?",
       "Warfarin. Mechanical valves, especially mitral, carry a significant thrombosis risk, and the target INR may be higher than for other indications. DOACs must not be used as an alternative. Decisions on choice and intensity should be made with the cardiologist or cardiac surgeon."),
    _v("What clinical review do all patients on anticoagulants require?",
       "A daily clinical review by a medical officer."),
    _v("What baseline tests are required before prescribing any anticoagulant?",
       "Full blood count — seek advice if platelets are below 100 x 10^9/L or the haemoglobin is low; the platelet count also gives the baseline for HIT screening. Coagulation profile — APTT, PT, INR, fibrinogen, and thrombin time if requested. INR if prescribing warfarin, and seek advice if the baseline INR is abnormal. Liver function tests — seek advice before prescribing if there is known cirrhosis or oesophageal varices. Kidney function — if CrCl is below 50 mL/min and LMWH is being given, consider dose reduction and an anti-Xa assay after the third or fourth dose."),
    _v("Outline routine platelet monitoring for HIT and HITT.",
       "Patients on heparin-based treatment (UFH or LMWH) should have platelets checked at baseline; at least three times per week from day 4 to day 14 for VTE prophylaxis and LMWH treatment; and daily for UFH treatment. HIT usually develops after five to ten days of therapy, with a higher risk on UFH."),
    _v("What are the monitoring recommendations for warfarin?",
       "INR daily for all inpatients initiated on warfarin, until it is therapeutic and stable. If admitted already on warfarin, monitor daily until stable, then every 2 to 3 days."),
    _v("What are the monitoring recommendations for LMWH?",
       "Platelet count three times per week from day 4 to day 14, or until LMWH is stopped, whichever is sooner. Anti-Xa levels where there are extremes of body weight, an eGFR below 50 mL/min, or pregnancy — start after the third or fourth dose, with the sample taken 4 hours post-dose and aligned with local phlebotomy times."),
    _v("What are the monitoring recommendations for IV unfractionated heparin?",
       "APTT every 4 to 6 hours until it is within range on two consecutive readings, then daily. Platelet count daily to screen for HIT — seek advice if the count falls below 100 x 10^9/L or drops by more than 30% from baseline."),
    _v("What monitoring do DOACs require?",
       "In patients with normal kidney function and no signs of bleeding, therapeutic drug monitoring is generally not required. Kidney function should be monitored in all patients at least every 6 to 12 months."),
    _v("What are the target anti-Xa levels for IV unfractionated heparin?",
       "Low intensity (oral anticoagulant replacement, or ACS): 0.3 to 0.5 units/mL. Regular intensity (acute treatment of PE or DVT): 0.3 to 0.7 units/mL."),
    _v("What are the target anti-Xa levels for LMWH?",
       "Enoxaparin 1 mg/kg twice daily: peak 0.5 to 1 unit/mL (target 0.75). Enoxaparin 1.5 mg/kg once daily with normal kidney function: peak 1 to 2 units/mL (target 1.5). Dalteparin 100 units/kg twice daily: peak 0.5 to 1 unit/mL (target 0.75). Dalteparin 200 units/kg once daily: peak 1 to 2 units/mL (target 1.5). Take the sample after the third or fourth dose, 4 hours after the subcut dose."),
    _v("When is DOAC laboratory testing helpful?",
       "Perioperatively; in acute coronary syndrome; with bleeding or recurrent thrombosis; with deteriorating liver or kidney function, or severe renal impairment; when considering switching to a parenteral anticoagulant; at the extremes of body weight; with potentially interacting medicines; and in overdose or where compliance is in doubt."),
    _v("What is bridging therapy?",
       "The use of a short-acting anticoagulant such as UFH or LMWH during the period in which warfarin is interrupted for surgery, and post-operatively while waiting for the INR to return to therapeutic levels."),
    _v("When is anticoagulation resumed after a minor procedure with low bleeding risk?",
       "Usually within 24 hours. If the bleeding risk is high, treatment doses should be delayed until haemostasis is secured — and if there is a delay in resuming treatment doses, appropriate thromboprophylaxis should be given in the interim."),
    _v("Categorise elective procedures by bleeding risk.",
       "High bleeding risk (30-day risk of major bleed above 2%): neurosurgery, bowel resection. Low to moderate risk (0 to 2%): arthroscopy, coronary angiography, abdominal hernia repair. Minimal risk (approximately 0%): ophthalmological procedures such as cataract surgery."),
    _v("Which patients on warfarin require bridging?",
       "High risk, bridging recommended: any mitral valve prosthesis, any caged-ball or tilting-disc aortic prosthesis, or stroke/TIA within 6 months; AF with CHA2DS2-VA of 6 or more, stroke/TIA within 3 months, or rheumatic valvular disease; VTE within the last 3 months, or severe thrombophilia. Moderate risk, case-by-case: bileaflet aortic prosthesis with one or more of AF, prior stroke/TIA, hypertension, diabetes, heart failure or age over 75; AF with CHA2DS2-VA of 4 or 5, or below 4 with a stroke/TIA more than 3 months ago; VTE 3 to 12 months ago, non-severe thrombophilia, recurrent VTE, or active cancer. Low risk, no bridging: bileaflet aortic prosthesis without AF or other stroke risk factors; AF with CHA2DS2-VA of 3 or less and no prior stroke/TIA; a single non-life-threatening VTE more than 12 months ago with no other risk factors."),
    _v("Outline the perioperative bridging schedule for a high-risk patient on warfarin.",
       "Six days before: take the last dose of warfarin. Five days before: no warfarin. Four days before: no warfarin, check INR, and start treatment-dose LMWH or UFH once the INR is below 2 or subtherapeutic. Three and two days before: no warfarin, check INR, continue LMWH or UFH. One day before: no warfarin, check the INR is below 1.5, and cease LMWH 24 hours or UFH 4 to 6 hours before the procedure. Morning of the procedure: no warfarin, confirm the INR is below 1.5."),
    _v("Outline pre-operative interruption for rivaroxaban.",
       "CrCl 50 mL/min or above: withhold 48 hours for high bleeding risk surgery, 24 hours for low risk. CrCl 30 to 49: 48 hours high, 24 hours low. CrCl 15 to 29: at least 72 hours high, 36 to 48 hours low. Below 15: seek specialist advice."),
    _v("Outline pre-operative interruption for apixaban.",
       "CrCl 50 mL/min or above: withhold 48 hours for high bleeding risk surgery, 24 hours for low risk. CrCl 25 to 49: 60 to 72 hours high, 36 to 48 hours low. Below 25: seek specialist advice."),
    _v("Outline pre-operative interruption for dabigatran.",
       "CrCl above 80 mL/min: 48 hours high bleeding risk, 24 hours low. CrCl 50 to 80: 72 hours high, 36 hours low. CrCl 30 to 49: 96 hours high, 48 hours low. Below 30: 120 hours (5 days) high, 96 hours (4 days) low. Dabigatran needs the longest interruption of the DOACs because it is the most renally cleared."),
    _v("How do you approach a patient on anticoagulants who needs urgent surgery?",
       "Stop or withhold the anticoagulant. Check full blood count, kidney and liver function, electrolytes including calcium, and the relevant coagulation screen — specifying the anticoagulant and the time of the last dose on the request form. Decide how to proceed on the results, and seek expert advice. In life-threatening situations consider a reversal agent before the results are known. Consider delaying surgery until the drug has cleared or the coagulation screen is normal. Where surgery cannot be delayed, crossmatch blood and consult haematology about controlling bleeding before and during the operation."),
    _v("What are the general assessment steps for anticoagulant-associated bleeding?",
       "Assess and identify the severity of the bleeding; assess for haemodynamic instability; and determine the source and cause of the bleeding."),
    _v("Distinguish minor, moderate and severe bleeding.",
       "Minor: managed with local haemostatic measures; withhold the next dose or cease as appropriate. Moderate: non-trivial bleeding with a haemoglobin fall of less than 20 g/L, or requiring fewer than two units of red cells. Severe or life-threatening: a haemoglobin fall of 20 g/L or more, two or more units of red cells transfused, bleeding at a critical site, or haemodynamic instability."),
    _v("How is moderate bleeding managed?",
       "Ensure senior clinical staff are aware; cease or withhold the anticoagulant; consult the haematology service; apply mechanical compression, or consider surgical intervention or wound packing; provide haemodynamic support and monitor; consider rescue therapy including reversal agents in consultation with a haematologist; consider volume replacement to maintain good urine output, since factor Xa inhibitors are partly renally excreted; and consider platelets if the count is below 70 x 10^9/L or the patient is on a concurrent antiplatelet."),
    _v("How is severe or life-threatening bleeding managed?",
       "Escalate to senior clinical staff. Implement all the measures for moderate bleeding. Stop all anticoagulants, antiplatelet agents and NSAIDs. Consider intensive care, and obtain an urgent surgical or gastroenterology opinion. Follow local massive haemorrhage protocols."),
    _v("List the reversal agents for each anticoagulant.",
       "Unfractionated heparin: protamine sulphate (100% reversal). LMWH — enoxaparin, dalteparin: protamine sulphate (60 to 80% reversal). Warfarin: phytomenadione (vitamin K) and Prothrombinex. Dabigatran: idarucizumab (Praxbind)."),
    _v("What is the mode of action of protamine?",
       "It combines with heparin to form a stable inactive complex, reversing its anticoagulant effect."),
    _v("What is the mode of action of vitamin K (phytomenadione)?",
       "It is an essential cofactor in the synthesis of clotting factors II, VII, IX and X, and of proteins C and S. It therefore reverses the effect of vitamin K antagonists such as warfarin."),
    _v("What is the mode of action of idarucizumab?",
       "It is a humanised monoclonal antibody that binds dabigatran and its metabolites to form a stable inactive complex, reversing the anticoagulant effect."),
    _v("Who is at risk of protamine anaphylaxis?",
       "Patients who have previously received protamine; those on long-term protamine-containing (isophane) insulin such as Protaphane; those who have had a vasectomy; and those allergic to fish or shellfish. They may require antihistamine and corticosteroid premedication with a MET trolley ready. In clinically significant bleeding, the benefit generally still outweighs the risk."),
    _v("How is bleeding on apixaban or rivaroxaban managed?",
       "There is currently no available antidote — andexanet alfa is not TGA-approved. Options: activated charcoal if ingested within 2 hours, though this may be inappropriate if the patient is going to theatre because of aspiration risk; Prothrombinex; consider tranexamic acid; and if the patient is critical, discuss recombinant activated factor VIIa (NovoSeven) with a haematologist. Neither drug can be removed by haemodialysis."),
    _v("How is bleeding on dabigatran managed?",
       "Consider haemodialysis, as dabigatran may be removed by up to 65%. Give activated charcoal if ingested within 2 hours. For life-threatening bleeding or emergency surgery, consider idarucizumab (Praxbind)."),
    _v("How do you transition from IV UFH to another anticoagulant?",
       "To LMWH, rivaroxaban, apixaban or dabigatran: start the new agent within 1 to 2 hours of ceasing the UFH infusion. To warfarin: start warfarin and cease the UFH infusion once the INR is therapeutic."),
    _v("How do you transition from LMWH to another anticoagulant?",
       "To IV UFH: cease LMWH and start the infusion 10 to 12 hours after the last LMWH dose — a bolus is generally not required when switching from another anticoagulant, unless the thrombosis risk is very high. To warfarin: start warfarin and cease LMWH once the INR is therapeutic. To rivaroxaban, apixaban or dabigatran: cease LMWH and start the DOAC when the next LMWH dose would have been due."),
    _v("How do you transition from warfarin to another anticoagulant?",
       "To IV UFH or LMWH: cease warfarin and start the heparin once the INR is below 2 or subtherapeutic. To rivaroxaban, apixaban or dabigatran: cease warfarin and start the DOAC once the INR is below 2."),
    _v("How do you transition from a DOAC to warfarin?",
       "For rivaroxaban and apixaban: overlap warfarin with the DOAC until the INR is therapeutic, testing immediately before the next DOAC dose to minimise the DOAC's own effect on the INR. For dabigatran: overlap warfarin until the INR is therapeutic on warfarin, but note that the INR is unreliable until dabigatran has been ceased for at least 48 hours."),
    _v("How do you transition from one DOAC to another, or from a DOAC to a heparin?",
       "Cease the current DOAC and start the new agent when the next dose of the current DOAC would have been due. For IV UFH, a bolus is generally not required."),
]


# ===========================================================================
# UNIT 3 — INPATIENT DIABETES MANAGEMENT (VIVA)
# ===========================================================================

_INSULIN_VIVA = [
    _v("Outline the significance of diabetes in the Australian healthcare setting.",
       "Diabetes affects 7.4% of Australians over 25, increasing by 0.8% per year, and the prevalence is higher (14% or more) in the Aboriginal and Torres Strait Islander population. Around 25% of hospitalised patients have diabetes. For every diagnosed person with T2DM there is roughly one undiagnosed — about 500,000 Australians. Diabetes is associated with a length of stay around 2 days longer than non-diabetic patients. Insulin is a high-risk medication and a leading cause of prescribing errors."),
    _v("Define the pathophysiology of type 1 diabetes.",
       "T-cell mediated autoimmune destruction of the beta cells, leading to absolute insulin deficiency. These patients are insulin-deficient and at high risk of diabetic ketoacidosis without insulin."),
    _v("Define the pathophysiology of type 2 diabetes.",
       "Varying degrees of insulin resistance with relative insulin deficiency, producing hyperglycaemia. It is heterogeneous in both pathogenesis and clinical manifestation, and in contemporary practice is often diagnosed on HbA1c."),
    _v("What are the diagnostic criteria for diabetes mellitus?",
       "HbA1c of 6.5% or more; fasting plasma glucose of 7 mmol/L or more, with fasting defined as at least 8 hours; a 2-hour plasma glucose of 11.1 mmol/L or more on OGTT, following a 75 g anhydrous glucose load; or classic hyperglycaemic symptoms plus a random glucose of 11.1 mmol/L or more."),
    _v("What do the key symptoms of diabetes tell you at first presentation?",
       "Polyuria, thirst and polydipsia are hyperosmolar symptoms and reflect hyperglycaemia with osmotic diuresis. Weight loss may reflect severe insulin deficiency. Nausea, vomiting and abdominal pain may occur with ketoacidosis."),
    _v("Name four adjunctive tests used to distinguish the diabetes subtype.",
       "1. Autoantibodies directed at islet cell molecules (GAD, IA2, ZnT8) — detection confirms islet cell autoimmunity and is consistent with T1DM. 2. C-peptide with a matched glucose — a low C-peptide is consistent with loss of beta cell mass. 3. Genetic testing, for example for monogenic diabetes (MODY), considered in a younger patient with negative antibodies and a suggestive family history. 4. Anatomical imaging such as CT abdomen, where a pancreatic neoplasm is suspected."),
    _v("Why does correctly identifying the diabetes subtype matter?",
       "It ensures the right therapy — T1DM requires insulin, while T2DM may be treated with non-insulin agents that carry cardiac, renal or weight benefits. It ensures registration with the National Diabetes Services Scheme so the patient gets the right support and supplies. And it enables patients with T1DM to access subsidised continuous glucose monitoring."),
    _v("Describe metformin: mechanism, pros, cons and adverse effects.",
       "Mechanism is poorly understood, but it reduces hepatic gluconeogenesis and improves insulin sensitivity. Pros: cheap, effective, moderate glycaemic benefit of about 1% HbA1c reduction, weight neutral, and no risk of hypoglycaemia. Cons: requires dose reduction in renal impairment, and is contraindicated in end-stage renal failure and severe liver disease. Adverse effects: nausea, vomiting, diarrhoea, and a rare risk of lactic acidosis."),
    _v("How is metformin prescribed and titrated?",
       "Start at 500 mg once or twice daily, best taken with food, and uptitrate slowly to a maximum of 2 g per day. The extended-release form allows daily dosing and may cause less GI upset, though it costs slightly more; the immediate-release form is best given twice daily."),
    _v("What are the metformin dose adjustments for renal impairment?",
       "eGFR above 45: up to 2 g/day. eGFR 30 to 45: up to 1 g/day. eGFR below 30: stop — contraindicated. Also contraindicated in severe liver disease."),
    _v("When must metformin be withheld?",
       "In acute kidney injury; before CT contrast — because although the absolute risk of lactic acidosis is low, the mortality is high if it occurs; and pre-operatively, withheld on the same day."),
    _v("Describe sulfonylureas: mechanism, pros, cons and adverse effects.",
       "Examples are gliclazide, glipizide, glimepiride and glibenclamide. They cause glucose-independent beta-cell secretion of insulin. Pros: moderate glycaemic benefit of about 1% HbA1c reduction, and cheap. Cons and adverse effects: risk of hypoglycaemia and weight gain. They are less commonly initiated now, given the adverse effects and superior alternatives."),
    _v("What are the indications, best practice and dosing for sulfonylureas?",
       "Indications: poor glycaemic control on mono- or dual therapy, and monogenic diabetes (MODY), where patients are highly responsive. Gliclazide and glipizide are safer in older patients and in renal impairment, though glucose monitoring is still needed. Avoid glibenclamide — it is long-acting, renally cleared, and carries the highest risk of hypoglycaemia. Dosing: gliclazide IR 40 to 160 mg twice daily with breakfast and dinner; gliclazide MR 30 to 120 mg daily; glipizide 5 to 20 mg twice daily; glimepiride 1 to 4 mg daily."),
    _v("Describe SGLT2 inhibitors: mechanism, pros, cons and adverse effects.",
       "Examples are empagliflozin (Jardiance) and dapagliflozin (Forxiga). They inhibit SGLT2 in the proximal tubule, which is responsible for 80 to 90% of glucose reabsorption, lowering the plasma glucose threshold for urinary glucose excretion. Pros: cardiac benefit especially in heart failure, with or without diabetes; renal benefit, slowing progression of diabetic nephropathy; modest weight loss of 2 to 3 kg; and a diuretic effect with modest BP lowering. Cons: weak glycaemic effect, about 0.5% HbA1c reduction. Adverse effects: volume depletion, genitourinary infections, and rare euglycaemic DKA."),
    _v("What are the PBS requirements and doses for SGLT2 inhibitors?",
       "Not PBS-subsidised as monotherapy. HbA1c must be above 7.0% despite monotherapy such as metformin, and they must be prescribed in combination with metformin, a sulfonylurea, or insulin. They can be combined with metformin or a DPP4 inhibitor, but a GLP-1 agonist cannot be concurrently prescribed on the PBS. Dosing: empagliflozin 10 or 25 mg daily; dapagliflozin 10 mg daily; ertugliflozin 5 to 15 mg daily."),
    _v("What are the renal thresholds and withholding rules for SGLT2 inhibitors?",
       "Dapagliflozin: do not start if eGFR is below 25 mL/min. Empagliflozin: contraindicated if eGFR is below 30. Ertugliflozin: contraindicated if eGFR is below 45. Review volume balance and concurrent diuretics with any of them. They must be withheld for acute serious illness, for prolonged fasting or bowel prep, and for 72 hours before a procedure, to limit the risk of euglycaemic DKA."),
    _v("Describe GLP-1 receptor agonists: mechanism, pros, cons and adverse effects.",
       "Examples: dulaglutide (Trulicity, weekly subcut), semaglutide (Ozempic, weekly subcut), liraglutide (Victoza, daily subcut). Mechanisms: glucose-dependent stimulation of insulin secretion — so unlike sulfonylureas they do not cause hypos; blunting of glucagon secretion; slowed gastric emptying; and a centrally acting reduction in appetite and food intake. Pros: cardiovascular benefit, particularly for non-fatal stroke, demonstrated for semaglutide and dulaglutide; significant weight loss, especially with semaglutide; and a moderate to high glycaemic effect of around 2% HbA1c reduction. Cons: injectable. Adverse effects: gastrointestinal upset — nausea, vomiting, constipation or diarrhoea."),
    _v("What are the PBS requirements and doses for GLP-1 receptor agonists?",
       "Particularly indicated where there is concurrent obesity and/or atherosclerotic disease. PBS: HbA1c above 7.0% despite monotherapy, in combination with metformin AND a sulfonylurea (unless the SU is contraindicated), or with insulin. An SGLT2 inhibitor cannot be concurrently prescribed on the PBS, and any DPP4 inhibitor must be stopped. Dosing: dulaglutide 1.5 mg subcut weekly with no uptitration; semaglutide uptitrated from 0.25 mg subcut weekly to 1 mg weekly over 8 weeks to reduce GI upset."),
    _v("What are the renal rules and precautions for GLP-1 receptor agonists?",
       "eGFR 15 to 30: use with caution. Dulaglutide may slow renal decline in CKD stage 3 or 4. Contraindicated with a personal or family history of medullary thyroid carcinoma. Caution with prior pancreatitis, with diabetic retinopathy (higher rates seen with semaglutide, likely from rapid glucose lowering), or an eGFR below 30. In hospital: stop in severe illness or acute gastrointestinal illness. They can be continued perioperatively, though if a weekly dose falls immediately post-operatively it may be best to delay it by up to 3 days."),
    _v("Describe DPP4 inhibitors: mechanism, pros, cons and adverse effects.",
       "Examples: sitagliptin (Januvia), linagliptin (Trajenta), vildagliptin (Galvus). They inhibit dipeptidyl peptidase 4, the enzyme that rapidly degrades the incretins GLP-1 and GIP after release, thereby prolonging incretin action. Pros: modest adverse effect profile, and linagliptin is safe in renal failure. Cons: weak glycaemic effect of about 0.5% HbA1c reduction; no weight loss benefit; and no cardiac or renal benefit — saxagliptin in fact carries an increased risk of heart failure hospitalisation. Adverse effects: higher risk of upper respiratory tract infection, headache, and rare pancreatitis."),
    _v("What are the dosing and renal rules for DPP4 inhibitors?",
       "Linagliptin 5 mg daily; sitagliptin 100 mg daily; vildagliptin 50 mg twice daily; saxagliptin 5 mg daily; alogliptin 25 mg daily. Linagliptin is safe at any level of renal impairment and needs no dose reduction; all the other gliptins require dose reduction in CKD stages 3 to 5. They can be continued perioperatively. Use caution if there is a history of pancreatitis."),
    _v("Describe thiazolidinediones (glitazones).",
       "Pioglitazone (Actos) stimulates the nuclear receptor PPAR-gamma, producing insulin sensitisation. Pros: moderate glycaemic effect of about 1% HbA1c reduction, and it can be used in renal failure with no dose reduction. Cons: it is unclear whether it improves diabetes-related complications or mortality, and it has a concerning adverse effect profile — weight gain, fluid retention, oedema, heart failure and fractures. It is third-line and rarely initiated now. Pioglitazone must NOT be used in patients with heart failure."),
    _v("When is insulin initiated in type 2 diabetes, and with what regimen?",
       "When glycaemic control remains inadequate on optimal non-insulin therapy. The approach is stepwise, usually starting with basal insulin plus ongoing oral therapies and/or a GLP-1 receptor agonist, and progressing to pre-mixed or basal-bolus insulin if needed. Other diabetes drugs may be continued, though sulfonylureas are often stopped once quick-acting insulin is introduced, to reduce the risk of hypoglycaemia. Newly diagnosed patients presenting with uncontrolled diabetes may be stabilised on insulin, and non-insulin therapies reintroduced later with insulin stopped."),
    _v("How is insulin therapy split and delivered in type 1 diabetes?",
       "Into basal insulin, to prevent fasting hyperglycaemia and ketosis, at around 50% of the total daily dose; and bolus or prandial insulin, to prevent post-prandial hyperglycaemia, at 40 to 60% of the TDD depending on dietary carbohydrate. Modes: basal-bolus, also called multiple daily injections; or pre-mixed insulin, usually twice daily with meals. Methods: pre-filled disposable pens (most common), cartridges for reusable pens, vials and syringes (rare), or an insulin pump with continuous subcutaneous insulin infusion, usually coupled with continuous glucose monitoring."),
    _v("What are the two methods for calculating mealtime bolus dosing?",
       "A fixed-dose regimen, approximating the dose to the patient's usual portions and glycaemic patterns — for example Novorapid 4 units with breakfast and 6 units with lunch and dinner. Or carbohydrate counting with dose adjustment, using an insulin-to-carbohydrate ratio such as 1 unit per 15 g of carbohydrate, individualised from the TDD and post-prandial patterns. Correctional (supplemental) insulin is then added to adjust for prevailing hyperglycaemia, using the insulin sensitivity factor."),
    _v("List the insulin types with their onset, peak and duration.",
       "Ultra rapid-acting — aspart (Fiasp): onset 5 to 15 min, peak 30 to 90 min, duration 3 h; given at the start of a meal, up to 20 min after starting. Rapid-acting — aspart (Novorapid), lispro (Humalog), glulisine (Apidra): onset 10 to 15 min, peak 60 to 90 min, duration 3 to 5 h; immediately pre-meal. Short-acting — neutral insulin (Actrapid, Humulin R): onset 30 min, peak 2 to 3 h, duration 6 to 8 h; within 30 min pre-meal. Intermediate — isophane (Protaphane, Humulin NPH): onset 1 to 3 h, peak 4 to 12 h, duration 16 to 24 h; daily or twice daily. Long-acting detemir (Levemir): onset 1 to 2 h, peak 6 to 8 h, duration up to 24 h; commonly twice daily. Glargine 100 u/mL (Optisulin): onset 1 to 2 h, no peak, duration 24 h; daily. Glargine 300 u/mL (Toujeo): onset 1 to 6 h, no peak, duration 24 to 36 h; daily."),
    _v("What precautions apply to pre-mixed insulins?",
       "They must be dosed pre-meal, never at bedtime. Those containing quick-acting insulin are preferred over those containing regular insulin. Ryzodeg contains degludec (ultra-long acting) plus aspart (rapid-acting) and can be given once daily with the largest meal. Beware the range of similar-sounding names with very different actions — Humalog, Humulin R, Humulin NPH, Humalog Mix 25, Humalog Mix 50, Humulin 30/70 — and always check with the patient which insulin they actually take."),
    _v("List the key practice points for insulin administration.",
       "Subcutaneous injection only, usually into the abdomen, though the thigh, upper arm or buttock can be used. Avoid long needles — 4 to 5 mm is usually appropriate. Rotate sites to prevent lipohypertrophy and glycaemic variability. Cloudy insulins such as Protaphane and some mixes should be gently rolled before use; modern clear insulins do not need rolling. Ensure basal insulin is never missed. Ensure pre-mixed insulin is dosed with meals, not at bedtime."),
    _v("How often do inpatients need finger-prick BGL monitoring?",
       "Most non-critically ill inpatients: four times daily, pre-meals and at bedtime. An overnight check at 0200 h is appropriate to look for fasting or nocturnal hypoglycaemia. Patients with stable control may not need that check, as it is disruptive. Women with gestational diabetes: fasting 5.0 mmol/L or less, and 2-hour post-prandial 6.7 mmol/L or less. Patients on an insulin infusion need hourly BGL monitoring unless a senior doctor specifies otherwise."),
    _v("Describe continuous glucose monitoring and its subsidisation in Australia.",
       "CGM measures interstitial glucose every 1 to 5 minutes with reasonable accuracy, with customisable alerts for hypo- and hyperglycaemia, reducing the need for confirmatory finger-pricks. For T1DM in Australia it is free for those under 21, for pregnant women or those planning conception, and for concession card holders; all other adults with T1DM pay a copayment of about $32 per month."),
    _v("Contrast the two types of continuous glucose monitor.",
       "Flash or intermittently-scanned CGM (Freestyle Libre 2): worn on the arm for 14 days, stores 8 hours of data, requires scanning with a reader or smartphone, has hypo alarms and customisable high-glucose alarms, and is incompatible with existing insulin pumps. Real-time CGM (Dexcom G6): sensor worn on the abdomen for 10 days, connects automatically by Bluetooth to a smartphone, has hypo alarms and customisable alerts, and is compatible with certain insulin pumps."),
    _v("What is HbA1c, how is average glucose derived from it, and what are its limitations?",
       "HbA1c is a fraction of haemoglobin formed when glucose attaches to HbA1 by non-enzymatic glycation. It reflects glycaemia over the past 3 months, with 50% coming from the past month. Average glucose is estimated as (2 x HbA1c) - 6. It is unreliable in abnormal red cell turnover, haemoglobinopathies, renal and liver disease, and pregnancy (because of haemodilution). Fructosamine, an assay of glycosylated serum protein, is the alternative and reflects the preceding 2 to 3 weeks."),
    _v("How should HbA1c targets be individualised?",
       "The conventional target is around 7.0%. Tighter targets below 6.5% may be achievable in younger patients with shorter disease duration and few comorbidities, or in women planning pregnancy. Looser targets of 8.0 to 8.5% are more appropriate with a history of severe hypos, older age at diagnosis, limited life expectancy, advanced complications, extensive comorbidity, non-adherence, or poor self-care capacity."),
    _v("Why do glycaemic targets matter in hospitalised patients?",
       "Hyperglycaemia, especially above 11 mmol/L, is associated with poor wound healing, delayed recovery from surgery and increased reoperation rates, longer stays and more readmissions, more hospital-acquired infections, increased morbidity, and dehydration with electrolyte disturbance."),
    _v("Why must hypoglycaemia be prevented in hospitalised patients?",
       "Hypoglycaemia (BGL below 4 mmol/L) is associated with rebound hyperglycaemia after treatment, falls, delirium, cardiac events including acute coronary syndrome, arrhythmias and pulmonary oedema, and consumes substantial nursing time and resources."),
    _v("When and how should ketones be measured in hospital?",
       "In patients with diabetes who are unwell and have a BGL above 16 mmol/L. Finger-prick ketones are more accurate and respond more quickly to ketotic change than urinary ketones, and are the preferred modality. Ketoacidosis is more likely in T1DM, but significant ketosis and DKA can occur in T2DM. SGLT2 inhibitors frequently produce ketosis and carry a risk of euglycaemic ketoacidosis during fasting or acute illness."),
    _v("How are blood ketone readings interpreted and acted upon?",
       "Below 0.6 mmol/L: normal, no action. 0.6 to 1.5: more ketones than normal — ensure adequate hydration and repeat in 2 hours. 1.6 to 3.0: potential DKA — interpret in clinical context and send a venous blood gas. Above 3.0: probably DKA — send a VBG and seek senior assistance."),
    _v("Describe the Queensland diagnostic pathway for DKA in adults.",
       "In an unwell patient with T1DM, test BGL and finger-prick ketones. Ketones below 0.6: no ketosis — do not use the protocol; recheck BGL and ketones in 2 hours and treat as clinically indicated. Ketones 0.6 to 1.5 (at risk) or above 1.5 (high risk): check a VBG for pH, bicarbonate and anion gap. If there is no acidosis: do not use the protocol; recheck in 2 hours. If there is acidosis with ketosis — pH below 7.35 AND bicarbonate below 15 AND an elevated anion gap AND ketones above 1 — the patient is in DKA. Note the BGL may be normal or elevated."),
    _v("What six things must be identified when admitting a patient with diabetes?",
       "1. Do they have T1DM, T2DM with or without insulin, or another subtype? 2. What are their usual medications? 3. Are the non-insulin medications safe to continue? 4. If on insulin, is it basal only, multiple daily injections, pre-mixed, or a pump? 5. What is their current or recent glycaemic control? 6. Can they self-manage their insulin?"),
    _v("What are the glucose targets for hospitalised patients?",
       "In most adults with T2DM hospitalised for non-critical illness, regular insulin should be used rather than non-insulin therapies for glycaemic management, though DPP4 inhibitors such as linagliptin may be used in selected patients with mild hyperglycaemia. The typical inpatient target range for non-pregnant patients is 5.0 to 10.0 mmol/L. Targets differ in pregnancy and should be individualised in frail or elderly patients and those prone to hypoglycaemia."),
    _v("How do you calculate initial basal-bolus doses in an insulin-naive patient?",
       "By body weight: basal dose (for example Optisulin) = weight in kg divided by 4. Bolus dose (for example Novorapid) = weight in kg divided by 12, given with each meal."),
    _v("When should basal insulin be charted?",
       "Often at night, at bedtime or with dinner. Patients with renal or liver failure — who have reduced glycogen stores — or those at risk of nocturnal hypoglycaemia, such as the elderly, may do better with morning dosing."),
    _v("How do you convert a patient on pre-mixed insulin to basal-bolus in hospital?",
       "Pre-mixed insulin carries a higher risk of hypoglycaemia in hospital, so in the acute setting it is preferable to convert to basal-bolus. Take the total daily dose, split it 50:50 into basal and bolus, and divide the bolus into three. For example, Novomix 30/70 at 36 units twice daily is a TDD of 72 units: 36 units basal and 36 units bolus, which becomes Optisulin 36 units daily plus Novorapid 12 units with each meal."),
    _v("What is supplemental insulin, and how is the correction factor calculated?",
       "Supplemental insulin is additional quick-acting insulin added to the prevailing bolus orders to correct hyperglycaemia. Prescribe the same quick-acting insulin the patient normally uses. The rule of thumb for the correction factor is 100 divided by the total daily dose — so a T1DM patient with a TDD of 25 units has a factor of 4, meaning 1 unit corrects for every 4 mmol/L above target."),
    _v("What is the standard preparation for an IV insulin infusion in Queensland?",
       "The Queensland Health standing order is 50 units of Actrapid added to 49.5 mL of sodium chloride 0.9%, to a total volume of 50 mL — giving a concentration of 1 unit per mL."),
    _v("What fluids must accompany a routine IV insulin infusion?",
       "The IV insulin chart does not include fluid orders, so they must be ordered separately. Glucose-containing fluids must be co-administered to all patients on routine insulin infusions, to reduce the risk of hypoglycaemia if the line becomes blocked. With normal renal and cardiac function: glucose 3.3% with sodium chloride 0.3%, 1 L at 125 mL/hr; or glucose 5% at 100 to 125 mL/hr with maintenance fluids through a separate line. In patients requiring cautious fluid replacement — fluid restriction, heart failure, renal failure — use glucose 10% starting at 42 to 50 mL/hr. Consider potassium replacement in patients who are nil by mouth or on prolonged IV replacement."),
    _v("What are the indications for starting intravenous insulin?",
       "Hyperglycaemic crisis (DKA or HHS); critically unwell patients including sepsis; and insulin-dependent patients in situations requiring IV insulin — perioperatively, especially for major surgery; prolonged fasting and some bowel preps; unpredictable gut absorption; and diabetes in pregnancy, including intrapartum women with T1DM and women receiving high-dose steroids."),
    _v("Outline the rate adjustments for IV insulin.",
       "Rates come from the IV insulin infusion form, and patients using more than 40 units of glargine daily need the higher regimen. BGL 0 to 5 mmol/L: suspend the insulin infusion and continue the dextrose; if below 4, treat the hypoglycaemia; recheck in 15 minutes. BGL 5.1 to 7: 0.5 units/hr on regimen 1, 1 unit/hr on the higher regimen. BGL 7.1 to 10: 1 versus 2 units/hr. BGL 10.1 to 15: 2 versus 3 units/hr. BGL 15.1 to 20: 3 versus 5 units/hr. BGL above 20: 4 versus 7 units/hr."),
    _v("What additional monitoring is required during an IV insulin infusion?",
       "Chart concurrent glucose-containing fluids, such as 5% dextrose at 100 mL/hr. Check the BGL hourly. Aim for 5.0 to 10.0 mmol/L. If the patient usually takes basal insulin it is usually appropriate to continue it at the usual dose and time, so that the infusion acts as a top-up — this makes it easier to cease the infusion later. Make it explicit to nursing staff that the patient is receiving both IV and subcutaneous insulin, so doses are not missed or confused."),
    _v("When should a diabetes educator be involved, and what do they do?",
       "Always involve the diabetes educator. Their role covers injection technique, BGL monitoring, education about the insulin profile and the effect of food, hypoglycaemia management, and driving advice."),
    _v("What patient-related barriers to insulin administration should be considered?",
       "Fear or reluctance, including needle phobia; compliance; cognitive impairment; manual dexterity; and visual impairment."),
]


# ===========================================================================
# EXPORTS — the bank keys the app loads
# ===========================================================================

def _mcq_key(topic):
    return f"{_C} :: LLP - {topic} (MCQ)"


def _viva_key(topic):
    return f"{_C} :: LLP - {topic} (VIVA)"


# Every LLP topic gets a bank, so the topic appears in the module even when it
# has no questions yet. Do NOT rename these keys once deployed.
LLP_BANKS = {_mcq_key(t): [] for t in LLP_TOPICS}
LLP_VIVA = {_viva_key(t): [] for t in LLP_TOPICS}

LLP_BANKS[_mcq_key(_ANTICOAG)] = _ANTICOAG_MCQ
LLP_VIVA[_viva_key(_ANTICOAG)] = _ANTICOAG_VIVA
LLP_BANKS[_mcq_key(_INSULIN)] = _INSULIN_MCQ
LLP_VIVA[_viva_key(_INSULIN)] = _INSULIN_VIVA


if __name__ == "__main__":
    for t in LLP_TOPICS:
        print(f"{len(LLP_BANKS[_mcq_key(t)]):>3} MCQ  "
              f"{len(LLP_VIVA[_viva_key(t)]):>3} VIVA   {t}")
