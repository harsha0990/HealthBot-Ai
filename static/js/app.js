/* ═══════════════════════════════════════════════
   HealthBot AI — Frontend Logic (Personalized)
   Patient Profile System · Initials Avatar · HB-XXXXX ID
   Dark/Light Mode · Confidence Rings · Clinical Print Report
   Body System Tabs · Voice Input · Interactive Modals
   ═══════════════════════════════════════════════ */
"use strict";

// ─── STATE ──────────────────────────────────────
let sessionData = {
  state: "idle",
  active_symptoms: [],
  profile: {
    name: "",
    age: null,
    gender: "",
    patient_id: ""
  }
};

// ─── PATIENT ID & INITIALS HELPERS ─────────────
function generatePatientId() {
  const chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ";
  let id = "";
  for (let i = 0; i < 5; i++) {
    id += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return "HB-" + id;
}

function getInitials(name) {
  if (!name || !name.trim()) return "?";
  const parts = name.trim().split(/\s+/).filter(Boolean);
  if (parts.length === 1) {
    return parts[0].substring(0, 2).toUpperCase();
  }
  return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
}

// ─── DOM ELEMENTS ──────────────────────────────
const chatWindow       = document.getElementById("chatWindow");
const welcomeCard      = document.getElementById("welcomeCard");
const typingBar        = document.getElementById("typingBar");
const userInput        = document.getElementById("userInput");
const sendBtn          = document.getElementById("sendBtn");
const charCount        = document.getElementById("charCount");
const voiceBtn         = document.getElementById("voiceBtn");

const themeToggle      = document.getElementById("themeToggle");
const historyBtn       = document.getElementById("historyBtn");
const clearBtn         = document.getElementById("clearBtn");
const menuBtn          = document.getElementById("menuBtn");
const sidebar          = document.getElementById("sidebar");
const sidebarClose     = document.getElementById("sidebarClose");

const modalOverlay     = document.getElementById("modalOverlay");
const modalContent     = document.getElementById("modalContent");
const modalClose       = document.getElementById("modalClose");

const historyPanel     = document.getElementById("historyPanel");
const historyPanelBody = document.getElementById("historyPanelBody");
const historyClose     = document.getElementById("historyClose");
const historyList      = document.getElementById("historyList");

const saveProfile      = document.getElementById("saveProfile");
const profileFields    = document.getElementById("profileFields");
const profileNameInput = document.getElementById("profileNameInput");
const profileAge       = document.getElementById("profileAge");
const profileGender    = document.getElementById("profileGender");
const profileAvatar    = document.getElementById("profileAvatar");
const profileName      = document.getElementById("profileName");
const profileMeta      = document.getElementById("profileMeta");
const patientIdBadge   = document.getElementById("patientIdBadge");
const editNameBtn      = document.getElementById("editNameBtn");

const sysTabs          = document.getElementById("sysTabs");
const quickSymptoms    = document.getElementById("quickSymptoms");
const particlesCanvas  = document.getElementById("particles");

// ─── SYSTEM SYMPTOM MAP ─────────────────────────
const SYSTEM_SYMPTOMS = {
  all: [
    { label: "🌡️ Fever", sym: "fever" },
    { label: "🤕 Headache", sym: "headache" },
    { label: "😤 Cough", sym: "cough" },
    { label: "😴 Fatigue", sym: "fatigue" },
    { label: "🤢 Nausea", sym: "nausea" },
    { label: "💔 Chest Pain", sym: "chest pain" },
    { label: "😮‍💨 Breathless", sym: "shortness of breath" },
    { label: "💫 Dizziness", sym: "dizziness" },
    { label: "🦴 Back Pain", sym: "back pain" },
    { label: "🦵 Joint Pain", sym: "joint pain" },
    { label: "🔴 Skin Rash", sym: "skin rash" },
    { label: "😰 Anxiety", sym: "anxiety" },
    { label: "🤒 Stomach Pain", sym: "stomach pain" },
    { label: "😷 Sore Throat", sym: "sore throat" },
    { label: "🤮 Vomiting", sym: "vomiting" },
    { label: "💊 Diarrhea", sym: "diarrhea" }
  ],
  respiratory: [
    { label: "😤 Cough", sym: "cough" },
    { label: "😮‍💨 Shortness of Breath", sym: "shortness of breath" },
    { label: "😷 Sore Throat", sym: "sore throat" },
    { label: "🤧 Runny Nose", sym: "runny nose" },
    { label: "🫁 Phlegm", sym: "phlegm" },
    { label: "🌬️ Wheezing", sym: "wheezing" },
    { label: "👃 Sinus Pressure", sym: "sinus pressure" },
    { label: "🌡️ Fever", sym: "fever" }
  ],
  cardiovascular: [
    { label: "💔 Chest Pain", sym: "chest pain" },
    { label: "💓 Palpitations", sym: "palpitations" },
    { label: "😮‍💨 Shortness of Breath", sym: "shortness of breath" },
    { label: "⚡ Fast Heart Rate", sym: "rapid heartbeat" },
    { label: "💫 Dizziness", sym: "dizziness" },
    { label: "😴 Fatigue", sym: "fatigue" },
    { label: "💦 Sweating", sym: "sweating" }
  ],
  digestive: [
    { label: "🤒 Stomach Pain", sym: "stomach pain" },
    { label: "🤢 Nausea", sym: "nausea" },
    { label: "🤮 Vomiting", sym: "vomiting" },
    { label: "💊 Diarrhea", sym: "diarrhea" },
    { label: "🔥 Acidity / Heartburn", sym: "acidity" },
    { label: "🍽️ Loss of Appetite", sym: "loss of appetite" },
    { label: "🛑 Constipation", sym: "constipation" },
    { label: "💨 Bloating", sym: "bloating" }
  ],
  neurological: [
    { label: "🤕 Headache", sym: "headache" },
    { label: "💫 Dizziness", sym: "dizziness" },
    { label: "👁️ Blurred Vision", sym: "blurred vision" },
    { label: "🌀 Loss of Balance", sym: "loss of balance" },
    { label: "⚡ Numbness / Tingling", sym: "numbness" },
    { label: "🧠 Confusion", sym: "confusion" },
    { label: "🧣 Stiff Neck", sym: "stiff neck" }
  ],
  musculoskeletal: [
    { label: "🦵 Joint Pain", sym: "joint pain" },
    { label: "🦴 Back Pain", sym: "back pain" },
    { label: "💪 Muscle Pain", sym: "muscle pain" },
    { label: "🧣 Neck Pain", sym: "neck pain" },
    { label: "🚶 Painful Walking", sym: "painful walking" },
    { label: "🦵 Knee Pain", sym: "knee pain" },
    { label: "⚡ Muscle Cramps", sym: "cramps" }
  ],
  dermatological: [
    { label: "🔴 Skin Rash", sym: "skin rash" },
    { label: "🖐️ Itching", sym: "itching" },
    { label: "🟡 Yellow Skin", sym: "yellow skin" },
    { label: "🧴 Pus Filled Pimples", sym: "pimples" },
    { label: "🩹 Skin Peeling", sym: "skin peeling" },
    { label: "💧 Blisters", sym: "blister" },
    { label: "🩸 Bruising", sym: "bruising" }
  ],
  urinary: [
    { label: "🔥 Burning Urination", sym: "burning urination" },
    { label: "💧 Frequent Urination", sym: "frequent urination" },
    { label: "🟤 Dark Urine", sym: "dark urine" },
    { label: "⚠️ Bladder Discomfort", sym: "bladder discomfort" }
  ],
  endocrine: [
    { label: "📉 Weight Loss", sym: "weight loss" },
    { label: "📈 Weight Gain", sym: "weight gain" },
    { label: "💧 Excessive Thirst", sym: "thirst" },
    { label: "🍔 Excessive Hunger", sym: "increased appetite" },
    { label: "😴 Chronic Fatigue", sym: "fatigue" },
    { label: "🎭 Mood Swings", sym: "mood swings" }
  ],
  mental_health: [
    { label: "😰 Anxiety", sym: "anxiety" },
    { label: "🌧️ Depression", sym: "depression" },
    { label: "⚡ Panic Attacks", sym: "panic" },
    { label: "🌪️ Restlessness", sym: "restlessness" },
    { label: "😡 Irritability", sym: "irritability" },
    { label: "🧠 Lack of Focus", sym: "lack of concentration" }
  ],
  infectious: [
    { label: "🌡️ High Fever", sym: "high fever" },
    { label: "🥶 Chills & Shivering", sym: "chills" },
    { label: "💦 Sweating", sym: "sweating" },
    { label: "😴 Extreme Fatigue", sym: "fatigue" },
    { label: "🤢 Nausea / Vomiting", sym: "nausea" },
    { label: "🔴 Red Spots / Rash", sym: "red spots" }
  ]
};

// ─── HELPERS ───────────────────────────────────
function esc(str) {
  if (!str) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function mdToHtml(text) {
  if (!text) return "";
  return text
    .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
    .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
    .replace(/\*(.+?)\*/g, "<em>$1</em>")
    .replace(/_(.+?)_/g, "<em>$1</em>")
    .replace(/\n/g, "<br>");
}

function scrollBottom() {
  if (chatWindow) {
    chatWindow.scrollTo({ top: chatWindow.scrollHeight, behavior: "smooth" });
  }
}

function showTyping() {
  if (typingBar) {
    typingBar.style.display = "flex";
    scrollBottom();
  }
}

function hideTyping() {
  if (typingBar) typingBar.style.display = "none";
}

function hideWelcome() {
  if (welcomeCard) welcomeCard.style.display = "none";
}

function appendUserMsg(text) {
  hideWelcome();
  const row = document.createElement("div");
  row.className = "msg-row user";
  row.innerHTML = `
    <div class="msg-avatar">👤</div>
    <div class="msg-bubble">${esc(text)}</div>
  `;
  chatWindow.appendChild(row);
  scrollBottom();
}

function appendBotMsg(html, extraClass = "") {
  hideWelcome();
  const row = document.createElement("div");
  row.className = "msg-row bot";
  row.innerHTML = `
    <div class="msg-avatar" style="background:linear-gradient(135deg,var(--accent),var(--accent2));color:#fff">⚕</div>
    <div class="msg-bubble ${extraClass}">${html}</div>
  `;
  chatWindow.appendChild(row);
  scrollBottom();
}

// ─── PREDICTION CARD RENDERING ──────────────────
function renderPredictionCard(data) {
  hideWelcome();
  const preds = data.predictions || [];
  const syms  = data.detected_symptoms || [];
  const primaryInfo = data.primary_info || {};
  const topDisease = preds.length ? preds[0].disease : (primaryInfo.disease || "Unknown");
  const patientName = data.patient_name || (sessionData.profile && sessionData.profile.name) || "Patient";
  const patientId = data.patient_id || (sessionData.profile && sessionData.profile.patient_id) || "HB-00000";

  const row = document.createElement("div");
  row.className = "msg-row bot prediction-wrap";

  // Build rings HTML
  const circumference = 220; // 2 * PI * 35 approx
  let ringsHtml = "";
  const ringColors = ["r1", "r2", "r3"];

  preds.slice(0, 3).forEach((p, idx) => {
    const colorClass = ringColors[idx] || "r1";
    const rank = idx === 0 ? "🥇 #1" : idx === 1 ? "🥈 #2" : "🥉 #3";
    const dashoffset = circumference - (circumference * (p.confidence || 0) / 100);

    ringsHtml += `
      <div class="confidence-ring-item">
        <div class="ring-wrap">
          <svg class="ring-svg" viewBox="0 0 80 80">
            <circle class="ring-bg" cx="40" cy="40" r="35" />
            <circle class="ring-fill ${colorClass}" cx="40" cy="40" r="35"
                    data-offset="${dashoffset}" style="stroke-dashoffset: ${circumference};" />
          </svg>
          <div class="ring-center">
            <div class="ring-pct">${p.confidence}%</div>
            <div class="ring-rank">${rank}</div>
          </div>
        </div>
        <div class="ring-name">${esc(p.disease)}</div>
        <div class="ring-system">${esc((p.body_system || "").replace("_", " "))}</div>
      </div>
    `;
  });

  const symsHtml = syms.map(s => `<span class="sym-tag">✓ ${esc(s)}</span>`).join("");

  // Risk notes from personalized engine
  const riskNotes = primaryInfo.personalized_risk_notes || [];
  const riskHtml = riskNotes.length ? `
    <div style="padding:12px 20px;background:rgba(251,191,36,0.08);border-bottom:1px solid var(--border);font-size:0.75rem;line-height:1.5;color:var(--text-2)">
      ${riskNotes.map(n => mdToHtml(n)).join("<br>")}
    </div>
  ` : "";

  const payloadStr = JSON.stringify(data).replace(/"/g, '&quot;');
  const primaryInfoStr = JSON.stringify(primaryInfo).replace(/"/g, '&quot;');

  row.innerHTML = `
    <div class="msg-avatar" style="background:linear-gradient(135deg,var(--accent),var(--accent2));color:#fff">⚕</div>
    <div class="prediction-card">
      <div class="pred-hero">
        <div class="pred-hero-icon">🔬</div>
        <div class="pred-hero-text" style="flex:1">
          <div style="display:flex;align-items:center;justify-content:space-between;gap:8px">
            <h3 style="margin:0">Analysis for <strong>${esc(patientName)}</strong></h3>
            <span class="patient-id-badge">${esc(patientId)}</span>
          </div>
          <p style="margin-top:3px">Primary Indication: <strong style="color:var(--accent)">${esc(topDisease)}</strong> · Based on ${syms.length} reported symptoms</p>
        </div>
      </div>

      ${riskHtml}

      ${syms.length ? `
      <div class="pred-symptoms">
        <div style="font-size:0.7rem;font-weight:700;color:var(--text-3);width:100%;margin-bottom:2px">DETECTED SYMPTOMS:</div>
        ${symsHtml}
      </div>
      ` : ""}

      <div class="confidence-section">
        <div class="confidence-label">DISEASE PROBABILITIES</div>
        <div class="confidence-rings">
          ${ringsHtml}
        </div>
      </div>

      <div class="pred-actions">
        <button class="pred-btn pred-btn-primary" onclick="showDiseaseDetail(${primaryInfoStr}, '${esc(topDisease)}')">
          📖 View Full Details & Meds
        </button>
        <button class="pred-btn pred-btn-print" onclick="printReport(${payloadStr})">
          🖨️ Print Health Report
        </button>
      </div>
    </div>
  `;

  chatWindow.appendChild(row);
  scrollBottom();

  // Trigger smooth ring stroke animation
  requestAnimationFrame(() => {
    row.querySelectorAll(".ring-fill").forEach(ring => {
      const targetOffset = ring.getAttribute("data-offset");
      if (targetOffset !== null) {
        ring.style.strokeDashoffset = targetOffset;
      }
    });
  });
}

// ─── MODAL CONTROLS ─────────────────────────────
function openModal(html) {
  if (modalContent && modalOverlay) {
    modalContent.innerHTML = html;
    modalOverlay.style.display = "flex";
  }
}

function closeModal() {
  if (modalOverlay) {
    modalOverlay.style.display = "none";
    if (modalContent) modalContent.innerHTML = "";
  }
}

async function showDiseaseDetail(info, diseaseName) {
  const profile = sessionData.profile || {};
  if (!info && diseaseName) {
    try {
      const params = new URLSearchParams({
        name: profile.name || "",
        age: profile.age || "",
        gender: profile.gender || "",
        patient_id: profile.patient_id || ""
      });
      const res = await fetch(`/disease/${encodeURIComponent(diseaseName)}?${params.toString()}`);
      info = await res.json();
    } catch(e) {
      openModal('<div style="padding:40px;text-align:center;color:var(--danger)">Failed to load disease details.</div>');
      return;
    }
  }
  if (!info) return;

  const severityClass = `badge-severity-${(info.severity || "mild").toLowerCase().replace(/\s+/g, "-")}`;
  const li = arr => (arr && arr.length)
    ? `<ul>${arr.map(a => `<li>${mdToHtml(a)}</li>`).join("")}</ul>`
    : `<p style="color:var(--text-3);font-size:0.8rem">Not specified</p>`;

  const payloadStr = JSON.stringify(info).replace(/"/g, '&quot;');
  const patientId = info.patient_id || profile.patient_id || "HB-00000";
  const patientName = info.patient_name || profile.name || "Patient";

  const riskNotes = info.personalized_risk_notes || [];
  const riskBlock = riskNotes.length ? `
    <div style="margin-top:14px;padding:12px;background:rgba(251,191,36,0.1);border-left:3px solid var(--warning);border-radius:6px;font-size:0.78rem;line-height:1.5">
      ${riskNotes.map(r => mdToHtml(r)).join("<br>")}
    </div>
  ` : "";

  const html = `
    <div class="modal-hero">
      <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:6px">
        <h2>${esc(info.disease || info.name || "Disease Information")}</h2>
        <span class="patient-id-badge">${esc(patientId)}</span>
      </div>
      <div class="modal-hero-meta">
        ${info.severity ? `<span class="meta-badge ${severityClass}">${esc(info.severity.toUpperCase())}</span>` : ""}
        ${info.icd10 ? `<span class="meta-badge" style="background:rgba(56,189,248,.12);border-color:rgba(56,189,248,.3);color:var(--accent)">ICD-10: ${esc(info.icd10)}</span>` : ""}
        ${info.contagious ? `<span class="meta-badge" style="background:rgba(248,113,113,.12);border-color:rgba(248,113,113,.3);color:var(--danger)">⚠️ Contagious</span>` : ""}
        ${info.body_system ? `<span class="meta-badge" style="background:rgba(129,140,248,.12);border-color:rgba(129,140,248,.3);color:var(--accent2)">${esc(info.body_system.replace("_", " "))}</span>` : ""}
      </div>
      <p>${esc(info.description || "No description provided.")}</p>
      ${riskBlock}
    </div>
    <div class="modal-body">
      <div class="info-grid">
        <div class="info-section meds">
          <h4>💊 Medications & Dosages</h4>
          ${li(info.medications)}
        </div>
        <div class="info-section prec">
          <h4>🛡️ Precautions</h4>
          ${li(info.precautions)}
        </div>
        <div class="info-section diet">
          <h4>🥗 Tailored Diet Plan</h4>
          ${li(info.diets)}
        </div>
        <div class="info-section workout">
          <h4>🏃 Lifestyle & Movement</h4>
          ${li(info.workouts)}
        </div>
      </div>
      ${info.followup_questions && info.followup_questions.length ? `
        <div style="margin-top:16px;padding:12px;background:var(--surface);border:1px solid var(--border);border-radius:8px">
          <div style="font-size:0.72rem;font-weight:700;color:var(--text-3);text-transform:uppercase;margin-bottom:8px">❓ Personalized Follow-up Questions</div>
          ${li(info.followup_questions)}
        </div>
      ` : ""}
      ${info.when_to_see_doctor ? `
        <div class="doctor-alert">
          🏥 <strong>When to See a Doctor:</strong><br>${esc(info.when_to_see_doctor)}
        </div>
      ` : ""}
      <div class="doctor-alert" style="margin-top:10px;background:rgba(248,113,113,.06);border-color:rgba(248,113,113,.2)">
        ⚠️ <strong>Medical Disclaimer:</strong> HealthBot AI is for informational and educational purposes only. Always consult a qualified healthcare professional.
      </div>
      <button class="modal-print-btn" onclick="printReportFromModal(${payloadStr})">
        🖨️ Print Full Health Report
      </button>
    </div>
  `;
  openModal(html);
}

// ─── PRINT REPORT ───────────────────────────────
function printReport(data) {
  const info    = data.primary_info || {};
  const profile = data.profile || sessionData.profile || {};
  const preds   = data.predictions || [];
  const syms    = data.detected_symptoms || [];
  const patientId = profile.patient_id || data.patient_id || "HB-00000";
  const patientName = profile.name || data.patient_name || "Anonymous Patient";
  const now     = new Date().toLocaleString();

  const riskNotes = info.personalized_risk_notes || [];

  const html = `
    <div class="print-report" style="font-family:Outfit,sans-serif;padding:40px;max-width:760px;margin:auto;color:#0f1e35">
      <div style="border-bottom:3px solid #2563eb;padding-bottom:20px;margin-bottom:24px;display:flex;justify-content:space-between;align-items:flex-start">
        <div>
          <div style="font-size:28px;font-weight:800;color:#2563eb;margin-bottom:4px">⚕️ HealthBot AI</div>
          <div style="font-size:16px;font-weight:600;color:#0f1e35">Personalized Health Assessment Report</div>
        </div>
        <div style="text-align:right;font-size:12px;color:#64748b">
          <div style="font-weight:700;color:#2563eb;font-size:14px;font-family:monospace">${esc(patientId)}</div>
          <div>${now}</div>
          <div style="color:#64748b">Open Source HealthBot AI</div>
        </div>
      </div>

      <div style="background:#eff6ff;border:1px solid #bfdbfe;border-radius:10px;padding:16px;margin-bottom:20px;display:flex;justify-content:space-between;flex-wrap:wrap;gap:10px">
        <div>
          <div style="font-size:11px;font-weight:700;color:#64748b;text-transform:uppercase;letter-spacing:.08em;margin-bottom:4px">PATIENT NAME</div>
          <div style="font-size:16px;font-weight:700;color:#1e3a8a">${esc(patientName)}</div>
        </div>
        <div>
          <div style="font-size:11px;font-weight:700;color:#64748b;text-transform:uppercase;letter-spacing:.08em;margin-bottom:4px">AGE & GENDER</div>
          <div style="font-size:15px;font-weight:600">${profile.age ? profile.age + " yrs" : "N/A"} · ${profile.gender || "Not specified"}</div>
        </div>
        <div>
          <div style="font-size:11px;font-weight:700;color:#64748b;text-transform:uppercase;letter-spacing:.08em;margin-bottom:4px">RECORD ID</div>
          <div style="font-size:15px;font-weight:700;font-family:monospace;color:#2563eb">${esc(patientId)}</div>
        </div>
      </div>

      ${riskNotes.length ? `
      <div style="background:#fffbeb;border:1px solid #fde68a;border-radius:10px;padding:14px;margin-bottom:20px;font-size:12px;color:#92400e;line-height:1.5">
        <div style="font-weight:700;text-transform:uppercase;letter-spacing:.05em;margin-bottom:4px">CLINICAL RISK PROFILE</div>
        ${riskNotes.map(n => mdToHtml(n)).join("<br>")}
      </div>
      ` : ""}

      ${syms.length ? `
      <div style="background:#f0fdf4;border:1px solid #bbf7d0;border-radius:10px;padding:16px;margin-bottom:20px">
        <div style="font-size:11px;font-weight:700;color:#166534;text-transform:uppercase;letter-spacing:.08em;margin-bottom:10px">REPORTED SYMPTOMS</div>
        <div style="display:flex;flex-wrap:wrap;gap:6px">${syms.map(s => `<span style="background:#dcfce7;border:1px solid #86efac;border-radius:12px;padding:3px 10px;font-size:12px;color:#166534">✓ ${esc(s)}</span>`).join("")}</div>
      </div>
      ` : ""}

      ${preds.length ? `
      <div style="margin-bottom:20px">
        <div style="font-size:11px;font-weight:700;color:#64748b;text-transform:uppercase;letter-spacing:.08em;margin-bottom:12px">DISEASE PROBABILITY ASSESSMENT</div>
        ${preds.map((p, i) => `
          <div style="display:flex;align-items:center;gap:12px;padding:12px;background:${i===0?'#eff6ff':'#f8fafc'};border:1px solid ${i===0?'#bfdbfe':'#e2e8f0'};border-radius:8px;margin-bottom:8px">
            <div style="font-size:1.2rem">${i===0?'🥇':i===1?'🥈':'🥉'}</div>
            <div style="flex:1">
              <div style="font-weight:700;font-size:15px">${esc(p.disease)}</div>
              <div style="font-size:12px;color:#64748b">${(p.body_system||"").replace("_"," ")}</div>
            </div>
            <div style="font-size:20px;font-weight:800;color:${i===0?'#2563eb':'#64748b'}">${p.confidence}%</div>
          </div>
        `).join("")}
      </div>
      ` : ""}

      ${info.disease ? `
      <div style="margin-bottom:20px">
        <div style="font-size:11px;font-weight:700;color:#64748b;text-transform:uppercase;letter-spacing:.08em;margin-bottom:8px">PRIMARY DIAGNOSIS: ${esc(info.disease||"")} ${info.icd10?`(ICD-10: ${info.icd10})`:"" }</div>
        <p style="font-size:13px;color:#475569;line-height:1.6;background:#f8fafc;padding:12px;border-radius:8px">${esc(info.description||"")}</p>
      </div>

      <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:20px">
        <div>
          <div style="font-size:11px;font-weight:700;color:#64748b;text-transform:uppercase;letter-spacing:.08em;margin-bottom:8px">💊 MEDICATIONS & DOSAGES</div>
          ${(info.medications||[]).map(m=>`<div style="padding:5px 10px;margin-bottom:4px;border-left:3px solid #2563eb;background:#eff6ff;font-size:12px">${mdToHtml(m)}</div>`).join("")||"<p style='font-size:12px;color:#94a3b8'>Not available</p>"}
        </div>
        <div>
          <div style="font-size:11px;font-weight:700;color:#64748b;text-transform:uppercase;letter-spacing:.08em;margin-bottom:8px">🛡️ PRECAUTIONS</div>
          ${(info.precautions||[]).map(m=>`<div style="padding:5px 10px;margin-bottom:4px;border-left:3px solid #f59e0b;background:#fffbeb;font-size:12px">${esc(m)}</div>`).join("")||"<p style='font-size:12px;color:#94a3b8'>Not available</p>"}
        </div>
        <div>
          <div style="font-size:11px;font-weight:700;color:#64748b;text-transform:uppercase;letter-spacing:.08em;margin-bottom:8px">🥗 TAILORED DIET PLAN</div>
          ${(info.diets||[]).map(m=>`<div style="padding:5px 10px;margin-bottom:4px;border-left:3px solid #10b981;background:#f0fdf4;font-size:12px">${esc(m)}</div>`).join("")||"<p style='font-size:12px;color:#94a3b8'>Not available</p>"}
        </div>
        <div>
          <div style="font-size:11px;font-weight:700;color:#64748b;text-transform:uppercase;letter-spacing:.08em;margin-bottom:8px">🏃 LIFESTYLE & EXERCISE</div>
          ${(info.workouts||[]).map(m=>`<div style="padding:5px 10px;margin-bottom:4px;border-left:3px solid #818cf8;background:#eef2ff;font-size:12px">${esc(m)}</div>`).join("")||"<p style='font-size:12px;color:#94a3b8'>Not available</p>"}
        </div>
      </div>

      ${info.when_to_see_doctor ? `
      <div style="background:#fffbeb;border:1px solid #fde68a;border-radius:8px;padding:14px;margin-bottom:16px;font-size:12px;color:#92400e;line-height:1.6">
        🏥 <strong>When to See a Doctor:</strong> ${esc(info.when_to_see_doctor)}
      </div>
      ` : ""}
      ` : ""}

      <div style="background:#fef2f2;border:1px solid #fecaca;border-radius:8px;padding:14px;font-size:11px;color:#991b1b;line-height:1.6;margin-top:20px">
        ⚠️ <strong>Medical Disclaimer:</strong> This report is generated by HealthBot AI for informational purposes only. It does not constitute medical advice, diagnosis, or treatment. Always consult a qualified healthcare professional for proper medical evaluation.
      </div>

      <div style="margin-top:20px;padding-top:16px;border-top:1px solid #e2e8f0;text-align:center;font-size:11px;color:#94a3b8">
        Patient Record: ${esc(patientId)} · Generated by HealthBot AI · ${now}
      </div>
    </div>
  `;

  const printEl = document.getElementById("printTemplate");
  if (printEl) {
    printEl.innerHTML = html;
    window.print();
    printEl.innerHTML = "";
  }
}

function printReportFromModal(infoStr) {
  let info;
  try {
    info = typeof infoStr === "string" ? JSON.parse(infoStr) : infoStr;
  } catch(e) {
    return;
  }
  printReport({
    primary_info: info,
    predictions: [{ disease: info.disease || info.name, confidence: 100, body_system: info.body_system }],
    detected_symptoms: [],
    profile: sessionData.profile || {},
    patient_id: info.patient_id || (sessionData.profile && sessionData.profile.patient_id),
    patient_name: info.patient_name || (sessionData.profile && sessionData.profile.name)
  });
}

// ─── SEND CHAT MESSAGE ──────────────────────────
async function sendMessage() {
  if (!userInput) return;
  const text = userInput.value.trim();
  if (!text) return;

  appendUserMsg(text);

  userInput.value = "";
  userInput.style.height = "auto";
  if (charCount) charCount.textContent = "0/600";

  showTyping();
  if (sendBtn) sendBtn.disabled = true;

  try {
    const res = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: text,
        session_data: sessionData
      })
    });

    const data = await res.json();
    hideTyping();
    if (sendBtn) sendBtn.disabled = false;

    if (data.session) {
      sessionData = data.session;
      if (data.session.profile) {
        updateProfileUI(data.session.profile);
      }
    }

    if (data.type === "emergency") {
      appendBotMsg(mdToHtml(data.message), "emergency-msg");
    } else if (data.type === "prediction") {
      renderPredictionCard(data);
      refreshSidebarHistory();
    } else if (data.message) {
      appendBotMsg(mdToHtml(data.message));
    }
  } catch(err) {
    hideTyping();
    if (sendBtn) sendBtn.disabled = false;
    appendBotMsg("⚠️ Unable to connect to server. Please ensure the backend is running.", "emergency-msg");
  }
}

// ─── PROFILE LOGIC ──────────────────────────────
function updateProfileUI(prof, isSaved = false) {
  if (!prof) return;
  if (profileNameInput && prof.name !== undefined) {
    profileNameInput.value = prof.name || "";
  }
  if (profileAge && prof.age) {
    profileAge.value = prof.age;
  }
  if (profileGender && prof.gender) {
    profileGender.value = prof.gender;
  }

  const pid = prof.patient_id || prof.patient_code || sessionData.profile.patient_id || generatePatientId();
  sessionData.profile.patient_id = pid;

  const hasName = Boolean(prof.name && prof.name.trim());
  const displayName = hasName ? prof.name.trim() : "Patient Profile";

  if (profileAvatar) {
    profileAvatar.textContent = getInitials(displayName);
  }

  if (profileName) {
    // Only display the patient name
    profileName.textContent = displayName;
  }

  if (patientIdBadge) {
    patientIdBadge.textContent = `ID: ${pid}`;
    patientIdBadge.style.display = hasName ? "inline-block" : "none";
  }

  if (profileMeta) {
    profileMeta.style.display = hasName ? "none" : "block";
    profileMeta.textContent = hasName ? "" : "Enter your details below";
  }

  if (editNameBtn) {
    editNameBtn.style.display = hasName ? "inline-flex" : "none";
    if (isSaved) {
      editNameBtn.textContent = "✏️ Edit";
    }
  }

  if (isSaved && profileFields) {
    profileFields.style.display = "none";
  }
}

async function handleSaveProfile() {
  const name = profileNameInput ? profileNameInput.value.trim() : "";
  const ageRaw = profileAge ? profileAge.value.trim() : "";
  const gender = profileGender ? profileGender.value.trim() : "";

  const age = parseInt(ageRaw, 10);
  if (isNaN(age) || age < 1 || age > 120) {
    alert("Please enter a valid age between 1 and 120.");
    if (profileAge) profileAge.focus();
    return;
  }

  if (!gender) {
    alert("Please select your gender.");
    if (profileGender) profileGender.focus();
    return;
  }

  const patient_id = sessionData.profile.patient_id || generatePatientId();
  const cleanName = name || "Anonymous";

  sessionData.profile = {
    ...sessionData.profile,
    name: cleanName,
    age: age,
    gender: gender,
    patient_id: patient_id
  };

  // Close panel and show only the patient name
  updateProfileUI(sessionData.profile, true);

  // Injected into session context string per system instructions:
  // "Patient profile saved — Name: {name}, Age: {age}, Gender: {gender}"
  const injectionMsg = `Patient profile saved — Name: ${cleanName}, Age: ${age}, Gender: ${gender}`;

  showTyping();
  if (sendBtn) sendBtn.disabled = true;

  try {
    const res = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: injectionMsg,
        session_data: sessionData
      })
    });
    const data = await res.json();
    hideTyping();
    if (sendBtn) sendBtn.disabled = false;

    if (data.session) {
      sessionData = data.session;
      if (data.session.profile) {
        updateProfileUI(data.session.profile, true);
      }
    }

    if (data.message) {
      appendBotMsg(mdToHtml(data.message));
    }
  } catch(err) {
    hideTyping();
    if (sendBtn) sendBtn.disabled = false;
    appendBotMsg(mdToHtml(
      `✅ **Patient profile saved — Name: ${cleanName}, Age: ${age}, Gender: ${gender}** (ID: \`${patient_id}\`)\n\n` +
      `Hello **${cleanName}**! Your profile is active. Describe your symptoms to begin your assessment.`
    ));
  }
}

