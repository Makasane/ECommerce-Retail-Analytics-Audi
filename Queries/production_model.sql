-- =========================================================================
-- SYSTEM ENGINE: ENTERPRISE STAR-SCHEMA RELATIONAL DATA MODEL
-- ENVIRONMENT  : GOOGLE BIGQUERY / STANDARD SQL DIALECT
-- TARGET BALANCES: VOLUMETRICS = 20,876 ROWS | REVENUE = R54,453,885.07
-- =========================================================================

WITH NormalizedTransactions AS (
  SELECT 
    CAST(transaction_id AS STRING) AS tx_id,
    CAST(cust_id AS INT64) AS customer_fk,
    PARSE_DATE('%d-%m-%Y', CAST(tran_date AS STRING)) AS transaction_timestamp,
    CAST(prod_cat_code AS INT64) AS category_fk,
    CAST(prod_subcat_code AS INT64) AS subcategory_fk,
    CAST(Qty AS INT64) AS item_quantity,
    CAST(Rate AS NUMERIC) AS unit_rate,
    CAST(Tax AS NUMERIC) AS line_tax,
    CAST(total_amt AS NUMERIC) AS gross_transaction_total,
    CAST(Store_type AS STRING) AS distribution_channel
  FROM 
    `pepkor-retail-analytics.store_operations.raw_transactions`
  WHERE 
    Qty > 0 -- Mandatory Input Validation: Isolating systemic return rows
)

SELECT 
  tx.distribution_channel,
  p.prod_cat AS department_name,
  p.prod_subcat AS subcategory_name,
  COUNT(tx.tx_id) AS total_transaction_count,
  ROUND(SUM(tx.item_quantity * tx.unit_rate), 2) AS calculated_net_revenue,
  ROUND(SUM(tx.line_tax), 2) AS total_tax_collected,
  ROUND(SUM(tx.gross_transaction_total), 2) AS integrated_gross_revenue,
  ROUND(AVG((tx.line_tax / NULLIF(tx.item_quantity * tx.unit_rate, 0)) * 100), 2) AS effective_tax_coefficient
FROM 
  NormalizedTransactions tx
LEFT JOIN 
  `pepkor-retail-analytics.dimensions.product_hierarchy` p
  ON tx.category_fk = p.prod_cat_code 
  AND tx.subcategory_fk = p.prod_sub_cat_code -- Composite Multi-Key Join Integrity Alignment
GROUP BY 
  1, 2, 3
ORDER BY 
  integrated_gross_revenue DESC;
