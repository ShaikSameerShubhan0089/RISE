# RISE - Machine Learning Training Pipeline
## Knowledge Transfer: Data to Deployment

This document explains how the RISE "Intelligence Engine" is trained, from raw clinical data to the final optimized models, with a detailed breakdown of the underlying code.

---

### 📋 1. Training Pipeline Overview

The training process is automated via the `ml/train_models.py` script. It follows a 6-step rigorous scientific workflow:

1.  **Data Loading**: Ingesting cleaned clinical assessment records.
2.  **Feature Engineering**: Transforming raw scores into clinical indices (SCII, NSI, etc.).
3.  **Data Partitioning**: Splitting data into Train, Validation, and Test sets.
4.  **Model Training (Model A)**: Training the Autism Risk Classifier (XGBoost).
5.  **Longitudinal Processing**: Preparing "Delta" features for escalation prediction.
6.  **Model Training (Model B)**: Training the Risk Escalation Predictor.

---

### 🧪 2. Phase 1: Feature Engineering (The Clinical Lens)
Before the model sees any data, we translate raw scores into meaningful clinical indices using the `FeatureEngineer` class in `ml/feature_engineering.py`.

#### **Code Breakdown: Clinical Indices**
```python
def compute_scii(self, row: pd.Series) -> float:
    # 1. We invert the DQ (100 - Score) because a LOWER DQ means HIGHER impairment
    lc_inverse = 100 - row['language_dq']
    se_inverse = 100 - row['socio_emotional_dq']
    behavior = row['behavior_score']
    
    # 2. Apply clinical weights: Socio-emotional (45%) and Language (40%) are primary
    scii = (
        self.scii_weights['lc_weight'] * lc_inverse +
        self.scii_weights['se_weight'] * se_inverse +
        self.scii_weights['behavior_weight'] * behavior
    )
    return round(scii, 2)
```

#### **Key Clinical Indices Calculated:**
- **SCII (Social Communication Impairment Index)**: Captures the core deficits of autism.
- **NSI (Neurodevelopmental Severity Index)**: Formula: `1 - (Composite_DQ / 100)`. Measures global delay burden.
- **DBS (Delay Burden Score)**: Formula: `Delayed_Domains / 5`. Quantifies affected functional areas.

---

### 🏗️ 3. Phase 2: The Training Logic (Model A)

The `AutismRiskClassifier` (Model A) uses **XGBoost** with specific clinical optimizations found in `ml/train_classifier.py`.

#### **Code Breakdown: Balancing & Safety**
```python
# 1. Apply SMOTE to create synthetic 'High Risk' cases so the model isn't biased
smote = SMOTE(random_state=42, k_neighbors=5)
X_train_balanced, y_train_balanced = smote.fit_resample(X_train, y_train)

# 2. Find the threshold that guarantees we catch at least 75% of cases (Recall)
precision, recall, thresholds = precision_recall_curve(y_val, y_val_pred_proba)
optimal_idx = np.where(recall >= 0.75)[0]
optimal_threshold = thresholds[optimal_idx[-1]]
```

#### **Addressing Class Imbalance**
In clinical datasets, "High Risk" cases are much rarer. We use **SMOTE** to generate synthetic data points and **`scale_pos_weight`** to tell the model to pay 4x more attention to High Risk mistakes.

---

### 📈 4. Phase 3: Risk Escalation (Model B)

Model B predicts if a child will **escalate** from Low to High Risk in the future, as defined in `ml/train_escalation.py`.

#### **Code Breakdown: Longitudinal Logic**
```python
def prepare_escalation_data(df, logger):
    # Scan children with at least 2 visits
    for child_id in child_ids:
        child_assessments = df[df['child_id'] == child_id].sort_values('assessment_cycle')
        if len(child_assessments) < 2: continue
        
        for i in range(len(child_assessments) - 1):
            current = child_assessments.iloc[i]
            next_assessment = child_assessments.iloc[i + 1]
            # LABEL: Did they move from Risk 0 (Low) to Risk 1 (High)?
            will_escalate = (current['autism_risk'] == 0) and (next_assessment['autism_risk'] == 1)
            row = current.to_dict()
            row['will_escalate'] = int(will_escalate)
            escalation_data.append(row)
```

---

### 📊 5. Evaluation & Quality Control

Every training run generates an evaluation report in `ml/evaluation/`. We track:

1.  **ROC-AUC**: Overall ability to distinguish between High and Low risk (Target > 0.88).
2.  **Sensitivity (Recall)**: How many of the *actual* High Risk children did we catch? (Target > 0.85).
3.  **Calibration Plot**: We use **Platt Scaling** (`CalibratedClassifierCV`) to ensure the predicted probability matches real-world frequency.

---

### 💾 6. Model Persistence (Deployment)

Once a model passes all quality checks, it is serialized to disk.

#### **Code Breakdown: Serialization**
```python
def save_model(self, path):
    model_artifacts = {
        'model': self.model,           # The XGBoost Engine
        'scaler': self.scaler,         # Data Normalizer
        'optimal_threshold': self.optimal_threshold, # Clinical Safety Guard
        'feature_names': self.feature_names
    }
    with open(path, 'wb') as f:
        pickle.dump(model_artifacts, f)
```

---

### 🛠️ Summary for the Technical Team
"The training process is a closed-loop system. We take raw data, apply clinical domain knowledge through **Feature Engineering**, train an **XGBoost** model with **Class Weighting**, and verify everything with **Calibration** and **SHAP explanations**. This ensures our AI is not just fast, but clinically sound."
