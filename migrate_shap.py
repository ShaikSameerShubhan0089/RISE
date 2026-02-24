import os
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import sys

# Add backend to path if needed
sys.path.append('backend')

load_dotenv(dotenv_path='backend/.env')

MYSQL_URL = "mysql+pymysql://root:Lead%400089@localhost:3306/autism_cdss"
POSTGRES_URL = os.getenv("DATABASE_URL")

def migrate_shap():
    try:
        print("Connecting to MySQL...")
        mysql_engine = create_engine(MYSQL_URL)
        
        print("Connecting to PostgreSQL...")
        pg_engine = create_engine(POSTGRES_URL)
        
        table = "shap_explanations"
        
        print(f"Reading {table} from MySQL...")
        # Use chunking for large table
        df_iterator = pd.read_sql(f"SELECT * FROM {table}", mysql_engine, chunksize=10000)
        
        first_chunk = True
        total_migrated = 0
        
        for df in df_iterator:
            print(f"Migrating chunk of {len(df)} records (Total so far: {total_migrated})...")
            # For the first chunk, we might want to replace if we want a fresh start, 
            # but since it's currently missing, append/replace both work.
            mode = 'replace' if first_chunk else 'append'
            df.to_sql(table, pg_engine, if_exists=mode, index=False, method='multi', chunksize=1000)
            
            total_migrated += len(df)
            first_chunk = False
            
        print(f"Successfully migrated {total_migrated} records to {table}")
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    success = migrate_shap()
    if success:
        sys.exit(0)
    else:
        sys.exit(1)
