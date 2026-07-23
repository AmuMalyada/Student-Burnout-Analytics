"""Educational burnout risk modeling for MindPulse.

This module estimates a population-level Burnout Risk Index. It does not
diagnose mental illness and must not be used for individual clinical decisions.
"""

from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.tree import DecisionTreeClassifier

from utils import DATA_PROCESSED, REPORTS, write_json


try:
    from xgboost import XGBClassifier
except Exception:
    XGBClassifier = None


TARGET_COLUMN = "risk_target"


def build_modeling_frame(path: Path | None = None) -> pd.DataFrame:
    """Load the unified observation table and create an educational target."""
    source_path = path or DATA_PROCESSED / "fact_wellbeing_observation.csv"
    df = pd.read_csv(source_path)
    if "burnout_risk_index" not in df.columns:
        raise ValueError("burnout_risk_index is required for modeling.")
    df = df[df["burnout_risk_index"].notna()].copy()
    if df.empty:
        raise ValueError("No rows with burnout_risk_index are available.")
    threshold = df["burnout_risk_index"].quantile(0.66)
    df[TARGET_COLUMN] = (df["burnout_risk_index"] >= threshold).astype(int)
    return df


def make_preprocessor(df: pd.DataFrame) -> ColumnTransformer:
    """Create preprocessing pipeline for mixed data."""
    excluded = {TARGET_COLUMN, "burnout_risk_index", "risk_segment"}
    feature_df = df.drop(columns=[column for column in excluded if column in df.columns])
    numeric_features = feature_df.select_dtypes(include=np.number).columns.tolist()
    categorical_features = [column for column in feature_df.columns if column not in numeric_features]
    return ColumnTransformer(
        transformers=[
            ("numeric", Pipeline([("imputer", SimpleImputer(strategy="median")), ("scaler", StandardScaler())]), numeric_features),
            ("categorical", Pipeline([("imputer", SimpleImputer(strategy="most_frequent")), ("encoder", OneHotEncoder(handle_unknown="ignore"))]), categorical_features),
        ]
    )


def candidate_models() -> dict[str, object]:
    """Return the candidate algorithms required by the project brief."""
    models: dict[str, object] = {
        "logistic_regression": LogisticRegression(max_iter=1000),
        "random_forest": RandomForestClassifier(n_estimators=250, random_state=42, class_weight="balanced"),
        "decision_tree": DecisionTreeClassifier(random_state=42, class_weight="balanced"),
    }
    if XGBClassifier is not None:
        models["xgboost"] = XGBClassifier(eval_metric="logloss", random_state=42)
    return models


def evaluate_model(model: Pipeline, x_test: pd.DataFrame, y_test: pd.Series) -> dict[str, float]:
    """Calculate classification metrics."""
    predictions = model.predict(x_test)
    if hasattr(model, "predict_proba"):
        probabilities = model.predict_proba(x_test)[:, 1]
    else:
        probabilities = predictions
    return {
        "accuracy": float(accuracy_score(y_test, predictions)),
        "precision": float(precision_score(y_test, predictions, zero_division=0)),
        "recall": float(recall_score(y_test, predictions, zero_division=0)),
        "f1": float(f1_score(y_test, predictions, zero_division=0)),
        "roc_auc": float(roc_auc_score(y_test, probabilities)) if y_test.nunique() > 1 else float("nan"),
    }


def train_models() -> dict[str, object]:
    """Train and compare candidate burnout-risk models."""
    df = build_modeling_frame()
    y = df[TARGET_COLUMN]
    x = df.drop(columns=[TARGET_COLUMN, "burnout_risk_index", "risk_segment"], errors="ignore")
    if len(df) < 50 or y.nunique() < 2:
        raise ValueError("At least 50 modeled rows and two target classes are required.")
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.25, stratify=y, random_state=42)
    preprocessor = make_preprocessor(df)
    results = {}
    best_name = ""
    best_score = -1.0
    best_model: Pipeline | None = None
    for name, estimator in candidate_models().items():
        pipeline = Pipeline([("preprocessor", preprocessor), ("model", estimator)])
        pipeline.fit(x_train, y_train)
        metrics = evaluate_model(pipeline, x_test, y_test)
        results[name] = metrics
        if metrics["f1"] > best_score:
            best_name = name
            best_score = metrics["f1"]
            best_model = pipeline
    REPORTS.mkdir(parents=True, exist_ok=True)
    write_json({"best_model": best_name, "metrics": results}, REPORTS / "model_metrics.json")
    if best_model is not None:
        joblib.dump(best_model, DATA_PROCESSED / "burnout_risk_model.joblib")
    return {"best_model": best_name, "metrics": results}


if __name__ == "__main__":
    print(train_models())
