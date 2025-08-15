from parking.models import SpotPredictionLog, SpotAvailabilityLog
from sklearn.metrics import roc_auc_score, brier_score_loss
import pandas as pd
from datetime import timedelta


def evaluate_predictions(tolerance_seconds=120):
    preds = SpotPredictionLog.objects.all()
    rows = []
    for p in preds:
        t = p.predicted_for_time
        logs = SpotAvailabilityLog.objects.filter(
            parking_spot=p.parking_spot,
            timestamp__gte=t - timedelta(seconds=tolerance_seconds),
            timestamp__lte=t + timedelta(seconds=tolerance_seconds)
        ).order_by('timestamp')
        if not logs.exists():
            continue
        actual = 1 if logs.first().is_available else 0
        rows.append({"prob": p.probability, "actual": actual})

    df = pd.DataFrame(rows)
    if df.empty:
        print("No matching logs for evaluation")
        return None

    auc = roc_auc_score(df["actual"], df["prob"])
    brier = brier_score_loss(df["actual"], df["prob"])
    print(f"AUC={auc:.4f} Brier={brier:.4f}")

    return {"auc": auc, "brier": brier}
