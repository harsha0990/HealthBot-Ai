"""
HealthBot AI — Flask Backend (Open Source)
Features: Random Forest ML, Patient Profiles, Health History,
          Body-System Follow-ups, Printable Reports, SQLite DB
"""

import sys
if sys.platform == "win32":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")

import os, json, re, ast, joblib, sqlite3, datetime
import numpy as np
import pandas as pd
from flask import Flask, render_template, request, jsonify, session
import subprocess

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-only-change-me")  # set a real SECRET_KEY env var in production

BASE = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE, "instance", "healthbot.db")

# ─────────────────────────────────────────────
# AUTO-TRAIN IF MODEL MISSING
# ─────────────────────────────────────────────
def ensure_model():
    model_path = os.path.join(BASE, "models", "disease_model.pkl")
    db_exists   = os.path.exists(DB_PATH)
    if not os.path.exists(model_path) or not db_exists:
        print("Training model and building database...")
        result = subprocess.run(
            [sys.executable, os.path.join(BASE, "train_model.py")],
            cwd=BASE, capture_output=False
        )
        if result.returncode != 0:
            raise RuntimeError("Training failed. Run: python train_model.py")

ensure_model()

clf = joblib.load(os.path.join(BASE, "models", "disease_model.pkl"))
le  = joblib.load(os.path.join(BASE, "models", "label_encoder.pkl"))
if hasattr(clf, "n_jobs"):
    clf.n_jobs = 1

with open(os.path.join(BASE, "models", "symptoms.json"), encoding="utf-8") as f:
    ALL_SYMPTOMS = json.load(f)
with open(os.path.join(BASE, "models", "disease_db.json"), encoding="utf-8") as f:
    DISEASE_DB = json.load(f)

# ─────────────────────────────────────────────
# DATABASE HELPERS
# ─────────────────────────────────────────────
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_disease_info(disease_name):
    conn = get_db()
    c = conn.cursor()
    row = c.execute("SELECT * FROM diseases WHERE name=?", (disease_name,)).fetchone()
    if not row:
        info = DISEASE_DB.get(disease_name, {})
        return {
            "disease": disease_name,
            "body_system": info.get("body_system", "general"),
            "description": info.get("description", ""),
            "severity": info.get("severity", ""),
            "contagious": info.get("contagious", False),
            "icd10": info.get("icd10", ""),
            "medications": info.get("medications", []),
            "precautions": info.get("precautions", []),
            "diets": info.get("diets", []),
            "workouts": info.get("workouts", []),
            "when_to_see_doctor": info.get("when_to_see_doctor", ""),
            "followup_questions": info.get("followup_questions", [])
        }
    meds  = [r[0] for r in c.execute("SELECT medication FROM disease_medications WHERE disease_name=?", (disease_name,))]
    precs = [r[0] for r in c.execute("SELECT precaution FROM disease_precautions WHERE disease_name=?", (disease_name,))]
    diets = [r[0] for r in c.execute("SELECT diet FROM disease_diets WHERE disease_name=?", (disease_name,))]
    works = [r[0] for r in c.execute("SELECT workout FROM disease_workouts WHERE disease_name=?", (disease_name,))]
    fqs   = [r[0] for r in c.execute("SELECT question FROM disease_followup WHERE disease_name=?", (disease_name,))]
    conn.close()
    return {
        "disease": disease_name,
        "body_system": row["body_system"],
        "description": row["description"],
        "severity": row["severity"],
        "contagious": bool(row["contagious"]),
        "icd10": row["icd10"],
        "when_to_see_doctor": row["when_to_see_doctor"],
        "medications": meds,
        "precautions": precs,
        "diets": diets,
        "workouts": works,
        "followup_questions": fqs
    }

import random
import string

