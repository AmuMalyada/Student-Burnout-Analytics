# Power BI Dashboard Build Guide

Connect Power BI Desktop to:

`data/processed/mindpulse.sqlite`

Recommended import tables/views:

- `fact_wellbeing_observation`
- `vw_kpi_overview`
- `vw_department_risk`
- `vw_risk_distribution`
- `vw_sleep_lifestyle`
- `vw_academic_pressure`
- `vw_quality_missingness`

## Theme

Use a professional dark theme:

- Background: `#101418`
- Surface: `#171D23`
- Accent teal: `#2DD4BF`
- Accent amber: `#F59E0B`
- Accent rose: `#F43F5E`
- Text: `#E5E7EB`

## Pages

1. Executive Overview
2. Student Wellbeing
3. Academic Pressure
4. Sleep & Lifestyle
5. Burnout Risk Trends
6. Department Analysis
7. Resource Planning
8. Predictive Analytics

## Required Visuals

- KPI cards: average stress, average sleep, study hours, burnout risk index, counseling participation.
- Bar charts: department comparison, gender comparison, age group comparison.
- Matrix: resource planning by department and risk segment.
- Scatter: sleep hours vs stress proxy.
- Line chart: academic-year risk trend where fields exist.
- Tooltip page: department risk, sleep, stress, sample size.
- Drillthrough page: department-level detail.
- Navigation buttons and bookmarks for dark executive navigation.

## Mobile Layout

Create a simplified one-column mobile view with KPI cards first, followed by risk distribution and department ranking.

## PBIX Placeholder

This repository includes `powerbi/MindPulse.pbix.placeholder.md` because `.pbix` files must be created in Power BI Desktop. The guide above documents the exact build.

