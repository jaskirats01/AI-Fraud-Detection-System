# Prediction API

[Back to README](../README.md)

Run from `Project/Backend` so the relative model path resolves. FastAPI exposes interactive documentation at `/docs`.

| Method | Route | Behaviour |
|---|---|---|
| GET | `/` | Returns a service greeting; it is not a model-readiness probe |
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
if "error" in result:
    raise RuntimeError(result["error"])
print(result)
```

The values above are an illustrative request, not a validated fraud case.

## Inputs and output

`step` is the dataset time step. `type` uses the notebook's alphabetic label encoding: `0=CASH_IN`, `1=CASH_OUT`, `2=DEBIT`, `3=PAYMENT`, `4=TRANSFER`. The balance and amount fields are numbers; `isFlaggedFraud` represents an existing flag rather than the target label.

The feature order is `step`, `type`, `amount`, `oldbalanceOrg`, `newbalanceOrig`, `oldbalanceDest`, `newbalanceDest`, `isFlaggedFraud`, `balanceDiffOrig`, `balanceDiffDest`. The last two values are computed by the service.

A successful response contains `prediction` (`Fraudulent Transaction` or `Genuine Transaction`) and `fraud_probability` (positive-class probability multiplied by 100, rounded to two decimal places).

## Current operational behaviour

The schema checks Python-compatible types but does not constrain transaction categories, flags or negative amounts. Prediction exceptions currently return an `error` object with HTTP 200. Model-loading exceptions are logged at startup; the greeting can still respond even when prediction is unavailable. Callers should therefore check both status and response shape.

Before exposing this service beyond a demo, add field bounds, intentional CORS origins, authentication/rate limits where needed, structured error handling and model-readiness monitoring.
