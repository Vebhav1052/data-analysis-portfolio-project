# E-Commerce Data Analysis

A data analysis project I built using **500K+ e-commerce transactions** from a real online retail dataset. This is my first serious portfolio project where I worked through the entire analytics pipeline - from messy data to insights.

## Why I Did This

I wanted to practice end-to-end data analysis. The dataset had realistic problems (missing values, inconsistent formats, outliers) that I had to work through. Instead of just running commands, I had to think about *why* each step mattered.

## The Problem

I was given raw transaction data with ~500,000 rows. It had issues:
- Negative quantities (returns/cancellations)
- Missing customer IDs
- Text formatting inconsistencies
- Duplicate entries

I needed to figure out how to clean it, analyze it, and find actual business insights from it.

## What I Actually Did

**1. Data Cleaning** (`01_data_cleaning.py`)
- Removed null values and duplicates
- Fixed negative quantities and prices
- Handled edge cases like invoice cancellations

**2. Exploratory Analysis** (`02_exploratory_analysis.py`)
- Created visualizations (histograms, scatter plots, time series)
- Looked at customer behavior, product performance, geographic spread

**3. Statistical Analysis** (`03_statistical_analysis.py`)
- Calculated correlations and patterns
- Ran basic statistics to validate findings
- Created SQL queries to test hypotheses

**4. Built a Web Interface** (`app.py`)
- Flask app to display the analysis
- Interactive dashboard with charts
- Learned how to structure Python backends with Flask

## What I Discovered

- **Most customers are one-time buyers**: Only ~25% made more than one purchase
- **Customer concentration**: I noticed that top 20% of customers bring most of the revenue - which matches what's known as the Pareto principle
- **Geographic**: Heavily UK-focused (80%+). Most EU countries barely show up
- **Seasonal patterns**: Big spike in November-December (holiday shopping)
- **Product returns**: Some items have higher return rates, worth investigating

## How to Run It

**1. Get the data**
```bash
# Download OnlineRetail.csv from Kaggle
# https://www.kaggle.com/datasets/vijayuyadav/online-retail-dataset
# Place it in the data/ folder as "OnlineRetail.csv"
```

**2. Install packages**
```bash
pip install -r requirements.txt
```

**3. Run the analysis**
```bash
# Option A: Run everything at once
python end_to_end_analysis.py

# Option B: Open the web interface
python app.py
# Then go to http://localhost:5000
```

Results will appear in `results/` and `notebooks/visualizations/`

## What's in Here

```
├── end_to_end_analysis.py    - Runs all analysis at once
├── app.py                     - Flask web server
├── src/                       - Separate analysis modules
│   ├── 01_data_cleaning.py
│   ├── 02_exploratory_analysis.py
│   └── 03_statistical_analysis.py
├── sql_queries/               - Custom SQL analysis scripts
├── templates/                 - HTML pages for the web app
├── static/                    - CSS styling
├── results/                   - Generated analysis outputs
└── data/                      - Where you put the CSV
```

## Tech I Used

- **Python**: Pandas (data cleaning), NumPy (calculations), Matplotlib & Seaborn (charts)
- **Web**: Flask (backend), HTML/CSS (frontend)
- **Database**: SQL (querying and analysis)
- **Tools**: Jupyter notebooks for exploration

## What I Learned

1. **Real data is messy** - Took longer than expected to get it clean
2. **Visualization matters** - Same data told different stories depending on how I visualized it
3. **SQL is powerful** - Some analyses were way easier to write in SQL than pandas
4. **Web apps are cool** - Flask made it easy to share findings beyond just showing CSV exports
5. **Hypothesis testing** - Starting with a question (not just exploring randomly) was way more useful

## If This Dataset Was Much Larger

With 50M+ rows instead of 500K, I'd:
- Move from CSV files to a real database (PostgreSQL) for better performance
- Add indexes on CustomerID and InvoiceDate to speed up queries
- Do aggregations in SQL instead of loading everything into pandas (memory limits)
- Use chunk processing to read the data in smaller batches instead of all at once
- Consider PySpark if processing started taking hours instead of minutes

Right now pandas works fine, but this approach lets me think about real-world scalability.
