"""
Data cleaning script - prepares raw CSV for analysis
"""

import pandas as pd
import numpy as np
from datetime import datetime
import logging

# Basic logging to track what the script does
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DataCleaner:
    def __init__(self, input_file):
        self.df = pd.read_csv(input_file)
        self.initial_rows = len(self.df)
        self.cleaning_log = []
        logger.info(f"Loaded: {self.initial_rows} rows, {len(self.df.columns)} columns")
        
    def log_step(self, step_name, rows_before, rows_after, description):
        """Track what changed in each cleaning step"""
        rows_removed = rows_before - rows_after
        log_entry = {
            'step': step_name,
            'rows_removed': rows_removed,
            'rows_remaining': rows_after,
            'description': description
        }
        self.cleaning_log.append(log_entry)
        logger.info(f"{step_name}: Removed {rows_removed} rows → {rows_after} remaining")
        
    def step1_inspect_data(self):
        """Look at the data - what types, what's missing, what do the columns look like"""
        print("\nData types:")
        print(self.df.dtypes)
        
        print("\nMissing values:")
        missing = self.df.isnull().sum()
        print(missing[missing > 0])
        
        print("\nBasic statistics:")
        print(self.df.describe())
        
        print("\nFirst few rows:")
        print(self.df.head())
        
        return self.df
    
    def step2_handle_missing_values(self):
        """Remove rows that don't have customer or transaction ID - can't use them anyway"""
        rows_before = len(self.df)
        
        self.df = self.df[self.df['InvoiceNo'].notna()]  # invoice ID is required
        self.df = self.df[self.df['CustomerID'].notna()]  # customer ID is required
        
        rows_after = len(self.df)
        self.log_step("Remove missing InvoiceNo/CustomerID", 
                      rows_before, rows_after, 
                      "Need these IDs for analysis")
        
        return self.df
    
    def step3_remove_duplicates(self):
        """Get rid of exact duplicate rows"""
        rows_before = len(self.df)
        
        duplicates_count = self.df.duplicated().sum()
        logger.info(f"Found {duplicates_count} exact duplicates")
        
        self.df = self.df.drop_duplicates()
        
        rows_after = len(self.df)
        self.log_step("Remove exact duplicates", 
                      rows_before, rows_after,
                      "Same row repeated multiple times")
        
        return self.df
    
    def step4_handle_invalid_quantities(self):
        """Remove orders with negative/zero quantities - those are returns or cancellations"""
        rows_before = len(self.df)
        
        self.df['IsReturn'] = (self.df['Quantity'] < 0).astype(int)  # mark them first
        
        # keep only actual sales (positive quantity and price)
        self.df = self.df[(self.df['Quantity'] > 0) & (self.df['UnitPrice'] > 0)]
        
        rows_after = len(self.df)
        self.log_step("Remove zero/negative quantities",
                      rows_before, rows_after,
                      "Returns and cancellations filtered out")
        
        logger.info(f"Note: Marked {self.df['IsReturn'].sum()} returns for separate analysis")
        
        return self.df
    
    def step5_fix_data_types(self):
        """Convert text/numbers to the right format - dates as dates, prices as numbers"""
        # convert date column to actual datetime (not just text)
        self.df['InvoiceDate'] = pd.to_datetime(
            self.df['InvoiceDate'], 
            format='%m/%d/%Y %H:%M',
            errors='coerce'
        )
        
        # make sure prices and quantities are numbers
        self.df['UnitPrice'] = pd.to_numeric(self.df['UnitPrice'], errors='coerce')
        self.df['Quantity'] = pd.to_numeric(self.df['Quantity'], errors='coerce')
        self.df['CustomerID'] = self.df['CustomerID'].astype(str).str.strip()
        
        # categorize text that repeats a lot (saves memory)
        self.df['Country'] = self.df['Country'].astype('category')
        self.df['Description'] = self.df['Description'].astype('string')
        
        logger.info("Data types fixed")
        print("\nNew data types:")
        print(self.df.dtypes)
        
        return self.df
    
    def step6_create_features(self):
        """Add some useful calculated columns - total per sale, time breakdowns, etc"""
        # calculate total spent per line item
        self.df['TotalSales'] = self.df['Quantity'] * self.df['UnitPrice']
        
        # break down the date into separate columns
        self.df['TransactionDate'] = self.df['InvoiceDate'].dt.date
        self.df['Year'] = self.df['InvoiceDate'].dt.year
        self.df['Month'] = self.df['InvoiceDate'].dt.month
        self.df['DayOfWeek'] = self.df['InvoiceDate'].dt.day_name()
        self.df['Quarter'] = self.df['InvoiceDate'].dt.quarter
        
        # extract product category from product name
        self.df['ProductCategory'] = self.df['Description'].str.split().str[0]
        
        logger.info("Created new columns: TotalSales, Year, Month, DayOfWeek, Quarter, ProductCategory")
        
        return self.df
    
    def step7_handle_outliers(self):
        """Find unusual transactions (very high/low values) and flag them - but keep them for now"""
        Q1_sales = self.df['TotalSales'].quantile(0.25)
        Q3_sales = self.df['TotalSales'].quantile(0.75)
        IQR_sales = Q3_sales - Q1_sales
        
        # flag anything more than 3 IQRs away from the middle
        self.df['IsOutlier'] = (
            (self.df['TotalSales'] > Q3_sales + 3 * IQR_sales) |
            (self.df['TotalSales'] < Q1_sales - 3 * IQR_sales)
        ).astype(int)
        
        outlier_count = self.df['IsOutlier'].sum()
        logger.info(f"Found {outlier_count} unusual transactions (flagged)")
        
        return self.df
    
    def step8_final_validation(self):
        """Do a final check - how many rows are we left with, any remaining issues"""
        rows_removed = self.initial_rows - len(self.df)
        pct_removed = 100 * rows_removed / self.initial_rows
        
        print("\nFinal data quality check:")
        print(f"Started with: {self.initial_rows} rows")
        print(f"Removed: {rows_removed} rows ({pct_removed:.1f}%)")
        print(f"Final dataset: {len(self.df)} rows, {len(self.df.columns)} columns")
        
        print(f"\nAny null values left:")
        nulls = self.df.isnull().sum()
        print(nulls[nulls > 0] if nulls.any() else "None")
        
        print(f"\nSales per transaction (statistics):")
        print(self.df['TotalSales'].describe())
        
        return self.df
    
    def generate_cleaning_report(self, output_path):
        """Save a summary of what we removed at each step"""
        report = pd.DataFrame(self.cleaning_log)
        report.to_csv(output_path, index=False)
        logger.info(f"Cleaning report saved: {output_path}")
        
        print("\nHow many rows were removed at each step:")
        print(report.to_string(index=False))
        
        return report
    
    def save_cleaned_data(self, output_path):
        """Save the final cleaned CSV"""
        self.df.to_csv(output_path, index=False)
        logger.info(f"Cleaned data saved: {output_path}")
        return self.df


def main():
    """Load raw data, run all cleaning steps, save results"""
    
    cleaner = DataCleaner('data/OnlineRetail.csv')
    
    # Run all cleaning steps in order
    cleaner.step1_inspect_data()
    cleaner.step2_handle_missing_values()
    cleaner.step3_remove_duplicates()
    cleaner.step4_handle_invalid_quantities()
    cleaner.step5_fix_data_types()
    cleaner.step6_create_features()
    cleaner.step7_handle_outliers()
    cleaner.step8_final_validation()
    
    # Save the cleaned data
    cleaner.generate_cleaning_report('data/cleaning_report.csv')
    cleaner.save_cleaned_data('data/cleaned_data.csv')
    
    logger.info("Done!")
    

if __name__ == "__main__":
    main()
