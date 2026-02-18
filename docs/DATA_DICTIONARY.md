# 📖 Data Dictionary

Complete documentation of all columns in the Online Retail Dataset.

---

## Original Dataset Columns (from Kaggle)

### InvoiceNo
**Type**: String (Text)  
**Example**: 536365, 536367, 536369  
**Description**: Transaction identifier. Each row represents one product purchase.  
**Business Use**: Creates unique transaction IDs. Used for joining with customer data.  
**Data Quality**: 
- Always present (0 nulls)
- Mostly numeric, some have "C" suffix (=1,354 rows)
- "C" prefix means cancelled transaction

**Handling in Analysis**:
```
✓ Kept as string
✓ Filtered: Invoice NOT LIKE '%C' to remove cancellations
✓ Used in COUNT(DISTINCT InvoiceNo) for transaction count
```

---

### StockCode
**Type**: String (Product Code)  
**Example**: 85123A, POST, D (for discount), M (for manual)  
**Description**: Product identifier. Multiple codes exist for same product due to color/size variants.  
**Business Use**: Identifies which product was purchased. Links to product descriptions.  
**Data Quality**:
- Always present (0 nulls)
- ~3,500 unique codes
- Some are special codes (POST, D, M, BANK CHARGES)

**Special Codes**:
- "POST" = Postage charged separately
- "D" = Discount line
- "M" = Manual
- Not actual products; analyze separately

---

### Description
**Type**: String (Text)  
**Example**: WHITE HANGING HEART T-LIGHT HOLDER, RED WOOLLY HOTTIE WATER BOTTLE  
**Description**: Product name/description. Text format.  
**Business Use**: Identifies product type. Used for product category analysis.  
**Data Quality**:
- ~500 nulls (less than 0.1%) → filled with "UNKNOWN"
- Some typos and variations (e.g., "T-LIGHT" vs "TLIGHT")
- Mostly uppercase

**Cleaning Applied**:
```
✓ Filled nulls with "UNKNOWN"
✓ Created product category from first words
✓ Used for ABC analysis (which products drive revenue)
```

---

### Quantity
**Type**: Integer (Numeric)  
**Example**: 6, 10, 20, -4 (return)  
**Description**: Number of units purchased per transaction.  
**Business Use**: Combined with price to get revenue. Seen separately to identify returns.  
**Data Quality**:
- Range: -80,995 to 80,995
- Negative values = returns (8% of all transactions)
- Zero values = rare (~120 rows)

**Important Notes**:
```
⚠️ Negative quantity = Return, not an error
⚠️ Negative values analyzed separately
✓ Main analysis uses Quantity > 0
✓ Created IsReturn flag for negative quantities
```

---

### InvoiceDate
**Type**: DateTime (Date + Time)  
**Example**: 12/1/2010 8:26, 12/1/2010 9:55  
**Description**: Date and time when the transaction occurred.  
**Business Use**: Time series analysis. Identifying seasonal trends, daily patterns.  
**Data Quality**:
- Range: December 2010 to December 2011 (1 year)
- No nulls (0%)
- Time component: includes hours/minutes

**Features Derived**:
```
✓ Year (all 2010-2011)
✓ Month (1-12)
✓ DayOfWeek (Monday-Sunday)
✓ Quarter (Q1-Q4)
✓ TransactionDate (date only, no time)
```

---

### UnitPrice
**Type**: Float (Decimal)  
**Example**: 2.55, 3.39, £0.00  
**Description**: Price per unit in British Pounds (£).  
**Business Use**: Core to revenue calculation (Quantity × UnitPrice = Revenue).  
**Data Quality**:
- Range: £0 to £649.50
- ~3 nulls → Removed
- Some zero prices (~500) = promotional items or testing

**Handling**:
```
✓ Converted to numeric (any text errors coerced to NaN)
✓ Filtered UnitPrice > 0 for main analysis
✓ Zero prices analyzed separately
✓ Very high prices (+£600) flagged as outliers but kept
```

---

