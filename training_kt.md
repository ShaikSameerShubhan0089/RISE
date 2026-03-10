# RISE - Machine Learning Training Pipeline
## Knowledge Transfer: Data to Deployment

This document explains how the RISE "Intelligence Engine" is trained, from raw clinical data to the final optimized models.

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

#### **Key Clinical Indices Calculated:**
- **SCII (Social Communication Impairment Index)**: 
    - *Formula*: $0.4 \cdot (100 - Language\_DQ) + 0.45 \cdot (100 - SE\_DQ) + 0.15 \cdot Behavior\_Score$
    - *Purpose*: Captures the core deficits of autism.
- **NSI (Neurodevelopmental Severity Index)**:
    - *Formula*: $1 - (Composite\_DQ / 100)$
    - *Purpose*: Measures the global delay burden.
- **DBS (Delay Burden Score)**:
    - *Formula*: $Delayed\_Domains / 5$
    - *Purpose*: Quantifies how many functional areas are affected.

#### **Longitudinal Deltas (Growth Tracking):**
For children with multiple assessments, we calculate **Deltas**:
- `dq_delta`: Did the overall score improve or decline?
- `behavior_delta`: Is behavior becoming more challenging?
- `delay_delta`: Are new delays appearing over time?

---

### 🏗️ 3. Phase 2: The Training Logic (Model A)

The `AutismRiskClassifier` (Model A) uses **XGBoost** with specific clinical optimizations.

#### **Data Splitting Strategy**
We use a triple-split to ensure the model is truly accurate and hasn't just "memorized" the data:
1.  **Training Set (70%)**: Used to teach the model patterns.
2.  **Validation Set (15%)**: Used to tune the "Learning Rate" and "Tree Depth" during training.
3.  **Test Set (15%)**: **Hidden** from the model during training. This is the final exam used to generate the 0.88+ accuracy reports.

#### **Addressing Class Imbalance**
In clinical datasets, "High Risk" cases are much rarer than "Low Risk" cases. To prevent the model from ignoring the rare cases, we use:
- **`scale_pos_weight`**: We tell the model to pay ~4x more attention to a High Risk mistake than a Low Risk mistake.

---

### 📈 4. Phase 3: Risk Escalation (Model B)

Model B predicts if a child will **escalate** to High Risk in the future.

- **Data Preparation**: The system looks at "Cycle 1" and "Cycle 2."
- **Labeling**: If a child was Low Risk in Cycle 1 but became High Risk in Cycle 2, they are marked as an "Escalation Case."
- **Predictive Power**: By learning the patterns that lead to escalation (e.g., a dropping Language DQ), the model can warn clinicians *before* the child reaches the high-risk tier.

---

### 📊 5. Evaluation & Quality Control

Every training run generates an evaluation report in `ml/evaluation/`. We track:

1.  **ROC-AUC**: The "Gold Standard" of accuracy. Our target is > 0.88.
2.  **Sensitivity (Recall)**: How many of the *actual* High Risk children did we catch? (Target > 0.85).
3.  **Calibration Plot**: Does a "70% risk" prediction actually mean 7 out of 10 such children have autism? We use **Platt Scaling** to ensure the answer is Yes.

---

### 💾 6. Model Persistence (Deployment)

Once a model passes all quality checks:
1.  **Serialization**: The model is "pickled" into a `.pkl` file in `ml/models/saved/`.
2.  **Versioning**: Every model is tagged (e.g., `v1.0`) to ensure we can track performance over time.
3.  **Integration**: The FastAPI backend loads these `.pkl` files on startup to provide instant predictions to the frontend.

---

### 🛠️ Summary for the Technical Team
"The training process is a closed-loop system. We take raw data, apply clinical domain knowledge through **Feature Engineering**, train an **XGBoost** model with **Class Weighting**, and verify everything with **Calibration** and **SHAP explanations**. This ensures our AI is not just fast, but clinically sound."