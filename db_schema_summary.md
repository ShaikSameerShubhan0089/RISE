### Table: anganwadi_centers

| Column | Type | Nullable | Default | PK | FK |
| --- | --- | --- | --- | --- | --- |
| center_id | INTEGER | False | None | Yes |  |
| mandal_id | INTEGER | False | None |  | mandals(mandal_id) |
| center_code | VARCHAR(50) | False | None |  |  |
| center_name | VARCHAR(150) | False | None |  |  |
| address | TEXT | True | None |  |  |
| contact_number | VARCHAR(20) | True | None |  |  |
| created_at | TIMESTAMP | True | CURRENT_TIMESTAMP |  |  |


### Table: assessments

| Column | Type | Nullable | Default | PK | FK |
| --- | --- | --- | --- | --- | --- |
| assessment_id | INTEGER | False | None | Yes |  |
| child_id | INTEGER | False | None |  | children(child_id) |
| assessment_cycle | INTEGER | False | None |  |  |
| assessment_date | DATE | False | None |  |  |
| age_months | INTEGER | True | None |  |  |
| gross_motor_dq | FLOAT | True | None |  |  |
| fine_motor_dq | FLOAT | True | None |  |  |
| language_dq | FLOAT | True | None |  |  |
| cognitive_dq | FLOAT | True | None |  |  |
| socio_emotional_dq | FLOAT | True | None |  |  |
| composite_dq | FLOAT | True | None |  |  |
| gross_motor_delay | TINYINT | True | '0' |  |  |
| fine_motor_delay | TINYINT | True | '0' |  |  |
| language_delay | TINYINT | True | '0' |  |  |
| cognitive_delay | TINYINT | True | '0' |  |  |
| socio_emotional_delay | TINYINT | True | '0' |  |  |
| delayed_domains | INTEGER | True | None |  |  |
| autism_screen_flag | TINYINT | True | None |  |  |
| adhd_risk | TINYINT | True | None |  |  |
| behavior_risk | TINYINT | True | None |  |  |
| attention_score | FLOAT | True | None |  |  |
| behavior_score | FLOAT | True | None |  |  |
| stunting | TINYINT | True | None |  |  |
| wasting | TINYINT | True | None |  |  |
| anemia | TINYINT | True | None |  |  |
| nutrition_score | FLOAT | True | None |  |  |
| stimulation_score | FLOAT | True | None |  |  |
| caregiver_engagement_score | FLOAT | True | None |  |  |
| language_exposure_score | FLOAT | True | None |  |  |
| parent_child_interaction_score | FLOAT | True | None |  |  |
| assessed_by | INTEGER | True | None |  | users(user_id) |
| notes | TEXT | True | None |  |  |
| created_at | TIMESTAMP | True | CURRENT_TIMESTAMP |  |  |


### Table: audit_logs

| Column | Type | Nullable | Default | PK | FK |
| --- | --- | --- | --- | --- | --- |
| log_id | INTEGER | False | None | Yes |  |
| user_id | INTEGER | True | None |  | users(user_id) |
| action | VARCHAR(200) | False | None |  |  |
| entity_type | VARCHAR(100) | True | None |  |  |
| entity_id | INTEGER | True | None |  |  |
| request_method | VARCHAR(10) | True | None |  |  |
| request_path | VARCHAR(500) | True | None |  |  |
| request_body | TEXT | True | None |  |  |
| response_status | INTEGER | True | None |  |  |
| ip_address | VARCHAR(50) | True | None |  |  |
| user_agent | TEXT | True | None |  |  |
| timestamp | DATETIME | True | None |  |  |


### Table: children

| Column | Type | Nullable | Default | PK | FK |
| --- | --- | --- | --- | --- | --- |
| child_id | INTEGER | False | None | Yes |  |
| unique_child_code | VARCHAR(100) | False | None |  |  |
| first_name | VARCHAR(100) | False | None |  |  |
| last_name | VARCHAR(100) | True | None |  |  |
| dob | DATE | False | None |  |  |
| gender | VARCHAR(20) | True | None |  |  |
| center_id | INTEGER | False | None |  | anganwadi_centers(center_id) |
| caregiver_name | VARCHAR(150) | True | None |  |  |
| caregiver_relationship | VARCHAR(50) | True | None |  |  |
| caregiver_education | VARCHAR(100) | True | None |  |  |
| caregiver_phone | VARCHAR(20) | True | None |  |  |
| caregiver_email | VARCHAR(150) | True | None |  |  |
| caregiver_additional_info | TEXT | True | None |  |  |
| enrollment_date | DATE | True | (curdate()) |  |  |
| status | VARCHAR(50) | True | 'Active' |  |  |
| created_at | TIMESTAMP | True | CURRENT_TIMESTAMP |  |  |
| updated_at | TIMESTAMP | True | CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP |  |  |


