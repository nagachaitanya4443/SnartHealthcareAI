"""
disease_prediction.py
----------------------
Loads the trained RandomForest models (diabetes, heart, kidney) and
provides an interactive form for each disease. Predictions are saved
to the database and linked to a selected patient.
"""

import streamlit as st
import pandas as pd
import joblib
import os

from database import get_patients, save_prediction
from utils import risk_level_from_probability, badge, risk_color

MODEL_DIR = "models"


@st.cache_resource
def load_model(disease: str):
    path = os.path.join(MODEL_DIR, f"{disease}.pkl")
    if not os.path.exists(path):
        return None
    return joblib.load(path)


def show_prediction_page():
    st.title("🧬 Disease Prediction")

    patients_df = get_patients(st.session_state.username)
    if patients_df.empty:
        st.warning("Please add a patient first, from the Patient Management page.")
        return

    # Preselect patient if navigated from patient.py
    default_index = 0
    patient_names = patients_df["name"].tolist()
    if st.session_state.get("selected_patient_id"):
        ids = patients_df["id"].tolist()
        if st.session_state.selected_patient_id in ids:
            default_index = ids.index(st.session_state.selected_patient_id)

    selected_name = st.selectbox("Select Patient", patient_names, index=default_index)
    selected_patient = patients_df[patients_df["name"] == selected_name].iloc[0]

    disease = st.tabs(["🩸 Diabetes", "❤️ Heart Disease", "🩺 Kidney Disease"])

    with disease[0]:
        _diabetes_form(int(selected_patient["id"]))
    with disease[1]:
        _heart_form(int(selected_patient["id"]))
    with disease[2]:
        _kidney_form(int(selected_patient["id"]))


def _predict_and_display(model, input_df, disease_name, patient_id, positive_label, negative_label):
    if model is None:
        st.error(f"Model file for {disease_name} not found. Run train_models.py first.")
        return

    proba = model.predict_proba(input_df)[0]
    prob_positive = float(proba[1]) if len(proba) > 1 else float(proba[0])
    prediction = model.predict(input_df)[0]
    result_label = positive_label if prediction == 1 else negative_label
    risk = risk_level_from_probability(prob_positive)
    color = risk_color(risk)

    st.markdown("### Result")
    col1, col2, col3 = st.columns(3)
    col1.metric("Prediction", result_label)
    col2.metric("Probability", f"{prob_positive*100:.1f}%")
    col3.markdown(f"**Risk Level:**<br>{badge(risk, color)}", unsafe_allow_html=True)

    st.progress(min(max(prob_positive, 0.0), 1.0))

    if st.button(f"💾 Save {disease_name} Result to Patient Record", key=f"save_{disease_name}"):
        save_prediction(patient_id, disease_name, input_df.to_dict(orient="records")[0],
                         result_label, prob_positive, risk)
        st.success("Result saved to patient history.")


def _diabetes_form(patient_id):
    st.subheader("Diabetes Risk Prediction")
    model = load_model("diabetes")

    col1, col2 = st.columns(2)
    with col1:
        pregnancies = st.number_input("Pregnancies", 0, 20, 1, key="d_preg")
        glucose = st.slider("Glucose Level (mg/dL)", 50, 250, 110, key="d_gluc")
        bp = st.slider("Blood Pressure (mm Hg)", 40, 130, 72, key="d_bp")
        skin = st.slider("Skin Thickness (mm)", 0, 60, 20, key="d_skin")
    with col2:
        insulin = st.slider("Insulin (mu U/mL)", 0, 400, 80, key="d_ins")
        bmi = st.slider("BMI", 15.0, 55.0, 25.0, key="d_bmi")
        dpf = st.slider("Diabetes Pedigree Function", 0.05, 2.5, 0.4, key="d_dpf")
        age = st.slider("Age", 18, 90, 35, key="d_age")

    if st.button("🔍 Predict Diabetes Risk", key="btn_diabetes"):
        input_df = pd.DataFrame([{
            "Pregnancies": pregnancies, "Glucose": glucose, "BloodPressure": bp,
            "SkinThickness": skin, "Insulin": insulin, "BMI": bmi,
            "DiabetesPedigreeFunction": dpf, "Age": age
        }])
        _predict_and_display(model, input_df, "diabetes", patient_id, "Diabetic", "Non-Diabetic")


