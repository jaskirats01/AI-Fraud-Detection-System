"""Report edition of the transaction review interface using the real prediction API."""
import json
import os
import time
import pandas as pd
import requests
import streamlit as st

API_URL = os.getenv("FRAUD_API_URL", "https://ai-fraud-detection-system-fyta.onrender.com/predict")
TYPES = {"CASH_IN": 0, "CASH_OUT": 1, "DEBIT": 2, "PAYMENT": 3, "TRANSFER": 4}
SAMPLES = {
    "genuine": dict(step=1, transaction_type="PAYMENT", amount=9839.64, oldbalanceOrg=170136.0,
                    newbalanceOrig=160296.36, oldbalanceDest=0.0, newbalanceDest=0.0, isFlaggedFraud=0),
    "fraud": dict(step=1, transaction_type="TRANSFER", amount=181.0, oldbalanceOrg=181.0,
                  newbalanceOrig=0.0, oldbalanceDest=0.0, newbalanceDest=0.0, isFlaggedFraud=0),
}
st.set_page_config(page_title="AI Fraud Detection | Transaction Review", page_icon="◈", layout="wide")
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {background:#0a111e;}
[data-testid="stHeader"] {background:rgba(10,17,30,.94);}
.block-container {max-width:1440px;padding:4.4rem 2.8rem 2rem;}
h1,h2,h3 {letter-spacing:-.03em;}
.eyebrow {font-size:11px;letter-spacing:.18em;font-weight:700;color:#65dcc2;margin-bottom:12px;}
.hero h1 {font-size:38px;margin:0 0 6px;color:#f4f7fc;line-height:1.15;}
.hero p {color:#9aabc1;font-size:15px;margin:0 0 20px;}
.stats {display:flex;border-top:1px solid #233149;border-bottom:1px solid #233149;padding:16px 0;margin:8px 0 24px;}
.stat {flex:1;border-right:1px solid #233149;padding-left:24px;}.stat:first-child {padding-left:0;}.stat:last-child {border:0;}
.stat strong {font-size:25px;font-weight:650;color:#eef4ff;display:block;line-height:1.2;}
.stat span {font-size:11px;color:#8ea1bc;letter-spacing:.06em;text-transform:uppercase;}
[data-testid="stForm"] {background:#101b2d;border:1px solid #26354c;border-radius:14px;padding:20px;}
.panel-title {font-size:19px;font-weight:600;color:#f0f5fc;margin:0 0 3px;}
.panel-sub {color:#8ea1bc;font-size:12px;margin:0 0 16px;}
.group-label {font-size:11px;letter-spacing:.11em;color:#8ea1bc;margin:9px 0 8px;}
.stButton button {border-radius:8px;font-weight:600;}
[data-testid="stFormSubmitButton"] button {background:#63ddc0;color:#061c18;border:0;font-weight:750;min-height:44px;}
.result {min-height:264px;padding:24px;border:1px solid #2a3b54;border-radius:14px;background:#111e31;}
.result.genuine {border-color:#237263;background:linear-gradient(135deg,#11352f,#112132);}
.result.fraud {border-color:#8f4759;background:linear-gradient(135deg,#3e202d,#172035);}
.result .label {font-size:11px;text-transform:uppercase;letter-spacing:.12em;color:#9eb2cc;}
.result h2 {font-size:26px;line-height:1.2;margin:13px 0 20px;}
.result .score {font-size:52px;line-height:1;color:#eef6ff;font-weight:650;letter-spacing:-.05em;}
.result .note {color:#afbdd0;font-size:12px;line-height:1.55;margin-top:16px;}
.meter {height:6px;background:#26364e;border-radius:5px;margin-top:15px;overflow:hidden;}.meter div {height:100%;background:#63ddc0;}.fraud .meter div {background:#ff8ca2;}
.feature {margin-top:14px;padding:16px 20px;border-radius:12px;border:1px solid #26354c;background:#0d1829;}
.feature .row {display:flex;justify-content:space-between;padding:7px 0;font-size:13px;color:#b6c4d6;}.feature b {color:#e5edf9;}
.footer {font-size:11px;color:#71849e;border-top:1px solid #233149;margin-top:23px;padding-top:14px;}
[data-testid="stMetricValue"] {font-size:30px;}
@media(min-width:480px) {
  [data-testid="stForm"] [data-testid="stHorizontalBlock"] {flex-wrap:nowrap!important;}
  [data-testid="stForm"] [data-testid="stColumn"] {min-width:0!important;flex:1 1 0!important;width:auto!important;}
}
@media(max-width:750px) {.block-container{padding:4.4rem 1rem 1.5rem;}.hero h1{font-size:30px;}.stat{padding-left:10px}.stat strong{font-size:21px}.stat span{font-size:9px}}
</style>
""", unsafe_allow_html=True)
for k, v in SAMPLES["genuine"].items():
    st.session_state.setdefault(k, v)

def load_sample(kind):
    st.session_state.update(SAMPLES[kind])
    st.session_state.pop("analysis", None)

st.markdown('<div class="hero"><div class="eyebrow">JASKIRAT SINGH / MACHINE LEARNING PROJECT</div><h1>AI Fraud Detection</h1><p>Inspect a transaction. Understand the inputs. Review the model decision.</p></div>', unsafe_allow_html=True)
st.markdown('<div class="stats"><div class="stat"><strong>6.36M</strong><span>Dataset transactions</span></div><div class="stat"><strong>0.13%</strong><span>Fraud in source data</span></div><div class="stat"><strong>10</strong><span>Model features</span></div><div class="stat"><strong>200</strong><span>Decision trees</span></div></div>', unsafe_allow_html=True)
review, performance, guide = st.tabs(["Transaction review", "Model evaluation", "How it works"])
with review:
    left, right = st.columns([1.65, 1], gap="large")
    with left:
        a, b = st.columns(2)
        a.button("Load genuine sample", on_click=load_sample, args=("genuine",), use_container_width=True)
        b.button("Load fraud sample", on_click=load_sample, args=("fraud",), use_container_width=True)
        st.caption("Labelled notebook examples. The API calculates each prediction independently.")
        with st.form("transaction_form"):
            st.markdown('<div class="panel-title">Transaction details</div><div class="panel-sub">Enter amounts in the dataset\'s monetary units.</div>', unsafe_allow_html=True)
            a, b, c = st.columns([1, 1.25, 1.35])
            a.number_input("Step (hour)", min_value=0, step=1, key="step", help="Hour index in the dataset; not an hour-of-day value.")
            b.selectbox("Transaction type", list(TYPES), key="transaction_type")
            c.number_input("Amount", min_value=0.0, step=1.0, format="%.2f", key="amount")
            st.markdown('<div class="group-label">ACCOUNT BALANCES</div>', unsafe_allow_html=True)
            a, b = st.columns(2)
            a.number_input("Sender before", min_value=0.0, format="%.2f", key="oldbalanceOrg")
            b.number_input("Sender after", min_value=0.0, format="%.2f", key="newbalanceOrig")
            a.number_input("Receiver before", min_value=0.0, format="%.2f", key="oldbalanceDest")
            b.number_input("Receiver after", min_value=0.0, format="%.2f", key="newbalanceDest")
            st.selectbox("Existing rule flag", [0, 1], format_func=lambda x: "Not flagged (0)" if x == 0 else "Flagged (1)", key="isFlaggedFraud", help="An existing rule flag; separate from the target fraud label.")
            submitted = st.form_submit_button("Analyse transaction", use_container_width=True)
        payload = {k: st.session_state[k] for k in SAMPLES["genuine"] if k != "transaction_type"}
        payload["type"] = TYPES[st.session_state.transaction_type]
        if submitted:
            st.session_state.pop("analysis", None)
            try:
                start = time.perf_counter()
                with st.spinner("Running model prediction..."):
                    response = requests.post(API_URL, json=payload, timeout=30)
                    response.raise_for_status()
                result = response.json()
                probability = float(result["fraud_probability"])
                if not 0 <= probability <= 100 or result["prediction"] not in ("Genuine Transaction", "Fraudulent Transaction"):
                    raise ValueError("Invalid prediction response")
                st.session_state.analysis = dict(result=result, payload=payload.copy(), seconds=time.perf_counter()-start)
            except (requests.RequestException, ValueError, KeyError):
                st.error("Prediction unavailable. Check that the API is running, then try again.")
    with right:
        analysis = st.session_state.get("analysis")
        if analysis:
            result = analysis["result"]
            probability = float(result["fraud_probability"])
            fraud = result["prediction"] == "Fraudulent Transaction"
            css = "fraud" if fraud else "genuine"
            title = "Fraudulent transaction" if fraud else "Genuine transaction"
            st.markdown(f'<div class="result {css}"><div class="label">Model decision / completed</div><h2>{title}</h2><div class="score">{probability:.2f}%</div><div class="label" style="margin-top:9px">Fraud probability score</div><div class="meter"><div style="width:{max(probability,0.4)}%"></div></div><div class="note">Prediction from the saved Random Forest model.<br>Score applies to the last submitted transaction.</div></div>', unsafe_allow_html=True)
            st.caption(f"Request completed in {analysis['seconds']:.2f} s · Single local observation")
            shown = analysis["payload"]
        else:
            shown = payload
            st.markdown('<div class="result"><div class="label">Model decision</div><h2>Ready to analyse</h2><div class="score" style="font-size:40px">Your next check</div><div class="note">Choose a sample or enter transaction details, then select Analyse transaction.</div></div>', unsafe_allow_html=True)
        sender = shown["oldbalanceOrg"] - shown["newbalanceOrig"]
        receiver = shown["newbalanceDest"] - shown["oldbalanceDest"]
        st.markdown(f'<div class="feature"><div class="group-label">ENGINEERED BALANCE FEATURES</div><div class="row"><span>Sender decrease</span><b>{sender:,.2f}</b></div><div class="row"><span>Receiver increase</span><b>{receiver:,.2f}</b></div><div class="panel-sub" style="margin:9px 0 0">Calculated from displayed or last submitted balances. A difference alone does not establish fraud.</div></div>', unsafe_allow_html=True)
        if analysis:
            st.download_button("Download prediction JSON", json.dumps(analysis, indent=2), "transaction-prediction.json", "application/json", use_container_width=True)
with performance:
    st.subheader("What the saved test results show")
    st.caption("Source: FraudDetection.ipynb · 1,272,524 test transactions · Original stratified 80/20 split")
    a, b, c, d = st.columns(4)
    a.metric("Fraud recall", "98.23%")
    b.metric("Fraud precision", "32.06%")
    c.metric("Fraud F1 score", "48.34%")
    d.metric("Overall accuracy", "99.73%")
    st.write("The model detected 1,614 of 1,643 fraud cases. It also flagged 3,421 genuine transactions. High recall therefore comes with a substantial review workload.")
    st.dataframe(pd.DataFrame([[1267460, 3421], [29, 1614]], index=["Actual genuine", "Actual fraud"], columns=["Predicted genuine", "Predicted fraud"]), use_container_width=True)
    st.markdown("#### Why accuracy is not enough")
    st.write("Predicting genuine for every test transaction would score about 99.87% accuracy and detect no fraud. Fraud recall, precision and the confusion matrix make the trade-off visible.")
    st.info("These figures come from saved notebook outputs. This interface does not retrain the model or rerun the full test set.")
with guide:
    st.subheader("From transaction to prediction")
    st.write("1. Enter eight transaction fields.\n2. The API validates types, allowed categories and non-negative values.\n3. Two balance-change features are computed.\n4. The saved 200-tree Random Forest predicts a label and score.\n5. Review the result and export the prediction if needed.")
    st.markdown("#### The two engineered features")
    st.code("balanceDiffOrig = oldbalanceOrg - newbalanceOrig\nbalanceDiffDest = newbalanceDest - oldbalanceDest", language="python")
    st.write("Training used SMOTE only on the training partition. New account balances are post-transaction inputs, so this application demonstrates retrospective transaction classification.")
    st.caption("No account identifiers are required. Transaction history is not persisted by this interface.")
st.markdown('<div class="footer">Individual internship project · TECHEONN · Python / scikit-learn / FastAPI / Streamlit<br>Portfolio demonstration. Model estimates are not calibrated banking risk scores.</div>', unsafe_allow_html=True)
