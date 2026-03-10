# RISE - Deep-Dive Line-by-Line Code Documentation
## Technical Breakdown: ML Infrastructure

This guide provides a granular, line-by-line explanation of the logic within the feature engineering and training scripts.

---

### 📂 1. `ml/feature_engineering.py` (The Clinical Translator)

This class is responsible for converting raw clinical assessments into predictive indices.

#### **`class FeatureEngineer`**
- **Lines 24-36 (`__init__`)**: We define the mathematical "importance" (weights) for our indices. 
    - **SCII**: Language (40%) and Socio-Emotional (45%) are the primary drivers of autism detection.
    - **ERM**: Caregiver engagement (35%) and Language exposure (30%) are the top environmental protective factors.
- **Lines 38-56 (`compute_scii`)**: 
    - `lc_inverse = 100 - row['language_dq']`: We "flip" the score. A high DQ is good, but a high *impairment* (the inverse) is what predicts risk.
    - The final `scii` sum is the weighted combination of these clinical impairments.
- **Lines 58-67 (`compute_nsi`)**: 
    - `1 - (row['composite_dq'] / 100)`: If a child has a DQ of 70, their NSI is 0.30 (Moderate severity). If DQ is 30, NSI is 0.70 (High severity).
- **Lines 86-96 (`compute_dbs`)**: 
    - `row['delayed_domains'] / 5`: There are 5 total domains (Motor, Language, etc.). If 3 are delayed, the "Burden" is 0.60.
- **Lines 98-148 (`compute_longitudinal_features`)**: 
    - **`if previous is None`**: For a child's first visit, we set all changes (Deltas) to 0.0.
    - **Deltas**: We subtract the previous score from the current score. A negative DQ delta means the child is regressing.
- **Lines 150-191 (`engineer_features`)**: 
    - `df.apply(..., axis=1)`: Calculates indices for every row in the database.
    - **Longitudinal Loop**: We group data by `child_id` and sort by `assessment_cycle`. We then step through each cycle, comparing the "Current" assessment to the "Previous" one to build the child's developmental trajectory.

---

### 📂 2. `ml/train_classifier.py` (Model A Training Logic)

#### **`main()` Function**
- **Lines 67-75**: Initializes paths for model storage (`saved/classifier`) and logging.
- **Lines 86-89**: Calls the `FeatureEngineer` to prepare the clinical data.
- **Lines 92-93**: `classifier.prepare_data(df_engineered)`: Converts text gender to 0/1 and ensures all clinical flags are integers for the XGBoost engine.
- **Lines 95-101**: 
    - **1st Split**: Separates 20% of data for the "Final Exam" (Test set).
    - **2nd Split**: Separates 15% of the remainder for "Validation" to prevent the model from over-learning (Overfitting).
- **Lines 105-113 (SMOTE)**: 
    - `SMOTE(random_state=42)`: Because we have fewer "High Risk" cases, SMOTE creates "synthetic" examples by finding similar children and interpolating new data points. This balances the "scales" of the model.
- **Lines 116-130 (Training)**: 
    - Checks for `xgb_optuna_best.json`. If you've run a hyperparameter search, it loads those specific "best" settings.
    - `classifier.train(...)`: Starts the boosting process.
- **Lines 132-147 (Thresholding)**: 
    - The model outputs a probability (0.0 to 1.0).
    - **Logic**: We look for the threshold where **Recall (Sensitivity) is at least 0.75**. If at 0.42 probability we catch 75% of autism cases, we set 0.42 as our "Clinical Threshold."
- **Lines 185-187**: Saves the `autism_risk_classifier_v1.pkl` containing the trained "Brain," the data scaler, and the optimized threshold.

---

### 📂 3. `ml/train_escalation.py` (Model B Training Logic)

#### **Core Functions**
- **Lines 69-87 (`prepare_escalation_data`)**: 
    - **Logic**: It identifies "Escalation Events."
    - `(current['autism_risk'] == 0) and (next_assessment['autism_risk'] == 1)`: If a child was Low Risk but moved to High Risk in the next visit, the label is set to **1** (Escalation). All others are **0**.
- **Lines 89-162 (`main`)**:
    - **Constraint Check (Lines 116-119)**: If the dataset has no children with multiple visits, the code stops here with a warning. You cannot predict "Change" without at least two data points.
    - **Training (Line 137)**: Trains a separate XGBoost model that focuses specifically on **Deltas** (Speed of change) rather than static scores.
- **Lines 143-152 (Metadata)**: Saves a `training_meta.json` which recording the **Final Metrics** (ROC-AUC, Error) so administrators can verify model health without opening the code.

---

### 🛠️ Global Execution Logic Summary
1.  **Scaling**: All data is normalized to a Z-score (mean 0, variance 1) before hitting the model.
2.  **Early Stopping**: Both scripts monitor the "Validation" set. If error stops dropping for 10 rounds, the training stops to save the most accurate version.
3.  **Auditability**: Every step is logged with timestamps and record counts in `training.log`.
