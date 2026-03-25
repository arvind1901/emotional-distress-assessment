"""
Emotional Distress Assessment — Vercel Serverless Python Handler
Adapated from app.py for Vercel deployment
"""

import os
import pickle
import numpy as np
from flask import Flask, request, jsonify
import json

app = Flask(__name__)

# Model paths - relative to api/ dir
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "..", "models")

CARE_MODEL  = os.path.join(MODEL_DIR, "caregiver_kfold_best_model.pkl")
CARE_SCALER = os.path.join(MODEL_DIR, "caregiver_kfold_scaler.pkl")
PAT_MODEL   = os.path.join(MODEL_DIR, "patient_loocv_best_model.pkl")
PAT_SCALER  = os.path.join(MODEL_DIR, "patient_loocv_scaler.pkl")

# ─────────────────────────────────────────────
# STATIC DATA (copied from app.py)
# ─────────────────────────────────────────────
INDIAN_STATES = [
    "Andhra Pradesh","Arunachal Pradesh","Assam","Bihar","Chhattisgarh","Goa","Gujarat",
    "Haryana","Himachal Pradesh","Jharkhand","Karnataka","Kerala","Madhya Pradesh",
    "Maharashtra","Manipur","Meghalaya","Mizoram","Nagaland","Odisha","Punjab",
    "Rajasthan","Sikkim","Tamil Nadu","Telangana","Tripura","Uttar Pradesh",
    "Uttarakhand","West Bengal","Andaman and Nicobar Islands","Chandigarh",
    "Dadra and Nagar Haveli and Daman and Diu","Delhi","Jammu and Kashmir",
    "Ladakh","Lakshadweep","Puducherry"
]

CANCER_TYPES = [
    "Breast Cancer","Lung Cancer","Colorectal Cancer","Prostate Cancer","Stomach Cancer",
    "Liver Cancer","Cervical Cancer","Esophageal Cancer","Thyroid Cancer","Bladder Cancer",
    "Non-Hodgkin Lymphoma","Pancreatic Cancer","Leukemia","Kidney Cancer","Oral Cancer",
    "Brain Tumor","Ovarian Cancer","Skin Cancer (Melanoma)","Blood Cancer","Other"
]

TREATMENT_TYPES = [
    "Surgery","Chemotherapy","Radiation Therapy","Immunotherapy","Targeted Therapy",
    "Hormone Therapy","Stem Cell Transplant","Palliative Care","Medication","Other"
]

CAREGIVER_QUESTIONS = {
    "psychological": [
        {"id": "exp_anxiety_depression_emotional_exhaustion", "text": "I feel anxiety, depression, or emotional exhaustion."},
        {"id": "worry_health_deterioration_possible_death",   "text": "I worry about health deterioration or possible death."},
        {"id": "feel_guilty",        "text": "I feel guilty."},
        {"id": "unclear_expectations","text": "Caregiving expectations are unclear."}
    ],
    "social": [
        {"id": "social_activities_reduced",  "text": "My social activities are reduced."},
        {"id": "strained_relationships",     "text": "My relationships are strained."},
        {"id": "give_up_hobbies",            "text": "I have given up hobbies or personal interests."},
        {"id": "little_no_time_for_yourself","text": "I have little or no time for myself."},
        {"id": "burden",                     "text": "I feel caregiving is a burden."},
        {"id": "overwhelmed",                "text": "I feel overwhelmed."},
        {"id": "affected_performance",       "text": "My performance (work/role) is affected."}
    ],
    "sleep_physical": [
        {"id": "sleep_disturbed",     "text": "My sleep is disturbed."},
        {"id": "rest_sleep",          "text": "I get restful sleep."},
        {"id": "physically_exhausted","text": "I feel physically exhausted."}
    ],
    "financial": [
        {"id": "lost_income_leave_work",      "text": "I have lost income or had to leave work."},
        {"id": "medical_expenses_increased",  "text": "Medical expenses have increased."},
        {"id": "risk_jobloss",                "text": "I worry about losing my job."},
        {"id": "missed_ownmedical",           "text": "I missed my own medical appointments."}
    ],
    "care_management": [
        {"id": "difficult_to_manage", "text": "Managing the patient's care is difficult."}
    ],
    "protective": [
        {"id": "closer_to_patient", "text": "Caregiving makes me feel closer to the patient."},
        {"id": "sense_of_purpose",  "text": "Caregiving gives me a sense of purpose."}
    ]
}

