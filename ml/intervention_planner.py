"""
Personalized Intervention Engine
Translates SHAP-based AI insights into localized, practical intervention pathways
for caregivers and AWC workers (Problem B).
"""

from typing import Dict, List, Optional
import pandas as pd


class InterventionPlanner:
    """
    Logic engine to generate individualized intervention pathways based on
    AI risk stratification and SHAP contribution values.
    """

    def __init__(self):

        # ---------------- LANGUAGE MAP ----------------
        self.lang_map = {
            'telugu': 'te', 'te': 'te',
            'hindi': 'hi', 'hi': 'hi',
            'kannada': 'kn', 'kn': 'kn',
            'urdu': 'ur', 'ur': 'ur',
            'tamil': 'ta', 'ta': 'ta',
            'english': 'en', 'en': 'en'
        }

        # ---------------- FEATURE → CATEGORY ----------------
        self.category_mapping = {
            'language_dq': 'Speech Therapy',
            'fine_motor_dq': 'Occupational Therapy',
            'gross_motor_dq': 'Early Intervention',
            'socio_emotional_dq': 'Behavioral Therapy',
            'scii': 'Social Communication Training',
            'behavior_score': 'Behavioral Therapy',
            'nutrition_score': 'Nutritional Support',
            'caregiver_engagement_score': 'Parental Training',
            'stunting': 'Nutritional Support',
            'wasting': 'Nutritional Support',
            'anemia': 'Nutritional Support'
        }

        # ---------------- LOAD TRANSLATIONS ----------------
        import json
        from pathlib import Path

        translations_path = Path(__file__).parent.parent / "shared" / "translations.json"

        try:
            with open(translations_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = {}

        self.translation_map = data.get("translation_map", {})
        self.feature_translations = data.get("feature_translations", {})
        self.localized_content = data.get("localized_content", {})

        # ---------------- SAFETY DEFAULTS (CRITICAL FIX) ----------------
        # Guarantees system NEVER crashes due to missing translations
        self.translation_map.setdefault("en", {})
        self.feature_translations.setdefault("en", {})
        self.localized_content.setdefault("en", {})

    # ============================================================
    # INTERNAL HELPER
    # ============================================================

    def _resolve_lang(self, lang: str):
        """Safely resolve language with English fallback."""
        target_lang = self.lang_map.get((lang or "en").lower(), "en")

        uimap = self.translation_map.get(target_lang) or self.translation_map["en"]
        content = self.localized_content.get(target_lang) or self.localized_content["en"]
        featmap = self.feature_translations.get(target_lang) or self.feature_translations["en"]

        return target_lang, uimap, content, featmap

    # ============================================================
    # PATHWAY GENERATION
    # ============================================================

    def generate_pathway(self, shap_explanations: List[Dict], lang: str = "en") -> List[Dict]:

        recommendations = []

        sorted_features = sorted(
            [f for f in shap_explanations if f["shap_value"] > 0],
            key=lambda x: x["shap_value"],
            reverse=True,
        )

        _, uimap, content, _ = self._resolve_lang(lang)

        seen_categories = set()

        for feature in sorted_features:
            feature_name = feature["feature_name"]
            category = self.category_mapping.get(feature_name)

            if category and category not in seen_categories:

                category_content = content.get(category, {})

                priority_key = "High" if len(recommendations) < 2 else "Moderate"

                recommendations.append({
                    "category": uimap.get(category, category),
                    "priority": uimap.get(priority_key, priority_key),
                    "objective": category_content.get(
                        "objective", "Support growth."
                    ),
                    "daily_steps": category_content.get("daily_steps", []),
                    "parent_guide": category_content.get(
                        "parent_guide", "Consult expert."
                    ),
                    "ui_labels": {
                        "objective": uimap.get("objective", "Objective"),
                        "daily_steps": uimap.get("daily_steps", "Daily Steps"),
                        "parent_guide": uimap.get("parent_guide", "Parent Guide"),
                        "priority_label": uimap.get("priority", "Priority"),
                    },
                    "triggered_by": feature_name,
                    "impact_score": round(feature["shap_value"], 4),
                })

                seen_categories.add(category)

        # Default fallback recommendation
        if not recommendations:
            cat_content = content.get("Parental Training", {})
            recommendations.append({
                "category": "Parental Training",
                "priority": "Low",
                "objective": cat_content.get("objective", "Support development."),
                "daily_steps": cat_content.get("daily_steps", []),
                "parent_guide": cat_content.get("parent_guide", ""),
                "triggered_by": "General Assessment",
                "impact_score": 0.0,
            })

        return recommendations

    # ============================================================
    # CLINICAL SUMMARY
    # ============================================================

    def get_clinical_summary(self, risk_tier: str, probability: float, lang: str = "en") -> str:

        target_lang, uimap, _, _ = self._resolve_lang(lang)

        localized_tier = uimap.get(risk_tier, risk_tier)

        summaries = {
            "en": f"Risk Assessment: {localized_tier} ({probability*100:.1f}% confidence). Primary intervention focus identified below.",
            "te": f"రిస్క్ అసెస్మెంట్: {localized_tier} ({probability*100:.1f}% ఖచ్చితత్వం).",
            "hi": f"जोखिम मूल्यांकन: {localized_tier} ({probability*100:.1f}% निश्चितता)।",
            "kn": f"ಜೋಖಮು ಮೌಲ್ಯಮಾಪನ: {localized_tier} ({probability*100:.1f}% ಖಚಿತತೆ).",
            "ur": f"رسک اسسمنٹ: {localized_tier} ({probability*100:.1f}% یقین).",
            "ta": f"ஆபத்து மதிப்பீடு: {localized_tier} ({probability*100:.1f}% உறுதி).",
        }

        return summaries.get(target_lang, summaries["en"])

    # ============================================================
    # PREDICTION LOCALIZATION
    # ============================================================

    def localize_prediction(self, prediction: Dict, lang: str = "en") -> Dict:

        if not prediction:
            return prediction

        _, uimap, _, featmap = self._resolve_lang(lang)

        prediction["risk_tier"] = uimap.get(
            prediction.get("risk_tier"), prediction.get("risk_tier")
        )

        if "top_features" in prediction:
            for feat in prediction["top_features"]:
                fname = feat.get("feature_name", "")

                localized_fname = featmap.get(
                    fname, fname.replace("_", " ").title()
                )

                feat["interpretation"] = uimap.get(
                    "impact_of", "Impact of {feature}"
                ).format(feature=localized_fname)

                feat["impact_direction"] = uimap.get(
                    feat.get("impact_direction"),
                    feat.get("impact_direction"),
                )

        prediction["escalation_description"] = uimap.get(
            "escalation_desc",
            "Likelihood of escalating risk."
        )

        return prediction

    # ============================================================
    # SIMPLE VALUE LOCALIZATION
    # ============================================================

    def localize_value(self, value: Optional[str], lang: str = "en") -> str:

        if not value:
            return ""

        _, uimap, _, _ = self._resolve_lang(lang)

        return uimap.get(value, value)

    def localize_item(self, item: Dict, keys: List[str], lang: str = "en") -> Dict:

        for key in keys:
            if key in item and isinstance(item[key], str):
                item[key] = self.localize_value(item[key], lang)

        return item