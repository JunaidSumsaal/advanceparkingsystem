from django.core.management.base import BaseCommand
from parking.models import SpotPredictionLog, SpotAvailabilityLog, ParkingSpot
from sklearn.metrics import precision_score, recall_score, f1_score
import pandas as pd

class Command(BaseCommand):
    help = "Generate evaluation reports for each spot"

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING("Generating spot evaluation reports..."))

        spots = ParkingSpot.objects.all()
        report = []

        for spot in spots:
            preds = SpotPredictionLog.objects.filter(parking_spot=spot)
            logs = SpotAvailabilityLog.objects.filter(parking_spot=spot)

            if not preds.exists() or not logs.exists():
                continue

            df_preds = pd.DataFrame(list(preds.values("predicted_for_time", "probability")))
            df_logs = pd.DataFrame(list(logs.values("timestamp", "is_available")))

            df = pd.merge_asof(
                df_preds.sort_values("predicted_for_time"),
                df_logs.sort_values("timestamp"),
                left_on="predicted_for_time",
                right_on="timestamp",
                direction="nearest"
            )

            if df.empty:
                continue

            y_true = df["is_available"].astype(int)
            y_pred = (df["probability"] > 0.5).astype(int)

            report.append({
                "spot": spot.name,
                "precision": precision_score(y_true, y_pred, zero_division=0),
                "recall": recall_score(y_true, y_pred, zero_division=0),
                "f1": f1_score(y_true, y_pred, zero_division=0),
            })

        for r in report:
            self.stdout.write(self.style.SUCCESS(
                f"{r['spot']} → precision={r['precision']:.2f}, recall={r['recall']:.2f}, f1={r['f1']:.2f}"
            ))

        self.stdout.write(self.style.SUCCESS("Spot evaluation report completed"))
