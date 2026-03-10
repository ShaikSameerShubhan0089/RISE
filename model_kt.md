# RISE Machine Learning Model Knowledge Transfer (KT)
## 🧠 Model Evolution: From Decision Trees to XGBoost

### **1. The Foundation: Decision Tree (The "Unit")**
A Decision Tree is the simplest building block. It makes decisions based on feature values by splitting data into branches.

**Logic**: "If Language DQ < 70 AND Social Impairment > 40, then High Risk."
**Pro**: Easy to interpret.
**Con**: Prone to **overfitting** (it "memorizes" the training data instead of learning patterns).

```text
       [ Is Language DQ < 70? ]
             /          \
          [YES]         [NO]
           /              \
[High Risk Tier]    [Moderate/Low Risk]
```

---

### **2. Random Forest (Parallel Ensemble - "Bagging")**
Random Forest builds **multiple** decision trees in **parallel**. Each tree sees a random subset of data and features.

- **Voting**: The final prediction is the "average" or "majority vote" of all trees.
- **Goal**: Reduce variance and overfitting.
- **Limitation**: It treats all trees as equals, even if some make poor predictions.

---

### **3. XGBoost (Sequential Ensemble - "Boosting")**
XGBoost is the "Extreme" version of Gradient Boosting. Unlike Random Forest, trees are built **one after another**.

#### **How it Works: Residual Learning**
Instead of just voting, each new tree focuses **only** on the mistakes (the **Residuals**) of the previous trees.

**Data Flow in XGBoost**:
1.  **Tree 1**: Makes an initial guess (e.g., 0.5 probability).
2.  **Calculate Residual**: If a child is "High Risk" (1.0) but Tree 1 predicted 0.6, the **Residual (Error)** is 0.4.
3.  **Tree 2**: This tree is built specifically to predict that **0.4 error**, NOT the original label.
4.  **Repeat**: This continues for hundreds of trees, with each tree "boosting" the accuracy of the overall ensemble by minimizing the remaining error.

```text
Input Data -> [ Tree 1 ] -> Residual_1 -> [ Tree 2 ] -> Residual_2 -> [ Tree 3 ] -> ... -> Final Prediction
                  ^                          ^                          ^
           (Initial Guess)           (Learns from T1)           (Learns from T2)
```

---

### **4. RISE End-to-End Data Flow Diagram**

This diagram shows how a child's assessment travels through our XGBoost architecture to become a clinical action.

```mermaid
graph TD
    A[Child Assessment Data] --> B{Feature Engineering}
    B --> B1[Clinical Indices: SCII, NSI, ERM]
    B --> B2[Developmental Deltas: ΔDQ, ΔBehavior]
    
    subgraph "XGBoost Prediction Engine"
    C[Base Prediction] --> D[Tree 1: Initial Risk Estimate]
    D --> E[Calculate Residual Error]
    E --> F[Tree 2: Target Error Reduction]
    F --> G[... 100+ Sequential Trees ...]
    G --> H[Raw Prediction Score]
    end
    
    H --> I[Platt Scaling Calibration]
    I --> J[Calibrated Probability (0-100%)]
    
    subgraph "Decision Support Layer"
    J --> K{Risk Stratification}
    K --> L1[Low Risk: Monitor]
    K --> L2[Mild Concern: Reassess]
    K --> L3[Moderate Risk: Referral Recommended]
    K --> L4[High Risk: Urgent Referral]
    
    J --> M[SHAP Explainer]
    M --> N[Top 5 Clinical Drivers]
    end
    
    L1 & L2 & L3 & L4 & N --> O[Final Clinician Dashboard]
```

---

### **5. Why XGBoost for RISE?**

1.  **Precision for Small Classes**: High-risk autism cases are fewer than low-risk cases. XGBoost's `scale_pos_weight` and sequential learning allow it to focus more on correctly identifying these critical high-risk cases.
2.  **Regularization (The "Brakes")**: We use L1 (Lasso) and L2 (Ridge) penalties to ensure the model doesn't get "too smart" for its own good, maintaining clinical stability even with noisy data.
3.  **Speed**: Despite building 300+ trees, XGBoost's parallel tree building algorithm (at the feature level) ensures near-instant predictions in the clinic.

---

### **6. Summary for the Client**
"We start with a single **Decision Tree** (like a clinical flowchart). We evolve to a **Random Forest** (a group of flowcharts). Finally, we use **XGBoost**, which is like a team of experts where each expert specializes in fixing the mistakes of the previous one. This 'Sequential Boosting' is what gives RISE its industry-leading **0.88+ ROC-AUC** accuracy."
