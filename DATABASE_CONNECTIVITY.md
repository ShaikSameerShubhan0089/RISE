# Database Connectivity: Local vs Render

## Problem

Your current setup uses **MySQL** locally, but Render provides **PostgreSQL**. They're different databases!

```
Local Development      vs      Render Production
─────────────────────         ─────────────────────
MySQL                         PostgreSQL
mysql+pymysql://              postgresql://
port 3306                      port 5432
Lead%400089                    auto-generated password
localhost:3306                 autism-cdss-db.onrender.com:5432
```

---

## Solution: Automatic Detection

Your code already handles this! The database driver is determined by the `DATABASE_URL` prefix:

### Local (MySQL)
```python
DATABASE_URL = "mysql+pymysql://root:Lead%400089@localhost:3306/autism_cdss"
# Driver: PyMySQL
# Database: MySQL
```

### Render (PostgreSQL)
```python
DATABASE_URL = "postgresql://postgres:PASSWORD@autism-cdss-db.onrender.com:5432/autism_cdss"
# Driver: psycopg2 (binary)
# Database: PostgreSQL
```

### Code in `backend/database.py`
```python
from sqlalchemy import create_engine

DATABASE_URL = os.getenv("DATABASE_URL")

# SQLAlchemy auto-detects DB type from URL prefix
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)
```

✅ **No changes needed** - SQLAlchemy handles it automatically!

---

## Connection String Format

### MySQL (Local)
```
mysql+pymysql://[user]:[password]@[host]:[port]/[database]
mysql+pymysql://root:Lead%400089@localhost:3306/autism_cdss
```

**Components**:
- `user`: `root`
- `password`: `Lead%400089` (URL-encoded if special chars)
- `host`: `localhost`
- `port`: `3306`
- `database`: `autism_cdss`

### PostgreSQL (Render)
```
postgresql://[user]:[password]@[host]:[port]/[database]
postgresql://postgres:XXXXX@autism-cdss-db.onrender.com:5432/autism_cdss
```

**Components**:
- `user`: `postgres` (default Render user)
- `password`: (random, from Render dashboard)
- `host`: `autism-cdss-db.onrender.com` (Render internal hostname)
- `port`: `5432` (PostgreSQL default)
- `database`: `autism_cdss` (auto-created)

---

## Special Characters in Passwords

If your password has special characters, URL-encode them:

| Character | Encoded | Example |
|-----------|---------|---------|
| `@` | `%40` | `Pass@word` → `Pass%40word` |
| `#` | `%23` | `Pass#123` → `Pass%23123` |
| `:` | `%3A` | `Pass:123` → `Pass%3A123` |
| `/` | `%2F` | `Pass/123` → `Pass%2F123` |
| `%` | `%25` | `Pass%123` → `Pass%25123` |

**Your local password**:
```
Original: Lead@0089
Encoded:  Lead%400089
```

---

## Testing Connection

### Test MySQL Locally
```bash
python -c "
from sqlalchemy import create_engine, text

url = 'mysql+pymysql://root:Lead%400089@localhost:3306/autism_cdss'
engine = create_engine(url)

try:
    with engine.connect() as conn:
        result = conn.execute(text('SELECT 1'))
    print('✓ MySQL connection successful')
except Exception as e:
    print(f'✗ MySQL connection failed: {e}')
"
```

### Test PostgreSQL (After Render Setup)
```bash
python -c "
from sqlalchemy import create_engine, text

url = 'postgresql://postgres:PASSWORD@autism-cdss-db.onrender.com:5432/autism_cdss'
engine = create_engine(url)

try:
    with engine.connect() as conn:
        result = conn.execute(text('SELECT 1'))
    print('✓ PostgreSQL connection successful')
except Exception as e:
    print(f'✗ PostgreSQL connection failed: {e}')
"
```

### Test via API
```bash
curl http://localhost:8000/api/health
# Should return:
# {"status":"healthy","database":"connected","version":"1.0.0"}
```

---

## Database Schema

Both MySQL and PostgreSQL use the same **SQLAlchemy ORM**, so schemas are identical:

```
autism_cdss/
├── users (authentication)
├── children (patient info)
├── assessments (test scores)
├── predictions (risk predictions)
├── referrals (specialist referrals)
├── interventions (treatment plans)
└── audit_logs (tracking)
```

**Auto-initialization** happens on API startup:
```python
# In backend/database.py
Base.metadata.create_all(bind=engine)
```

This creates all tables automatically, whether MySQL or PostgreSQL!

---

## Connection Pool Configuration

Both databases use the same pool settings:

```python
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,      # Test connection before use
    pool_size=10,             # 10 connections in pool
    max_overflow=20,          # Allow up to 20 extra connections
    echo=False                # Don't log SQL queries (set to True for debugging)
)
```

