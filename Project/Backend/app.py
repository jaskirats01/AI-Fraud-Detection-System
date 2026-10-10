# from fastapi import FastAPI
# from pydantic import BaseModel
# from fastapi.middleware.cors import CORSMiddleware
# import numpy as np
# import joblib

# # Load trained model
# model = joblib.load("fraud_detection_model.pkl")

# app = FastAPI(title="Fraud Detection API")

# # Enable CORS
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Input schema
# class Transaction(BaseModel):
#     step: int
#     type: int
#     amount: float
#     oldbalanceOrg: float
#     newbalanceOrig: float
#     oldbalanceDest: float
#     newbalanceDest: float
#     isFlaggedFraud: int

# @app.get("/")
# def home():
#     return {
#         "message": "Fraud Detection API Running"
#     }

# @app.post("/predict")
# def predict(data: Transaction):

#     # Feature engineering
#     balanceDiffOrig = data.oldbalanceOrg - data.newbalanceOrig
#     balanceDiffDest = data.newbalanceDest - data.oldbalanceDest

#     # Model input
#     features = np.array([[
#         data.step,
#         data.type,
#         data.amount,
#         data.oldbalanceOrg,
#         data.newbalanceOrig,
#         data.oldbalanceDest,
#         data.newbalanceDest,
#         data.isFlaggedFraud,
#         balanceDiffOrig,
#         balanceDiffDest
#     ]])

#     # Prediction
#     prediction = model.predict(features)[0]

#     # Probability
#     probability = model.predict_proba(features)[0][1]

#     result = (
#         "Fraudulent Transaction"
#         if prediction == 1
#         else "Genuine Transaction"
#     )

#     return {
#         "prediction": result,
#         "fraud_probability": round(float(probability) * 100, 2)
#     }
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
import joblib

# ==============================
# Initialize FastAPI App
# ==============================

app = FastAPI(
    title="AI Fraud Detection API",
    description="Machine Learning API for detecting fraudulent financial transactions",
    version="1.0"
)

# ==============================
# Enable CORS
# ==============================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==============================
# Load Trained Model
# ==============================

try:
    model = joblib.load("fraud_detection_model.pkl")
    print("✅ Model loaded successfully")

except Exception as e:
    print("❌ Model loading error:", e)

# ==============================
# Request Schema
# ==============================

class Transaction(BaseModel):
    step: int
    type: int
    amount: float
    oldbalanceOrg: float
    newbalanceOrig: float
    oldbalanceDest: float
    newbalanceDest: float
    isFlaggedFraud: int

# ==============================
# Root Endpoint
# ==============================

@app.get("/")
def home():

    return {
        "message": "🚀 AI Fraud Detection API Running Successfully"
    }

# ==============================
# Prediction Endpoint
# ==============================

@app.post("/predict")
def predict(data: Transaction):

    try:

        # Feature Engineering
        balanceDiffOrig = (
            data.oldbalanceOrg - data.newbalanceOrig
        )

        balanceDiffDest = (
            data.newbalanceDest - data.oldbalanceDest
        )

        # Prepare Features
        features = np.array([[
            data.step,
            data.type,
            data.amount,
            data.oldbalanceOrg,
            data.newbalanceOrig,
            data.oldbalanceDest,
            data.newbalanceDest,
            data.isFlaggedFraud,
            balanceDiffOrig,
            balanceDiffDest
        ]])

        # Prediction
        prediction = model.predict(features)[0]

        # Probability
        probability = model.predict_proba(features)[0][1]

        # Result Label
        result = (
            "Fraudulent Transaction"
            if prediction == 1
            else "Genuine Transaction"
        )

        return {
            "prediction": result,
            "fraud_probability": round(float(probability) * 100, 2)
        }

    except Exception as e:

        return {
            "error": str(e)
        }

# ==============================
# Run Application
# ==============================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )