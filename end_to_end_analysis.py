"""
End-to-end data analysis script
Loads data, cleans it, runs exploratory analysis, and generates visualizations
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
import os

warnings.filterwarnings('ignore')

# Setup visualization
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 5)
plt.rcParams['font.size'] = 10

print(f"\nAnalysis started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# ====================
# 1. Load data
# ====================

print("Loading data...")
try:
    df = pd.read_csv('data/OnlineRetail.csv')
    print(f"✓ Loaded {len(df):,} rows, {len(df.columns)} columns")
except FileNotFoundError:
    print("✗ Error: OnlineRetail.csv not found in data/ folder")
    exit()

print("\nData overview:")
print(f"  Columns: {', '.join(df.columns.tolist())}")
print(f"  Date range: {df['InvoiceDate'].min()} to {df['InvoiceDate'].max()}")
print(f"\nMissing values:")
missing = df.isnull().sum()
for col in df.columns:
    if missing[col] > 0:
        print(f"  {col}: {missing[col]:,} ({100*missing[col]/len(df):.1f}%)")

# ====================
# 2. Clean data
# ====================

print("\n\nCleaning data...")

# Remove missing values
df = df[df['CustomerID'].notna()]
df = df[df['InvoiceNo'].notna()]
print(f"✓ Removed rows with missing customer/invoice ID")

# Remove duplicates
initial = len(df)
df = df.drop_duplicates()
print(f"✓ Removed {initial - len(df):,} duplicate rows")

# Fix data types
df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'], format='%m/%d/%Y %H:%M', errors='coerce')
df['UnitPrice'] = pd.to_numeric(df['UnitPrice'], errors='coerce')
df['Quantity'] = pd.to_numeric(df['Quantity'], errors='coerce')
df['CustomerID'] = df['CustomerID'].astype(str).str.strip()
df['Country'] = df['Country'].astype('category')
print(f"✓ Fixed data types")

# Create derived columns
df['TotalSales'] = df['Quantity'] * df['UnitPrice']
df['Date'] = df['InvoiceDate'].dt.date
df['Month'] = df['InvoiceDate'].dt.month
df['DayOfWeek'] = df['InvoiceDate'].dt.day_name()
df['Quarter'] = df['InvoiceDate'].dt.quarter
print(f"✓ Created derived columns")

# Filter data for analysis (remove returns)
df_sales = df[(df['Quantity'] > 0) & (df['UnitPrice'] > 0)].copy()
df_returns = df[df['Quantity'] < 0].copy()
print(f"✓ Filtered: {len(df_sales):,} sales, {len(df_returns):,} returns")

print(f"\nFinal dataset: {len(df_sales):,} rows ready for analysis")

# ====================
# 3. Exploratory analysis
# ====================

print("\n\nExploring data...")

# Basic metrics
total_revenue = df_sales['TotalSales'].sum()
num_customers = df_sales['CustomerID'].nunique()
num_products = df_sales['StockCode'].nunique()
num_countries = df_sales['Country'].nunique()
avg_order = df_sales['TotalSales'].mean()

print(f"\nMetrics:")
print(f"  Total revenue: £{total_revenue:,.0f}")
print(f"  Customers: {num_customers:,}")
print(f"  Products: {num_products:,}")
print(f"  Countries: {num_countries}")
print(f"  Average order value: £{avg_order:.2f}")

# Customer analysis
customer_sales = df_sales.groupby('CustomerID').agg({
    'TotalSales': 'sum',
    'InvoiceNo': 'nunique',
    'Quantity': 'sum'
}).rename(columns={'InvoiceNo': 'NumTransactions', 'Quantity': 'NumItems'})

print(f"\nCustomer behavior:")
repeat_pct = (customer_sales['NumTransactions'] > 1).sum() / len(customer_sales) * 100
print(f"  Repeat customers: {repeat_pct:.1f}%")
print(f"  One-time customers: {100-repeat_pct:.1f}%")

# Revenue concentration
customer_sales_sorted = customer_sales.sort_values('TotalSales', ascending=False)
top20_revenue = customer_sales_sorted.head(int(0.2*len(customer_sales)))['TotalSales'].sum()
concentration = top20_revenue / total_revenue * 100
print(f"  Top 20% of customers: {concentration:.0f}% of revenue")

# Geography
country_sales = df_sales.groupby('Country')['TotalSales'].sum().sort_values(ascending=False)
top_country = country_sales.iloc[0]
top_country_pct = top_country / total_revenue * 100
print(f"\nGeography:")
print(f"  Top country ({country_sales.index[0]}): {top_country_pct:.0f}% of revenue")
print(f"  Top 5 countries:")
for i, (country, revenue) in enumerate(country_sales.head(5).items(), 1):
    pct = revenue / total_revenue * 100
    print(f"    {i}. {country}: {pct:.0f}%")

# Seasonality
monthly_sales = df_sales.groupby('Month')['TotalSales'].sum()
print(f"\nSeasonality (by month):")
for month, sales in monthly_sales.items():
    pct = sales / monthly_sales.mean() * 100
    print(f"  Month {month:2d}: £{sales:>10,.0f} ({pct:>3.0f}% of average)")

# Product analysis
product_sales = df_sales.groupby('StockCode')['TotalSales'].sum().sort_values(ascending=False)
top20_products = product_sales.head(int(0.2*len(product_sales)))
product_concentration = top20_products.sum() / total_revenue * 100
print(f"\nProducts:")
print(f"  Top 20% of products: {product_concentration:.0f}% of revenue")

# ====================
# 4. Statistical analysis
# ====================

print("\n\nStatistical analysis...")

# Correlation analysis
numeric_cols = df_sales[['Quantity', 'UnitPrice', 'TotalSales']].select_dtypes(include=[np.number])
print(f"\nCorrelations:")
for col1 in numeric_cols.columns:
    for col2 in numeric_cols.columns:
        if col1 < col2:
            corr = df_sales[col1].corr(df_sales[col2])
            print(f"  {col1} vs {col2}: {corr:.3f}")

# Price sensitivity (avg price vs quantity sold)
price_quartiles = pd.qcut(df_sales['UnitPrice'], q=4, duplicates='drop')
price_qty = df_sales.groupby(price_quartiles)['Quantity'].mean()
print(f"\nPrice vs Quantity (lower price = more units?):")
for price_range, qty in price_qty.items():
    print(f"  {price_range}: avg {qty:.0f} units")

print("\n✓ Analysis complete!")
print(f"Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# ====================
# 5. Save outputs
# ====================

print("Saving outputs...")

# Save cleaned data
os.makedirs('results', exist_ok=True)
df_sales.to_csv('results/cleaned_data.csv', index=False)
print(f"✓ Saved: results/cleaned_data.csv")

# Save summary statistics
summary = {
    'Total Revenue': f"£{total_revenue:,.0f}",
    'Customers': f"{num_customers:,}",
    'Products': f"{num_products:,}",
    'Countries': f"{num_countries}",
    'Transactions': f"{len(df_sales):,}",
    'Avg Order Value': f"£{avg_order:.2f}",
    'Repeat Rate': f"{repeat_pct:.1f}%",
    'Top Customer Market Share': f"{concentration:.0f}%",
    'Top Country Market Share': f"{top_country_pct:.0f}%",
}

summary_df = pd.DataFrame(list(summary.items()), columns=['Metric', 'Value'])
summary_df.to_csv('results/summary.csv', index=False)
print(f"✓ Saved: results/summary.csv")

print(f"\nDone! Check results/ folder for outputs.")
