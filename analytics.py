"""
analytics.py
------------
Population-level analytics dashboard: dataset exploration charts and
trends drawn from the prediction history stored in the database.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from database import get_all_predictions


DATASET_PATHS = {
    "Diabetes": "datasets/diabetes.csv",
    "Heart Disease": "datasets/heart.csv",
    "Kidney Disease": "datasets/kidney.csv",
}


def show_analytics_page():
    st.title("📊 Analytics")

    tab_pred, tab_data = st.tabs(["🩺 Prediction History Analytics", "📁 Dataset Explorer"])

    with tab_pred:
        _prediction_analytics()

    with tab_data:
        _dataset_explorer()


def _prediction_analytics():
    df = get_all_predictions(st.session_state.username)

    if df.empty:
        st.info("No predictions recorded yet. Run some predictions from the Disease Prediction page.")
        return

    df["created_at"] = pd.to_datetime(df["created_at"])

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Predictions", len(df))
    col2.metric("Unique Patients", df["patient_name"].nunique())
    col3.metric("High/Critical Risk", int(df["risk_level"].isin(["High", "Critical"]).sum()))
    col4.metric("Avg. Probability", f"{df['probability'].mean()*100:.1f}%")

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        by_disease = df["disease"].value_counts().reset_index()
        by_disease.columns = ["Disease", "Count"]
        fig = px.bar(by_disease, x="Disease", y="Count", color="Disease",
                     title="Predictions by Disease Type")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        by_risk = df["risk_level"].value_counts().reset_index()
        by_risk.columns = ["Risk Level", "Count"]
        color_map = {"Low": "#2ecc71", "Moderate": "#f1c40f", "High": "#e67e22", "Critical": "#e74c3c"}
        fig = px.pie(by_risk, names="Risk Level", values="Count", title="Risk Level Distribution",
                     color="Risk Level", color_discrete_map=color_map)
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Predictions Over Time")
    trend = df.set_index("created_at").resample("D").size().reset_index(name="Count")
    fig = px.line(trend, x="created_at", y="Count", markers=True, title="Daily Prediction Volume")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Raw Prediction Log")
    st.dataframe(
        df[["patient_name", "disease", "result", "probability", "risk_level", "created_at"]]
        .sort_values("created_at", ascending=False),
        use_container_width=True
    )


def _dataset_explorer():
    choice = st.selectbox("Choose a dataset to explore", list(DATASET_PATHS.keys()))
    path = DATASET_PATHS[choice]

    try:
        df = pd.read_csv(path)
    except FileNotFoundError:
        st.error(f"Dataset not found at {path}. Run train_models.py to generate it.")
        return

    st.write(f"**Shape:** {df.shape[0]} rows × {df.shape[1]} columns")
    st.dataframe(df.head(50), use_container_width=True)

    target_col = df.columns[-1]
    col1, col2 = st.columns(2)

    with col1:
        counts = df[target_col].value_counts().reset_index()
        counts.columns = [target_col, "Count"]
        fig = px.bar(counts, x=target_col, y="Count", title=f"Target Distribution ({target_col})")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        numeric_cols = df.select_dtypes(include="number").columns.tolist()
        feature = st.selectbox("Feature to inspect", [c for c in numeric_cols if c != target_col])
        fig = px.histogram(df, x=feature, color=df[target_col].astype(str),
                            title=f"Distribution of {feature}", barmode="overlay", opacity=0.7)
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Correlation Heatmap")
    numeric_df = df.select_dtypes(include="number")
    corr = numeric_df.corr()
    fig = px.imshow(corr, text_auto=".2f", aspect="auto", color_continuous_scale="RdBu_r",
                     title="Feature Correlation Matrix")
    st.plotly_chart(fig, use_container_width=True)
