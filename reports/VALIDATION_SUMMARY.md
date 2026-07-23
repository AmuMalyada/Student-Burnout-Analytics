# MindPulse Validation Summary

## Current Automated Run

The ETL was executed successfully with all five documented sources present.

- All five sources loaded: UCI Student Performance, Student Mental Health, Student Depression, Student Stress Monitoring (2 files), Sleep Health & Lifestyle
- Unified rows: 31,336
- Unified columns: 26
- SQLite database created: `data/processed/mindpulse.sqlite`
- Data quality report created: `reports/data_quality_report.json`
- Data dictionary created: `reports/data_dictionary.json`
- Correlation heatmap created: `reports/correlation_matrix.png`
- Risk-segment distribution chart created: `reports/risk_distribution.png`
- Model comparison run: `reports/model_metrics.json` — best model (`logistic_regression`) reached 91.9% accuracy, 0.97 ROC AUC. See `reports/BUSINESS_RECOMMENDATIONS.md` for important caveats on how to read this number (partial label leakage from feature construction).

## Data Source Notes

Two mapping gaps were found and fixed while integrating the real files:

- The Student Mental Health dataset's self-reported depression/anxiety/panic-attack fields were not originally recognized by the Burnout Risk Index formula, so all 101 rows scored as null. Fixed in `python/feature_engineering.py`.
- One of the two Student Stress Monitoring files (`Stress_Dataset.csv`) has ~25 individual Likert-scale items but no pre-aggregated score column, so it also scored as null. Fixed by deriving a composite `stress_score` in `python/preprocessing.py`. See `documentation/ASSUMPTIONS.md` items 15-16.

## Combination Method

Datasets are combined using source-preserving fact tables and a conformed population-level observation table. No person-level joins are fabricated between unrelated public datasets.

## Ethical Control

The generated Burnout Risk Index is educational and statistical only. It must not be interpreted as diagnosis, clinical prediction, or individual-level labeling.
