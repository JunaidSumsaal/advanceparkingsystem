import pandas as pd
from .models import SpotAvailabilityLog
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import joblib

def prepare_training_data():
    logs = SpotAvailabilityLog.objects.all().values(
        "parking_spot__latitude",
        "parking_spot__longitude",
        "parking_spot__spot_type",
        "is_available",
        "timestamp"
    )
    df = pd.DataFrame(logs)
    df['hour'] = df['timestamp'].dt.hour
    df['day_of_week'] = df['timestamp'].dt.dayofweek
    df['spot_type'] = df['spot_type'].map({'public': 0, 'private': 1})
    return df
