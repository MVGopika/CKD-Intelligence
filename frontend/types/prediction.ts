export interface Prediction {
  id: number;
  egfr_predicted: number;
  egfr_confidence: number;
  ckd_stage: string;
  stage_confidence: number;
  risk_level: string;
  clinical_guidance?: string;
  recommendations?: string[];
  shap_values?: Record<string, number>;
  top_contributing_features?: Array<{ feature: string; importance: number }>;
  created_at: string;
}

export interface Consultation {
  id: number;
  input_type: string;
  raw_input?: string;
  transcription?: string;
  structured_data?: any;
  created_at: string;
}
