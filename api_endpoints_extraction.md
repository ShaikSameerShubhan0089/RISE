## Router: assessments.py

| Method | Path | Function | Response Model | RBAC Roles |
| --- | --- | --- | --- | --- |
| POST |  | create_assessment | schemas.AssessmentResponse | anganwadi_worker, supervisor, district_officer, state_admin, system_admin |
| GET | /{assessment_id} | get_assessment | schemas.AssessmentResponse | None |
| GET |  | list_recent_assessments | List[schemas.AssessmentResponse] | anganwadi_worker, supervisor, district_officer, state_admin, system_admin |

## Router: auth.py

| Method | Path | Function | Response Model | RBAC Roles |
| --- | --- | --- | --- | --- |
| POST | /login | login | schemas.Token | None |
| GET | /me | get_current_user_info | schemas.UserResponse | None |
| POST | /users | create_user | schemas.UserResponse | system_admin, state_admin, district_officer, supervisor, anganwadi_worker |
| PUT | /users/{user_id} | update_user | schemas.UserResponse | system_admin, state_admin, district_officer, supervisor, anganwadi_worker |
| GET | /users | list_users | None | system_admin, state_admin, district_officer, supervisor, anganwadi_worker |
| PATCH | /users/{user_id}/status | toggle_user_status | schemas.UserResponse | system_admin, state_admin, district_officer, supervisor, anganwadi_worker |
| POST | /users/{user_id}/reset-password | reset_user_password | None | system_admin, state_admin, district_officer, supervisor, anganwadi_worker |
| DELETE | /users/{user_id} | delete_user | None | system_admin, state_admin, district_officer, supervisor, anganwadi_worker |

## Router: children.py

| Method | Path | Function | Response Model | RBAC Roles |
| --- | --- | --- | --- | --- |
| POST |  | create_child | schemas.ChildResponse | anganwadi_worker, supervisor, district_officer, state_admin, system_admin |
| GET | /{child_id} | get_child | schemas.ChildResponse | None |
| GET |  | list_children | List[schemas.ChildResponse] | None |
| PUT | /{child_id} | update_child | schemas.ChildResponse | anganwadi_worker, supervisor, district_officer, state_admin, system_admin |
| GET | /{child_id}/assessments | get_child_assessments | List[schemas.AssessmentResponse] | None |

## Router: dashboard.py

| Method | Path | Function | Response Model | RBAC Roles |
| --- | --- | --- | --- | --- |
| GET | /districts-for-state | districts_for_state | None | None |
| GET | /districts | list_districts | None | None |
| GET | /mandals | list_mandals | None | None |
| GET | /mandals-for-district | mandals_for_district | None | None |
| GET | /centers-for-mandal | centers_for_mandal | None | None |
| GET | /summary | dashboard_summary | None | None |
| GET | /children | dashboard_children | None | None |
| GET | /interventions | dashboard_interventions | None | None |
| GET | /users | dashboard_users | None | None |
| GET | /charts | dashboard_charts | None | None |
| GET | /child-growth/{child_id} | child_growth | None | None |
| GET | /analytics/summary | analytics_summary | None | None |
| GET | /analytics/users | analytics_users | None | None |
| GET | /analytics/children | analytics_children | None | None |
| GET | /analytics/predictions | analytics_predictions | None | None |

## Router: interventions.py

| Method | Path | Function | Response Model | RBAC Roles |
| --- | --- | --- | --- | --- |
| POST |  | create_intervention | schemas.InterventionResponse | supervisor, district_officer, state_admin, system_admin |
| PUT | /{intervention_id} | update_intervention | schemas.InterventionResponse | supervisor, district_officer, state_admin, system_admin |
| GET | /{intervention_id} | get_intervention | schemas.InterventionResponse | None |
| GET | /child/{child_id} | get_child_interventions | List[schemas.InterventionResponse] | None |
| GET |  | list_interventions | List[schemas.InterventionResponse] | supervisor, district_officer, state_admin, system_admin |

## Router: predictions.py

| Method | Path | Function | Response Model | RBAC Roles |
| --- | --- | --- | --- | --- |
| POST | /run | run_realtime_prediction | schemas.RiskPredictionResponse | None |
| POST | /{assessment_id} | generate_risk_prediction | schemas.RiskPredictionResponse | None |
| GET | /{prediction_id} | get_prediction | schemas.RiskPredictionResponse | None |

## Router: referrals.py

| Method | Path | Function | Response Model | RBAC Roles |
| --- | --- | --- | --- | --- |
| POST |  | create_referral | schemas.ReferralResponse | None |
| PUT | /{referral_id} | update_referral | schemas.ReferralResponse | None |
| GET | /{referral_id} | get_referral | schemas.ReferralResponse | None |
| GET | /child/{child_id} | get_child_referrals | List[schemas.ReferralResponse] | None |
| GET |  | list_referrals | List[schemas.ReferralResponse] | None |

