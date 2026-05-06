# Urban Pulse — NYC Taxi Mobility Explorer

A fullstack data analytics platform for exploring urban movement patterns across 7.6 million NYC Yellow Taxi trips (January 2019).

**Live app:** https://dazzling-dusk-4b3f37.netlify.app

**API:** https://urban-mobility-data-explorer-y6h6.onrender.com/apidocs/

---

## What it does

Urban Pulse ingests the full January 2019 NYC TLC dataset (7.6M trips), runs a cleaning pipeline that removes invalid records (outlier fares, zero passengers, time violations), engineers five new features per trip, and exposes the cleaned data through a REST API. A browser dashboard visualises the data with 8 interactive charts and real-time filters.

The API serves a 10,000-trip random sample — a deliberate trade-off for the free hosting tier. The full pipeline processes all 7.6M rows locally before sampling.

---

## Quick Start

### Prerequisites
- Python 3.11+
- Git

### 1. Clone and setup backend

```bash
git clone https://github.com/davidmuo/Urban-Mobility-Data-Explorer.git
cd Urban-Mobility-Data-Explorer/backend
pip install -r requirements.txt
```

### 2. Download data files

Download into `backend/data/raw/`:

| File | Source | Size |
|------|--------|------|
| `yellow_tripdata_2019-01.csv` | [NYC TLC Trip Data](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page) | ~687 MB |
| `taxi_zone_lookup.csv` | [TLC Lookup Table](https://d37ci6vzurychx.cloudfront.net/misc/taxi_zone_lookup.csv) | 12 KB |
| `taxi_zones.zip` | [TLC Spatial Metadata](https://d37ci6vzurychx.cloudfront.net/misc/taxi_zones.zip) | ~850 KB |

### 3. Run data pipeline

```bash
cd backend

# Clean raw data (outputs 7.5M cleaned rows)
python scripts/clean_data.py

# Load random 10k sample into DB
python -c "
import pandas as pd
from app import create_app
from app.extensions import db
app = create_app()
with app.app_context():
    db.create_all()
    df = pd.read_csv('data/processed/cleaned_trips.csv')
    sample = df.sample(n=10000, random_state=42)
    sample = sample.rename(columns={'VendorID':'vendor_id','RatecodeID':'ratecode_id','PULocationID':'pulocation_id','DOLocationID':'dolocation_id'})
    sample.to_sql('trips', db.engine, if_exists='append', index=False)
    print('Loaded', len(sample), 'trips')
"
```

### 4. Start backend

```bash
python run.py
```

Flask runs on `http://127.0.0.1:5000`

### 5. Start frontend

```bash
cd ../frontend
python -m http.server 5500
```

Dashboard loads at `http://127.0.0.1:5500/frontend/index.html`

### 6. Run tests

```bash
cd backend
pytest tests/ -v
```

---

## Project Structure

```
Urban-Mobility-Data-Explorer/
├── backend/
│   ├── app/
│   │   ├── __init__.py          # Flask app factory
│   │   ├── models.py            # Trip and Zone SQLAlchemy models
│   │   ├── extensions.py        # DB and migration setup
│   │   ├── config.py            # Dual SQLite/PostgreSQL config
│   │   ├── routes/
│   │   │   ├── trips.py         # /api/trips/ endpoints
│   │   │   ├── zones.py         # /api/zones/ endpoints
│   │   │   └── analytics.py     # /api/analytics/ endpoints
│   │   └── services/
│   │       ├── data_processor.py # Cleaning and feature engineering
│   │       └── custom_algorithm.py # Custom QuickSort algorithm
│   ├── tests/
│   │   ├── conftest.py          # Pytest fixtures and in-memory DB seed
│   │   ├── test_trips.py        # Trips endpoint tests
│   │   ├── test_zones.py        # Zones endpoint tests
│   │   └── test_analytics.py    # Analytics endpoint tests
│   ├── scripts/
│   │   ├── clean_data.py        # Data cleaning pipeline
│   │   └── load_data.py         # Database loader
│   ├── run.py                   # Entry point
│   └── requirements.txt
├── frontend/
│   ├── index.html               # Dashboard page
│   ├── css/style.css            # Warm theme styling
│   └── js/
│       ├── charts.js            # 8 Chart.js visualizations
│       └── main.js              # API integration, filters, search
└── README.md
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/trips/?per_page=N` | Paginated trip records with optional filters |
| GET | `/api/zones/` | All taxi zones with borough info |
| GET | `/api/zones/<id>` | Single zone by location ID |
| GET | `/api/analytics/top-routes` | Top routes via custom QuickSort |

Full interactive docs available at `/apidocs/` when running locally.

---

## Database

Dual-database support via environment variable:

```bash
# SQLite (default — zero config)
python run.py

# PostgreSQL
export DB_TYPE=postgres
export DATABASE_URL=postgresql://user:pass@localhost:5432/nyc_db
python run.py
```

**Schema:** Normalised with `trips` (fact) and `zones` (dimension) tables. Foreign keys on `pulocation_id` and `dolocation_id` reference `zones.location_id`.

---

## Data Pipeline

| Step | Input | Output | Records |
|------|-------|--------|---------|
| Raw data | yellow_tripdata_2019-01.csv | — | 7,667,792 |
| Cleaning | Raw CSV | cleaned_trips.csv | 7,535,237 (98.3%) |
| Sampling | Cleaned CSV | SQLite DB | 10,000 |

**Cleaning removes:** zero passengers (117K), invalid fares (9.5K), time violations (5.7K), distance outliers (>200mi), fare outliers (>$500)

**Features engineered:** trip_duration_minutes, trip_speed_mph, fare_per_mile, is_weekend, time_of_day_category

---

## Custom Algorithm

**ManualTopRoutesAnalyzer** (`backend/app/services/custom_algorithm.py`)

Identifies the most popular pickup-dropoff zone pairs using:
1. Manual hash map for frequency counting (no Counter)
2. Custom QuickSort for ranking (no built-in sort)

Complexity: O(n + k log k) average, where n = trips, k = unique routes

---

## Dashboard Features

- 8 interactive charts (speed histogram, duration distribution, scatter plots, borough bars, payment donut, hourly volume with fare overlay, fare-distance correlation, day×hour heatmap)
- Animated KPI counter cards
- Functional search bar with section navigation
- Vendor/passenger/date filters with real-time chart updates
- CSV export of filtered data
- Toast notifications
- Scroll-spy sidebar navigation
- Responsive design (mobile breakpoints)

Built with vanilla JS and Chart.js — no frontend framework, demonstrating core DOM and async patterns without build tooling.

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Frontend | HTML5, CSS3, Vanilla JS ES6+, Chart.js |
| Backend | Python, Flask, SQLAlchemy, Alembic |
| Database | SQLite (dev) / PostgreSQL (prod) |
| Data Processing | Pandas, NumPy |
| Testing | Pytest |
| Deployment | Render (backend), GitHub Actions (keep-alive cron) |

---

## Author

David Muotoh-Francis — Frontend dashboard, backend API, data pipeline, custom algorithm, deployment config
