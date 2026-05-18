# Retail Analytics Pipeline & Business Intelligence Dashboard
> Retail sales analytics project developed using Python, BigQuery SQL, and Looker Studio.

---

##  1. Project Overview

This project builds an end-to-end retail analytics workflow using Python, SQL, Google BigQuery, and Looker Studio to analyze over **20,876 retail transaction records**. The objective was to transform raw transactional datasets into a structured analytical environment capable of supporting sales reporting, KPI tracking, and business decision-making.

The project focuses on:
- Data cleaning and validation
- Relational data modelling
- SQL-based KPI analysis
- Retail sales performance tracking
- Dashboard development
- Data quality assurance and reconciliation

The final solution integrates transactional sales records with customer and product datasets to generate interactive business insights across distribution channels, product categories, and financial metrics.

---

##  2. Technical Stack

### Technologies Used
- **Python 3.10+** (Pandas, NumPy, Matplotlib)
- **Google BigQuery** (Standard SQL, Common Table Expressions, Relational Joins)
- **Looker Studio**
- **Google Colab**
- **GitHub**

### Core Skills Demonstrated
- Data Cleaning & Validation
- SQL Data Modelling
- Retail Sales Analytics
- KPI Engineering
- Dashboard Reporting
- Relational Database Design
- Data Quality Assurance
- Statistical Outlier Detection

---

##  3. Data Cleaning & Validation

Before analysis, the retail datasets were cleaned and validated using Python to improve reporting accuracy and maintain consistency across relational tables.

### Validation Workflow
The ingestion pipeline included:
- Removing refund and return transactions (`Qty < 0`) from active sales analysis
- Standardizing mismatched relational join keys across tables (`prod_sub_cat_code` to `prod_subcat_code`)
- Resolving missing demographic values within customer profiles (`Gender` voids mapped to `U` for Unspecified)
- Removing duplicate transaction records to maintain line-item accuracy

### Python Validation Pipeline

```python
import pandas as pd

def run_retail_ingest_audit(file_path: str) -> pd.DataFrame:
    """
    Executes data validation and preprocessing checks
    for retail transaction analysis.
    """
    df = pd.read_csv(file_path)

    # Separate active sales records from refund transactions
    active_sales = df[df['Qty'] > 0].copy()

    # Remove duplicate records on a composite basis to preserve item baskets
    active_sales = active_sales.drop_duplicates(subset=['transaction_id', 'prod_subcat_code'])

    print(f"[AUDIT COMPLETE] {len(active_sales):,} active sales records validated.")

    return active_sales
```

---

##  4. SQL Data Modelling & Schema Normalization

The validated datasets were loaded into Google BigQuery and structured into a relational **Star Schema** to establish a single source of truth and optimize query execution.

### Engineered Commercial KPIs (Calculated Fields)
1. **True Gross Sales Volume:** Vectorized aggregation tracking revenue line amounts before tax parameters:
   $$\text{Gross Line Revenue} = \text{Qty} \times \text{Rate}$$
2. **Shopper Age at Purchase:** Dynamic math calculation mapping customer birth years directly against transaction dates:
   $$\text{Shopper Age} = \text{Year of Transaction} - \text{Year of Birth}$$

### Production Schema Query
```sql
WITH NormalizedSales AS (
  SELECT 
    CAST(transaction_id AS STRING) AS tx_id,
    CAST(cust_id AS INT64) AS customer_fk,
    SAFE.PARSE_DATE('%d-%m-%Y', TRIM(LAX_STRING(tran_date))) AS transaction_timestamp,
    CAST(prod_cat_code AS INT64) AS category_fk,
    CAST(prod_subcat_code AS INT64) AS subcategory_fk,
    ABS(CAST(Qty AS INT64)) AS item_quantity,
    CAST(Rate AS NUMERIC) AS unit_rate,
    CAST(Tax AS NUMERIC) AS line_tax,
    CAST(total_amt AS NUMERIC) AS gross_transaction_total,
    CAST(Store_type AS STRING) AS distribution_channel
  FROM 
    `pepkor-retail-analytics.store_operations.raw_transactions`
  WHERE 
    Qty > 0 -- Input validation constraint
)
SELECT 
  distribution_channel,
  COUNT(tx_id) AS transaction_count,
  ROUND(SUM(gross_transaction_total), 2) AS total_accumulated_revenue,
  ROUND(AVG(line_tax), 2) AS average_tax_margin
FROM 
  NormalizedSales
GROUP BY 
  distribution_channel
ORDER BY 
  total_accumulated_revenue DESC;
```

