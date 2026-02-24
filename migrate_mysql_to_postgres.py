#!/usr/bin/env python
"""
MySQL to PostgreSQL Data Migration Script
Migrates all data from local MySQL to Render PostgreSQL
"""

import os
import sys
import pandas as pd
from sqlalchemy import create_engine, inspect, text
from typing import Dict, List
import time

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
            self.mysql_engine = create_engine(
                self.mysql_url,
                echo=False,
                pool_pre_ping=True
            )
            
            with self.mysql_engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            self.log("✓ Connected to MySQL successfully", "SUCCESS")
            return True
        except Exception as e:
            self.log(f"✗ Failed to connect to MySQL: {e}", "ERROR")
            return False
    
    def connect_postgres(self) -> bool:
        """Connect to PostgreSQL"""
        try:
            self.log("Connecting to PostgreSQL (destination)...", "STEP")
            self.postgres_engine = create_engine(
                self.postgres_url,
                echo=False,
                pool_pre_ping=True
            )
            
            with self.postgres_engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            self.log("✓ Connected to PostgreSQL successfully", "SUCCESS")
            return True
        except Exception as e:
            self.log(f"✗ Failed to connect to PostgreSQL: {e}", "ERROR")
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
    
    def migrate_table(self, table: str) -> bool:
        """Migrate single table from MySQL to PostgreSQL"""
        try:
            # Get record count before
            mysql_count = self.get_record_count(self.mysql_engine, table)
            
            # Read from MySQL
            self.log(f"  Reading {table}... ({mysql_count} records)", "INFO")
            df = pd.read_sql(f"SELECT * FROM {table}", self.mysql_engine)
            
            if len(df) == 0:
                self.log(f"  Skipping empty table: {table}", "INFO")
                return True
            
            # Write to PostgreSQL
            self.log(f"  Writing {table}...", "INFO")
            df.to_sql(
                table,
                self.postgres_engine,
                if_exists='replace',  # Replace existing data
                index=False,
                method='multi',
                chunksize=1000
            )
            
            # Verify count
            postgres_count = self.get_record_count(self.postgres_engine, table)
            
            if postgres_count == mysql_count:
                self.log(f"✓ {table}: {mysql_count} records", "SUCCESS")
                return True
            else:
                self.log(
                    f"⚠ {table}: MySQL={mysql_count}, PostgreSQL={postgres_count}",
                    "WARNING"
                )
                return False
            
        except Exception as e:
            self.log(f"✗ Failed to migrate {table}: {e}", "ERROR")
            return False
    
    def get_table_order(self, tables: List[str]) -> List[str]:
        """
        Return tables in order of dependencies
        (foreign keys must be migrated after parent tables)
        """
        dependency_order = [
            'states', 'districts', 'mandals', 'anganwadi_centers',
            'children', 'assessments', 'predictions',
            'referrals', 'interventions', 'users', 'audit_logs'
        ]
        
        # Return only existing tables in correct order
        ordered = [t for t in dependency_order if t in tables]
        
        # Add any tables not in our predefined order
        for table in tables:
            if table not in ordered:
                ordered.append(table)
        
        return ordered
    
    def run_migration(self) -> bool:
        """Execute full migration"""
        print("=" * 80)
        print("MYSQL TO POSTGRESQL MIGRATION")
        print("=" * 80)
        print()
        
        # Connect to both databases
        if not self.connect_mysql():
            return False
        
        if not self.connect_postgres():
            return False
        
        # Get tables
        self.log("Fetching table list from MySQL...", "STEP")
        mysql_tables = self.get_tables(self.mysql_engine)
        self.log(f"Found {len(mysql_tables)} tables", "INFO")
        print()
        
        # Order tables by dependencies
        ordered_tables = self.get_table_order(mysql_tables)
        
        # Pre-migration counts
        print("PRE-MIGRATION RECORD COUNTS (MySQL):")
        print("-" * 80)
        mysql_totals = {}
        for table in ordered_tables:
            count = self.get_record_count(self.mysql_engine, table)
            mysql_totals[table] = count
            print(f"  {table:30s}: {count:8d}")
        
        total_mysql = sum(mysql_totals.values())
        print(f"  {'TOTAL':30s}: {total_mysql:8d}")
        print()
        
        # Migrate tables
        print("MIGRATING DATA:")
        print("-" * 80)
        
        successful = 0
        failed = 0
        
        for i, table in enumerate(ordered_tables, 1):
            print(f"{i}/{len(ordered_tables)} {table}")
            if self.migrate_table(table):
                successful += 1
            else:
                failed += 1
        
        print()
        print("=" * 80)
        print("POST-MIGRATION RECORD COUNTS (PostgreSQL):")
        print("-" * 80)
        
        postgres_totals = {}
        for table in ordered_tables:
            count = self.get_record_count(self.postgres_engine, table)
            postgres_totals[table] = count
            match = "✓" if count == mysql_totals.get(table, 0) else "⚠"
            print(f"  {match} {table:30s}: {count:8d}")
        
        total_postgres = sum(postgres_totals.values())
        print(f"  {'TOTAL':30s}: {total_postgres:8d}")
        print()
        
        # Summary
        print("=" * 80)
        print("MIGRATION SUMMARY")
        print("=" * 80)
        print(f"Tables processed:    {len(ordered_tables)}")
        print(f"Successful:          {successful}")
        print(f"Failed:              {failed}")
        print(f"MySQL total records: {total_mysql}")
        print(f"PostgreSQL total:    {total_postgres}")
        
        if failed == 0 and total_mysql == total_postgres:
            print("\n✓ MIGRATION SUCCESSFUL!")
            print("\nNext steps:")
            print("1. Update API environment variable:")
            print("   DATABASE_URL=postgresql://postgres:PASSWORD@host:5432/autism_cdss")
            print("2. Restart API service on Render")
            print("3. Test: curl https://api-url.com/api/health")
            return True
        else:
            print("\n✗ MIGRATION INCOMPLETE - Please review errors above")
            return False
    
    def save_log(self, filename: str = "migration.log"):
        """Save migration log to file"""
        with open(filename, 'w') as f:
            f.write('\n'.join(self.migration_log))
        self.log(f"Migration log saved to {filename}", "INFO")


