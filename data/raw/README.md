# Raw Data

Place original public datasets here without editing source files.

All five documented sources are bundled in this repo so the pipeline runs end-to-end with no external downloads or Kaggle credentials required:

- `student_performance/`: UCI Student Performance dataset (math + Portuguese course files).
- `student_mental_health/`: Kaggle Student Mental Health dataset.
- `student_depression/`: Kaggle Student Depression dataset.
- `student_stress/`: Kaggle Student Stress Monitoring datasets (two files with different schemas — see `documentation/ASSUMPTIONS.md`).
- `sleep_lifestyle/`: Kaggle Sleep Health and Lifestyle dataset.

`python/etl.py` will attempt a live re-download of each source on every run (via `kagglehub` for Kaggle sources, direct HTTP for UCI) and falls back to whatever is already in these folders if that fails — so it works the same whether or not you have network/Kaggle access. See `reports/download_manifest.json` after a run for the live per-source status.

