# Render Deployment Checklist

## 📋 Overview

This checklist guides you through deploying your Autism Risk Stratification CDSS to Render with proper database connectivity.

**Current Status**: ✅ All files prepared for deployment

---

## 🔧 Phase 1: Local Preparation (15 minutes)

- [ ] **Save ML Models**
  ```bash
  python save_models_for_deployment.py
  ```
  Creates: `ml/models/saved/*.pkl`

- [ ] **Verify Requirements**
  ```bash
  cat requirements.txt | grep -E "(psycopg2|SQLAlchemy|xgboost|shap)"
  ```
  Should show PostgreSQL driver included

- [ ] **Test Locally** (optional)
  ```bash
  cd backend
  uvicorn main:app --reload
  ```
  Check: `http://localhost:8000/api/health`

- [ ] **Commit All Changes**
  ```bash
  git add -A
  git commit -m "Prepare for Render deployment - add models, configs, docs"
  git push origin main
  ```
  **⚠️ Important**: ML model `.pkl` files must be committed!

---

## 🌐 Phase 2: Render Setup (15 minutes)

### 2.1 Create PostgreSQL Database

- [ ] Go to: https://dashboard.render.com
- [ ] Click: **+ New** → **PostgreSQL**
- [ ] Settings:
  - Name: `autism-cdss-db`
  - Region: Choose your region (Singapore/US-East-1)
  - Plan: **Free** ($0/month)
- [ ] Click: **Create Database**
- [ ] **Save these credentials**:
  - Host: _______________
  - Database: `autism_cdss`
  - User: `postgres`
  - Password: _______________

### 2.2 Create Backend API Service

- [ ] Click: **+ New** → **Web Service**
- [ ] Select your GitHub repository
- [ ] Settings:
  ```
  Name: autism-cdss-api
  Runtime: Python 3
  Build Command: pip install -r requirements.txt
  Start Command: cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT
  Plan: Free (optional: Starter $7/mo for always-on)
  ```
- [ ] Click: **Create Web Service**
- [ ] **While deploying**, go to **Environment** tab

### 2.3 Add Backend Environment Variables

In the **autism-cdss-api** service, Environment section, add:

| Key | Value | Where from |
|-----|-------|-----------|
| `DATABASE_URL` | `postgresql://postgres:PASSWORD@autism-cdss-db.onrender.com:5432/autism_cdss` | Step 2.1 credentials |
| `JWT_SECRET` | `python -c "import secrets; print(secrets.token_urlsafe(64))"` | Run this command locally |
| `JWT_ALGORITHM` | `HS256` | Copy as-is |
| `JWT_EXPIRATION` | `1440` | Copy as-is |
| `API_HOST` | `0.0.0.0` | Copy as-is |
| `API_PORT` | `8000` | Copy as-is |
| `API_RELOAD` | `False` | Copy as-is |
| `CORS_ORIGINS` | `https://autism-cdss-frontend.onrender.com` | Will update after frontend deploy |
| `ML_MODEL_PATH` | `./ml/models/saved/` | Copy as-is |
| `LOG_LEVEL` | `INFO` | Copy as-is |

- [ ] Click: **Save**
- [ ] Wait for deployment (status changes to "Live")
- [ ] **Save API URL**: `https://autism-cdss-api.onrender.com`

### 2.4 Deploy Frontend

- [ ] Click: **+ New** → **Static Site**
- [ ] Select your GitHub repository
- [ ] Settings:
  ```
  Name: autism-cdss-frontend
  Build Command: cd frontend && npm install && npm run build
  Publish Directory: frontend/dist
  ```
- [ ] **Before creating**, ensure `frontend/.env.production` exists:
  ```
  VITE_API_URL=https://autism-cdss-api.onrender.com/api
  ```
- [ ] Click: **Create Static Site**
- [ ] **Save Frontend URL**: `https://autism-cdss-frontend.onrender.com`

### 2.5 Update Backend CORS

- [ ] Go back to **autism-cdss-api** service
- [ ] Go to **Environment** tab
- [ ] Update `CORS_ORIGINS`:
  ```
  https://autism-cdss-frontend.onrender.com
  ```
- [ ] Click: **Save**
- [ ] Wait for restart (~30 seconds)

---

## ✅ Phase 3: Verification (10 minutes)

### 3.1 API Health Check

- [ ] Run:
  ```bash
  curl https://autism-cdss-api.onrender.com/api/health
  ```
- [ ] Expected Response:
  ```json
  {"status":"healthy","database":"connected","version":"1.0.0"}
  ```
- [ ] If FAILED:
  - Check logs: Dashboard → **autism-cdss-api** → **Logs**
  - Common issues: DATABASE_URL wrong, ML models not found

### 3.2 Frontend Load

- [ ] Open: https://autism-cdss-frontend.onrender.com
- [ ] Check page loads (no blank page)
- [ ] If FAILED:
  - Check browser console: Right-click → **Inspect** → **Console**
  - Check if API URL shows errors

