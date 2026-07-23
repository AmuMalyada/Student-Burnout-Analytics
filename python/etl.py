"""MindPulse end-to-end ETL pipeline.

The pipeline uses real public datasets only. Kaggle datasets are downloaded
through kagglehub when credentials/access are available; otherwise the script
records direct source links and continues with any files already present.
"""

from __future__ import annotations

import shutil
import zipfile
from pathlib import Path
from urllib.request import urlretrieve

import pandas as pd

from feature_engineering import add_age_group, add_burnout_features, build_unified_observations
from preprocessing import (
    clean_sleep_lifestyle,
    clean_student_depression,
    clean_student_mental_health,
    clean_student_performance,
    clean_student_stress,
)
from utils import (
    DATA_EXTERNAL,
    DATA_PROCESSED,
    DATA_RAW,
    DB_PATH,
    PROJECT_ROOT,
    REPORTS,
    SQL_DIR,
    connect_database,
    ensure_directories,
    execute_sql_file,
    read_csv_safely,
    save_dataframe,
    to_repo_relative,
    write_json,
)
from visualization import save_correlation_matrix, save_risk_distribution


DATASET_REGISTRY = {
    "student_mental_health": {
        "kaggle": "aminasalamat/mental-health-of-students-dataset",
        "manual_url": "https://www.kaggle.com/datasets/aminasalamat/mental-health-of-students-dataset",
        "cleaner": clean_student_mental_health,
        "match": ["mental", "student"],
    },
    "student_depression": {
        "kaggle": "hopesb/student-depression-dataset",
        "manual_url": "https://www.kaggle.com/datasets/hopesb/student-depression-dataset",
        "cleaner": clean_student_depression,
        "match": ["depression"],
    },
    "student_stress": {
        "kaggle": "mdsultanulislamovi/student-stress-monitoring-datasets",
        "manual_url": "https://www.kaggle.com/datasets/mdsultanulislamovi/student-stress-monitoring-datasets",
        "cleaner": clean_student_stress,
        "match": ["stress"],
    },
    "sleep_lifestyle": {
        "kaggle": "uom190346a/sleep-health-and-lifestyle-dataset",
        "manual_url": "https://www.kaggle.com/datasets/uom190346a/sleep-health-and-lifestyle-dataset",
        "cleaner": clean_sleep_lifestyle,
        "match": ["sleep"],
    },
    "student_performance": {
        "manual_url": "https://archive.ics.uci.edu/dataset/320/student+performance",
        "cleaner": clean_student_performance,
        "match": ["student-mat", "student-por"],
    },
}


def profile_dataframe(df: pd.DataFrame, dataset_name: str) -> dict[str, object]:
    """Generate a data quality profile for a dataframe."""
    return {
        "dataset": dataset_name,
        "rows": int(df.shape[0]),
        "columns": int(df.shape[1]),
        "duplicate_records": int(df.duplicated().sum()),
        "missing_values_total": int(df.isna().sum().sum()),
        "missing_values_by_column": {column: int(value) for column, value in df.isna().sum().items()},
        "data_types": {column: str(dtype) for column, dtype in df.dtypes.items()},
    }


def download_kaggle_dataset(dataset_slug: str, destination: Path) -> bool:
    """Attempt to download a public Kaggle dataset through kagglehub."""
    try:
        import kagglehub
    except ImportError:
        return False
    try:
        downloaded_path = Path(kagglehub.dataset_download(dataset_slug))
    except Exception:
        return False
    destination.mkdir(parents=True, exist_ok=True)
    for item in downloaded_path.rglob("*"):
        if item.is_file():
            target = destination / item.name
            shutil.copy2(item, target)
    return True


def download_uci_student_performance() -> bool:
    """Download the UCI Student Performance dataset."""
    url = "https://archive.ics.uci.edu/static/public/320/student+performance.zip"
    zip_path = DATA_EXTERNAL / "student_performance.zip"
    extract_path = DATA_RAW / "student_performance"
    try:
        DATA_EXTERNAL.mkdir(parents=True, exist_ok=True)
        urlretrieve(url, zip_path)
        extract_path.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(zip_path) as archive:
            archive.extractall(extract_path)
        for nested_zip in extract_path.rglob("*.zip"):
            nested_folder = nested_zip.with_suffix("")
            nested_folder.mkdir(parents=True, exist_ok=True)
            with zipfile.ZipFile(nested_zip) as archive:
                archive.extractall(nested_folder)
        return True
    except Exception:
        return False


def download_public_datasets() -> dict[str, object]:
    """Download public datasets where automatic download is available.

    A dataset only needs a manual-download callout if no usable raw files
    are present locally after the automatic attempt. If files were placed
    manually (or the auto-download simply succeeded), it is reported as
    available, regardless of whether the live network fetch worked in this
    particular run.
    """
    manifest: dict[str, object] = {"downloads": {}, "manual_downloads": {}}
    for dataset_name, metadata in DATASET_REGISTRY.items():
        destination = DATA_RAW / dataset_name
        if dataset_name == "student_performance":
            ok = download_uci_student_performance()
        else:
            ok = download_kaggle_dataset(str(metadata.get("kaggle")), destination)
        files_present = bool(find_csv_files(dataset_name))
        if ok:
            manifest["downloads"][dataset_name] = "downloaded"
        elif files_present:
            manifest["downloads"][dataset_name] = "already_present_locally"
        else:
            manifest["downloads"][dataset_name] = "not_downloaded"
        if not ok and not files_present:
            manifest["manual_downloads"][dataset_name] = {
                "url": metadata["manual_url"],
                "place_files_under": to_repo_relative(destination),
            }
    write_json(manifest, REPORTS / "download_manifest.json")
    return manifest


