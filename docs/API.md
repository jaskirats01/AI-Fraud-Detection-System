# Prediction API

[Back to README](../README.md)

The model path is resolved relative to the backend module, independently of the working directory. FastAPI exposes interactive documentation at `/docs`.

| Method | Route | Behaviour |
|---|---|---|
| GET | `/` | Returns a service greeting; it is not a model-readiness probe |
| GET | `/health` | Returns model readiness, feature count and tree count; 503 if unavailable |
| POST | `/predict` | Engineers two balance features and returns a prediction |

## Example request

```python
import requests

response = requests.post(
    "http://127.0.0.1:8000/predict",
    json={
        "step": 5,
        "type": 4,
        "amount": 250000.0,
        "oldbalanceOrg": 500000.0,
        "newbalanceOrig": 250000.0,
        "oldbalanceDest": 10000.0,
        "newbalanceDest": 260000.0,
        "isFlaggedFraud": 0,
    },
    timeout=30,
)
response.raise_for_status()
result = response.json()
print(result)
```

The values above are an illustrative request, not a validated fraud case.

## Inputs and output

`step` is the dataset time step. `type` uses the notebook's alphabetic label encoding: `0=CASH_IN`, `1=CASH_OUT`, `2=DEBIT`, `3=PAYMENT`, `4=TRANSFER`. The balance and amount fields are numbers; `isFlaggedFraud` represents an existing flag rather than the target label.

The feature order is `step`, `type`, `amount`, `oldbalanceOrg`, `newbalanceOrig`, `oldbalanceDest`, `newbalanceDest`, `isFlaggedFraud`, `balanceDiffOrig`, `balanceDiffDest`. The last two values are computed by the service.

A successful response contains `prediction` (`Fraudulent Transaction` or `Genuine Transaction`) and `fraud_probability` (positive-class probability multiplied by 100, rounded to two decimal places).

## Current operational behaviour

The schema requires a non-negative integer step, a transaction type from 0 to 4, a flag of 0 or 1, and finite non-negative amounts and balances. Extra fields are rejected. Invalid requests return HTTP 422; an unavailable model returns 503; an unexpected prediction failure returns 500 with a generic message. The successful prediction response retains the original two-field contract.

The Streamlit server calls FastAPI server-to-server, so unrestricted CORS is not enabled. Before exposing this service beyond a demo, add authentication, rate limits and operational monitoring appropriate to the deployment.