def generate_unique_patient_code(conn=None):
    close_conn = False
    if conn is None:
        conn = get_db()
        close_conn = True
    chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    for _ in range(100):
        code = f"HB-{''.join(random.choices(chars, k=5))}"
        row = conn.execute("SELECT id FROM patients WHERE patient_code=?", (code,)).fetchone()
        if not row:
            if close_conn:
                conn.close()
            return code
    # Timestamp fallback to guarantee mathematical uniqueness
    ts_part = hex(int(datetime.datetime.now().timestamp() * 1000))[2:].upper()[-5:]
    code = f"HB-{ts_part}"
    if close_conn:
        conn.close()
    return code

def init_db_schema():
    conn = get_db()
    try:
        conn.execute("ALTER TABLE patients ADD COLUMN patient_code TEXT")
    except Exception:
        pass
    try:
        conn.execute("ALTER TABLE health_history ADD COLUMN patient_code TEXT")
    except Exception:
        pass
    try:
        conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_patients_code ON patients(patient_code)")
    except Exception:
        pass
    conn.commit()
    conn.close()

init_db_schema()

def get_age_group(age):
    if age is None or age == 0:
        return "Adult"
    try:
        age_int = int(age)
        if age_int < 12:
            return "Child"
        elif age_int <= 18:
            return "Teen"
        elif age_int >= 60:
            return "Senior"
        else:
            return "Adult"
    except (ValueError, TypeError):
        return "Adult"