// ─── BODY SYSTEM TABS & QUICK SYMPTOMS ──────────
function renderQuickSymptoms(systemKey) {
  if (!quickSymptoms) return;
  const items = SYSTEM_SYMPTOMS[systemKey] || SYSTEM_SYMPTOMS.all;
  quickSymptoms.innerHTML = "";

  items.forEach(item => {
    const btn = document.createElement("button");
    btn.className = "sym-chip";
    btn.setAttribute("data-sym", item.sym);
    btn.textContent = item.label;

    btn.addEventListener("click", () => {
      handleSymptomClick(item.sym, btn);
    });

    quickSymptoms.appendChild(btn);
  });
}

function handleSymptomClick(symName, chipEl) {
  if (!userInput) return;
  const curVal = userInput.value.trim();

  if (!curVal) {
    userInput.value = `I am having ${symName}`;
  } else if (!curVal.toLowerCase().includes(symName.toLowerCase())) {
    userInput.value = `${curVal}, ${symName}`;
  }

  if (chipEl) {
    chipEl.classList.add("active");
    setTimeout(() => chipEl.classList.remove("active"), 1200);
  }

  if (charCount) {
    charCount.textContent = `${userInput.value.length}/600`;
  }
  userInput.focus();
}

// ─── HEALTH HISTORY ─────────────────────────────
async function refreshSidebarHistory() {
  if (!historyList) return;
  try {
    const res = await fetch("/history");
    const data = await res.json();

    if (!data || !data.length) {
      historyList.innerHTML = '<div class="history-empty">No sessions yet</div>';
      return;
    }

    historyList.innerHTML = "";
    data.slice(0, 5).forEach(item => {
      const div = document.createElement("div");
      div.className = "history-item";
      const dateStr = item.session_date ? new Date(item.session_date).toLocaleDateString() : "";
      const pidStr = item.patient_id_code || item.patient_code || "";
      div.innerHTML = `
        <div class="hi-disease">🩺 ${esc(item.predicted_disease)}</div>
        <div class="hi-meta">${item.confidence ? item.confidence + '%' : ''} · ${pidStr} · ${dateStr}</div>
      `;
      div.addEventListener("click", () => {
        showDiseaseDetail(null, item.predicted_disease);
      });
      historyList.appendChild(div);
    });
  } catch(e) {
    // Ignore silent history errors
  }
}

