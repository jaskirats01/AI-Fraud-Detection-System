# Development and deployment

[Back to README](../README.md)

## Start-up checks

1. Launch the API from `Project/Backend`, where the model file lives.
2. Request `/health` and confirm that it reports `ready`, 10 features and 200 trees.
3. Open `/docs` and send an example transaction from the [API guide](API.md).
4. Set `FRAUD_API_URL` to `http://127.0.0.1:8000/predict` for local testing; without this override the UI calls the existing hosted backend.
5. Install `requirements-dev.txt` and run `python -m unittest discover -s tests -v`.

## Hosting layout

For the existing Render configuration, use `Project/Backend` as the service root. Its build command installs that directory's requirements; the start command runs `uvicorn app:app --host 0.0.0.0 --port 10000`.

The Streamlit entry point is `Project/Fronttend/app.py`. Keep its requirements available to the chosen Streamlit deployment. If a repository is recreated, check the hosting service's repository binding and webhook rather than assuming the old integration was preserved.

## Troubleshooting

| Symptom | Check |
|---|---|
| Model file not found | The model must be next to `Project/Backend/app.py` |
| Model deserialization/version error | scikit-learn and joblib versions used when training |
| UI reports backend failure | API URL, service availability and response shape |
| API greets but predictions fail | `/health` status and model-loading log |

## Contribution checklist

Keep training and serving feature order synchronized. The current ten checks cover the two labelled notebook examples, feature construction, missing/invalid fields, readiness and model-unavailable behaviour. Those sample predictions are regression checks, not independent performance estimates. Document any new full-data evaluation with its environment and input data hash.