def get_personalized_disease_info(base_info, profile):
    """
    Tailor disease medications, diets, workouts, followup questions, and risk notes
    based on patient profile (Name, Age, Gender, Patient ID).
    """
    name = (profile.get("name") or "").strip() or "Patient"
    age = profile.get("age")
    gender = profile.get("gender") or "Not specified"
    age_group = get_age_group(age)
    patient_id = profile.get("patient_id") or profile.get("patient_code")
    if not patient_id or patient_id == "HB-00000":
        patient_id = generate_unique_patient_code()

    info = dict(base_info)
    info["patient_id"] = patient_id
    info["patient_name"] = name
    info["age_group"] = age_group
    info["gender"] = gender

    # 1. Personalized risk notes based on Age and Gender
    risk_notes = []
    if age_group == "Child":
        risk_notes.append(f"👶 **Pediatric Risk Profile for {name}:** Children (<12 yrs) can develop rapid temperature changes and heightened vulnerability to respiratory complications. Close monitoring of fluid intake, alertness, and breathing rate is essential.")
    elif age_group == "Teen":
        risk_notes.append(f"🧑 **Adolescent Profile for {name}:** Ensure ample restorative rest, balanced electrolyte replenishment, and monitor for school/sports fatigue.")
    elif age_group == "Senior":
        risk_notes.append(f"👴 **Senior Clinical Risk for {name}:** Patients aged 60+ have higher susceptibility to secondary complications, cardiac/respiratory strain, and slower healing. Monitoring SpO2, blood pressure, and hydration is strongly advised.")

    if gender == "Male":
        if base_info.get("body_system") in ("cardiovascular", "endocrine"):
            risk_notes.append("❤️ **Cardiovascular / Metabolic Risk:** Males exhibit higher statistical prevalence of acute cardiac and hypertensive events; avoid heavy physical exertion.")
    elif gender == "Female":
        if base_info.get("body_system") in ("neurological", "endocrine", "urinary"):
            risk_notes.append("👩 **Endocrine / Neurological Factors:** Hormonal fluctuations and physiological variations may influence symptom intensity. Ensure iron and micronutrient balance.")

    info["personalized_risk_notes"] = risk_notes

    # 2. Tailored Follow-up Questions based on Age and Gender
    custom_followups = list(base_info.get("followup_questions", []))
    if age_group == "Child":
        custom_followups.insert(0, f"Is {name} drinking sufficient fluids, alert, and active?")
        custom_followups.insert(1, "Has the fever or symptom persisted continuously for more than 24 hours?")
    elif age_group == "Senior":
        custom_followups.insert(0, "Do you have any existing hypertension, diabetes, or heart conditions?")
        custom_followups.insert(1, "Are you currently taking any prescription medications that might interact?")
    elif gender == "Female":
        custom_followups.append("Are these symptoms correlated with recent hormonal or menstrual changes?")
    elif gender == "Male":
        custom_followups.append("Do you have any prior history of high blood pressure or cardiac strain?")

    info["followup_questions"] = custom_followups[:4]

    # 3. Tailor Medications & Dosages for Age Group
    base_meds = list(base_info.get("medications", []))
    tailored_meds = []
    if age_group == "Child":
        tailored_meds.append(f"⚠️ **Pediatric Dosage Note for {name}:** All medication dosages must be strictly weight-adjusted by a licensed pediatrician (e.g. Paracetamol 10–15 mg/kg suspension). Standard adult tablets should not be administered.")
        for m in base_meds:
            clean_m = re.sub(r'\b\d+mg\b', 'Pediatric Syrup (doctor prescribed)', m, flags=re.IGNORECASE)
            tailored_meds.append(clean_m)
    elif age_group == "Senior":
        tailored_meds.append(f"⚠️ **Senior Dosage Advisory for {name}:** Begin at the lowest effective dose under physician guidance. Check for polypharmacy interactions and renal/hepatic safety.")
        for m in base_meds:
            tailored_meds.append(f"{m} (standard senior supervision)")
    else:
        tailored_meds = base_meds

    info["medications"] = tailored_meds

    # 4. Tailor Diet Recommendations for Age Group
    base_diets = list(base_info.get("diets", []))
    if age_group == "Child":
        tailored_diets = [
            "Oral rehydration solution (ORS) & diluted natural fruit juices",
            "Warm chicken or vegetable broth",
            "Mashed soft fruits (bananas, stewed apples)",
            "Warm turmeric milk (if tolerated)",
            "Soft easily digestible porridge (khichdi, oats)"
        ]
    elif age_group == "Senior":
        tailored_diets = [
            "Low-sodium warm vegetable and lentil soups",
            "High-fiber steamed vegetables and whole grains",
            "Calcium & Vitamin D enriched yogurt or fortified milk",
            "Warm herbal teas (ginger, chamomile) for soothing",
            "Hydration reminder: Drink small sips of water every hour"
        ]
    else:
        tailored_diets = base_diets

    info["diets"] = tailored_diets

    # 5. Tailor Workout / Lifestyle for Age Group
    base_workouts = list(base_info.get("workouts", []))
    if age_group == "Child":
        tailored_workouts = [
            "Complete bed rest and quiet indoor activities",
            "Avoid strenuous running or outdoor exertion until fully recovered",
            "Ensure 10–12 hours of restorative sleep"
        ]
    elif age_group == "Senior":
        tailored_workouts = [
            "Rest as primary recovery strategy",
            "Gentle seated breathing exercises (deep diaphragmatic breathing)",
            "Short, slow assisted indoor walking to maintain circulation",
            "Avoid sudden standing to prevent postural hypotension"
        ]
    else:
        tailored_workouts = base_workouts

    info["workouts"] = tailored_workouts

    return info

def save_health_history(patient_id, symptoms, disease, confidence, age, gender, duration, notes="", patient_code=None):
    conn = get_db()
    conn.execute("""
        INSERT INTO health_history (patient_id, symptoms, predicted_disease, confidence, age, gender, duration, notes, patient_code)
        VALUES (?,?,?,?,?,?,?,?,?)
    """, (patient_id, json.dumps(symptoms), disease, confidence, age, gender, duration, notes, patient_code))
    conn.commit()
    conn.close()

def get_or_create_patient(name, age, gender, patient_code=None):
    conn = get_db()
    if patient_code and patient_code != "HB-00000":
        row = conn.execute("SELECT id, patient_code FROM patients WHERE patient_code=?", (patient_code,)).fetchone()
        if row:
            conn.execute("UPDATE patients SET name=?, age=?, gender=? WHERE id=?", (name, age, gender, row["id"]))
            conn.commit()
            conn.close()
            return row["id"]
    if not patient_code or patient_code == "HB-00000":
        patient_code = generate_unique_patient_code(conn)
    cur = conn.execute("INSERT INTO patients (name, age, gender, patient_code) VALUES (?,?,?,?)", (name, age, gender, patient_code))
    pid = cur.lastrowid
    conn.commit()
    conn.close()
    return pid

