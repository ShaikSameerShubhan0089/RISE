"""
SQLAlchemy ORM Models
Maps to PostgreSQL database schema
"""

from sqlalchemy import (
    Column, Integer, String, Date, Float, Boolean, Text, 
    DateTime, ForeignKey, CheckConstraint, UniqueConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

from database import Base


class State(Base):
    __tablename__ = "states"
    
    state_id = Column(Integer, primary_key=True, index=True)
    state_name = Column(String(150), nullable=False, unique=True)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    districts = relationship("District", back_populates="state", cascade="all, delete-orphan")
    users = relationship("User", back_populates="state")


class District(Base):
    __tablename__ = "districts"
    
    district_id = Column(Integer, primary_key=True, index=True)
    state_id = Column(Integer, ForeignKey("states.state_id", ondelete="CASCADE"), nullable=False)
    district_name = Column(String(150), nullable=False)
    created_at = Column(DateTime, default=func.now())
    
    __table_args__ = (
        UniqueConstraint('state_id', 'district_name', name='uq_state_district'),
    )
    
    # Relationships
    state = relationship("State", back_populates="districts")
    mandals = relationship("Mandal", back_populates="district", cascade="all, delete-orphan")
    users = relationship("User", back_populates="district")
    district_summaries = relationship("DistrictSummary", back_populates="district")


class Mandal(Base):
    __tablename__ = "mandals"
    
    mandal_id = Column(Integer, primary_key=True, index=True)
    district_id = Column(Integer, ForeignKey("districts.district_id", ondelete="CASCADE"), nullable=False)
    mandal_name = Column(String(150), nullable=False)
    created_at = Column(DateTime, default=func.now())
    
    __table_args__ = (
        UniqueConstraint('district_id', 'mandal_name', name='uq_district_mandal'),
    )
    
    # Relationships
    district = relationship("District", back_populates="mandals")
    anganwadi_centers = relationship("AnganwadiCenter", back_populates="mandal", cascade="all, delete-orphan")
    users = relationship("User", back_populates="mandal")


class AnganwadiCenter(Base):
    __tablename__ = "anganwadi_centers"
    
    center_id = Column(Integer, primary_key=True, index=True)
    mandal_id = Column(Integer, ForeignKey("mandals.mandal_id", ondelete="CASCADE"), nullable=False)
    center_code = Column(String(50), unique=True, nullable=False)
    center_name = Column(String(150), nullable=False)
    address = Column(Text)
    contact_number = Column(String(20))
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    mandal = relationship("Mandal", back_populates="anganwadi_centers")
    children = relationship("Child", back_populates="center")
    users = relationship("User", back_populates="center")


class Child(Base):
    __tablename__ = "children"
    
    child_id = Column(Integer, primary_key=True, index=True)
    unique_child_code = Column(String(100), unique=True, nullable=False, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100))
    dob = Column(Date, nullable=False, index=True)
    gender = Column(String(20), CheckConstraint("gender IN ('Male', 'Female', 'Other')"))
    center_id = Column(Integer, ForeignKey("anganwadi_centers.center_id", ondelete="RESTRICT"), nullable=False, index=True)
    
    # Caregiver information
    caregiver_name = Column(String(150))
    caregiver_relationship = Column(String(50))
    caregiver_education = Column(String(100))
    caregiver_phone = Column(String(20))
    caregiver_email = Column(String(150))
    caregiver_additional_info = Column(Text)
    
    # Administrative
    enrollment_date = Column(Date, default=func.current_date())
    status = Column(String(50), CheckConstraint("status IN ('Active', 'Inactive', 'Transferred', 'Graduated')"), default='Active', index=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    center = relationship("AnganwadiCenter", back_populates="children")
    assessments = relationship("Assessment", back_populates="child", cascade="all, delete-orphan")
    referrals = relationship("Referral", back_populates="child")
    interventions = relationship("Intervention", back_populates="child")
    parent_mappings = relationship("ParentChildMapping", back_populates="child")


class Assessment(Base):
    __tablename__ = "assessments"
    
    assessment_id = Column(Integer, primary_key=True, index=True)
    child_id = Column(Integer, ForeignKey("children.child_id", ondelete="CASCADE"), nullable=False, index=True)
    assessment_cycle = Column(Integer, CheckConstraint("assessment_cycle > 0"), nullable=False)
    assessment_date = Column(Date, nullable=False, index=True)
    age_months = Column(Integer, CheckConstraint("age_months >= 0 AND age_months <= 72"), nullable=False)
    
    # DQ Scores
    gross_motor_dq = Column(Float, CheckConstraint("gross_motor_dq >= 0 AND gross_motor_dq <= 200"))
    fine_motor_dq = Column(Float, CheckConstraint("fine_motor_dq >= 0 AND fine_motor_dq <= 200"))
    language_dq = Column(Float, CheckConstraint("language_dq >= 0 AND language_dq <= 200"))
    cognitive_dq = Column(Float, CheckConstraint("cognitive_dq >= 0 AND cognitive_dq <= 200"))
    socio_emotional_dq = Column(Float, CheckConstraint("socio_emotional_dq >= 0 AND socio_emotional_dq <= 200"))
    composite_dq = Column(Float, CheckConstraint("composite_dq >= 0 AND composite_dq <= 200"))
    
    # Delays
    gross_motor_delay = Column(Boolean, default=False)
    fine_motor_delay = Column(Boolean, default=False)
    language_delay = Column(Boolean, default=False)
    cognitive_delay = Column(Boolean, default=False)
    socio_emotional_delay = Column(Boolean, default=False)
    delayed_domains = Column(Integer, CheckConstraint("delayed_domains >= 0 AND delayed_domains <= 5"))
    
    # Neuro-behavioral
    autism_screen_flag = Column(Boolean)
    adhd_risk = Column(Boolean)
    behavior_risk = Column(Boolean)
    attention_score = Column(Float, CheckConstraint("attention_score >= 0 AND attention_score <= 200"))
    behavior_score = Column(Float, CheckConstraint("behavior_score >= 0 AND behavior_score <= 200"))
    
    # Nutrition
    stunting = Column(Boolean)
    wasting = Column(Boolean)
    anemia = Column(Boolean)
    nutrition_score = Column(Float, CheckConstraint("nutrition_score >= 0 AND nutrition_score <= 200"))
    
    # Environmental
    stimulation_score = Column(Float, CheckConstraint("stimulation_score >= 0 AND stimulation_score <= 200"))
    caregiver_engagement_score = Column(Float, CheckConstraint("caregiver_engagement_score >= 0 AND caregiver_engagement_score <= 200"))
    language_exposure_score = Column(Float, CheckConstraint("language_exposure_score >= 0 AND language_exposure_score <= 200"))
    parent_child_interaction_score = Column(Float, CheckConstraint("parent_child_interaction_score >= 0 AND parent_child_interaction_score <= 200"))
    
    # Metadata
    assessed_by = Column(Integer, ForeignKey("users.user_id"))
    notes = Column(Text)
    created_at = Column(DateTime, default=func.now())
    
    __table_args__ = (
        UniqueConstraint('child_id', 'assessment_cycle', name='uq_child_cycle'),
    )
    
    # Relationships
    child = relationship("Child", back_populates="assessments")
    assessor = relationship("User", foreign_keys=[assessed_by])
    engineered_features = relationship("EngineeredFeature", back_populates="assessment", uselist=False)
    model_predictions = relationship("ModelPrediction", back_populates="assessment")
    referrals = relationship("Referral", back_populates="assessment")


class EngineeredFeature(Base):
    __tablename__ = "engineered_features"
    
    feature_id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("assessments.assessment_id", ondelete="CASCADE"), nullable=False, unique=True)
    
    # Clinical indices
    social_communication_impairment_index = Column(Float)
    neurodevelopmental_severity_index = Column(Float)
    environmental_risk_modifier = Column(Float)
    delay_burden_score = Column(Float)
    
    # Longitudinal changes
    dq_delta = Column(Float)
    behavior_delta = Column(Float)
    socio_emotional_delta = Column(Float)
    environmental_delta = Column(Float)
    delay_delta = Column(Integer)
    nutrition_delta = Column(Float)
    days_since_last_assessment = Column(Integer)
    
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    assessment = relationship("Assessment", back_populates="engineered_features")


