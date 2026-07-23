-- MindPulse SQLite warehouse schema.
-- Source fact tables are also created by pandas during ETL because public
-- datasets vary in available columns. This script defines the conformed layer.

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS dim_dataset_source (
    dataset_source_id INTEGER PRIMARY KEY,
    dataset_source TEXT NOT NULL UNIQUE,
    source_name TEXT NOT NULL,
    public_url TEXT NOT NULL,
    usage_notes TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_risk_segment (
    risk_segment_id INTEGER PRIMARY KEY,
    risk_segment TEXT NOT NULL UNIQUE,
    lower_bound REAL NOT NULL,
    upper_bound REAL NOT NULL,
    interpretation TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS fact_wellbeing_observation (
    source_table TEXT,
    dataset_source TEXT,
    gender TEXT,
    age REAL,
    age_group TEXT,
    department TEXT,
    academic_year TEXT,
    cgpa REAL,
    cgpa_band TEXT,
    sleep_hours REAL,
    sleep_quality REAL,
    stress_score REAL,
    stress_level REAL,
    academic_pressure REAL,
    study_satisfaction REAL,
    study_hours REAL,
    study_hours_band TEXT,
    financial_stress REAL,
    social_support REAL,
    physical_activity_minutes REAL,
    extracurricular_activities TEXT,
    attendance_proxy_absences REAL,
    final_grade REAL,
    counseling_participation REAL,
    burnout_risk_index REAL,
    risk_segment TEXT
);

CREATE INDEX IF NOT EXISTS idx_wellbeing_source ON fact_wellbeing_observation(dataset_source);
CREATE INDEX IF NOT EXISTS idx_wellbeing_department ON fact_wellbeing_observation(department);
CREATE INDEX IF NOT EXISTS idx_wellbeing_gender ON fact_wellbeing_observation(gender);
CREATE INDEX IF NOT EXISTS idx_wellbeing_age_group ON fact_wellbeing_observation(age_group);
CREATE INDEX IF NOT EXISTS idx_wellbeing_risk_segment ON fact_wellbeing_observation(risk_segment);

INSERT OR IGNORE INTO dim_risk_segment VALUES
(1, 'Lower', 0, 33, 'Lower relative statistical burnout risk indicator.'),
(2, 'Moderate', 33, 66, 'Moderate relative statistical burnout risk indicator.'),
(3, 'Elevated', 66, 100, 'Elevated relative statistical burnout risk indicator for aggregate planning.');

