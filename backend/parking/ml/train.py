import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import roc_auc_score, brier_score_loss, precision_score
from parking.ml.data_prep import build_full_dataset
from django.conf import settings
import os

MODEL_DIR = os.path.join(settings.BASE_DIR, "parking", "ml", "model")
os.makedirs(MODEL_DIR, exist_ok=True)
MODEL_PATH = os.path.join(MODEL_DIR, "rf_spot_predictor.joblib")

def time_train_test_split(df, time_col="timestamp", test_fraction=0.2):
    if df.empty:
        return pd.DataFrame(), pd.DataFrame()
    df_sorted = df.sort_values(time_col)
    cutoff_index = int(len(df_sorted) * (1 - test_fraction))
    if cutoff_index == 0 or cutoff_index >= len(df_sorted):
        return df_sorted, pd.DataFrame()
    train = df_sorted.iloc[:cutoff_index]
    test = df_sorted.iloc[cutoff_index:]
    return train, test

def train_and_save():
    print("🚀 Starting model training...")
    df = build_full_dataset()
    print(f"📊 Dataset built: {df.shape[0]} rows, {df.shape[1]} cols")

    if df.empty:
        print("❌ No data to train on")
        return

    cat_cols = ["spot_type"]
    num_cols = [
        "hour", "dow", "is_weekend",
        "ratio_15m", "ratio_60m", "changes_last_hour",
        "last_status", "active_booking", "price_per_hour"
    ]
    features = cat_cols + num_cols

    train, test = time_train_test_split(df, "timestamp", test_fraction=0.2)
    if train.empty or test.empty:
        print("⚠️ Not enough data for train/test split")
        return

    X_train, y_train = train[features], train["label"]
    X_test, y_test = test[features], test["label"]

    print(f"🔹 Train size={len(train)}, Test size={len(test)}")
    print(f"🔹 Train labels balance: {y_train.value_counts().to_dict()}")
    print(f"🔹 Test labels balance: {y_test.value_counts().to_dict()}")

    preprocessor = ColumnTransformer([
        ("cat", OneHotEncoder(handle_unknown="ignore"), cat_cols),
    ], remainder="passthrough")

    clf = RandomForestClassifier(n_estimators=200, n_jobs=-1, random_state=42)
    pipeline = Pipeline([("pre", preprocessor), ("clf", clf)])

    pipeline.fit(X_train, y_train)

    if len(set(y_test)) < 2:
        print("⚠️ Only one class in test set, skipping AUC/Brier/Precision")
    else:
        preds = pipeline.predict_proba(X_test)[:, 1]
        auc = roc_auc_score(y_test, preds)
        brier = brier_score_loss(y_test, preds)
        prec = precision_score(y_test, (preds > 0.5).astype(int))
        print(f"✅ Trained model AUC={auc:.4f} Brier={brier:.4f} Prec@0.5={prec:.4f}")

    joblib.dump(pipeline, MODEL_PATH)
    print(f"💾 Saved model to {MODEL_PATH}")

if __name__ == "__main__":
    train_and_save()
