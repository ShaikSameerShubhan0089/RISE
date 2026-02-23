-- ============================================================
-- CLINICAL-GRADE AUTISM RISK STRATIFICATION CDSS
-- PostgreSQL Database Schema
-- ============================================================
-- This schema supports:
-- - Longitudinal child development tracking
-- - ML-based risk stratification
-- - Clinical decision support workflows
-- - Role-based access control
-- - Audit logging
-- ============================================================

-- ============================================================
-- 1. MASTER LOCATION TABLES
-- ============================================================

CREATE TABLE states (
    state_id SERIAL PRIMARY KEY,
    state_name VARCHAR(150) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE districts (
    district_id SERIAL PRIMARY KEY,
    state_id INT NOT NULL REFERENCES states(state_id) ON DELETE CASCADE,
    district_name VARCHAR(150) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(state_id, district_name)
);

CREATE TABLE mandals (
    mandal_id SERIAL PRIMARY KEY,
    district_id INT NOT NULL REFERENCES districts(district_id) ON DELETE CASCADE,
    mandal_name VARCHAR(150) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(district_id, mandal_name)
);

CREATE TABLE anganwadi_centers (
    center_id SERIAL PRIMARY KEY,
    mandal_id INT NOT NULL REFERENCES mandals(mandal_id) ON DELETE CASCADE,
    center_code VARCHAR(50) UNIQUE NOT NULL,
    center_name VARCHAR(150) NOT NULL,
    address TEXT,
    contact_number VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 2. CHILD MASTER TABLE
-- ============================================================

CREATE TABLE children (
    child_id SERIAL PRIMARY KEY,
    unique_child_code VARCHAR(100) UNIQUE NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100),
    dob DATE NOT NULL,
    gender VARCHAR(20) CHECK (gender IN ('Male', 'Female', 'Other')),
    center_id INT NOT NULL REFERENCES anganwadi_centers(center_id) ON DELETE RESTRICT,
    
    -- Caregiver Information
    caregiver_name VARCHAR(150),
    caregiver_relationship VARCHAR(50),
    caregiver_education VARCHAR(100),
    caregiver_phone VARCHAR(20),
    caregiver_email VARCHAR(150),
    
    -- Administrative
    enrollment_date DATE DEFAULT CURRENT_DATE,
    status VARCHAR(50) DEFAULT 'Active' CHECK (status IN ('Active', 'Inactive', 'Transferred', 'Graduated')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 3. ASSESSMENTS (LONGITUDINAL TRACKING)
-- ============================================================

CREATE TABLE assessments (
    assessment_id SERIAL PRIMARY KEY,
    child_id INT NOT NULL REFERENCES children(child_id) ON DELETE CASCADE,
    assessment_cycle INT NOT NULL CHECK (assessment_cycle > 0),
    assessment_date DATE NOT NULL,
    age_months INT NOT NULL CHECK (age_months >= 0 AND age_months <= 72),
    
    -- Developmental Quotient (DQ) Scores (0-100 scale)
    gross_motor_dq FLOAT CHECK (gross_motor_dq >= 0 AND gross_motor_dq <= 100),
    fine_motor_dq FLOAT CHECK (fine_motor_dq >= 0 AND fine_motor_dq <= 100),
    language_dq FLOAT CHECK (language_dq >= 0 AND language_dq <= 100),
    cognitive_dq FLOAT CHECK (cognitive_dq >= 0 AND cognitive_dq <= 100),
    socio_emotional_dq FLOAT CHECK (socio_emotional_dq >= 0 AND socio_emotional_dq <= 100),
    composite_dq FLOAT CHECK (composite_dq >= 0 AND composite_dq <= 100),
    
    -- Developmental Delays (Boolean flags)
    gross_motor_delay BOOLEAN DEFAULT FALSE,
    fine_motor_delay BOOLEAN DEFAULT FALSE,
    language_delay BOOLEAN DEFAULT FALSE,
    cognitive_delay BOOLEAN DEFAULT FALSE,
    socio_emotional_delay BOOLEAN DEFAULT FALSE,
    delayed_domains INT CHECK (delayed_domains >= 0 AND delayed_domains <= 5),
    
    -- Neuro-Behavioral Screening
    autism_screen_flag BOOLEAN,
    adhd_risk BOOLEAN,
    behavior_risk BOOLEAN,
    attention_score FLOAT CHECK (attention_score >= 0 AND attention_score <= 100),
    behavior_score FLOAT CHECK (behavior_score >= 0 AND behavior_score <= 100),
    
    -- Nutrition Indicators
    stunting BOOLEAN,
    wasting BOOLEAN,
    anemia BOOLEAN,
    nutrition_score FLOAT CHECK (nutrition_score >= 0 AND nutrition_score <= 100),
    
    -- Environmental & Caregiving
    stimulation_score FLOAT CHECK (stimulation_score >= 0 AND stimulation_score <= 100),
    caregiver_engagement_score FLOAT CHECK (caregiver_engagement_score >= 0 AND caregiver_engagement_score <= 100),
    language_exposure_score FLOAT CHECK (language_exposure_score >= 0 AND language_exposure_score <= 100),
    parent_child_interaction_score FLOAT CHECK (parent_child_interaction_score >= 0 AND parent_child_interaction_score <= 100),
    
    -- Metadata
    assessed_by INT REFERENCES users(user_id),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(child_id, assessment_cycle)
);

-- ============================================================
-- 4. ENGINEERED FEATURES (ML-GENERATED)
-- ============================================================

CREATE TABLE engineered_features (
    feature_id SERIAL PRIMARY KEY,
    assessment_id INT NOT NULL REFERENCES assessments(assessment_id) ON DELETE CASCADE,
    
    -- Clinical Indices
    social_communication_impairment_index FLOAT, -- SCII
    neurodevelopmental_severity_index FLOAT,     -- NSI
    environmental_risk_modifier FLOAT,           -- ERM
    delay_burden_score FLOAT,                    -- DBS
    
    -- Longitudinal Changes (compared to previous cycle)
    dq_delta FLOAT,                    -- Change in composite DQ
    behavior_delta FLOAT,              -- Change in behavior score
    socio_emotional_delta FLOAT,       -- Change in SE_DQ
    environmental_delta FLOAT,         -- Change in environmental scores
    delay_delta INT,                   -- Change in number of delays
    nutrition_delta FLOAT,             -- Change in nutrition score
    
    -- Time metrics
    days_since_last_assessment INT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(assessment_id)
);

-- ============================================================
-- 5. MODEL PREDICTIONS
-- ============================================================

CREATE TABLE model_predictions (
    prediction_id SERIAL PRIMARY KEY,
    assessment_id INT NOT NULL REFERENCES assessments(assessment_id) ON DELETE CASCADE,
    model_version VARCHAR(50) NOT NULL,
    prediction_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Risk Classification Probabilities (sum to 1.0)
    low_probability FLOAT CHECK (low_probability >= 0 AND low_probability <= 1),
    moderate_probability FLOAT CHECK (moderate_probability >= 0 AND moderate_probability <= 1),
    high_probability FLOAT CHECK (high_probability >= 0 AND high_probability <= 1),
    
    -- Final Prediction
    predicted_risk_class VARCHAR(50) CHECK (predicted_risk_class IN ('Low', 'Moderate', 'High')),
    combined_high_probability FLOAT CHECK (combined_high_probability >= 0 AND combined_high_probability <= 1),
    
    -- Risk Stratification Tier
    risk_tier VARCHAR(50) CHECK (risk_tier IN ('Low Risk', 'Mild Concern', 'Moderate Risk', 'High Risk')),
    clinical_action VARCHAR(200),
    
    -- Escalation Prediction
    escalation_probability FLOAT CHECK (escalation_probability >= 0 AND escalation_probability <= 1),
    predicted_escalation BOOLEAN,
    
    -- Model Metadata
    model_confidence FLOAT,
    calibration_applied BOOLEAN DEFAULT TRUE,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(assessment_id, model_version)
);

-- ============================================================
-- 6. SHAP EXPLANATIONS (EXPLAINABLE AI)
-- ============================================================

CREATE TABLE shap_explanations (
    shap_id SERIAL PRIMARY KEY,
    prediction_id INT NOT NULL REFERENCES model_predictions(prediction_id) ON DELETE CASCADE,
    
    feature_name VARCHAR(150) NOT NULL,
    feature_value FLOAT,
    shap_value FLOAT NOT NULL,
    contribution_rank INT CHECK (contribution_rank >= 1 AND contribution_rank <= 5),
    
    -- Clinical Interpretation
    interpretation TEXT,
    impact_direction VARCHAR(20) CHECK (impact_direction IN ('Increases Risk', 'Decreases Risk')),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 7. REFERRALS
-- ============================================================

CREATE TABLE referrals (
    referral_id SERIAL PRIMARY KEY,
    assessment_id INT NOT NULL REFERENCES assessments(assessment_id) ON DELETE CASCADE,
    child_id INT NOT NULL REFERENCES children(child_id) ON DELETE CASCADE,
    
    -- Referral Details
    risk_level_at_referral VARCHAR(50) NOT NULL,
    referral_reason TEXT,
    referral_generated BOOLEAN DEFAULT FALSE,
    auto_generated BOOLEAN DEFAULT FALSE,
    
    -- Referral Dates
    referral_date DATE DEFAULT CURRENT_DATE,
    expected_completion_date DATE,
    completion_date DATE,
    
    -- Referral Target
    referred_to VARCHAR(200),
    specialist_type VARCHAR(100),
    facility_name VARCHAR(200),
    facility_contact VARCHAR(50),
    
    -- Status Tracking
    status VARCHAR(100) DEFAULT 'Pending' CHECK (status IN ('Pending', 'Scheduled', 'In Progress', 'Completed', 'Cancelled', 'No Show')),
    referral_completed BOOLEAN DEFAULT FALSE,
    
    -- Outcome
    outcome_summary TEXT,
    diagnosis_received VARCHAR(200),
    
    -- Metadata
    created_by INT REFERENCES users(user_id),
    updated_by INT REFERENCES users(user_id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 8. INTERVENTIONS
-- ============================================================

CREATE TABLE interventions (
    intervention_id SERIAL PRIMARY KEY,
    child_id INT NOT NULL REFERENCES children(child_id) ON DELETE CASCADE,
    referral_id INT REFERENCES referrals(referral_id) ON DELETE SET NULL,
    
    -- Intervention Details
    intervention_type VARCHAR(200) NOT NULL,
    intervention_category VARCHAR(100) CHECK (intervention_category IN ('Speech Therapy', 'Occupational Therapy', 'Behavioral Therapy', 'Early Intervention', 'Nutritional Support', 'Parental Training', 'Other')),
    intervention_description TEXT,
    
    -- Timeline
    start_date DATE NOT NULL,
    end_date DATE,
    planned_duration_weeks INT,
    actual_duration_weeks INT,
    
    -- Progress Tracking
    total_sessions_planned INT,
    sessions_completed INT DEFAULT 0,
    compliance_percentage FLOAT CHECK (compliance_percentage >= 0 AND compliance_percentage <= 100),
    
    -- Outcomes
    improvement_status VARCHAR(100) CHECK (improvement_status IN ('Significant Improvement', 'Moderate Improvement', 'Minimal Improvement', 'No Change', 'Decline', 'In Progress')),
    delay_reduction_months FLOAT,
    outcome_notes TEXT,
    
    -- Provider Information
    provider_name VARCHAR(150),
    provider_contact VARCHAR(50),
    
    -- Metadata
    created_by INT REFERENCES users(user_id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 9. USERS (ROLE-BASED ACCESS CONTROL)
-- ============================================================

CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    
    -- User Identity
    full_name VARCHAR(150) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    
    -- Role
    role VARCHAR(100) NOT NULL CHECK (role IN ('anganwadi_worker', 'supervisor', 'district_officer', 'state_admin', 'system_admin', 'parent')),
    
    -- Location Assignment (determines data access scope)
    state_id INT REFERENCES states(state_id) ON DELETE SET NULL,
    district_id INT REFERENCES districts(district_id) ON DELETE SET NULL,
    mandal_id INT REFERENCES mandals(mandal_id) ON DELETE SET NULL,
    center_id INT REFERENCES anganwadi_centers(center_id) ON DELETE SET NULL,
    
    -- Account Status
    status VARCHAR(50) DEFAULT 'Active' CHECK (status IN ('Active', 'Inactive', 'Suspended')),
    email_verified BOOLEAN DEFAULT FALSE,
    last_login TIMESTAMP,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 10. PARENT-CHILD MAPPING
-- ============================================================

CREATE TABLE parent_child_mapping (
    mapping_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    child_id INT NOT NULL REFERENCES children(child_id) ON DELETE CASCADE,
    relationship VARCHAR(50),
    is_primary_contact BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(user_id, child_id)
);

-- ============================================================
-- 11. AUDIT LOGS
-- ============================================================

CREATE TABLE audit_logs (
    log_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(user_id) ON DELETE SET NULL,
    
    -- Action Details
    action VARCHAR(200) NOT NULL,
    entity_type VARCHAR(100),
    entity_id INT,
    
    -- Request Details
    request_method VARCHAR(10),
    request_path VARCHAR(500),
    request_body TEXT,
    response_status INT,
    
    -- Metadata
    ip_address VARCHAR(50),
    user_agent TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 12. DISTRICT SUMMARY (AGGREGATED METRICS)
-- ============================================================

CREATE TABLE district_summary (
    summary_id SERIAL PRIMARY KEY,
    district_id INT NOT NULL REFERENCES districts(district_id) ON DELETE CASCADE,
    report_month DATE NOT NULL,
    
    -- Population Metrics
    total_children INT DEFAULT 0,
    total_assessments INT DEFAULT 0,
    
    -- Risk Distribution
    low_risk INT DEFAULT 0,
    moderate_risk INT DEFAULT 0,
    high_risk INT DEFAULT 0,
    
    -- Clinical Metrics
    referral_completion_rate FLOAT CHECK (referral_completion_rate >= 0 AND referral_completion_rate <= 100),
    risk_escalation_rate FLOAT,
    improvement_rate FLOAT,
    
    -- Intervention Metrics
    active_interventions INT DEFAULT 0,
    completed_interventions INT DEFAULT 0,
    
    -- Quality Indicators
    average_assessment_delay_days FLOAT,
    percentage_on_time_assessments FLOAT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(district_id, report_month)
);

-- ============================================================
-- INDEXES FOR PERFORMANCE OPTIMIZATION
-- ============================================================

-- Children
CREATE INDEX idx_children_center ON children(center_id);
CREATE INDEX idx_children_unique_code ON children(unique_child_code);
CREATE INDEX idx_children_status ON children(status);
CREATE INDEX idx_children_dob ON children(dob);

-- Assessments
CREATE INDEX idx_assessment_child ON assessments(child_id);
CREATE INDEX idx_assessment_date ON assessments(assessment_date);
CREATE INDEX idx_assessment_cycle ON assessments(assessment_cycle);
CREATE INDEX idx_assessment_child_cycle ON assessments(child_id, assessment_cycle);

-- Predictions
CREATE INDEX idx_prediction_assessment ON model_predictions(assessment_id);
CREATE INDEX idx_prediction_timestamp ON model_predictions(prediction_timestamp);
CREATE INDEX idx_prediction_risk_class ON model_predictions(predicted_risk_class);

-- Referrals
CREATE INDEX idx_referral_child ON referrals(child_id);
CREATE INDEX idx_referral_status ON referrals(status);
CREATE INDEX idx_referral_date ON referrals(referral_date);
CREATE INDEX idx_referral_completed ON referrals(referral_completed);

-- Interventions
CREATE INDEX idx_intervention_child ON interventions(child_id);
CREATE INDEX idx_intervention_dates ON interventions(start_date, end_date);

-- Users
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_center ON users(center_id);

-- Audit Logs
CREATE INDEX idx_audit_user ON audit_logs(user_id);
CREATE INDEX idx_audit_timestamp ON audit_logs(timestamp);
CREATE INDEX idx_audit_entity ON audit_logs(entity_type, entity_id);

-- District Summary
CREATE INDEX idx_district_summary ON district_summary(district_id, report_month);

-- ============================================================
-- TRIGGERS FOR AUTOMATIC TIMESTAMP UPDATES
-- ============================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_children_updated_at BEFORE UPDATE ON children
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_referrals_updated_at BEFORE UPDATE ON referrals
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_interventions_updated_at BEFORE UPDATE ON interventions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================
-- COMMENTS FOR DOCUMENTATION
-- ============================================================

COMMENT ON TABLE assessments IS 'Stores longitudinal developmental assessments for children across multiple cycles';
COMMENT ON TABLE model_predictions IS 'ML model predictions with risk stratification and SHAP explanations';
COMMENT ON TABLE shap_explanations IS 'SHAP feature importance values for explainable AI';
COMMENT ON TABLE referrals IS 'Clinical referrals generated based on risk assessments';
COMMENT ON TABLE interventions IS 'Intervention programs and their outcomes';
COMMENT ON TABLE audit_logs IS 'Complete audit trail of all system actions for compliance';

-- ============================================================
-- END OF SCHEMA
-- ============================================================
