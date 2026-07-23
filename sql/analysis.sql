-- 55 portfolio-ready analytical queries for MindPulse.

-- 01 Overall KPI snapshot
SELECT * FROM vw_kpi_overview;

-- 02 Average stress by department
SELECT department, ROUND(AVG(stress_proxy), 2) AS avg_stress FROM vw_clean_wellbeing_observation GROUP BY department ORDER BY avg_stress DESC;

-- 03 Stress by gender
SELECT gender, ROUND(AVG(stress_proxy), 2) AS avg_stress, COUNT(*) AS observations FROM vw_clean_wellbeing_observation GROUP BY gender ORDER BY avg_stress DESC;

-- 04 Stress by age group
SELECT age_group, ROUND(AVG(stress_proxy), 2) AS avg_stress FROM vw_clean_wellbeing_observation GROUP BY age_group ORDER BY avg_stress DESC;

-- 05 Stress by sleep duration band
WITH bands AS (
    SELECT CASE WHEN sleep_hours < 6 THEN '<6h' WHEN sleep_hours < 7 THEN '6-7h' WHEN sleep_hours <= 8 THEN '7-8h' WHEN sleep_hours > 8 THEN '>8h' ELSE 'Unknown' END AS sleep_band, stress_proxy
    FROM vw_clean_wellbeing_observation
)
SELECT sleep_band, ROUND(AVG(stress_proxy), 2) AS avg_stress, COUNT(*) AS observations FROM bands GROUP BY sleep_band;

-- 06 Academic workload by department
SELECT department, ROUND(AVG(study_hours), 2) AS avg_study_hours FROM vw_clean_wellbeing_observation GROUP BY department ORDER BY avg_study_hours DESC;

-- 07 Attendance proxy by academic group
SELECT academic_year, ROUND(AVG(attendance_proxy_absences), 2) AS avg_absences FROM vw_clean_wellbeing_observation GROUP BY academic_year ORDER BY avg_absences DESC;

-- 08 Exercise habits and stress
SELECT CASE WHEN physical_activity_minutes >= 60 THEN '60+ min' WHEN physical_activity_minutes >= 30 THEN '30-59 min' WHEN physical_activity_minutes > 0 THEN '<30 min' ELSE 'Unknown' END AS activity_band, ROUND(AVG(stress_proxy), 2) AS avg_stress FROM vw_clean_wellbeing_observation GROUP BY activity_band;

-- 09 Financial stress distribution
SELECT financial_stress, COUNT(*) AS observations FROM vw_clean_wellbeing_observation WHERE financial_stress IS NOT NULL GROUP BY financial_stress ORDER BY financial_stress;

-- 10 Social support and burnout
SELECT social_support, ROUND(AVG(burnout_risk_index), 2) AS avg_risk FROM vw_clean_wellbeing_observation WHERE social_support IS NOT NULL GROUP BY social_support ORDER BY social_support;

-- 11 Study hours and burnout
SELECT ROUND(study_hours, 0) AS study_hours_rounded, ROUND(AVG(burnout_risk_index), 2) AS avg_risk FROM vw_clean_wellbeing_observation WHERE study_hours IS NOT NULL GROUP BY ROUND(study_hours, 0) ORDER BY study_hours_rounded;

-- 12 Burnout risk indicators by source
SELECT dataset_source, ROUND(AVG(burnout_risk_index), 2) AS avg_risk, COUNT(*) AS observations FROM vw_clean_wellbeing_observation GROUP BY dataset_source ORDER BY avg_risk DESC;

-- 13 Counseling utilization by risk segment
SELECT risk_segment, ROUND(AVG(counseling_participation), 3) AS counseling_rate FROM vw_clean_wellbeing_observation GROUP BY risk_segment;

-- 14 Semester or academic-year risk trends
SELECT academic_year, ROUND(AVG(burnout_risk_index), 2) AS avg_risk FROM vw_clean_wellbeing_observation GROUP BY academic_year ORDER BY academic_year;

-- 15 Department risk rank
SELECT * FROM vw_department_risk ORDER BY risk_rank;

-- 16 Top elevated-risk departments
SELECT department, COUNT(*) AS elevated_count FROM vw_clean_wellbeing_observation WHERE risk_segment = 'Elevated' GROUP BY department ORDER BY elevated_count DESC LIMIT 10;

-- 17 Sleep quality and stress
SELECT sleep_quality, ROUND(AVG(stress_proxy), 2) AS avg_stress FROM vw_clean_wellbeing_observation WHERE sleep_quality IS NOT NULL GROUP BY sleep_quality ORDER BY sleep_quality;

