# RISE - Machine Learning Training: Deep Dive Technical Manual
## Complete Code & Logic Breakdown for Developers

This document provides an exhaustive explanation of the entire RISE training codebase. It is designed for engineers who need to maintain, update, or audit the system's "Intelligence Engine."

---

### 📂 1. `ml/train_models.py` (The Orchestrator)
This is the main entry point for Phase 1. It automates the training of both Model A and Model B in one go.

- **`train_model_pipeline()`**: 
    - **Directory Setup**: Automatically creates folders for data, models, and evaluation to ensure a clean workspace.
    - **Sequential Logic**: It ensures that `Model A` (Risk Classifier) is trained first, as its outputs (Risk Status) are often required to label data for `Model B` (Escalation Predictor).
- **`prepare_escalation_data()`**:
    - This is a critical helper function that iterates through every child's history. It looks for "State Transitions"—specifically children who move from a "Low Risk" (0) state to a "High Risk" (1) state.

---

### 📂 2. `ml/train_classifier.py` (Advanced Training for Model A)
This script handles the "heavy lifting" for the primary Risk Classifier. It includes advanced data science techniques to ensure clinical safety.

- **SMOTE (Synthetic Minority Over-sampling Technique)**:
    - **The Problem**: High-risk cases are rare. Without SMOTE, the model might "ignore" them to achieve easy accuracy.
    - **The Solution**: SMOTE creates "synthetic" high-risk children by interpolating between existing ones, ensuring the model has enough data to learn the markers of autism.
- **Threshold Optimization**:
    - **Code Logic**: The script doesn't just use a standard 0.5 threshold. It scans the `precision_recall_curve` to find a threshold that guarantees at least **75% Recall** (Sensitivity).
    - **Clinical Goal**: We would rather have a "False Alarm" (Higher Precision cost) than miss a child with autism (High Recall priority).
- **Learning Curves**: Generates plots for `logloss`, `auc`, and `error` to detect if the model is learning too fast or stalling.

---

### 📂 3. `ml/train_escalation.py` (Predictive Warning System)
Focuses specifically on the longitudinal aspect of the project.

- **Longitudinal Extracter**: Scans for "Patterns of Decline." It focuses on children with at least 2 cycles of data.
- **Validation Constraints**: If the dataset doesn't have enough longitudinal data, the script is designed to "Fail Gracefully"—logging a warning but keeping the system stable.

---

### 📂 4. `ml/feature_engineering.py` (The Domain Logic)
This is where clinical expertise is converted into math.

- **`FeatureEngineer` Class**:
    - **SCII (Social Index)**: Uses weighted logic where Socio-Emotional markers (45%) and Language (40%) are given high priority.
    - **NSI (Severity Index)**: Inverts the Composite DQ so that a **higher** NSI means a **worse** clinical state ($1 - DQ/100$).
    - **Longitudinal Deltas**: Calculates the "Speed of Change." A child whose DQ drops by 10 points in 6 months is flagged much more aggressively than a child whose DQ is stable.

---

### 📂 5. `ml/models/autism_risk_classifier.py` (The Classifier Brain)
The definition of our XGBoost wrapper.

- **`_calibrate_model`**: Uses **Platt Scaling** (`CalibratedClassifierCV`). This ensures that if the model says "80% Risk," it actually means the child has an 8 in 10 chance based on the training data.
- **`explain_prediction`**: The bridge to **SHAP**. It takes the raw math from the trees and converts it into clinical interpretations (e.g., "Language DQ is 15% below threshold").

---

### 📂 6. `ml/models/risk_escalation_predictor.py` (The Escalation Brain)
Similar to the classifier, but optimized for "Trend Analysis."

- **Feature Selection**: It ignores "Static" features (like Gender) and focuses on "Dynamic" features (like `dq_delta` and `behavior_delta`).
- **Clinical Action Mapping**: While the Classifier maps to "Risk Tiers," this model maps to "Urgency of Follow-up."

---

### 🛠️ The RISE Training "Golden Rules"
1.  **Always use `stratify=y`**: When splitting data, we must ensure the percentage of high-risk cases is the same in both Train and Test sets.
2.  **Pickle with Metadata**: We don't just save the model; we save the **`scaler`** (to normalize new data) and the **`feature_names`** to ensure the API never gets confused.
3.  **Audit Logs**: Every training run generates a `training.log` file. If accuracy drops, developers can look back to see if the data distribution changed.

**Summary**: The RISE training suite is built for **Clinical Integrity**. It uses advanced balancing (SMOTE), safety-first thresholding (75% Recall), and explainable AI (SHAP) to ensure that every prediction is both accurate and justifiable to a specialist.
