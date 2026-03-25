# 🏥 Emotional Distress Assessment System
### ML-powered assessment for cancer patients and caregivers

---

## 📁 Project Structure

```
emotional-distress-assessment/
│
├── app.py                        ← Flask backend (routes + prediction logic)
├── train_models.py               ← Run ONCE to train & save ML models
├── requirements.txt              ← Python dependencies
│
├── data/
│   ├── caregivers_actual.xlsx    ← Caregiver training data (N=103)
│   └── Patient_actual1.xlsx      ← Patient training data (N=21)
│
├── models/                       ← Auto-created by train_models.py
│   ├── caregiver_kfold_best_model.pkl
│   ├── caregiver_kfold_scaler.pkl
│   ├── patient_loocv_best_model.pkl
│   └── patient_loocv_scaler.pkl
│
├── templates/
│   └── index.html                ← Main HTML page (Flask Jinja2 template)
│
└── static/
    ├── css/
    │   └── style.css             ← All styles
    └── js/
        └── app.js                ← Frontend logic (form flow + API calls)
```

---

## ⚙️ ML Models Used

| Role       | Method              | Dataset   | Best Model           |
|------------|---------------------|-----------|----------------------|
| Caregiver  | Stratified 5-Fold CV| N = 103   | Logistic Regression  |
| Patient    | Leave-One-Out CV    | N = 21    | Decision Tree        |

**Features — Caregiver:**  
`sleep_score`, `Financial_Score`, `Social_Score`, `Anxiety_Score`, `Care_Management_Score`, `Gender`

**Features — Patient:**  
`Patient_Sleep_Score`, `Patient_Physical_Symptom_Score_Sub`, `Patient_Emotional_Score_Sub`, `Age`, `Gender`

---

## 🚀 Local Development

### Prerequisites
Python 3.8+

### Quick Local Run
```bash
pip install -r requirements.txt
python train_models.py  # If models/ missing
python app.py
```
Visit: http://localhost:5000

## ☁️ Vercel Deployment (Serverless)

### Option 1: GitHub + Vercel Dashboard (Recommended)
1. `git init; git add .; git commit -m "Initial"; git branch -M main`
2. Create GitHub repo, `git remote add origin <url>; git push -u origin main`
3. vercel.com → New Project → Import repo → Deploy

### Option 2: Vercel CLI
```bash
npm i -g vercel
vercel login
vercel
```
Follow prompts (scope, link, dir=.).

### Deployed URLs
- App: https://your-project.vercel.app
- API Health: https://your-project.vercel.app/api/health

**Notes:**
- Models/data/static auto-included.
- Cold starts ~1-2s (serverless).
- Free tier: 100GB-hours/mo.

### Test Deployed
```
curl https://your-project.vercel.app/api/health
```

---

## 🌐 API Endpoints

| Method | Endpoint       | Description                            |
|--------|----------------|----------------------------------------|
| GET    | `/`            | Serve the frontend HTML page           |
| GET    | `/api/config`  | Get states, cancer types, questions    |
| POST   | `/api/predict` | Submit answers → get prediction        |
| GET    | `/api/health`  | Check if models are loaded             |

### POST `/api/predict` — Request Body

```json
{
  "role": "patient",
  "demographics": {
    "age_group": 3,
    "gender": 0,
    "treatments": ["Chemotherapy", "Surgery"]
  },
  "answers": {
    "feel_tense": 4,
    "worry": 3,
    "feel_depressed": 4,
    "feel_uncertain": 3,
    "pain": 3,
    "felt_nauseated": 2,
    "felt_weak": 3,
    "lacked_appetite": 2,
    "tired": 4,
    "need_to_rest": 4,
    "trouble_sleeping": 3
  }
}
```

### Response

```json
{
  "success": true,
  "prediction": "Moderate",
  "confidence": 0.87,
  "scores": {
    "Emotional Functioning Score": 3.5,
    "Physical Symptoms Score": 2.5,
    "Sleep Quality Score": 3.67
  },
  "interpretation": "Your responses indicate moderate emotional distress...",
  "role": "patient"
}
```

---

## ❓ Troubleshooting

| Problem | Solution |
|---|---|
| `ModuleNotFoundError: flask` | Run `pip install -r requirements.txt` |
| `FileNotFoundError: Missing model files` | Run `python train_models.py` first |
| `Missing columns` error during training | Check that Excel files are in `data/` folder unchanged |
| Port 5000 already in use | Change port in `app.py`: `app.run(port=5001)` |
| Browser shows blank page | Make sure Flask is running and go to `http://localhost:5000` |

---

## 📝 Notes

- The `models/` folder is **auto-created** by `train_models.py` — you do not need to create it manually.
- The Excel data files **must stay in** `data/` and keep their original names.
- Models are retrained fresh every time you run `train_models.py`.
- No internet connection is required once dependencies are installed.

---

© 2024 Emotional Distress Assessment System | For Research Purposes Only
