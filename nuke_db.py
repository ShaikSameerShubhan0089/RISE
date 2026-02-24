import os
from sqlalchemy import create_engine, text, inspect
from dotenv import load_dotenv

# Load PostgreSQL connection string
load_dotenv('backend/.env')
POSTGRES_URL = os.getenv("DATABASE_URL")

if not POSTGRES_URL:
    print("Error: DATABASE_URL not found in backend/.env")
    exit(1)

def nuke_db():
    print(f"Target Database: {POSTGRES_URL.split('@')[-1]}") # Print host only for security
    confirm = input("Are you absolutely sure you want to DELETE ALL TABLES AND DATA? (yes/delete-all-data): ").strip().lower()
    
    if confirm not in ['yes', 'delete-all-data']:
        print("Operation cancelled.")
        return

    try:
        engine = create_engine(POSTGRES_URL)
        with engine.connect() as conn:
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            
            if not tables:
                print("No tables found in the database. It is already clean.")
                return

            print(f"Found {len(tables)} tables. Dropping...")
            
            # Use a transaction for the drops
            with conn.begin():
                for table in tables:
                    print(f" Dropping table: {table}")
                    conn.execute(text(f'DROP TABLE IF EXISTS "{table}" CASCADE'))
            
            # Check for views or other objects if necessary, but tables are the primary concern
            print("\nOK: All tables have been dropped.")
            
            # Double check
            remaining = inspect(engine).get_table_names()
            if not remaining:
                print("VERIFIED: Database is now empty.")
            else:
                print(f"WARNING: Some tables remain: {remaining}")

    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    nuke_db()