async function openHistoryPanel() {
  if (!historyPanel || !historyPanelBody) return;
  historyPanel.style.display = "flex";
  historyPanelBody.innerHTML = '<div class="loading-spinner"></div>';

  try {
    const res = await fetch("/history");
    const data = await res.json();

    if (!data || !data.length) {
      historyPanelBody.innerHTML = '<div class="history-empty" style="padding:40px 20px;text-align:center">No recorded health sessions yet.</div>';
      return;
    }

    historyPanelBody.innerHTML = "";
    data.forEach(item => {
      const entry = document.createElement("div");
      entry.className = "history-entry";
      const dateStr = item.session_date ? new Date(item.session_date).toLocaleString() : "";
      let syms = [];
      try { syms = JSON.parse(item.symptoms); } catch(e) { syms = [item.symptoms]; }
      const pidStr = item.patient_id_code || item.patient_code || "HB-00000";

      entry.innerHTML = `
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px">
          <div class="he-disease">🩺 ${esc(item.predicted_disease)}</div>
          <span class="patient-id-badge">${esc(pidStr)}</span>
        </div>
        <div class="he-symptoms">Symptoms: ${(syms || []).join(", ") || "None listed"}</div>
        <div class="he-meta">
          <span class="he-badge">${item.confidence ? item.confidence + '% match' : 'Recorded'}</span>
          <span class="he-badge">${item.patient_name ? esc(item.patient_name) : 'Patient'}</span>
          <span class="he-badge">${dateStr}</span>
        </div>
      `;
      entry.style.cursor = "pointer";
      entry.addEventListener("click", () => {
        showDiseaseDetail(null, item.predicted_disease);
      });
      historyPanelBody.appendChild(entry);
    });
  } catch(e) {
    historyPanelBody.innerHTML = '<div style="color:var(--danger);padding:20px;text-align:center">Failed to load history records.</div>';
  }
}