class ModelPrediction(Base):
    __tablename__ = "model_predictions"
    
    prediction_id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("assessments.assessment_id", ondelete="CASCADE"), nullable=False, index=True)
    model_version = Column(String(50), nullable=False)
    prediction_timestamp = Column(DateTime, default=func.now())
    
    # Risk probabilities
    low_probability = Column(Float, CheckConstraint("low_probability >= 0 AND low_probability <= 1"))
    moderate_probability = Column(Float, CheckConstraint("moderate_probability >= 0 AND moderate_probability <= 1"))
    high_probability = Column(Float, CheckConstraint("high_probability >= 0 AND high_probability <= 1"))
    
    # Prediction
    predicted_risk_class = Column(String(50), CheckConstraint("predicted_risk_class IN ('Low', 'Moderate', 'High')"))
    combined_high_probability = Column(Float, CheckConstraint("combined_high_probability >= 0 AND combined_high_probability <= 1"))
    
    # Risk tier
    risk_tier = Column(String(50), CheckConstraint("risk_tier IN ('Low Risk', 'Mild Concern', 'Moderate Risk', 'High Risk')"))
    clinical_action = Column(String(200))
    
    # Escalation
    escalation_probability = Column(Float, CheckConstraint("escalation_probability >= 0 AND escalation_probability <= 1"))
    predicted_escalation = Column(Boolean)
    
    # Metadata
    model_confidence = Column(Float)
    calibration_applied = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    
    __table_args__ = (
        UniqueConstraint('assessment_id', 'model_version', name='uq_assessment_model'),
    )
    
    # Relationships
    assessment = relationship("Assessment", back_populates="model_predictions")
    shap_explanations = relationship("SHAPExplanation", back_populates="prediction", cascade="all, delete-orphan")