def find_csv_files(dataset_name: str) -> list[Path]:
    """Find source CSV files for a registered dataset."""
    folder = DATA_RAW / dataset_name
    if not folder.exists():
        return []
    files = list(folder.rglob("*.csv"))
    files += list(folder.rglob("*.data"))
    return files


def select_matching_files(dataset_name: str, files: list[Path]) -> list[Path]:
    """Select relevant files from a dataset folder."""
    tokens = DATASET_REGISTRY[dataset_name]["match"]
    selected = [path for path in files if any(token in path.name.lower() for token in tokens)]
    return selected or files


def read_source_file(path: Path) -> pd.DataFrame:
    """Read a source file with dataset-specific delimiter support."""
    if path.suffix.lower() == ".data" or path.name.startswith("student-"):
        return pd.read_csv(path, sep=";")
    return read_csv_safely(path)


def load_and_clean_sources() -> tuple[dict[str, pd.DataFrame], dict[str, object]]:
    """Load all available raw datasets and return cleaned tables plus profiles."""
    cleaned_tables: dict[str, pd.DataFrame] = {}
    profiles: dict[str, object] = {}
    data_dictionary: dict[str, list[dict[str, str]]] = {}

    for dataset_name, metadata in DATASET_REGISTRY.items():
        files = select_matching_files(dataset_name, find_csv_files(dataset_name))
        cleaner = metadata["cleaner"]
        for index, file_path in enumerate(files, start=1):
            raw = read_source_file(file_path)
            raw_profile_key = f"{dataset_name}_{index}_raw"
            profiles[raw_profile_key] = profile_dataframe(raw, raw_profile_key)
            cleaned = add_burnout_features(add_age_group(cleaner(raw)))
            table_name = dataset_name if len(files) == 1 else f"{dataset_name}_{index}"
            cleaned_tables[table_name] = cleaned
            profiles[table_name] = profile_dataframe(cleaned, table_name)
            data_dictionary[table_name] = [
                {
                    "field": column,
                    "data_type": str(cleaned[column].dtype),
                    "description": infer_field_description(column),
                }
                for column in cleaned.columns
            ]

    write_json(profiles, REPORTS / "data_quality_report.json")
    write_json(data_dictionary, REPORTS / "data_dictionary.json")
    return cleaned_tables, profiles


def infer_field_description(column: str) -> str:
    """Return a business-friendly field description for a column."""
    descriptions = {
        "dataset_source": "Original public dataset source identifier.",
        "gender": "Self-reported gender category where provided.",
        "age": "Respondent age where provided.",
        "age_group": "Derived age band for aggregate reporting.",
        "department": "Course, department, major, occupation, or source-equivalent grouping.",
        "academic_year": "Student year or academic level where provided.",
        "cgpa": "Student CGPA value where available.",
        "cgpa_band": "Source CGPA band where available.",
        "sleep_hours": "Approximate sleep duration in hours.",
        "stress_score": "Source stress score or normalized stress indicator.",
        "burnout_risk_index": "Educational, non-diagnostic 0-100 statistical risk indicator.",
        "risk_segment": "Lower, Moderate, or Elevated aggregate risk segment.",
        "counseling_participation": "Self-reported treatment or counseling participation indicator.",
    }
    return descriptions.get(column, column.replace("_", " ").capitalize())


def persist_outputs(cleaned_tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Write processed CSV files and SQLite warehouse tables."""
    unified = build_unified_observations(cleaned_tables)
    for table_name, dataframe in cleaned_tables.items():
        save_dataframe(dataframe, DATA_PROCESSED / f"{table_name}.csv")
    save_dataframe(unified, DATA_PROCESSED / "fact_wellbeing_observation.csv")

    with connect_database() as connection:
        for table_name, dataframe in cleaned_tables.items():
            dataframe.to_sql(f"fact_{table_name}", connection, if_exists="replace", index=False)
        unified.to_sql("fact_wellbeing_observation", connection, if_exists="replace", index=False)
        for script_name in ["schema.sql", "cleaning.sql", "views.sql"]:
            execute_sql_file(connection, SQL_DIR / script_name)
    return unified


def build_reports(unified: pd.DataFrame, download_manifest: dict[str, object]) -> None:
    """Create EDA artifacts and executive summary files."""
    save_correlation_matrix(unified, REPORTS / "correlation_matrix.png")
    save_risk_distribution(unified, REPORTS / "risk_distribution.png")
    pending = sorted(download_manifest.get("manual_downloads", {}).keys())
    summary = {
        "database": to_repo_relative(DB_PATH),
        "unified_rows": int(unified.shape[0]),
        "unified_columns": int(unified.shape[1]),
        "datasets_loaded": sorted(unified["dataset_source"].dropna().unique().tolist()) if not unified.empty else [],
        "datasets_pending_manual_download": pending,
        "ethics_notice": "MindPulse provides population-level educational analytics only and must not be used to diagnose individuals.",
    }
    write_json(summary, REPORTS / "executive_summary.json")


def main() -> None:
    """Run the complete ETL process."""
    ensure_directories()
    manifest = download_public_datasets()
    cleaned_tables, _profiles = load_and_clean_sources()
    unified = persist_outputs(cleaned_tables)
    build_reports(unified, manifest)
    print(f"MindPulse ETL complete. SQLite database: {to_repo_relative(DB_PATH)}")


if __name__ == "__main__":
    main()