-- 18 CGPA band and risk
SELECT cgpa_band, ROUND(AVG(burnout_risk_index), 2) AS avg_risk FROM vw_clean_wellbeing_observation GROUP BY cgpa_band ORDER BY avg_risk DESC;

-- 19 Final grade and absences
SELECT CASE WHEN attendance_proxy_absences >= 20 THEN 'High Absence' WHEN attendance_proxy_absences >= 10 THEN 'Moderate Absence' ELSE 'Lower Absence' END AS absence_band, ROUND(AVG(final_grade), 2) AS avg_final_grade FROM vw_clean_wellbeing_observation WHERE final_grade IS NOT NULL GROUP BY absence_band;

-- 20 Dataset coverage
SELECT dataset_source, COUNT(*) AS rows, COUNT(DISTINCT source_table) AS source_tables FROM vw_clean_wellbeing_observation GROUP BY dataset_source;

-- 21 Missingness report
SELECT * FROM vw_quality_missingness;

-- 22 Risk distribution
SELECT * FROM vw_risk_distribution;

-- 23 Lifestyle profile
SELECT * FROM vw_sleep_lifestyle;

-- 24 Academic pressure page extract
SELECT * FROM vw_academic_pressure;

-- 25 Window function: percentile style department rank
SELECT department, AVG(burnout_risk_index) AS avg_risk, NTILE(4) OVER (ORDER BY AVG(burnout_risk_index)) AS risk_quartile FROM vw_clean_wellbeing_observation GROUP BY department;

-- 26 CTE: elevated risk share by department
WITH totals AS (SELECT department, COUNT(*) total_rows FROM vw_clean_wellbeing_observation GROUP BY department), elevated AS (SELECT department, COUNT(*) elevated_rows FROM vw_clean_wellbeing_observation WHERE risk_segment='Elevated' GROUP BY department) SELECT t.department, ROUND(COALESCE(e.elevated_rows,0)*100.0/t.total_rows,2) AS elevated_pct FROM totals t LEFT JOIN elevated e ON t.department=e.department ORDER BY elevated_pct DESC;

-- 27 Stress quartiles
SELECT dataset_source, stress_proxy, NTILE(4) OVER (PARTITION BY dataset_source ORDER BY stress_proxy) AS stress_quartile FROM vw_clean_wellbeing_observation WHERE stress_proxy IS NOT NULL;

-- 28 High academic pressure and low sleep
SELECT COUNT(*) AS observations FROM vw_clean_wellbeing_observation WHERE academic_pressure >= 4 AND sleep_hours < 6;

-- 29 High study hours and elevated risk
SELECT COUNT(*) AS observations FROM vw_clean_wellbeing_observation WHERE study_hours >= 8 AND risk_segment = 'Elevated';

-- 30 Gender mix by source
SELECT dataset_source, gender, COUNT(*) AS observations FROM vw_clean_wellbeing_observation GROUP BY dataset_source, gender;

-- 31 Age group mix by source
SELECT dataset_source, age_group, COUNT(*) AS observations FROM vw_clean_wellbeing_observation GROUP BY dataset_source, age_group;

-- 32 Department comparison with window average
SELECT department, AVG(burnout_risk_index) AS avg_risk, AVG(AVG(burnout_risk_index)) OVER () AS portfolio_avg_risk FROM vw_clean_wellbeing_observation GROUP BY department;

-- 33 Above portfolio average departments
WITH d AS (SELECT department, AVG(burnout_risk_index) avg_risk FROM vw_clean_wellbeing_observation GROUP BY department), p AS (SELECT AVG(burnout_risk_index) avg_risk FROM vw_clean_wellbeing_observation) SELECT d.department, ROUND(d.avg_risk,2) AS avg_risk FROM d CROSS JOIN p WHERE d.avg_risk > p.avg_risk ORDER BY d.avg_risk DESC;

-- 34 Counseling gap for elevated risk
SELECT risk_segment, COUNT(*) AS observations, SUM(CASE WHEN counseling_participation = 1 THEN 1 ELSE 0 END) AS counseling_yes FROM vw_clean_wellbeing_observation GROUP BY risk_segment;

-- 35 Physical activity by risk segment
SELECT risk_segment, ROUND(AVG(physical_activity_minutes),2) AS avg_activity FROM vw_clean_wellbeing_observation GROUP BY risk_segment;

-- 36 Sleep by risk segment
SELECT risk_segment, ROUND(AVG(sleep_hours),2) AS avg_sleep FROM vw_clean_wellbeing_observation GROUP BY risk_segment;

-- 37 Financial stress by risk segment
SELECT risk_segment, ROUND(AVG(financial_stress),2) AS avg_financial_stress FROM vw_clean_wellbeing_observation GROUP BY risk_segment;