def _heart_form(patient_id):
    st.subheader("Heart Disease Risk Prediction")
    model = load_model("heart")

    col1, col2 = st.columns(2)
    with col1:
        age = st.slider("Age", 20, 90, 50, key="h_age")
        sex = st.selectbox("Sex", ["Male", "Female"], key="h_sex")
        cp = st.selectbox("Chest Pain Type", [0, 1, 2, 3], key="h_cp",
                           help="0: typical angina, 1: atypical, 2: non-anginal, 3: asymptomatic")
        trestbps = st.slider("Resting Blood Pressure", 90, 200, 130, key="h_bps")
        chol = st.slider("Cholesterol (mg/dl)", 120, 450, 220, key="h_chol")
        fbs = st.selectbox("Fasting Blood Sugar > 120 mg/dl", ["No", "Yes"], key="h_fbs")
        restecg = st.selectbox("Resting ECG (0-2)", [0, 1, 2], key="h_ecg")
    with col2:
        thalach = st.slider("Max Heart Rate Achieved", 70, 202, 150, key="h_thalach")
        exang = st.selectbox("Exercise-Induced Angina", ["No", "Yes"], key="h_exang")
        oldpeak = st.slider("ST Depression (oldpeak)", 0.0, 6.2, 1.0, key="h_oldpeak")
        slope = st.selectbox("Slope of ST Segment (0-2)", [0, 1, 2], key="h_slope")
        ca = st.selectbox("Major Vessels Colored (0-3)", [0, 1, 2, 3], key="h_ca")
        thal = st.selectbox("Thalassemia (0-2)", [0, 1, 2], key="h_thal")

    if st.button("🔍 Predict Heart Disease Risk", key="btn_heart"):
        input_df = pd.DataFrame([{
            "age": age, "sex": 1 if sex == "Male" else 0, "cp": cp, "trestbps": trestbps,
            "chol": chol, "fbs": 1 if fbs == "Yes" else 0, "restecg": restecg,
            "thalach": thalach, "exang": 1 if exang == "Yes" else 0, "oldpeak": oldpeak,
            "slope": slope, "ca": ca, "thal": thal
        }])
        _predict_and_display(model, input_df, "heart", patient_id, "Heart Disease Detected", "No Heart Disease")


def _kidney_form(patient_id):
    st.subheader("Chronic Kidney Disease Risk Prediction")
    model = load_model("kidney")

    col1, col2 = st.columns(2)
    with col1:
        age = st.slider("Age", 2, 90, 45, key="k_age")
        bp = st.slider("Blood Pressure", 50, 180, 76, key="k_bp")
        sg = st.select_slider("Specific Gravity", options=[1.005, 1.010, 1.015, 1.020, 1.025], value=1.015, key="k_sg")
        al = st.slider("Albumin (0-5)", 0, 5, 0, key="k_al")
        su = st.slider("Sugar (0-5)", 0, 5, 0, key="k_su")
        bu = st.slider("Blood Urea", 10, 200, 40, key="k_bu")
        sc = st.slider("Serum Creatinine", 0.3, 15.0, 1.2, key="k_sc")
    with col2:
        sod = st.slider("Sodium", 110, 150, 137, key="k_sod")
        pot = st.slider("Potassium", 2.5, 8.0, 4.4, key="k_pot")
        hemo = st.slider("Hemoglobin", 3.0, 18.0, 13.5, key="k_hemo")
        wbcc = st.slider("White Blood Cell Count", 3000, 20000, 8000, key="k_wbcc")
        rbcc = st.slider("Red Blood Cell Count", 2.0, 7.0, 4.8, key="k_rbcc")
        htn = st.selectbox("Hypertension", ["No", "Yes"], key="k_htn")
        dm = st.selectbox("Diabetes Mellitus", ["No", "Yes"], key="k_dm")

    if st.button("🔍 Predict Kidney Disease Risk", key="btn_kidney"):
        input_df = pd.DataFrame([{
            "age": age, "bp": bp, "sg": sg, "al": al, "su": su, "bu": bu, "sc": sc,
            "sod": sod, "pot": pot, "hemo": hemo, "wbcc": wbcc, "rbcc": rbcc,
            "htn": 1 if htn == "Yes" else 0, "dm": 1 if dm == "Yes" else 0
        }])
        _predict_and_display(model, input_df, "kidney", patient_id, "CKD Detected", "No CKD")
