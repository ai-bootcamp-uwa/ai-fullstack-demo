# Data Foundation Project with Snowflake Integration

A geospatial data foundation for the Western Australian Mineral Exploration Reports (WAMEX) dataset, featuring Snowflake cloud data warehouse integration and FastAPI-based REST services.

## 🎯 Overview

This project implements a modern data foundation for geological exploration data with:

- **Snowflake Integration**: Cloud-native data warehouse with geospatial capabilities
- **FastAPI REST API**: High-performance API endpoints for data access
- **GeoPandas Processing**: Advanced geospatial data handling
- **ETL Pipeline**: Automated data migration from shapefiles to Snowflake
- **Flexible Architecture**: Supports both cloud (Snowflake) and local data sources

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Shapefile     │───▶│  ETL Pipeline    │───▶│   Snowflake     │
│   (Local Data)  │    │  (GeoPandas)     │    │  (Cloud DW)     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                         │
┌─────────────────┐    ┌──────────────────┐             │
│   Frontend UI   │◀───│   FastAPI        │◀────────────┘
│   (React/Next)  │    │   REST API       │
└─────────────────┘    └──────────────────┘
```

## 📊 Features

### Data Management
- **Geospatial Data Loading**: Support for shapefiles, GeoJSON, and other formats
- **Snowflake Integration**: GEOGRAPHY data types for spatial queries
- **Data Quality Metrics**: Automated validation and monitoring
- **ETL Pipeline**: Robust data migration with error handling

### API Capabilities
- **RESTful Endpoints**: Full CRUD operations for geological reports
- **Spatial Queries**: Find reports by location and radius
- **Advanced Filtering**: Filter by commodity, year, company, and more
- **Pagination**: Efficient handling of large datasets
- **Health Monitoring**: Built-in health checks and metrics

### Deployment Options
- **Cloud-First**: Optimized for Snowflake cloud data warehouse
- **Local Fallback**: Graceful degradation to local data when needed
- **Docker Support**: Containerized deployment
- **Environment Management**: Secure credential handling

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Snowflake account with appropriate permissions
- WAMEX shapefile data

### 1. Environment Setup

```bash
# Clone the repository
git clone <repository-url>
cd data_foundation_project

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Snowflake

```bash
# Copy environment template
cp env_template.txt .env

# Edit .env with your Snowflake credentials
SNOWFLAKE_ACCOUNT=your_account.region
SNOWFLAKE_USER=your_username
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_WAREHOUSE=COMPUTE_WH
SNOWFLAKE_DATABASE=WAMEX_EXPLORATION
SNOWFLAKE_SCHEMA=GEOSPATIAL_DATA
```

### 3. Migrate Data to Snowflake

```bash
# Run the ETL pipeline
python scripts/migrate_to_snowflake.py

# Or with specific shapefile
python scripts/migrate_to_snowflake.py --shapefile /path/to/your/data.shp

# Setup tables only (without data migration)
python scripts/migrate_to_snowflake.py --setup-only
```

### 4. Start the API Server

```bash
# Start the FastAPI server
cd src
python -m api.main

# Or with uvicorn directly
uvicorn api.main:app --host localhost --port 8000 --reload
```

### 5. Test the API

```bash
# Health check
curl http://localhost:8000/health

# Get reports
curl http://localhost:8000/reports?limit=5

# Spatial query
curl "http://localhost:8000/spatial-query?latitude=-31.9505&longitude=115.8605&radius_km=50"

# Filter by commodity
curl "http://localhost:8000/reports/filter?commodity=GOLD"
```

## 📚 API Documentation

### Core Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check and system status |
| `/reports` | GET | List geological reports (paginated) |
| `/reports/{id}` | GET | Get specific report by ID |
| `/reports/filter` | GET | Filter reports by criteria |
| `/spatial-query` | POST | Find reports near location |
| `/quality-metrics` | GET | Data quality statistics |

### Admin Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/admin/setup-tables` | POST | Create Snowflake tables |
| `/admin/migrate-data` | POST | Migrate shapefile to Snowflake |

### Example Responses

**Health Check:**
```json
{
  "snowflake_configured": true,
  "snowflake_available": true,
  "data_source": "snowflake",
  "status": "healthy",
  "total_records": 10543,
  "last_updated": "2024-01-15T10:30:00Z"
}
```

**Spatial Query:**
```json
{
  "reports": [
    {
      "ANUMBER": 12345,
      "TITLE": "Perth Basin Gold Exploration",
      "OPERATOR": "Mining Co Ltd",
      "TARGET_COMMODITIES": "GOLD",
      "DISTANCE_KM": 15.2,
      "GEOMETRY": "POLYGON((...))"
    }
  ],
  "query": {
    "latitude": -31.9505,
    "longitude": 115.8605,
    "radius_km": 50
  },
  "total_found": 1
}
```