# ─────────────────────────────────────────────
# SYMPTOM EXTRACTION — NLP
# ─────────────────────────────────────────────
SYMPTOM_ALIASES = {
    "fever": ["high_fever", "mild_fever"],
    "high fever": ["high_fever"],
    "mild fever": ["mild_fever"],
    "temperature": ["high_fever", "mild_fever"],
    "cough": ["cough", "dry_cough"],
    "dry cough": ["dry_cough"],
    "cold": ["runny_nose", "continuous_sneezing"],
    "headache": ["headache"],
    "head pain": ["headache"],
    "nausea": ["nausea"],
    "vomit": ["vomiting"],
    "vomiting": ["vomiting"],
    "diarrhea": ["diarrhoea"],
    "diarrhoea": ["diarrhoea"],
    "loose stools": ["diarrhoea"],
    "stomach pain": ["stomach_pain", "abdominal_pain"],
    "abdominal pain": ["abdominal_pain"],
    "belly pain": ["belly_pain"],
    "chest pain": ["chest_pain"],
    "chest tightness": ["chest_pain", "breathlessness"],
    "shortness of breath": ["breathlessness", "shortness_of_breath"],
    "breathlessness": ["breathlessness"],
    "difficulty breathing": ["breathlessness", "shortness_of_breath"],
    "fatigue": ["fatigue"],
    "tired": ["fatigue", "lethargy"],
    "exhausted": ["fatigue", "lethargy"],
    "weakness": ["fatigue", "weakness_in_limbs"],
    "itching": ["itching"],
    "itch": ["itching"],
    "rash": ["skin_rash"],
    "skin rash": ["skin_rash"],
    "joint pain": ["joint_pain"],
    "joint ache": ["joint_pain", "swelling_joints"],
    "back pain": ["back_pain"],
    "neck pain": ["neck_pain"],
    "dizziness": ["dizziness"],
    "dizzy": ["dizziness"],
    "anxiety": ["anxiety"],
    "panic": ["panic_attacks", "anxiety"],
    "depression": ["depression"],
    "sad": ["depression"],
    "wheezing": ["wheezing"],
    "sneezing": ["continuous_sneezing"],
    "runny nose": ["runny_nose"],
    "stuffy nose": ["congestion"],
    "congestion": ["congestion"],
    "sinus pressure": ["sinus_pressure"],
    "ear pain": ["ear_pain"],
    "hearing loss": ["hearing_loss"],
    "eye redness": ["redness_of_eyes", "eye_redness"],
    "blurred vision": ["blurred_and_distorted_vision"],
    "burning urination": ["burning_micturition"],
    "frequent urination": ["continuous_feel_of_urine", "polyuria"],
    "constipation": ["constipation"],
    "bloating": ["passage_of_gases"],
    "swelling": ["swelling_joints", "swollen_legs"],
    "weight loss": ["weight_loss"],
    "weight gain": ["weight_gain"],
    "loss of appetite": ["loss_of_appetite"],
    "no appetite": ["loss_of_appetite"],
    "muscle pain": ["muscle_pain"],
    "muscle ache": ["muscle_pain"],
    "body ache": ["muscle_pain", "joint_pain"],
    "numbness": ["numbness"],
    "tingling": ["tingling"],
    "palpitations": ["palpitations"],
    "heart racing": ["fast_heart_rate", "palpitations"],
    "rapid heartbeat": ["fast_heart_rate"],
    "sweating": ["sweating"],
    "night sweats": ["sweating"],
    "chills": ["chills"],
    "shivering": ["shivering"],
    "jaundice": ["yellowish_skin", "yellowing_of_eyes"],
    "yellow skin": ["yellowish_skin"],
    "yellow eyes": ["yellowing_of_eyes"],
    "dark urine": ["dark_urine"],
    "blood in stool": ["bloody_stool"],
    "irregular periods": ["abnormal_menstruation"],
    "menstrual cramps": ["cramps"],
    "sore throat": ["throat_irritation", "patches_in_throat"],
    "throat pain": ["throat_irritation"],
    "mood swings": ["mood_swings"],
    "irritability": ["irritability"],
    "confusion": ["altered_sensorium"],
    "memory loss": ["lack_of_concentration"],
    "concentration": ["lack_of_concentration"],
    "loss of smell": ["loss_of_smell"],
    "no smell": ["loss_of_smell"],
    "acidity": ["acidity"],
    "heartburn": ["acidity", "indigestion"],
    "indigestion": ["indigestion"],
    "dehydration": ["dehydration"],
    "thirst": ["dehydration"],
    "bruising": ["bruising"],
    "pimples": ["pus_filled_pimples"],
    "acne": ["pus_filled_pimples", "blackheads"],
}