**Meaning**:
- `pool_pre_ping`: Prevents "connection has gone away" errors
- `pool_size=10`: Base connections to keep open
- `max_overflow=20`: Allow temp connections during high load (total: 30)

---

## Environment Variable Management

### Local Development
```bash
# .env file in backend/
DATABASE_URL=mysql+pymysql://root:Lead%400089@localhost:3306/autism_cdss
```

### Render Production
```bash
# Set in Render Dashboard → Service → Environment
DATABASE_URL=postgresql://postgres:PASSWORD@autism-cdss-db.onrender.com:5432/autism_cdss
```

### In Code
```python
# Automatically loaded from .env or environment
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
```

---

## Common Errors & Solutions

### Error: `Access denied for user 'root'`
**Cause**: Wrong MySQL password or MySQL not running
**Solution**:
```bash
mysql -u root -p  # Test login locally
```
Check password in `.env` matches MySQL actual password.

### Error: `could not connect to server: Connection refused`
**Cause**: 
- PostgreSQL database not created yet, OR
- Network connectivity issue, OR
- Wrong hostname
**Solution**:
1. Verify database created in Render: Dashboard → PostgreSQL → Check status
2. Wait 2-3 minutes for database to start
3. Verify hostname in Render dashboard
4. Check if API service can reach database (same region)

### Error: `FATAL: password authentication failed for user "postgres"`
**Cause**: Wrong password in DATABASE_URL
**Solution**:
1. Go to Render PostgreSQL dashboard
2. Copy exact connection string
3. Paste into API environment variable
4. Re-deploy

### Error: `relation "users" does not exist`
**Cause**: Schema not created
**Solution**:
```python
# In backend/database.py, ensure this runs:
Base.metadata.create_all(bind=engine)

# Or manually:
from backend.models import Base
from backend.database import engine
Base.metadata.create_all(bind=engine)
```

### Error: `(psycopg2.OperationalError) could not connect...`
**Cause**: psycopg2 driver not installed
**Solution**:
```bash
pip install psycopg2-binary
# Or already in requirements.txt:
psycopg2-binary>=2.9.9
```

---

## Migration from MySQL to PostgreSQL (Optional)

If you want to migrate existing data:

### Step 1: Dump MySQL Data
```bash
mysqldump -u root -p autism_cdss > backup.sql
```

### Step 2: Convert SQL Syntax (if needed)
```bash
# Some SQL dialects differ; PostgreSQL is more standard
# Usually no conversion needed for basic schemas
```

### Step 3: Import to PostgreSQL
```bash
psql -U postgres -d autism_cdss -f backup.sql
```

### Step 4: Update DATABASE_URL
```bash
# Change API environment to PostgreSQL
DATABASE_URL=postgresql://postgres:PASSWORD@autism-cdss-db.onrender.com:5432/autism_cdss
```

---

## Performance Tips

### MySQL (Local)
- Good for development
- Simpler setup
- Slower than PostgreSQL for complex queries

### PostgreSQL (Render)
- Better for production
- Faster queries
- Better connection pooling
- More reliable

**Recommendation**: Develop with MySQL locally, deploy with PostgreSQL on Render.

---

## Connection Limits

### Free Tier Render PostgreSQL
- Max 10 concurrent connections
- 1 GB storage
- 7 days backup retention

### Starter Tier Render PostgreSQL ($15/mo)
- Max 100 connections
- 10 GB storage
- 14 days backup retention

**Upgrade if**: Your app creates many concurrent connections or data exceeds 1 GB.

---

## Network Diagram

### Local (Both on Same Machine)
```
React (3000)
    ↓
FastAPI Backend (8000)
    ↓
MySQL (3306)
```

All via `localhost` - no network latency.

### Render (Different Services)
```
Browser → CDN
    ↓
React Frontend (Static Site)
    ↓ HTTPS
FastAPI Backend (Web Service)
    ↓ Internal Network
PostgreSQL (Database)
```

All on Render's internal network - very fast.

---

## Summary

| Aspect | Local | Render |
|--------|-------|--------|
| Database | MySQL | PostgreSQL |
| Driver | PyMySQL | psycopg2 |
| Host | localhost | autism-cdss-db.onrender.com |
| Port | 3306 | 5432 |
| Connection | Direct | Network tunnel |
| Setup | Manual | Auto |
| Backup | Manual | Automatic |
| **Cost** | **Free** | **Free tier / $15/mo standard** |

---

## Checklist Before Deploying

- [ ] `.env` file in `backend/` with MySQL URL
- [ ] Requirements includes `psycopg2-binary` for PostgreSQL
- [ ] `DATABASE_URL` in Render environment uses PostgreSQL format
- [ ] ML models saved and committed to git
- [ ] Database health check passes: `curl /api/health`
- [ ] Schema auto-creates (or use Alembic for migrations)
- [ ] API can query PostgreSQL after deployment

---

**Questions?** See DEPLOYMENT_GUIDE.md or RENDER_SETUP.md
