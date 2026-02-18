E-Commerce Data Analysis (500K+ Transactions)
This is an end-to-end data analysis project I built using around 500,000 real-world e-commerce transactions from an online retail dataset.
I created this project to practice real data analysis — not just small practice problems, but working with messy, large-scale data and extracting meaningful insights from it. This is my first complete portfolio project where I handled everything from raw data to a working web dashboard.

Why I Built This
While learning data analytics, I realized that most examples use very clean datasets. But real-world data is never clean.
So I decided to work on a large dataset that includes:
Missing values
Negative quantities (returns and cancellations)
Duplicate records
Inconsistent formatting

Outliers
My goal was to simulate what a real data analyst would do — clean the data, analyze patterns, validate findings, and present insights properly.

Dataset Overview
~500,000 transaction records
Online retail sales data
Includes invoice numbers, products, quantities, prices, customers, countries, and timestamps
The dataset mainly focuses on UK-based retail transactions but also includes other countries.

What I Did
1️⃣ Data Cleaning (01_data_cleaning.py)
I started by preparing the data:
Removed duplicate rows
Handled missing Customer IDs
Managed negative quantities (returns) carefully
Removed unrealistic price or quantity values
Standardized formatting.
This step took more time than I expected, but it helped me understand how important clean data is before analysis.

2️⃣ Exploratory Data Analysis (02_exploratory_analysis.py)
After cleaning, I explored the dataset to understand patterns:
Revenue trends over time
Customer purchase frequency
Top-selling products
Country-wise distribution
Return rate patterns.
I created visualizations using Matplotlib and Seaborn to make patterns easier to understand.

3️⃣ Statistical & SQL Analysis (03_statistical_analysis.py)
To validate observations, I:
Calculated correlations
Measured revenue concentration
Analyzed repeat customer behavior
Used SQL queries to test aggregations and hypotheses
This helped me compare pandas-based analysis with SQL-based analysis.

4️⃣ Built a Flask Web App (app.py)
To make the project more practical, I built a simple Flask web application:
Displays insights through multiple routes
Uses HTML templates for structure
Styled with basic CSS
Allows easy viewing of results
This helped me understand how backend analysis connects with frontend presentation.

Key Insights I Found
Around 75% of customers made only one purchase.
A small percentage of customers generate most of the revenue (Pareto effect).
The majority of revenue comes from the UK.
There is a clear sales spike in November–December (holiday season).
Some products show noticeably higher return rates.

How to Run This Project
1️⃣ Download Dataset
Download the dataset from Kaggle:
https://www.kaggle.com/datasets/vijayuyadav/online-retail-dataset
Place the file inside the data/ folder as:
OnlineRetail.csv

2️⃣ Install Dependencies
pip install -r requirements.txt

3️⃣ Run the Analysis
Option A – Run Full Pipeline
python end_to_end_analysis.py
Option B – Run Web App
python app.py
Then open:
http://localhost:5000
Results will be generated inside the results/ folder.

Project Structure
├── end_to_end_analysis.py
├── app.py
├── src/
│   ├── 01_data_cleaning.py
│   ├── 02_exploratory_analysis.py
│   └── 03_statistical_analysis.py
├── sql_queries/
├── templates/
├── static/
├── results/
└── data/

Tools & Technologies Used
Python (Pandas, NumPy)
Matplotlib & Seaborn
Flask
SQL
Jupyter Notebook

What I Learned
Real-world data cleaning is more challenging than expected.
Visualization helps reveal patterns that raw numbers cannot.
SQL can sometimes simplify aggregation-heavy tasks.
Structuring code into modules improves clarity and maintainability.
Building a web app makes analysis more interactive and presentable.

If This Dataset Were Much Larger
If this dataset had 50M+ rows instead of 500K, I would:
Use PostgreSQL instead of CSV files
Add indexing on key columns
Perform aggregations in SQL
Use chunk processing in pandas
Consider PySpark for distributed processing
Right now, pandas works efficiently at this scale, but I tried to think about scalability as well.

This project helped me understand how data analysis works beyond tutorials. It gave me practical experience in cleaning, exploring, validating, and presenting data in a structured way.


