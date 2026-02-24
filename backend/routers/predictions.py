"""
Risk Prediction Routes
Generate autism risk predictions with SHAP explanations
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import sys
import os
from pathlib import Path
from datetime import date, datetime
import json

# Add project root to path for ml module
project_root = str(Path(__file__).parent.parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

from database import get_db
import models
import schemas
from auth import get_current_user
from rbac import check_assessment_access

# Try to import ML modules (optional if models not trained yet)
try:
    from ml.models.autism_risk_classifier import AutismRiskClassifier
    from ml.models.risk_escalation_predictor import RiskEscalationPredictor
    from ml.feature_engineering import FeatureEngineer
    from ml.intervention_planner import InterventionPlanner
    import pandas as pd
    ML_AVAILABLE = True
except Exception as e:
    import traceback
    print(f"⚠ ML modules not available: {e}")
    traceback.print_exc()
    ML_AVAILABLE = False
    AutismRiskClassifier = None
    RiskEscalationPredictor = None
    FeatureEngineer = None
    InterventionPlanner = None
    pd = None

router = APIRouter()

# Load ML models (loaded once on startup)
classifier = None
escalation_predictor = None
feature_engineer = None
intervention_planner = None

def load_models():
    """Load ML models on first use"""
    global classifier, escalation_predictor, feature_engineer, intervention_planner
    
    # Use a file for foolproof debug on Windows
    debug_path = os.path.join(project_root, "debug_load.txt")
    with open(debug_path, "a") as f:
        f.write(f"\n--- load_models called at {datetime.now()} ---\n")
        
        if classifier is None:
            # Priority 1: .env path, Priority 2: project root relative path
            model_path_env = os.getenv("ML_MODEL_PATH", "ml/models/saved/")
            f.write(f"DEBUG: ML_MODEL_PATH env: {model_path_env}\n")
            
            model_path = model_path_env
            if not os.path.isabs(model_path):
                # Specific fix for Windows relative paths from .env
                clean_rel = model_path.replace("../", "").replace("backend/../", "").replace("/", os.sep).strip(os.sep)
                model_path = os.path.join(project_root, clean_rel)
            
            f.write(f"DEBUG: Resolved model_path: {model_path}\n")

            model_a_file = os.path.join(model_path, "autism_risk_classifier_v1.pkl")
            model_b_file = os.path.join(model_path, "risk_escalation_predictor_v1.pkl")
            
            f.write(f"DEBUG: Checking Model A file: {model_a_file} (Exists: {os.path.exists(model_a_file)})\n")
            f.write(f"DEBUG: Checking Model B file: {model_b_file} (Exists: {os.path.exists(model_b_file)})\n")

            try:
                if AutismRiskClassifier and os.path.exists(model_a_file):
                    classifier = AutismRiskClassifier.load_model(model_a_file)
                    f.write("DEBUG: Model A loaded successfully!\n")
                
                if RiskEscalationPredictor and os.path.exists(model_b_file):
                    escalation_predictor = RiskEscalationPredictor.load_model(model_b_file)
                    f.write("DEBUG: Model B loaded successfully!\n")
                
                if FeatureEngineer:
                    feature_engineer = FeatureEngineer()
                if InterventionPlanner:
                    intervention_planner = InterventionPlanner()
            except Exception as e:
                f.write(f"DEBUG: Error during model loading: {e}\n")

@router.post("/run", response_model=schemas.RiskPredictionResponse)
async def run_realtime_prediction(
    request: schemas.ModelPredictionRequest,
    lang: schemas.Language = schemas.Language.ENGLISH,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Run real-time prediction for a selected model (Model A or B)"""
    if not ML_AVAILABLE:
        raise HTTPException(status_code=503, detail="ML modules not available")
    
    # Check access
    from rbac import check_child_access
    if not check_child_access(current_user, request.child_id, db):
        raise HTTPException(status_code=403, detail="Access denied")
    
    # 3. Create Assessment record
    cycle = db.query(models.Assessment).filter(models.Assessment.child_id == request.child_id).count() + 1
    
    assessment_data = request.inputs.copy()
    assessment_data['child_id'] = request.child_id
    assessment_data['assessment_cycle'] = cycle
    assessment_data['assessed_by'] = current_user.user_id
    assessment_data['assessment_date'] = date.today()
    
    child = db.query(models.Child).filter(models.Child.child_id == request.child_id).first()
    if child and child.dob:
        delta = date.today() - child.dob
        assessment_data['age_months'] = int(delta.days / 30.44)
    else:
        assessment_data['age_months'] = 12

    new_assessment = models.Assessment(**assessment_data)
    db.add(new_assessment)
    db.commit()
    db.refresh(new_assessment)

    return await generate_risk_prediction(new_assessment.assessment_id, request.model_type, lang, db, current_user)

