# Consulting-Style Recommendations

Generated from the current warehouse run with all five datasets loaded (`data/processed/mindpulse.sqlite`, `reports/executive_summary.json`, `reports/model_metrics.json`).

## Current Data Scope

This run includes all five documented sources: UCI Student Performance (1,044 rows), Student Mental Health (101), Student Depression (27,901), Student Stress Monitoring — two files (1,916 combined), and Sleep Health & Lifestyle (374). Total: **31,336 observations** across the conformed `fact_wellbeing_observation` table. See `reports/data_quality_report.json` for per-source row/column/missingness detail and `documentation/ASSUMPTIONS.md` for how each source's fields were mapped into a common schema.

Two real limitations still apply and should shape how these numbers are read:

- **Sources are not respondent-linked** — they are different surveys of different populations combined at the population level, not joined per-student. A "department" comparison mixes literal course codes (UCI), free-text course names (Student Mental Health), occupations (Sleep & Lifestyle), and an "Unknown" bucket for sources with no department-like field (Student Depression, Student Stress) — the large majority of rows currently fall into "Unknown." Department-level recommendations below describe the intended workflow, not yet a reliable segmentation with the current sources.
- **The Burnout Risk Index formula weights each source's available fields equally**, and those fields differ a lot in nature (self-reported yes/no screening items vs. 1-10 Likert stress scales vs. academic absences). Treat the index as a relative, within-source planning signal, not an absolute score comparable 1:1 across datasets.

## What the Current Run Actually Shows

- Average estimated Burnout Risk Index: **48.1** (0-100 scale) across all 31,336 observations. Segment mix varies substantially by source — e.g. Student Depression skews high (25.6% Elevated, 49.1% Moderate) while UCI Student Performance skews low (0.4% Elevated, 90.2% Lower) — which mostly reflects each survey's own question design and target population, not a real difference in underlying student wellbeing. Compare within a source before comparing across sources.
- Counseling participation rate: **5.9%**, based only on the Student Mental Health dataset's treatment-seeking field — the one source that asked this question directly (n=101). Too small to generalize beyond that source.
- Average sleep: **6.39 hours**, average study hours: **7.16/day**, average physical activity: **59.2 minutes/day** — pooled across whichever sources reported each field (not all 31,336 rows have every field).
- With the full dataset, the ML model comparison improved substantially over the single-dataset run: best model (`logistic_regression`) reached **91.9% accuracy, 88.0% F1, 0.97 ROC AUC** (`reports/model_metrics.json`). This is a much stronger result than the single-source baseline, but it's worth being clear-eyed about why: the target label (`risk_target`) is itself derived from the same `burnout_risk_index` the model's input features are built from, so part of this score reflects the model recovering its own scoring formula rather than an independent clinical outcome. Present this as "the model recovers population risk segments consistent with the underlying survey data," not as validated clinical prediction.

## Recommendations

1. **Use this as a working multi-source pipeline, not a cross-institution benchmark.** The biggest immediate opportunity is getting real department/course metadata into more of the five sources — without that, resource-planning-by-department can't move past the UCI subset.
2. **Report risk segments within-source, not pooled**, until a common risk-scoring methodology is validated against an external benchmark (e.g. a validated clinical screening instrument). Right now differences between sources mostly reflect survey design, not population differences.
3. **Treat the model metrics as a pipeline health check**, not a deployable predictor — the label leakage from the input features (noted above) means the reported AUC overstates real-world predictive power. A cleaner future iteration would define `risk_target` from a held-out subset of fields not used to build `burnout_risk_index`.
4. **Sleep, study-hour, and activity averages are usable today** for lifestyle-awareness messaging (6.39 avg sleep hours is a reasonable "know your numbers" data point), since these are simple aggregates, not the composite risk score.
5. **Keep using department-level, aggregate reporting only** for any future intervention planning — never route individual-level risk scores to advising or disciplinary decisions, per `documentation/ETHICS.md`.
