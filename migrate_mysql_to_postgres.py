#!/usr/bin/env python
"""
MySQL to PostgreSQL Data Migration Script
Migrates all data from local MySQL to Render PostgreSQL
"""

import os
import sys
import pandas as pd
from sqlalchemy import create_engine, inspect, text, Boolean
from typing import Dict, List, Any
import time

# Add backend to path for model imports
backend_dir = os.path.join(os.getcwd(), 'backend')
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

import models
from database import Base

class MigrationManager:
    def __init__(self, mysql_url: str, postgres_url: str):
        self.mysql_url = mysql_url
        self.postgres_url = postgres_url
        self.mysql_engine = None
        self.postgres_engine = None
        self.migration_log = []
        
    def log(self, message: str, status: str = "INFO"):
        """Log migration progress"""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {status}: {message}"
        print(log_entry)
        self.migration_log.append(log_entry)
    
    def connect_mysql(self) -> bool:
        """Connect to MySQL"""
        try:
            self.log("Connecting to MySQL (source)...", "STEP")
            self.mysql_engine = create_engine(self.mysql_url, echo=False, pool_pre_ping=True)
            with self.mysql_engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            self.log("OK: Connected to MySQL successfully", "SUCCESS")
            return True
        except Exception as e:
            self.log(f"ERROR: Failed to connect to MySQL: {e}", "ERROR")
            return False
    
    def connect_postgres(self) -> bool:
        """Connect to PostgreSQL"""
        try:
            self.log("Connecting to PostgreSQL (destination)...", "STEP")
            self.postgres_engine = create_engine(self.postgres_url, echo=False, pool_pre_ping=True)
            with self.postgres_engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            self.log("OK: Connected to PostgreSQL successfully", "SUCCESS")
            return True
        except Exception as e:
            self.log(f"ERROR: Failed to connect to PostgreSQL: {e}", "ERROR")
            return False
    
    def get_tables(self, engine) -> List[str]:
        """Get list of tables from database"""
        inspector = inspect(engine)
        return inspector.get_table_names()
    
    def get_record_count(self, engine, table: str) -> int:
        """Get record count in a table"""
        try:
            with engine.connect() as conn:
                result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                return result.scalar()
        except Exception as e:
            self.log(f"Error counting records in {table}: {e}", "WARNING")
            return 0

    def _get_boolean_cols(self, table_name: str) -> List[str]:
        """Identify boolean columns for a table from SQLAlchemy models"""
        try:
            for table in Base.metadata.tables.values():
                if table.fullname == table_name:
                    return [c.name for c in table.columns if isinstance(c.type, Boolean)]
            return []
        except Exception as e:
            self.log(f"Error identifying boolean columns for {table_name}: {e}", "WARNING")
            return []

    def migrate_table(self, table: str) -> bool:
        """Migrate single table from MySQL to PostgreSQL"""
        try:
            mysql_count = self.get_record_count(self.mysql_engine, table)
            self.log(f"  Reading {table}... ({mysql_count} records)", "INFO")
            df = pd.read_sql(f"SELECT * FROM {table}", self.mysql_engine)
            
            # Boolean casting for Postgres compatibility
            boolean_cols = self._get_boolean_cols(table)
            if boolean_cols:
                for col in boolean_cols:
                    if col in df.columns:
                        df[col] = df[col].map({1: True, 0: False, 1.0: True, 0.0: False, True: True, False: False, None: None})

            self.log(f"  Writing {table}...", "INFO")
            df.to_sql(table, self.postgres_engine, if_exists='append', index=False, method='multi', chunksize=1000)
            
            postgres_count = self.get_record_count(self.postgres_engine, table)
            if postgres_count == mysql_count:
                self.log(f"OK: {table}: {mysql_count} records", "SUCCESS")
                return True
            else:
                self.log(f"WARNING: {table}: MySQL={mysql_count}, PostgreSQL={postgres_count}", "WARNING")
                return False
        except Exception as e:
            import traceback
            self.log(f"ERROR: Failed to migrate {table}: {e}", "ERROR")
            traceback.print_exc()
            return False
    
    def get_table_order(self, tables: List[str]) -> List[str]:
        dependency_order = [
            'states', 'districts', 'mandals', 'anganwadi_centers',
            'users', 'children', 'assessments', 'engineered_features', 
            'model_predictions', 'referrals', 'interventions', 
            'audit_logs', 'parent_child_mapping', 'district_summary'
        ]
        skip_tables = ['shap_explanations']
        ordered = [t for t in dependency_order if t in tables and t not in skip_tables]
        for table in tables:
            if table not in ordered and table not in skip_tables:
                ordered.append(table)
        return ordered
    
    def run_migration(self) -> bool:
        if not self.connect_mysql() or not self.connect_postgres(): return False
        mysql_tables = self.get_tables(self.mysql_engine)
        ordered_tables = self.get_table_order(mysql_tables)
        
        successful = 0
        failed = 0
        for i, table in enumerate(ordered_tables, 1):
            if self.migrate_table(table): successful += 1
            else: failed += 1
        
        return failed == 0

    def save_log(self, filename: str = "migration.log"):
        with open(filename, 'w') as f: f.write('\n'.join(self.migration_log))

def main():
    MYSQL_URL = "mysql+pymysql://root:Lead%400089@localhost:3306/autism_cdss"
    POSTGRES_URL = os.getenv("DATABASE_URL")
    if not POSTGRES_URL:
        print("DATABASE_URL not found in environment!")
        return
    
    manager = MigrationManager(MYSQL_URL, POSTGRES_URL)
    if manager.run_migration():
        print("MIGRATION SUCCESSFUL!")
        sys.exit(0)
    else:
        print("MIGRATION FAILED!")
        sys.exit(1)

if __name__ == "__main__":
    main()
