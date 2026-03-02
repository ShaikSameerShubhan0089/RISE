-- ============================================================
-- SEED DATA FOR DEVELOPMENT AND TESTING
-- RISE - Risk Identification System for Early Detection
-- ============================================================

-- ============================================================
-- 1. LOCATION HIERARCHY
-- ============================================================

-- States
INSERT INTO states (state_name) VALUES
('Telangana'),
('Andhra Pradesh'),
('Karnataka');

-- Districts
INSERT INTO districts (state_id, district_name) VALUES
(1, 'Hyderabad'),
(1, 'Rangareddy'),
(1, 'Medchal-Malkajgiri'),
(2, 'Visakhapatnam'),
(2, 'Vijayawada'),
(3, 'Bangalore Urban');

-- Mandals
INSERT INTO mandals (district_id, mandal_name) VALUES
(1, 'Secunderabad'),
(1, 'Kukatpally'),
(1, 'LB Nagar'),
(2, 'Shamshabad'),
(2, 'Rajendranagar'),
(3, 'Ghatkesar'),
(4, 'Gajuwaka'),
(5, 'Gannavaram');

-- Anganwadi Centers
INSERT INTO anganwadi_centers (mandal_id, center_code, center_name, address, contact_number) VALUES
(1, 'SEC-AWC-001', 'Secunderabad Center 1', 'Plot 45, Tirmulgherry', '9876543210'),
(1, 'SEC-AWC-002', 'Secunderabad Center 2', 'West Marredpally', '9876543211'),
(2, 'KUK-AWC-001', 'Kukatpally Center 1', 'KPHB Colony', '9876543212'),
(3, 'LBN-AWC-001', 'LB Nagar Center 1', 'Kothapet', '9876543213'),
(4, 'SHA-AWC-001', 'Shamshabad Center 1', 'Near Airport', '9876543214'),
(5, 'RAJ-AWC-001', 'Rajendranagar Center 1', 'Budwel', '9876543215'),
(6, 'GHA-AWC-001', 'Ghatkesar Center 1', 'Old Village', '9876543216'),
(7, 'GAJ-AWC-001', 'Gajuwaka Center 1', 'Main Road', '9876543217'),
(8, 'GAN-AWC-001', 'Gannavaram Center 1', 'Center Street', '9876543218');

-- ============================================================
-- 2. USERS (ROLE-BASED ACCESS)
-- ============================================================

-- Password: 'password123' (hashed with bcrypt)
-- In production, use proper password hashing library

