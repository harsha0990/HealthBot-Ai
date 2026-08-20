"""
HealthBot AI — ML Training Script (Open Source)
Uses Random Forest + Gradient Boosting ensemble for disease prediction.
Generates SQLite database with full disease info, symptoms, medications, etc.
Run: python train_model.py
"""

import sys
if sys.platform == "win32":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, VotingClassifier
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
import joblib
import os
import json
import sqlite3

# ─────────────────────────────────────────────
# 1. FULL SYMPTOM LIST (132 symptoms)
# ─────────────────────────────────────────────
ALL_SYMPTOMS = [
    "itching","skin_rash","nodal_skin_eruptions","continuous_sneezing",
    "shivering","chills","joint_pain","stomach_pain","acidity",
    "ulcers_on_tongue","muscle_wasting","vomiting","burning_micturition",
    "fatigue","weight_gain","anxiety","cold_hands_and_feets",
    "mood_swings","weight_loss","restlessness","lethargy",
    "patches_in_throat","irregular_sugar_level","cough","high_fever",
    "sunken_eyes","breathlessness","sweating","dehydration",
    "indigestion","headache","yellowish_skin","dark_urine",
    "nausea","loss_of_appetite","pain_behind_the_eyes","back_pain",
    "constipation","abdominal_pain","diarrhoea","mild_fever",
    "yellow_urine","yellowing_of_eyes","acute_liver_failure",
    "fluid_overload","swelling_of_stomach","swelled_lymph_nodes",
    "malaise","blurred_and_distorted_vision","phlegm",
    "throat_irritation","redness_of_eyes","sinus_pressure",
    "runny_nose","congestion","chest_pain","weakness_in_limbs",
    "fast_heart_rate","pain_during_bowel_movements","pain_in_anal_region",
    "bloody_stool","irritation_in_anus","neck_pain","dizziness",
    "cramps","bruising","obesity","swollen_legs",
    "swollen_blood_vessels","puffy_face_and_eyes","enlarged_thyroid",
    "brittle_nails","swollen_extremities","excessive_hunger",
    "extra_marital_contacts","drying_and_tingling_lips","slurred_speech",
    "knee_pain","hip_joint_pain","muscle_weakness","stiff_neck",
    "swelling_joints","movement_stiffness","spinning_sensations",
    "loss_of_balance","unsteadiness","weakness_of_one_body_side",
    "loss_of_smell","bladder_discomfort","foul_smell_of_urine",
    "continuous_feel_of_urine","passage_of_gases","internal_itching",
    "toxic_look_typhos","depression","irritability","muscle_pain",
    "altered_sensorium","red_spots_over_body","belly_pain",
    "abnormal_menstruation","dischromic_patches","watering_from_eyes",
    "increased_appetite","polyuria","family_history","mucoid_sputum",
    "rusty_sputum","lack_of_concentration","visual_disturbances",
    "receiving_blood_transfusion","receiving_unsterile_injections",
    "coma","stomach_bleeding","distention_of_abdomen",
    "history_of_alcohol_consumption","fluid_overload2",
    "blood_in_sputum","prominent_veins_on_calf","palpitations",
    "painful_walking","pus_filled_pimples","blackheads",
    "scurring","skin_peeling","silver_like_dusting",
    "small_dents_in_nails","inflammatory_nails","blister",
    "red_sore_around_nose","yellow_crust_ooze",
    "prognosis","ear_pain","discharge_from_ear",
    "hearing_loss","dry_cough","panic_attacks",
    "numbness","tingling","shortness_of_breath",
    "wheezing","eye_redness"
]

