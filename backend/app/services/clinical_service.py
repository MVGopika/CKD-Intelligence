"""
Clinical decision support and guidance service
"""
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)

class ClinicalGuidanceService:
    """Service for generating stage-based clinical guidance"""
    
    @staticmethod
    def get_stage_guidance(ckd_stage: str, egfr: float) -> Dict[str, Any]:
        """
        Generate stage-based guidance
        Returns: dict with clinical_guidance, recommendations, and actions
        """
        
        guidance_map = {
            "1": {
                "title": "CKD Stage 1: Normal or High eGFR",
                "description": "Your kidney function is normal. eGFR ≥ 90",
                "clinical_guidance": (
                    "No kidney damage detected. Maintain healthy lifestyle to prevent kidney disease. "
                    "Continue regular health checkups."
                ),
                "recommendations": [
                    "Manage blood pressure (target: <120/80 mmHg)",
                    "Control blood sugar if diabetic",
                    "Reduce salt intake to <5g per day",
                    "Maintain healthy weight",
                    "Exercise regularly (150 min/week)",
                    "Limit alcohol consumption",
                    "Avoid NSAIDs unless necessary",
                    "Repeat kidney function tests annually"
                ],
                "urgency": "low",
                "follow_up_interval_months": 12,
                "risk_category": "minimal"
            },
            "2": {
                "title": "CKD Stage 2: Mildly Decreased eGFR",
                "description": "Mild reduction in kidney function. eGFR 60-89",
                "clinical_guidance": (
                    "Minor kidney damage detected. Monitor kidney function regularly. "
                    "Implement preventive measures to slow progression."
                ),
                "recommendations": [
                    "Monitor blood pressure closely",
                    "Reduce sodium intake to <2.3g per day",
                    "Maintain stable blood glucose",
                    "Avoid NSAIDs and contrast agents",
                    "Moderate protein intake",
                    "Regular exercise (150 min/week)",
                    "Healthy diet (Mediterranean or DASH)",
                    "Repeat kidney function tests every 6-12 months",
                    "Consider referral to nephrologist if risk factors present"
                ],
                "urgency": "low",
                "follow_up_interval_months": 6,
                "risk_category": "low"
            },
            "3": {
                "title": "CKD Stage 3: Moderately Decreased eGFR",
                "description": "Moderate reduction in kidney function. eGFR 30-59",
                "clinical_guidance": (
                    "Moderate kidney damage detected. Close monitoring and management are essential. "
                    "See your doctor regularly to slow disease progression and prevent complications."
                ),
                "recommendations": [
                    "Consult with a nephrologist for specialized care",
                    "Monitor blood pressure (target: <120/80 mmHg)",
                    "Strict sodium restriction (<2g per day)",
                    "Restrict protein intake (0.6-0.8g/kg body weight)",
                    "Monitor and manage anemia if present",
                    "Screen for bone disease",
                    "Avoid NSAIDs and nephrotoxic drugs",
                    "Monitor potassium and phosphorus levels",
                    "Kidney function tests every 3-6 months",
                    "Consider ACE inhibitor/ARB therapy if hypertensive or diabetic"
                ],
                "urgency": "moderate",
                "follow_up_interval_months": 3,
                "risk_category": "moderate"
            },
            "4": {
                "title": "CKD Stage 4: Severely Decreased eGFR",
                "description": "Severe reduction in kidney function. eGFR 15-29",
                "clinical_guidance": (
                    "Severe kidney damage requires intensive management. "
                    "Plan for renal replacement therapy and see your nephrologist frequently."
                ),
                "recommendations": [
                    "Regular nephrologist visits (monthly or as needed)",
                    "Prepare for dialysis or transplant",
                    "Strict dietary management (low sodium, potassium, phosphorus, protein)",
                    "Fluid restriction may be necessary",
                    "Manage bone disease and anemia proactively",
                    "Vaccinations (influenza, pneumococcal, hepatitis B)",
                    "Cardiovascular risk assessment and management",
                    "Monthly kidney function tests",
                    "Avoid contrast media; use alternatives when possible",
                    "Begin vascular access planning if appropriate"
                ],
                "urgency": "high",
                "follow_up_interval_months": 1,
                "risk_category": "high"
            },
            "5": {
                "title": "CKD Stage 5: Kidney Failure",
                "description": "Kidney failure requiring renal replacement therapy. eGFR <15",
                "clinical_guidance": (
                    "End-stage renal disease (ESRD) has been reached. "
                    "Immediate medical attention required. Start renal replacement therapy urgently."
                ),
                "recommendations": [
                    "URGENT: Contact nephrologist or emergency room immediately",
                    "Initiate dialysis (hemodialysis or peritoneal) or pursue transplant",
                    "Weekly or bi-weekly nephrologist visits",
                    "Strict dietary restrictions (low sodium, potassium, phosphorus, fluid, protein)",
                    "Manage complications: hypertension, anemia, bone disease, cardiovascular disease",
                    "Mental health support and patient education",
                    "Manage medications carefully (many are contraindicated)",
                    "Coordinate care with dialysis team",
                    "Explore kidney transplant options",
                    "Palliative care consultation if appropriate"
                ],
                "urgency": "critical",
                "follow_up_interval_months": 0,  # continuous monitoring
                "risk_category": "critical"
            }
        }
        
        return guidance_map.get(ckd_stage, guidance_map["3"])
    
    @staticmethod
    def get_lifestyle_recommendations(ckd_stage: str, risk_factors: List[str] = None) -> Dict[str, Any]:
        """
        Generate personalized lifestyle recommendations
        """
        base_recommendations = {
            "diet": {
                "1": "No restrictions needed. Maintain balanced, healthy diet.",
                "2": "Reduce salt to <5g/day. Moderate protein intake.",
                "3": "Low sodium (<2.3g/day), moderate protein (0.8g/kg/day).",
                "4": "Very low sodium, protein, potassium, phosphorus.",
                "5": "Strict dietary management required. Follow dietitian's plan closely."
            },
            "exercise": {
                "1": "150 minutes moderate activity per week (e.g., brisk walking, swimming).",
                "2": "150 minutes moderate activity per week. Avoid strenuous exercise if hypertensive.",
                "3": "100-150 minutes moderate activity per week. Gradual progression.",
                "4": "Light to moderate activity as tolerated. Consult doctor before exercising.",
                "5": "Activities adapted to tolerance. May need oxygen support during exercise."
            },
            "fluid": {
                "1": "No restriction. Drink adequate fluids daily.",
                "2": "No restriction. Stay well hydrated.",
                "3": "Maintain normal hydration. Monitor if hypertensive.",
                "4": "Fluid restriction may apply. Follow doctor's guidance.",
                "5": "Strict fluid restriction typically necessary. Daily limit set by nephrologist."
            },
            "medications": {
                "1": "Take prescribed medications as directed. Avoid over-the-counter NSAIDs.",
                "2": "Continue regular medications. Avoid NSAIDs and unnecessary supplements.",
                "3": "Careful medication management. Avoid NSAIDs, certain antibiotics. ACE/ARB recommended.",
                "4": "Very careful medication selection. Avoid nephrotoxic drugs. Adjust doses based on eGFR.",
                "5": "Strict medication protocol. Most drugs need dose adjustment. Follow prescriptions exactly."
            }
        }
        
        return {
            "diet": base_recommendations["diet"].get(ckd_stage, base_recommendations["diet"]["3"]),
            "exercise": base_recommendations["exercise"].get(ckd_stage, base_recommendations["exercise"]["3"]),
            "fluid": base_recommendations["fluid"].get(ckd_stage, base_recommendations["fluid"]["3"]),
            "medications": base_recommendations["medications"].get(ckd_stage, base_recommendations["medications"]["3"]),
            "monitoring": f"Follow-up kidney function tests every {ClinicalGuidanceService.get_stage_guidance(ckd_stage, 50)['follow_up_interval_months'] or 1} month(s)"
        }
    
    @staticmethod
    def get_alert_status(ckd_stage: str, egfr: float) -> Dict[str, Any]:
        """
        Determine alert status and urgency level
        """
        alert_map = {
            "1": {"level": "none", "color": "green", "alert": None},
            "2": {"level": "info", "color": "blue", "alert": "Regular monitoring recommended"},
            "3": {"level": "warning", "color": "yellow", "alert": "Schedule doctor visit soon"},
            "4": {"level": "danger", "color": "orange", "alert": "Contact doctor urgently"},
            "5": {"level": "critical", "color": "red", "alert": "⚠️ CRITICAL: Seek immediate medical attention"}
        }
        
        return alert_map.get(ckd_stage, alert_map["3"])
