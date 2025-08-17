import pandas as pd
import numpy as np
from parking.models import SpotAvailabilityLog, ParkingSpot, Booking
from datetime import timedelta

HORIZON_MIN = 5
LOOKBACK_SECONDS = 15 * 60
STEP_SECONDS = 300 

def load_logs_for_spot(spot_id):
    return SpotAvailabilityLog.objects.filter(parking_spot_id=spot_id).order_by('timestamp')

def build_examples_for_spot(spot, horizon_min=HORIZON_MIN, lookback_seconds=LOOKBACK_SECONDS, step_seconds=300):
    logs = list(SpotAvailabilityLog.objects.filter(parking_spot=spot).order_by('timestamp'))
    if not logs:
        return pd.DataFrame()

    rows = []
    start = logs[0].timestamp
    end = logs[-1].timestamp
    current = start

    while current + timedelta(minutes=horizon_min) <= end:
        # Take logs in the last hour, but allow empty
        lookback_start = current - timedelta(seconds=lookback_seconds)
        window_logs = [l for l in logs if lookback_start <= l.timestamp < current]

        avail_vals = [1 if l.is_available else 0 for l in window_logs]
        ratio_15m = np.mean(avail_vals[-15:]) if avail_vals else 0.5   # default neutral
        ratio_60m = np.mean(avail_vals[-60:]) if avail_vals else 0.5
        changes = sum(avail_vals[i] != avail_vals[i - 1] for i in range(1, len(avail_vals))) if avail_vals else 0
        last_status = avail_vals[-1] if avail_vals else 1

        active_booking = Booking.objects.filter(
            parking_spot=spot, start_time__lte=current, is_active=True
        ).exists()

        # Future label — fallback to last known status if no future logs
        target_time = current + timedelta(minutes=horizon_min)
        future_logs = [l for l in logs if l.timestamp >= target_time]
        if future_logs:
            label = 1 if future_logs[0].is_available else 0
        else:
            label = last_status   # fallback

        row = {
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
        rows.append(row)
        current += timedelta(seconds=step_seconds)

    return pd.DataFrame(rows) if rows else pd.DataFrame()



def build_full_dataset(spots_queryset=None):
    if spots_queryset is None:
        spots_queryset = ParkingSpot.objects.all()
    df_list = []
    for spot in spots_queryset:
        df = build_examples_for_spot(spot)
        print(f"Spot {spot.id} ({spot.name}) -> {df.shape[0]} rows")
        if not df.empty:
            df_list.append(df)
    if not df_list:
        print("⚠️ No data generated for any spots")
        return pd.DataFrame()
    return pd.concat(df_list, ignore_index=True)

