# Development and deployment

[Back to README](../README.md)

## Start-up checks

1. Launch the API from `Project/Backend`, where the model file lives.
2. Confirm the startup log reports that the model loaded.
3. Open `/docs` and send an example transaction from the [API guide](API.md).
4. Check the UI's `API_URL` before testing; it defaults to the hosted backend.

## Hosting layout

For the existing Render configuration, use `Project/Backend` as the service root. Its build command installs that directory's requirements; the start command runs `uvicorn app:app --host 0.0.0.0 --port 10000`.

The Streamlit entry point is `Project/Fronttend/app.py`. Keep its requirements available to the chosen Streamlit deployment. If a repository is recreated, check the hosting service's repository binding and webhook rather than assuming the old integration was preserved.

## Troubleshooting

| Symptom | Check |
|---|---|
| Model file not found | Current working directory and backend model path |
| Model deserialization/version error | scikit-learn and joblib versions used when training |
| UI reports backend failure | API URL, service availability and response shape |
| API greets but predictions fail | Model startup log; the root endpoint does not validate readiness |

## Contribution checklist

Keep training and serving feature order synchronized. Add tests for invalid inputs and the prediction response when changing the API. Use synthetic examples in tests, document measured results with their environment, and make focused commits describing the behaviour changed.
