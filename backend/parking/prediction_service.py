import math
import logging
from datetime import timedelta
from django.utils import timezone
from .models import SpotAvailabilityLog, SpotPredictionLog

logger = logging.getLogger(__name__)

def compute_probability(spot, lookback_entries=200):
    logs = list(
        SpotAvailabilityLog.objects.filter(parking_spot=spot)
        .order_by("-timestamp")[:lookback_entries]
    )
    if not logs:
        return 0.6 if spot.is_available else 0.3

    total_w = 0.0
    w_sum = 0.0
    for i, log in enumerate(logs):
        w = math.exp(-i / 50.0)
        total_w += w
        w_sum += (1.0 if log.is_available else 0.0) * w

    ratio = (w_sum / total_w) if total_w else 0.0
    prob = 0.7 * ratio + 0.3 * (1.0 if spot.is_available else 0.0)
    return max(0.0, min(1.0, prob))

def predict_spots_nearby(spots, time_ahead_minutes=15):
    results = []
    predicted_for = timezone.now() + timedelta(minutes=time_ahead_minutes)

    for spot in spots:
        try:
            p = compute_probability(spot)
            SpotPredictionLog.objects.create(
                parking_spot=spot,
                probability=p,
                predicted_for_time=predicted_for,
                model_version="v1",
            )
            results.append({"spot": spot, "probability": p, "predicted_for_time": predicted_for})
        except Exception:
            logger.exception("SpotPredictionLog save failed for spot=%s", spot.id)

    results.sort(key=lambda x: x["probability"], reverse=True)
    return results