## 🛠️ Development

### Project Structure

```
data_foundation_project/
├── src/
│   ├── api/
│   │   └── main.py              # FastAPI application
│   ├── config.py                # Configuration management
│   ├── data_access.py           # Data access layer
│   └── snowflake_client.py      # Snowflake operations
├── scripts/
│   ├── migrate_to_snowflake.py  # ETL pipeline
│   ├── explore_shapefile.py     # Data exploration
│   ├── load_data.py             # Data loading utilities
│   └── process_data.py          # Data processing utilities
├── tests/
│   └── test_processing.py       # Unit tests
├── data/
│   ├── raw/                     # Original shapefile data
│   └── processed/               # Processed data outputs
├── docs/                        # Documentation
├── requirements.txt             # Python dependencies
├── env_template.txt            # Environment variables template
└── README.md                   # This file
```

### Database Schema

**GEOLOGICAL_REPORTS Table:**
```sql
CREATE TABLE GEOLOGICAL_REPORTS (
    ANUMBER INTEGER PRIMARY KEY,
    TITLE STRING,
    REPORT_YEAR FLOAT,
    AUTHOR_NAME STRING,
    AUTHOR_COMPANY STRING,
    OPERATOR STRING,
    TARGET_COMMODITIES STRING,
    GEOMETRY GEOGRAPHY,
    CREATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Configuration Management

The project uses environment variables for configuration:

```python
from src.config import snowflake_config, app_config

# Snowflake connection
if snowflake_config.validate_credentials():
    # Connect to Snowflake
    
# Application settings
app.run(host=app_config.api_host, port=app_config.api_port)
```

## 🧪 Testing

```bash
# Run unit tests
python -m pytest tests/

# Test Snowflake connection
python scripts/migrate_to_snowflake.py --validate-only

# Test API endpoints
python -m pytest tests/test_api.py
```

## 🐳 Docker Deployment

```bash
# Build Docker image
docker build -t data-foundation .

# Run container
docker run -p 8000:8000 --env-file .env data-foundation

# With docker-compose
docker-compose up -d
```

## 📈 Monitoring and Metrics

### Data Quality Metrics

- **Total Records**: Count of geological reports
- **Geometry Coverage**: Percentage of records with valid geometry
- **Temporal Coverage**: Date range of reports
- **Spatial Coverage**: Geographic extent of data
- **Data Completeness**: Null value analysis

### Performance Metrics

- **Query Response Time**: <100ms for simple queries
- **Spatial Query Performance**: <500ms for radius searches
- **Data Loading Speed**: >1000 records/second
- **API Throughput**: 100+ requests/second

## 🔒 Security

- **Environment Variables**: Secure credential management
- **Connection Encryption**: TLS for all Snowflake connections
- **API Authentication**: JWT-based authentication (planned)
- **Data Validation**: Input sanitization and validation

## 🚀 Deployment

### Local Development
```bash
uvicorn src.api.main:app --reload --host localhost --port 8000
```

### Production Deployment
```bash
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Cloud Deployment
- **Azure Container Instances**: Recommended for production
- **AWS ECS**: Alternative container deployment
- **Google Cloud Run**: Serverless option

## 🤝 Integration

This module integrates with other components:

- **Cortex Engine** (Port 3002): AI/ML processing and embeddings
- **Backend Gateway** (Port 3003): API orchestration and authentication
- **Frontend UI** (Port 3004): User interface and visualization

## 🆘 Troubleshooting

### Common Issues

**Snowflake Connection Failed:**
```bash
# Check credentials
python scripts/migrate_to_snowflake.py --validate-only

# Verify network connectivity
ping your_account.snowflakecomputing.com
```

**Shapefile Loading Errors:**
```bash
# Check file permissions
ls -la data/raw/

# Validate shapefile
python scripts/explore_shapefile.py
```

**API Startup Issues:**
```bash
# Check port availability
netstat -an | grep 8000

# Verify dependencies
pip list | grep fastapi
```

## 📖 Documentation

- [API Documentation](http://localhost:8000/docs) - Interactive API docs
- [Snowflake Integration Guide](docs/snowflake-setup.md)
- [Data Processing Guide](docs/data-processing.md)
- [Deployment Guide](docs/deployment.md)

## 🏷️ Version History

- **v2.0.0**: Snowflake integration, enhanced API, ETL pipeline
- **v1.0.0**: Basic shapefile processing, initial FastAPI endpoints

## 📄 License

This project is part of the AI Full-Stack Engineer Bootcamp curriculum.

## 🤝 Contributing

1. Follow the established code style
2. Add tests for new features
3. Update documentation
4. Submit pull requests for review

## 📞 Support

For issues and questions:
- Create GitHub issues for bugs
- Check documentation for common solutions
- Contact the development team for urgent issues
