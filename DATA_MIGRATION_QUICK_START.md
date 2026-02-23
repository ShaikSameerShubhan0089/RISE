# Data Migration: MySQL to PostgreSQL (Quick Start)

## 🎯 Goal
Move your existing data from **local MySQL** → **Render PostgreSQL** before deploying

---

## ⏱️ Time: 10-15 minutes

---

## 📋 Checklist (Do These First!)

- [ ] **API is STOPPED** (not writing data during migration)
- [ ] **MySQL is running** locally
- [ ] **PostgreSQL exists** on Render (created in RENDER_SETUP.md)
- [ ] **Backups are made** (I'll create them)
- [ ] **PostgreSQL password** from Render dashboard (copy it!)

---

## 🚀 Method 1: Easiest - SQL Dump & Import (Recommended First Time)

### Step 1: Create MySQL Backup

```bash
# Run this locally
mysqldump -u root -pLead@0089 --single-transaction autism_cdss > mysql_backup.sql

# Verify file created
ls -lh mysql_backup.sql
```

**Output**:
```
mysql_backup.sql  (size: 1-100 MB depending on data)
```

### Step 2: Import to PostgreSQL

**Get your connection info**:
1. Go to: https://dashboard.render.com
2. Click: PostgreSQL service → **Info** tab
3. Copy: **Connection String**
   ```
   postgresql://postgres:PASSWORD@autism-cdss-db.onrender.com:5432/autism_cdss
   ```

**Import data** (choose one):

#### Option A: Using psql (Recommended)
```bash
# Replace PASSWORD with actual password from Step 1
psql -U postgres -h autism-cdss-db.onrender.com -d autism_cdss \
     -W < mysql_backup.sql

# When prompted: Enter password (from Render dashboard)
```

#### Option B: If psql not installed
Install PostgreSQL client:
```bash
# macOS
brew install postgresql

# Ubuntu/Debian
sudo apt-get install postgresql-client

# Windows
# Download: https://www.enterprisedb.com/download/postgresql-installer
```

### Step 3: Verify Migration

```bash
# Count records in MySQL
mysql -u root -pLead@0089 autism_cdss -e "SELECT COUNT(*) as count FROM children;"

# Count records in PostgreSQL
psql -U postgres -h autism-cdss-db.onrender.com -d autism_cdss \
     -c "SELECT COUNT(*) as count FROM children;"
     # When prompted: Enter password

# Numbers should match!
```

### ✅ Done!

Proceed to **Update API** section below.

---

## 🐍 Method 2: Python Script (More Control & Logging)

### Step 1: Prepare Script

```bash
# The script is ready: migrate_mysql_to_postgres.py
# Just need to update PostgreSQL password

# Open the script and find this line:
POSTGRES_URL = "postgresql://postgres:PASSWORD@autism-cdss-db.onrender.com:5432/autism_cdss"

# Replace PASSWORD with actual password from Render
```

### Step 2: Run Migration

```bash
python migrate_mysql_to_postgres.py

# When prompted:
# Continue with migration? (yes/no): yes
# Enter PostgreSQL password: [paste from Render]
```

**Output** (looks like):
```
================================================================================
MYSQL TO POSTGRESQL MIGRATION
================================================================================

[timestamp] SUCCESS: ✓ Connected to MySQL successfully
[timestamp] SUCCESS: ✓ Connected to PostgreSQL successfully
[timestamp] INFO: Found 11 tables

PRE-MIGRATION RECORD COUNTS (MySQL):
────────────────────────────────────
  states                        :        5
  districts                     :       25
  mandals                       :      150
  children                      :      350
  assessments                   :      700
  predictions                   :      420
  TOTAL                         :     1650

MIGRATING DATA:
────────────────────────────────────
1/11 states
✓ states: 5 records
2/11 districts
✓ districts: 25 records
...
[continues]

✓ MIGRATION SUCCESSFUL!

Next steps:
1. Update API environment variable:
   DATABASE_URL=postgresql://postgres:PASSWORD@host:5432/autism_cdss
2. Restart API service on Render
3. Test: curl https://api-url.com/api/health
```

### ✅ Done!

Proceed to **Update API** section below.

---

## 🔧 Update API to Use PostgreSQL

### Step 1: Update Environment Variable

**On Render Dashboard**:

1. Go to: https://dashboard.render.com
2. Click: **autism-cdss-api** service
3. Click: **Environment** tab
4. Find: `DATABASE_URL`
5. Change from:
   ```
   mysql+pymysql://root:Lead%400089@localhost:3306/autism_cdss
   ```
   To:
   ```
   postgresql://postgres:PASSWORD@autism-cdss-db.onrender.com:5432/autism_cdss
   ```
   (Replace PASSWORD with actual PostgreSQL password)

6. Click: **Save**
7. Wait for restart (~30 seconds)

**Via Git** (alternative):
```bash
# Edit: backend/.env
# Change DATABASE_URL line to PostgreSQL URL

# Commit and push
git add backend/.env
git commit -m "Switch to PostgreSQL on Render"
git push origin main
```

### Step 2: Test Connection

```bash
# Wait 30 seconds for restart, then:
curl https://autism-cdss-api.onrender.com/api/health

# Expected response:
# {"status":"healthy","database":"connected","version":"1.0.0"}
```

### ✅ Success!

Your data is now on PostgreSQL and API is connected!

---

## ✋ If Something Goes Wrong

### Problem: "Access denied" during migration

**Solution**:
```bash
# Check MySQL password
mysql -u root -pLead@0089 -e "SELECT 1;"

# Should return: 1
```

### Problem: "Could not connect to PostgreSQL"

**Solution**:
1. Verify database exists: Render dashboard → PostgreSQL → Check status
2. Wait 2-3 minutes if just created
3. Check password: Is it correct?
4. Try connecting directly:
   ```bash
   psql -U postgres -h autism-cdss-db.onrender.com
   # When prompted for password, enter it
   # Should see: psql (15.0)
   ```

### Problem: Record counts don't match

**MySQL count**:
```bash
mysql -u root -pLead@0089 autism_cdss -e "
SELECT 'users' as table_name, COUNT(*) as count FROM users UNION ALL
SELECT 'children', COUNT(*) FROM children UNION ALL
SELECT 'assessments', COUNT(*) FROM assessments UNION ALL
SELECT 'predictions', COUNT(*) FROM predictions;
"
```

**PostgreSQL count**:
```bash
psql -U postgres -h autism-cdss-db.onrender.com -d autism_cdss -c "
SELECT 'users' as table_name, COUNT(*) as count FROM users UNION ALL
SELECT 'children', COUNT(*) FROM children UNION ALL
SELECT 'assessments', COUNT(*) FROM assessments UNION ALL
SELECT 'predictions', COUNT(*) FROM predictions;
"
```

If different:
- Check for errors in migration output
- Try Python script method for detailed logging
- Check `migration.log` file

### Problem: Can't Login After Migration

**Cause**: User passwords not migrated correctly

**Solution**:
1. Create new test user in PostgreSQL
2. Check users table exists:
   ```bash
   psql -U postgres -h autism-cdss-db.onrender.com -d autism_cdss -c "SELECT * FROM users LIMIT 1;"
   ```
3. If no users: Manually create test user or restore from MySQL backup

### Problem: Data Looks Different

**Check data types**:
```bash
# MySQL
mysql -u root -pLead@0089 autism_cdss -e "DESC children;" | head -10

# PostgreSQL
psql -U postgres -h autism-cdss-db.onrender.com -d autism_cdss -c "\d children" | head -10
```

Usually fine - PostgreSQL auto-converts types.

---

## 🆘 Rollback (If Needed)

```bash
# Stop using PostgreSQL and go back to MySQL

# 1. Stop API
# (Render Dashboard → autism-cdss-api → Stop)

# 2. Update DATABASE_URL back to MySQL
# (Render Dashboard → Environment)
# DATABASE_URL=mysql+pymysql://root:Lead%400089@localhost:3306/autism_cdss

# 3. Restart API

# You still have your MySQL data intact locally!
```

---

## 📊 Comparison After Migration

| Aspect | Before | After |
|--------|--------|-------|
| Database | MySQL (local) | PostgreSQL (Render) |
| Access | localhost:3306 | autism-cdss-db.onrender.com:5432 |
| Data Location | Your computer | Render servers |
| Backup | Manual | Automatic |
| Reliability | Good | Better (Render managed) |
| Scalability | Limited | Enterprise-grade |

---

## ✅ Verification Checklist

- [ ] MySQL backup created: `mysql_backup.sql`
- [ ] Data migrated to PostgreSQL
- [ ] Record counts match MySQL ↔ PostgreSQL
- [ ] API DATABASE_URL updated to PostgreSQL
- [ ] API restarted
- [ ] Health check returns "healthy"
- [ ] Can login to frontend
- [ ] Previous assessments data visible
- [ ] Can create new assessments
- [ ] ML predictions work

---

## 🎉 You're Done!

Your data is now:
- ✓ Safely migrated
- ✓ On Render PostgreSQL
- ✓ Connected to API
- ✓ Backed up automatically
- ✓ Ready for production

---

## Detailed Guide

For more details (troubleshooting, advanced options, rollback):
→ See: `MIGRATE_MYSQL_TO_POSTGRESQL.md`

---

**Questions?**
- PostgreSQL: https://www.postgresql.org/docs/
- Render: https://render.com/docs
- SQLAlchemy: https://docs.sqlalchemy.org/

---

**Time Estimate**: 10-15 minutes  
**Difficulty**: Easy (Method 1) / Medium (Method 2)  
**Risk**: Low (with backups)