@router.post("/{assessment_id}", response_model=schemas.RiskPredictionResponse)
async def generate_risk_prediction(
    assessment_id: int,
    model_type: schemas.ModelType = schemas.ModelType.MODEL_A,
    lang: schemas.Language = schemas.Language.ENGLISH,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Generate or retrieve risk prediction for an assessment"""
    try:
        if not ML_AVAILABLE:
            raise HTTPException(status_code=503, detail="ML modules not available")
        
        # 1. Load models
        load_models()
        
        if classifier is None:
            raise HTTPException(status_code=503, detail="ML models could not be loaded")

        # 2. Get assessment
        assessment = db.query(models.Assessment).filter(models.Assessment.assessment_id == assessment_id).first()
        if not assessment:
            raise HTTPException(status_code=404, detail="Assessment not found")
            
        # Check access
        if not check_assessment_access(current_user, assessment.assessment_id, db):
            raise HTTPException(status_code=403, detail="Access denied")

        # 3. Check for existing prediction of the same model type
        existing = db.query(models.ModelPrediction).filter(
            models.ModelPrediction.assessment_id == assessment_id,
            models.ModelPrediction.model_version.like(f"{model_type.value}%")
        ).first()
        
        if existing:
            return await format_prediction_response(existing, lang, db)

        # 4. Prepare data
        if model_type == schemas.ModelType.MODEL_A:
            return await _predict_model_a(assessment, lang, db)
        else:
            return await _predict_model_b(assessment, lang, db)
            
    except Exception as e:
        import traceback
        with open(os.path.join(project_root, "debug_load.txt"), "a") as f:
            f.write(f"DEBUG: Top-level Error: {e}\n")
            f.write(traceback.format_exc())
        raise e

async def _predict_model_a(assessment, lang, db):
    """Helper for Model A prediction"""
    # Calculate delayed domains if not provided
    delay_fields = [
        assessment.gross_motor_delay,
        assessment.fine_motor_delay,
        assessment.language_delay,
        assessment.cognitive_delay,
        assessment.socio_emotional_delay
    ]
    delayed_domains = sum(1 for d in delay_fields if d)
    
    child = db.query(models.Child).filter(models.Child.child_id == assessment.child_id).first()
    gender_binary = 1 if (child and child.gender == "Male") else 0
    
    raw_data = {
        'gross_motor_dq': assessment.gross_motor_dq,
        'fine_motor_dq': assessment.fine_motor_dq,
        'language_dq': assessment.language_dq,
        'cognitive_dq': assessment.cognitive_dq,
        'socio_emotional_dq': assessment.socio_emotional_dq,
        'composite_dq': assessment.composite_dq,
        'gross_motor_delay': assessment.gross_motor_delay or False,
        'fine_motor_delay': assessment.fine_motor_delay or False,
        'language_delay': assessment.language_delay or False,
        'cognitive_delay': assessment.cognitive_delay or False,
        'socio_emotional_delay': assessment.socio_emotional_delay or False,
        'delayed_domains': delayed_domains,
        'adhd_risk': assessment.adhd_risk or False,
        'behavior_risk': assessment.behavior_risk or False,
        'attention_score': assessment.attention_score or 70.0,
        'behavior_score': assessment.behavior_score or 15.0,
        'stunting': assessment.stunting or False,
        'wasting': assessment.wasting or False,
        'anemia': assessment.anemia or False,
        'nutrition_score': assessment.nutrition_score or 75.0,
        'caregiver_engagement_score': assessment.caregiver_engagement_score or 70.0,
        'language_exposure_score': assessment.language_exposure_score or 70.0,
        'parent_child_interaction_score': assessment.parent_child_interaction_score or 75.0,
        'stimulation_score': assessment.stimulation_score or 70.0,
        'age_months': assessment.age_months or 24,
        'gender_encoded': gender_binary
    }
    
    if feature_engineer:
        row_series = pd.Series(raw_data)
        raw_data['scii'] = feature_engineer.compute_scii(row_series)
        raw_data['nsi'] = feature_engineer.compute_nsi(row_series)
        raw_data['erm'] = feature_engineer.compute_erm(row_series)
        raw_data['dbs'] = feature_engineer.compute_dbs(row_series)
    else:
        raw_data['scii'], raw_data['nsi'], raw_data['erm'], raw_data['dbs'] = 30.0, 0.3, 70.0, delayed_domains/5.0

    # Ensure correct column order
    feature_cols = classifier.feature_names or list(raw_data.keys())
    input_df = pd.DataFrame([raw_data])[feature_cols]
    
    # Run prediction
    _, probabilities = classifier.predict(input_df)
    risk_prob = float(probabilities[0])
    risk_class = "High" if risk_prob > 0.5 else "Low"
    
    # Save prediction
    new_pred = models.ModelPrediction(
        assessment_id=assessment.assessment_id,
        model_version="Model A v1.0",
        high_probability=risk_prob,
        combined_high_probability=risk_prob,
        predicted_risk_class=risk_class,
        risk_tier="High Risk" if risk_class == "High" else "Low Risk",
        clinical_action="Urgent Clinical Referral" if risk_class == "High" else "Routine Monitoring"
    )
    db.add(new_pred)
    db.commit()
    db.refresh(new_pred)

    # Generate SHAP
    shap_data = classifier.explain_prediction(input_df)
    for feat in shap_data[0]:
        expl = models.SHAPExplanation(
            prediction_id=new_pred.prediction_id,
            feature_name=feat['feature_name'],
            shap_value=feat['shap_value'],
            feature_value=feat['feature_value']
        )
        db.add(expl)
    db.commit()

    return await format_prediction_response(new_pred, lang, db)

async def _predict_model_b(assessment, lang, db):
    """Helper for Model B prediction (Escalation)"""
    if escalation_predictor is None:
        raise HTTPException(status_code=503, detail="Model B weights not loaded")
        
    # Prepare Model B features
    raw_data = {
        'composite_dq': assessment.composite_dq,
        'socio_emotional_dq': assessment.socio_emotional_dq,
        'language_dq': assessment.language_dq,
        'behavior_score': assessment.behavior_score or 15.0,
        'delayed_domains': assessment.delayed_domains or 0,
        'dq_delta': 0, 
        'behavior_delta': 0,
        'socio_emotional_delta': 0,
        'environmental_delta': 0,
        'delay_delta': 0,
        'nutrition_delta': 0,
        'scii': 30.0,
        'nsi': 0.3,
        'erm': 70.0,
        'dbs': 0.5,
        'age_months': assessment.age_months or 24,
        'days_since_last_assessment': 30 
    }
    
    input_df = pd.DataFrame([raw_data])[escalation_predictor.feature_names]
    _, probabilities = escalation_predictor.predict(input_df)
    esc_prob = float(probabilities[0])
    
    new_pred = models.ModelPrediction(
        assessment_id=assessment.assessment_id,
        model_version="Model B v1.0",
        escalation_probability=esc_prob,
        predicted_escalation=esc_prob > 0.5,
        risk_tier="High Risk" if esc_prob > 0.5 else "Stable",
        clinical_action="Early Intervention Required" if esc_prob > 0.5 else "Periodic Review"
    )
    db.add(new_pred)
    db.commit()
    db.refresh(new_pred)
    
    return await format_prediction_response(new_pred, lang, db)

async def format_prediction_response(prediction, lang, db):
    load_models()
    
    shaps = db.query(models.SHAPExplanation).filter(
        models.SHAPExplanation.prediction_id == prediction.prediction_id
    ).all()

    # Build SHAP feature list for response
    top_features = [
        schemas.SHAPFeature(
            feature_name=s.feature_name,
            feature_value=float(s.feature_value or 0),
            shap_value=float(s.shap_value or 0),
            contribution_rank=i + 1,
            interpretation=f"{'Increases' if s.shap_value > 0 else 'Decreases'} risk",
            impact_direction="Positive" if s.shap_value > 0 else "Negative"
        )
        for i, s in enumerate(sorted(shaps, key=lambda x: abs(x.shap_value or 0), reverse=True)[:8])
    ]

    # Generate intervention recommendations
    recommendations = []
    if intervention_planner:
        try:
            shap_for_planner = [{'feature_name': s.feature_name, 'shap_value': float(s.shap_value or 0)} for s in shaps]
            raw_recs = intervention_planner.generate_pathway(shap_for_planner, lang.value if hasattr(lang, 'value') else lang)
            for r in raw_recs:
                recommendations.append(schemas.InterventionRecommendation(
                    category=r.get('category', 'General'),
                    priority=r.get('priority', 'Moderate'),
                    action_plan=r.get('parent_guide') or r.get('objective', 'Consult specialist'),
                    triggered_by=r.get('triggered_by', 'Assessment'),
                    impact_score=float(r.get('impact_score', 0))
                ))
        except Exception as e:
            print(f"Intervention planner error (non-fatal): {e}")

    # Build clinical summary
    risk_class = prediction.predicted_risk_class or "Low"
    risk_prob = float(prediction.combined_high_probability or prediction.escalation_probability or 0)
    risk_tier = prediction.risk_tier or ("High Risk" if risk_class == "High" else "Low Risk")
    
    if risk_class == "High":
        clinical_summary = (
            f"This child shows signs of elevated autism risk (probability: {risk_prob:.1%}). "
            "Immediate clinical referral is recommended for comprehensive evaluation."
        )
    else:
        clinical_summary = (
            f"This child's risk profile is within normal range (probability: {risk_prob:.1%}). "
            "Continue routine monitoring and parental engagement activities."
        )

    return schemas.RiskPredictionResponse(
        prediction_id=prediction.prediction_id,
        assessment_id=prediction.assessment_id,
        model_version=prediction.model_version or "Model A v1.0",
        predicted_risk_class=risk_class,
        combined_high_probability=risk_prob,
        risk_tier=risk_tier,
        clinical_action=prediction.clinical_action or "Routine Monitoring",
        escalation_probability=prediction.escalation_probability,
        predicted_escalation=prediction.predicted_escalation,
        early_warning_flag=risk_prob > 0.7,
        top_features=top_features,
        recommendations=recommendations,
        clinical_summary=clinical_summary,
        prediction_timestamp=prediction.prediction_timestamp or prediction.created_at
    )

@router.get("/{prediction_id}", response_model=schemas.RiskPredictionResponse)
async def get_prediction(
    prediction_id: int,
    lang: schemas.Language = schemas.Language.ENGLISH,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    prediction = db.query(models.ModelPrediction).filter(models.ModelPrediction.prediction_id == prediction_id).first()
    if not prediction:
        raise HTTPException(status_code=404, detail="Prediction not found")
    return await format_prediction_response(prediction, lang, db)
