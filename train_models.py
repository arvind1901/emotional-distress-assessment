"""
===========================================================
TRAIN ALL MODELS — Run this ONCE before starting the app
Saves PKL files to models/ directory
===========================================================
"""

import pandas as pd
import numpy as np
import warnings
import pickle
import os

from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.model_selection import StratifiedKFold, LeaveOneOut, cross_val_score, cross_val_predict
from sklearn.metrics import accuracy_score, f1_score, classification_report
from sklearn.linear_model import LogisticRegression, Perceptron
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier, GradientBoostingClassifier

warnings.filterwarnings("ignore")

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR  = os.path.join(BASE_DIR, "models")
DATA_DIR   = os.path.join(BASE_DIR, "data")
os.makedirs(MODEL_DIR, exist_ok=True)

MODELS = [
    ("Logistic Regression", LogisticRegression(max_iter=1000, class_weight="balanced")),
    ("Naive Bayes",          GaussianNB()),
    ("KNN",                  KNeighborsClassifier(n_neighbors=5)),
    ("SVM (RBF)",            SVC(kernel="rbf", class_weight="balanced", probability=True)),
    ("Perceptron",           Perceptron(max_iter=1000)),
    ("Decision Tree",        DecisionTreeClassifier(max_depth=5, random_state=42)),
    ("Random Forest",        RandomForestClassifier(n_estimators=200, max_depth=6, random_state=42)),
    ("Extra Trees",          ExtraTreesClassifier(n_estimators=200, max_depth=6, random_state=42)),
    ("Gradient Boosting",    GradientBoostingClassifier(random_state=42)),
]


# ─────────────────────────────────────────────────────────
# CAREGIVER — Stratified 5-Fold CV  (N = 103)
# ─────────────────────────────────────────────────────────
def train_caregiver():
    print("\n" + "="*60)
    print("CAREGIVER MODEL — Stratified 5-Fold CV (N=103)")
    print("="*60)

    df = pd.read_excel(os.path.join(DATA_DIR, "caregivers_actual.xlsx"))
    df.columns = df.columns.str.strip()
    df.rename(columns={"Physical & Financial Strain Score": "Physical_Financial_Score"}, inplace=True)
    df["Care_Management_Score"] = df["difficult_to_manage"]

    FEATURES = ["sleep_score", "Financial_Score", "Social_Score",
                "Anxiety_Score", "Care_Management_Score", "Gender"]
    TARGET   = "Rating"

    X = df[FEATURES].values
    y = df[TARGET].values

    skf     = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    results = []

    for name, model in MODELS:
        pipe = Pipeline([("scaler", StandardScaler()), ("model", model)])
        acc  = cross_val_score(pipe, X, y, cv=skf, scoring="accuracy").mean()
        f1   = cross_val_score(pipe, X, y, cv=skf, scoring="f1_weighted").mean()
        results.append((name, acc, f1, model))
        print(f"  {name:<22}  Acc={acc:.4f}  F1={f1:.4f}")

    results.sort(key=lambda r: r[2], reverse=True)
    best_name, best_acc, best_f1, best_model = results[0]
    print(f"\n  ✅ Best: {best_name}  (F1={best_f1:.4f})")

    # Fit on full data
    prod_pipe = Pipeline([("scaler", StandardScaler()), ("model", best_model)])
    prod_pipe.fit(X, y)

    scaler = StandardScaler(); scaler.fit(X)

    model_path  = os.path.join(MODEL_DIR, "caregiver_kfold_best_model.pkl")
    scaler_path = os.path.join(MODEL_DIR, "caregiver_kfold_scaler.pkl")

    with open(model_path,  "wb") as f: pickle.dump(prod_pipe, f)
    with open(scaler_path, "wb") as f: pickle.dump(scaler, f)

    print(f"  Saved: {model_path}")
    print(f"  Saved: {scaler_path}")
    return best_name


# ─────────────────────────────────────────────────────────
# PATIENT — Leave-One-Out CV  (N = 21)
# ─────────────────────────────────────────────────────────
def train_patient():
    print("\n" + "="*60)
    print("PATIENT MODEL — LOOCV (N=21)")
    print("="*60)

    df = pd.read_excel(os.path.join(DATA_DIR, "Patient_actual1.xlsx"))
    df.columns = df.columns.str.strip()
    df = df[df["Rating"].isin(["High", "Moderate", "Low"])].copy()
    df.reset_index(drop=True, inplace=True)

    FEATURES = ["Patient_Sleep_Score", "Patient_Physical_Symptom_Score_Sub",
                "Patient_Emotional_Score_Sub", "Age", "Gender"]
    TARGET   = "Rating"

    X = df[FEATURES].values
    y = df[TARGET].values

    loo     = LeaveOneOut()
    results = []
    models_small = [
        ("Logistic Regression", LogisticRegression(max_iter=1000, class_weight="balanced")),
        ("Naive Bayes",          GaussianNB()),
        ("KNN",                  KNeighborsClassifier(n_neighbors=3)),
        ("SVM (RBF)",            SVC(kernel="rbf", class_weight="balanced", probability=True)),
        ("Perceptron",           Perceptron(max_iter=1000)),
        ("Decision Tree",        DecisionTreeClassifier(max_depth=3, random_state=42)),
        ("Random Forest",        RandomForestClassifier(n_estimators=100, max_depth=3, random_state=42)),
        ("Extra Trees",          ExtraTreesClassifier(n_estimators=100, max_depth=3, random_state=42)),
        ("Gradient Boosting",    GradientBoostingClassifier(n_estimators=50, max_depth=2, random_state=42)),
    ]

    for name, model in models_small:
        pipe   = Pipeline([("scaler", StandardScaler()), ("model", model)])
        y_pred = cross_val_predict(pipe, X, y, cv=loo)
        acc    = accuracy_score(y, y_pred)
        f1     = f1_score(y, y_pred, average="weighted", zero_division=0)
        results.append((name, acc, f1, model))
        print(f"  {name:<22}  Acc={acc:.4f}  F1={f1:.4f}")

    results.sort(key=lambda r: r[2], reverse=True)
    best_name, best_acc, best_f1, best_model = results[0]
    print(f"\n  ✅ Best: {best_name}  (F1={best_f1:.4f})")

    # Fit on full data
    prod_pipe = Pipeline([("scaler", StandardScaler()), ("model", best_model)])
    prod_pipe.fit(X, y)

    scaler = StandardScaler(); scaler.fit(X)

    model_path  = os.path.join(MODEL_DIR, "patient_loocv_best_model.pkl")
    scaler_path = os.path.join(MODEL_DIR, "patient_loocv_scaler.pkl")

    with open(model_path,  "wb") as f: pickle.dump(prod_pipe, f)
    with open(scaler_path, "wb") as f: pickle.dump(scaler, f)

    print(f"  Saved: {model_path}")
    print(f"  Saved: {scaler_path}")
    return best_name


if __name__ == "__main__":
    print("\n🚀 TRAINING ALL MODELS...")
    c = train_caregiver()
    p = train_patient()
    print("\n" + "="*60)
    print("✅ ALL MODELS TRAINED & SAVED TO models/")
    print(f"   Caregiver best → {c}")
    print(f"   Patient  best  → {p}")
    print("="*60)
    print("\nNow run:  python app.py")
