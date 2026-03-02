# MySQL to PostgreSQL Migration Guide

## Overview

You have data in **local MySQL** that needs to move to **Render PostgreSQL** before going live.

**Options**:
1. **Simple Export/Import** (2-5 minutes) - Basic SQL dump & restore
2. **Python Script** (5-10 minutes) - More control, handles differences
3. **Live Migration** (10-15 minutes) - Zero downtime using replication

---

## Option 1: Simple SQL Dump & Restore (Easiest)

### Step 1.1: Export MySQL Data Locally

```bash
# Export entire rise database to SQL file
mysqldump -u root -pLead@0089 --single-transaction --no-tablespaces rise > backup.sql

# Options explained:
# -u root              : MySQL username
# -pLead@0089          : MySQL password (no space after -p)
# --single-transaction : Consistent snapshot (no locks)
# --no-tablespaces     : Skip tablespace (PostgreSQL compatible)
# rise                 : Database name
# > backup.sql         : Save to file
```

**Verify file created**:
```bash
ls -lh backup.sql
# Should see: backup.sql (size varies, likely 1-100 MB)
```

### Step 1.2: Convert SQL Syntax (If Needed)

MySQL and PostgreSQL have slight syntax differences. Use `pgloader` to auto-convert:

```bash
# Install pgloader
# macOS:
brew install pgloader

# Ubuntu/Debian:
sudo apt-get install pgloader

# Windows:
# Download: https://pgloader.readthedocs.io/en/latest/install.html
```

Create migration config file: `migrate.load`

```
LOAD DATABASE
    FROM      mysql://root:Lead@0089@localhost:3306/rise
    INTO      postgresql://postgres:RENDER_PASSWORD@rise-db.onrender.com:5432/rise
    WITH      data only, skip truncate, create no indexes
    EXCLUDING TABLE NAMES MATCHING 'alembic%'
;
```

Run migration:
```bash
pgloader migrate.load
```

**Status**: Shows migration progress and results.

### Step 1.3: Manual SQL Import (If pgloader Not Available)

```bash
# Connect to PostgreSQL on Render
psql -U postgres -h rise-db.onrender.com -d rise

# Inside psql terminal:
\i backup.sql

# Or from command line:
psql -U postgres -h rise-db.onrender.com -d rise < backup.sql
```

**Password**: Enter the Render PostgreSQL password when prompted.

### Step 1.4: Verify Data

```bash
# Count records in PostgreSQL
psql -U postgres -h autism-cdss-db.onrender.com -d autism_cdss -c "
SELECT 
  'users' as table_name, COUNT(*) as count FROM users UNION ALL
SELECT 'children', COUNT(*) FROM children UNION ALL
SELECT 'assessments', COUNT(*) FROM assessments UNION ALL
SELECT 'predictions', COUNT(*) FROM predictions;
"
```

Compare with local MySQL:
```bash
mysql -u root -pLead@0089 autism_cdss -e "
SELECT 
  'users' as table_name, COUNT(*) as count FROM users UNION ALL
SELECT 'children', COUNT(*) FROM children UNION ALL
SELECT 'assessments', COUNT(*) FROM assessments UNION ALL
SELECT 'predictions', COUNT(*) FROM predictions;
"
```

Numbers should match!

---

## Option 2: Python Script Migration (Most Control)

Use this for detailed logging and error handling.

### Step 2.1: Create Migration Script

Create file: `migrate_data.py`

