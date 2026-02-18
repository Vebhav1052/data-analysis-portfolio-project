"""
Exploratory Data Analysis (EDA) Script
======================================

Comprehensive EDA with visualizations to understand data patterns.
Focus on business-relevant insights.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import logging

# Setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)


class ExploratoryDataAnalysis:
    def __init__(self, data_path):
        """Load cleaned data"""
        self.df = pd.read_csv(data_path)
        self.df['InvoiceDate'] = pd.to_datetime(self.df['InvoiceDate'])
        self.figures_saved = []
        logger.info(f"Loaded data: {len(self.df)} rows")
    
    def save_figure(self, filename, title):
        """Save figure and track it"""
        filepath = f'notebooks/visualizations/{filename}'
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        self.figures_saved.append({'filename': filename, 'title': title})
        logger.info(f"Saved: {filename}")
    
    # ==================== PHASE 1: UNIVARIATE ANALYSIS ====================
    
    def analyze_sales_distribution(self):
        """Analyze distribution of sales values"""
        logger.info("\n=== PHASE 1: Univariate Analysis ===")
        logger.info("Analyzing Sales Distribution...")
        
        print("\nSales Statistics:")
        print(f"Mean Sales: £{self.df['TotalSales'].mean():.2f}")
        print(f"Median Sales: £{self.df['TotalSales'].median():.2f}")
        print(f"Std Dev: £{self.df['TotalSales'].std():.2f}")
        print(f"Min: £{self.df['TotalSales'].min():.2f}")
        print(f"Max: £{self.df['TotalSales'].max():.2f}")
        print(f"Skewness: {self.df['TotalSales'].skew():.2f} (Right-skewed means outliers)")
        
        # Create visualization
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        
        # Histogram
        axes[0].hist(self.df['TotalSales'], bins=50, edgecolor='black', color='skyblue')
        axes[0].set_xlabel('Sales Amount (£)')
        axes[0].set_ylabel('Frequency')
        axes[0].set_title('Distribution of Sales (All Transactions)')
        axes[0].grid(axis='y', alpha=0.3)
        
        # Histogram with log scale (better for right-skewed)
        axes[1].hist(self.df['TotalSales'], bins=50, edgecolor='black', color='coral')
        axes[1].set_xlabel('Sales Amount (£)')
        axes[1].set_ylabel('Frequency (Log Scale)')
        axes[1].set_yscale('log')
        axes[1].set_title('Distribution of Sales (Log Scale)')
        axes[1].grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        self.save_figure('01_sales_distribution.png', 'Sales Distribution Analysis')
        
        # Box plot to show outliers
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.boxplot(self.df['TotalSales'], vert=True)
        ax.set_ylabel('Sales Amount (£)')
        ax.set_title('Box Plot of Sales (Shows Outliers)')
        ax.grid(axis='y', alpha=0.3)
        plt.tight_layout()
        self.save_figure('02_sales_boxplot.png', 'Sales Box Plot')
    
    def analyze_quantity_distribution(self):
        """Analyze quantity purchased per transaction"""
        logger.info("Analyzing Quantity Distribution...")
        
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        
        axes[0].hist(self.df['Quantity'], bins=50, edgecolor='black', color='lightgreen')
        axes[0].set_xlabel('Quantity (units)')
        axes[0].set_ylabel('Frequency')
        axes[0].set_title('Distribution of Quantity Purchased')
        axes[0].grid(axis='y', alpha=0.3)
        
        axes[1].hist(self.df['UnitPrice'], bins=50, edgecolor='black', color='orange')
        axes[1].set_xlabel('Unit Price (£)')
        axes[1].set_ylabel('Frequency')
        axes[1].set_title('Distribution of Unit Price')
        axes[1].grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        self.save_figure('03_quantity_price_distribution.png', 'Quantity & Price Distribution')
    
    # ==================== PHASE 2: BIVARIATE ANALYSIS ====================
    
    def analyze_top_countries(self):
        """Top countries by revenue"""
        logger.info("\n=== PHASE 2: Bivariate Analysis ===")
        logger.info("Analyzing Top Countries...")
        
        country_sales = self.df.groupby('Country').agg({
            'TotalSales': 'sum',
            'CustomerID': 'nunique',
            'InvoiceNo': 'count'
        }).round(2)
        country_sales.columns = ['TotalRevenue', 'UniqueCustomers', 'Transactions']
        country_sales = country_sales.sort_values('TotalRevenue', ascending=False).head(15)
        
        print("\nTop 15 Countries by Revenue:")
        print(country_sales)
        
        # Visualization: Top countries
        fig, axes = plt.subplots(2, 1, figsize=(12, 10))
        
        # Revenue by country
        top_countries_rev = country_sales['TotalRevenue'].head(10)
        axes[0].barh(range(len(top_countries_rev)), top_countries_rev.values, color='steelblue')
        axes[0].set_yticks(range(len(top_countries_rev)))
        axes[0].set_yticklabels(top_countries_rev.index)
        axes[0].set_xlabel('Total Revenue (£)')
        axes[0].set_title('Top 10 Countries by Revenue')
        axes[0].invert_yaxis()
        
        # Add value labels
        for i, v in enumerate(top_countries_rev.values):
            axes[0].text(v + 100, i, f'£{v:,.0f}', va='center')
        
        # Unique customers by country
        top_customers = country_sales['UniqueCustomers'].head(10)
        axes[1].barh(range(len(top_customers)), top_customers.values, color='coral')
        axes[1].set_yticks(range(len(top_customers)))
        axes[1].set_yticklabels(top_customers.index)
        axes[1].set_xlabel('Number of Unique Customers')
        axes[1].set_title('Top 10 Countries by Customer Count')
        axes[1].invert_yaxis()
        
        plt.tight_layout()
        self.save_figure('04_top_countries.png', 'Top Countries Analysis')
    
    def analyze_top_products(self):
        """Top products by revenue and quantity"""
        logger.info("Analyzing Top Products...")
        
        product_sales = self.df.groupby('Description').agg({
            'TotalSales': 'sum',
            'Quantity': 'sum',
            'InvoiceNo': 'count',
            'UnitPrice': 'mean'
        }).round(2)
        product_sales.columns = ['Revenue', 'QuantitySold', 'Transactions', 'AvgPrice']
        product_sales = product_sales.sort_values('Revenue', ascending=False).head(15)
        
        print("\nTop 15 Products by Revenue:")
        print(product_sales)
        
        # Visualization
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        
        # Top products by revenue
        top_10_products = product_sales['Revenue'].head(10)
        axes[0].barh(range(len(top_10_products)), top_10_products.values, color='darkgreen')
        axes[0].set_yticks(range(len(top_10_products)))
        axes[0].set_yticklabels([name[:30] for name in top_10_products.index], fontsize=9)
        axes[0].set_xlabel('Revenue (£)')
        axes[0].set_title('Top 10 Products by Revenue')
        axes[0].invert_yaxis()
        
        # Quantity sold
        top_qty = product_sales['QuantitySold'].sort_values(ascending=False).head(10)
        axes[1].barh(range(len(top_qty)), top_qty.values, color='teal')
        axes[1].set_yticks(range(len(top_qty)))
        axes[1].set_yticklabels([name[:30] for name in top_qty.index], fontsize=9)
        axes[1].set_xlabel('Quantity Sold (units)')
        axes[1].set_title('Top 10 Products by Quantity')
        axes[1].invert_yaxis()
        
        plt.tight_layout()
        self.save_figure('05_top_products.png', 'Top Products Analysis')
    
    def analyze_revenue_vs_customers(self):
        """Relationship between customer count and revenue by country"""
        logger.info("Analyzing Revenue vs Customer Count...")
        
        country_analysis = self.df.groupby('Country').agg({
            'TotalSales': 'sum',
            'CustomerID': 'nunique',
            'InvoiceNo': 'count'
        })
        country_analysis.columns = ['Revenue', 'Customers', 'Transactions']
        
        # Filter for countries with significant revenue
        country_analysis = country_analysis[country_analysis['Revenue'] > 500]
        
        fig, ax = plt.subplots(figsize=(12, 6))
        scatter = ax.scatter(country_analysis['Customers'], 
                           country_analysis['Revenue'],
                           s=country_analysis['Transactions']/2,
                           alpha=0.6, c=country_analysis['Revenue'],
                           cmap='viridis')
        
        ax.set_xlabel('Number of Customers')
        ax.set_ylabel('Total Revenue (£)')
        ax.set_title('Revenue vs Customer Count by Country\n(Bubble size = Transaction count)')
        
        # Label major countries
        for idx, country in enumerate(country_analysis.index):
            if country_analysis.iloc[idx]['Revenue'] > 2000:
                ax.annotate(country, 
                           (country_analysis.iloc[idx]['Customers'],
                            country_analysis.iloc[idx]['Revenue']),
                           fontsize=9, alpha=0.7)
        
        plt.colorbar(scatter, label='Revenue (£)')
        plt.grid(alpha=0.3)
        plt.tight_layout()
        self.save_figure('06_revenue_vs_customers.png', 'Revenue vs Customers')
    
    # ==================== PHASE 3: TIME SERIES ANALYSIS ====================
    
    def analyze_monthly_trends(self):
        """Monthly sales trends"""
        logger.info("\n=== PHASE 3: Time Series Analysis ===")
        logger.info("Analyzing Monthly Trends...")
        
        monthly_sales = self.df.groupby(self.df['InvoiceDate'].dt.to_period('M')).agg({
            'TotalSales': 'sum',
            'CustomerID': 'nunique',
            'InvoiceNo': 'count'
        }).round(2)
        monthly_sales.index = monthly_sales.index.to_timestamp()
        
        print("\nMonthly Sales Summary:")
        print(monthly_sales.tail(10))
        
        # Visualization
        fig, axes = plt.subplots(3, 1, figsize=(14, 10))
        
        # Revenue trend
        axes[0].plot(monthly_sales.index, monthly_sales['TotalSales'], 
                    marker='o', linewidth=2, color='darkblue', markersize=6)
        axes[0].fill_between(monthly_sales.index, monthly_sales['TotalSales'], alpha=0.3)
        axes[0].set_ylabel('Revenue (£)')
        axes[0].set_title('Monthly Revenue Trend')
        axes[0].grid(alpha=0.3)
        
        # Customer trend
        axes[1].plot(monthly_sales.index, monthly_sales['CustomerID'], 
                    marker='s', linewidth=2, color='darkgreen', markersize=6)
        axes[1].set_ylabel('Unique Customers')
        axes[1].set_title('Monthly Active Customers')
        axes[1].grid(alpha=0.3)
        
        # Transaction count
        axes[2].bar(monthly_sales.index, monthly_sales['InvoiceNo'], 
                   width=20, color='coral', alpha=0.7)
        axes[2].set_ylabel('Number of Transactions')
        axes[2].set_xlabel('Month')
        axes[2].set_title('Monthly Transaction Volume')
        axes[2].grid(alpha=0.3, axis='y')
        
        plt.tight_layout()
        self.save_figure('07_monthly_trends.png', 'Monthly Trends')
    
    def analyze_day_of_week(self):
        """Sales patterns by day of week"""
        logger.info("Analyzing Day of Week Patterns...")
        
        self.df['DayOfWeek'] = self.df['InvoiceDate'].dt.day_name()
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        day_sales = self.df.groupby('DayOfWeek')['TotalSales'].agg(['sum', 'count', 'mean'])
        day_sales = day_sales.reindex(day_order)
        
        print("\nSales by Day of Week:")
        print(day_sales)
        
        # Visualization
        fig, axes = plt.subplots(1, 3, figsize=(15, 4))
        
        colors = ['green' if day in ['Friday', 'Saturday', 'Sunday'] else 'steelblue' 
                 for day in day_sales.index]
        
        axes[0].bar(range(len(day_sales)), day_sales['sum'], color=colors, alpha=0.7)
        axes[0].set_xticks(range(len(day_sales)))
        axes[0].set_xticklabels(day_sales.index, rotation=45)
        axes[0].set_ylabel('Total Revenue (£)')
        axes[0].set_title('Revenue by Day of Week')
        axes[0].grid(axis='y', alpha=0.3)
        
        axes[1].bar(range(len(day_sales)), day_sales['count'], color=colors, alpha=0.7)
        axes[1].set_xticks(range(len(day_sales)))
        axes[1].set_xticklabels(day_sales.index, rotation=45)
        axes[1].set_ylabel('Transaction Count')
        axes[1].set_title('Transactions by Day of Week')
        axes[1].grid(axis='y', alpha=0.3)
        
        axes[2].bar(range(len(day_sales)), day_sales['mean'], color=colors, alpha=0.7)
        axes[2].set_xticks(range(len(day_sales)))
        axes[2].set_xticklabels(day_sales.index, rotation=45)
        axes[2].set_ylabel('Average Transaction Value (£)')
        axes[2].set_title('Avg Transaction Value by Day')
        axes[2].grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        self.save_figure('08_day_of_week.png', 'Day of Week Analysis')
    
    # ==================== PHASE 4: CUSTOMER ANALYSIS ====================
    
    def analyze_customer_segments(self):
        """RFM-style customer segmentation"""
        logger.info("\n=== PHASE 4: Customer Analysis ===")
        logger.info("Analyzing Customer Segments...")
        
        # Calculate customer metrics
        customer_analysis = self.df.groupby('CustomerID').agg({
            'InvoiceDate': 'max',
            'InvoiceNo': 'count',
            'TotalSales': 'sum'
        })
        customer_analysis.columns = ['LastPurchase', 'PurchaseFrequency', 'LifetimeValue']
        
        print("\nCustomer Metrics Summary:")
        print(f"Total Customers: {len(customer_analysis)}")
        print(f"Avg Lifetime Value: £{customer_analysis['LifetimeValue'].mean():.2f}")
        print(f"Median Lifetime Value: £{customer_analysis['LifetimeValue'].median():.2f}")
        print(f"Avg Purchase Frequency: {customer_analysis['PurchaseFrequency'].mean():.1f}")
        
        # Segment by lifetime value
        customer_analysis['Segment'] = pd.cut(
            customer_analysis['LifetimeValue'],
            bins=[0, 500, 1500, 5000, float('inf')],
            labels=['Low Value', 'Medium Value', 'High Value', 'Top Tier']
        )
        
        segment_summary = customer_analysis.groupby('Segment').agg({
            'LifetimeValue': ['count', 'sum', 'mean'],
            'PurchaseFrequency': 'mean'
        }).round(2)
        
        print("\nCustomer Segments:")
        print(segment_summary)
        
        # Visualization
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        # Lifetime value distribution
        axes[0, 0].hist(customer_analysis['LifetimeValue'], bins=50, 
                       edgecolor='black', color='skyblue')
        axes[0, 0].set_xlabel('Lifetime Value (£)')
        axes[0, 0].set_ylabel('Number of Customers')
        axes[0, 0].set_title('Distribution of Customer Lifetime Value')
        axes[0, 0].grid(axis='y', alpha=0.3)
        
        # Purchase frequency distribution
        axes[0, 1].hist(customer_analysis['PurchaseFrequency'], bins=30,
                       edgecolor='black', color='lightcoral')
        axes[0, 1].set_xlabel('Purchase Frequency')
        axes[0, 1].set_ylabel('Number of Customers')
        axes[0, 1].set_title('Distribution of Purchase Frequency')
        axes[0, 1].grid(axis='y', alpha=0.3)
        
        # Frequency vs Lifetime Value (scatter)
        scatter = axes[1, 0].scatter(customer_analysis['PurchaseFrequency'],
                                    customer_analysis['LifetimeValue'],
                                    alpha=0.5, s=50, c=customer_analysis['LifetimeValue'],
                                    cmap='viridis')
        axes[1, 0].set_xlabel('Purchase Frequency')
        axes[1, 0].set_ylabel('Lifetime Value (£)')
        axes[1, 0].set_title('Frequency vs Lifetime Value')
        axes[1, 0].grid(alpha=0.3)
        plt.colorbar(scatter, ax=axes[1, 0])
        
        # Segment pie chart
        segment_counts = customer_analysis['Segment'].value_counts()
        axes[1, 1].pie(segment_counts.values, labels=segment_counts.index, autopct='%1.1f%%',
                      colors=['#ff9999', '#ffcc99', '#99ccff', '#99ff99'])
        axes[1, 1].set_title('Customer Distribution by Segment')
        
        plt.tight_layout()
        self.save_figure('09_customer_analysis.png', 'Customer Segmentation')
    
    # ==================== PHASE 5: CORRELATION ANALYSIS ====================
    
    def analyze_correlations(self):
        """Correlation between numeric variables"""
        logger.info("\n=== PHASE 5: Correlation Analysis ===")
        logger.info("Analyzing Correlations...")
        
        # Select numeric columns
        numeric_cols = ['Quantity', 'UnitPrice', 'TotalSales']
        correlation_matrix = self.df[numeric_cols].corr()
        
        print("\nCorrelation Matrix:")
        print(correlation_matrix)
        
        # Visualization: Heatmap
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.heatmap(correlation_matrix, annot=True, fmt='.2f', cmap='coolwarm',
                   center=0, square=True, ax=ax, cbar_kws={'label': 'Correlation'})
        ax.set_title('Correlation Matrix - Key Variables')
        plt.tight_layout()
        self.save_figure('10_correlation_heatmap.png', 'Correlation Analysis')
    
    def generate_summary_report(self):
        """Generate summary statistics report"""
        logger.info("\nGenerating Summary Report...")
        
        report = f"""
        ===========================================
        EXPLORATORY DATA ANALYSIS SUMMARY REPORT
        ===========================================
        
        Dataset Overview:
        - Total Transactions: {len(self.df):,}
        - Unique Customers: {self.df['CustomerID'].nunique():,}
        - Countries Covered: {self.df['Country'].nunique()}
        - Analysis Period: {self.df['InvoiceDate'].min().date()} to {self.df['InvoiceDate'].max().date()}
        
        Revenue Metrics:
        - Total Revenue: £{self.df['TotalSales'].sum():,.2f}
        - Average Transaction: £{self.df['TotalSales'].mean():.2f}
        - Median Transaction: £{self.df['TotalSales'].median():.2f}
        - Revenue Range: £{self.df['TotalSales'].min():.2f} - £{self.df['TotalSales'].max():.2f}
        
        Customer Metrics:
        - Average Customer Lifetime Value: £{self.df.groupby('CustomerID')['TotalSales'].sum().mean():.2f}
        - Average Transactions per Customer: {self.df.groupby('CustomerID')['InvoiceNo'].count().mean():.1f}
        - Unique Products: {self.df['Description'].nunique()}
        
        Geographic Insights:
        - Top Country: {self.df.groupby('Country')['TotalSales'].sum().idxmax()} 
          (£{self.df.groupby('Country')['TotalSales'].sum().max():,.2f})
        
        Visualizations Created: {len(self.figures_saved)}
        """
        
        print(report)
        
        # Save report
        with open('notebooks/EDA_SUMMARY_REPORT.txt', 'w') as f:
            f.write(report)
        
        logger.info("Summary report saved")


def main():
    """Main execution"""
    eda = ExploratoryDataAnalysis('data/cleaned_data.csv')
    
    # Run all analyses
    eda.analyze_sales_distribution()
    eda.analyze_quantity_distribution()
    eda.analyze_top_countries()
    eda.analyze_top_products()
    eda.analyze_revenue_vs_customers()
    eda.analyze_monthly_trends()
    eda.analyze_day_of_week()
    eda.analyze_customer_segments()
    eda.analyze_correlations()
    eda.generate_summary_report()
    
    logger.info(f"\n✅ EDA Complete! {len(eda.figures_saved)} visualizations created")


if __name__ == "__main__":
    main()
