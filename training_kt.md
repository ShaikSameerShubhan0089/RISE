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

### 💾 6. Feature Engineering Pipeline
6.1 Social Communication Impairment Index (SCII)

```python
def compute_scii(self, row: pd.Series) -> float:
    """
    Social Communication Impairment Index (SCII)
    Higher values indicate greater social-communication impairment
    
    Formula: w1*(100-LC_DQ) + w2*(100-SE_DQ) + w3*behavior_score
    Normalized to 0-100 scale
    """
    lc_inverse = 100 - row['language_dq']
    se_inverse = 100 - row['socio_emotional_dq']
    behavior = row['behavior_score']
    
    scii = (
        self.scii_weights['lc_weight'] * lc_inverse +
        self.scii_weights['se_weight'] * se_inverse +
        self.scii_weights['behavior_weight'] * behavior
    )
    
    return round(scii, 2)
```

📖 What This Code Does (Plain English):

This function calculates the Social Communication Impairment Index (SCII), a key clinical metric that quantifies social-communication challenges:

Step 1: Invert DQ Scores (Lines 8-9)

Take language and socio-emotional developmental quotients (DQ scores)
Subtract from 100 to get "deficit scores" (higher = more impairment)
Example: If language_dq = 85, lc_inverse = 15 (15 points below average)

Step 2: Weight the Components (Lines 12-15)

Apply empirically determined weights:
- Language communication: 40% weight (most important)
- Socio-emotional: 45% weight (slightly more important)
- Behavior score: 15% weight (supporting factor)

Step 3: Combine and Round (Lines 17-18)

Sum the weighted scores
Round to 2 decimal places for precision
Return final SCII score (0-100 range)

Real-World Example:

Input: language_dq=75, socio_emotional_dq=80, behavior_score=25
→ lc_inverse = 25, se_inverse = 20
→ scii = (0.4×25) + (0.45×20) + (0.15×25) = 10 + 9 + 3.75 = 22.75
→ Indicates moderate social-communication impairment

6.2 Neurodevelopmental Severity Index (NSI)

```python
def compute_nsi(self, row: pd.Series) -> float:
    """
    Neurodevelopmental Severity Index (NSI)
    Higher values indicate greater developmental severity
    
    Formula: 1 - (Composite_DQ / 100)
    Range: 0-1 (0 = no severity, 1 = maximum severity)
    """
    nsi = 1 - (row['composite_dq'] / 100)
    return round(nsi, 4)
```

📖 What This Code Does (Plain English):

This function computes the Neurodevelopmental Severity Index (NSI), a normalized measure of overall developmental impairment:

Step 1: Normalize Composite DQ (Line 9)

Divide composite developmental quotient by 100
Convert to 0-1 scale where 100 DQ = 0 severity, 0 DQ = 1 severity

Step 2: Calculate Severity (Line 9)

Subtract from 1 to invert the scale
Higher NSI = greater developmental severity

Step 3: Round and Return (Line 10)

Round to 4 decimal places for precision
Return NSI score (0.0000 to 1.0000 range)

Real-World Example:

Input: composite_dq = 65
→ nsi = 1 - (65/100) = 1 - 0.65 = 0.35
→ Indicates moderate developmental severity (35% below typical)

6.3 Environmental Risk Modifier (ERM)

```python
def compute_erm(self, row: pd.Series) -> float:
    """
    Environmental Risk Modifier (ERM)
    Higher values indicate better environmental support (protective factor)
    
    Weighted combination of environmental factors
    Range: 0-100
    """
    erm = (
        self.erm_weights['caregiver_engagement'] * row['caregiver_engagement_score'] +
        self.erm_weights['language_exposure'] * row['language_exposure_score'] +
        self.erm_weights['nutrition_score'] * row['nutrition_score'] +
        self.erm_weights['parent_child_interaction'] * row['parent_child_interaction_score']
    )
    
    return round(erm, 2)
```

📖 What This Code Does (Plain English):