### 3.3 Full Integration Test

- [ ] Click: **Login** (create test user)
- [ ] Click: **Add Child Assessment**
- [ ] Fill form with test data (use values from earlier analysis)
- [ ] Click: **Get Risk Prediction**
- [ ] Verify: Risk tier + clinical action displays
- [ ] Verify: SHAP explanations show top 5 features

### 3.4 Database Verification

- [ ] Check data persists:
  - Refresh page
  - Previously added data should still be visible
- [ ] If NOT persisting:
  - Check DATABASE_URL in API environment variables
  - Verify schema created: Check Render PostgreSQL logs

---

## 🔍 Phase 4: Troubleshooting

### Issue: API returns 500 Internal Server Error

**Steps**:
1. Dashboard → **autism-cdss-api** → **Logs**
2. Look for error messages
3. Common causes:
   - `DATABASE_URL` format wrong
   - `ML_MODEL_PATH` file not found
   - Missing environment variable
4. Fix and re-deploy: Push to GitHub or click **Redeploy**

### Issue: CORS Error in Frontend

**Error**: `Access to XMLHttpRequest blocked by CORS policy`

**Steps**:
1. Go to **autism-cdss-api** environment
2. Check `CORS_ORIGINS` matches your frontend URL
3. Add your domain if needed:
   ```
   https://autism-cdss-frontend.onrender.com,https://yourdomain.com
   ```
4. Save and restart

### Issue: ML Models Not Found

**Error**: `FileNotFoundError: ./ml/models/saved/autism_risk_classifier_v1.pkl`

**Steps**:
1. Verify files committed:
   ```bash
   git ls-tree -r HEAD ml/models/saved/
   ```
2. If empty, run locally:
   ```bash
   python save_models_for_deployment.py
   git add ml/models/saved/
   git commit -m "Add ML models"
   git push
   ```
3. Redeploy on Render

### Issue: Database Connection Timeout

**Error**: `could not translate host name "autism-cdss-db.onrender.com" to address`

**Steps**:
1. Wait 2-3 minutes after creating database
2. Verify host name in Render PostgreSQL dashboard
3. Ensure API service in same region as database
4. Check firewall: All Render services can access each other

---

## 🚀 Phase 5: Post-Deployment (Optional)

### 5.1 Add Custom Domain

- [ ] Domain registered (e.g., autism-cdss.com)
- [ ] Go to **autism-cdss-frontend** → **Settings**
- [ ] Click: **Add Custom Domain**
- [ ] Follow DNS setup instructions
- [ ] Update **CORS_ORIGINS** in API:
  ```
  https://autism-cdss.yourdomain.com
  ```

### 5.2 Upgrade to Paid Plans (Recommended for Production)

| Service | Current | Recommended | Cost |
|---------|---------|-------------|------|
| Frontend | Static (Free) | Static (Free) | $0 |
| Backend | Free | Starter | $7/mo |
| Database | Free | Standard | $15/mo |

**Reason**: Free tiers have limitations:
- API sleeps after 15 mins inactivity
- Database limited to 1 GB storage, 10 connections

### 5.3 Set Up Monitoring

- [ ] Enable Render alerts: Service → **Alerts**
- [ ] Export database backup monthly
- [ ] Review logs weekly: Service → **Logs**

### 5.4 Update Environment Variables

- [ ] Generate new JWT_SECRET for each environment
- [ ] Use strong passwords for database
- [ ] Never commit `.env` files with secrets

---

## 📊 Architecture Summary

```
Internet (HTTPS)
    ↓
┌─────────────────────────────────────┐
│         Render Platform             │
├─────────────────────────────────────┤
│                                     │
│  Frontend              API Backend   │ Database
│  (Static Site)         (Python)      │ (PostgreSQL)
│  ───────────           ────────      │ ──────────
│  React App      →      FastAPI  →   │  Patients
│  dist/index    ←      + Models  ←   │  Assessments
│                                     │  Predictions
│  URL:              URL:              │
│  https://...       https://.../api   │
│  frontend          autism-cdss-api   │
│                                     │
└─────────────────────────────────────┘
```

---

## 📞 Support & Resources

| Resource | URL |
|----------|-----|
| Render Docs | https://render.com/docs |
| FastAPI Docs | https://fastapi.tiangolo.com |
| PostgreSQL | https://www.postgresql.org/docs/ |
| Python Secrets | https://docs.python.org/3/library/secrets.html |

---

## ✨ Success Criteria

✅ All items below checked = **Fully Deployed**

- [ ] API health endpoint returns `200 OK`
- [ ] Frontend loads without errors
- [ ] Can create user accounts
- [ ] Can add child assessments
- [ ] Predictions return correct risk tiers
- [ ] SHAP explanations display
- [ ] Data persists after page refresh
- [ ] CORS errors resolved
- [ ] Database backups working

---

**Last Updated**: 2026-02-21  
**Status**: Ready for Deployment
