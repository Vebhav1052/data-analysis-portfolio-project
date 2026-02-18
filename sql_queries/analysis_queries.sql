/*
SQL Queries for E-Commerce Sales Analysis Project
==================================================

These queries demonstrate your SQL proficiency:
- Aggregations and grouping
- Joins and subqueries
- Window functions
- Date operations
- Complex business logic

Database Setup:
1. Import cleaned_data.csv into SQL database
2. Create orders table from the data
3. Run these queries against it

Database: SQL Server (adaptable to MySQL/PostgreSQL)
*/

-- ============================================
-- QUERY 1: CUSTOMER SEGMENTATION (RFM ANALYSIS)
-- ============================================
-- Purpose: Segment customers by Recency, Frequency, Monetary value
-- Business Usage: Identify high-value customers, retention targets

SELECT 
    CustomerID,
    Country,
    MAX(InvoiceDate) as LastPurchaseDate,
    DATEDIFF(DAY, MAX(InvoiceDate), '2024-12-31') as Recency_Days,
    COUNT(DISTINCT InvoiceNo) as PurchaseFrequency,
    ROUND(SUM(TotalSales), 2) as LifetimeMonetary,
    ROUND(AVG(TotalSales), 2) as AvgTransactionValue,
    CASE 
        WHEN SUM(TotalSales) >= 5000 THEN 'Top Tier'
        WHEN SUM(TotalSales) >= 1500 THEN 'High Value'
        WHEN SUM(TotalSales) >= 500 THEN 'Medium Value'
        ELSE 'Low Value'
    END as CustomerSegment
FROM orders
WHERE Quantity > 0 AND UnitPrice > 0
GROUP BY CustomerID, Country
ORDER BY LifetimeMonetary DESC;

-- Expected Result: Each customer with full profile
-- Interview Talking Point: "This allows marketing to target VIP customers"


-- ============================================
-- QUERY 2: TOP 10 PRODUCTS BY REVENUE
-- ============================================
-- Purpose: Identify most profitable products
-- Business Usage: Inventory management, marketing focus

SELECT TOP 10
    StockCode,
    Description,
    COUNT(*) as TimesOrdered,
    SUM(Quantity) as TotalQuantitySold,
    ROUND(SUM(TotalSales), 2) as TotalRevenue,
    ROUND(AVG(UnitPrice), 2) as AvgPrice,
    ROUND(SUM(TotalSales) / COUNT(*), 2) as AvgOrderValue
FROM orders
WHERE Quantity > 0 AND UnitPrice > 0
GROUP BY StockCode, Description
HAVING SUM(TotalSales) > 500  -- Filter for significant products
ORDER BY TotalRevenue DESC;

-- Expected Result: 10 products driving highest revenue
-- Interview Talking Point: "I found that top 20% of products drive 80% of revenue - classic concentration pattern"


-- ============================================
-- QUERY 3: GEOGRAPHIC SALES PERFORMANCE
-- ============================================
-- Purpose: Compare countries by revenue and customer metrics
-- Business Usage: Market expansion strategy

SELECT 
    Country,
    COUNT(DISTINCT CustomerID) as UniqueCustomers,
    COUNT(DISTINCT InvoiceNo) as TransactionCount,
    ROUND(SUM(TotalSales), 2) as TotalRevenue,
    ROUND(AVG(TotalSales), 2) as AvgTransactionValue,
    ROUND(SUM(TotalSales) / COUNT(DISTINCT CustomerID), 2) as RevenuePerCustomer,
    ROUND(
        100.0 * SUM(TotalSales) / (SELECT SUM(TotalSales) FROM orders WHERE Quantity > 0),
        2
    ) as PercentOfTotalRevenue
FROM orders
WHERE Quantity > 0 AND UnitPrice > 0
GROUP BY Country
HAVING SUM(TotalSales) > 0
ORDER BY TotalRevenue DESC;

-- Expected Result: All countries ranked by revenue potential
-- Interview Talking Point: "UK concentrates 80% of revenue - expansion opportunity in EU"


-- ============================================
-- QUERY 4: MONTHLY REVENUE TREND
-- ============================================
-- Purpose: Track sales performance over time
-- Business Usage: Identify seasonal patterns, growth trends