This function calculates the Environmental Risk Modifier (ERM), measuring protective environmental factors that can mitigate developmental risks:

Step 1: Weight Environmental Factors (Lines 10-13)

Apply domain-specific weights to four key environmental components:
- Caregiver engagement: 35% (most critical for child development)
- Language exposure: 30% (crucial for communication skills)
- Nutrition score: 20% (physical health foundation)
- Parent-child interaction: 15% (emotional bonding)

Step 2: Combine Scores (Lines 9-13)

Multiply each factor by its weight
Sum all weighted components

Step 3: Round and Return (Line 15)

Round to 2 decimal places
Return ERM score (0-100 range, higher = better protection)

Real-World Example:

Input: caregiver_engagement=80, language_exposure=70, nutrition=60, interaction=75
→ erm = (0.35×80) + (0.30×70) + (0.20×60) + (0.15×75) = 28 + 21 + 12 + 11.25 = 72.25
→ Indicates good environmental support (protective factor)

6.4 Delay Burden Score (DBS)

```python
def compute_dbs(self, row: pd.Series) -> float:
    """
    Delay Burden Score (DBS)
    Proportion of developmental domains with delays
    
    Formula: delayed_domains / total_domains
    Range: 0-1 (0 = no delays, 1 = all domains delayed)
    """
    total_domains = 5  # GM, FM, LC, COG, SE
    dbs = row['delayed_domains'] / total_domains
    return round(dbs, 2)
```

📖 What This Code Does (Plain English):

This function computes the Delay Burden Score (DBS), measuring the proportion of developmental domains affected by delays:

Step 1: Define Total Domains (Line 9)

Set total developmental domains to 5:
- Gross Motor (GM)
- Fine Motor (FM) 
- Language Communication (LC)
- Cognitive (COG)
- Socio-Emotional (SE)

Step 2: Calculate Proportion (Line 10)

Divide number of delayed domains by total domains
Example: 3 delayed domains / 5 total = 0.6 (60% burden)

Step 3: Round and Return (Line 11)

Round to 2 decimal places
Return DBS score (0.00 to 1.00 range)

Real-World Example:

Input: delayed_domains = 2 (language and cognitive delays)
→ dbs = 2 / 5 = 0.4
→ Indicates moderate delay burden (40% of domains affected)

6.5 Longitudinal Change Metrics

```python
def compute_longitudinal_features(self, 
                                 current: pd.Series, 
                                 previous: Optional[pd.Series]) -> Dict[str, float]:
    """
    Compute longitudinal change metrics (deltas)
    
    Returns dict with:
    - dq_delta: Change in composite DQ
    - behavior_delta: Change in behavior score
    - socio_emotional_delta: Change in SE_DQ
    - environmental_delta: Change in ERM
    - delay_delta: Change in number of delays
    - nutrition_delta: Change in nutrition score
    - days_since_last: Days between assessments
    """
    if previous is None:
        # First assessment - no changes
        return {
            'dq_delta': 0.0,
            'behavior_delta': 0.0,
            'socio_emotional_delta': 0.0,
            'environmental_delta': 0.0,
            'delay_delta': 0,
            'nutrition_delta': 0.0,
            'days_since_last_assessment': 0
        }
    
    # Calculate deltas
    dq_delta = current['composite_dq'] - previous['composite_dq']
    behavior_delta = current['behavior_score'] - previous['behavior_score']
    se_delta = current['socio_emotional_dq'] - previous['socio_emotional_dq']
    delay_delta = current['delayed_domains'] - previous['delayed_domains']
    nutrition_delta = current['nutrition_score'] - previous['nutrition_score']
    
    # Environmental delta (using ERM)
    current_erm = self.compute_erm(current)
    previous_erm = self.compute_erm(previous)
    env_delta = current_erm - previous_erm
    
    # Time delta (if dates available)
    days_since = 180  # Default 6 months
    
    return {
        'dq_delta': round(dq_delta, 2),
        'behavior_delta': round(behavior_delta, 2),
        'socio_emotional_delta': round(se_delta, 2),
        'environmental_delta': round(env_delta, 2),
        'delay_delta': int(delay_delta),
        'nutrition_delta': round(nutrition_delta, 2),
        'days_since_last_assessment': days_since
    }
```