class SHAPExplanation(Base):
    __tablename__ = "shap_explanations"
    
    prediction_id = Column(Integer, ForeignKey("model_predictions.prediction_id", ondelete="CASCADE"), primary_key=True)
    feature_name = Column(String(100), primary_key=True)
    feature_value = Column(Float)
    shap_value = Column(Float, nullable=False)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    prediction = relationship("ModelPrediction", back_populates="shap_explanations")


class Referral(Base):
    __tablename__ = "referrals"
    
    referral_id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("assessments.assessment_id", ondelete="CASCADE"), nullable=False)
    child_id = Column(Integer, ForeignKey("children.child_id", ondelete="CASCADE"), nullable=False, index=True)
    
    risk_level_at_referral = Column(String(50), nullable=False)
    referral_reason = Column(Text)
    referral_generated = Column(Boolean, default=False)
    auto_generated = Column(Boolean, default=False)
    
    referral_date = Column(Date, default=func.current_date(), index=True)
    expected_completion_date = Column(Date)
    completion_date = Column(Date)
    
    referred_to = Column(String(200))
    specialist_type = Column(String(100))
    facility_name = Column(String(200))
    facility_contact = Column(String(50))
    
    status = Column(String(100), 
                   CheckConstraint("status IN ('Pending', 'Scheduled', 'In Progress', 'Completed', 'Cancelled', 'No Show')"),
                   default='Pending',
                   index=True)
    referral_completed = Column(Boolean, default=False, index=True)
    
    outcome_summary = Column(Text)
    diagnosis_received = Column(String(200))
    
    created_by = Column(Integer, ForeignKey("users.user_id"))
    updated_by = Column(Integer, ForeignKey("users.user_id"))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    assessment = relationship("Assessment", back_populates="referrals")
    child = relationship("Child", back_populates="referrals")
    creator = relationship("User", foreign_keys=[created_by])
    updater = relationship("User", foreign_keys=[updated_by])
    interventions = relationship("Intervention", back_populates="referral")


class Intervention(Base):
    __tablename__ = "interventions"
    
    intervention_id = Column(Integer, primary_key=True, index=True)
    child_id = Column(Integer, ForeignKey("children.child_id", ondelete="CASCADE"), nullable=False, index=True)
    referral_id = Column(Integer, ForeignKey("referrals.referral_id", ondelete="SET NULL"))
    
    intervention_type = Column(String(200), nullable=False)
    intervention_category = Column(String(100),
                                   CheckConstraint("intervention_category IN ('Speech Therapy', 'Occupational Therapy', 'Behavioral Therapy', 'Early Intervention', 'Nutritional Support', 'Parental Training', 'Other')"))
    intervention_description = Column(Text)
    
    start_date = Column(Date, nullable=False, index=True)
    end_date = Column(Date)
    planned_duration_weeks = Column(Integer)
    actual_duration_weeks = Column(Integer)
    
    total_sessions_planned = Column(Integer)
    sessions_completed = Column(Integer, default=0)
    compliance_percentage = Column(Float, CheckConstraint("compliance_percentage >= 0 AND compliance_percentage <= 100"))
    
    improvement_status = Column(String(100),
                               CheckConstraint("improvement_status IN ('Significant Improvement', 'Moderate Improvement', 'Minimal Improvement', 'No Change', 'Decline', 'In Progress')"))
    delay_reduction_months = Column(Float)
    outcome_notes = Column(Text)
    
    provider_name = Column(String(150))
    provider_contact = Column(String(50))
    
    created_by = Column(Integer, ForeignKey("users.user_id"))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    child = relationship("Child", back_populates="interventions")
    referral = relationship("Referral", back_populates="interventions")
    creator = relationship("User", foreign_keys=[created_by])


