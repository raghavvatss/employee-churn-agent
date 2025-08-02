import streamlit as st
import pandas as pd
import joblib

from utils.preprocess import preprocess_input
from utils.notify import send_email

# Load your trained model
model = joblib.load("model/churn_model.pkl")

st.title("🧠 Employee Churn Prediction")
st.markdown("Upload a CSV file to predict which employees are at risk of leaving.")

# Step 1: Upload CSV
file = st.file_uploader("Upload Employee Data CSV", type=["csv"])

if file:
    df = pd.read_csv(file)
    st.subheader("Preview:")
    st.dataframe(df)

    if st.button("Predict Churn"):
        processed = preprocess_input(df)
        probs = model.predict_proba(processed)[:, 1]

        df["churn_prob"] = probs
        df["risk_level"] = df["churn_prob"].apply(
            lambda p: "High Risk" if p > 0.7 else "Medium Risk" if p > 0.4 else "Low Risk"
        )
        df["action"] = df["risk_level"].map({
            "High Risk": "Schedule retention interview",
            "Medium Risk": "Monitor closely",
            "Low Risk": "No action needed"
        })

        st.success("✅ Prediction Done")
        st.dataframe(df)

        # Send Emails
        if st.button("Send Alert Emails"):
            for index, row in df.iterrows():
                if row["risk_level"] != "Low Risk":
                    subject = f"[Churn Risk Alert] Employee {index} - {row['risk_level']}"
                    body = f"""
Employee {index} is at {row['risk_level']} of attrition.
Churn probability: {row['churn_prob']:.2f}
Recommended Action: {row['action']}
"""
                    send_email(subject, body)
            st.success("📩 Emails sent for high/medium-risk employees.")
