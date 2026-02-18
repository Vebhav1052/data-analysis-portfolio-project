# How This Project Works

## Data Flow

Here's what happens when you run the analysis:

```
Raw CSV (OnlineRetail.csv)
         ↓
   Cleaning Phase
   - Remove missing values
   - Fix duplicates
   - Convert types
         ↓
   Exploratory Phase
   - Create charts
   - Look for patterns
         ↓
   Statistical Phase
   - Calculate metrics
   - Generate insights
         ↓
   Output (results/ folder)
```

## The Main Pieces

**Analysis Scripts** (`src/` folder)
- `01_data_cleaning.py` - Takes raw data and fixes problems (nulls, duplicates, formatting)
- `02_exploratory_analysis.py` - Makes charts and explores what the data looks like
- `03_statistical_analysis.py` - Calculates metrics and finds patterns

**Flask Web App** (`app.py`)
- A simple backend server that runs on localhost
- Shows the analysis results in a web browser
- Routes handle different pages (dashboard, data explorer, etc.)

**Frontend** (`templates/` folder)
- HTML pages: dashboard, visualizations, data tables, help pages
- CSS styling in `static/`
- Bootstrap for responsive design

**SQL Queries** (`sql_queries/` folder)
- Raw SQL files for testing hypotheses
- Can run independently or from Python

## How to Run

**Option 1: Web Dashboard**
```bash
python app.py
# Open http://localhost:5000
```

**Option 2: Run All Analysis**
```bash
python end_to_end_analysis.py
# Outputs go to results/ and notebooks/visualizations/
```

## What You Need

- Python 3.8+
- Flask (web server)
- Pandas (data processing)
- NumPy (calculations)
- Matplotlib & Seaborn (charts)
- SQL libraries (querying)

All listed in `requirements.txt`
