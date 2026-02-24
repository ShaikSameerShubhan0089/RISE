import os
import sys
from sqlalchemy import create_engine, text, inspect
from dotenv import load_dotenv

# Add backend to path
sys.path.append('backend')
from database import Base, engine as pg_engine
import models

load_dotenv(dotenv_path='backend/.env')

def fix_migration():
    # Remove confirmation for automated run
    # confirm = input("Are you sure? (yes/no): ").strip().lower()
    # if confirm != 'yes': return

    try:
        # 1. Drop all tables
        print("Step 1: Dropping tables...")
        with pg_engine.connect() as conn:
            inspector = inspect(pg_engine)
            tables = inspector.get_table_names()
            for table in tables:
                conn.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE"))
            conn.commit()
        print("OK: Tables dropped.")

        # 2. Re-create tables
        print("Step 2: Re-creating tables...")
        Base.metadata.create_all(bind=pg_engine)
        print("OK: Tables created.")

        # 3. Core migration
        print("Step 3: Core migration...")
        from migrate_mysql_to_postgres import MigrationManager
        MYSQL_URL = "mysql+pymysql://root:Lead%400089@localhost:3306/autism_cdss"
        POSTGRES_URL = os.getenv("DATABASE_URL")
        manager = MigrationManager(MYSQL_URL, POSTGRES_URL)
        if manager.run_migration():
            print("OK: Core migration successful.")
            
            # 4. SHAP migration
            print("Step 4: SHAP migration...")
            from migrate_shap import migrate_shap
            if migrate_shap():
                print("SUCCESS: Full migration completed!")
            else:
                print("ERROR: SHAP migration failed.")
        else:
            print("ERROR: Core migration failed.")

    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    fix_migration()
