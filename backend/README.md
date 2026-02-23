# Autism Risk CDSS - Backend API

FastAPI backend for the Clinical Decision Support System.

## Setup

### 1. Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Edit `.env` with your database credentials and settings.

### 2. Install Dependencies

```bash
pip install -r ../requirements.txt
```

### 3. Database Setup

Ensure PostgreSQL is running and create the database:

```bash
createdb autism_cdss
psql -d autism_cdss -f ../database/schema.sql
psql -d autism_cdss -f ../database/seed_data.sql
```

### 4. Train ML Models (if not already done)

```bash
cd ../ml
python train_models.py
```

## Running the Server

### Development Mode

```bash
python run.py
```

Or with uvicorn directly:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Documentation

Once the server is running, access:

- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc
- **Health Check**: http://localhost:8000/api/health

## API Endpoints

### Authentication
- `POST /api/auth/login` - User login (returns JWT token)
- `GET /api/auth/me` - Get current user info
- `POST /api/auth/users` - Create user (admin only)
- `GET /api/auth/users` - List users

### Children
- `POST /api/children` - Register new child
- `GET /api/children/{child_id}` - Get child details
- `GET /api/children` - List children (filtered by access)
- `PUT /api/children/{child_id}` - Update child
- `GET /api/children/{child_id}/assessments` - Get child's assessments

### Assessments
- `POST /api/assessments` - Submit new assessment
- `GET /api/assessments/{assessment_id}` - Get assessment details
- `GET /api/assessments` - List recent assessments

### Risk Predictions
- `POST /api/predictions/{assessment_id}/predict` - Generate risk prediction
- `GET /api/predictions/{prediction_id}` - Get prediction with SHAP

### Referrals
- `POST /api/referrals` - Create referral
- `PUT /api/referrals/{referral_id}` - Update referral
- `GET /api/referrals/{referral_id}` - Get referral details
- `GET /api/referrals/child/{child_id}` - Get child's referrals
- `GET /api/referrals` - List referrals

### Interventions
- `POST /api/interventions` - Create intervention
- `PUT /api/interventions/{intervention_id}` - Update intervention
- `GET /api/interventions/{intervention_id}` - Get intervention details
- `GET /api/interventions/child/{child_id}` - Get child's interventions
- `GET /api/interventions` - List interventions

## Authentication

All protected endpoints require JWT token in Authorization header:

```
Authorization: Bearer <your_jwt_token>
```

### Getting a Token

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "password123"
  }'
```

## Role-Based Access Control

6 roles with hierarchical permissions:

1. **system_admin** - Full system access
2. **state_admin** - State-level access
3. **district_officer** - District-level access
4. **supervisor** - Mandal-level access
5. **anganwadi_worker** - Center-level access
6. **parent** - Child-specific access only

## Project Structure

```
backend/
├── main.py              # FastAPI application
├── run.py               # Startup script
├── database.py          # Database connection
├── models.py            # SQLAlchemy ORM models
├── schemas.py           # Pydantic schemas
├── auth.py              # JWT authentication
├── rbac.py              # Role-based access control
├── middleware/
│   ├── audit.py         # Audit logging
│   └── disclaimer.py    # Clinical disclaimer
└── routers/
    ├── auth.py          # Authentication routes
    ├── children.py      # Children management
    ├── assessments.py   # Assessment submission
    ├── predictions.py   # Risk prediction (ML)
    ├── referrals.py     # Referral management
    └── interventions.py # Intervention tracking
```

## Testing with Seed Data

The seed data includes:

- **Users**: 14 users across all 6 roles
- **Children**: 8 sample children
- **Assessments**: 7 developmental assessments
- **Locations**: 3 states, 6 districts, 8 mandals, 9 centers

Test user credentials (from seed data):
```
Email: admin@cdss.gov.in
Password: admin123
```

## Audit Logging

All API requests are logged to the `audit_logs` table with:
- User ID
- Action (method + path)
- Request body (passwords redacted)
- Response status
- IP address & user agent
- Timestamp
