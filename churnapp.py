import streamlit as st
import pandas as pd
import joblib
import utils.notify
from utils.notify import send_email



# Load the model
model = joblib.load("model/churn_model.pkl")

# Define thresholds and actions
def get_risk_level(prob):
    if prob > 0.6:
        return "High Risk"
    elif prob > 0.3:
        return "Moderate Risk"
    else:
        return "Low Risk"

def get_recommended_action(risk):
    return {
        "High Risk": "Immediate HR intervention required.",
        "Moderate Risk": "Schedule one-on-one discussion.",
        "Low Risk": "No action needed."
    }.get(risk, "No action needed.")

# Streamlit App UI
st.title("📉 Employee Churn Risk Dashboard")
st.write("Upload an employee data CSV to assess churn risks and notify HR for intervention.")

uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.write("Uploaded Data:")
    st.dataframe(df)

    # Preprocessing: (Assume your model expects the same order and columns)
    # Replace this with your actual preprocessing
    X = df[["age", "salary", "tenure", "performance", "project_hours"]].copy()

    # Encode performance (example)
    X["performance"] = X["performance"].map({"Low": 0, "Average": 1, "High": 2})

    # Predict churn probability
    churn_probs = model.predict_proba(X)[:, 1]
    df["churn_prob"] = churn_probs
    df["risk_level"] = df["churn_prob"].apply(get_risk_level)
    df["action"] = df["risk_level"].apply(get_recommended_action)

    # Show results
    st.subheader("🧠 Prediction Results")
    st.dataframe(df[["churn_prob", "risk_level", "action"]])

    # Email Alerts
    st.subheader("📧 Sending Alerts...")
    for index, row in df.iterrows():
        if row["risk_level"] != "Low Risk":
            subject = f"[Churn Risk Alert] Employee {index} - {row['risk_level']}"
            body = f"""
            Employee {index} is at {row['risk_level']} of attrition.
            Churn probability: {row['churn_prob']:.2f}
            Recommended Action: {row['action']}
            """
            send_email(subject, body)
            st.warning(f"Email sent for Employee {index} ({row['risk_level']}) ✅")

    st.success("✅ All done!")

