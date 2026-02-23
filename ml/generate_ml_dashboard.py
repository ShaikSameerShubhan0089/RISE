import os
import json
from datetime import datetime

def generate_dashboard():
    dashboard_path = 'ml/evaluation/ML_DASHBOARD.md'
    classifier_dir = 'ml/evaluation/classifier'
    escalation_dir = 'ml/evaluation/escalation'
    
    try:
        with open(dashboard_path, 'w', encoding='utf-8') as f:
            f.write("# 🧪 Professional ML Assessment Dashboard\n")
            f.write(f"*Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n")
            
            # --- MODEL A ---
            f.write("## 🟢 Model A: Autism Risk Classifier\n")
            
            f.write("### 🏥 Clinical Guideline Preview (New)\n")
            f.write("> [!NOTE]\n")
            f.write("> Model A now generates structured intervention pathways based on clinical markers. \n\n")
            f.write("| Category | Objective | Sample Daily Step | Parent Guide |\n")
            f.write("| :--- | :--- | :--- | :--- |\n")
            f.write("| **Speech Therapy** | Improve verbal communication | Spend 10 mins naming household objects | Speak slowly and clearly |\n")
            f.write("| **Occupational Therapy** | Develop fine motor skills | Practice stacking blocks or nesting cups | Focus on grip strength |\n")
            f.write("| **Behavioral Therapy** | Enhance social engagement | Practice eye contact during play | Consistency is key |\n\n")
            
            meta_path = 'ml/models/saved/classifier/training_meta.json'
            if os.path.exists(meta_path):
                with open(meta_path, 'r') as m:
                    meta = json.load(m)
                f.write("### 📈 Training Progress\n")
                f.write(f"- **Timestamp**: {meta.get('timestamp', 'N/A')}\n")
                f.write(f"- **Training Records**: {meta.get('train_size', 'N/A')}\n")
                if os.path.exists(os.path.join(classifier_dir, 'learning_curves.png')):
                    f.write("![Learning Curves](classifier/learning_curves.png)\n\n")
            
            report_path = os.path.join(classifier_dir, 'test_report.json')
            if os.path.exists(report_path):
                with open(report_path, 'r') as r:
                    report = json.load(r)
                f.write("### 📊 Test Evaluation (Unseen Data)\n")
                metrics = report.get('metrics', {})
                f.write(f"- **ROC-AUC**: {metrics.get('roc_auc', 0):.4f}\n")
                f.write(f"- **Sensitivity (Recall)**: {metrics.get('sensitivity', 0):.4f}\n")
                f.write(f"- **Specificity**: {metrics.get('specificity', 0):.4f}\n")
                f.write(f"- **F1-Score**: {metrics.get('f1_score', 0):.4f}\n\n")
                if os.path.exists(os.path.join(classifier_dir, 'evaluation_dashboard.png')):
                    f.write("![Evaluation Dashboard](classifier/evaluation_dashboard.png)\n\n")
                if os.path.exists(os.path.join(classifier_dir, 'shap_summary.png')):
                    f.write("### 🔍 Model Interpretability (Global SHAP)\n")
                    f.write("![SHAP Summary](classifier/shap_summary.png)\n\n")
            
            # --- MODEL B ---
            f.write("--- \n")
            f.write("## 🟠 Model B: Risk Escalation Predictor\n")
            
            if not os.path.exists(os.path.join(escalation_dir, 'evaluation_dashboard.png')):
                f.write("> [!WARNING]\n")
                f.write("> Model B training is currently in **Architecture Ready** status. \n")
                f.write("> Longitudinal data (multiple visits per child) is required to train the escalation predictor.\n")
            else:
                f.write("### 📊 Escalation Prediction Metrics\n")
                f.write("![Evaluation Dashboard](escalation/evaluation_dashboard.png)\n")
                f.write("![SHAP Summary](escalation/shap_summary.png)\n")
        
        print(f"SUCCESS: ML Dashboard generated at {dashboard_path}")
    except Exception as e:
        import traceback
        print(f"ERROR: Failed to generate dashboard: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    generate_dashboard()