PATIENT_QUESTIONS = {
    "emotional": [
        {"id": "feel_tense",    "text": "I feel tense."},
        {"id": "worry",         "text": "I worry."},
        {"id": "feel_depressed","text": "I feel depressed."},
        {"id": "feel_uncertain","text": "I feel uncertain about my health/future."}
    ],
    "physical": [
        {"id": "pain",           "text": "I experience pain."},
        {"id": "felt_nauseated", "text": "I feel nauseated."},
        {"id": "felt_weak",      "text": "I feel weak."},
        {"id": "lacked_appetite","text": "I lack appetite."}
    ],
    "sleep": [
        {"id": "tired",           "text": "I feel tired."},
        {"id": "need_to_rest",    "text": "I need to rest."},
        {"id": "trouble_sleeping","text": "I have trouble sleeping."}
    ]
}

# Copy all functions from app.py: _get, calculate_caregiver_scores, calculate_patient_scores, get_interpretation, ModelManager
def _get(answers, key):
    if key not in answers or answers[key] is None:
        raise ValueError(f"Missing answer: {key}")
    return float(answers[key])

def calculate_caregiver_scores(answers, demographics):
    exp_anxiety        = _get(answers, "exp_anxiety_depression_emotional_exhaustion")
    worry_death        = _get(answers, "worry_health_deterioration_possible_death")
    feel_guilty        = _get(answers, "feel_guilty")
    unclear            = _get(answers, "unclear_expectations")

    psychological_score = (exp_anxiety + worry_death + feel_guilty + unclear) / 4
    anxiety_score       = (exp_anxiety + feel_guilty + unclear) / 3

    social_act         = _get(answers, "social_activities_reduced")
    strained           = _get(answers, "strained_relationships")
    hobbies            = _get(answers, "give_up_hobbies")
    no_time            = _get(answers, "little_no_time_for_yourself")
    burden             = _get(answers, "burden")
    overwhelmed        = _get(answers, "overwhelmed")
    perf               = _get(answers, "affected_performance")

    social_score           = (no_time + social_act + perf) / 3
    emotional_burden_raw   = (strained + social_act + hobbies + burden + overwhelmed + no_time) / 6

    closer             = _get(answers, "closer_to_patient")
    purpose            = _get(answers, "sense_of_purpose")
    protective_factor  = (closer + purpose) / 2
    emotion_score      = emotional_burden_raw - (0.5 * protective_factor)

    sleep_disturbed    = _get(answers, "sleep_disturbed")
    rest_sleep         = _get(answers, "rest_sleep")
    physically_exh     = _get(answers, "physically_exhausted")
    sleep_score        = (rest_sleep + sleep_disturbed) / 2

    lost_income        = _get(answers, "lost_income_leave_work")
    med_expenses       = _get(answers, "medical_expenses_increased")
    risk_job           = _get(answers, "risk_jobloss")
    missed_med         = _get(answers, "missed_ownmedical")
    financial_score    = (lost_income + med_expenses + missed_med) / 3

    care_mgmt_score    = _get(answers, "difficult_to_manage")

    gender = float(demographics.get("gender", 0))

    features = [sleep_score, financial_score, social_score, anxiety_score, care_mgmt_score, gender]

    scores_breakdown = {
        "Psychological Score":  round(psychological_score, 2),
        "Social Impact Score":  round(social_score, 2),
        "Sleep Score":          round(sleep_score, 2),
        "Financial Score":      round(financial_score, 2),
        "Care Management Score":round(care_mgmt_score, 2),
        "Emotional Score":      round(emotion_score, 2)
    }
    return features, scores_breakdown

def calculate_patient_scores(answers, demographics):
    feel_tense      = _get(answers, "feel_tense")
    worry           = _get(answers, "worry")
    feel_depressed  = _get(answers, "feel_depressed")
    feel_uncertain  = _get(answers, "feel_uncertain")

    pain            = _get(answers, "pain")
    felt_nauseated  = _get(answers, "felt_nauseated")
    felt_weak       = _get(answers, "felt_weak")
    lacked_appetite = _get(answers, "lacked_appetite")

    tired           = _get(answers, "tired")
    need_to_rest    = _get(answers, "need_to_rest")
    trouble_sleep   = _get(answers, "trouble_sleeping")

    emotional_score = (feel_tense + worry + feel_depressed + feel_uncertain) / 4
    physical_score  = (pain + felt_nauseated + felt_weak + lacked_appetite) / 4
    sleep_score     = (tired + need_to_rest + trouble_sleep) / 3

    age    = float(demographics.get("age_group", 3))
    gender = float(demographics.get("gender", 0))

    features = [sleep_score, physical_score, emotional_score, age, gender]

    scores_breakdown = {
        "Emotional Functioning Score": round(emotional_score, 2),
        "Physical Symptoms Score":     round(physical_score, 2),
        "Sleep Quality Score":         round(sleep_score, 2)
    }
    return features, scores_breakdown

def get_interpretation(label, role):
    if label == "Low":
        return ("Your responses indicate low emotional distress. "
                "Continue healthy coping strategies and reach out for support if needed.")
    if label == "Moderate":
        return ("Your responses indicate moderate emotional distress. "
                "Consider talking to a counselor, support group, or healthcare professional.")
    return ("Your responses indicate high emotional distress. "
            "We strongly recommend seeking professional mental health support.")

