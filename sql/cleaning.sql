-- SQLite cleaning patterns used for QA and repeatable transformations.

CREATE VIEW IF NOT EXISTS vw_quality_missingness AS
SELECT
    dataset_source,
    COUNT(*) AS row_count,
    SUM(CASE WHEN gender IS NULL THEN 1 ELSE 0 END) AS missing_gender,
    SUM(CASE WHEN age IS NULL THEN 1 ELSE 0 END) AS missing_age,
    SUM(CASE WHEN department IS NULL THEN 1 ELSE 0 END) AS missing_department,
    SUM(CASE WHEN sleep_hours IS NULL THEN 1 ELSE 0 END) AS missing_sleep_hours,
    SUM(CASE WHEN burnout_risk_index IS NULL THEN 1 ELSE 0 END) AS missing_burnout_risk_index
FROM fact_wellbeing_observation
GROUP BY dataset_source;

CREATE VIEW IF NOT EXISTS vw_clean_wellbeing_observation AS
WITH normalized AS (
    SELECT
        source_table,
        dataset_source,
        NULLIF(TRIM(gender), '') AS gender,
        age,
        COALESCE(age_group, 'Unknown') AS age_group,
        COALESCE(NULLIF(TRIM(department), ''), 'Unknown') AS department,
        academic_year,
        cgpa,
        cgpa_band,
        sleep_hours,
        sleep_quality,
        COALESCE(stress_score, stress_level, academic_pressure) AS stress_proxy,
        academic_pressure,
        study_satisfaction,
        study_hours,
        study_hours_band,
        financial_stress,
        social_support,
        physical_activity_minutes,
        extracurricular_activities,
        attendance_proxy_absences,
        final_grade,
        counseling_participation,
        burnout_risk_index,
        COALESCE(risk_segment, 'Unscored') AS risk_segment
    FROM fact_wellbeing_observation
)
SELECT * FROM normalized;

-- SQLite does not support stored procedures. The repeatable ETL procedure is
-- implemented in python/etl.py and documented in documentation/ASSUMPTIONS.md.