function closeHistoryPanel() {
  if (historyPanel) historyPanel.style.display = "none";
}

// ─── CLEAR SESSION ──────────────────────────────
async function handleClearSession() {
  const currentPid = sessionData.profile.patient_id || generatePatientId();
  try {
    const res = await fetch("/clear", { method: "POST" });
    const data = await res.json();
    sessionData = data.session_data || { state: "idle", active_symptoms: [], profile: {} };
  } catch(e) {
    sessionData = { state: "idle", active_symptoms: [], profile: {} };
  }

  sessionData.profile.patient_id = currentPid;

  if (chatWindow) {
    chatWindow.innerHTML = "";
  }

  const name = (sessionData.profile && sessionData.profile.name) ? sessionData.profile.name : "";
  const greeting = name ? `👋 **New Health Session for ${name}!**` : "👋 **New Health Session Started!**";

  appendBotMsg(mdToHtml(
    `${greeting}\n\n` +
    "Describe your symptoms below to get started, or select a body system from the sidebar.\n\n" +
    "_Example: 'I have fever, chills, and headache for 2 days'_"
  ));
}

// ─── THEME TOGGLE ───────────────────────────────
function initTheme() {
  const saved = localStorage.getItem("healthbot-theme") || "dark";
  document.documentElement.setAttribute("data-theme", saved);
  if (themeToggle) {
    themeToggle.textContent = saved === "dark" ? "🌙" : "☀️";
  }
}

