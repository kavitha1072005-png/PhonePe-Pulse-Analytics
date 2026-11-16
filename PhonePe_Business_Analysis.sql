-- =====================================================
-- PHONEPE TRANSACTION INSIGHTS
-- Complete SQL Business Analysis
-- Database: phonepe_pulse
-- =====================================================

USE phonepe_pulse;


-- 1. SHOW ALL TABLES
SHOW TABLES;


-- 2. ROW COUNT OF ALL 10 TABLES
SELECT 'aggregated_transaction' AS Table_Name,
       COUNT(*) AS Total_Rows
FROM aggregated_transaction
UNION ALL
SELECT 'aggregated_merchant_india', COUNT(*)
FROM aggregated_merchant_india
UNION ALL
SELECT 'aggregated_merchant_state', COUNT(*)
FROM aggregated_merchant_state
UNION ALL
SELECT 'aggregated_user_india', COUNT(*)
FROM aggregated_user_india
UNION ALL
SELECT 'aggregated_user_state', COUNT(*)
FROM aggregated_user_state
UNION ALL
SELECT 'map_state', COUNT(*)
FROM map_state
UNION ALL
SELECT 'map_district', COUNT(*)
FROM map_district
UNION ALL
SELECT 'top_master', COUNT(*)
FROM top_master
UNION ALL
SELECT 'transaction_validation', COUNT(*)
FROM transaction_validation
UNION ALL
SELECT 'top_missing_files', COUNT(*)
FROM top_missing_files;


-- 3. TOP 10 TRANSACTION STATES
WITH latest_period AS (
    SELECT Year, QuarterNumber
    FROM map_state
    WHERE Category = 'Transaction'
    ORDER BY Year DESC, QuarterNumber DESC
    LIMIT 1
)
SELECT
    m.State,
    SUM(m.Transactions) AS Total_Transactions
FROM map_state m
JOIN latest_period p
    ON m.Year = p.Year
   AND m.QuarterNumber = p.QuarterNumber
WHERE m.Category = 'Transaction'
GROUP BY m.State
ORDER BY Total_Transactions DESC
LIMIT 10;


-- 4. PAYMENT CATEGORY SHARE
WITH latest_period AS (
    SELECT Year, QuarterNumber
    FROM aggregated_transaction
    ORDER BY Year DESC, QuarterNumber DESC
    LIMIT 1
),
category_totals AS (
    SELECT
        a.Category,
        SUM(a.Transactions) AS Total_Transactions
    FROM aggregated_transaction a
    JOIN latest_period p
        ON a.Year = p.Year
       AND a.QuarterNumber = p.QuarterNumber
    GROUP BY a.Category
)
SELECT
    Category,
    Total_Transactions,
    ROUND(
        Total_Transactions * 100.0 /
        NULLIF(SUM(Total_Transactions) OVER (), 0),
        2
    ) AS Share_Percentage
FROM category_totals
ORDER BY Total_Transactions DESC;


-- 5. TOP 10 TRANSACTION DISTRICTS
WITH latest_period AS (
    SELECT Year, QuarterNumber
    FROM map_district
    WHERE Category = 'Transaction'
    ORDER BY Year DESC, QuarterNumber DESC
    LIMIT 1
)
SELECT
    d.State,
    d.District,
    SUM(d.Transactions) AS Total_Transactions
FROM map_district d
JOIN latest_period p
    ON d.Year = p.Year
   AND d.QuarterNumber = p.QuarterNumber
WHERE d.Category = 'Transaction'
GROUP BY d.State, d.District
ORDER BY Total_Transactions DESC
LIMIT 10;


-- 6. TOP 10 REGISTERED MERCHANT STATES
WITH latest_period AS (
    SELECT Year, QuarterNumber
    FROM map_state
    WHERE Category = 'Merchant'
    ORDER BY Year DESC, QuarterNumber DESC
    LIMIT 1
)
SELECT
    m.State,
    SUM(m.RegisteredCount) AS Registered_Merchants
FROM map_state m
JOIN latest_period p
    ON m.Year = p.Year
   AND m.QuarterNumber = p.QuarterNumber
WHERE m.Category = 'Merchant'
GROUP BY m.State
ORDER BY Registered_Merchants DESC
LIMIT 10;


-- 7. TOP 10 REGISTERED USER STATES
WITH latest_period AS (
    SELECT Year, QuarterNumber
    FROM map_state
    WHERE Category = 'User'
    ORDER BY Year DESC, QuarterNumber DESC
    LIMIT 1
)
SELECT
    u.State,
    SUM(u.RegisteredCount) AS Registered_Users
FROM map_state u
JOIN latest_period p
    ON u.Year = p.Year
   AND u.QuarterNumber = p.QuarterNumber
WHERE u.Category = 'User'
GROUP BY u.State
ORDER BY Registered_Users DESC
LIMIT 10;


-- 8. QUARTERLY TRANSACTION TREND AND GROWTH
WITH quarterly_totals AS (
    SELECT
        Year,
        QuarterNumber,
        SUM(Transactions) AS Total_Transactions
    FROM aggregated_transaction
    GROUP BY Year, QuarterNumber
),
growth_analysis AS (
    SELECT
        Year,
        QuarterNumber,
        Total_Transactions,
        LAG(Total_Transactions) OVER (
            ORDER BY Year, QuarterNumber
        ) AS Previous_Quarter
    FROM quarterly_totals
)
SELECT
    Year,
    CONCAT('Q', QuarterNumber) AS Quarter,
    Total_Transactions,
    Previous_Quarter,
    ROUND(
        (Total_Transactions - Previous_Quarter) * 100.0 /
        NULLIF(Previous_Quarter, 0),
        2
    ) AS Growth_Percentage
FROM growth_analysis
ORDER BY Year, QuarterNumber;


-- 9. TRANSACTION VALIDATION SUMMARY
SELECT
    Status,
    COUNT(*) AS Total_Records
FROM transaction_validation
GROUP BY Status
ORDER BY Status;


-- 10. TOP DATA COVERAGE
SELECT
    Category,
    Scope,
    Level,
    COUNT(*) AS Total_Records
FROM top_master
GROUP BY Category, Scope, Level
ORDER BY Category, Scope, Level;


-- 11. MISSING TOP SOURCE FILES BY YEAR AND QUARTER
SELECT
    Category,
    Scope,
    Year,
    Quarter,
    COUNT(*) AS Reported_Missing_Files
FROM top_missing_files
GROUP BY Category, Scope, Year, Quarter
ORDER BY Year, Quarter;


-- 12. LATEST AVAILABLE DATA PERIODS
SELECT
    'aggregated_transaction' AS Dataset,
    MAX(Year) AS Latest_Year,
    MAX(
        CASE
            WHEN Year = (
                SELECT MAX(Year)
                FROM aggregated_transaction
            )
            THEN QuarterNumber
        END
    ) AS Latest_Quarter
FROM aggregated_transaction

UNION ALL

SELECT
    'map_state',
    MAX(Year),
    MAX(
        CASE
            WHEN Year = (SELECT MAX(Year) FROM map_state)
            THEN QuarterNumber
        END
    )
FROM map_state

UNION ALL

SELECT
    'map_district',
    MAX(Year),
    MAX(
        CASE
            WHEN Year = (SELECT MAX(Year) FROM map_district)
            THEN QuarterNumber
        END
    )
FROM map_district;


-- =====================================================
-- END OF PHONEPE BUSINESS ANALYSIS
-- =====================================================