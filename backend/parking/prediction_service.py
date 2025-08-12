from datetime import timedelta
from django.utils import timezone
from .models import SpotAvailabilityLog, SpotPredictionLog
import math
import logging

logger = logging.getLogger(__name__)

def compute_mvp_probability(spot, lookback_entries=200):
    """
        Simple heuristic:
            - Use recent availability history (last N logs) to compute availability ratio.
            - Weight recent entries more heavily.
            - Combine with current spot.is_available to nudge score.
        Returns probability in [0,1].
    """
    logs_qs = SpotAvailabilityLog.objects.filter(parking_spot=spot).order_by('-timestamp')[:lookback_entries]
    logs = list(logs_qs)
    if not logs:
        return 0.6 if spot.is_available else 0.3

    total_weight = 0.0
    weighted_sum = 0.0
    for i, log in enumerate(logs):
        weight = math.exp(-i / 50.0)
        total_weight += weight
        weighted_sum += (1.0 if log.is_available else 0.0) * weight

    ratio = weighted_sum / total_weight if total_weight else 0.0

    prob = 0.7 * ratio + 0.3 * (1.0 if spot.is_available else 0.0)

    prob = max(0.0, min(1.0, prob))
    return prob

def predict_spots_nearby(spots, time_ahead_minutes=15):
    """
        For a list/queryset of ParkingSpot objects, produce predictions.
        Returns list of dicts with parking_spot and probability.
        Also writes SpotPredictionLog entries.
    """
    results = []
    predicted_for = timezone.now() + timedelta(minutes=time_ahead_minutes)

    for spot in spots:
        p = compute_mvp_probability(spot)
        try:
            SpotPredictionLog.objects.create(
                parking_spot=spot,
                probability=p,
                predicted_for_time=predicted_for
            )
        except Exception as e:
            logger.exception("Failed to save SpotPredictionLog: %s", e)
        results.append({
            "spot": spot,
            "probability": p,
            "predicted_for_time": predicted_for
        })
    results.sort(key=lambda x: x["probability"], reverse=True)
    return results