function toggleTheme() {
  const current = document.documentElement.getAttribute("data-theme") || "dark";
  const next = current === "dark" ? "light" : "dark";
  document.documentElement.setAttribute("data-theme", next);
  localStorage.setItem("healthbot-theme", next);
  if (themeToggle) {
    themeToggle.textContent = next === "dark" ? "🌙" : "☀️";
  }
}

// ─── VOICE INPUT ────────────────────────────────
function initVoiceInput() {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  let recognition = null;
  let isListening = false;
  let baseTextBeforeVoice = "";
  let voiceToast = null;

  function showVoiceToast(msg = "Listening to your symptoms… Speak now") {
    removeVoiceToast();
    voiceToast = document.createElement("div");
    voiceToast.className = "voice-status-toast";
    voiceToast.id = "voiceStatusToast";
    voiceToast.innerHTML = `
      <div class="voice-wave">
        <span></span><span></span><span></span><span></span>
      </div>
      <span>${msg}</span>
    `;
    document.body.appendChild(voiceToast);
  }

  function removeVoiceToast() {
    if (voiceToast && voiceToast.parentNode) {
      voiceToast.parentNode.removeChild(voiceToast);
    }
    voiceToast = null;
    const old = document.getElementById("voiceStatusToast");
    if (old && old.parentNode) old.parentNode.removeChild(old);
  }

  function setVoiceActive(active) {
    isListening = active;
    if (voiceBtn) {
      if (active) {
        voiceBtn.classList.add("recording");
        voiceBtn.title = "Recording… Click to stop voice input";
        showVoiceToast();
      } else {
        voiceBtn.classList.remove("recording");
        voiceBtn.title = "Voice input (Speak symptoms)";
        removeVoiceToast();
      }
    }
  }

  if (!SpeechRecognition) {
    if (voiceBtn) {
      voiceBtn.title = "Voice recognition not supported in this browser";
      voiceBtn.addEventListener("click", () => {
        alert("Voice recognition (Web Speech API) is not supported in this browser. For voice input, please use Google Chrome, Microsoft Edge, or Safari.");
      });
    }
    return;
  }

  try {
    recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = navigator.language || "en-US";
    recognition.maxAlternatives = 1;
  } catch (err) {
    console.error("Speech recognition setup error:", err);
    return;
  }

  recognition.onstart = () => {
    setVoiceActive(true);
    baseTextBeforeVoice = userInput ? userInput.value.trim() : "";
  };

  recognition.onresult = (e) => {
    let interim = "";
    let finalTranscript = "";

    for (let i = 0; i < e.results.length; i++) {
      const trans = e.results[i][0].transcript;
      if (e.results[i].isFinal) {
        finalTranscript += trans + " ";
      } else {
        interim += trans;
      }
    }

    if (userInput) {
      const combinedSpeech = (finalTranscript + interim).trim();
      if (baseTextBeforeVoice) {
        userInput.value = `${baseTextBeforeVoice} ${combinedSpeech}`;
      } else {
        userInput.value = combinedSpeech;
      }
      if (charCount) charCount.textContent = `${userInput.value.length}/600`;
      userInput.style.height = "auto";
      userInput.style.height = `${Math.min(userInput.scrollHeight, 120)}px`;
    }
  };

  recognition.onerror = (e) => {
    console.warn("Speech recognition error:", e.error);
    setVoiceActive(false);
    if (e.error === "not-allowed" || e.error === "service-not-allowed") {
      alert("🎙️ Microphone Access Denied:\nPlease allow microphone access in your browser address bar settings to use voice symptom dictation.");
    } else if (e.error === "audio-capture") {
      alert("🎙️ Microphone Not Found:\nNo microphone was detected on your device. Please plug in a microphone or headset.");
    } else if (e.error === "network") {
      console.warn("Speech recognition network glitch occurred.");
    }
  };

  recognition.onend = () => {
    setVoiceActive(false);
    if (userInput) userInput.focus();
  };

  if (voiceBtn) {
    voiceBtn.addEventListener("click", async () => {
      if (isListening) {
        try {
          recognition.stop();
        } catch (e) {}
        setVoiceActive(false);
      } else {
        // Request microphone permission if supported
        if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
          try {
            await navigator.mediaDevices.getUserMedia({ audio: true });
          } catch (micErr) {
            console.warn("getUserMedia error:", micErr);
            alert("🎙️ Microphone Permission Required:\nPlease grant microphone permission to enable voice input.");
            return;
          }
        }
        try {
          baseTextBeforeVoice = userInput ? userInput.value.trim() : "";
          recognition.start();
        } catch (e) {
          console.warn("Recognition start error:", e);
          try {
            recognition.stop();
            setTimeout(() => recognition.start(), 200);
          } catch (e2) {}
        }
      }
    });
  }
}

