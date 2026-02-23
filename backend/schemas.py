"""
Pydantic Schemas for Request/Response Validation
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import date, datetime
from enum import Enum


# Enums
class Gender(str, Enum):
    MALE = "Male"
    FEMALE = "Female"
    OTHER = "Other"

class Language(str, Enum):
    ENGLISH = "en"
    TELUGU = "te"
    HINDI = "hi"
    KANNADA = "kn"


class ChildStatus(str, Enum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"
    TRANSFERRED = "Transferred"
    GRADUATED = "Graduated"


class UserRole(str, Enum):
    ANGANWADI_WORKER = "anganwadi_worker"
    SUPERVISOR = "supervisor"
    DISTRICT_OFFICER = "district_officer"
    STATE_ADMIN = "state_admin"
    SYSTEM_ADMIN = "system_admin"
    PARENT = "parent"


class ReferralStatus(str, Enum):
    PENDING = "Pending"
    SCHEDULED = "Scheduled"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"
    NO_SHOW = "No Show"


# Child Schemas
class ChildBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    dob: date
    gender: Gender
    caregiver_name: Optional[str] = Field(None, max_length=150)
    caregiver_relationship: Optional[str] = Field(None, max_length=50)
    caregiver_education: Optional[str] = Field(None, max_length=100)
    caregiver_phone: Optional[str] = Field(None, max_length=20)
    caregiver_email: Optional[EmailStr] = None
    caregiver_additional_info: Optional[str] = None


class ChildCreate(ChildBase):
    center_id: int
    unique_child_code: Optional[str] = None  # Auto-generated if not provided
    
    # Parent account fields (optional)
    create_parent_account: bool = False
    parent_password: Optional[str] = Field(None, min_length=8)


class ChildResponse(ChildBase):
    child_id: int
    unique_child_code: str
    center_id: int
    enrollment_date: date
    status: ChildStatus
    center_name: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# Assessment Schemas
class AssessmentBase(BaseModel):
    assessment_cycle: int = Field(..., ge=1)
    assessment_date: date
    age_months: int = Field(..., ge=0, le=72)
    
    # DQ Scores
    gross_motor_dq: float = Field(..., ge=0, le=200)
    fine_motor_dq: float = Field(..., ge=0, le=200)
    language_dq: float = Field(..., ge=0, le=200)
    cognitive_dq: float = Field(..., ge=0, le=200)
    socio_emotional_dq: float = Field(..., ge=0, le=200)
    composite_dq: float = Field(..., ge=0, le=200)
    
    # Delays
    gross_motor_delay: bool = False
    fine_motor_delay: bool = False
    language_delay: bool = False
    cognitive_delay: bool = False
    socio_emotional_delay: bool = False
    delayed_domains: int = Field(..., ge=0, le=5)
    
    # Neuro-behavioral
    autism_screen_flag: Optional[bool] = None
    adhd_risk: Optional[bool] = None
    behavior_risk: Optional[bool] = None
    attention_score: Optional[float] = Field(None, ge=0, le=200)
    behavior_score: Optional[float] = Field(None, ge=0, le=200)
    
    # Nutrition
    stunting: Optional[bool] = None
    wasting: Optional[bool] = None
    anemia: Optional[bool] = None
    nutrition_score: Optional[float] = Field(None, ge=0, le=200)
    
    # Environmental
    stimulation_score: Optional[float] = Field(None, ge=0, le=200)
    caregiver_engagement_score: Optional[float] = Field(None, ge=0, le=200)
    language_exposure_score: Optional[float] = Field(None, ge=0, le=200)
    parent_child_interaction_score: Optional[float] = Field(None, ge=0, le=200)
    
    notes: Optional[str] = None


class AssessmentCreate(AssessmentBase):
    child_id: int


class AssessmentResponse(AssessmentBase):
    assessment_id: int
    child_id: int
    assessed_by: Optional[int]
    created_at: datetime
    
    class Config:
        from_attributes = True


# Risk Prediction Schemas
class SHAPFeature(BaseModel):
    feature_name: str
    feature_value: float
    shap_value: float
    contribution_rank: int
    interpretation: str
    impact_direction: str


class InterventionRecommendation(BaseModel):
    category: str
    priority: str
    action_plan: str
    triggered_by: str
    impact_score: float

class ModelType(str, Enum):
    MODEL_A = "Model A"
    MODEL_B = "Model B"


class ModelPredictionRequest(BaseModel):
    child_id: int
    model_type: ModelType
    inputs: dict  # Raw inputs for the model
    assessment_cycle: Optional[int] = None

class RiskPredictionResponse(BaseModel):
    prediction_id: int
    assessment_id: int
    model_version: str
    
    # Risk classification (Problem A)
    predicted_risk_class: str
    combined_high_probability: float
    risk_tier: str
    clinical_action: str
    
    # Predictive Early Warnings (Problem A extension)
    escalation_probability: Optional[float]
    predicted_escalation: Optional[bool]
    early_warning_flag: bool = False
    
    # SHAP explanations
    top_features: List[SHAPFeature]
    
    # AI-Driven Intervention Pathway (Problem B)
    recommendations: List[InterventionRecommendation] = []
    clinical_summary: Optional[str] = None
    
    # Clinical disclaimer
    disclaimer: str = "This tool provides autism risk stratification based on structured developmental assessments. It does NOT provide a clinical diagnosis. Final diagnosis must be made by a qualified pediatrician or developmental specialist."
    
    prediction_timestamp: datetime
    
    class Config:
        from_attributes = True


# Referral Schemas
class ReferralBase(BaseModel):
    referred_to: Optional[str] = Field(None, max_length=200)
    specialist_type: Optional[str] = Field(None, max_length=100)
    facility_name: Optional[str] = Field(None, max_length=200)
    facility_contact: Optional[str] = Field(None, max_length=50)
    referral_reason: Optional[str] = None
    expected_completion_date: Optional[date] = None


class ReferralCreate(ReferralBase):
    assessment_id: int
    child_id: int


class ReferralUpdate(BaseModel):
    status: Optional[ReferralStatus] = None
    completion_date: Optional[date] = None
    outcome_summary: Optional[str] = None
    diagnosis_received: Optional[str] = None


class ReferralResponse(ReferralBase):
    referral_id: int
    assessment_id: int
    child_id: int
    risk_level_at_referral: str
    auto_generated: bool
    referral_date: date
    status: ReferralStatus
    referral_completed: bool
    child_name: Optional[str] = None
    center_name: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# Intervention Schemas
class InterventionBase(BaseModel):
    intervention_type: str = Field(..., max_length=200)
    intervention_category: str
    intervention_description: Optional[str] = None
    start_date: date
    end_date: Optional[date] = None
    planned_duration_weeks: Optional[int] = None
    total_sessions_planned: Optional[int] = None
    provider_name: Optional[str] = Field(None, max_length=150)
    provider_contact: Optional[str] = Field(None, max_length=50)


class InterventionCreate(InterventionBase):
    child_id: int
    referral_id: Optional[int] = None


class InterventionUpdate(BaseModel):
    sessions_completed: Optional[int] = None
    compliance_percentage: Optional[float] = Field(None, ge=0, le=100)
    improvement_status: Optional[str] = None
    delay_reduction_months: Optional[float] = None
    outcome_notes: Optional[str] = None
    end_date: Optional[date] = None


class InterventionResponse(InterventionBase):
    intervention_id: int
    child_id: int
    referral_id: Optional[int]
    sessions_completed: int
    compliance_percentage: Optional[float]
    improvement_status: Optional[str]
    delay_reduction_months: Optional[float]
    created_at: datetime
    
    class Config:
        from_attributes = True


# User Schemas
class UserBase(BaseModel):
    full_name: str = Field(..., max_length=150)
    email: EmailStr
    role: UserRole


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    state_id: Optional[int] = None
    district_id: Optional[int] = None
    mandal_id: Optional[int] = None
    center_id: Optional[int] = None


class UserResponse(UserBase):
    user_id: int
    state_id: Optional[int]
    district_id: Optional[int]
    mandal_id: Optional[int]
    center_id: Optional[int]
    status: str
    email_verified: bool
    last_login: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# Parent Portal Schemas
class ChildTimeline(BaseModel):
    assessment_id: int
    assessment_cycle: int
    assessment_date: date
    age_months: int
    composite_dq: float
    risk_tier: Optional[str]
    risk_probability: Optional[float]


class ParentChildView(BaseModel):
    child: ChildResponse
    latest_assessment: Optional[AssessmentResponse]
    latest_risk_prediction: Optional[RiskPredictionResponse]
    assessment_history: List[ChildTimeline]
    active_interventions: List[InterventionResponse]


# District Summary Schema
class DistrictSummaryResponse(BaseModel):
    summary_id: int
    district_id: int
    report_month: date
    total_children: int
    total_assessments: int
    low_risk: int
    moderate_risk: int
    high_risk: int
    referral_completion_rate: Optional[float]
    risk_escalation_rate: Optional[float]
    improvement_rate: Optional[float]
    active_interventions: int
    completed_interventions: int
    
    class Config:
        from_attributes = True
