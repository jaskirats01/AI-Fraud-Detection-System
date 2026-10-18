"""Prediction service for the report edition; preserves the saved classifier."""
from contextlib import asynccontextmanager
import logging
from pathlib import Path
from typing import Annotated, Literal
import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, Field

log = logging.getLogger(__name__)
MODEL_PATH = Path(__file__).resolve().parent / "fraud_detection_model.pkl"
FEATURE_NAMES = ["step", "type", "amount", "oldbalanceOrg", "newbalanceOrig", "oldbalanceDest", "newbalanceDest", "isFlaggedFraud", "balanceDiffOrig", "balanceDiffDest"]
model = None

@asynccontextmanager
async def lifespan(app):
    global model
    try:
        model = joblib.load(MODEL_PATH)
    except Exception:
        model = None
        log.exception("Model could not be loaded")
    yield

app = FastAPI(title="AI Fraud Detection API", version="1.1.0", lifespan=lifespan)
NonNegative = Annotated[float, Field(ge=0, allow_inf_nan=False)]

class Transaction(BaseModel):
    model_config = ConfigDict(extra="forbid")
    step: Annotated[int, Field(ge=0, strict=True)]
    type: Literal[0, 1, 2, 3, 4]
    amount: NonNegative
    oldbalanceOrg: NonNegative
    newbalanceOrig: NonNegative
    oldbalanceDest: NonNegative
    newbalanceDest: NonNegative
    isFlaggedFraud: Literal[0, 1]

def build_features(data):
    values = data.model_dump()
    values["balanceDiffOrig"] = data.oldbalanceOrg - data.newbalanceOrig
    values["balanceDiffDest"] = data.newbalanceDest - data.oldbalanceDest
    return pd.DataFrame([[values[name] for name in FEATURE_NAMES]], columns=FEATURE_NAMES)

@app.get("/")
def home():
    return {"message": "AI Fraud Detection API", "version": "1.1.0"}

@app.get("/health")
def health():
    if model is None:
        raise HTTPException(status_code=503, detail="Prediction model unavailable")
    return {"status": "ready", "features": int(model.n_features_in_), "trees": len(model.estimators_)}

@app.post("/predict")
def predict(data: Transaction):
    if model is None:
        raise HTTPException(status_code=503, detail="Prediction model unavailable")
    try:
        features = build_features(data)
        prediction = int(model.predict(features)[0])
        fraud_index = list(model.classes_).index(1)
        probability = float(model.predict_proba(features)[0][fraud_index])
        return {"prediction": "Fraudulent Transaction" if prediction else "Genuine Transaction", "fraud_probability": round(probability * 100, 2)}
    except Exception:
        log.exception("Prediction failed")
        raise HTTPException(status_code=500, detail="Prediction could not be completed")