# ─────────────────────────────────────────────
# 2. COMPREHENSIVE DISEASE DATABASE
# ─────────────────────────────────────────────
DISEASE_DB = {
    "Common Cold": {
        "symptoms": ["runny_nose","continuous_sneezing","mild_fever","cough","throat_irritation","headache","fatigue","congestion","watering_from_eyes"],
        "body_system": "respiratory",
        "description": "A viral infection of the upper respiratory tract caused by rhinoviruses. Highly contagious and typically resolves within 7–10 days.",
        "severity": "mild",
        "contagious": True,
        "icd10": "J00",
        "medications": ["Paracetamol 500mg","Cetirizine 10mg","Dextromethorphan syrup","Phenylephrine nasal drops","Vitamin C 1000mg"],
        "precautions": ["Rest adequately","Stay hydrated","Wash hands frequently","Avoid close contact with others","Use steam inhalation"],
        "diets": ["Warm chicken soup","Ginger tea with honey","Citrus fruits (Vitamin C)","Warm broths","Turmeric milk","Garlic-infused foods"],
        "workouts": ["Light walking only","Avoid strenuous exercise","Gentle yoga breathing","Rest is primary treatment"],
        "followup_questions": ["Do you have a sore throat?","Is your nose completely blocked?","Have you had contact with someone sick recently?"],
        "when_to_see_doctor": "If fever exceeds 39°C, symptoms last more than 10 days, or breathing becomes difficult."
    },
    "Influenza (Flu)": {
        "symptoms": ["high_fever","cough","fatigue","muscle_pain","headache","chills","sweating","nausea","vomiting","runny_nose"],
        "body_system": "respiratory",
        "description": "A highly contagious respiratory illness caused by influenza viruses A, B, or C. More severe than common cold with sudden onset.",
        "severity": "moderate",
        "contagious": True,
        "icd10": "J11",
        "medications": ["Oseltamivir (Tamiflu) 75mg","Paracetamol 650mg","Ibuprofen 400mg","Zanamivir inhaler","Electrolyte solutions"],
        "precautions": ["Annual flu vaccination","Complete bed rest","Isolate from vulnerable people","Use N95 mask","Monitor oxygen saturation"],
        "diets": ["Clear broths and soups","Electrolyte-rich drinks","Soft easily digestible foods","Avoid alcohol","Plenty of warm fluids"],
        "workouts": ["Complete rest during acute phase","No exercise for 1 week post-recovery","Gradual return to activity"],
        "followup_questions": ["Did symptoms come on suddenly?","Do you have severe body aches?","Have you been vaccinated this year?"],
        "when_to_see_doctor": "Immediately if breathing difficulty, persistent chest pain, confusion, or severe vomiting occurs."
    },
    "Pneumonia": {
        "symptoms": ["high_fever","cough","breathlessness","chest_pain","phlegm","fatigue","nausea","sweating","chills","rusty_sputum","mucoid_sputum"],
        "body_system": "respiratory",
        "description": "Infection causing inflammation of air sacs in one or both lungs, which may fill with fluid. Can be bacterial, viral, or fungal.",
        "severity": "severe",
        "contagious": True,
        "icd10": "J18",
        "medications": ["Amoxicillin 500mg (bacterial)","Azithromycin 500mg","Doxycycline 100mg","Levofloxacin 750mg","Cough expectorant"],
        "precautions": ["Pneumococcal vaccination","Avoid smoking","Complete antibiotic course","Monitor oxygen levels","Chest physiotherapy"],
        "diets": ["High protein foods","Vitamin C rich foods","Probiotic yogurt","Plenty of fluids","Avoid cold foods"],
        "workouts": ["Complete rest","Breathing exercises post-recovery","Gradual activity after clearance"],
        "followup_questions": ["Are you coughing up colored phlegm?","Do you feel short of breath at rest?","Is the chest pain worse on breathing?"],
        "when_to_see_doctor": "Seek emergency care if O2 saturation below 95%, confusion, or cyanosis (bluish lips)."
    },
    "Asthma": {
        "symptoms": ["breathlessness","wheezing","cough","chest_pain","dry_cough","shortness_of_breath","fatigue","phlegm","throat_irritation"],
        "body_system": "respiratory",
        "description": "A chronic condition causing airway inflammation and narrowing, leading to recurring breathing difficulties triggered by allergens, exercise, or irritants.",
        "severity": "moderate",
        "contagious": False,
        "icd10": "J45",
        "medications": ["Salbutamol inhaler (rescue)","Budesonide inhaler (controller)","Montelukast 10mg","Formoterol inhaler","Prednisolone (acute)"],
        "precautions": ["Identify and avoid triggers","Always carry rescue inhaler","Monitor peak flow","Use spacer with inhaler","Avoid cold air"],
        "diets": ["Anti-inflammatory foods","Magnesium-rich foods","Vitamin D foods","Avoid sulfites","Omega-3 fatty acids"],
        "workouts": ["Swimming (warm water)","Warm-up before exercise","Yoga breathing","Avoid outdoor exercise on high-pollution days"],
        "followup_questions": ["Do symptoms worsen at night or early morning?","What triggers your symptoms?","Do you use any inhalers currently?"],
        "when_to_see_doctor": "Emergency if rescue inhaler not working, lips turn blue, or unable to complete sentences."
    },
    "Diabetes Mellitus Type 2": {
        "symptoms": ["polyuria","increased_appetite","fatigue","weight_loss","blurred_and_distorted_vision","irregular_sugar_level","weakness_in_limbs","excessive_hunger","frequent_infections"],
        "body_system": "endocrine",
        "description": "A metabolic disorder characterized by high blood sugar due to insulin resistance or insufficient insulin production.",
        "severity": "chronic",
        "contagious": False,
        "icd10": "E11",
        "medications": ["Metformin 500mg","Glipizide 5mg","Sitagliptin 100mg","Empagliflozin 10mg","Insulin (if needed)"],
        "precautions": ["Regular blood glucose monitoring","Foot care daily","Eye check-ups annually","HbA1c every 3 months","Avoid skipping meals"],
        "diets": ["Low glycemic index foods","High fiber vegetables","Lean proteins","Avoid sugary drinks","Portion control","Complex carbohydrates"],
        "workouts": ["Brisk walking 30 min daily","Resistance training 2-3x/week","Swimming","Cycling","Yoga for stress management"],
        "followup_questions": ["Do you urinate frequently at night?","Have you noticed increased thirst?","Is there any family history of diabetes?"],
        "when_to_see_doctor": "If blood sugar is consistently above 250mg/dL, or you experience confusion, rapid breathing."
    },
    "Hypertension": {
        "symptoms": ["headache","dizziness","blurred_and_distorted_vision","chest_pain","breathlessness","fatigue","palpitations","nausea"],
        "body_system": "cardiovascular",
        "description": "Persistently elevated blood pressure (≥130/80 mmHg) that strains the heart, arteries, kidneys, and brain.",
        "severity": "chronic",
        "contagious": False,
        "icd10": "I10",
        "medications": ["Amlodipine 5mg","Lisinopril 10mg","Losartan 50mg","Hydrochlorothiazide 12.5mg","Atenolol 50mg"],
        "precautions": ["Monitor BP daily","Reduce sodium intake","Quit smoking","Limit alcohol","Manage stress"],
        "diets": ["DASH diet","Low sodium foods","Potassium-rich foods (banana)","Magnesium-rich foods","Reduce caffeine"],
        "workouts": ["Moderate aerobic exercise 150 min/week","Avoid heavy weightlifting","Yoga and meditation","Swimming","Walking"],
        "followup_questions": ["Do you know your blood pressure readings?","Do you smoke or consume alcohol?","Any family history of hypertension?"],
        "when_to_see_doctor": "Immediately if BP > 180/120, severe headache, vision changes, or chest pain."
    },
    "Heart Attack": {
        "symptoms": ["chest_pain","breathlessness","sweating","nausea","vomiting","fast_heart_rate","weakness_in_limbs","palpitations","dizziness","fatigue","shortness_of_breath"],
        "body_system": "cardiovascular",
        "description": "A medical emergency where blood flow to part of the heart muscle is blocked, causing permanent damage if untreated.",
        "severity": "critical",
        "contagious": False,
        "icd10": "I21",
        "medications": ["Aspirin 325mg (immediate)","Nitroglycerin sublingual","Thrombolytics (hospital)","Beta-blockers","ACE inhibitors"],
        "precautions": ["Call emergency services immediately","Chew aspirin if not allergic","Do not drive yourself","CPR if unconscious","Angioplasty/stenting"],
        "diets": ["Cardiac diet post-recovery","Mediterranean diet","Low saturated fat","High fiber","Omega-3 rich fish"],
        "workouts": ["Cardiac rehabilitation program","Gradual supervised exercise","No strenuous activity without clearance"],
        "followup_questions": ["Is the chest pain radiating to arm or jaw?","Are you sweating profusely?","Do you have a history of heart disease?"],
        "when_to_see_doctor": "CALL 911 IMMEDIATELY. Do not wait."
    },
    "Dengue Fever": {
        "symptoms": ["high_fever","headache","pain_behind_the_eyes","muscle_pain","joint_pain","skin_rash","nausea","vomiting","fatigue","chills"],
        "body_system": "infectious",
        "description": "A mosquito-borne viral infection (Aedes mosquito) causing severe flu-like illness, potentially progressing to dengue hemorrhagic fever.",
        "severity": "severe",
        "contagious": False,
        "icd10": "A90",
        "medications": ["Paracetamol (NOT aspirin/ibuprofen)","IV fluids (hospital)","Platelet transfusion if needed","Electrolyte solutions"],
        "precautions": ["Use mosquito repellents","Wear long sleeves","Eliminate standing water","Use bed nets","Monitor platelet count"],
        "diets": ["Papaya leaf juice (platelet boost)","Coconut water","Pomegranate juice","Kiwi (Vitamin C)","High fluid intake","Avoid oily foods"],
        "workouts": ["Complete bed rest during illness","No exercise until fully recovered","Light walking only after platelet count normalizes"],
        "followup_questions": ["Did symptoms start 4-7 days after mosquito exposure?","Do you have bleeding gums or skin bruising?","Have you been in a tropical region recently?"],
        "when_to_see_doctor": "Immediately if platelet count drops below 100,000 or bleeding occurs."
    },
    "Malaria": {
        "symptoms": ["high_fever","chills","shivering","sweating","headache","nausea","vomiting","muscle_pain","fatigue","diarrhoea"],
        "body_system": "infectious",
        "description": "A life-threatening parasitic disease transmitted by female Anopheles mosquitoes, causing cyclical fever attacks.",
        "severity": "severe",
        "contagious": False,
        "icd10": "B54",
        "medications": ["Chloroquine (P. vivax)","Artemether-Lumefantrine (P. falciparum)","Primaquine","Quinine sulfate","Doxycycline (prophylaxis)"],
        "precautions": ["Antimalarial prophylaxis when traveling","Insecticide-treated bed nets","Mosquito repellent (DEET)","Indoor spraying","Blood smear test"],
        "diets": ["Easy-to-digest foods","Plenty of fluids","Electrolyte drinks","Avoid spicy foods","Rice and boiled vegetables"],
        "workouts": ["Complete bed rest during treatment","No exercise until fully recovered"],
        "followup_questions": ["Are fevers recurring in cycles of 48-72 hours?","Have you traveled to malaria-endemic areas?","Do you have rigors (violent shivering)?"],
        "when_to_see_doctor": "Urgently — malaria can be fatal within 24-48 hours if P. falciparum."
    },
    "Typhoid": {
        "symptoms": ["high_fever","headache","abdominal_pain","constipation","diarrhoea","fatigue","loss_of_appetite","vomiting","malaise","toxic_look_typhos"],
        "body_system": "infectious",
        "description": "A bacterial infection caused by Salmonella typhi, spread through contaminated food and water.",
        "severity": "severe",
        "contagious": True,
        "icd10": "A01",
        "medications": ["Ciprofloxacin 500mg","Azithromycin 1g","Ceftriaxone (IV)","Paracetamol","Chloramphenicol (alternative)"],
        "precautions": ["Typhoid vaccination","Safe water and food","Hand hygiene","Cook food thoroughly","Widal test for diagnosis"],
        "diets": ["Soft bland diet","Rice gruel","Banana","Boiled potatoes","Avoid raw vegetables","High calorie easily digestible foods"],
        "workouts": ["Strict bed rest","No physical activity during treatment","Gentle walks only after recovery"],
        "followup_questions": ["Have you consumed outside food or water recently?","Is the fever higher in the evening?","Do you have rose-colored spots on abdomen?"],
        "when_to_see_doctor": "If intestinal perforation suspected (sudden severe abdominal pain) — emergency surgery needed."
    },
    "COVID-19": {
        "symptoms": ["high_fever","dry_cough","fatigue","loss_of_smell","breathlessness","chest_pain","headache","throat_irritation","muscle_pain","diarrhoea"],
        "body_system": "respiratory",
        "description": "An infectious respiratory illness caused by SARS-CoV-2 coronavirus with a wide spectrum from asymptomatic to critical disease.",
        "severity": "variable",
        "contagious": True,
        "icd10": "U07.1",
        "medications": ["Paracetamol for fever","Remdesivir (hospital)","Dexamethasone (severe)","Tocilizumab","Anticoagulants (severe)"],
        "precautions": ["COVID-19 vaccination","N95/KN95 masks","Hand sanitization","Social distancing","RT-PCR test for diagnosis","Isolate 10 days"],
        "diets": ["Zinc-rich foods","Vitamin D and C","Immunity-boosting foods","Ginger and turmeric","Stay well hydrated"],
        "workouts": ["Complete rest during active infection","Breathing exercises (pranayama) during recovery","Gradual return to activity"],
        "followup_questions": ["Have you lost your sense of smell or taste?","Have you been vaccinated?","What is your oxygen saturation level?"],
        "when_to_see_doctor": "If O2 saturation below 94%, persistent chest pain, or confusion develops."
    },
    "Tuberculosis": {
        "symptoms": ["cough","blood_in_sputum","high_fever","weight_loss","fatigue","sweating","chest_pain","loss_of_appetite","mucoid_sputum","rusty_sputum"],
        "body_system": "respiratory",
        "description": "A bacterial infection by Mycobacterium tuberculosis primarily affecting the lungs but can affect any organ.",
        "severity": "severe",
        "contagious": True,
        "icd10": "A15",
        "medications": ["Isoniazid","Rifampicin","Pyrazinamide","Ethambutol","DOTS therapy (6 months minimum)"],
        "precautions": ["Complete DOTS therapy","Wear N95 mask","Sputum culture test","BCG vaccination","Notify health authorities"],
        "diets": ["High calorie high protein diet","Eggs, milk, meat","Vitamin B6 (pyridoxine) with isoniazid","Avoid alcohol","Green leafy vegetables"],
        "workouts": ["Light activity during treatment","No strenuous exercise","Breathing exercises after sputum conversion"],
        "followup_questions": ["How long have you been coughing?","Have you coughed up blood?","Have you had contact with a TB patient?"],
        "when_to_see_doctor": "Immediately — TB is a notifiable disease requiring supervised treatment."
    },
    "Liver Disease": {
        "symptoms": ["yellowish_skin","yellowing_of_eyes","dark_urine","swelling_of_stomach","loss_of_appetite","fatigue","acute_liver_failure","vomiting","weight_loss","history_of_alcohol_consumption","fluid_overload"],
        "body_system": "digestive",
        "description": "Encompasses conditions including hepatitis, cirrhosis, fatty liver disease causing progressive liver dysfunction.",
        "severity": "severe",
        "contagious": False,
        "icd10": "K76",
        "medications": ["Ursodeoxycholic acid","Lactulose","Spironolactone","Rifaximin","Liver transplant (end-stage)"],
        "precautions": ["Abstain from alcohol completely","Hepatitis B/C vaccination","Regular LFT monitoring","Avoid hepatotoxic drugs","Salt restriction"],
        "diets": ["Low sodium diet","High protein (unless encephalopathy)","Avoid alcohol completely","Small frequent meals","Zinc-rich foods"],
        "workouts": ["Light walking if compensated","Avoid heavy lifting (ascites risk)","Yoga and stretching"],
        "followup_questions": ["Do you consume alcohol?","Have you had hepatitis B or C?","Is your abdomen swollen?"],
        "when_to_see_doctor": "If jaundice appears, abdomen swells, or you become confused (hepatic encephalopathy)."
    },
    "Kidney Disease (CKD)": {
        "symptoms": ["fatigue","swollen_legs","breathlessness","nausea","dark_urine","back_pain","loss_of_appetite","high_fever","dehydration","constipation"],
        "body_system": "urinary",
        "description": "Gradual loss of kidney function affecting fluid, electrolyte balance and waste removal from blood.",
        "severity": "chronic",
        "contagious": False,
        "icd10": "N18",
        "medications": ["ACE inhibitors","Erythropoietin injections","Phosphate binders","Diuretics","Dialysis (advanced)"],
        "precautions": ["Strict BP and glucose control","Low protein diet","Regular creatinine/eGFR monitoring","Avoid NSAIDs","Adequate hydration"],
        "diets": ["Low potassium foods","Low phosphorus diet","Controlled protein intake","Low sodium","Renal-specific diet plan"],
        "workouts": ["Light aerobic exercise","Walking 20-30 minutes","Avoid overexertion","Renal rehabilitation program"],
        "followup_questions": ["Do you have diabetes or hypertension?","Is your urine frothy or bloody?","Do you have swelling in both legs?"],
        "when_to_see_doctor": "If urine output decreases significantly, severe swelling, or breathlessness at rest."
    },
    "Urinary Tract Infection (UTI)": {
        "symptoms": ["burning_micturition","bladder_discomfort","foul_smell_of_urine","yellow_urine","continuous_feel_of_urine","mild_fever","abdominal_pain","back_pain"],
        "body_system": "urinary",
        "description": "Bacterial infection (commonly E. coli) affecting the bladder, urethra, or kidneys. More common in women.",
        "severity": "mild",
        "contagious": False,
        "icd10": "N39.0",
        "medications": ["Nitrofurantoin 100mg","Trimethoprim-Sulfamethoxazole","Ciprofloxacin 500mg","Fosfomycin","Phenazopyridine (pain relief)"],
        "precautions": ["Drink 2-3 liters water daily","Wipe front to back","Urinate after intercourse","Avoid holding urine","Urine culture for recurrent UTI"],
        "diets": ["Cranberry juice","Plenty of water","Probiotic foods","Vitamin C rich foods","Avoid caffeine and alcohol"],
        "workouts": ["Normal activity","Avoid cycling during active infection","Kegel exercises for prevention"],
        "followup_questions": ["Is there a burning sensation when urinating?","Is the urine cloudy or has an unusual smell?","Is there any back/flank pain?"],
        "when_to_see_doctor": "If fever exceeds 38.5°C, back pain is severe (kidney infection), or symptoms persist after 3 days."
    },
    "Migraine": {
        "symptoms": ["headache","nausea","vomiting","blurred_and_distorted_vision","dizziness","pain_behind_the_eyes","fatigue","sensitivity_to_light","sensitivity_to_sound"],
        "body_system": "neurological",
        "description": "A neurological condition causing severe recurring headaches often with nausea, vomiting, and sensitivity to light and sound.",
        "severity": "moderate",
        "contagious": False,
        "icd10": "G43",
        "medications": ["Sumatriptan 50mg (acute)","Rizatriptan","Topiramate (preventive)","Propranolol (preventive)","Ibuprofen 400mg"],
        "precautions": ["Maintain migraine diary","Identify triggers","Regular sleep schedule","Stress management","Avoid bright screens during attack"],
        "diets": ["Avoid tyramine-rich foods (aged cheese)","Magnesium-rich foods","Regular meal timing","Avoid alcohol (especially red wine)","Stay hydrated"],
        "workouts": ["Regular aerobic exercise (prevention)","Yoga for stress","Avoid exercise during attack","Swimming"],
        "followup_questions": ["Is it a throbbing pain on one side?","Do you see visual auras before headache?","Are you sensitive to light and sound?"],
        "when_to_see_doctor": "If worst headache of life, sudden onset, neurological symptoms, or fever with stiff neck."
    },
    "Anxiety Disorder": {
        "symptoms": ["anxiety","restlessness","fast_heart_rate","sweating","fatigue","mood_swings","irritability","headache","muscle_pain","chest_pain","dizziness"],
        "body_system": "mental_health",
        "description": "A mental health disorder characterized by excessive worry, fear, and physical symptoms affecting daily functioning.",
        "severity": "moderate",
        "contagious": False,
        "icd10": "F41",
        "medications": ["Sertraline 50mg","Escitalopram 10mg","Buspirone","Alprazolam (short-term)","Propranolol for performance anxiety"],
        "precautions": ["Cognitive Behavioral Therapy (CBT)","Mindfulness practice","Limit caffeine","Regular sleep","Build support network"],
        "diets": ["Magnesium-rich foods","Omega-3 fatty acids","Avoid caffeine and alcohol","B-vitamin rich foods","Chamomile tea"],
        "workouts": ["Regular aerobic exercise","Yoga and meditation","Tai chi","Deep breathing exercises","Walking in nature"],
        "followup_questions": ["Is the anxiety affecting your daily activities?","Do you have panic attacks?","How long have you been experiencing this?"],
        "when_to_see_doctor": "If interfering with work/relationships or considering self-harm."
    },
    "Depression": {
        "symptoms": ["depression","fatigue","mood_swings","weight_loss","loss_of_appetite","irritability","lethargy","lack_of_concentration","anxiety","restlessness"],
        "body_system": "mental_health",
        "description": "A mood disorder causing persistent feelings of sadness, hopelessness, and loss of interest affecting quality of life.",
        "severity": "moderate",
        "contagious": False,
        "icd10": "F32",
        "medications": ["Fluoxetine 20mg","Sertraline 50mg","Venlafaxine 75mg","Mirtazapine 15mg","Bupropion 150mg"],
        "precautions": ["Regular therapy sessions","Social support","Regular exercise","Sleep hygiene","Avoid alcohol","Medication compliance"],
        "diets": ["Omega-3 fatty acids","Folate-rich foods","Vitamin D","Probiotic foods","Dark chocolate (moderate)","Avoid processed foods"],
        "workouts": ["Aerobic exercise 30 min daily","Yoga","Group fitness classes","Nature walks","Exercise has antidepressant effects"],
        "followup_questions": ["How long have you been feeling this way?","Are you having thoughts of self-harm?","Has this affected your work and relationships?"],
        "when_to_see_doctor": "Immediately if having thoughts of suicide or self-harm."
    },
    "Arthritis": {
        "symptoms": ["joint_pain","swelling_joints","movement_stiffness","fatigue","muscle_pain","knee_pain","hip_joint_pain","back_pain","painful_walking"],
        "body_system": "musculoskeletal",
        "description": "Inflammation of one or more joints causing pain, swelling, and reduced range of motion. Includes osteoarthritis and rheumatoid arthritis.",
        "severity": "chronic",
        "contagious": False,
        "icd10": "M13",
        "medications": ["Ibuprofen 400mg","Diclofenac 50mg","Methotrexate (RA)","Hydroxychloroquine","Corticosteroid injections"],
        "precautions": ["Weight management","Joint protection techniques","Use of assistive devices","Physical therapy","Avoid repetitive joint stress"],
        "diets": ["Anti-inflammatory diet","Omega-3 (fish oil)","Turmeric (curcumin)","Vitamin D and calcium","Avoid processed foods and sugar"],
        "workouts": ["Swimming (low impact)","Cycling","Gentle yoga","Range of motion exercises","Tai chi","Avoid high-impact activities"],
        "followup_questions": ["Is the stiffness worse in the morning?","Which joints are affected?","Is there any family history of arthritis?"],
        "when_to_see_doctor": "If multiple joints are swollen, fever accompanies joint pain, or function is severely limited."
    },
    "Gastroenteritis": {
        "symptoms": ["vomiting","diarrhoea","abdominal_pain","nausea","high_fever","fatigue","dehydration","belly_pain"],
        "body_system": "digestive",
        "description": "Inflammation of the stomach and intestines, typically due to viral or bacterial infection causing vomiting and diarrhea.",
        "severity": "moderate",
        "contagious": True,
        "icd10": "K52",
        "medications": ["ORS solution","Ondansetron 4mg (anti-nausea)","Loperamide (adults)","Ciprofloxacin (bacterial)","Zinc supplements"],
        "precautions": ["Strict hand hygiene","Oral rehydration therapy","Food safety practices","Avoid solid food until vomiting stops","Isolate from food preparation"],
        "diets": ["BRAT diet (Banana, Rice, Applesauce, Toast)","Clear fluids","Oral Rehydration Salts","Avoid dairy initially","Coconut water"],
        "workouts": ["Complete rest until symptoms resolve","Light activity after recovery"],
        "followup_questions": ["How many times have you vomited today?","Is there blood in stool or vomit?","Are you able to keep fluids down?"],
        "when_to_see_doctor": "If signs of dehydration, blood in stool, fever over 39°C, or symptoms persist more than 48 hours."
    },
    "Psoriasis": {
        "symptoms": ["skin_rash","itching","silver_like_dusting","small_dents_in_nails","inflammatory_nails","skin_peeling","joint_pain"],
        "body_system": "dermatological",
        "description": "A chronic autoimmune skin condition causing rapid build-up of skin cells resulting in scaly, itchy patches.",
        "severity": "chronic",
        "contagious": False,
        "icd10": "L40",
        "medications": ["Topical corticosteroids","Calcipotriol cream","Methotrexate","Cyclosporine","Biologics (adalimumab)"],
        "precautions": ["Moisturize regularly","Avoid skin trauma (Koebner effect)","Manage stress","Avoid triggers (alcohol, smoking)","UV phototherapy"],
        "diets": ["Anti-inflammatory diet","Vitamin D foods","Fish oil supplements","Avoid gluten (some patients)","Reduce alcohol"],
        "workouts": ["Regular exercise (reduces inflammation)","Swimming","Yoga","Avoid activities causing skin trauma"],
        "followup_questions": ["Are the plaques silvery-white?","Do you have nail changes?","Is there joint pain (psoriatic arthritis)?"],
        "when_to_see_doctor": "If covering more than 10% body area, or joint pain develops."
    },
    "Eczema (Atopic Dermatitis)": {
        "symptoms": ["skin_rash","itching","skin_peeling","blister","watering_from_eyes","inflammatory_nails","redness_of_eyes"],
        "body_system": "dermatological",
        "description": "A chronic inflammatory skin condition causing itchy, red, and cracked skin, often associated with allergies and asthma.",
        "severity": "moderate",
        "contagious": False,
        "icd10": "L20",
        "medications": ["Topical corticosteroids","Tacrolimus ointment","Dupilumab injection","Antihistamines","Moisturizers (emollients)"],
        "precautions": ["Use fragrance-free products","Keep skin moisturized","Identify triggers","Cool showers","Cotton clothing"],
        "diets": ["Probiotic foods","Omega-3 fatty acids","Avoid known food allergens","Vitamin E foods","Anti-inflammatory diet"],
        "workouts": ["Swimming (rinse off chlorine)","Yoga","Avoid sweating excessively","Wear moisture-wicking clothes"],
        "followup_questions": ["Does itching get worse at night?","Are there any known allergies?","Is there family history of eczema or asthma?"],
        "when_to_see_doctor": "If skin becomes infected (yellow crusting, increased redness), or condition severely impacts sleep."
    },
    "Hypothyroidism": {
        "symptoms": ["fatigue","weight_gain","cold_hands_and_feets","constipation","depression","brittle_nails","puffy_face_and_eyes","enlarged_thyroid","muscle_weakness","mood_swings"],
        "body_system": "endocrine",
        "description": "Underactive thyroid gland failing to produce sufficient thyroid hormones, slowing metabolism.",
        "severity": "chronic",
        "contagious": False,
        "icd10": "E03",
        "medications": ["Levothyroxine (T4) 50-150mcg daily","Liothyronine (T3) in some cases","Selenium supplements"],
        "precautions": ["Take levothyroxine on empty stomach","TSH monitoring every 6 months","Avoid goitrogens in excess","Regular exercise"],
        "diets": ["Iodine-rich foods (limit goitrogens)","Selenium-rich foods","Zinc-rich foods","Avoid excess raw cruciferous vegetables","Adequate calcium"],
        "workouts": ["Regular aerobic exercise","Strength training","Yoga","Walk 30 minutes daily","Helps boost metabolism"],
        "followup_questions": ["Do you feel unusually cold?","Have you noticed hair loss?","Are you constipated frequently?"],
        "when_to_see_doctor": "For TSH testing and regular hormone level monitoring."
    },
    "Panic Disorder": {
        "symptoms": ["anxiety","fast_heart_rate","shortness_of_breath","chest_pain","dizziness","sweating","nausea","panic_attacks","restlessness","palpitations","numbness","tingling"],
        "body_system": "mental_health",
        "description": "Recurrent unexpected panic attacks — sudden intense fear causing physical symptoms like heart pounding and breathlessness.",
        "severity": "moderate",
        "contagious": False,
        "icd10": "F41.0",
        "medications": ["SSRIs (Sertraline)","Clonazepam (short-term)","Alprazolam","Propranolol","Cognitive Behavioral Therapy"],
        "precautions": ["CBT is first-line treatment","Breathing techniques","Exposure therapy","Avoid caffeine","Regular exercise"],
        "diets": ["Magnesium-rich foods","Avoid caffeine and alcohol","B-vitamin rich diet","Omega-3","Chamomile tea"],
        "workouts": ["Regular cardio exercise","Yoga and meditation","Breathing exercises","Progressive muscle relaxation"],
        "followup_questions": ["Do attacks come on suddenly without warning?","Do you fear having another panic attack?","Do you avoid situations that might trigger attacks?"],
        "when_to_see_doctor": "If attacks are frequent, you are avoiding daily activities, or have suicidal thoughts."
    },
    "GERD (Acid Reflux)": {
        "symptoms": ["chest_pain","indigestion","throat_irritation","nausea","acidity","vomiting","cough","belching"],
        "body_system": "digestive",
        "description": "Gastroesophageal reflux disease where stomach acid flows back into the esophagus causing heartburn and irritation.",
        "severity": "moderate",
        "contagious": False,
        "icd10": "K21",
        "medications": ["Omeprazole 20mg","Pantoprazole 40mg","Ranitidine","Antacids (Gaviscon)","Domperidone"],
        "precautions": ["Elevate head of bed","Avoid lying down 3 hours after eating","Small frequent meals","Lose weight if obese","Stop smoking"],
        "diets": ["Avoid spicy and fatty foods","No caffeine or alcohol","Alkaline foods","Low-acid fruits","Non-fat dairy"],
        "workouts": ["Walking after meals","Avoid exercises that worsen reflux","No heavy lifting after meals","Core strengthening"],
        "followup_questions": ["Does the chest pain worsen after eating?","Do you have a sour taste in mouth?","Does lying down worsen symptoms?"],
        "when_to_see_doctor": "If difficulty swallowing, unexplained weight loss, or vomiting blood."
    },
    "Appendicitis": {
        "symptoms": ["abdominal_pain","nausea","vomiting","high_fever","loss_of_appetite","constipation","diarrhoea","fatigue","belly_pain"],
        "body_system": "digestive",
        "description": "Inflammation of the appendix, a finger-shaped pouch attached to the large intestine. Requires urgent surgical treatment.",
        "severity": "critical",
        "contagious": False,
        "icd10": "K37",
        "medications": ["IV antibiotics pre-surgery","Pain management (hospital)","Appendectomy (surgical)"],
        "precautions": ["Emergency surgery (appendectomy)","Do not take laxatives or enemas","Nil by mouth before surgery"],
        "diets": ["Post-surgery: clear liquids then soft foods","High fiber diet for prevention","Avoid constipation"],
        "workouts": ["Rest post-surgery","Light walking 2-4 weeks post-op","No strenuous activity for 4-6 weeks"],
        "followup_questions": ["Is pain worse at the lower right abdomen?","Does pain worsen with movement?","Did pain start around navel then move to right side?"],
        "when_to_see_doctor": "EMERGENCY — if suspected appendicitis requires immediate evaluation."
    },
    "Anemia": {
        "symptoms": ["fatigue","weakness_in_limbs","breathlessness","dizziness","headache","cold_hands_and_feets","pale_skin","fast_heart_rate","loss_of_appetite"],
        "body_system": "hematological",
        "description": "A condition where blood lacks enough healthy red blood cells or hemoglobin to carry adequate oxygen to tissues.",
        "severity": "moderate",
        "contagious": False,
        "icd10": "D50",
        "medications": ["Ferrous sulfate 200mg (iron deficiency)","Folic acid 5mg","Vitamin B12 injections","Erythropoietin","Blood transfusion (severe)"],
        "precautions": ["Regular CBC monitoring","Identify and treat underlying cause","Avoid tea/coffee with iron supplements","Vitamin C enhances iron absorption"],
        "diets": ["Iron-rich foods (red meat, lentils, spinach)","Vitamin C with meals","Folate-rich foods","Vitamin B12 (meat, eggs, dairy)","Avoid tea/coffee with meals"],
        "workouts": ["Light exercise as tolerated","Gradual increase as hemoglobin improves","Yoga breathing exercises","Walking"],
        "followup_questions": ["Do you feel very tired with minimal exertion?","Are you a vegetarian?","Have you had any recent blood loss?"],
        "when_to_see_doctor": "If hemoglobin below 8g/dL, severe breathlessness, or chest pain."
    }
}

# ─────────────────────────────────────────────
# 3. BUILD SQLite DATABASE
# ─────────────────────────────────────────────
def build_database():
    db_path = os.path.join("instance", "healthbot.db")
    os.makedirs("instance", exist_ok=True)
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Diseases table
    c.execute("""
        CREATE TABLE IF NOT EXISTS diseases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            body_system TEXT,
            description TEXT,
            severity TEXT,
            contagious INTEGER,
            icd10 TEXT,
            when_to_see_doctor TEXT
        )
    """)

    # Disease details tables
    c.execute("""
        CREATE TABLE IF NOT EXISTS disease_medications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            disease_name TEXT,
            medication TEXT,
            FOREIGN KEY(disease_name) REFERENCES diseases(name)
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS disease_precautions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            disease_name TEXT,
            precaution TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS disease_diets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            disease_name TEXT,
            diet TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS disease_workouts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            disease_name TEXT,
            workout TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS disease_symptoms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            disease_name TEXT,
            symptom TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS disease_followup (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            disease_name TEXT,
            question TEXT
        )
    """)

    # Patient profiles
    c.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            age INTEGER,
            gender TEXT,
            blood_type TEXT,
            allergies TEXT,
            chronic_conditions TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Patient health history
    c.execute("""
        CREATE TABLE IF NOT EXISTS health_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            session_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            symptoms TEXT,
            predicted_disease TEXT,
            confidence REAL,
            age INTEGER,
            gender TEXT,
            duration TEXT,
            notes TEXT,
            FOREIGN KEY(patient_id) REFERENCES patients(id)
        )
    """)

    # Insert disease data
    for name, d in DISEASE_DB.items():
        c.execute("""
            INSERT OR REPLACE INTO diseases (name, body_system, description, severity, contagious, icd10, when_to_see_doctor)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (name, d["body_system"], d["description"], d["severity"], int(d["contagious"]), d.get("icd10",""), d.get("when_to_see_doctor","")))

        c.execute("DELETE FROM disease_medications WHERE disease_name=?", (name,))
        c.execute("DELETE FROM disease_precautions WHERE disease_name=?", (name,))
        c.execute("DELETE FROM disease_diets WHERE disease_name=?", (name,))
        c.execute("DELETE FROM disease_workouts WHERE disease_name=?", (name,))
        c.execute("DELETE FROM disease_symptoms WHERE disease_name=?", (name,))
        c.execute("DELETE FROM disease_followup WHERE disease_name=?", (name,))

        for item in d.get("medications", []):
            c.execute("INSERT INTO disease_medications (disease_name, medication) VALUES (?,?)", (name, item))
        for item in d.get("precautions", []):
            c.execute("INSERT INTO disease_precautions (disease_name, precaution) VALUES (?,?)", (name, item))
        for item in d.get("diets", []):
            c.execute("INSERT INTO disease_diets (disease_name, diet) VALUES (?,?)", (name, item))
        for item in d.get("workouts", []):
            c.execute("INSERT INTO disease_workouts (disease_name, workout) VALUES (?,?)", (name, item))
        for item in d.get("symptoms", []):
            c.execute("INSERT INTO disease_symptoms (disease_name, symptom) VALUES (?,?)", (name, item))
        for item in d.get("followup_questions", []):
            c.execute("INSERT INTO disease_followup (disease_name, question) VALUES (?,?)", (name, item))

    conn.commit()
    conn.close()
    print(f"✓ Database created at {db_path}")
    return db_path


# ─────────────────────────────────────────────
# 4. BUILD TRAINING DATASET
# ─────────────────────────────────────────────
def build_dataset():
    rows = []
    for disease, d in DISEASE_DB.items():
        symptoms = d["symptoms"]
        for _ in range(60):
            row = {s: 0 for s in ALL_SYMPTOMS}
            num_syms = max(3, len(symptoms) - np.random.randint(0, 3))
            chosen = np.random.choice(symptoms, min(num_syms, len(symptoms)), replace=False)
            for s in chosen:
                if s in row:
                    row[s] = 1
            noise = np.random.choice(ALL_SYMPTOMS, np.random.randint(0, 3), replace=False)
            for s in noise:
                row[s] = 1
            row["disease"] = disease
            rows.append(row)
    return pd.DataFrame(rows)


# ─────────────────────────────────────────────
# 5. TRAIN RANDOM FOREST + ENSEMBLE
# ─────────────────────────────────────────────
def train():
    print("\n" + "="*55)
    print("  HealthBot AI — ML Training (Open Source)")
    print("="*55)

    build_database()

    print("\n[1/4] Building training dataset...")
    df = build_dataset()
    X = df[ALL_SYMPTOMS]
    y = df["disease"]

    le = LabelEncoder()
    y_enc = le.fit_transform(y)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y_enc, test_size=0.2, random_state=42, stratify=y_enc
    )

    print(f"      Samples: {len(X_train)} train / {len(X_test)} test")
    print(f"      Features: {len(ALL_SYMPTOMS)} symptoms")
    print(f"      Classes: {len(le.classes_)} diseases")

    print("\n[2/4] Training Random Forest Classifier...")
    rf = RandomForestClassifier(
        n_estimators=500,
        max_depth=None,
        min_samples_leaf=1,
        min_samples_split=2,
        max_features="sqrt",
        random_state=42,
        n_jobs=-1,
        class_weight="balanced"
    )
    rf.fit(X_train, y_train)
    rf_acc = accuracy_score(y_test, rf.predict(X_test))
    print(f"      Random Forest Accuracy: {rf_acc:.4f} ({rf_acc*100:.2f}%)")

    print("\n[3/4] Training Gradient Boosting Classifier...")
    gb = GradientBoostingClassifier(
        n_estimators=200,
        learning_rate=0.1,
        max_depth=5,
        random_state=42
    )
    gb.fit(X_train, y_train)
    gb_acc = accuracy_score(y_test, gb.predict(X_test))
    print(f"      Gradient Boosting Accuracy: {gb_acc:.4f} ({gb_acc*100:.2f}%)")

    # Use RF as primary (faster inference, high accuracy)
    clf = rf

    print("\n[4/4] Cross-validation & saving models...")
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_scores = cross_val_score(clf, X, y_enc, cv=cv, scoring="accuracy")
    print(f"      5-Fold CV: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")

    os.makedirs("models", exist_ok=True)
    joblib.dump(clf, "models/disease_model.pkl")
    joblib.dump(le, "models/label_encoder.pkl")

    with open("models/symptoms.json", "w", encoding="utf-8") as f:
        json.dump(ALL_SYMPTOMS, f, indent=2)
    with open("models/disease_db.json", "w", encoding="utf-8") as f:
        json.dump(DISEASE_DB, f, indent=2)

    # Feature importance
    importances = rf.feature_importances_
    feat_imp = sorted(zip(ALL_SYMPTOMS, importances), key=lambda x: x[1], reverse=True)[:20]
    with open("models/feature_importance.json", "w", encoding="utf-8") as f:
        json.dump([{"symptom": s, "importance": round(float(v), 6)} for s, v in feat_imp], f, indent=2)

    print("\n" + "="*55)
    print("  ✓ Models saved to models/")
    print("  ✓ Database saved to instance/healthbot.db")
    print(f"  ✓ Final Accuracy: {rf_acc*100:.2f}%")
    print("  Run: python app.py")
    print("="*55 + "\n")


if __name__ == "__main__":
    train()
