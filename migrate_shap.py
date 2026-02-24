import os
import pandas as pd
import sqlalchemy
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv(dotenv_path='backend/.env')

def migrate_shap():
    MYSQL_URL = "mysql+pymysql://root:Lead%400089@localhost:3306/autism_cdss"
    POSTGRES_URL = os.getenv("DATABASE_URL")
    
    mysql_engine = create_engine(MYSQL_URL)
    pg_engine = create_engine(POSTGRES_URL)
    
    table = 'shap_explanations'
    print(f"Migrating {table}...")
    
    try:
        # Read total count
        with mysql_engine.connect() as conn:
            total = conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
            
        print(f"Total records to migrate: {total}")
        
        # Migrate in chunks
        chunk_size = 5000
        cols = "prediction_id, feature_name, feature_value, shap_value, created_at"
        for offset in range(0, total, chunk_size):
            print(f"Migrating chunk {offset} to {offset+chunk_size}...")
            query = f"SELECT {cols} FROM {table} ORDER BY prediction_id, feature_name LIMIT {chunk_size} OFFSET {offset}"
            df = pd.read_sql(query, mysql_engine)
            df.to_sql(table, pg_engine, if_exists='append', index=False, method='multi')
            
        print("✓ SHAP Migration successful.")
        return True
    except Exception as e:
        print(f"✗ SHAP Migration failed: {e}")
        return False

if __name__ == "__main__":
    migrate_shap()