class User(Base):
    __tablename__ = "users"
    
    user_id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(150), nullable=False)
    email = Column(String(150), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    
    role = Column(String(100), 
                 CheckConstraint("role IN ('anganwadi_worker', 'supervisor', 'district_officer', 'state_admin', 'system_admin', 'parent')"),
                 nullable=False,
                 index=True)
    
    # Location assignment
    state_id = Column(Integer, ForeignKey("states.state_id", ondelete="SET NULL"))
    district_id = Column(Integer, ForeignKey("districts.district_id", ondelete="SET NULL"))
    mandal_id = Column(Integer, ForeignKey("mandals.mandal_id", ondelete="SET NULL"))
    center_id = Column(Integer, ForeignKey("anganwadi_centers.center_id", ondelete="SET NULL"), index=True)
    
    status = Column(String(50), 
                   CheckConstraint("status IN ('Active', 'Inactive', 'Suspended', 'Revoked')"),
                   default='Active')
    email_verified = Column(Boolean, default=False)
    last_login = Column(DateTime)
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    state = relationship("State", back_populates="users")
    district = relationship("District", back_populates="users")
    mandal = relationship("Mandal", back_populates="users")
    center = relationship("AnganwadiCenter", back_populates="users")
    parent_mappings = relationship("ParentChildMapping", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="user")


class ParentChildMapping(Base):
    __tablename__ = "parent_child_mapping"
    
    mapping_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    child_id = Column(Integer, ForeignKey("children.child_id", ondelete="CASCADE"), nullable=False)
    relationship_type = Column(String(50))
    is_primary_contact = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    
    # __table_args__ = (
    #     UniqueConstraint('user_id', 'child_id', name='uq_user_child'),
    # )
    
    # Relationships
    user = relationship("User", back_populates="parent_mappings")
    child = relationship("Child", back_populates="parent_mappings")


class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    log_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="SET NULL"), index=True)
    
    action = Column(String(200), nullable=False)
    entity_type = Column(String(100), index=True)
    entity_id = Column(Integer, index=True)
    
    request_method = Column(String(10))
    request_path = Column(String(500))
    request_body = Column(Text)
    response_status = Column(Integer)
    
    ip_address = Column(String(50))
    user_agent = Column(Text)
    timestamp = Column(DateTime, default=func.now(), index=True)
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")


class DistrictSummary(Base):
    __tablename__ = "district_summary"
    
    summary_id = Column(Integer, primary_key=True, index=True)
    district_id = Column(Integer, ForeignKey("districts.district_id", ondelete="CASCADE"), nullable=False, index=True)
    report_month = Column(Date, nullable=False, index=True)
    
    total_children = Column(Integer, default=0)
    total_assessments = Column(Integer, default=0)
    
    low_risk = Column(Integer, default=0)
    moderate_risk = Column(Integer, default=0)
    high_risk = Column(Integer, default=0)
    
    referral_completion_rate = Column(Float, CheckConstraint("referral_completion_rate >= 0 AND referral_completion_rate <= 100"))
    risk_escalation_rate = Column(Float)
    improvement_rate = Column(Float)
    
    active_interventions = Column(Integer, default=0)
    completed_interventions = Column(Integer, default=0)
    
    average_assessment_delay_days = Column(Float)
    percentage_on_time_assessments = Column(Float)
    
    created_at = Column(DateTime, default=func.now())
    
    __table_args__ = (
        UniqueConstraint('district_id', 'report_month', name='uq_district_month'),
    )
    
    # Relationships
    district = relationship("District", back_populates="district_summaries")
