# MindPulse Architecture

```mermaid
flowchart LR
    A["Public Datasets"] --> B["data/raw"]
    B --> C["Python ETL"]
    C --> D["Data Quality Reports"]
    C --> E["data/processed CSVs"]
    E --> F["SQLite Warehouse"]
    F --> G["SQL Views and KPI Layer"]
    F --> H["EDA Reports"]
    F --> I["Educational ML Risk Model"]
    G --> J["Power BI Dashboard"]
    H --> K["Consulting Recommendations"]
    I --> K
```

## Design Pattern

MindPulse uses a conformed star-schema style analytical layer. Public datasets are preserved as source facts, then mapped into a unified observation table for population-level analytics.

No row-level joins are performed across unrelated datasets.

