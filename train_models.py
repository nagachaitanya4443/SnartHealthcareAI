"""
train_models.py
----------------
One-time utility script that generates realistic *synthetic* datasets
(diabetes, heart disease, kidney disease) and trains a RandomForest
classifier for each one, saving both the .csv datasets and the .pkl
models into the expected folders.

Run this once with:  python train_models.py

NOTE: These are synthetically generated datasets meant to make the app
fully runnable out-of-the-box. For a real deployment, replace the CSVs
in /datasets with real, properly-licensed clinical data (e.g. the Pima
Indians Diabetes dataset, UCI Heart Disease dataset, and UCI Chronic
Kidney Disease dataset) and simply re-run this script.
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import joblib
import os

np.random.seed(42)
os.makedirs("datasets", exist_ok=True)
os.makedirs("models", exist_ok=True)

N = 1200


def save_model(model, X, y, path):
    model.fit(X, y)
    joblib.dump(model, path)
    acc = model.score(X, y)
    print(f"Saved {path} | train accuracy: {acc:.3f}")


# ----------------------------------------------------------------------
# 1. DIABETES DATASET (Pima-style features)
# ----------------------------------------------------------------------
def make_diabetes(n=N):
    outcome = np.random.binomial(1, 0.35, n)
    glucose = np.where(outcome == 1,
                        np.random.normal(150, 30, n),
                        np.random.normal(105, 20, n))
    bmi = np.where(outcome == 1,
                   np.random.normal(33, 6, n),
                   np.random.normal(26, 5, n))
    age = np.where(outcome == 1,
                   np.random.normal(45, 12, n),
                   np.random.normal(32, 10, n))
    df = pd.DataFrame({
        "Pregnancies": np.random.poisson(2.5, n),
        "Glucose": glucose.clip(60, 250),
        "BloodPressure": np.random.normal(72, 12, n).clip(40, 130),
        "SkinThickness": np.random.normal(23, 10, n).clip(0, 60),
        "Insulin": np.random.normal(85, 60, n).clip(0, 400),
        "BMI": bmi.clip(15, 55),
        "DiabetesPedigreeFunction": np.random.gamma(2, 0.25, n).clip(0.05, 2.5),
        "Age": age.clip(18, 85),
        "Outcome": outcome
    })
    return df


diabetes_df = make_diabetes()
diabetes_df.to_csv("datasets/diabetes.csv", index=False)
X = diabetes_df.drop(columns=["Outcome"])
y = diabetes_df["Outcome"]
save_model(RandomForestClassifier(n_estimators=200, max_depth=6, random_state=42),
           X, y, "models/diabetes.pkl")

# ----------------------------------------------------------------------
# 2. HEART DISEASE DATASET (UCI-style features)
# ----------------------------------------------------------------------
def make_heart(n=N):
    target = np.random.binomial(1, 0.45, n)
    age = np.where(target == 1, np.random.normal(58, 9, n), np.random.normal(48, 10, n))
    chol = np.where(target == 1, np.random.normal(250, 45, n), np.random.normal(200, 35, n))
    thalach = np.where(target == 1, np.random.normal(130, 20, n), np.random.normal(155, 18, n))
    oldpeak = np.where(target == 1, np.random.gamma(2, 0.9, n), np.random.gamma(1, 0.4, n))

    df = pd.DataFrame({
        "age": age.clip(25, 90),
        "sex": np.random.binomial(1, 0.6, n),
        "cp": np.random.randint(0, 4, n),
        "trestbps": np.random.normal(131, 17, n).clip(90, 200),
        "chol": chol.clip(120, 450),
        "fbs": np.random.binomial(1, 0.15, n),
        "restecg": np.random.randint(0, 3, n),
        "thalach": thalach.clip(70, 202),
        "exang": np.random.binomial(1, 0.3, n),
        "oldpeak": oldpeak.clip(0, 6.2),
        "slope": np.random.randint(0, 3, n),
        "ca": np.random.randint(0, 4, n),
        "thal": np.random.randint(0, 3, n),
        "target": target
    })
    return df


heart_df = make_heart()
heart_df.to_csv("datasets/heart.csv", index=False)
X = heart_df.drop(columns=["target"])
y = heart_df["target"]
save_model(RandomForestClassifier(n_estimators=200, max_depth=6, random_state=42),
           X, y, "models/heart.pkl")

# ----------------------------------------------------------------------
# 3. CHRONIC KIDNEY DISEASE DATASET (UCI-style, simplified numeric subset)
# ----------------------------------------------------------------------
def make_kidney(n=N):
    ckd = np.random.binomial(1, 0.4, n)
    bu = np.where(ckd == 1, np.random.normal(80, 30, n), np.random.normal(30, 10, n))
    sc = np.where(ckd == 1, np.random.gamma(3, 1.1, n), np.random.gamma(1.2, 0.5, n))
    hemo = np.where(ckd == 1, np.random.normal(10, 2, n), np.random.normal(14, 1.5, n))
    sg = np.where(ckd == 1, np.random.normal(1.012, 0.005, n), np.random.normal(1.020, 0.004, n))

    df = pd.DataFrame({
        "age": np.random.normal(50, 15, n).clip(2, 90),
        "bp": np.random.normal(76, 13, n).clip(50, 180),
        "sg": sg.clip(1.005, 1.025),
        "al": np.where(ckd == 1, np.random.randint(1, 5, n), np.random.randint(0, 2, n)),
        "su": np.where(ckd == 1, np.random.randint(0, 5, n), np.random.randint(0, 2, n)),
        "bu": bu.clip(10, 200),
        "sc": sc.clip(0.3, 15),
        "sod": np.random.normal(137, 6, n).clip(110, 150),
        "pot": np.random.normal(4.4, 0.8, n).clip(2.5, 8),
        "hemo": hemo.clip(3, 18),
        "wbcc": np.random.normal(8500, 2500, n).clip(3000, 20000),
        "rbcc": np.random.normal(4.7, 0.9, n).clip(2, 7),
        "htn": np.where(ckd == 1, np.random.binomial(1, 0.7, n), np.random.binomial(1, 0.15, n)),
        "dm": np.where(ckd == 1, np.random.binomial(1, 0.5, n), np.random.binomial(1, 0.1, n)),
        "classification": ckd
    })
    return df


kidney_df = make_kidney()
kidney_df.to_csv("datasets/kidney.csv", index=False)
X = kidney_df.drop(columns=["classification"])
y = kidney_df["classification"]
save_model(RandomForestClassifier(n_estimators=200, max_depth=6, random_state=42),
           X, y, "models/kidney.pkl")

print("\nAll datasets and models generated successfully.")
