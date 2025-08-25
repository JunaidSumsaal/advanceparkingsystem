import os
import joblib
import pandas as pd
from datetime import timedelta
from django.utils import timezone
from django.conf import settings
from parking.models import SpotAvailabilityLog, Booking

MODEL_PATH = os.path.join(settings.BASE_DIR, "parking",
                          "ml", "model", "rf_spot_predictor.joblib")
_model = None

CAT_COLS = ["spot_type"]
NUM_COLS = ["hour", "dow", "is_weekend", "ratio_15m", "ratio_60m",
            "changes_last_hour", "last_status", "active_booking", "price_per_hour"]
FEATURES = CAT_COLS + NUM_COLS


def _load_model():
    global _model
    if _model is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError("Model not found. Train the model first.")
        _model = joblib.load(MODEL_PATH)
    return _model


def _recent_features(spot, now=None):
    now = now or timezone.now()
    t60 = now - timedelta(minutes=60)
    t15 = now - timedelta(minutes=15)
    logs = list(
        SpotAvailabilityLog.objects.filter(
            parking_spot=spot, timestamp__gte=t60, timestamp__lt=now
        ).order_by("timestamp")
    )
    vals = [1 if l.is_available else 0 for l in logs]
    ratio_60 = float(sum(vals) / len(vals)) if vals else 0.5
    ratio_15 = float(sum(v for (v, l) in zip(vals[-len(vals):], logs[-len(vals):]) if l.timestamp >= t15)) / \
        float(sum(1 for l in logs if l.timestamp >= t15)) if logs and any(
            l.timestamp >= t15 for l in logs) else 0.5
    # simpler/robust:
    if logs:
        seq = vals
        last_status = seq[-1]
        changes = sum(seq[i] != seq[i - 1] for i in range(1, len(seq)))
    else:
        last_status = 1 if spot.is_available else 0
        changes = 0

    active_booking = Booking.objects.filter(
        parking_spot=spot, is_active=True).exists()

    return {
        "spot_type": spot.spot_type,
        "hour": now.hour,
        "dow": now.weekday(),
        "is_weekend": 1 if now.weekday() >= 5 else 0,
        "ratio_15m": ratio_15,
        "ratio_60m": ratio_60,
        "changes_last_hour": changes,
        "last_status": last_status,
        "active_booking": 1 if active_booking else 0,
        "price_per_hour": float(spot.price_per_hour or 0.0),
    }


def predict_for_spots(spots, top_n=None):
    model = _load_model()
    now = timezone.now()
    rows, mapping = [], []
    for s in spots:
        rows.append(_recent_features(s, now))
        mapping.append(s)

    if not rows:
        return []

    X = pd.DataFrame(rows, columns=FEATURES)
    probs = model.predict_proba(X)[:, 1]

    results = [{"spot": s, "probability": float(
        p)} for s, p in zip(mapping, probs)]
    results.sort(key=lambda x: x["probability"], reverse=True)
    return results[:top_n] if top_n else results
