# Cleaning, Transformation, and Modeling Assumptions

1. Datasets are not respondent-linked. They are combined through a conformed analytical model, not row-level joins.
2. `dataset_source` and `source_table` preserve lineage for every observation.
3. Column names are standardized to snake_case.
4. Duplicate records are removed within each source table.
5. Yes/no survey fields are encoded as 1/0 where the source uses clear yes/no categories.
6. Sleep duration text bands are converted to approximate hours for aggregate analysis.
7. Course, department, occupation, or field-like values are mapped to `department` only for reporting; they are not treated as identical institutional departments.
8. Academic absences from UCI are used as an attendance proxy.
9. Burnout Risk Index is an educational statistical score based on available survey variables. It is not a clinical diagnosis.
10. Risk segments are relative planning indicators: Lower, Moderate, Elevated.
11. Missing fields are retained as nulls rather than imputed in the reporting layer.
12. Machine learning uses the derived risk score to compare algorithms. It does not predict medical conditions.
13. The Sleep Health and Lifestyle dataset is used as a lifestyle benchmark because it is not student-specific.
14. UCI Student Performance supports academic workload and attendance analysis, not mental health labeling.
15. `Stress_Dataset.csv` (one of the two Student Stress Monitoring files) has no single pre-aggregated stress score, only ~25 individual Likert-scale (1-5) survey items. A composite `stress_score` is derived as the row-mean of those items so the file contributes to the Burnout Risk Index like every other source. `StressLevelDataset.csv`, the other file in the same Kaggle dataset, already provides its own `stress_level` column and is left as-is.
16. The Student Mental Health dataset's self-reported depression, anxiety, and panic-attack yes/no fields are included as Burnout Risk Index components (in addition to counseling participation, which is reported separately, not scored). This is a self-report screening signal, not a diagnosis, consistent with `documentation/ETHICS.md`.