```python
#!/usr/bin/env python
"""
Migrate data from MySQL to PostgreSQL
Handles schema differences, data type conversions, etc.
"""

import pandas as pd
from sqlalchemy import create_engine
import sys

print("=" * 80)
print("MYSQL TO POSTGRESQL MIGRATION")
print("=" * 80)

# Source: Local MySQL
mysql_url = "mysql+pymysql://root:Lead%400089@localhost:3306/autism_cdss"

# Destination: Render PostgreSQL
postgres_url = "postgresql://postgres:RENDER_PASSWORD@autism-cdss-db.onrender.com:5432/autism_cdss"

try:
    print("\n1. Connecting to MySQL (source)...")
    mysql_engine = create_engine(mysql_url)
    mysql_conn = mysql_engine.connect()
    print("   ✓ Connected to MySQL")
    
    print("\n2. Connecting to PostgreSQL (destination)...")
    postgres_engine = create_engine(postgres_url)
    postgres_conn = postgres_engine.connect()
    print("   ✓ Connected to PostgreSQL")
    
    # List of tables to migrate
    tables = [
        'states', 'districts', 'mandals', 'anganwadi_centers',
        'children', 'assessments', 'predictions',
        'referrals', 'interventions', 'users', 'audit_logs'
    ]
    
    total_records = 0
    
    print("\n3. Migrating data...")
    for table in tables:
        try:
            # Query MySQL
            print(f"\n   Reading from {table}...", end=" ")
            df = pd.read_sql(f"SELECT * FROM {table}", mysql_conn)
            record_count = len(df)
            print(f"{record_count} records")
            
            # Insert to PostgreSQL (append, don't replace)
            print(f"   Writing to {table}...", end=" ")
            df.to_sql(table, postgres_engine, if_exists='append', index=False)
            print("✓")
            
            total_records += record_count
            
        except Exception as e:
            print(f"✗ ERROR: {e}")
            continue
    
    mysql_conn.close()
    postgres_conn.close()
    
    print("\n" + "=" * 80)
    print(f"MIGRATION COMPLETE!")
    print(f"Total records migrated: {total_records}")
    print("=" * 80)
    
except Exception as e:
    print(f"\n✗ MIGRATION FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
```

### Step 2.2: Update Passwords

```bash
# Replace RENDER_PASSWORD with actual PostgreSQL password from Render dashboard
sed -i "s/RENDER_PASSWORD/your_actual_password/g" migrate_data.py
```

### Step 2.3: Run Migration

```bash
python migrate_data.py
```

**Output**:
```
================================================================================
MYSQL TO POSTGRESQL MIGRATION
================================================================================

1. Connecting to MySQL (source)...
   ✓ Connected to MySQL

2. Connecting to PostgreSQL (destination)...
   ✓ Connected to PostgreSQL

3. Migrating data...

   Reading from states... 5 records
   Writing to states... ✓
   
   Reading from districts... 25 records
   Writing to districts... ✓
   
   Reading from children... 350 records
   Writing to children... ✓
   
   [... continues for all tables ...]

================================================================================
MIGRATION COMPLETE!
Total records migrated: 2847
================================================================================
```

---

## Option 3: Docker-Based Migration (Most Reliable)

For complex migrations with consistency guarantees.

### Step 3.1: Create Docker Container

```bash
# Start temporary PostgreSQL container
docker run -d \
  --name pg-temp \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=autism_cdss \
  -p 5433:5432 \
  postgres:15

# Wait for startup
sleep 5
```

### Step 3.2: Use pgloader Inside Container

```bash
docker run -it --rm \
  --network host \
  pgloader:3.6.7 \
  pgloader \
    --with "prefetch rows = 10000" \
    mysql://root:Lead@0089@localhost:3306/autism_cdss \
    postgresql://postgres:password@localhost:5433/autism_cdss
```

### Step 3.3: Verify and Push to Render

```bash
# Test migration locally
psql -U postgres -h localhost -p 5433 -d autism_cdss -c "SELECT COUNT(*) FROM children;"

# Export clean data
pg_dump -U postgres -h localhost -p 5433 autism_cdss > clean_backup.sql

# Import to Render
psql -U postgres -h autism-cdss-db.onrender.com -d autism_cdss < clean_backup.sql

# Cleanup
docker stop pg-temp
docker rm pg-temp
```

---

## Comparison of Methods

| Method | Time | Complexity | Reliability | Best For |
|--------|------|-----------|-------------|----------|
| **SQL Dump** | 2-5 min | Low | Good | Small datasets, simple migration |
| **Python Script** | 5-10 min | Medium | Excellent | Full control, logging, debugging |
| **Docker/pgloader** | 10-15 min | High | Best | Large datasets, complex schemas |

---

## Step-by-Step: Full Migration Walkthrough

### Prerequisites Check

```bash
# 1. MySQL running locally?
mysql -u root -pLead@0089 -e "SELECT VERSION();"

# 2. Can reach Render PostgreSQL?
psql -U postgres -h autism-cdss-db.onrender.com -d autism_cdss -c "SELECT 1;"
# (Will prompt for password - enter Render password)

# 3. Have psql installed?
psql --version

# 4. Have pgloader? (optional but recommended)
pgloader --version
```

### Migration Checklist

**Pre-Migration**:
- [ ] Backup local MySQL: `mysqldump -u root -pLead@0089 autism_cdss > backup_original.sql`
- [ ] Backup Render PostgreSQL: `pg_dump -U postgres -h autism-cdss-db.onrender.com -d autism_cdss > render_backup.sql`
- [ ] Stop API server (so no new data being written)
- [ ] Note down final record counts in MySQL

