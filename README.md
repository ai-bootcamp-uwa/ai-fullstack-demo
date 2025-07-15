# ai-fullstack-demo

This project is a data foundation project for geospatial exploration reports.

## Project Setup

- All dependencies and project metadata are now managed in `pyproject.toml` (PEP 621 standard).
- `setup.py` is no longer used or required.
- Data files (such as shapefiles and large datasets) are excluded from version control via `.gitignore`.

## Installation

To install the project and all dependencies, run:

```bash
pip install -e ./data_foundation_project
```

Or, for a regular install:

```bash
pip install ./data_foundation_project
```

## API Usage

See the documentation in `docs/` for API usage and curl examples (if available).

## Notes

- For development, use `requirements.txt` for any additional dev/test tools.
- For modern Python packaging, see the `pyproject.toml` for all dependencies and metadata.