### Table: district_summary

| Column | Type | Nullable | Default | PK | FK |
| --- | --- | --- | --- | --- | --- |
| summary_id | INTEGER | False | None | Yes |  |
| district_id | INTEGER | False | None |  | districts(district_id) |
| report_month | DATE | False | None |  |  |
| total_children | INTEGER | True | None |  |  |
| total_assessments | INTEGER | True | None |  |  |
| low_risk | INTEGER | True | None |  |  |
| moderate_risk | INTEGER | True | None |  |  |
| high_risk | INTEGER | True | None |  |  |
| referral_completion_rate | FLOAT | True | None |  |  |
| risk_escalation_rate | FLOAT | True | None |  |  |
| improvement_rate | FLOAT | True | None |  |  |
| active_interventions | INTEGER | True | None |  |  |
| completed_interventions | INTEGER | True | None |  |  |
| average_assessment_delay_days | FLOAT | True | None |  |  |
| percentage_on_time_assessments | FLOAT | True | None |  |  |
| created_at | DATETIME | True | None |  |  |


### Table: districts

| Column | Type | Nullable | Default | PK | FK |
| --- | --- | --- | --- | --- | --- |
| district_id | INTEGER | False | None | Yes |  |
| state_id | INTEGER | False | None |  | states(state_id) |
| district_name | VARCHAR(150) | False | None |  |  |
| created_at | TIMESTAMP | True | CURRENT_TIMESTAMP |  |  |


### Table: engineered_features

| Column | Type | Nullable | Default | PK | FK |
| --- | --- | --- | --- | --- | --- |
| feature_id | INTEGER | False | None | Yes |  |
| assessment_id | INTEGER | False | None |  | assessments(assessment_id) |
| social_communication_impairment_index | FLOAT | True | None |  |  |
| neurodevelopmental_severity_index | FLOAT | True | None |  |  |
| environmental_risk_modifier | FLOAT | True | None |  |  |
| delay_burden_score | FLOAT | True | None |  |  |
| dq_delta | FLOAT | True | None |  |  |
| behavior_delta | FLOAT | True | None |  |  |
| socio_emotional_delta | FLOAT | True | None |  |  |
| environmental_delta | FLOAT | True | None |  |  |
| delay_delta | INTEGER | True | None |  |  |
| nutrition_delta | FLOAT | True | None |  |  |
| days_since_last_assessment | INTEGER | True | None |  |  |
| created_at | TIMESTAMP | True | CURRENT_TIMESTAMP |  |  |


### Table: interventions

| Column | Type | Nullable | Default | PK | FK |
| --- | --- | --- | --- | --- | --- |
| intervention_id | INTEGER | False | None | Yes |  |
| child_id | INTEGER | False | None |  | children(child_id) |
| referral_id | INTEGER | True | None |  | referrals(referral_id) |
| intervention_type | VARCHAR(200) | False | None |  |  |
| intervention_category | VARCHAR(100) | True | None |  |  |
| intervention_description | TEXT | True | None |  |  |
| start_date | DATE | False | None |  |  |
| end_date | DATE | True | None |  |  |
| planned_duration_weeks | INTEGER | True | None |  |  |
| actual_duration_weeks | INTEGER | True | None |  |  |
| total_sessions_planned | INTEGER | True | None |  |  |
| sessions_completed | INTEGER | True | '0' |  |  |
| compliance_percentage | FLOAT | True | None |  |  |
| improvement_status | VARCHAR(100) | True | None |  |  |
| delay_reduction_months | FLOAT | True | None |  |  |
| outcome_notes | TEXT | True | None |  |  |
| provider_name | VARCHAR(150) | True | None |  |  |
| provider_contact | VARCHAR(50) | True | None |  |  |
| created_by | INTEGER | True | None |  | users(user_id) |
| created_at | TIMESTAMP | True | CURRENT_TIMESTAMP |  |  |
| updated_at | TIMESTAMP | True | CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP |  |  |


### Table: mandals

| Column | Type | Nullable | Default | PK | FK |
| --- | --- | --- | --- | --- | --- |
| mandal_id | INTEGER | False | None | Yes |  |
| district_id | INTEGER | False | None |  | districts(district_id) |
| mandal_name | VARCHAR(150) | False | None |  |  |
| created_at | TIMESTAMP | True | CURRENT_TIMESTAMP |  |  |


### Table: model_predictions