def extract_symptoms(text):
    text_l = text.lower()
    found = set()
    for sym in ALL_SYMPTOMS:
        readable = sym.replace("_", " ")
        if readable in text_l:
            found.add(sym)
    for alias, syms in SYMPTOM_ALIASES.items():
        if alias in text_l:
            for s in syms:
                if s in ALL_SYMPTOMS:
                    found.add(s)
    return list(found)

# ─────────────────────────────────────────────
# ML PREDICTION
# ─────────────────────────────────────────────
def predict_diseases(active_symptoms, top_n=3):
    vec = pd.DataFrame(
        [[1 if s in active_symptoms else 0 for s in ALL_SYMPTOMS]],
        columns=ALL_SYMPTOMS
    )
    proba = clf.predict_proba(vec)[0]
    top_idx = np.argsort(proba)[::-1][:top_n]
    results = []
    for idx in top_idx:
        disease = le.inverse_transform([idx])[0]
        confidence = float(proba[idx])
        if confidence > 0.03:
            body_system = DISEASE_DB.get(disease, {}).get("body_system", "general")
            severity = DISEASE_DB.get(disease, {}).get("severity", "")
            results.append({
                "disease": disease,
                "confidence": round(confidence * 100, 1),
                "body_system": body_system,
                "severity": severity
            })
    return results

# ─────────────────────────────────────────────
# EMERGENCY DETECTION
# ─────────────────────────────────────────────
EMERGENCY_PHRASES = [
    "heart attack","stroke","can't breathe","cannot breathe",
    "unconscious","severe bleeding","suicidal","kill myself",
    "overdose","poisoning","seizure","anaphylaxis","emergency",
    "ambulance","dying","collapsed","passed out","not breathing",
    "unresponsive","heavy bleeding","choking"
]

def is_emergency(text):
    t = text.lower()
    return any(p in t for p in EMERGENCY_PHRASES)

# ─────────────────────────────────────────────
# ─────────────────────────────────────────────
# CONVERSATION LOGIC
# ─────────────────────────────────────────────
GREETING_WORDS = ["hello","hi","hey","good morning","good evening","good afternoon","howdy","namaste"]
THANKS_WORDS   = ["thank","thanks","thank you","ty","thx"]
BYE_WORDS      = ["bye","goodbye","exit","quit","see you","ciao","take care"]

