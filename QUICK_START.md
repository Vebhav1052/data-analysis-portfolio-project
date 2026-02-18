# Quick Start

## Setup (5 minutes)

1. **Download data**
   - Get `OnlineRetail.csv` from [Kaggle](https://www.kaggle.com/datasets/vijayuyadav/online-retail-dataset)
   - Place it in `data/` folder

2. **Install packages**
   ```bash
   pip install -r requirements.txt
   ```

3. **Verify it works**
   ```python
   import pandas as pd
   df = pd.read_csv('data/OnlineRetail.csv')
   print(df.shape)  # Should show (541909, 9)
   ```

## Run Analysis

**Option 1: Quick web interface**
```bash
python app.py
# Open http://localhost:5000
```

**Option 2: Run everything**
```bash
python end_to_end_analysis.py
# Results in results/ and notebooks/visualizations/
```

## What Each Script Does

- `01_data_cleaning.py` - Removes nulls, duplicates, fixes formatting
- `02_exploratory_analysis.py` - Makes charts and explores data
- `03_statistical_analysis.py` - Calculates metrics and finds patterns

Done. Results go to `results/` folder.
