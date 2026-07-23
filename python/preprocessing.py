"""Cleaning and standardization logic for MindPulse source datasets."""

from __future__ import annotations

import numpy as np
import pandas as pd

from utils import standardize_columns


YES_NO_MAP = {
    "yes": 1,
    "y": 1,
    "true": 1,
    "1": 1,
    "no": 0,
    "n": 0,
    "false": 0,
    "0": 0,
}


def normalize_yes_no(series: pd.Series) -> pd.Series:
    """Map common yes/no string values to 1/0 while preserving nulls."""
    return series.astype(str).str.strip().str.lower().map(YES_NO_MAP)


def clean_text_categories(series: pd.Series) -> pd.Series:
    """Normalize categorical text values for reporting consistency."""
    return (
        series.astype("string")
        .str.strip()
        .str.replace(r"\s+", " ", regex=True)
        .str.title()
    )


def extract_sleep_hours(value: object) -> float:
    """Convert mixed sleep duration labels into approximate numeric hours."""
    if pd.isna(value):
        return np.nan
    text = str(value).lower().strip()
    if "less than 5" in text:
        return 4.5
    if "more than 8" in text:
        return 8.5
    if "-" in text:
        numbers = [float(part) for part in text.replace("hours", "").split("-") if part.strip().replace(".", "", 1).isdigit()]
        if numbers:
            return float(np.mean(numbers))
    try:
        return float(text.replace("hours", "").strip())
    except ValueError:
        return np.nan


def basic_clean(df: pd.DataFrame) -> pd.DataFrame:
    """Apply common cleaning steps to any source dataframe."""
    clean = standardize_columns(df)
    clean = clean.drop_duplicates().reset_index(drop=True)
    for column in clean.select_dtypes(include=["object", "string"]).columns:
        clean[column] = clean_text_categories(clean[column])
    return clean


def clean_student_mental_health(df: pd.DataFrame) -> pd.DataFrame:
    """Clean the Student Mental Health survey dataset."""
    clean = basic_clean(df)
    rename_map = {
        "choose_your_gender": "gender",
        "what_is_your_course": "department",
        "your_current_year_of_study": "academic_year",
        "what_is_your_cgpa": "cgpa_band",
        "do_you_have_depression": "self_reported_depression",
        "do_you_have_anxiety": "self_reported_anxiety",
        "do_you_have_panic_attack": "self_reported_panic_attack",
        "did_you_seek_any_specialist_for_a_treatment": "counseling_participation",
    }
    clean = clean.rename(columns={k: v for k, v in rename_map.items() if k in clean.columns})
    for column in ["self_reported_depression", "self_reported_anxiety", "self_reported_panic_attack", "counseling_participation"]:
        if column in clean.columns:
            clean[column] = normalize_yes_no(clean[column])
    clean["dataset_source"] = "student_mental_health"
    return clean


def clean_student_depression(df: pd.DataFrame) -> pd.DataFrame:
    """Clean the Student Depression dataset."""
    clean = basic_clean(df)
    rename_map = {
        "work_study_hours": "study_hours",
        "have_you_ever_had_suicidal_thoughts": "suicidal_thoughts_history",
        "family_history_of_mental_illness": "family_history_mental_illness",
    }
    clean = clean.rename(columns={k: v for k, v in rename_map.items() if k in clean.columns})
    if "sleep_duration" in clean.columns:
        clean["sleep_hours"] = clean["sleep_duration"].map(extract_sleep_hours)
    for column in ["suicidal_thoughts_history", "family_history_mental_illness"]:
        if column in clean.columns:
            clean[column] = normalize_yes_no(clean[column])
    clean["dataset_source"] = "student_depression"
    return clean


def clean_student_stress(df: pd.DataFrame) -> pd.DataFrame:
    """Clean either of the student stress source files."""
    clean = basic_clean(df)
    has_prebuilt_score = "stress_level" in clean.columns
    if not has_prebuilt_score:
        # This is the Stress_Dataset.csv schema: ~25 individual Likert-scale
        # (1-5) survey items with no single pre-aggregated score column, unlike
        # StressLevelDataset.csv which already provides `stress_level`. Build a
        # composite proxy stress_score as the row-mean of the numeric Likert
        # items so this file contributes to the burnout risk index instead of
        # silently scoring zero observations. See documentation/ASSUMPTIONS.md.
        excluded = {"gender", "age"}
        likert_columns = [
            column
            for column in clean.columns
            if column not in excluded and pd.api.types.is_numeric_dtype(clean[column])
        ]
        if likert_columns:
            clean["stress_score"] = clean[likert_columns].mean(axis=1)
    clean["dataset_source"] = "student_stress"
    return clean


def clean_sleep_lifestyle(df: pd.DataFrame) -> pd.DataFrame:
    """Clean the Sleep Health and Lifestyle dataset."""
    clean = basic_clean(df)
    rename_map = {
        "person_id": "source_person_id",
        "occupation": "department",
        "sleep_duration": "sleep_hours",
        "sleep_duration_hours": "sleep_hours",
        "quality_of_sleep": "sleep_quality",
        "physical_activity_level": "physical_activity_minutes",
        "physical_activity_level_minutes_day": "physical_activity_minutes",
        "stress_level": "stress_score",
    }
    clean = clean.rename(columns={k: v for k, v in rename_map.items() if k in clean.columns})
    clean["dataset_source"] = "sleep_lifestyle"
    return clean


def clean_student_performance(df: pd.DataFrame) -> pd.DataFrame:
    """Clean the UCI Student Performance dataset."""
    clean = basic_clean(df)
    clean["dataset_source"] = "student_performance"
    if "studytime" in clean.columns:
        clean["study_hours_band"] = clean["studytime"]
    if "absences" in clean.columns:
        clean["attendance_proxy_absences"] = pd.to_numeric(clean["absences"], errors="coerce")
    if "g3" in clean.columns:
        clean["final_grade"] = pd.to_numeric(clean["g3"], errors="coerce")
    return clean
