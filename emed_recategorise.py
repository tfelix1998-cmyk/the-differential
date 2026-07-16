"""
emed_recategorise.py — load-time correction of miscategorised EMED questions.
============================================================================

Some EMED questions were bulk-imported and auto-binned by keyword, which filed
a number of them under the wrong specialty (a car-crash trauma question under
"Motor Neuron Disease", an egg-allergy child under "Oesophageal Pathology",
ovarian cancer under "Colorectal Cancer", and so on).

This layer MOVES those questions to the correct bank at load time. Each move
was read and judged individually — this is deliberately NOT an automated
keyword re-bin, because keyword logic is exactly what caused the original
mistakes (a GI cancer legitimately touches both Gastroenterology and Oncology).
Only questions whose content clearly contradicts their bank are moved.

Keyed by a stable content hash of the (normalised) first 120 chars of the stem,
so it survives the index shifts that clean_banks() introduces when it drops
unservable questions. Applied AFTER clean_banks in uq._load_content().

Reversible and auditable: every move records where it came from and a stem
preview. To undo one, delete its entry.
"""

import re
import hashlib


def _sig(question_text):
    s = re.sub(r"\s+", " ", (question_text or "")).strip().lower()
    return hashlib.sha1(s[:120].encode()).hexdigest()[:16]