// ─── PARTICLE CANVAS ────────────────────────────
function initParticles() {
  if (!particlesCanvas) return;
  const ctx = particlesCanvas.getContext("2d");
  let width = (particlesCanvas.width = window.innerWidth);
  let height = (particlesCanvas.height = window.innerHeight);

  window.addEventListener("resize", () => {
    width = particlesCanvas.width = window.innerWidth;
    height = particlesCanvas.height = window.innerHeight;
  });

  const particles = Array.from({ length: 30 }, () => ({
    x: Math.random() * width,
    y: Math.random() * height,
    r: Math.random() * 2 + 1,
    vx: (Math.random() - 0.5) * 0.4,
    vy: (Math.random() - 0.5) * 0.4,
    alpha: Math.random() * 0.5 + 0.2
  }));

  function animate() {
    ctx.clearRect(0, 0, width, height);
    ctx.fillStyle = "rgba(56, 189, 248, 0.4)";

    particles.forEach(p => {
      p.x += p.vx;
      p.y += p.vy;

      if (p.x < 0) p.x = width;
      if (p.x > width) p.x = 0;
      if (p.y < 0) p.y = height;
      if (p.y > height) p.y = 0;

      ctx.beginPath();
      ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
      ctx.fill();
    });

    requestAnimationFrame(animate);
  }

  animate();
}