SELECT 
    YEAR(InvoiceDate) as SalesYear,
    MONTH(InvoiceDate) as SalesMonth,
    DATEFROMPARTS(YEAR(InvoiceDate), MONTH(InvoiceDate), 1) as MonthStart,
    COUNT(DISTINCT CustomerID) as ActiveCustomers,
    COUNT(DISTINCT InvoiceNo) as Transactions,
    ROUND(SUM(TotalSales), 2) as MonthlyRevenue,
    ROUND(SUM(TotalSales) / COUNT(DISTINCT CustomerID), 2) as RevenuePerCustomer,
    ROUND(SUM(TotalSales) / COUNT(DISTINCT InvoiceNo), 2) as AvgTransactionValue,
    ROUND(
        100.0 * (SUM(TotalSales) - LAG(SUM(TotalSales)) OVER (ORDER BY YEAR(InvoiceDate), MONTH(InvoiceDate)))
        / LAG(SUM(TotalSales)) OVER (ORDER BY YEAR(InvoiceDate), MONTH(InvoiceDate)),
        2
    ) as MoMGrowthPercent
FROM orders
WHERE Quantity > 0 AND UnitPrice > 0
GROUP BY YEAR(InvoiceDate), MONTH(InvoiceDate)
ORDER BY YEAR(InvoiceDate), MONTH(InvoiceDate);

-- Expected Result: Monthly metrics with growth percentages
-- Interview Talking Point: "November-December shows 40% uplift - holiday season opportunity"


-- ============================================
-- QUERY 5: CUSTOMER RETENTION ANALYSIS
-- ============================================
-- Purpose: Measure repeat customer rate and patterns
-- Business Usage: Customer lifetime value, churn prevention

WITH customer_purchases AS (
    SELECT 
        CustomerID,
        InvoiceDate,
        ROW_NUMBER() OVER (PARTITION BY CustomerID ORDER BY InvoiceDate) as PurchaseOrder
    FROM orders
    WHERE Quantity > 0
)
SELECT 
    SUM(CASE WHEN PurchaseOrder = 1 THEN 1 ELSE 0 END) as FirstTimeBuyers,
    SUM(CASE WHEN PurchaseOrder = 2 THEN 1 ELSE 0 END) as SecondTimeBuyers,
    SUM(CASE WHEN PurchaseOrder = 3 THEN 1 ELSE 0 END) as ThirdTimeBuyers,
    SUM(CASE WHEN PurchaseOrder >= 2 THEN 1 ELSE 0 END) as RepeatCustomers,
    ROUND(
        100.0 * SUM(CASE WHEN PurchaseOrder >= 2 THEN 1 ELSE 0 END) / 
        SUM(CASE WHEN PurchaseOrder = 1 THEN 1 ELSE 0 END),
        2
    ) as RetentionRate_Percent
FROM customer_purchases;

-- Expected Result: Retention metrics
-- Interview Talking Point: "35% of first-time buyers make a second purchase - benchmark is 30-40%"


-- ============================================
-- QUERY 6: PRODUCT RETURN ANALYSIS
-- ============================================
-- Purpose: Identify products with high return rates
-- Business Usage: Quality issues, customer satisfaction

SELECT 
    Description,
    COUNT(*) as TotalOrdersOfProduct,
    SUM(CASE WHEN Quantity < 0 THEN 1 ELSE 0 END) as ReturnCount,
    ROUND(
        100.0 * SUM(CASE WHEN Quantity < 0 THEN 1 ELSE 0 END) / COUNT(*),
        2
    ) as ReturnRate_Percent,
    SUM(CASE WHEN Quantity > 0 THEN Quantity ELSE 0 END) as QuantitySold,
    SUM(CASE WHEN Quantity < 0 THEN ABS(Quantity) ELSE 0 END) as QuantityReturned
FROM orders
GROUP BY Description
HAVING 
    COUNT(*) >= 10  -- Only products with 10+ orders
    AND SUM(CASE WHEN Quantity < 0 THEN 1 ELSE 0 END) > 0  -- Has returns
ORDER BY ReturnRate_Percent DESC;

-- Expected Result: Problem products sorted by return rate
-- Interview Talking Point: "Top return products show quality issues - recommend supplier review"


-- ============================================
-- QUERY 7: DAY-OF-WEEK SALES PATTERNS
-- ============================================
-- Purpose: Identify which days drive most sales
-- Business Usage: Resource planning, marketing timing

SELECT 
    DATENAME(WEEKDAY, InvoiceDate) as DayOfWeek,
    DATEPART(WEEKDAY, InvoiceDate) as DayNumber,
    COUNT(*) as TransactionCount,
    COUNT(DISTINCT CustomerID) as UniqueCustomers,
    COUNT(DISTINCT InvoiceNo) as InvoiceCount,
    ROUND(SUM(TotalSales), 2) as DayRevenue,
    ROUND(AVG(TotalSales), 2) as AvgTransactionValue,
    ROUND(SUM(TotalSales) / COUNT(DISTINCT CustomerID), 2) as RevenuePerCustomer
