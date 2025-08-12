import joblib
import os
from django.conf import settings
from parking.models import ParkingSpot
from datetime import datetime, timedelta
import math

MODEL_PATH = os.path.join(settings.BASE_DIR, "parking", "ml", "model", "rf_spot_predictor.joblib")
_model = None

def load_model():
    global _model
    if _model is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError("Model not found, run training first")
        _model = joblib.load(MODEL_PATH)
    return _model

def predict_for_spots(spots, user_lat=None, user_lng=None):
    # sourcery skip: aware-datetime-for-utc, for-append-to-extend, list-comprehension
    model = load_model()
    rows = []
    spot_map = []
    for s in spots:
        row = {
            "spot_type": s.spot_type,
            "hour": datetime.utcnow().hour,
            "dow": datetime.utcnow().weekday(),
            "is_weekend": 1 if datetime.utcnow().weekday() >= 5 else 0,
            "ratio_15m": 0.5,
            "ratio_60m": 0.5,
            "changes_last_hour": 0,
            "last_status": 1 if s.is_available else 0,
            "active_booking": 0,
            "price_per_hour": float(s.price_per_hour or 0.0)
        }
        rows.append(row)
        spot_map.append(s)
    import pandas as pd
    X = pd.DataFrame(rows)
    probs = model.predict_proba(X)[:, 1]
    results = []
    for s, p in zip(spot_map, probs):
        results.append({"spot": s, "probability": float(p)})
    results.sort(key=lambda x: x["probability"], reverse=True)
    return results
