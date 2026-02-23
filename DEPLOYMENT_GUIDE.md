# Autism CDSS - Render Deployment Guide

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Render Platform                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Frontend (React)          API (FastAPI)       Database     │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────┐  │
│  │ React SPA        │  │ Backend Server   │  │PostgreSQL│  │
│  │ (Static Site)    │──│ (uvicorn)        │──│  (DB)    │  │
│  │ dist/index.html  │  │ Port 8000        │  │ Port 5432│  │
│  └──────────────────┘  └──────────────────┘  └──────────┘  │
│                             ▲                                │
│                             │                                │
│                       ML Models (pkl)                        │
│                   ml/models/saved/*.pkl                      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
         │                    │                     │
      HTTPS             WebSocket/REST           Connection
                                                   Pool
```

---

## Step 1: Prepare Your Code

### 1.1 Update Database Configuration

**Current Issue**: Your backend uses MySQL locally, Render provides PostgreSQL.

#### Update `backend/database.py` to auto-detect:

```python
import os
from urllib.parse import urlparse

DATABASE_URL = os.getenv("DATABASE_URL")

# Auto-detect database type
if DATABASE_URL:
    parsed = urlparse(DATABASE_URL)
    if parsed.scheme.startswith('postgresql'):
        # PostgreSQL connection (Render production)
        print("✓ Using PostgreSQL")
    elif parsed.scheme.startswith('mysql'):
        # MySQL connection (Local development)
        print("✓ Using MySQL")
else:
    # Default to PostgreSQL for production
    DATABASE_URL = "postgresql://postgres:password@localhost:5432/autism_cdss"

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    echo=False
)
```

### 1.2 Save ML Models

```bash
python save_models_for_deployment.py
```

This creates:
- `ml/models/saved/autism_risk_classifier_v1.pkl` (2.17 MB)
- `ml/models/saved/risk_escalation_predictor_v1.pkl` 

**Important**: Commit these pickle files to GitHub!

### 1.3 Check Requirements

```bash
pip install -r requirements.txt
```

Verify the file includes:
- `psycopg2-binary>=2.9.9` (PostgreSQL driver)
- `SQLAlchemy>=2.0.0`
- `xgboost>=2.0.0`
- `shap>=0.42.0`

---

## Step 2: Create Render Services

### 2.1 Create Free Tier PostgreSQL Database

**On Render Dashboard:**

1. Click **"New +"** → **PostgreSQL**
2. Name: `autism-cdss-db`
3. Plan: **Free** (has limits, upgrade for production)
4. Region: Same as API (e.g., Singapore, N. Virginia)
5. Click **Create**
6. Note the Internal Connection String (save it temporarily)

### 2.2 Deploy FastAPI Backend

**On Render Dashboard:**

1. Click **"New +"** → **Web Service**
2. Connect your GitHub repository
3. Configure:
   - **Name**: `autism-cdss-api`
   - **Runtime**: Python
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Free or Starter ($7/month)

4. Set **Environment Variables**:

| Key | Value |
|-----|-------|
| `DATABASE_URL` | `postgresql://postgres:PASSWORD@autism-cdss-db:5432/autism_cdss` |
| `JWT_SECRET` | Generate: `python -c "import secrets; print(secrets.token_urlsafe(64))"` |
| `JWT_ALGORITHM` | `HS256` |
| `JWT_EXPIRATION` | `1440` |
| `API_HOST` | `0.0.0.0` |
| `API_PORT` | `8000` |
| `API_RELOAD` | `False` |
| `CORS_ORIGINS` | `https://autism-cdss-frontend.onrender.com` |
| `ML_MODEL_PATH` | `./ml/models/saved/` |
| `LOG_LEVEL` | `INFO` |

5. Click **Create Web Service**
6. Wait for deployment (~2-5 minutes)

### 2.3 Deploy React Frontend

**On Render Dashboard:**

1. Click **"New +"** → **Static Site**
2. Connect your GitHub repository
3. Configure:
   - **Name**: `autism-cdss-frontend`
   - **Build Command**: `cd frontend && npm install && npm run build`
   - **Publish Directory**: `frontend/dist`

4. Before creating, add **Environment Variable**:
   
   Create `.env.production` in `frontend/`:
   ```
   VITE_API_URL=https://autism-cdss-api.onrender.com/api
   ```

5. Click **Create Static Site**
6. Wait for deployment (~2-3 minutes)

---

## Step 3: Database Setup

### 3.1 Initialize Database Schema

You have two options:

#### Option A: Auto-initialization on startup
Your `database.py` with `Base.metadata.create_all(bind=engine)` will auto-create tables.

#### Option B: Use Alembic for migrations

```bash
# Generate migration
alembic revision --autogenerate -m "Initial schema"

# Apply migration
alembic upgrade head
```

### 3.2 Verify Database Connection

**Test Endpoint**:
```bash
curl https://autism-cdss-api.onrender.com/api/health
```

Expected Response:
```json
{
  "status": "healthy",
  "database": "connected",
  "version": "1.0.0"
}
```

---

## Step 4: Environment Variables Checklist

### Backend (.env in Render Dashboard)

```
DATABASE_URL=postgresql://postgres:XXXXX@autism-cdss-db:5432/autism_cdss
JWT_SECRET=<64-char random string>
JWT_ALGORITHM=HS256
JWT_EXPIRATION=1440
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=False
CORS_ORIGINS=https://autism-cdss-frontend.onrender.com,https://yourdomain.com
ML_MODEL_PATH=./ml/models/saved/
LOG_LEVEL=INFO
```

### Frontend (.env.production in git)

```
VITE_API_URL=https://autism-cdss-api.onrender.com/api
VITE_APP_NAME=Autism Risk Stratification CDSS
```

---

## Step 5: Troubleshooting

### 5.1 Database Connection Failed

**Error**: `could not connect to server: Connection refused`

**Solution**:
1. Check DATABASE_URL format: `postgresql://user:pass@host:5432/dbname`
2. Verify credentials in Render PostgreSQL dashboard
3. Ensure API service can reach DB service (same region)

### 5.2 ML Models Not Found

**Error**: `FileNotFoundError: ./ml/models/saved/autism_risk_classifier_v1.pkl`

**Solution**:
1. Commit `.pkl` files to GitHub: `git add ml/models/saved/*.pkl`
2. Ensure `.gitignore` doesn't exclude `*.pkl` files
3. Rebuild service on Render dashboard

### 5.3 CORS Origin Mismatch

**Error**: `Access to XMLHttpRequest blocked by CORS policy`

**Solution**:
1. Get frontend URL from Render: `https://autism-cdss-frontend.onrender.com`
2. Add to `CORS_ORIGINS` in API dashboard
3. Restart API service

### 5.4 Out of Memory (Free Tier)

**Error**: Service killed due to memory limit

**Solution**:
1. Upgrade to Starter plan ($7/month)
2. Or optimize model loading (load on-demand)

---

## Step 6: Database Backup & Maintenance

### 6.1 Backup PostgreSQL Data

```bash
# Export database
pg_dump postgresql://user:pass@host:5432/autism_cdss > backup.sql

# Import database
psql postgresql://user:pass@host:5432/autism_cdss < backup.sql
```

### 6.2 Monitor Database Size

On Render PostgreSQL dashboard:
- Storage used: Monitor to avoid exceeding limits
- Connections: Max 10 on free tier

---

## Step 7: Production Optimization

### 7.1 Enable HTTPS

Render auto-enables HTTPS. Update:
```
HTTPS_ONLY=True
SECURE_COOKIES=True
```

### 7.2 Set Up Custom Domain

1. Go to Frontend service
2. Click **Settings** → **Custom Domain**
3. Add your domain: `autism-cdss.yourdomain.com`
4. Update DNS CNAME records

### 7.3 Upgrade Plans for Production

| Service | Recommended | Cost |
|---------|-------------|------|
| Frontend | Static Site | Free |
| Backend | Starter | $7/month |
| Database | Standard | $15/month |
| **Total** | - | **$22/month** |

---

## Step 8: Deploy & Go Live

### 8.1 Final Checklist

- [ ] Code committed to GitHub
- [ ] ML models saved and committed
- [ ] All environment variables set in Render dashboard
- [ ] Database initialized and migrated
- [ ] Health check endpoint returns `200 OK`
- [ ] Frontend loads successfully
- [ ] Authentication works
- [ ] ML predictions work end-to-end

### 8.2 Test Production Deployment

```bash
# Test health
curl https://autism-cdss-api.onrender.com/api/health

# Test frontend
https://autism-cdss-frontend.onrender.com

# Test API docs
https://autism-cdss-api.onrender.com/api/docs
```

### 8.3 Monitor & Logs

**On Render Dashboard**:
- Click service → **Logs** to view real-time logs
- Set up email alerts for service failures
- Monitor database storage usage

---

## Step 9: Git Push to Deploy

After any code changes:

```bash
git add .
git commit -m "Update for production deployment"
git push origin main
```

Render automatically redeploys on push to `main` branch.

---

## Connection Flow Example

### Initial Request
```
User Browser
    ↓
https://autism-cdss-frontend.onrender.com
    ↓
React App loads (index.html from Render Static Site)
    ↓
App makes API call to https://autism-cdss-api.onrender.com/api/predictions/run
    ↓
FastAPI receives request
    ↓
Loads ML model from ./ml/models/saved/autism_risk_classifier_v1.pkl
    ↓
Queries PostgreSQL at autism-cdss-db:5432
    ↓
Returns JSON prediction with risk tier + explanations
```

---

## Quick Reference: URL Mappings

| Service | URL | Purpose |
|---------|-----|---------|
| Frontend | `https://autism-cdss-frontend.onrender.com` | React app |
| API | `https://autism-cdss-api.onrender.com/api` | REST endpoints |
| API Docs | `https://autism-cdss-api.onrender.com/api/docs` | Swagger UI |
| Database | `autism-cdss-db:5432` | PostgreSQL (internal only) |

---

## Support & Troubleshooting

- **Render Status**: https://status.render.com
- **Render Docs**: https://render.com/docs
- **PostgreSQL Docs**: https://www.postgresql.org/docs/
- **FastAPI Docs**: https://fastapi.tiangolo.com/deployment/

---

Generated: 2026-02-21
Last Updated: 2026-02-21
