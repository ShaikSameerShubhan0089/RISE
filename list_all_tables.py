
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv('backend/.env')

def list_tables():
    url = os.getenv("DATABASE_URL")
    if not url:
        print("DATABASE_URL not found")
        return
        
    engine = create_engine(url)
    try:
        with engine.connect() as conn:
            # Get table count
            query = text("""
                SELECT table_schema, table_name 
                FROM information_schema.tables 
                WHERE table_schema NOT IN ('information_schema', 'pg_catalog')
                ORDER BY table_schema, table_name
            """)
            result = conn.execute(query).fetchall()
            
            print(f"Found {len(result)} tables:")
            for schema, name in result:
                print(f" - {schema}.{name}")
                
            if len(result) == 0:
                print("No tables found in non-system schemas.")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    list_tables()