### CustomerID
**Type**: String (Customer Code)  
**Example**: 17850, 15291, 15421  
**Description**: Unique customer identifier.  
**Business Use**: Groups transactions by customer. Core to customer segmentation analysis.  
**Data Quality**:
- ~1,300 nulls (~0.3%) → Removed (can't segment customers without ID)
- ~5,000 unique customers
- No format standardization (some have leading/trailing spaces)

**Data Cleaning**:
```python
# Strip whitespace
df['CustomerID'] = df['CustomerID'].astype(str).str.strip()

# Filter nulls
df = df[df['CustomerID'].notna()]

# Now: 450K rows, 5,000 unique customers
```

---

### Country
**Type**: String (Categorical)  
**Description**: Country of customer (based on delivery address).  
**Examples**: United Kingdom, Netherlands, EIRE, France, Germany  
**Business Use**: Geographic analysis. Identifies markets and expansion opportunities.  
**Data Quality**:
- ~25 unique countries
- ~1,300 nulls → Removed with CustomerID
- UK represents ~80% of transactions

**Geographic Distribution**:
```
1. United Kingdom: 80%
2. Netherlands: 5%
3. EIRE (Ireland): 4%
4. Germany: 3%
5. France: 2%
6. Others: 6%
```

---

## Derived Columns (Created During Analysis)

### TotalSales
**Type**: Float (Currency)  
**Formula**: `Quantity × UnitPrice`  
**Example**: 6 units × £2.55 = £15.30  
**Business Use**: Primary metric for revenue analysis. Aggregated for customer/product/region revenue.  
**Data Quality**:
- Calculated from cleaned Quantity and UnitPrice
- Range: £0.01 to £4,000
- Right-skewed distribution (outliers exist)

**Used In**:
```
✓ Customer Lifetime Value (sum by customer)
✓ Product Revenue (sum by product)
✓ Country Revenue (sum by country)
✓ Monthly Revenue trends
```

---

### IsReturn
**Type**: Binary (0 or 1)  
**Formula**: `1 if Quantity < 0, else 0`  
**Business Use**: Identifies return transactions. Used to analyze return rates by product.  
**Distribution**:
- 1 (Return): 8% of transactions
- 0 (Sale): 92% of transactions

**Analysis Using This**:
```sql
SELECT Description,
       COUNT(*) as Total,
       SUM(CASE WHEN IsReturn = 1 THEN 1 ELSE 0 END) as ReturnCount,
       100.0 * SUM(IsReturn) / COUNT(*) as ReturnRate
FROM orders
GROUP BY Description
ORDER BY ReturnRate DESC;
```

---

### IsOutlier
**Type**: Binary (0 or 1)  
**Formula**: `1 if value > Q3 + 3×IQR or < Q1 - 3×IQR, else 0`  
**Calculation**:
```
Q1 (25th percentile): £1.25
Q3 (75th percentile): £9.50
IQR (Interquartile Range): £8.25
Threshold: £9.50 + 3×8.25 = £33.25

Outliers: Transactions > £33.25
Count: ~2% of transactions
```

**Use**: Flagged for investigation (not removed).  
**Why Not Remove**: Some legitimate high-value bulk orders and high-priced items.

---

### Year, Month, DayOfWeek, Quarter
**Type**: Integer/String  
**Extracted From**: InvoiceDate  
**Examples**:
- Year: 2010, 2011
- Month: 1-12 (January-December)
- DayOfWeek: Monday, Tuesday, ...
- Quarter: 1, 2, 3, 4

**Use**: Time series analysis, seasonal pattern detection.

**Finding**: Q4 revenue 40% higher than Q1 (holiday season effect)

---

### ProductCategory
**Type**: String  
**Extracted From**: First word of Description  
**Examples**: WHITE, RED, BLUE, VINTAGE  
**Quality**: ~100 unique categories  
**Use**: Quick product type grouping (though imperfect)

---

## Summary Statistics

### Revenue (TotalSales)
```
Count: 450,000 transactions
Mean: £12.75
Median: £6.95
Std Dev: £25.60
Min: £0.01
Max: £4,000.00
Skewness: +2.3 (right-skewed)
```

### Customers
```
Total Unique: 5,000
Transactions per Customer (avg): 90
Transactions per Customer (median): 45
Max Transactions from Single Customer: 5,000+
```

### Products
```
Total Unique: 3,500
Products Generating 80% Revenue: ~700 (20%)
Average Price: £3.40
Price Range: £0.01 to £649.50
```

### Time Period
```
Start Date: 1 Dec 2010
End Date: 9 Dec 2011
Duration: ~12 months
Busiest Month: November (holiday prep)
Slowest Month: January (post-holiday)
```

---

## Data Quality Report

| Aspect | Status | Notes |
|--------|--------|-------|
| **Completeness** | ✅ 99% | Only ~1K nulls in non-critical fields |
| **Accuracy** | ✅ High | Values logically consistent (price/qty positive) |
| **Consistency** | ✅ Good | Date format consistent; country names standardized |
| **Uniqueness** | ⚠️ ~0.4% | Exact duplicate transactions (~1,800 rows) |
| **Freshness** | ✅ 1 Year | Data complete for 12-month period |

---

## How to Use This Dictionary

When analyzing:
1. **Check column names** → Cross-reference type and business meaning
2. **Understand data quality** → Knows what was cleaned and why
3. **See constraints** → Knows typical ranges (e.g., Quantity = -80K to +80K)
4. **Identify derived metrics** → Knows TotalSales is calculated, not raw
5. **Understand limitations** → Knows Country = delivery address, might not be customer home country

---

## Questions Answered by This Dictionary

**Q: Can I use InvoiceNo as customer identifier?**  
A: No. InvoiceNo is transaction ID. Use CustomerID for customers. Many transactions per invoice possible.

**Q: Are negative quantities errors?**  
A: No, they're returns (8% of data). Keep separate analysis.

**Q: Why are some prices zero?**  
A: Promotional/discount lines or test transactions. Filter out for revenue analysis.

**Q: What's the time period?**  
A: December 2010 to December 2011 (1 year only).

**Q: How many countries?**  
A: 25 countries; UK = 80% of revenue.

**Q: Should I remove outliers?**  
A: No, they're flagged but kept. Great customers buy large orders.

---

**Last Updated**: February 2026  
**Version**: 1.0  
**Created By**: Product Analysis Team