class ModelManager:
    models_loaded = False
    care_pipe = None
    pat_pipe = None

    @classmethod
    def load_models(cls):
        if cls.models_loaded:
            return
        missing = [p for p in [CARE_MODEL, CARE_SCALER, PAT_MODEL, PAT_SCALER]
                   if not os.path.exists(p)]
        if missing:
            print(f"Missing models: {missing}")
            cls.models_loaded = True
            return
        try:
            cls.care_pipe  = pickle.load(open(CARE_MODEL,  "rb"))
            cls.pat_pipe   = pickle.load(open(PAT_MODEL,   "rb"))
            cls.models_loaded = True
            print("✅ Models loaded for Vercel")
        except Exception as e:
            print(f"Model load error: {e}")

    @classmethod
    def _predict(cls, pipe, features):
        if not pipe:
            return 1, None  # Default moderate
        X = np.array(features).reshape(1, -1)
        pred = pipe.predict(X)[0]
        conf = None
        if hasattr(pipe, "predict_proba"):
            conf = float(max(pipe.predict_proba(X)[0]))
        return pred, conf

    @classmethod
    def predict_caregiver(cls, features):
        cls.load_models()
        return cls._predict(cls.care_pipe, features)

    @classmethod
    def predict_patient(cls, features):
        cls.load_models()
        return cls._predict(cls.pat_pipe, features)

ModelManager.load_models()
LABEL_MAP = {0: "Low", 1: "Moderate", 2: "High"}

# ─────────────────────────────────────────────
# ROUTES (identical to app.py)
# ─────────────────────────────────────────────
@app.route("/")
def index():
    # Serve root index.html (static by Vercel)
    return app.response_class(
        response=open(os.path.join(BASE_DIR, "..", "index.html")).read(),
        status=200,
        mimetype='text/html'
    )

@app.route("/api/config")
def get_config():
    return jsonify({
        "states": INDIAN_STATES,
        "cancerTypes": CANCER_TYPES,
        "treatmentTypes": TREATMENT_TYPES,
        "caregiverQuestions": CAREGIVER_QUESTIONS,
        "patientQuestions": PATIENT_QUESTIONS
    })

@app.route("/api/predict", methods=["POST"])
def predict():
    try:
        data = request.json or {}
        role = data.get("role")
        demographics = data.get("demographics", {})
        answers = data.get("answers", {})

        if role not in ("caregiver", "patient"):
            return jsonify({"success": False, "error": "Invalid role"}), 400

        if role == "caregiver":
            features, scores = calculate_caregiver_scores(answers, demographics)
            pred, conf = ModelManager.predict_caregiver(features)
        else:
            features, scores = calculate_patient_scores(answers, demographics)
            pred, conf = ModelManager.predict_patient(features)

        label = LABEL_MAP.get(pred) if isinstance(pred, (int, float)) else str(pred).strip().title()

        return jsonify({
            "success": True,
            "prediction": label,
            "confidence": round(conf, 4) if conf else None,
            "scores": scores,
            "interpretation": get_interpretation(label, role),
            "role": role
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route("/api/health")
def health():
    ModelManager.load_models()
    missing = [CARE_MODEL, CARE_SCALER, PAT_MODEL, PAT_SCALER]
    missing = [p for p in missing if not os.path.exists(p)]
    return jsonify({
        "status": "healthy" if ModelManager.models_loaded and ModelManager.care_pipe and ModelManager.pat_pipe else "degraded",
        "caregiver_model": ModelManager.care_pipe is not None,
        "patient_model": ModelManager.pat_pipe is not None,
        "missing_model_files": [os.path.basename(p) for p in missing]
    })

# Vercel WSGI handler
def handler(request):
    # Path prefix handling for Vercel
    path = request.path
    if path.startswith('/api/'):
        path = path
    else:
        path = path or '/'
    
    # Method
    method = request.method
    
    # Headers
    headers_list = request.headers
    headers = {}
    for header in headers_list:
        headers[header[0].lower()] = header[1]
    
    # Body
    body = request.get_data(as_text=True)
    if method == 'POST' and 'application/json' in headers.get('content-type', ''):
        body = json.loads(body)
    
    # Create Flask request context
    with app.test_request_context(path, method=method, headers=headers, data=body, json=body):
        # Process request
        response = app.full_dispatch_request()
        
        # Build response
        resp_headers = {}
        for k, v in app.response_class.default_mimetype_params.items():
            resp_headers[k] = v
        for k, v in response.headers:
            resp_headers[k.lower()] = v
        
        return {
            'statusCode': response.status_code,
            'headers': resp_headers,
            'body': response.get_data(as_text=True)
        }

# Vercel exports handler as default