-- 38 Academic pressure by risk segment
SELECT risk_segment, ROUND(AVG(academic_pressure),2) AS avg_academic_pressure FROM vw_clean_wellbeing_observation GROUP BY risk_segment;

-- 39 Study satisfaction by risk segment
SELECT risk_segment, ROUND(AVG(study_satisfaction),2) AS avg_study_satisfaction FROM vw_clean_wellbeing_observation GROUP BY risk_segment;

-- 40 Grade outcome by study-time band
SELECT study_hours_band, ROUND(AVG(final_grade),2) AS avg_final_grade FROM vw_clean_wellbeing_observation GROUP BY study_hours_band ORDER BY study_hours_band;

-- 41 Absences by risk segment
SELECT risk_segment, ROUND(AVG(attendance_proxy_absences),2) AS avg_absences FROM vw_clean_wellbeing_observation GROUP BY risk_segment;

-- 42 Source-specific average sleep
SELECT dataset_source, ROUND(AVG(sleep_hours),2) AS avg_sleep FROM vw_clean_wellbeing_observation GROUP BY dataset_source;

-- 43 Source-specific average stress proxy
SELECT dataset_source, ROUND(AVG(stress_proxy),2) AS avg_stress FROM vw_clean_wellbeing_observation GROUP BY dataset_source;

-- 44 Source-specific scored coverage
SELECT dataset_source, SUM(CASE WHEN burnout_risk_index IS NOT NULL THEN 1 ELSE 0 END) AS scored_rows, COUNT(*) AS total_rows FROM vw_clean_wellbeing_observation GROUP BY dataset_source;

-- 45 Elevated risk with low sleep and high pressure
SELECT COUNT(*) AS observations FROM vw_clean_wellbeing_observation WHERE risk_segment='Elevated' AND sleep_hours < 6 AND academic_pressure >= 4;

-- 46 Department resource planning score
SELECT department, ROUND(AVG(burnout_risk_index),2) AS avg_risk, COUNT(*) AS demand_base, ROUND(AVG(burnout_risk_index) * COUNT(*) / 100.0,2) AS planning_weight FROM vw_clean_wellbeing_observation GROUP BY department ORDER BY planning_weight DESC;

-- 47 Drillthrough detail for elevated segments
SELECT dataset_source, department, gender, age_group, sleep_hours, stress_proxy, burnout_risk_index FROM vw_clean_wellbeing_observation WHERE risk_segment='Elevated';

-- 48 Tooltip summary by department
SELECT department, COUNT(*) AS observations, ROUND(AVG(sleep_hours),2) AS sleep, ROUND(AVG(stress_proxy),2) AS stress, ROUND(AVG(burnout_risk_index),2) AS risk FROM vw_clean_wellbeing_observation GROUP BY department;

-- 49 Risk trend proxy by academic year using lag
SELECT academic_year, AVG(burnout_risk_index) AS avg_risk, AVG(burnout_risk_index) - LAG(AVG(burnout_risk_index)) OVER (ORDER BY academic_year) AS risk_change FROM vw_clean_wellbeing_observation GROUP BY academic_year;

-- 50 Forecast input extract
SELECT academic_year, dataset_source, COUNT(*) AS observations, AVG(burnout_risk_index) AS avg_risk FROM vw_clean_wellbeing_observation GROUP BY academic_year, dataset_source;

-- 51 Cluster-analysis feature extract
SELECT sleep_hours, stress_proxy, academic_pressure, study_hours, financial_stress, physical_activity_minutes, burnout_risk_index FROM vw_clean_wellbeing_observation;

-- 52 Predictive analytics feature extract
SELECT * FROM vw_clean_wellbeing_observation WHERE burnout_risk_index IS NOT NULL;

-- 53 KPI card extract
SELECT 'Average Stress Score' AS kpi, ROUND(AVG(stress_proxy),2) AS value FROM vw_clean_wellbeing_observation UNION ALL SELECT 'Average Sleep', ROUND(AVG(sleep_hours),2) FROM vw_clean_wellbeing_observation UNION ALL SELECT 'Estimated Burnout Risk Index', ROUND(AVG(burnout_risk_index),2) FROM vw_clean_wellbeing_observation;

-- 54 Data-source limitation summary
SELECT dataset_source, MIN(source_table) AS example_table, COUNT(*) AS observations FROM vw_clean_wellbeing_observation GROUP BY dataset_source;

-- 55 Executive resource planning matrix
SELECT department, risk_segment, COUNT(*) AS observations, ROUND(AVG(burnout_risk_index),2) AS avg_risk FROM vw_clean_wellbeing_observation GROUP BY department, risk_segment ORDER BY department, risk_segment;