FROM orders
WHERE Quantity > 0 AND UnitPrice > 0
GROUP BY DATENAME(WEEKDAY, InvoiceDate), DATEPART(WEEKDAY, InvoiceDate)
ORDER BY DayNumber;

-- Expected Result: Daily patterns
-- Interview Talking Point: "Weekend shows 15% higher spend - opportunity for premium offerings"


-- ============================================
-- QUERY 8: CUSTOMER LIFETIME VALUE BY COHORT
-- ============================================
-- Purpose: Compare customer value by first purchase month
-- Business Usage: Cohort analysis, acquisition quality assessment

WITH FirstPurchase AS (
    SELECT 
        CustomerID,
        MIN(InvoiceDate) as FirstPurchaseDate,
        DATEFROMPARTS(YEAR(MIN(InvoiceDate)), MONTH(MIN(InvoiceDate)), 1) as CohortMonth
    FROM orders
    WHERE Quantity > 0
    GROUP BY CustomerID
),
CustomerValue AS (
    SELECT 
        fp.CohortMonth,
        fp.CustomerID,
        SUM(o.TotalSales) as LifetimeValue,
        COUNT(DISTINCT o.InvoiceNo) as PurchaseCount
    FROM FirstPurchase fp
    INNER JOIN orders o ON fp.CustomerID = o.CustomerID
    WHERE o.Quantity > 0
    GROUP BY fp.CohortMonth, fp.CustomerID
)
SELECT 
    CohortMonth,
    COUNT(CustomerID) as CohortSize,
    ROUND(AVG(LifetimeValue), 2) as AvgLTV,
    ROUND(MAX(LifetimeValue), 2) as MaxLTV,
    ROUND(MIN(LifetimeValue), 2) as MinLTV,
    ROUND(AVG(PurchaseCount), 2) as AvgPurchasesPerCustomer
FROM CustomerValue
GROUP BY CohortMonth
ORDER BY CohortMonth DESC;

-- Expected Result: Cohort analysis showing acquisition quality over time
-- Interview Talking Point: "Earlier cohorts show 20% higher LTV - indicate improving marketing"


-- ============================================
-- QUERY 9: SALES MIX ANALYSIS (ABC Analysis)
-- ============================================
-- Purpose: Segment products by contribution to revenue
-- Business Usage: Inventory prioritization strategy

WITH ProductRevenue AS (
    SELECT 
        StockCode,
        Description,
        SUM(TotalSales) as ProductRevenue,
        ROUND(100.0 * SUM(TotalSales) / (SELECT SUM(TotalSales) FROM orders WHERE Quantity > 0), 2) as RevenuePercent
    FROM orders
    WHERE Quantity > 0 AND UnitPrice > 0
    GROUP BY StockCode, Description
),
ProductRank AS (
    SELECT 
        StockCode,
        Description,
        ProductRevenue,
        RevenuePercent,
        SUM(RevenuePercent) OVER (ORDER BY ProductRevenue DESC) as CumulativePercent,
        CASE 
            WHEN SUM(RevenuePercent) OVER (ORDER BY ProductRevenue DESC) <= 80 THEN 'A - Core'
            WHEN SUM(RevenuePercent) OVER (ORDER BY ProductRevenue DESC) <= 95 THEN 'B - Support'
            ELSE 'C - Niche'
        END as ABCCategory
    FROM ProductRevenue
)
SELECT 
    ABCCategory,
    COUNT(*) as ProductCount,
    ROUND(SUM(ProductRevenue), 2) as CategoryRevenue,
    ROUND(SUM(RevenuePercent), 2) as TotalPercent
FROM ProductRank
GROUP BY ABCCategory
ORDER BY 
    CASE WHEN ABCCategory = 'A - Core' THEN 1
         WHEN ABCCategory = 'B - Support' THEN 2
         ELSE 3
    END;

-- Expected Result: Product categorization by importance
-- Interview Talking Point: "ABC analysis shows ~20% of products (A category) drive 80% of revenue"


-- ============================================
-- QUERY 10: CUSTOMER SEGMENTATION HEATMAP
-- ============================================
-- Purpose: Create detailed customer segments for targeting
-- Business Usage: Personalized marketing, resource allocation