def chat_response(user_msg, sd):
    msg_l = user_msg.lower().strip()
    profile = sd.get("profile", {})
    if not profile.get("patient_id") or profile.get("patient_id") == "HB-00000":
        profile["patient_id"] = profile.get("patient_code") or generate_unique_patient_code()
    patient_id = profile["patient_id"]
    name = (profile.get("name") or "").strip()

    # 1. Handle profile injection string format:
    # "Patient profile saved — Name: {name}, Age: {age}, Gender: {gender}"
    prof_saved_match = re.search(r'patient profile saved\s*[—\-:]+\s*name:\s*(.*?),\s*age:\s*(\d+),\s*gender:\s*(.*)', user_msg, re.IGNORECASE)
    if prof_saved_match:
        name = prof_saved_match.group(1).strip()
        try:
            age = int(prof_saved_match.group(2).strip())
        except ValueError:
            age = None
        gender = prof_saved_match.group(3).strip()

        profile["name"] = name
        profile["age"] = age
        profile["gender"] = gender
        profile["patient_id"] = patient_id
        sd["profile"] = profile
        sd["state"] = "awaiting_symptoms"

        # Save to DB
        pid = get_or_create_patient(name or "Anonymous", age or 0, gender or "Unknown", patient_id)
        sd["patient_db_id"] = pid

        age_grp = get_age_group(age)
        return {
            "type": "text",
            "message": (
                f"✅ **Patient Profile Registered**\n\n"
                f"• **Name:** {name}\n"
                f"• **Age:** {age} years ({age_grp})\n"
                f"• **Gender:** {gender}\n"
                f"• **Patient ID:** `{patient_id}`\n\n"
                f"Hello **{name}**! Your profile is active and all subsequent disease predictions, risk factors, medication dosages, and diet guidelines will be tailored to your age group and profile.\n\n"
                f"Please describe what symptoms you are experiencing to begin your assessment."
            ),
            "session": sd
        }

    # Emergency check
    if is_emergency(user_msg):
        sd["state"] = "idle"
        name_alert = f" — {name.upper()}" if name else ""
        dear_name = f"{name}, please" if name else "Please"
        return {
            "type": "emergency",
            "message": (
                f"🚨 **EMERGENCY DETECTED{name_alert}** 🚨\n\n"
                f"{dear_name} call emergency services IMMEDIATELY!\n\n"
                f"• 🇮🇳 India: **112** | **108** (Ambulance)\n"
                f"• 🇺🇸 USA / Canada: **911**\n"
                f"• 🇬🇧 UK: **999**\n"
                f"• 🇦🇺 Australia: **000**\n"
                f"• 🌍 WHO: +41 22 791 2111\n\n"
                f"**Do not wait — seek immediate medical help!**"
            ),
            "session": sd
        }

    # Greetings
    if any(g in msg_l for g in GREETING_WORDS) and len(msg_l) < 30:
        sd["state"] = "awaiting_symptoms"
        if name:
            return {
                "type": "text",
                "message": (
                    f"👋 Hello **{name}** (Patient ID: `{patient_id}`)!\n\n"
                    f"I am your HealthBot AI assistant. How are you feeling today?\n\n"
                    f"Describe your symptoms in detail to receive an assessment personalized for your age ({profile.get('age','N/A')}) and gender ({profile.get('gender','N/A')})."
                ),
                "session": sd
            }
        else:
            return {
                "type": "profile_request",
                "message": (
                    f"👋 Welcome to **HealthBot AI**!\n\n"
                    f"For personalized analysis, please save your **Name**, **Age**, and **Gender** in the sidebar profile panel.\n\n"
                    f"_Example: 'I am 28 years old, female, symptoms for 3 days'_\n\n"
                    f"Or describe your symptoms directly if you prefer."
                ),
                "session": sd
            }

    # Thanks
    if any(t in msg_l for t in THANKS_WORDS):
        addr = f", **{name}**" if name else ""
        return {"type": "text", "message": f"You're very welcome{addr}! 😊 Stay healthy and consult a doctor for proper diagnosis.", "session": sd}

    # Farewell
    if any(b in msg_l for b in BYE_WORDS):
        sd["state"] = "idle"
        addr = f", **{name}**" if name else ""
        return {"type": "text", "message": f"Take care{addr}! 👋 Your health session has been recorded under Patient ID `{patient_id}`. Stay well!", "session": sd}

    # Extract patient profile updates if mentioned in free text
    age_match = re.search(r'\b(\d{1,3})\s*(?:years?|yr|yrs|y\.?o\.?|age)\b', msg_l)
    if not age_match:
        age_match = re.search(r'\bage[d]?\s*(\d{1,3})\b', msg_l)
    if age_match:
        profile["age"] = int(age_match.group(1))

    gender_match = re.search(r'\b(male|female|man|woman|boy|girl)\b', msg_l)
    if gender_match:
        g = gender_match.group(1).lower()
        profile["gender"] = "Male" if g in ("male","man","boy") else "Female"

    dur_match = re.search(r'(\d+)\s*(day|days|week|weeks|month|months|hour|hours)', msg_l)
    if dur_match:
        profile["duration"] = f"{dur_match.group(1)} {dur_match.group(2)}"
    sd["profile"] = profile

    extracted = extract_symptoms(user_msg)
    active = list(set(sd.get("active_symptoms", []) + extracted))
    sd["active_symptoms"] = active

    if not active:
        sd["state"] = "awaiting_symptoms"
        greeting = f"Hello **{name}**, " if name else ""
        return {
            "type": "text",
            "message": (
                f"{greeting}I couldn't detect specific symptoms in your message. Please describe what you are experiencing.\n\n"
                f"*Example: 'I have fever, headache, and body aches for 2 days'*"
            ),
            "session": sd
        }

    predictions = predict_diseases(active, top_n=3)

    if not predictions:
        greeting = f"**{name}**, " if name else ""
        return {
            "type": "text",
            "message": f"{greeting}I need a few more symptom details. Could you describe more of what you're experiencing?",
            "session": sd
        }

    top_disease = predictions[0]["disease"]
    top_system  = predictions[0]["body_system"]
    top_conf    = predictions[0]["confidence"]

    # Retrieve base disease info and personalize it for patient age, gender, and name
    base_info = get_disease_info(top_disease)
    personalized_info = get_personalized_disease_info(base_info, profile)

    # Save to health history
    pid = get_or_create_patient(
        profile.get("name", "Anonymous"),
        profile.get("age", 0),
        profile.get("gender", "Unknown"),
        patient_id
    )
    save_health_history(
        pid, active, top_disease, top_conf,
        profile.get("age", 0),
        profile.get("gender", "Unknown"),
        profile.get("duration", "Unknown"),
        notes=f"Personalized for {name or 'Anonymous'} (ID: {patient_id})",
        patient_code=patient_id
    )
    sd["patient_db_id"] = pid
    sd["patient_id"] = patient_id

    symptom_labels = [s.replace("_", " ") for s in active]
    sd["state"] = "result_shown"
    sd["last_disease"] = top_disease
    sd["last_predictions"] = predictions

    return {
        "type": "prediction",
        "patient_id": patient_id,
        "patient_name": name,
        "detected_symptoms": symptom_labels,
        "predictions": predictions,
        "primary_info": personalized_info,
        "profile": profile,
        "body_system": top_system,
        "session": sd
    }