def main():
    """Main entry point"""
    
    # Configuration
    MYSQL_URL = "mysql+pymysql://root:Lead%400089@localhost:3306/autism_cdss"
    POSTGRES_URL = "postgresql://autism_cdss_user:zWDZ11QmvrYr9UCO5nyZHmZTSlLP3sZm@dpg-d6e8m90gjchc738hvvo0-a.oregon-postgres.render.com/autism_cdss?sslmode=require"
    
    print("""
    ╔════════════════════════════════════════════════════════════════════════╗
    ║         MYSQL TO POSTGRESQL MIGRATION TOOL                             ║
    ║                                                                        ║
    ║  This script will migrate all data from local MySQL to Render         ║
    ║  PostgreSQL. Make sure:                                              ║
    ║  1. MySQL is running locally                                         ║
    ║  2. PostgreSQL database exists on Render                             ║
    ║  3. Update POSTGRES_URL with actual password                         ║
    ║  4. API server is stopped (optional but recommended)                 ║
    ║  5. You have a backup of both databases                              ║
    ║                                                                        ║
    ╚════════════════════════════════════════════════════════════════════════╝
    """)
    
    # Prompt for confirmation
    response = input("Continue with migration? (yes/no): ").strip().lower()
    if response != 'yes':
        print("Migration cancelled.")
        return
    
    # Prompt for PostgreSQL password
    postgres_password = input("Enter PostgreSQL password (from Render): ").strip()
    if not postgres_password:
        print("✗ PostgreSQL password required")
        return
    
    # Update connection string
    POSTGRES_URL = POSTGRES_URL.replace("PASSWORD", postgres_password)
    
    # Run migration
    manager = MigrationManager(MYSQL_URL, POSTGRES_URL)
    success = manager.run_migration()
    
    # Save log
    manager.save_log("migration.log")
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