| Column | Type | Nullable | Default | PK | FK |
| --- | --- | --- | --- | --- | --- |
| prediction_id | INTEGER | False | None | Yes |  |
| assessment_id | INTEGER | False | None |  | assessments(assessment_id) |
| model_version | VARCHAR(50) | False | None |  |  |
| prediction_timestamp | TIMESTAMP | True | CURRENT_TIMESTAMP |  |  |
| low_probability | FLOAT | True | None |  |  |
| moderate_probability | FLOAT | True | None |  |  |
| high_probability | FLOAT | True | None |  |  |
| predicted_risk_class | VARCHAR(50) | True | None |  |  |
| combined_high_probability | FLOAT | True | None |  |  |
| risk_tier | VARCHAR(50) | True | None |  |  |
| clinical_action | VARCHAR(200) | True | None |  |  |
| escalation_probability | FLOAT | True | None |  |  |
| predicted_escalation | TINYINT | True | None |  |  |
| model_confidence | FLOAT | True | None |  |  |
| calibration_applied | TINYINT | True | '1' |  |  |
| created_at | TIMESTAMP | True | CURRENT_TIMESTAMP |  |  |


### Table: parent_child_mapping

| Column | Type | Nullable | Default | PK | FK |
| --- | --- | --- | --- | --- | --- |
| mapping_id | INTEGER | False | None | Yes |  |
| user_id | INTEGER | False | None |  | users(user_id) |
| child_id | INTEGER | False | None |  | children(child_id) |
| relationship_type | VARCHAR(50) | True | None |  |  |
| is_primary_contact | TINYINT | True | None |  |  |
| created_at | DATETIME | True | None |  |  |


### Table: referrals

| Column | Type | Nullable | Default | PK | FK |
| --- | --- | --- | --- | --- | --- |
| referral_id | INTEGER | False | None | Yes |  |
| assessment_id | INTEGER | False | None |  | assessments(assessment_id) |
| child_id | INTEGER | False | None |  | children(child_id) |
| risk_level_at_referral | VARCHAR(50) | True | None |  |  |
| referral_reason | TEXT | True | None |  |  |
| referral_generated | TINYINT | True | '0' |  |  |
| auto_generated | TINYINT | True | '0' |  |  |
| referral_date | DATE | True | (curdate()) |  |  |
| expected_completion_date | DATE | True | None |  |  |
| completion_date | DATE | True | None |  |  |
| referred_to | VARCHAR(200) | True | None |  |  |
| specialist_type | VARCHAR(100) | True | None |  |  |
| facility_name | VARCHAR(200) | True | None |  |  |
| facility_contact | VARCHAR(50) | True | None |  |  |
| status | VARCHAR(100) | True | 'Pending' |  |  |
| referral_completed | TINYINT | True | '0' |  |  |
| outcome_summary | TEXT | True | None |  |  |
| diagnosis_received | VARCHAR(200) | True | None |  |  |
| created_by | INTEGER | True | None |  | users(user_id) |
| updated_by | INTEGER | True | None |  | users(user_id) |
| created_at | TIMESTAMP | True | CURRENT_TIMESTAMP |  |  |
| updated_at | TIMESTAMP | True | CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP |  |  |


### Table: shap_explanations

| Column | Type | Nullable | Default | PK | FK |
| --- | --- | --- | --- | --- | --- |
| shap_id | INTEGER | False | None | Yes |  |
| prediction_id | INTEGER | False | None |  | model_predictions(prediction_id) |
| feature_name | VARCHAR(150) | False | None |  |  |
| feature_value | FLOAT | True | None |  |  |
| shap_value | FLOAT | False | None |  |  |
| contribution_rank | INTEGER | True | None |  |  |
| interpretation | TEXT | True | None |  |  |
| impact_direction | VARCHAR(20) | True | None |  |  |
| created_at | DATETIME | True | None |  |  |


### Table: states

| Column | Type | Nullable | Default | PK | FK |
| --- | --- | --- | --- | --- | --- |
| state_id | INTEGER | False | None | Yes |  |
| state_name | VARCHAR(150) | False | None |  |  |
| created_at | TIMESTAMP | True | CURRENT_TIMESTAMP |  |  |


### Table: users

| Column | Type | Nullable | Default | PK | FK |
| --- | --- | --- | --- | --- | --- |
| user_id | INTEGER | False | None | Yes |  |
| full_name | VARCHAR(150) | False | None |  |  |
| email | VARCHAR(150) | False | None |  |  |
| password_hash | VARCHAR(255) | False | None |  |  |
| role | VARCHAR(100) | False | None |  |  |
| state_id | INTEGER | True | None |  | states(state_id) |
| district_id | INTEGER | True | None |  | districts(district_id) |
| mandal_id | INTEGER | True | None |  | mandals(mandal_id) |
| center_id | INTEGER | True | None |  | anganwadi_centers(center_id) |
| status | VARCHAR(50) | True | 'Active' |  |  |
| email_verified | TINYINT | True | '0' |  |  |
| last_login | TIMESTAMP | True | None |  |  |
| created_at | TIMESTAMP | True | CURRENT_TIMESTAMP |  |  |
| updated_at | TIMESTAMP | True | CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP |  |  |