# ─────────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json or {}
    user_msg = data.get("message", "").strip()
    sd = data.get("session_data", {"state": "idle", "active_symptoms": [], "profile": {}})
    if not user_msg:
        return jsonify({"error": "Empty message"}), 400
    response = chat_response(user_msg, sd)
    return jsonify(response)

@app.route("/profile", methods=["POST"])
def update_profile():
    data = request.json or {}
    name = (data.get("name") or "").strip()
    age = data.get("age")
    gender = (data.get("gender") or "").strip()
    patient_id = data.get("patient_id")
    if not patient_id or patient_id == "HB-00000":
        patient_id = generate_unique_patient_code()

    try:
        age_val = int(age) if age is not None and str(age).strip() else None
    except (ValueError, TypeError):
        age_val = None

    profile = {
        "name": name,
        "age": age_val,
        "gender": gender,
        "patient_id": patient_id
    }

    pid = get_or_create_patient(name or "Anonymous", age_val or 0, gender or "Unknown", patient_id)
    context_msg = f"Patient profile saved — Name: {name or 'Anonymous'}, Age: {age_val or 'N/A'}, Gender: {gender or 'Not specified'}"

    return jsonify({
        "status": "success",
        "profile": profile,
        "patient_id": patient_id,
        "patient_db_id": pid,
        "context_message": context_msg
    })

