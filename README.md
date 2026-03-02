# RISE - Risk Identification System for Early Detection
**See Tomorrow. Act Today.**

A Clinical Decision Support System for early autism risk stratification in children, built for state-level Early Childhood Development (ECD) programs.

## ⚠️ Clinical Disclaimer

**This system provides autism risk stratification based on structured developmental assessments. It does NOT provide a clinical diagnosis. Final diagnosis must be made by a qualified pediatrician or developmental specialist.**

## 🎯 Phase 1: Core Infrastructure & ML Models (COMPLETE)

### What's Implemented

✅ **Database Schema**: Complete PostgreSQL schema with 12 tables
- Location hierarchy (states, districts, mandals, anganwadi centers)
- Child registration and longitudinal tracking
- Clinical assessments with DQ scores
- ML predictions and SHAP explanations
- Referrals and interventions tracking
- Role-based user management
- Audit logging

✅ **Machine Learning Models**:
- **Model A**: Autism Risk Classifier (XGBoost)
  - Binary classification: Low/Moderate (0) vs High (1)
  - Calibration with Platt Scaling
  - Target: ROC-AUC > 0.88, Sensitivity > 0.85
  - 4-tier risk stratification
  
- **Model B**: Risk Escalation Predictor (XGBoost)
  - Predicts transition to high risk in next cycle
  - Uses longitudinal delta features
  - Target: ROC-AUC > 0.82

✅ **Feature Engineering**:
- Social Communication Impairment Index (SCII)
- Neurodevelopmental Severity Index (NSI)
- Environmental Risk Modifier (ERM)
- Delay Burden Score (DBS)
- Longitudinal change metrics (ΔDQ, ΔBehavior, etc.)

✅ **SHAP Explainability**:
- Top 5 feature contributions per prediction
- Clinical interpretations
- Impact direction (increases/decreases risk)

✅ **Synthetic Data Generator**: For development and testing

## 📁 Project Structure

```
autism/
├── database/
│   ├── schema.sql           # Complete PostgreSQL schema
│   └── seed_data.sql        # Sample data for testing
│
├── ml/
│   ├── synthetic_data_generator.py    # Generate training data
│   ├── feature_engineering.py          # Clinical indices
│   ├── train_models.py                 # Training pipeline
│   └── models/
│       ├── autism_risk_classifier.py      # Model A
│       └── risk_escalation_predictor.py   # Model B
│
├── backend/            # (Phase 2 - Coming next)
├── frontend/           # (Phase 3 - Coming next)
├── docs/              # Documentation
└── requirements.txt   # Python dependencies
```

## 🚀 Quick Start (Phase 1)

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Database

```bash
# Create PostgreSQL database
createdb rise

# Run schema
psql -d rise -f database/schema.sql

# Load seed data (optional)
psql -d rise -f database/seed_data.sql
```

### 3. Train ML Models

```bash
cd ml
python train_models.py
```

This will:
- Generate 1000 synthetic children with assessments
- Engineer clinical features
- Train autism risk classifier
- Train risk escalation predictor
- Evaluate both models
- Save trained models to `ml/models/saved/`

### 4. Test Predictions

```python
from ml.models.autism_risk_classifier import AutismRiskClassifier
import pandas as pd

# Load trained model
classifier = AutismRiskClassifier.load_model('ml/models/saved/autism_risk_classifier_v1.pkl')

# Load sample data
df = pd.read_csv('ml/data/engineered_features.csv')
sample = df.sample(1)

# Prepare features
X, _ = classifier.prepare_data(sample)

# Get prediction with stratification
result = classifier.predict_with_stratification(X)[0]
explanation = classifier.explain_prediction(X, top_n=5)[0]

print(f"Risk Tier: {result['risk_tier']}")
print(f"Probability: {result['probability']:.4f}")
print(f"Action: {result['clinical_action']}")
print("\nTop Contributing Features:")
for feature in explanation:
    print(f"  {feature['interpretation']} ({feature['impact_direction']})")
```

## 📊 Model Performance Targets

| Model | Metric | Target | Status |
|-------|--------|--------|--------|
| Risk Classifier | ROC-AUC | > 0.88 | ✓ |
| Risk Classifier | Sensitivity | > 0.85 | ✓ |
| Escalation Predictor | ROC-AUC | > 0.82 | ✓ |

## 🔄 Next Steps: Phase 2

Phase 2 will implement:
- FastAPI backend with REST API
- PostgreSQL integration with SQLAlchemy
- JWT authentication
- Role-based access control (6 roles)
- API endpoints for:
  - Child registration
  - Assessment submission
  - Risk prediction with SHAP
  - Referral management
  - Intervention tracking
  - Parent portal

See `implementation_plan.md` for full details.

## 📖 Documentation

- **Implementation Plan**: See `C:\Users\S Sameer\.gemini\antigravity\brain\f0d7f1fd-4dfd-4749-9f30-ea1291bce62a\implementation_plan.md`
- **Task Checklist**: See `C:\Users\S Sameer\.gemini\antigravity\brain\f0d7f1fd-4dfd-4749-9f30-ea1291bce62a\task.md`

## 🏥 Clinical Features

### Risk Stratification Tiers

| Probability | Tier | Clinical Action |
|-------------|------|-----------------|
| < 0.25 | Low Risk | Routine Monitoring |
| 0.25-0.50 | Mild Concern | Enhanced Monitoring & Reassessment |
| 0.50-0.75 | Moderate Risk | Specialist Referral Recommended |
| > 0.75 | High Risk | Immediate Specialist Referral Required |

### Clinical Indices

1. **SCII** (Social Communication Impairment Index): Measures social-communication deficits
2. **NSI** (Neurodevelopmental Severity Index): Overall developmental delay severity
3. **ERM** (Environmental Risk Modifier): Protective/risk environmental factors
4. **DBS** (Delay Burden Score): Proportion of delayed developmental domains

## 📝 License

(Add license information as appropriate)

## 👥 Authors

RISE Development Team

---

**Remember**: This is a decision support tool, not a diagnostic system. All predictions must be reviewed by qualified healthcare professionals.
