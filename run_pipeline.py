"""
End-to-End DWBI Automated Pipeline Orchestrator
Executes:
  1. Data Extraction (extract.py)
  2. Data Transformation & Dimensional Modeling (transform.py)
  3. Database Provisioning & Loading (load.py)
  4. Quality Assurance & Validation (validate.py)
"""

import sys
import time
from src.extract import run_extraction
from src.transform import transform_data
from src.load import run_loading
from src.validate import run_validation


def main():
    start_time = time.time()
    print("=" * 70)
    print("   IT3101 DWBI - END-TO-END DATA WAREHOUSE & BI PIPELINE RUNNER   ")
    print("=" * 70)

    try:
        print("\n>>> STAGE 1: MULTI-SOURCE EXTRACTION...")
        run_extraction()

        print("\n>>> STAGE 2: DATA TRANSFORMATION & DIMENSIONAL MODELING...")
        transform_data()

        print("\n>>> STAGE 3: DATABASE LOADING & DATA MART CREATION...")
        run_loading()

        print("\n>>> STAGE 4: AUTOMATED QUALITY ASSURANCE & VALIDATION...")
        run_validation()

        elapsed = time.time() - start_time
        print("\n" + "=" * 70)
        print(f" PIPELINE COMPLETED SUCCESSFULLY IN {elapsed:.1f} SECONDS!")
        print(" SQLite Data Warehouse: olist_dw.db")
        print(" Power BI Ready Exports: powerbi/exports/")
        print(" Validation Report: docs/etl_validation_report.md")
        print("=" * 70)

    except Exception as e:
        print(f"\n[FATAL ERROR] Pipeline aborted due to: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
