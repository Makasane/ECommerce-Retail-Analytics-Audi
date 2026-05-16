import pandas as pd
import numpy as np

def run_commercial_lifecycle_pipeline(file_path, output_path):
    print(" [START] Initializing Pepkor Retail Analytics Data Lifecycle...")
    
    # =========================================================================
    # STEP 1: DATA INGESTION & QUALITY CONTROL
    # =========================================================================
    try:
        df = pd.read_csv(file_path)
        print(f" Step 1 Complete: Ingested {len(df)} raw product records.")
    except FileNotFoundError:
        print(f" Error: Raw file '{file_path}' not found. Please check local paths.")
        return

    # =========================================================================
    # STEP 2: DATA CLEANING (Noise & Error Filtering)
    # =========================================================================
    print("\n Step 2: Running Data Cleaning & Structural Audits...")
    
    # Isolate pricing engine anomalies where selling price exceeds the listed retail price
    pricing_errors = df[df['price'] > df['listPrice']]
    print(f"    Pricing Anomalies Isolated: {len(pricing_errors)} data rows found.")
    
    # Isolate behavioral mismatches (Products marked as Best Sellers with zero sales velocity)
    velocity_mismatches = df[(df['isBestSeller'] == True) & (df['boughtInLastMonth'] == 0)]
    print(f"    Best-Seller/Velocity Mismatches Isolated: {len(velocity_mismatches)} rows found.")
    
    # Execute cleaning rule: Drop pricing bugs from the operational reporting layer
    cleaned_df = df[df['price'] <= df['listPrice']].copy()
    
    # Handle structural gaps (Null metrics) to avoid dashboard calculation breaks
    cleaned_df['stars'] = cleaned_df['stars'].fillna(cleaned_df['stars'].median())
    cleaned_df['reviews'] = cleaned_df['reviews'].fillna(0)
    cleaned_df = cleaned_df.drop_duplicates()
    print("    Data cleaning, null handling, and deduplication complete.")

    # =========================================================================
    # STEP 3: DATA TRANSFORMATION & KPI ANALYSIS
    # =========================================================================
    print("\n Step 3: Transforming Data & Analyzing Commercial KPIs...")
    
    # Metric 1: Estimated Gross Monthly Revenue per product stock-keeping unit
    cleaned_df['estimated_monthly_revenue'] = cleaned_df['price'] * cleaned_df['boughtInLastMonth']
    
    # Metric 2: Markdown Discount Percentage Margin (Handles division by zero safely)
    cleaned_df['markdown_discount_percentage'] = np.where(
        cleaned_df['listPrice'] > 0,
        ((cleaned_df['listPrice'] - cleaned_df['price']) / cleaned_df['listPrice']) * 100,
        0
    )
    
    # Metric 3: Consumer Engagement Index (Combines rating weights with volume)
    cleaned_df['engagement_velocity'] = cleaned_df['stars'] * cleaned_df['reviews']
    print("    Feature engineering complete. 3 retail KPIs calculated.")

    # =========================================================================
    # STEP 4: PRE-VISUALISATION VALIDATION (The Control Baseline)
    # =========================================================================
    print("\n Step 4: Generating Pipeline Validation Baselines...")
    
    control_total_revenue = cleaned_df['estimated_monthly_revenue'].sum()
    control_record_count = len(cleaned_df)
    
    print("   =========================================================")
    print("    MASTER VALIDATION BALANCES (Match these on your Dashboard!):")
    print(f"    TOTAL DATASET REVENUE CONTROL: R{control_total_revenue:,.2f}")
    print(f"    TOTAL AUDITED RECORD COUNT : {control_record_count:,} rows")
    print("   =========================================================")

    # =========================================================================
    # STEP 5: EXPORT FOR VISUAL DISPLAY INTEGRATION
    # =========================================================================
    cleaned_df.to_csv(output_path, index=False)
    print(f"\n [SUCCESS] Cleaned dataset safely exported to: {output_path}")
    print(f" Total anomaly rows dropped across data lifecycle: {len(df) - len(cleaned_df)}")

if __name__ == "__main__":
    # Define filenames for local processing
    input_file = "raw_ecommerce_data.csv"
    output_file = "audited_retail_data.csv"
    
    # Run pipeline loop
    run_commercial_lifecycle_pipeline(input_file, output_file)