INSERT INTO users (full_name, email, password_hash, role, state_id, district_id, mandal_id, center_id, status, email_verified) VALUES
-- System Admin
('Admin User', 'admin@cdss.gov.in', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5lR4z8lRfVvvu', 'system_admin', NULL, NULL, NULL, NULL, 'Active', TRUE),

-- State Admins
('Telangana Admin', 'telangana.admin@cdss.gov.in', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5lR4z8lRfVvvu', 'state_admin', 1, NULL, NULL, NULL, 'Active', TRUE),
('AP Admin', 'ap.admin@cdss.gov.in', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5lR4z8lRfVvvu', 'state_admin', 2, NULL, NULL, NULL, 'Active', TRUE),

-- District Officers
('Hyderabad DO', 'hyd.do@cdss.gov.in', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5lR4z8lRfVvvu', 'district_officer', 1, 1, NULL, NULL, 'Active', TRUE),
('Rangareddy DO', 'ranga.do@cdss.gov.in', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5lR4z8lRfVvvu', 'district_officer', 1, 2, NULL, NULL, 'Active', TRUE),

-- Supervisors
('Supervisor - Secunderabad', 'sup.sec@cdss.gov.in', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5lR4z8lRfVvvu', 'supervisor', 1, 1, 1, NULL, 'Active', TRUE),
('Supervisor - Kukatpally', 'sup.kuk@cdss.gov.in', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5lR4z8lRfVvvu', 'supervisor', 1, 1, 2, NULL, 'Active', TRUE),

-- Anganwadi Workers
('Priya Sharma', 'priya.sharma@awc.gov.in', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5lR4z8lRfVvvu', 'anganwadi_worker', 1, 1, 1, 1, 'Active', TRUE),
('Lakshmi Reddy', 'lakshmi.reddy@awc.gov.in', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5lR4z8lRfVvvu', 'anganwadi_worker', 1, 1, 1, 2, 'Active', TRUE),
('Sunita Devi', 'sunita.devi@awc.gov.in', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5lR4z8lRfVvvu', 'anganwadi_worker', 1, 1, 2, 3, 'Active', TRUE),
('Anjali Patel', 'anjali.patel@awc.gov.in', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5lR4z8lRfVvvu', 'anganwadi_worker', 1, 1, 3, 4, 'Active', TRUE),

-- Parents (will be linked to children)
('Ramesh Kumar', 'ramesh.k@gmail.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5lR4z8lRfVvvu', 'parent', NULL, NULL, NULL, NULL, 'Active', TRUE),
('Deepa Singh', 'deepa.s@gmail.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5lR4z8lRfVvvu', 'parent', NULL, NULL, NULL, NULL, 'Active', TRUE),
('Vijay Menon', 'vijay.m@gmail.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5lR4z8lRfVvvu', 'parent', NULL, NULL, NULL, NULL, 'Active', TRUE);

-- ============================================================
-- 3. SAMPLE CHILDREN
-- ============================================================

INSERT INTO children (unique_child_code, first_name, last_name, dob, gender, center_id, caregiver_name, caregiver_relationship, caregiver_education, caregiver_phone, caregiver_email, enrollment_date, status) VALUES
('SEC001-2023-001', 'Aarav', 'Kumar', '2021-03-15', 'Male', 1, 'Ramesh Kumar', 'Father', 'Graduate', '9876501001', 'ramesh.k@gmail.com', '2023-01-10', 'Active'),
('SEC001-2023-002', 'Priya', 'Singh', '2021-06-20', 'Female', 1, 'Deepa Singh', 'Mother', 'Post Graduate', '9876501002', 'deepa.s@gmail.com', '2023-01-15', 'Active'),
('SEC002-2023-003', 'Arjun', 'Patel', '2020-11-10', 'Male', 2, 'Sunita Patel', 'Mother', 'High School', '9876501003', 'sunita.p@gmail.com', '2023-02-01', 'Active'),
('KUK001-2023-004', 'Ananya', 'Reddy', '2021-08-05', 'Female', 3, 'Lakshmi Reddy', 'Mother', 'Graduate', '9876501004', 'lakshmi.r@gmail.com', '2023-02-10', 'Active'),
('LBN001-2023-005', 'Rohan', 'Menon', '2021-01-25', 'Male', 4, 'Vijay Menon', 'Father', 'Graduate', '9876501005', 'vijay.m@gmail.com', '2023-02-20', 'Active'),
('SEC001-2023-006', 'Kavya', 'Sharma', '2021-04-12', 'Female', 1, 'Meena Sharma', 'Mother', 'Graduate', '9876501006', 'meena.s@gmail.com', '2023-03-01', 'Active'),
('SEC002-2023-007', 'Ishaan', 'Gupta', '2020-09-18', 'Male', 2, 'Rajesh Gupta', 'Father', 'Post Graduate', '9876501007', 'rajesh.g@gmail.com', '2023-03-05', 'Active'),
('KUK001-2023-008', 'Diya', 'Nair', '2021-12-03', 'Female', 3, 'Priya Nair', 'Mother', 'Graduate', '9876501008', 'priya.n@gmail.com', '2023-03-10', 'Active');

-- ============================================================
-- 4. PARENT-CHILD MAPPING
-- ============================================================

INSERT INTO parent_child_mapping (user_id, child_id, relationship, is_primary_contact) VALUES
(12, 1, 'Father', TRUE),   -- Ramesh Kumar -> Aarav
(13, 2, 'Mother', TRUE),   -- Deepa Singh -> Priya
(14, 5, 'Father', TRUE);   -- Vijay Menon -> Rohan

-- ============================================================
-- 5. SAMPLE ASSESSMENTS (for ML training/testing)
-- ============================================================

-- Child 1 (Aarav) - Cycle 1 (Low Risk Profile)
INSERT INTO assessments (child_id, assessment_cycle, assessment_date, age_months,
    gross_motor_dq, fine_motor_dq, language_dq, cognitive_dq, socio_emotional_dq, composite_dq,
    gross_motor_delay, fine_motor_delay, language_delay, cognitive_delay, socio_emotional_delay, delayed_domains,
    autism_screen_flag, adhd_risk, behavior_risk, attention_score, behavior_score,
    stunting, wasting, anemia, nutrition_score,
    stimulation_score, caregiver_engagement_score, language_exposure_score, parent_child_interaction_score,
    assessed_by) VALUES
(1, 1, '2023-07-15', 28,
    92.5, 88.0, 85.0, 90.0, 87.5, 88.6,
    FALSE, FALSE, FALSE, FALSE, FALSE, 0,
    FALSE, FALSE, FALSE, 85.0, 20.0,
    FALSE, FALSE, FALSE, 92.0,
    88.0, 90.0, 85.0, 88.0,
    8);

-- Child 1 (Aarav) - Cycle 2 (Stable)
INSERT INTO assessments (child_id, assessment_cycle, assessment_date, age_months,
    gross_motor_dq, fine_motor_dq, language_dq, cognitive_dq, socio_emotional_dq, composite_dq,
    gross_motor_delay, fine_motor_delay, language_delay, cognitive_delay, socio_emotional_delay, delayed_domains,
    autism_screen_flag, adhd_risk, behavior_risk, attention_score, behavior_score,
    stunting, wasting, anemia, nutrition_score,
    stimulation_score, caregiver_engagement_score, language_exposure_score, parent_child_interaction_score,
    assessed_by) VALUES
(1, 2, '2024-01-15', 34,
    94.0, 90.0, 88.0, 92.0, 89.0, 90.6,
    FALSE, FALSE, FALSE, FALSE, FALSE, 0,
    FALSE, FALSE, FALSE, 88.0, 18.0,
    FALSE, FALSE, FALSE, 94.0,
    90.0, 92.0, 87.0, 90.0,
    8);

-- Child 2 (Priya) - Cycle 1 (High Risk Profile)
INSERT INTO assessments (child_id, assessment_cycle, assessment_date, age_months,
    gross_motor_dq, fine_motor_dq, language_dq, cognitive_dq, socio_emotional_dq, composite_dq,
    gross_motor_delay, fine_motor_delay, language_delay, cognitive_delay, socio_emotional_delay, delayed_domains,
    autism_screen_flag, adhd_risk, behavior_risk, attention_score, behavior_score,
    stunting, wasting, anemia, nutrition_score,
    stimulation_score, caregiver_engagement_score, language_exposure_score, parent_child_interaction_score,
    assessed_by) VALUES
(2, 1, '2023-08-20', 26,
    68.0, 65.0, 55.0, 62.0, 48.0, 59.6,
    TRUE, TRUE, TRUE, TRUE, TRUE, 5,
    TRUE, FALSE, TRUE, 45.0, 78.0,
    FALSE, FALSE, TRUE, 62.0,
    55.0, 60.0, 50.0, 55.0,
    8);

-- Child 2 (Priya) - Cycle 2 (Slight deterioration)
INSERT INTO assessments (child_id, assessment_cycle, assessment_date, age_months,
    gross_motor_dq, fine_motor_dq, language_dq, cognitive_dq, socio_emotional_dq, composite_dq,
    gross_motor_delay, fine_motor_delay, language_delay, cognitive_delay, socio_emotional_delay, delayed_domains,
    autism_screen_flag, adhd_risk, behavior_risk, attention_score, behavior_score,
    stunting, wasting, anemia, nutrition_score,
    stimulation_score, caregiver_engagement_score, language_exposure_score, parent_child_interaction_score,
    assessed_by) VALUES
(2, 2, '2024-02-20', 32,
    70.0, 67.0, 52.0, 60.0, 45.0, 58.8,
    TRUE, TRUE, TRUE, TRUE, TRUE, 5,
    TRUE, TRUE, TRUE, 42.0, 82.0,
    FALSE, FALSE, TRUE, 60.0,
    53.0, 58.0, 48.0, 52.0,
    8);

-- Child 3 (Arjun) - Cycle 1 (Moderate Risk Profile)
INSERT INTO assessments (child_id, assessment_cycle, assessment_date, age_months,
    gross_motor_dq, fine_motor_dq, language_dq, cognitive_dq, socio_emotional_dq, composite_dq,
    gross_motor_delay, fine_motor_delay, language_delay, cognitive_delay, socio_emotional_delay, delayed_domains,
    autism_screen_flag, adhd_risk, behavior_risk, attention_score, behavior_score,
    stunting, wasting, anemia, nutrition_score,
    stimulation_score, caregiver_engagement_score, language_exposure_score, parent_child_interaction_score,
    assessed_by) VALUES
(3, 1, '2023-09-10', 34,
    78.0, 75.0, 68.0, 72.0, 65.0, 71.6,
    TRUE, TRUE, TRUE, FALSE, TRUE, 4,
    FALSE, FALSE, FALSE, 70.0, 45.0,
    FALSE, TRUE, FALSE, 75.0,
    72.0, 75.0, 68.0, 70.0,
    9);

-- Child 4 (Ananya) - Cycle 1 (Low Risk)
INSERT INTO assessments (child_id, assessment_cycle, assessment_date, age_months,
    gross_motor_dq, fine_motor_dq, language_dq, cognitive_dq, socio_emotional_dq, composite_dq,
    gross_motor_delay, fine_motor_delay, language_delay, cognitive_delay, socio_emotional_delay, delayed_domains,
    autism_screen_flag, adhd_risk, behavior_risk, attention_score, behavior_score,
    stunting, wasting, anemia, nutrition_score,
    stimulation_score, caregiver_engagement_score, language_exposure_score, parent_child_interaction_score,
    assessed_by) VALUES
(4, 1, '2023-09-15', 25,
    95.0, 92.0, 90.0, 93.0, 91.0, 92.2,
    FALSE, FALSE, FALSE, FALSE, FALSE, 0,
    FALSE, FALSE, FALSE, 90.0, 15.0,
    FALSE, FALSE, FALSE, 95.0,
    92.0, 94.0, 90.0, 92.0,
    10);

-- Child 5 (Rohan) - Cycle 1 (High Risk - Social-Emotional Specific)
INSERT INTO assessments (child_id, assessment_cycle, assessment_date, age_months,
    gross_motor_dq, fine_motor_dq, language_dq, cognitive_dq, socio_emotional_dq, composite_dq,
    gross_motor_delay, fine_motor_delay, language_delay, cognitive_delay, socio_emotional_delay, delayed_domains,
    autism_screen_flag, adhd_risk, behavior_risk, attention_score, behavior_score,
    stunting, wasting, anemia, nutrition_score,
    stimulation_score, caregiver_engagement_score, language_exposure_score, parent_child_interaction_score,
    assessed_by) VALUES
(5, 1, '2023-10-01', 32,
    85.0, 82.0, 60.0, 78.0, 42.0, 69.4,
    FALSE, FALSE, TRUE, FALSE, TRUE, 2,
    TRUE, FALSE, TRUE, 55.0, 85.0,
    FALSE, FALSE, FALSE, 80.0,
    65.0, 68.0, 62.0, 60.0,
    10);

-- ============================================================
-- 6. SAMPLE DISTRICT SUMMARY
-- ============================================================

INSERT INTO district_summary (district_id, report_month, total_children, total_assessments,
    low_risk, moderate_risk, high_risk,
    referral_completion_rate, risk_escalation_rate, improvement_rate,
    active_interventions, completed_interventions,
    average_assessment_delay_days, percentage_on_time_assessments) VALUES
(1, '2024-01-01', 156, 312,
    98, 38, 20,
    72.5, 12.3, 8.5,
    15, 8,
    12.5, 78.0),
(1, '2024-02-01', 158, 324,
    101, 36, 21,
    75.0, 10.8, 9.2,
    16, 10,
    11.0, 82.0);

-- ============================================================
-- END OF SEED DATA
-- ============================================================
