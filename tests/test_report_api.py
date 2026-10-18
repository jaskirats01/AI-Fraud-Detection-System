"""Contract and regression checks for the report edition."""
import importlib.util
import json
from pathlib import Path
import unittest
from fastapi.testclient import TestClient
ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("fraud_api", ROOT / "Project/Backend/app.py")
api = importlib.util.module_from_spec(spec)
spec.loader.exec_module(api)
GENUINE = dict(step=1, type=3, amount=9839.64, oldbalanceOrg=170136, newbalanceOrig=160296.36, oldbalanceDest=0, newbalanceDest=0, isFlaggedFraud=0)
FRAUD = dict(step=1, type=4, amount=181, oldbalanceOrg=181, newbalanceOrig=0, oldbalanceDest=0, newbalanceDest=0, isFlaggedFraud=0)
class ContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client_context = TestClient(api.app)
        cls.client = cls.client_context.__enter__()
    @classmethod
    def tearDownClass(cls):
        cls.client_context.__exit__(None, None, None)
    def test_health(self):
        r = self.client.get("/health")
        self.assertEqual(r.status_code, 200)
        self.assertEqual((r.json()["features"], r.json()["trees"]), (10, 200))
    def test_genuine_sample(self):
        r = self.client.post("/predict", json=GENUINE)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json(), {"prediction": "Genuine Transaction", "fraud_probability": 0.0})
    def test_fraud_sample(self):
        r = self.client.post("/predict", json=FRAUD)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json(), {"prediction": "Fraudulent Transaction", "fraud_probability": 99.99})
    def test_negative_value(self):
        self.assertEqual(self.client.post("/predict", json={**GENUINE, "amount": -1}).status_code, 422)
    def test_unknown_type(self):
        self.assertEqual(self.client.post("/predict", json={**GENUINE, "type": 9}).status_code, 422)
    def test_unknown_flag(self):
        self.assertEqual(self.client.post("/predict", json={**GENUINE, "isFlaggedFraud": 2}).status_code, 422)
    def test_missing_field(self):
        data = GENUINE.copy(); data.pop("amount")
        self.assertEqual(self.client.post("/predict", json=data).status_code, 422)
    def test_feature_order_and_values(self):
        x = api.build_features(api.Transaction(**GENUINE))
        self.assertEqual(list(x.columns), api.FEATURE_NAMES)
        self.assertAlmostEqual(x.iloc[0]["balanceDiffOrig"], 9839.64)
        self.assertEqual(x.iloc[0]["balanceDiffDest"], 0)
    def test_non_finite(self):
        data = json.dumps({**GENUINE, "amount": "Infinity"})
        self.assertEqual(self.client.post("/predict", content=data, headers={"content-type":"application/json"}).status_code, 422)
    def test_model_unavailable(self):
        saved = api.model
        try:
            api.model = None
            self.assertEqual(self.client.post("/predict", json=GENUINE).status_code, 503)
            self.assertEqual(self.client.get("/health").status_code, 503)
        finally:
            api.model = saved
if __name__ == "__main__":
    unittest.main(verbosity=2)
