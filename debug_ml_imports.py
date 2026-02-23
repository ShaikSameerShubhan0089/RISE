import sys
import os
from pathlib import Path

# Set project root
project_root = Path(os.getcwd())
sys.path.insert(0, str(project_root))

print(f"Project root: {project_root}")
print(f"CWD: {os.getcwd()}")
print(f"sys.path: {sys.path[:3]}")

try:
    print("Testing import ml...")
    import ml
    print("✓ import ml successful")
    
    print("Testing from ml.models.autism_risk_classifier import AutismRiskClassifier...")
    from ml.models.autism_risk_classifier import AutismRiskClassifier
    print("✓ from ml.models.autism_risk_classifier import AutismRiskClassifier successful")
    
    # Try loading the model file
    model_path = "ml/models/saved/autism_risk_classifier_v1.pkl"
    if os.path.exists(model_path):
        print(f"✓ Model file exists: {model_path}")
        classifier = AutismRiskClassifier.load_model(model_path)
        print("✓ Model loaded successfully")
    else:
        print(f"✗ Model file NOT found: {model_path}")
        
except Exception as e:
    print(f"✗ Import/Load failed: {e}")
    import traceback
    traceback.print_exc()
