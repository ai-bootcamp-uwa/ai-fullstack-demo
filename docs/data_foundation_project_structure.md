# Data Foundation Project Directory Structure

This document describes a recommended directory structure for a general-purpose data-centric Python project. This structure supports data processing, ETL, analytics, and includes an optional API for data access.

```
data_foundation_project/
├── data/                  # Raw and processed data files (not tracked by git, add to .gitignore)
│   ├── raw/
│   └── processed/
├── notebooks/             # Jupyter notebooks for exploration and analysis
├── scripts/               # Standalone scripts for ETL, data loading, etc.
│   ├── load_data.py
│   └── process_data.py
├── src/                   # Core source code
│   ├── __init__.py
│   ├── data_access.py     # Functions/classes for reading/writing data
│   ├── processing.py      # Data cleaning, transformation, feature engineering
│   ├── analysis.py        # Analysis, metrics, reporting
│   └── api/               # (Optional) API code for data access
│       ├── __init__.py
│       └── main.py
├── tests/                 # Unit and integration tests
│   └── test_processing.py
├── .env                   # Environment variables (DB credentials, etc.)
├── .gitignore
├── requirements.txt       # Python dependencies
├── README.md
└── setup.py               # (Optional) For packaging as a Python module
```

## Folder & File Descriptions

- **data/**: Contains all data files. Split into `raw/` for unprocessed data and `processed/` for cleaned/derived data. This folder should be added to `.gitignore` to avoid tracking large or sensitive files.
- **notebooks/**: Jupyter notebooks for data exploration, prototyping, and analysis.
- **scripts/**: Standalone Python scripts for ETL, data loading, or batch processing tasks.
- **src/**: Main source code for the project.
  - `data_access.py`: Functions and classes for reading from and writing to data sources (files, databases, etc.).
  - `processing.py`: Data cleaning, transformation, and feature engineering logic.
  - `analysis.py`: Analytical routines, metrics calculation, and reporting.
  - `api/`: (Optional) Contains code for exposing data via an API (e.g., FastAPI or Flask).
- **tests/**: Unit and integration tests to ensure code correctness.
- **.env**: Stores environment variables such as database credentials (should not be committed to git).
- **.gitignore**: Specifies files and folders to be ignored by git (e.g., `data/`, `.env`).
- **requirements.txt**: Lists Python dependencies for the project.
- **README.md**: Project overview, setup instructions, and usage examples.
- **setup.py**: (Optional) For packaging the project as a Python module for distribution.

---

This structure is flexible and can be adapted for data science, analytics, ETL, or data engineering projects. The API is just a submodule, not the main focus—use it only if you want to expose data via HTTP.

---

## Testing the API with curl

Once your FastAPI server is running (by default at http://127.0.0.1:8000), you can test the endpoints using curl:

### List Reports (first 10)

```bash
curl "http://127.0.0.1:8000/reports"
```

### List Reports (with pagination)

```bash
curl "http://127.0.0.1:8000/reports?limit=5&offset=10"
```

### Get a Report by ID (e.g., ID 1)

```bash
curl "http://127.0.0.1:8000/reports/1"
```

### Filter Reports (e.g., by commodity)

```bash
curl "http://127.0.0.1:8000/reports/filter?commodity=IRON"
```

#### Filter by year and company

```bash
curl "http://127.0.0.1:8000/reports/filter?year=1970&company=MINOPS"
```

### Get Report Geometry (e.g., ID 1)

```bash
curl "http://127.0.0.1:8000/reports/1/geometry"
```

You can also visit [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) in your browser for an interactive Swagger UI to try all endpoints.
