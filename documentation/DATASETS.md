# MindPulse Dataset Selection and Validation

MindPulse uses only real, publicly available datasets. The project does not use synthetic student burnout data.

## Selected Sources

| Dataset | Source | Role | Status |
|---|---|---|---|
| Student Mental Health Dataset | https://www.kaggle.com/datasets/aminasalamat/mental-health-of-students-dataset | Student wellbeing survey indicators | Bundled in `data/raw/`; re-downloaded via `kagglehub` if network/credentials are available |
| Student Depression Dataset | https://www.kaggle.com/datasets/hopesb/student-depression-dataset | Academic pressure, sleep, financial stress, study variables, educational risk modeling | Bundled in `data/raw/`; re-downloaded via `kagglehub` if network/credentials are available |
| Student Stress Monitoring Datasets | https://www.kaggle.com/datasets/mdsultanulislamovi/student-stress-monitoring-datasets | Stress-specific variables and segmentation | Bundled in `data/raw/`; re-downloaded via `kagglehub` if network/credentials are available |
| Sleep Health and Lifestyle Dataset | https://www.kaggle.com/datasets/uom190346a/sleep-health-and-lifestyle-dataset | Lifestyle benchmark for sleep, activity, and stress | Bundled in `data/raw/`; re-downloaded via `kagglehub` if network/credentials are available |
| UCI Student Performance Dataset | https://archive.ics.uci.edu/dataset/320/student+performance | Academic performance, absences, study time, family and school factors | Bundled in `data/raw/`; re-downloaded directly if network is available |

All five sources are committed to this repository under `data/raw/` so `python python/etl.py` runs the complete multi-source pipeline out of the box — no Kaggle account or API key required to reproduce the results in `reports/`.

## Validation Performed by ETL

The ETL writes `reports/data_quality_report.json` with:

- Number of rows
- Number of columns
- Missing values by column
- Total missing values
- Duplicate records
- Data types

The ETL writes `reports/data_dictionary.json` with every processed field and its standardized type.

## Manual Download Instructions

If Kaggle authentication is unavailable:

1. Open the source links above.
2. Download the dataset ZIP or CSV.
3. Extract files into `data/raw/<dataset_name>/`.
4. Re-run:

```bash
python python/etl.py
```

Use these folders:

- `data/raw/student_mental_health/`
- `data/raw/student_depression/`
- `data/raw/student_stress/`
- `data/raw/sleep_lifestyle/`
- `data/raw/student_performance/`

