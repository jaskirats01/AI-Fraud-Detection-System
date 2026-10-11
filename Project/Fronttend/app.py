import streamlit as st
import requests

# ==============================
# Page Config
# ==============================

st.set_page_config(
    page_title="AI Fraud Detection System",
    page_icon="🛡️",
    layout="wide"
)

# ==============================
# Custom CSS
# ==============================

st.markdown("""
<style>

.main {
    background-color: #0E1117;
}

.title {
    text-align: center;
    font-size: 52px;
    font-weight: bold;
    color: #00E5FF;
    margin-bottom: 10px;
}

.subtitle {
    text-align: center;
    font-size: 20px;
    color: #CFCFCF;
    margin-bottom: 40px;
}

.stButton>button {
    background: linear-gradient(90deg, #00E5FF, #00B8D4);
    color: black;
    font-size: 18px;
    font-weight: bold;
    border-radius: 14px;
    width: 100%;
    height: 52px;
    border: none;
    transition: 0.3s;
}

.stButton>button:hover {
    color: white;
    transform: scale(1.02);
}

.info-box {
    background-color: #161B22;
    padding: 15px;
    border-radius: 12px;
    border: 1px solid #2A2F3A;
}

</style>
""", unsafe_allow_html=True)

# ==============================
# Session State Defaults
# ==============================

default_values = {
    "step": 5,
    "type": (4, "TRANSFER"),
    "amount": 250000.0,
    "oldbalanceOrg": 500000.0,
    "newbalanceOrig": 250000.0,
    "oldbalanceDest": 10000.0,
    "newbalanceDest": 260000.0,
    "isFlaggedFraud": 0
}

for key, value in default_values.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ==============================
# Title
# ==============================

st.markdown(
    '<p class="title">AI Fraud Detection System</p>',
    unsafe_allow_html=True
)

st.markdown(
    '<p class="subtitle">Detect suspicious financial transactions using Machine Learning</p>',
    unsafe_allow_html=True
)

# ==============================
# Labelled Demo Transactions
# ==============================

# Source labels: FraudDetection.ipynb, df.head() rows 0 (genuine) and 2 (fraud).
# These examples populate inputs only; the API independently predicts the result.
DEMO_TRANSACTIONS = {
    "genuine": {
        "step": 1,
        "type": (3, "PAYMENT"),
        "amount": 9839.64,
        "oldbalanceOrg": 170136.0,
        "newbalanceOrig": 160296.36,
        "oldbalanceDest": 0.0,
        "newbalanceDest": 0.0,
        "isFlaggedFraud": 0,
    },
    "fraud": {
        "step": 1,
        "type": (4, "TRANSFER"),
        "amount": 181.0,
        "oldbalanceOrg": 181.0,
        "newbalanceOrig": 0.0,
        "oldbalanceDest": 0.0,
        "newbalanceDest": 0.0,
        "isFlaggedFraud": 0,
    },
}


def load_demo(kind):
    st.session_state.update(DEMO_TRANSACTIONS[kind])


demo_genuine, demo_fraud = st.columns(2)
with demo_genuine:
    st.button("Generate Genuine Demo", on_click=load_demo, args=("genuine",))
with demo_fraud:
    st.button("Generate Fraud Demo", on_click=load_demo, args=("fraud",))

st.caption("Load a labelled sample transaction, then click Predict Transaction Fraud.")

# ==============================
# Layout
# ==============================

col1, col2 = st.columns(2)

# ==============================
# LEFT COLUMN
# ==============================

with col1:

    step = st.number_input(
        "Step (Hour) ⓘ",
        min_value=0,
        key="step",
        help="Represents the hour at which the transaction occurred during the 30-day simulation."
    )

    transaction_type = st.selectbox(
        "Transaction Type ⓘ",
        [
            (0, "CASH-IN"),
            (1, "CASH-OUT"),
            (2, "DEBIT"),
            (3, "PAYMENT"),
            (4, "TRANSFER")
        ],
        key="type",
        format_func=lambda x: x[1],
        help="Type of financial transaction being performed."
    )

    amount = st.number_input(
        "Transaction Amount ⓘ",
        min_value=0.0,
        key="amount",
        help="The amount of money being transferred in the transaction."
    )

    oldbalanceOrg = st.number_input(
        "Sender Old Balance ⓘ",
        min_value=0.0,
        key="oldbalanceOrg",
        help="Account balance of the sender before the transaction."
    )

# ==============================
# RIGHT COLUMN
# ==============================

with col2:

    newbalanceOrig = st.number_input(
        "Sender New Balance ⓘ",
        min_value=0.0,
        key="newbalanceOrig",
        help="Account balance of the sender after the transaction."
    )

    oldbalanceDest = st.number_input(
        "Receiver Old Balance ⓘ",
        min_value=0.0,
        key="oldbalanceDest",
        help="Receiver account balance before receiving money."
    )

    newbalanceDest = st.number_input(
        "Receiver New Balance ⓘ",
        min_value=0.0,
        key="newbalanceDest",
        help="Receiver account balance after receiving money."
    )

    isFlaggedFraud = st.selectbox(
        "Flagged Fraud ⓘ",
        [0, 1],
        key="isFlaggedFraud",
        help="Indicates whether the transaction was already flagged as suspicious by existing systems."
    )

# ==============================
# Prediction Button
# ==============================

st.markdown("##")

if st.button("Predict Transaction Fraud"):

    data = {
        "step": step,
        "type": transaction_type[0],
        "amount": amount,
        "oldbalanceOrg": oldbalanceOrg,
        "newbalanceOrig": newbalanceOrig,
        "oldbalanceDest": oldbalanceDest,
        "newbalanceDest": newbalanceDest,
        "isFlaggedFraud": isFlaggedFraud
    }

    API_URL = "https://ai-fraud-detection-system-fyta.onrender.com/predict"

    try:

        response = requests.post(API_URL, json=data)

        if response.status_code == 200:

            result = response.json()

            prediction = result["prediction"]

            probability = result["fraud_probability"]

            st.markdown("---")

            if prediction == "Fraudulent Transaction":

                st.error(f"⚠️ {prediction}")

            else:

                st.success(f"✅ {prediction}")

            st.metric(
                "Fraud Probability",
                f"{probability}%"
            )

        else:

            st.error("❌ API Error")

    except Exception as e:

        st.error("❌ Backend connection failed")
        st.write(e)
