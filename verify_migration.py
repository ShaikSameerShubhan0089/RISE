
import os
import pandas as pd
from sqlalchemy import create_engine, text, inspect
from dotenv import load_dotenv
import sys

# Load env vars
load_dotenv('backend/.env')

def get_counts():
    MYSQL_URL = "mysql+pymysql://root:Lead%400089@localhost:3306/autism_cdss"
    POSTGRES_URL = os.getenv("DATABASE_URL")
    
    if not POSTGRES_URL:
        print("DATABASE_URL not found in environment!")
        return

    mysql_engine = create_engine(MYSQL_URL)
    pg_engine = create_engine(POSTGRES_URL)
    
    tables = [
        'states', 'districts', 'mandals', 'anganwadi_centers',
        'users', 'children', 'assessments', 'engineered_features', 
        'model_predictions', 'referrals', 'interventions', 
        'audit_logs', 'parent_child_mapping', 'district_summary',
        'shap_explanations'
    ]
    
    print(f"{'Table Name':<25} | {'MySQL':<8} | {'Postgres':<8} | {'Status'}")
    print("-" * 65)
    
    all_ok = True
    
    # Check MySQL connection
    try:
        with mysql_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as e:
        print(f"CRITICAL: Cannot connect to MySQL: {e}")
        return

    # Check Postgres connection
    try:
        with pg_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as e:
        print(f"CRITICAL: Cannot connect to Postgres: {e}")
        return

    for table in tables:
        m_count = "N/A"
        p_count = "N/A"
        status = "???"
        
        try:
            with mysql_engine.connect() as conn:
                m_count = conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
        except Exception as e:
            m_count = "ERR"
            
        try:
            with pg_engine.connect() as conn:
                p_count = conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
        except Exception as e:
            p_count = "MISSING" if "does not exist" in str(e).lower() else "ERR"
            
        if m_count == p_count and isinstance(m_count, int):
            status = "OK"
        elif p_count == "MISSING":
            status = "FAILURE"
            all_ok = False
        else:
            status = "MISMATCH"
            all_ok = False
            
        print(f"{table:<25} | {str(m_count):<8} | {str(p_count):<8} | {status}")
            
    if all_ok:
        print("\n[SUCCESS] Migration verified successfully.")
    else:
        print("\n[WARNING] Migration issues detected.")

    # Check for boolean types in assessments (spot check)
    print("\n--- Spot Check: Assessments Boolean Types ---")
    try:
        with pg_engine.connect() as conn:
            # Check a few boolean columns
            query = text("SELECT is_at_risk, has_stunting, has_wasting FROM assessments LIMIT 1")
            result = conn.execute(query).fetchone()
            if result:
                print(f"Sample boolean values: {result}")
                # Check types
                inspector = inspect(pg_engine)
                cols = inspector.get_columns('assessments')
                bool_cols = [c['name'] for c in cols if str(c['type']).upper() == 'BOOLEAN']
                print(f"Confirmed Boolean columns in Postgres: {', '.join(bool_cols[:5])}...")
            else:
                print("No records in assessments table to check.")
    except Exception as e:
        print(f"Error during spot check: {e}")

if __name__ == "__main__":
    get_counts()
