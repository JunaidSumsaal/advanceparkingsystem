import numpy as np
import pandas as pd
from datetime import timedelta
from parking.models import SpotAvailabilityLog, ParkingSpot, Booking

HORIZON_MIN = 5          # minutes into the future to predict
LOOKBACK_MIN = 60        # features look back 60 minutes
STEP_SECONDS = 300       # stride for generating examples


def build_examples_for_spot(
    spot, horizon_min=2, lookback_seconds=15 * 60, step_seconds=300
):
    logs = list(
        SpotAvailabilityLog.objects.filter(
            parking_spot=spot).order_by("timestamp")
    )
    if not logs:
        return pd.DataFrame()

    rows = []
    start = logs[0].timestamp
    end = logs[-1].timestamp
    current = start

    while current + timedelta(minutes=horizon_min) <= end:
        lookback_start = current - timedelta(seconds=lookback_seconds)
        window_logs = [l for l in logs if lookback_start <=
                       l.timestamp < current]

        avail_vals = [1 if l.is_available else 0 for l in window_logs]
        ratio_15m = np.mean(avail_vals[-15:]) if avail_vals else 0.5
        ratio_60m = np.mean(avail_vals[-60:]) if avail_vals else 0.5
        changes = (
            sum(avail_vals[i] != avail_vals[i - 1]
                for i in range(1, len(avail_vals)))
            if avail_vals
            else 0
        )
        last_status = avail_vals[-1] if avail_vals else 1

        active_booking = Booking.objects.filter(
            parking_spot=spot, start_time__lte=current, is_active=True
        ).exists()

        target_time = current + timedelta(minutes=horizon_min)
        future_logs = [l for l in logs if l.timestamp >= target_time]
        if future_logs:
            label = 1 if future_logs[0].is_available else 0
        else:
            label = last_status  # fallback to last known

        rows.append(
            {
                "spot_id": spot.id,
                "timestamp": current,
                "hour": current.hour,
                "dow": current.weekday(),
                "is_weekend": 1 if current.weekday() >= 5 else 0,
                "ratio_15m": ratio_15m,
                "ratio_60m": ratio_60m,
                "changes_last_hour": changes,
                "last_status": last_status,
                "active_booking": 1 if active_booking else 0,
                "label": label,
                "price_per_hour": float(spot.price_per_hour or 0.0),
                "spot_type": spot.spot_type,
            }
        )
        current += timedelta(seconds=step_seconds)

    # 🔹 Fallback: if no rows were generated but logs exist, add 1 row using last status
    if not rows and logs:
        last = logs[-1]
        rows.append(
            {
                "spot_id": spot.id,
                "timestamp": last.timestamp,
                "hour": last.timestamp.hour,
                "dow": last.timestamp.weekday(),
                "is_weekend": 1 if last.timestamp.weekday() >= 5 else 0,
                "ratio_15m": 0.5,
                "ratio_60m": 0.5,
                "changes_last_hour": 0,
                "last_status": 1 if last.is_available else 0,
                "active_booking": 0,
                "label": 1 if last.is_available else 0,
                "price_per_hour": float(spot.price_per_hour or 0.0),
                "spot_type": spot.spot_type,
            }
        )

    return pd.DataFrame(rows)


def build_full_dataset(spots_qs=None) -> pd.DataFrame:
    if spots_qs is None:
        spots_qs = ParkingSpot.objects.all()

    frames = []
    for spot in spots_qs:
        df = build_examples_for_spot(spot)
        if not df.empty:
            frames.append(df)

    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