@app.route("/symptoms", methods=["GET"])
def get_symptoms():
    return jsonify(sorted([s.replace("_", " ") for s in ALL_SYMPTOMS]))

@app.route("/diseases", methods=["GET"])
def get_diseases():
    conn = get_db()
    rows = conn.execute("SELECT name, body_system, severity, icd10 FROM diseases ORDER BY name").fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route("/disease/<name>", methods=["GET", "POST"])
def disease_detail(name):
    base_info = get_disease_info(name)
    age = request.args.get("age")
    gender = request.args.get("gender", "")
    pname = request.args.get("name", "")
    patient_id = request.args.get("patient_id", "")
    profile = {
        "name": pname,
        "age": int(age) if age and age.isdigit() else None,
        "gender": gender,
        "patient_id": patient_id
    }
    personalized = get_personalized_disease_info(base_info, profile)
    return jsonify(personalized)

@app.route("/history", methods=["GET"])
def health_history():
    conn = get_db()
    rows = conn.execute("""
        SELECT h.*, p.name as patient_name, COALESCE(h.patient_code, p.patient_code, 'HB-00000') as patient_id_code
        FROM health_history h
        LEFT JOIN patients p ON h.patient_id = p.id
        ORDER BY h.session_date DESC LIMIT 50
    """).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route("/history/<int:patient_id>", methods=["GET"])
def patient_history(patient_id):
    conn = get_db()
    rows = conn.execute("""
        SELECT * FROM health_history
        WHERE patient_id=? ORDER BY session_date DESC
    """, (patient_id,)).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route("/patients", methods=["GET"])
def list_patients():
    conn = get_db()
    rows = conn.execute("SELECT * FROM patients ORDER BY created_at DESC").fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route("/report/<disease_name>", methods=["GET"])
def get_report_data(disease_name):
    base_info = get_disease_info(disease_name)
    age = request.args.get("age")
    gender = request.args.get("gender", "")
    pname = request.args.get("name", "")
    patient_id = request.args.get("patient_id", "")
    profile = {
        "name": pname,
        "age": int(age) if age and age.isdigit() else None,
        "gender": gender,
        "patient_id": patient_id
    }
    info = get_personalized_disease_info(base_info, profile)
    info["generated_at"] = datetime.datetime.now().strftime("%d %B %Y, %H:%M")
    return jsonify(info)

@app.route("/stats", methods=["GET"])
def get_stats():
    conn = get_db()
    total_sessions = conn.execute("SELECT COUNT(*) FROM health_history").fetchone()[0]
    top_diseases = conn.execute("""
        SELECT predicted_disease, COUNT(*) as cnt
        FROM health_history GROUP BY predicted_disease
        ORDER BY cnt DESC LIMIT 5
    """).fetchall()
    total_patients = conn.execute("SELECT COUNT(*) FROM patients").fetchone()[0]
    conn.close()
    return jsonify({
        "total_sessions": total_sessions,
        "total_patients": total_patients,
        "top_diseases": [dict(r) for r in top_diseases]
    })

@app.route("/clear", methods=["POST"])
def clear_session():
    return jsonify({"status": "cleared", "session_data": {
        "state": "idle", "active_symptoms": [], "profile": {}
    }})

if __name__ == "__main__":
    print("="*55)
    print("  HealthBot AI — Open Source Healthcare Chatbot")
    print("  🌐 http://127.0.0.1:5000")
    print("  📚 Powered by Random Forest ML + SQLite")
    print("="*55)
    app.run(debug=False, host="0.0.0.0", port=5000)
