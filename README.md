# ⚕️ HealthBot AI — Intelligent Healthcare Assistant & Clinical Classifier

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.3+-green.svg)](https://flask.palletsprojects.com)
[![scikit-learn](https://img.shields.io/badge/ML-Random%20Forest%20(500%20Trees)-orange.svg)](https://scikit-learn.org)
[![UI](https://img.shields.io/badge/UI-Ultra%20Glassmorphism-9cf.svg)](https://developer.mozilla.org/en-US/docs/Web/CSS/backdrop-filter)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **HealthBot AI** is an open-source, AI-powered healthcare assistant and clinical disease classifier. Featuring a state-of-the-art **Ultra-Glassmorphism UI**, real-time **voice symptom recognition**, **demographic personalization** (age/gender tailored risk, dosages, and diets), and **interactive circular confidence rings**.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🪟 **Ultra-Glassmorphism UI** | Multi-layered frosted glass panels, ambient floating luminous mesh glows, and specular highlights in Dark and Light themes. |
| 🆔 **Unique Patient ID (`HB-XXXXX`)** | Cryptographically verified, collision-proof patient IDs assigned and persisted in SQLite for medical record-keeping. |
| 👤 **Patient Profile Engine** | Dynamic initials avatar, inline profile editor, and session context injection for personalized clinical assessment. |
| 🧬 **Personalized Clinical Engine** | Demographic-tailored medical advice: pediatric vs. senior risk warnings, weight-adjusted dosages, and age-specific nutrition plans. |
| 🎙️ **Interactive Voice Input** | Web Speech API integration with live streaming transcription, sound wave equalizer animations, and mic permission handling. |
| 🤖 **Random Forest Classifier** | 500-tree ensemble ML model trained across 132 symptom features and 30+ disease categories with noise augmentation. |
| 📊 **Confidence Rings** | Animated SVG circular meters displaying ranked probability distributions for top disease matches. |
| 🫁 **Body System Filtering** | Categorized symptoms: Respiratory, Cardiovascular, Digestive, Neurological, Musculoskeletal, Dermatology, and Urology. |
| 🖨️ **Printable Medical Reports** | One-click clinical report export formatted for patient consultations and physician reviews. |
| 📜 **SQLite Health History** | Full diagnostic audit trail with searchable consultation logs and symptom recurrence tracking. |

---

## 🚀 Quick Start Guide

### 1. Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/healthcare-chatbot.git
cd healthcare-chatbot
```

### 2. Set Up a Virtual Environment (Optional but Recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Train the ML Model & Build the Database
```bash
python train_model.py
```
> *Generates `models/disease_model.pkl`, feature datasets, and initializes the SQLite schema with diseases and remedies.*

### 5. Launch the Application
```bash
python app.py
```

### 6. Open in Your Browser
Navigate to: **[http://127.0.0.1:5000](http://127.0.0.1:5000)**

---

## 🌐 Running Online (Public Tunneling)

To share the chatbot online or access it from mobile devices:

### Option A: Cloudflare Quick Tunnel (Free & Instant HTTPS)
```bash
# Download cloudflared from https://github.com/cloudflare/cloudflared/releases
.\cloudflared.exe tunnel --url http://127.0.0.1:5000
```

### Option B: SSH Reverse Tunnel (Zero-Installation)
```bash
ssh -R 80:localhost:5000 nokey@localhost.run
```

---

## 📁 Project Structure

```
healthcare-chatbot/
├── app.py                    # Flask application, NLP engine, API routes & personalization
├── train_model.py            # Random Forest ML training pipeline & SQLite database generator
├── requirements.txt          # Python dependencies
├── README.md                 # Project documentation
├── LICENSE                   # MIT License
├── .gitignore                # Git ignore configuration
├── .env.example              # Example environment configuration
├── models/
│   ├── disease_db.json       # Structured medical knowledge base (diets, meds, precautions)
│   ├── symptoms.json         # 132 standardized symptom definitions
│   └── feature_importance.json # Model feature weights
├── templates/
│   └── index.html            # Main web application layout
└── static/
    ├── css/
    │   └── style.css         # Ultra-Glassmorphism design tokens & animations
    └── js/
        └── app.js            # Voice input, confidence rings, profile & chat logic
```

---

## 🗄️ Database Architecture

```sql
-- Patients table with unique patient code constraint
CREATE TABLE patients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    age INTEGER,
    gender TEXT,
    patient_code TEXT UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Complete health & diagnosis audit history
CREATE TABLE health_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER,
    patient_code TEXT,
    session_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    symptoms TEXT,            -- JSON array of detected symptoms
    predicted_disease TEXT,
    confidence REAL,
    age INTEGER,
    gender TEXT,
    duration TEXT,
    notes TEXT,
    FOREIGN KEY(patient_id) REFERENCES patients(id)
);
```
---

## 🤖 Machine Learning Model Architecture

- **Algorithm**: Random Forest Ensemble (`sklearn.ensemble.RandomForestClassifier`)
- **Estimators**: 500 decision trees (`n_estimators=500, max_features="sqrt"`)
- **Features**: 132 binary encoded clinical symptoms
- **Classes**: 30+ acute, chronic, infectious, and metabolic conditions
- **Augmentation**: Synthetic permutation with noise injection to handle multi-symptom overlaps

---

## ⚠️ Medical Disclaimer

> **HealthBot AI** is built strictly for **informational and educational purposes**. It does **not** provide formal medical diagnoses, clinical prescriptions, or replace direct consultation with a qualified medical professional. In case of an acute emergency, please contact your local emergency services (e.g., 911 / 112 / 108) immediately.

---

## 📄 License

Distributed under the **MIT License**. Free for academic, personal, and open-source use. See `LICENSE` for details.
