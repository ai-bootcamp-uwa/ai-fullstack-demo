# Data Foundation Project Workflow Diagram

This document visualizes the workflow and data flow for the data foundation project using a Mermaid diagram. It illustrates how raw data is processed, accessed, analyzed, and optionally exposed via an API.

```mermaid
flowchart TD
    A["Raw Data<br/>(data/raw/)"] --> B["ETL Scripts<br/>(scripts/)"]
    B --> C["Processed Data<br/>(data/processed/)"]
    C --> D["Data Access Layer<br/>(src/data_access.py)"]
    D --> E["Data Processing<br/>(src/processing.py)"]
    E --> F["Analysis & Reporting<br/>(src/analysis.py)"]
    F --> G["Jupyter Notebooks<br/>(notebooks/)"]
    D --> H["API<br/>(src/api/main.py)"]
    H --> I["External Consumers"]
    G --> I

    subgraph Testing
        J["Unit & Integration Tests<br/>(tests/)"]
    end
    D -.-> J
    E -.-> J
    F -.-> J
    H -.-> J

    subgraph ProjectRoot
        K[".env, requirements.txt,<br/>README.md, .gitignore"]
    end
    K -.-> B
    K -.-> H
    K -.-> J
```