**Migration**:
- [ ] Choose method (SQL Dump recommended for first time)
- [ ] Export MySQL: `mysqldump -u root -pLead@0089 autism_cdss > backup.sql`
- [ ] Import to PostgreSQL: `psql -U postgres -h autism-cdss-db.onrender.com -d autism_cdss < backup.sql`

**Post-Migration**:
- [ ] Verify record counts match
- [ ] Check data integrity (spot check few records)
- [ ] Update API DATABASE_URL to PostgreSQL
- [ ] Restart API server
- [ ] Test login and data retrieval

---

## Verification Steps

### 1. Count Records

**MySQL**:
```bash
mysql -u root -pLead@0089 autism_cdss -e "
SELECT COUNT(*) as users FROM users;
SELECT COUNT(*) as children FROM children;
SELECT COUNT(*) as assessments FROM assessments;
SELECT COUNT(*) as predictions FROM predictions;
"
```

**PostgreSQL**:
```bash
psql -U postgres -h autism-cdss-db.onrender.com -d autism_cdss -c "
SELECT 'users' as table_name, COUNT(*) as count FROM users UNION ALL
SELECT 'children', COUNT(*) FROM children UNION ALL
SELECT 'assessments', COUNT(*) FROM assessments UNION ALL
SELECT 'predictions', COUNT(*) FROM predictions;
"
```

### 2. Sample Data Comparison

**MySQL**:
```bash
mysql -u root -pLead@0089 autism_cdss -e "
SELECT child_id, first_name, dob FROM children LIMIT 5;
"
```

**PostgreSQL**:
```bash
psql -U postgres -h autism-cdss-db.onrender.com -d autism_cdss -c "
SELECT child_id, first_name, dob FROM children LIMIT 5;
"
```

Data should look identical.

### 3. Check Relationships

```bash
# PostgreSQL: Verify foreign keys still work
psql -U postgres -h autism-cdss-db.onrender.com -d autism_cdss -c "
SELECT child_id, first_name, center_id FROM children
WHERE center_id IN (SELECT center_id FROM anganwadi_centers)
LIMIT 5;
"
```

### 4. Check Sequences

```bash
# PostgreSQL: Verify auto-increment sequences
psql -U postgres -h autism-cdss-db.onrender.com -d autism_cdss -c "
SELECT sequence_name FROM information_schema.sequences;
"
```

---

## Troubleshooting

### Error: "Access denied for user 'root'"

```bash
# Verify password
mysql -u root -pLead@0089 -e "SELECT 1;"

# Wrong password? Update in commands
# Don't forget: no space between -p and password!
```

### Error: "could not connect to server"

```bash
# Verify Render database is running
# Check: Render Dashboard → PostgreSQL → Status (should say "Available")

# Check connection string format
postgresql://postgres:PASSWORD@autism-cdss-db.onrender.com:5432/autism_cdss
# ↑ Exactly as shown, replace PASSWORD only
```

### Error: "column does not exist"

**Cause**: Schema mismatch - PostgreSQL table doesn't exist or has different columns.

**Solution**:
```bash
# Verify tables exist in PostgreSQL
psql -U postgres -h autism-cdss-db.onrender.com -d autism_cdss -c "
\dt"
```

If tables missing, schema wasn't created. Initialize first:
```bash
# Run on API startup (automatic or manual):
# This creates all tables from SQLAlchemy models
python -c "from backend.database import Base, engine; Base.metadata.create_all(engine)"
```

### Error: "duplicate key value"

**Cause**: Data already exists in PostgreSQL from previous migration attempt.

**Solution**:
```bash
# Option 1: Start fresh (if no critical data)
psql -U postgres -h autism-cdss-db.onrender.com -d autism_cdss -c "
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;"

# Option 2: Use INSERT ... ON CONFLICT (requires Python script)
```

### Error: "Nextval sequence mismatch"

**Cause**: Auto-increment IDs don't match after migration.

**Solution**:
```bash
# Sync sequences to max ID in each table
psql -U postgres -h autism-cdss-db.onrender.com -d autism_cdss << EOF
SELECT setval('users_user_id_seq', (SELECT MAX(user_id) FROM users)+1);
SELECT setval('children_child_id_seq', (SELECT MAX(child_id) FROM children)+1);
SELECT setval('assessments_assessment_id_seq', (SELECT MAX(assessment_id) FROM assessments)+1);
EOF
```