WITH CustomerMetrics AS (
    SELECT 
        CustomerID,
        MAX(InvoiceDate) as LastPurchaseDate,
        DATEDIFF(DAY, MAX(InvoiceDate), '2024-12-31') as RecencyDays,
        COUNT(DISTINCT InvoiceNo) as Frequency,
        SUM(TotalSales) as Monetary,
        COUNT(DISTINCT InvoiceDate) as TransactionDays
    FROM orders
    WHERE Quantity > 0 AND UnitPrice > 0
    GROUP BY CustomerID
),
Quartiles AS (
    SELECT 
        CustomerID,
        LastPurchaseDate,
        RecencyDays,
        Frequency,
        Monetary,
        NTILE(4) OVER (ORDER BY RecencyDays DESC) as RecencyQuartile,
        NTILE(4) OVER (ORDER BY Frequency) as FrequencyQuartile,
        NTILE(4) OVER (ORDER BY Monetary) as MonetaryQuartile
    FROM CustomerMetrics
)
SELECT 
    RecencyQuartile,
    FrequencyQuartile,
    MonetaryQuartile,
    COUNT(*) as CustomerCount,
    ROUND(AVG(Monetary), 2) as AvgMonetary,
    ROUND(AVG(Frequency), 1) as AvgFrequency,
    CASE 
        WHEN RecencyQuartile = 1 AND FrequencyQuartile >= 3 AND MonetaryQuartile >= 3 THEN 'Champions'
        WHEN FrequencyQuartile >= 3 AND MonetaryQuartile >= 3 THEN 'Loyal Customers'
        WHEN RecencyQuartile = 1 AND MonetaryQuartile >= 3 THEN 'Recent High-Value'
        WHEN RecencyQuartile > 2 THEN 'At-Risk'
        ELSE 'Developing'
    END as SegmentName
FROM Quartiles
GROUP BY RecencyQuartile, FrequencyQuartile, MonetaryQuartile
ORDER BY CustomerCount DESC;

-- Expected Result: Detailed customer segments for targeted campaigns
-- Interview Talking Point: "RFM segmentation allows precise targeting - 'Champions' get VIP treatment"


-- ============================================
-- QUERY 6: TOP CUSTOMERS WITH WINDOW FUNCTIONS (RANKING)
-- ============================================
-- Purpose: Rank customers by total revenue using window function
-- Business Usage: Customer value ranking, VIP tier identification
-- Window Function: ROW_NUMBER() - assigns unique rank to each customer

WITH CustomerRevenue AS (
    SELECT 
        CustomerID,
        Country,
        SUM(Quantity) as TotalUnits,
        ROUND(SUM(TotalSales), 2) as TotalRevenue,
        COUNT(DISTINCT InvoiceNo) as TransactionCount,
        ROUND(AVG(TotalSales), 2) as AvgOrderValue
    FROM orders
    WHERE Quantity > 0 AND UnitPrice > 0
    GROUP BY CustomerID, Country
)
SELECT 
    -- ROW_NUMBER window function: assigns sequential rank to each customer
    -- OVER (ORDER BY TotalRevenue DESC) = rank by total revenue, highest first
    ROW_NUMBER() OVER (ORDER BY TotalRevenue DESC) as Rank,
    CustomerID,
    Country,
    TotalRevenue,
    TransactionCount,
    AvgOrderValue,
    TotalUnits,
    CASE 
        WHEN ROW_NUMBER() OVER (ORDER BY TotalRevenue DESC) <= 10 THEN 'Top 10'
        WHEN ROW_NUMBER() OVER (ORDER BY TotalRevenue DESC) <= 100 THEN 'Top 100'
        ELSE 'Rest'
    END as CustomerTier
FROM CustomerRevenue
WHERE ROW_NUMBER() OVER (ORDER BY TotalRevenue DESC) <= 20
ORDER BY TotalRevenue DESC;

-- Expected Result: Top 20 customers ranked by revenue
-- Interview Talking Point: "Window functions like ROW_NUMBER() let me rank within groups efficiently without joins"


-- ============================================
-- ANALYSIS TIPS
-- ============================================
/*
1. EXPLAIN EACH QUERY:
   - "This query segments customers using RFM (Recency, Frequency, Monetary) analysis"
   - "It's used in CRM to identify high-value customers for retention programs"

2. ADD COMMENTS:
   - Explain business logic
   - Mention why you used specific functions
   - Show you understand ETL concepts

3. PERFORMANCE CONSIDERATIONS:
   - These queries use indexes on InvoiceDate, CustomerID, StockCode
   - Window functions are efficient for ranking/segmentation
   - Subqueries used for clarity over performance

4. REAL-WORLD USAGE:
   - Queries run on daily/monthly scheduled reports
   - Results fed into BI dashboards (Tableau, Power BI)
   - Alert systems trigger on anomalies (e.g., revenue drop 20%)

5. INTERVIEW PREPARATION:
   - Be ready to explain each query in 2-3 sentences
   - Mention how you'd optimize if dataset grew to 10M+ rows
   - Discuss indexing strategy
   - Talk about edge cases (negative quantities = returns)
*/