# content-hash -> destination bank key. (Provenance in the comment.)
MOVES = {
    # Cardiology/DVT -> Breast Cancer: Post-mastectomy lymphoedema (Stemmer's sign), not DVT
    '140508028ff80536': 'UQ Critical Care Module :: EMED - Oncology - Breast Cancer (MCQ)',
    # Gastro/Colorectal Cancer -> Ovarian Pathology: Krukenberg - bilateral ovarian masses + gastric wall thickening
    '680bf0874b8fe5b1': 'UQ Critical Care Module :: EMED - Gynaecology - Ovarian Pathology (MCQ)',
    # Gastro/Colorectal Cancer -> Ovarian Pathology: Ovarian mass + CA-125, not colorectal
    '5e5f21baa6d7f48c': 'UQ Critical Care Module :: EMED - Gynaecology - Ovarian Pathology (MCQ)',
    # Gastro/Oesophageal Pathology -> General Paediatrics: Egg allergy in a 3-year-old, not oesophageal
    'd5d130ce58d8e4fb': 'UQ Critical Care Module :: EMED - Paediatrics - General Paediatrics (MCQ)',
    # Neurology/Spinal Cord Injury -> Paediatric Neurology / Development: Autism + lead poisoning in a child
    '9c4ce6ebd7538b41': 'UQ Critical Care Module :: EMED - Paediatrics - Paediatric Neurology / Development (MCQ)',
    # Neurology/Motor Neuron Disease -> Traumatic Brain Injury: Car-crash primary survey / head injury
    '968ff5b2d6659de8': 'UQ Critical Care Module :: EMED - Neurology - Traumatic Brain Injury (MCQ)',
    # Oncology/Palliative Care -> Communication / Boundaries: Antimicrobial-stewardship professionalism scenario
    'a326a824f01d66d5': 'UQ Critical Care Module :: EMED - Professional Practice - Communication / Boundaries (MCQ)',
    # Oncology/Palliative Care -> Communication / Boundaries: Antimicrobial-stewardship professionalism scenario (2)
    'a3326cd8ea41689c': 'UQ Critical Care Module :: EMED - Professional Practice - Communication / Boundaries (MCQ)',
    # Respiratory/Lung Cancer -> Appendicitis: Appendicitis in a 19-year-old woman, not lung cancer
    '5d2e5281082d6d11': 'UQ Critical Care Module :: EMED - Gastroenterology - Appendicitis (MCQ)',

    # ---- Neurology / Seizures-Epilepsy bank cleanup (hand-audited) ----
    # These were filed under Seizures because the vignette mentions a seizure or
    # neurology in passing, but the question tests something else entirely.
    # 16p11.2 deletion + developmental delay / ASD -> Genetics
    '699d79d496727f16': 'UQ Critical Care Module :: EMED - Genetics - Inheritance Patterns (MCQ)',
    # Facial nerve palsy localisation (LMN vs UMN) -> General Neurology, not seizures
    'd64756bfe42f85ca': 'UQ Critical Care Module :: EMED - Neurology - General Neurology (MCQ)',
    # Lymphangiosarcoma (Stewart-Treves) on post-mastectomy lymphoedema -> Oncology
    '0d9a1c68d40a37dd': 'UQ Critical Care Module :: EMED - Oncology - General Oncology (MCQ)',
    # Hyponatraemia correction / central pontine myelinolysis -> Acid-Base / electrolytes
    '8c3acf9311f168c6': 'UQ Critical Care Module :: EMED - Renal - Acid-Base Balance (MCQ)',
    # MMSE 18/30, progressive memory loss -> Dementia, not Seizures
    'cb414b93cdbc4b12': 'UQ Critical Care Module :: EMED - Neurology - Dementia (MCQ)',
    # Benzodiazepine (oxazepam) dependence / switching -> Substance Use
    '044c3837acbb063d': 'UQ Critical Care Module :: EMED - Psychiatry - Substance Use (MCQ)',
    # Stevens-Johnson syndrome (drug eruption) -> Dermatology
    'becdab93d305ca77': 'UQ Critical Care Module :: EMED - Dermatology - Rashes / Other Dermatoses (MCQ)',
    # TCA overdose ECG (wide QRS, R in aVR) -> Toxicology
    '7ff08eca6dce43c3': 'UQ Critical Care Module :: EMED - Toxicology - Toxicology Treatments (MCQ)',
    # Alprazolam dependence / tapering -> Substance Use
    'a1841af9692f598d': 'UQ Critical Care Module :: EMED - Psychiatry - Substance Use (MCQ)',

    # ---- Magnet-bank cleanup (Lung Cancer / UTI / Hernia, hand-audited) ----
    # Neck lump: laryngeal/thyroid carcinoma with hoarseness -> ENT, not Lung Cancer
    'f461126ec9bdfbaf': 'UQ Critical Care Module :: EMED - ENT - Neck Lump (MCQ)',
    # Genital/perianal warts, Mpox differential -> STI, not Lung Cancer
    '57eb592c15119f41': 'UQ Critical Care Module :: EMED - Infectious Disease - Sexually Transmitted Infection (MCQ)',
    # Chemical (alkaline) eye burn with symblepharon -> Red Eye, not Lung Cancer
    'b516385c5fa062ee': 'UQ Critical Care Module :: EMED - Ophthalmology - Red Eye (MCQ)',
    # Myasthenia gravis (fatigable diplopia, pyridostigmine) -> Neurology, not Lung Cancer
    '48a1f93892f6fc31': 'UQ Critical Care Module :: EMED - Neurology - General Neurology (MCQ)',
    # Bronchiolitis in a 6-month-old -> Paediatric Respiratory, not UTI
    'c321869c984c0288': 'UQ Critical Care Module :: EMED - Paediatrics - Paediatric Respiratory (MCQ)',
    # Childhood strabismus / amblyopia -> Ophthalmology, not Hernia
    '8084679d98c715dd': 'UQ Critical Care Module :: EMED - Ophthalmology - General Ophthalmology (MCQ)',
    # Delusional disorder (Othello/Capgras) in polysubstance user -> Psychiatry, not Hernia
    '4effa762a6ec76f2': 'UQ Critical Care Module :: EMED - Psychiatry - Schizophrenia / Psychosis (MCQ)',

    # ---- Batch 3: high-flag banks (hand-audited) ----
    # Monochorionic twin pregnancy complication -> Obstetrics, not Hypertension
    '7815b4794fcf7ac4': 'UQ Critical Care Module :: EMED - Obstetrics - General Obstetrics (MCQ)',
    # Splenic injury after a fall -> Major Trauma, not Hypertension
    'd935a7ecb627a3b6': 'UQ Critical Care Module :: EMED - Trauma / Emergency - Major Trauma (MCQ)',
    # Terminal delirium in metastatic lung cancer -> Palliative, not Hypertension
    '431a7a2c1d42426a': 'UQ Critical Care Module :: EMED - Oncology - Palliative Care (MCQ)',
    # Acute soccer knee (ACL/meniscus) -> Soft Tissue Injury, not Palliative Care
    '7f8cc904b47192ef': 'UQ Critical Care Module :: EMED - Musculoskeletal - Soft Tissue Injury (MCQ)',
    # Childhood syncope / long-QT -> Cardiac Arrhythmia, not Lymphoma
    '9020ff7f61718940': 'UQ Critical Care Module :: EMED - Cardiology - Cardiac Arrhythmia (MCQ)',
    # Meniere's disease (vertigo + aural fullness + tinnitus) -> ENT Vertigo, not RCC
    '035dabcceaa20304': 'UQ Critical Care Module :: EMED - ENT - Vertigo / Vestibular (MCQ)',
    # Bacillus cereus food poisoning outbreak in children -> Gastroenteritis, not RCC
    '700d025a96433012': 'UQ Critical Care Module :: EMED - Infectious Disease - Gastroenteritis / Food Poisoning (MCQ)',
    # Nasal bone fracture / septal haematoma -> ENT, not Bowel Perforation
    '27ba2122c65329b1': 'UQ Critical Care Module :: EMED - ENT - Sinusitis / Rhinitis (MCQ)',
    # Otitis media in an 18-month-old -> Paediatric Fever/Infection, not Bowel Perforation
    '66d34100d304c4a7': 'UQ Critical Care Module :: EMED - Paediatrics - Paediatric Fever / Infection (MCQ)',
    # Nasal septal perforation (occupational) -> ENT, not Bowel Perforation
    'd0e2681a018187bf': 'UQ Critical Care Module :: EMED - ENT - Sinusitis / Rhinitis (MCQ)',
    # Benign breast lump referral -> Breast surgery, not Bowel Perforation
    '654dc6027633afb4': 'UQ Critical Care Module :: EMED - Surgery - Breast Lump / Benign Breast (MCQ)',

    # ---- Batch 4: medium-density banks (hand-audited) ----
    # Age-related macular degeneration (reading/crosswords) -> Ophthalmology, not GORD
    'a60b75163b1892ce': 'UQ Critical Care Module :: EMED - Ophthalmology - Macular Degeneration (MCQ)',
    # Morton's neuroma (forefoot burning pain) -> MSK, not PE
    '7d227125d473da17': 'UQ Critical Care Module :: EMED - Musculoskeletal - General Musculoskeletal (MCQ)',
    # Acute dystonia from haloperidol -> Neurology, not PE
    '4dacd799fd6fcf5f': 'UQ Critical Care Module :: EMED - Neurology - General Neurology (MCQ)',
    # Corticosteroid-induced mania -> Psychiatry (Bipolar), not COPD
    'f19f3c6ee761a0db': 'UQ Critical Care Module :: EMED - Psychiatry - Bipolar Disorder (MCQ)',
    # Cauda equina red flags (back pain + leg weakness) -> Spinal, not COPD
    '6582f962e4e6bd65': 'UQ Critical Care Module :: EMED - Neurology - Spinal Cord Injury / Cauda Equina (MCQ)',
    # Diabetic foot ulcer + ABI (peripheral arterial) -> Vascular PAD, not Vasculitis
    'c3a808cf1a987837': 'UQ Critical Care Module :: EMED - Vascular - Peripheral Arterial Disease (MCQ)',
    # Aortic dissection (tearing chest->back pain) -> Aortic Dissection, not Vasculitis
    'a41c4638024264a8': 'UQ Critical Care Module :: EMED - Cardiology - Aortic Dissection (MCQ)',
    # Budd-Chiari syndrome (OCP, distension, jaundice) -> Hepatology, not Transfusion
    '0eb9e92bcad5db51': 'UQ Critical Care Module :: EMED - Hepatology - Alcoholic Liver Disease / Cirrhosis (MCQ)',
    # Death certification procedure -> Professional Practice, not Sodium Disorders
    'e0ab823de40ab886': 'UQ Critical Care Module :: EMED - Professional Practice - Ethics / Consent (MCQ)',
    # Multinodular goitre / thyroid neck mass -> Thyroid, not Gastric Cancer
    '69b18a7af8c0269c': 'UQ Critical Care Module :: EMED - Endocrinology - Thyroid Nodule / Cancer (MCQ)',
    # Pregnant trauma + CTG interpretation -> Obstetrics, not Spinal Cord Injury
    '9c976d0925209825': 'UQ Critical Care Module :: EMED - Obstetrics - General Obstetrics (MCQ)',
    # Post-thyroidectomy hypocalcaemia (perioral tingling) -> Calcium, not Spinal Cord Injury
    '7b7660c9de6a2bcc': 'UQ Critical Care Module :: EMED - Endocrinology - Calcium / Parathyroid (MCQ)',

    # ---- Batch 5: long tail + pharmacology care (hand-audited) ----
    # Vesicovaginal fistula after pelvic surgery (continuous leakage) -> Gynae, not Cholesterol
    '37a602d94847badd': 'UQ Critical Care Module :: EMED - Gynaecology - General Gynaecology (MCQ)',
    # HSV encephalitis (fever + confusion + focal signs) -> Encephalitis, not Rashes
    '6e57d60aa2f640b8': 'UQ Critical Care Module :: EMED - Neurology - Encephalitis (MCQ)',
    # IVDU + new murmur + positive cultures -> Infective Endocarditis, not Opioids
    '3a066b69c5c4a5df': 'UQ Critical Care Module :: EMED - Cardiology - Infective Endocarditis (MCQ)',
    # ESRD renal replacement therapy choice -> CKD, not Bowel Obstruction
    '948f81a8b67696f4': 'UQ Critical Care Module :: EMED - Renal - Chronic Kidney Disease (MCQ)',
    # Recurrent infections / immunodeficiency in an infant -> Paediatric Respiratory, not Pneumonia
    '9da72f548f711702': 'UQ Critical Care Module :: EMED - Paediatrics - Paediatric Respiratory (MCQ)',
    # Postpartum lactational mastitis -> Breast, not (Trauma) Toxicology
    'a58845dd264d9972': 'UQ Critical Care Module :: EMED - Surgery - Breast Lump / Benign Breast (MCQ)',
    # GPA (nasal crusting, saddle nose, ANCA options) -> Vasculitis, not Red Eye
    'f4c3ea19e55f4ad4': 'UQ Critical Care Module :: EMED - Musculoskeletal - Vasculitis / Autoimmune (MCQ)',
    # Cotard/nihilistic delusion in psychotic depression -> Depression, not Potassium
    '3578361fea4dcd01': 'UQ Critical Care Module :: EMED - Psychiatry - Depression (MCQ)',

    # ---- Batch 6: remaining 2+ flag banks (hand-audited) ----
    # Paronychia / finger infection -> Skin Infection, not Atrial Fibrillation
    '2a06087b45cfc469': 'UQ Critical Care Module :: EMED - Dermatology - Cellulitis / Skin Infection (MCQ)',
    # Paget's disease bone pain + headaches -> MSK, not Heart Failure
    'c3e4a0a347926d10': 'UQ Critical Care Module :: EMED - Musculoskeletal - General Musculoskeletal (MCQ)',
    # Fetal congenital heart on morphology scan -> Obstetrics, not Heart Failure
    '0dd6d855c1d0af9f': 'UQ Critical Care Module :: EMED - Obstetrics - General Obstetrics (MCQ)',
    # Myasthenia gravis (fatigable weakness) -> Neurology, not Eczema
    '63ef06bd1f3e3ca5': 'UQ Critical Care Module :: EMED - Neurology - General Neurology (MCQ)',
    # Breast retraction / skin change -> Breast Cancer, not Eczema
    'a826849ab6956fa5': 'UQ Critical Care Module :: EMED - Oncology - Breast Cancer (MCQ)',
    # Paediatric mastocytosis (Darier's sign) skin lesion -> Dermatology, not Cholecystitis
    'a6c0bf1cbaf14bac': 'UQ Critical Care Module :: EMED - Dermatology - Rashes / Other Dermatoses (MCQ)',
    # Hidradenitis suppurativa (axillary) -> Dermatology, not Ovarian Pathology
    'ccaf09c9e8598aa5': 'UQ Critical Care Module :: EMED - Dermatology - Rashes / Other Dermatoses (MCQ)',
    # Morton's neuroma (high heels, forefoot) -> MSK, not Septic Arthritis
    'f5925b0e8a61f5f7': 'UQ Critical Care Module :: EMED - Musculoskeletal - General Musculoskeletal (MCQ)',
    # Postpartum lactational mastitis -> Breast, not Labour and Delivery
    'a01501d169439e8f': 'UQ Critical Care Module :: EMED - Surgery - Breast Lump / Benign Breast (MCQ)',
    # Postpartum lactational mastitis -> benign Breast, not Breast Cancer
    '79c55a50669afd00': 'UQ Critical Care Module :: EMED - Surgery - Breast Lump / Benign Breast (MCQ)',
    # Post-knee-replacement PE -> Pulmonary Embolism, not General Neurology
    'a22269d71a07eabe': 'UQ Critical Care Module :: EMED - Respiratory - Pulmonary Embolism (MCQ)',

    # ---- Batch 6 tail: strict single-flag sweep (hand-audited) ----
    # Warfarin-associated intracranial haemorrhage -> Haemorrhagic Stroke, not Personality Disorder
    '1fc1d38053e4be0e': 'UQ Critical Care Module :: EMED - Neurology - Haemorrhagic Stroke / SAH (MCQ)',
    # Marfan aortic dissection in pregnancy -> Aortic Dissection, not Vasculitis
    '0bbac31329cf3117': 'UQ Critical Care Module :: EMED - Cardiology - Aortic Dissection (MCQ)',
}


def apply_moves(banks):
    """Move miscategorised questions to their correct bank. `banks` is the
    fully-cleaned EMED dict. Returns a new dict; originals are not mutated."""
    if not MOVES:
        return banks
    out = {k: list(v) for k, v in banks.items()}
    pending = []
    for bank, qs in list(out.items()):
        keep = []
        for q in qs:
            dest = MOVES.get(_sig(q.get("question_text", "")))
            if dest and dest != bank and dest in out:
                pending.append((dest, q))
            else:
                keep.append(q)
        out[bank] = keep
    for dest, q in pending:
        out[dest].append(q)
    return out