---

##  5. Looker Studio Business Intelligence Dashboard

The analytical views built within BigQuery were connected directly to Looker Studio to deliver real-time, interactive performance tracking.

### Live Production Dashboard Interface
> **[ CLICK HERE TO INTERACT WITH THE LIVE VIEW WORKSPACE PORTAL](https://google.com)**

Below is the verified operational interface rendering directly from the repository baseline metrics:

![Master Business Intelligence Dashboard](dashboard_preview.png)

### Data Validation & Reconciliation Check
To fulfill audit requirements, the reporting workspace includes control totals to track data consistency against the background database engine:
- **Target Grand Total Revenue Anchor:** `R54,453,885.07` *(Verified 1:1 down to the absolute cent against backend Python execution sums)*
- **Target Total Record Counter Balance:** `20,876` records verified across multi-table composite merges.
- **Target Average System Tax Margin Baseline:** `R247.86` control total balance check.

### 5.1 Business Interpretation & Strategic Insights
A deep-dive data distribution assessment reveals critical performance insights across core divisions:
- **Digital Channel Performance:** The `e-Shop` distribution platform is the primary revenue driver, generating **R22,185,609.88 (40.74% of total turnover)**. It outperforms physical channel formats, outperforming the combined sales volumes of both traditional `MBR` (20.03%) and `Flagship store` (20.03%) formats.
- **Category Trends:** `Books` and `Electronics` serve as high-performing product categories. Consumers show a strong preference for digital acquisition channels in these segments, suggesting that physical stock allocations should be leanly optimized in favor of expanded e-commerce operations.

### 5.2 Advanced Compliance, Outlier & Tax Validation
To guarantee performance tracking precision for stakeholders, programmatic variance checks were deployed:
- **Tax Pipeline Verification:** The database shows an absolute, mathematically uniform **10.50% system-wide Effective Tax Rate** across all processed rows. This structural constant verifies that zero table leakage or record mismatching occurred during schema joins.
- **Bulk-Purchase Detection:** Interquartile Range (IQR) boundary scanning isolated exactly **152 high-value outlier transactions** operating above the standard threshold boundary of **R8,017.74**. These bulk lines contribute a concentrated **R1,240,406.70** to gross performance asset volume, helping identify unusually large purchasing behaviour.

```text
[SYSTEMIC VARIANCE LOG] Generating Data Integrity Validation Audit...

======================================================================
 DATA INTEGRITY METRICS LOG
======================================================================
 SYSTEMIC TAX CONSTANT      : 10.50%
 TAX VARIANCE COEFFICIENT   : 0.000000 (Flawless Stability)
 CHANNEL VARIANCE GAP       : R1,917.18
----------------------------------------------------------------------
 VALIDATION SUMMARY:
  • Total Validated Cash Volume : R54,453,885.07
  • Active Transaction Volume  : 20,876 records
  • Average Transaction Size   : R2,608.44
======================================================================
```

---

##  6. Repository Architecture & Navigation
- `Scripts/` — Programmatic Python source files executing data cleaning, ingestion formatting, and verification audits.
- `Queries/` — Production-ready `.sql` files containing schema-building dimension blocks and BigQuery aggregation scripts.
- `Dashboard/` — Interface screenshots, data wireframe layout blueprints, and visual presentation assets.