// ─── INITIALIZATION & EVENT LISTENERS ───────────
window.addEventListener("DOMContentLoaded", () => {
  // Initialize unique patient ID
  const pid = generatePatientId();
  sessionData.profile.patient_id = pid;
  if (patientIdBadge) patientIdBadge.textContent = `ID: ${pid}`;

  initTheme();
  initParticles();
  initVoiceInput();
  renderQuickSymptoms("all");
  refreshSidebarHistory();

  // Dynamic initials on typing name
  if (profileNameInput) {
    profileNameInput.addEventListener("input", () => {
      const init = getInitials(profileNameInput.value);
      if (profileAvatar) profileAvatar.textContent = init;
    });
  }

  // Inline Edit button (toggles panel open/closed and focuses name input)
  if (editNameBtn) {
    editNameBtn.addEventListener("click", () => {
      if (!profileFields) return;
      const isClosed = profileFields.style.display === "none" || window.getComputedStyle(profileFields).display === "none";
      if (isClosed) {
        profileFields.style.display = "flex";
        editNameBtn.textContent = "✕ Close";
        if (profileNameInput) {
          profileNameInput.focus();
          profileNameInput.select();
        }
      } else {
        profileFields.style.display = "none";
        editNameBtn.textContent = "✏️ Edit";
      }
    });
  }

  // 1. Send button
  if (sendBtn) {
    sendBtn.addEventListener("click", sendMessage);
  }

  // 2. User input (Enter to send, Auto-expand, Char count)
  if (userInput) {
    userInput.addEventListener("keydown", (e) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
      }
    });

    userInput.addEventListener("input", () => {
      userInput.style.height = "auto";
      userInput.style.height = Math.min(userInput.scrollHeight, 120) + "px";
      if (charCount) {
        const len = userInput.value.length;
        charCount.textContent = `${len}/600`;
        if (len > 550) charCount.classList.add("warn");
        else charCount.classList.remove("warn");
      }
    });
  }

  // 3. Theme Toggle
  if (themeToggle) {
    themeToggle.addEventListener("click", toggleTheme);
  }

  // 4. Clear Session
  if (clearBtn) {
    clearBtn.addEventListener("click", handleClearSession);
  }

  // 5. History Panel
  if (historyBtn) {
    historyBtn.addEventListener("click", openHistoryPanel);
  }
  if (historyClose) {
    historyClose.addEventListener("click", closeHistoryPanel);
  }

  // 6. Mobile Sidebar Toggle
  if (menuBtn) {
    menuBtn.addEventListener("click", () => {
      if (sidebar) sidebar.classList.toggle("open");
    });
  }
  if (sidebarClose) {
    sidebarClose.addEventListener("click", () => {
      if (sidebar) sidebar.classList.remove("open");
    });
  }

  // 7. Save Profile
  if (saveProfile) {
    saveProfile.addEventListener("click", handleSaveProfile);
  }

  // 8. Body System Tabs
  if (sysTabs) {
    sysTabs.querySelectorAll(".sys-tab").forEach(tab => {
      tab.addEventListener("click", () => {
        sysTabs.querySelectorAll(".sys-tab").forEach(t => t.classList.remove("active"));
        tab.classList.add("active");
        const sys = tab.getAttribute("data-system") || "all";
        renderQuickSymptoms(sys);
      });
    });
  }

  // 9. Modal close
  if (modalClose) {
    modalClose.addEventListener("click", closeModal);
  }
  if (modalOverlay) {
    modalOverlay.addEventListener("click", (e) => {
      if (e.target === modalOverlay) closeModal();
    });
  }

  // 10. Escape key closes modals
  window.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      closeModal();
      closeHistoryPanel();
    }
  });

  // Welcome greeting
  setTimeout(() => {
    appendBotMsg(mdToHtml(
      "👋 Welcome to **HealthBot AI**!\n\n" +
      "Please enter your **Full Name**, **Age**, and **Gender** in the profile panel to get personalized predictions tailored to your demographic profile.\n\n" +
      "*Example: Set your profile, then type 'I have fever, headache, and cough for 2 days'*\n\n" +
      "_⚠️ For informational use only. Always consult a licensed medical professional._"
    ));
  }, 400);
});

// Expose globals for inline onclicks in generated HTML
window.showDiseaseDetail = showDiseaseDetail;
window.printReport = printReport;
window.printReportFromModal = printReportFromModal;
window.closeModal = closeModal;