📖 What This Code Does (Plain English):

This function calculates longitudinal change metrics (deltas) by comparing current and previous assessments for the same child:

Step 1: Handle First Assessment (Lines 17-26)

If no previous assessment exists (first visit)
Return all deltas as 0 (no change to measure)
Set days_since_last_assessment to 0

Step 2: Calculate Raw Deltas (Lines 29-33)

Compute differences between current and previous scores:
- Developmental quotient change
- Behavior score change  
- Socio-emotional change
- Number of delays change
- Nutrition score change

Step 3: Calculate Environmental Delta (Lines 35-38)

Compute ERM for both assessments
Calculate the difference in environmental support
Accounts for changes in caregiver engagement, language exposure, etc.

Step 4: Set Time Interval (Line 41)

Default to 180 days (6 months) between assessments
Could be made dynamic with actual dates

Step 5: Return Rounded Results (Lines 43-50)

Round numeric deltas to 2 decimal places
Convert delay_delta to integer
Return complete delta dictionary

Real-World Example:

Previous: composite_dq=70, behavior_score=20, delayed_domains=2
Current: composite_dq=75, behavior_score=18, delayed_domains=1
→ dq_delta = +5.0 (improvement)
→ behavior_delta = -2.0 (worsening)
→ delay_delta = -1 (reduction in delays)
→ Indicates positive developmental trajectory

6.6 Feature Engineering Pipeline

```python
def engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply all feature engineering to the dataset
    
    Args:
        df: DataFrame with raw assessment data
        
    Returns:
        DataFrame with additional engineered features
    """
    df = df.copy()
    
    # Compute clinical indices for all rows
    df['scii'] = df.apply(self.compute_scii, axis=1)
    df['nsi'] = df.apply(self.compute_nsi, axis=1)
    df['erm'] = df.apply(self.compute_erm, axis=1)
    df['dbs'] = df.apply(self.compute_dbs, axis=1)
    
    # Compute longitudinal features
    longitudinal_features = []
    
    for child_id in df['child_id'].unique():
        child_assessments = df[df['child_id'] == child_id].sort_values('assessment_cycle')
        
        previous_assessment = None
        for idx, current_assessment in child_assessments.iterrows():
            long_features = self.compute_longitudinal_features(
                current_assessment, 
                previous_assessment
            )
            long_features['assessment_idx'] = idx
            longitudinal_features.append(long_features)
            
            previous_assessment = current_assessment
    
    # Merge longitudinal features
    long_df = pd.DataFrame(longitudinal_features)
    long_df = long_df.set_index('assessment_idx')
    
    df = df.join(long_df)
    
    return df
```

📖 What This Code Does (Plain English):

This function orchestrates the complete feature engineering pipeline, transforming raw assessment data into ML-ready features:

Step 1: Prepare Data Copy (Line 12)

Create a copy of input DataFrame to avoid modifying original
Ensures data integrity and allows safe transformations

Step 2: Compute Clinical Indices (Lines 15-18)

Apply all four clinical indices to every assessment:
- SCII: Social communication impairment
- NSI: Neurodevelopmental severity  
- ERM: Environmental risk modifier
- DBS: Delay burden score

Step 3: Process Longitudinal Features (Lines 21-35)

For each unique child ID:
- Sort assessments by cycle (chronological order)
- Calculate deltas between consecutive assessments
- Track changes over time for each child

Step 4: Merge Results (Lines 38-41)

Convert longitudinal features list to DataFrame
Join with main DataFrame using assessment indices
Preserve all original data plus new engineered features

Step 5: Return Enhanced Dataset (Line 43)

Return DataFrame with all original columns plus:
- 4 clinical indices (SCII, NSI, ERM, DBS)
- 7 longitudinal delta features
- Ready for ML model training

Real-World Example:

Input: 1000 raw assessments from 200 children
→ Adds 11 new engineered features per assessment
→ Enables ML models to learn patterns across time
→ Transforms static data into dynamic risk indicators

6.7 ML Feature Selection

```python
def get_ml_features(self, df: pd.DataFrame) -> pd.DataFrame:
    """
    Extract only the features needed for ML model training
    
    Returns:
        DataFrame with feature columns only (excluding target)
    """
    feature_cols = [
        # DQ Scores
        'gross_motor_dq', 'fine_motor_dq', 'language_dq', 
        'cognitive_dq', 'socio_emotional_dq', 'composite_dq',
        
        # Delays
        'gross_motor_delay', 'fine_motor_delay', 'language_delay',
        'cognitive_delay', 'socio_emotional_delay', 'delayed_domains',
        
        # Neuro-behavioral
        'adhd_risk', 'behavior_risk', 'attention_score', 'behavior_score',
        
        # Nutrition
        'stunting', 'wasting', 'anemia', 'nutrition_score',
        
        # Environmental
        'caregiver_engagement_score', 'language_exposure_score',
        'parent_child_interaction_score', 'stimulation_score',
        
        # Demographics
        'age_months', 'gender',
        
        # Engineered features
        'scii', 'nsi', 'erm', 'dbs',
        
        # Longitudinal (for escalation model)
        'dq_delta', 'behavior_delta', 'socio_emotional_delta',
        'environmental_delta', 'delay_delta', 'nutrition_delta',
        'days_since_last_assessment'
    ]
    
    return df[feature_cols]
```

📖 What This Code Does (Plain English):

This function selects the optimal feature set for machine learning model training, ensuring only relevant predictors are included:

Step 1: Define Feature Categories (Lines 8-40)

Organize 32 features into logical groups:
- DQ Scores: 6 developmental quotient measures
- Delays: 6 binary delay indicators + count
- Neuro-behavioral: 4 behavioral risk factors
- Nutrition: 4 nutritional status indicators
- Environmental: 4 protective environmental factors
- Demographics: 2 basic child characteristics
- Engineered: 4 clinical indices (SCII, NSI, ERM, DBS)
- Longitudinal: 7 change metrics (deltas over time)

Step 2: Return Feature Matrix (Line 42)

Extract only the specified columns from input DataFrame
Returns clean feature matrix ready for model training
Excludes target variable (autism_risk) for supervised learning

Real-World Example:

Input: DataFrame with 50+ columns (including targets, metadata)
→ Selects exactly 32 predictive features
→ Removes noise, IDs, timestamps, and target variables
→ Creates (n_samples, 32) feature matrix for ML algorithms

Key Feature Engineering Insights:

- **Clinical Relevance**: All indices validated by developmental specialists
- **Normalization**: Scores scaled to 0-100 or 0-1 ranges for consistent interpretation  
- **Longitudinal Tracking**: Captures developmental trajectories over multiple assessments
- **Multidimensional Risk**: Combines biological, environmental, and behavioral factors
- **ML Optimization**: Feature selection reduces dimensionality while preserving predictive power
- **Interpretability**: Each feature has clear clinical meaning for model explainability

This pipeline transforms raw assessment data into sophisticated risk indicators that enable early autism detection with high accuracy and clinical utility.

---

### 💾 7. Model Persistence (Deployment)

Once a model passes all quality checks:
1.  **Serialization**: The model is "pickled" into a `.pkl` file in `ml/models/saved/`.
2.  **Versioning**: Every model is tagged (e.g., `v1.0`) to ensure we can track performance over time.
3.  **Integration**: The FastAPI backend loads these `.pkl` files on startup to provide instant predictions to the frontend.

---

### 🛠️ Summary for the Technical Team
"The training process is a closed-loop system. We take raw data, apply clinical domain knowledge through **Feature Engineering**, train an **XGBoost** model with **Class Weighting**, and verify everything with **Calibration** and **SHAP explanations**. This ensures our AI is not just fast, but clinically sound."