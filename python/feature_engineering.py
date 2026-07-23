"""Feature engineering for the MindPulse analytics and ML layers."""

from __future__ import annotations

import numpy as np
import pandas as pd


def min_max_score(series: pd.Series) -> pd.Series:
    """Scale a numeric series to 0-100."""
    numeric = pd.to_numeric(series, errors="coerce")
    minimum = numeric.min()
    maximum = numeric.max()
    if pd.isna(minimum) or pd.isna(maximum) or minimum == maximum:
        return pd.Series(np.nan, index=series.index)
    return ((numeric - minimum) / (maximum - minimum)) * 100


def add_age_group(df: pd.DataFrame) -> pd.DataFrame:
    """Add a reporting-friendly age group when age is available."""
    enriched = df.copy()
    if "age" in enriched.columns:
        age = pd.to_numeric(enriched["age"], errors="coerce")
        enriched["age_group"] = pd.cut(
            age,
            bins=[0, 17, 21, 25, 30, 40, 65, 120],
            labels=["Under 18", "18-21", "22-25", "26-30", "31-40", "41-65", "65+"],
            include_lowest=True,
        ).astype("string")
    return enriched


def add_burnout_features(df: pd.DataFrame) -> pd.DataFrame:
    """Create non-diagnostic burnout indicator features for population analytics."""
    enriched = df.copy()
    stress_candidates = [
        "stress_score",
        "stress_level",
        "academic_pressure",
        "study_load",
        "financial_stress",
        "anxiety_level",
        "depression",
        "absences",
        "attendance_proxy_absences",
        "failures",
        "self_reported_depression",
        "self_reported_anxiety",
        "self_reported_panic_attack",
    ]
    components = []
    for column in stress_candidates:
        if column in enriched.columns:
            components.append(min_max_score(enriched[column]))

    if "sleep_hours" in enriched.columns:
        sleep = pd.to_numeric(enriched["sleep_hours"], errors="coerce")
        enriched["sleep_deficit_score"] = ((7 - sleep).clip(lower=0) / 7) * 100
        components.append(enriched["sleep_deficit_score"])

    if "study_hours" in enriched.columns:
        components.append(min_max_score(enriched["study_hours"]))

    if "health" in enriched.columns:
        health = pd.to_numeric(enriched["health"], errors="coerce")
        enriched["low_health_score"] = ((5 - health).clip(lower=0) / 4) * 100
        components.append(enriched["low_health_score"])

    if components:
        enriched["burnout_risk_index"] = pd.concat(components, axis=1).mean(axis=1).round(2)
        enriched["risk_segment"] = pd.cut(
            enriched["burnout_risk_index"],
            bins=[-0.1, 33, 66, 100],
            labels=["Lower", "Moderate", "Elevated"],
        ).astype("string")
    else:
        enriched["burnout_risk_index"] = np.nan
        enriched["risk_segment"] = pd.NA
    return enriched


def build_unified_observations(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Build a conformed population-level observation table from source facts."""
    semantic_columns = [
        "dataset_source",
        "gender",
        "age",
        "age_group",
        "department",
        "academic_year",
        "cgpa",
        "cgpa_band",
        "sleep_hours",
        "sleep_quality",
        "stress_score",
        "stress_level",
        "academic_pressure",
        "study_satisfaction",
        "study_hours",
        "study_hours_band",
        "financial_stress",
        "social_support",
        "physical_activity_minutes",
        "extracurricular_activities",
        "attendance_proxy_absences",
        "final_grade",
        "counseling_participation",
        "burnout_risk_index",
        "risk_segment",
    ]
    frames = []
    for name, df in tables.items():
        enriched = add_burnout_features(add_age_group(df))
        enriched["source_table"] = name
        for column in semantic_columns:
            if column not in enriched.columns:
                enriched[column] = pd.NA
        frames.append(enriched[["source_table", *semantic_columns]])
    if not frames:
        return pd.DataFrame(columns=["source_table", *semantic_columns])
    return pd.concat(frames, ignore_index=True)
