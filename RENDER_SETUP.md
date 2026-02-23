# Render Deployment - Quick Setup

## What You Need

1. **GitHub Account** - To connect your repo
2. **Render Account** - https://render.com (free)
3. **Trained ML Models** - `*.pkl` files saved
4. **Environment Variables** - Database credentials, JWT secret

---

## Detailed Steps

### Step 1: Prepare Code (5 minutes)

```bash
# 1. Save ML models
python save_models_for_deployment.py

# 2. Commit everything
git add .
git commit -m "Prepare for Render deployment"
git push origin main
```

**What gets saved**:
```
ml/models/saved/
├── autism_risk_classifier_v1.pkl (2.17 MB)
└── risk_escalation_predictor_v1.pkl (~1 MB)
```

### Step 2: Create PostgreSQL Database (3 minutes)

**Go to**: https://dashboard.render.com

1. Click **+ New**
2. Select **PostgreSQL**
3. Name: `autism-cdss-db`
4. Plan: **Free** ($0/month, 1 GB storage)
5. Region: Pick same as API (e.g., Singapore)
6. Click **Create Database**

**Save these credentials**:
- Host: `autism-cdss-db.onrender.com` (or similar)
- Database: `autism_cdss` (auto-created)
- User: `postgres`
- Password: (auto-generated, copy it!)
- Port: `5432`

**Connection String**:
```
postgresql://postgres:PASSWORD@autism-cdss-db.onrender.com:5432/autism_cdss
```

### Step 3: Deploy Backend API (5 minutes)

**On Render Dashboard**:

1. Click **+ New** → **Web Service**
2. Select **Connect a Repository**
3. Choose your GitHub repo
4. Configuration:
   ```
   Name: autism-cdss-api
   Root Directory: (leave blank)
   Runtime: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT
   Plan: Free (or Starter $7/month)
   ```

5. Click **Create Web Service**
6. While deploying, go to **Environment** tab and add variables:

```
DATABASE_URL = postgresql://postgres:PASSWORD@autism-cdss-db.onrender.com:5432/autism_cdss
JWT_SECRET = (generate: python -c "import secrets; print(secrets.token_urlsafe(64))")
JWT_ALGORITHM = HS256
JWT_EXPIRATION = 1440
API_HOST = 0.0.0.0
API_PORT = 8000
API_RELOAD = False
CORS_ORIGINS = https://autism-cdss-frontend.onrender.com
ML_MODEL_PATH = ./ml/models/saved/
LOG_LEVEL = INFO
```

7. Save & Deploy
8. **Get Backend URL**: `https://autism-cdss-api.onrender.com`

### Step 4: Deploy Frontend (3 minutes)

**On Render Dashboard**:

1. Click **+ New** → **Static Site**
2. Connect your GitHub repo
3. Configuration:
   ```
   Name: autism-cdss-frontend
   Root Directory: (leave blank)
   Build Command: cd frontend && npm install && npm run build
   Publish Directory: frontend/dist
   ```

4. Before creating, add file: `frontend/.env.production`

```
VITE_API_URL=https://autism-cdss-api.onrender.com/api
```

5. Click **Create Static Site**
6. **Get Frontend URL**: `https://autism-cdss-frontend.onrender.com`

### Step 5: Update CORS (2 minutes)

Go back to **autism-cdss-api** service → **Environment**:

Update:
```
CORS_ORIGINS = https://autism-cdss-frontend.onrender.com
```

Click **Save** and wait for restart (~30 seconds).

### Step 6: Test (5 minutes)

```bash
# 1. Check API health
curl https://autism-cdss-api.onrender.com/api/health

# Expected response:
# {"status":"healthy","database":"connected","version":"1.0.0"}

# 2. Open frontend
# https://autism-cdss-frontend.onrender.com

# 3. Test login & prediction
# Create a test user and try making predictions
```

---

## Troubleshooting Quick Fixes

### API returns 500 Error
→ Check logs: Dashboard → **autism-cdss-api** → **Logs**
→ Usually: database connection, missing environment variable, or ML model file not found

### Frontend shows blank page
→ Check browser console: Right-click → **Inspect** → **Console**
→ Usually: CORS issue or API URL wrong

### Can't connect to database
→ Verify `DATABASE_URL` in API Environment variables
→ Format must be: `postgresql://user:pass@host:5432/dbname`

### ML models not found
→ Check git: `git log --all --full-history -- "ml/models/saved/"`
→ Make sure `*.pkl` files are committed: `git add ml/models/saved/*.pkl`

---

## Cost Breakdown

| Service | Free Tier | Starter | Notes |
|---------|-----------|---------|-------|
| Frontend (Static) | $0 | $0 | No cost |
| Backend API | $0 (limited) | $7/mo | Free: 750 hrs/month, 0.5GB RAM |
| Database | $0 (limited) | $15/mo | Free: 1GB storage, 10 connections |
| **Total** | **$0** | **$22/mo** | Recommended for production |

**Note**: Free tier API auto-sleeps after 15 mins inactivity. Upgrade to Starter for always-on.

---

## Important: Database Connection String

**Local Development**:
```
mysql+pymysql://root:password@localhost:3306/autism_cdss
```

**Render Production**:
```
postgresql://postgres:PASSWORD@autism-cdss-db.onrender.com:5432/autism_cdss
```

Your code automatically detects which database to use based on the URL prefix!

---

## After Deployment

1. **Monitor Logs**: Dashboard → Service → Logs
2. **Set Alerts**: Dashboard → Service → Alerts
3. **Backup Data**: Export database monthly
4. **Update Domain**: Add custom domain when ready

---

## Need Help?

- **Render Docs**: https://render.com/docs
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **PostgreSQL Docs**: https://www.postgresql.org/docs/
- **GitHub Status**: https://www.githubstatus.com

---

✅ **You're done!** Your app is now live on Render!
