-- Power BI semantic views.

CREATE VIEW IF NOT EXISTS vw_kpi_overview AS
SELECT
    COUNT(*) AS observations,
    ROUND(AVG(stress_proxy), 2) AS average_stress_score,
    ROUND(AVG(sleep_hours), 2) AS average_sleep_hours,
    ROUND(AVG(study_hours), 2) AS average_study_hours,
    ROUND(AVG(burnout_risk_index), 2) AS estimated_burnout_risk_index,
    ROUND(AVG(counseling_participation), 3) AS counseling_participation_rate,
    ROUND(AVG(physical_activity_minutes), 2) AS average_physical_activity_minutes
FROM vw_clean_wellbeing_observation;

CREATE VIEW IF NOT EXISTS vw_department_risk AS
SELECT
    department,
    COUNT(*) AS observations,
    ROUND(AVG(stress_proxy), 2) AS average_stress_score,
    ROUND(AVG(sleep_hours), 2) AS average_sleep_hours,
    ROUND(AVG(burnout_risk_index), 2) AS average_burnout_risk_index,
    RANK() OVER (ORDER BY AVG(burnout_risk_index) DESC) AS risk_rank
FROM vw_clean_wellbeing_observation
GROUP BY department
HAVING COUNT(*) >= 5;

CREATE VIEW IF NOT EXISTS vw_risk_distribution AS
SELECT
    dataset_source,
    risk_segment,
    COUNT(*) AS observations,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY dataset_source), 2) AS pct_of_source
FROM vw_clean_wellbeing_observation
GROUP BY dataset_source, risk_segment;

CREATE VIEW IF NOT EXISTS vw_sleep_lifestyle AS
SELECT
    dataset_source,
    age_group,
    gender,
    ROUND(AVG(sleep_hours), 2) AS average_sleep_hours,
    ROUND(AVG(sleep_quality), 2) AS average_sleep_quality,
    ROUND(AVG(physical_activity_minutes), 2) AS average_physical_activity_minutes,
    ROUND(AVG(stress_proxy), 2) AS average_stress_score
FROM vw_clean_wellbeing_observation
GROUP BY dataset_source, age_group, gender;

CREATE VIEW IF NOT EXISTS vw_academic_pressure AS
SELECT
    dataset_source,
    department,
    academic_year,
    ROUND(AVG(academic_pressure), 2) AS average_academic_pressure,
    ROUND(AVG(study_hours), 2) AS average_study_hours,
    ROUND(AVG(attendance_proxy_absences), 2) AS average_absences,
    ROUND(AVG(final_grade), 2) AS average_final_grade
FROM vw_clean_wellbeing_observation
GROUP BY dataset_source, department, academic_year;

