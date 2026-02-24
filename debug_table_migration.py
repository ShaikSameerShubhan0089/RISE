import os
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv(dotenv_path='backend/.env')
MYSQL_URL = "mysql+pymysql://root:Lead%400089@localhost:3306/autism_cdss"
PG_URL = os.getenv("DATABASE_URL")

def debug(table):
    ms_engine = create_engine(MYSQL_URL)
    pg_engine = create_engine(PG_URL)
    
    try:
        print(f"Reading {table} from MySQL...")
        df = pd.read_sql(f"SELECT * FROM {table}", ms_engine)
        print(f"Read {len(df)} records.")
        
        print(f"Appending {table} to PostgreSQL...")
        df.to_sql(table, pg_engine, if_exists='append', index=False)
        print("✓ Success!")
    except Exception as e:
        print(f"✗ Error: {e}")

if __name__ == "__main__":
    debug("audit_logs")