---

## Rollback Plan

### If Migration Fails

**Step 1**: Stop API server

```bash
# Don't let API write to broken PostgreSQL
# On Render: Dashboard → API Service → Stop
```

**Step 2**: Restore PostgreSQL

```bash
# Restore from backup
psql -U postgres -h autism-cdss-db.onrender.com -d autism_cdss < render_backup.sql
```

**Step 3**: Keep using MySQL

```bash
# Update API environment variable back to MySQL
DATABASE_URL=mysql+pymysql://root:Lead%400089@localhost:3306/autism_cdss

# Restart API
```

**Step 4**: Retry Migration

- Wait 24 hours (relax!)
- Try again with better preparation
- Use Python script for debugging

---

## After Successful Migration

### Update API to Use PostgreSQL

**Option A: On Render Dashboard**
1. Go to **autism-cdss-api** → **Environment**
2. Update `DATABASE_URL`:
   ```
   postgresql://postgres:PASSWORD@autism-cdss-db.onrender.com:5432/autism_cdss
   ```
3. Click **Save**
4. Wait for restart (~30 seconds)

**Option B: Via GitHub**
```bash
# Update .env locally
cd backend
echo "DATABASE_URL=postgresql://postgres:PASSWORD@autism-cdss-db.onrender.com:5432/autism_cdss" >> .env

# Push
git add .env
git commit -m "Switch to PostgreSQL on Render"
git push origin main
```

### Test API Connection

```bash
# Should return healthy status with PostgreSQL connection
curl https://autism-cdss-api.onrender.com/api/health

# Expected:
# {"status":"healthy","database":"connected","version":"1.0.0"}
```

### Stop Using Local MySQL

Once confirmed working:

```bash
# Stop MySQL locally (optional, can keep for backup)
mysql.server stop  # macOS
# OR
sudo systemctl stop mysql  # Linux
# OR
Use Services app to stop MySQL  # Windows
```

---

## Migration Summary

| Phase | Action | Time | Tools |
|-------|--------|------|-------|
| **Backup** | Export MySQL, backup Render | 2 min | mysqldump, pg_dump |
| **Prepare** | Initialize PostgreSQL schema | 1 min | Python/SQLAlchemy |
| **Migrate** | Transfer data MySQL → PostgreSQL | 2-5 min | pgloader or Python |
| **Verify** | Check data integrity | 2 min | SQL queries |
| **Cutover** | Switch API to PostgreSQL | 1 min | Render dashboard |
| **Test** | Health check, data retrieval | 2 min | curl, browser |

**Total Time**: ~10-15 minutes

---

## Example: Complete Migration Session

```bash
#!/bin/bash
# Complete migration script

echo "Step 1: Backup MySQL..."
mysqldump -u root -pLead@0089 --single-transaction autism_cdss > mysql_backup.sql
echo "✓ MySQL backed up to mysql_backup.sql"

echo ""
echo "Step 2: Backup PostgreSQL (Render)..."
psql -U postgres -h autism-cdss-db.onrender.com -d autism_cdss -Fc > pg_backup.dump
echo "✓ PostgreSQL backed up to pg_backup.dump"

echo ""
echo "Step 3: Migrate data..."
psql -U postgres -h autism-cdss-db.onrender.com -d autism_cdss < mysql_backup.sql
echo "✓ Data migrated to PostgreSQL"

echo ""
echo "Step 4: Verify counts..."
echo "MySQL counts:"
mysql -u root -pLead@0089 autism_cdss -e "SELECT COUNT(*) FROM children;"

echo ""
echo "PostgreSQL counts:"
psql -U postgres -h autism-cdss-db.onrender.com -d autism_cdss -c "SELECT COUNT(*) FROM children;"

echo ""
echo "✓ Migration complete! Update API DATABASE_URL to PostgreSQL."
```

Save as `migrate.sh` and run:
```bash
chmod +x migrate.sh
./migrate.sh
```

---

## Questions?

- **pgloader issues**: https://pgloader.readthedocs.io/
- **PostgreSQL docs**: https://www.postgresql.org/docs/
- **SQLAlchemy**: https://docs.sqlalchemy.org/
- **Render support**: https://render.com/support

---

**Status**: Ready to migrate!  
**Recommended Method**: SQL Dump + Import (simplest for first-time)  
**Estimated Time**: 15 minutes
