"use client";

import { useState } from "react";
import { runPrediction } from "../../services/predictionService";
import ClinicalDataInput from "../../components/ui/ClinicalDataInput";
import PredictionResults from "../../components/ui/PredictionResults";
import ShapChart from "../../components/charts/ShapChart";
import { useEffect } from "react";
import { submitLabResults } from "../../services/patientService";
import { toast } from "sonner";

export default function PredictionPage() {
  const [prediction, setPrediction] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [showAlert, setShowAlert] = useState(false);

  useEffect(() => {
    if (!prediction) return;

    const stage = Number(prediction.ckd_stage);
    const risk = prediction.risk_level?.toLowerCase();

    if (stage >= 4 || risk === "high" || risk === "critical") {
      setShowAlert(true);
    }
  }, [prediction]);

  const handleSubmit = async (formData: any) => {
    setLoading(true);
    setError("");
    setPrediction(null);

    try {
      const payload = {
        test_date: new Date().toISOString(),
        age: Number(formData.age),
        sex: formData.sex,
        bmi: Number(formData.bmi),
        serum_creatinine: Number(formData.serumCreatinine),
        cystatin_c: Number(formData.cystatinC) || null,
        hba1c: Number(formData.hba1c),
        blood_pressure_sys: Number(formData.systolicBP),
        blood_pressure_dia: Number(formData.diastolicBP),
        albumin: Number(formData.albumin),
        crp: Number(formData.crp),
      };
      await submitLabResults(payload);
      const response = await runPrediction(payload);
      toast.success("Prediction completed successfully");
      setPrediction(response.data);
    } catch (err: any) {
      setError(
        err.response?.data?.detail || "Prediction failed. Please try again.",
      );
      toast.error("Prediction failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <div
        className={`min-h-screen bg-black text-white px-6 py-12 transition-all duration-300 ${
          showAlert ? "blur-sm pointer-events-none select-none" : ""
        }`}
      >
        <div className="mx-auto">
          {/* HERO */}
          <div className="relative mb-6 rounded-3xl border border-gray-800 bg-gradient-to-br from-gray-950 via-black to-gray-950 p-12 shadow-[0_0_80px_rgba(59,130,246,0.08)] overflow-hidden">
            <div className="absolute -top-32 -left-32 h-[400px] w-[400px] bg-blue-500/10 rounded-full blur-3xl" />
            <div className="absolute -bottom-32 -right-32 h-[400px] w-[400px] bg-purple-500/10 rounded-full blur-3xl" />

            <div className="relative z-10">
              <h1 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-blue-400 to-cyan-300 bg-clip-text">
                🔬 AI-Powered CKD Risk Prediction Engine
              </h1>

              <p className="mt-6 text-gray-400 text-lg max-w-3xl leading-relaxed">
                Real-time Chronic Kidney Disease detection using Hybrid GWO-SVR
                + XGBoost ensemble modeling. Enter patient clinical parameters
                to estimate eGFR, CKD stage, and personalized risk insights
                instantly.
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-12">
            <div className="lg:col-span-2 rounded-2xl border border-gray-800 bg-black backdrop-blur-xl p-2 shadow-xl">
                 <div className="flex justify-end mb-6">
                {prediction && (
                  <button
                    onClick={() => {
                      setPrediction(null);
                      setError("");
                      setShowAlert(false);
                      toast.success("Ready for new prediction");
                    }}
                    className="bg-blue-600 hover:bg-blue-700 transition text-white px-6 py-2 rounded-xl font-semibold"
                  >
                    Reset Prediction
                  </button>
                )}
              </div>
              <ClinicalDataInput onSubmit={handleSubmit} />

              {error && (
                <div className="mt-6 bg-red-500/10 border border-red-500/30 rounded-xl p-4">
                  <p className="text-red-400">{error}</p>
                </div>
              )}
            </div>
            {/* <div className="rounded-3xl border border-white/10 bg-gradient-to-br from-neutral-950 via-black to-neutral-950 p-10 shadow-[0_0_60px_rgba(59,130,246,0.08)]">
           
              <h2 className="text-2xl font-semibold text-cyan-400 mb-6">
                Stage-wise CKD Prediction
              </h2>

              {!prediction && (
                <div className="text-gray-400 space-y-3">
                  <p className="text-lg">
                    No prediction generated yet. Enter the patient’s clinical
                    data above to run the CKD risk assessment.
                  </p>
                  <p className="text-sm text-gray-500">
                    Make sure all mandatory lab values and vitals are provided
                    for an accurate stage-wise prediction.
                  </p>
                </div>
              )}
            </div> */}
            {prediction && (
              <div className="space-y-8">
                <div className="rounded-3xl border border-gray-800 shadow-xl">
                  <PredictionResults result={prediction} />
                </div>

                {/* {prediction.top_contributing_features && (
                  <div className="rounded-3xl border border-gray-800 bg-black backdrop-blur-xl p-8 shadow-xl">
                    <h3 className="text-xl font-semibold mb-6 text-blue-400">
                      Feature Contribution Analysis (SHAP)
                    </h3>
                    <ShapChart
                      features={prediction.top_contributing_features}
                    />
                  </div>
                )} */}
              </div>
            )}
          </div>

          {/* RECOMMENDATIONS */}
          {prediction?.recommendations && (
            <div className="mt-10 rounded-3xl border border-gray-800 bg-black backdrop-blur-xl p-10 shadow-xl">
              <h2 className="text-2xl font-semibold mb-6 text-cyan-400">
                Clinical Recommendations
              </h2>

              <p className="text-gray-400 mb-6">
                {prediction.clinical_guidance}
              </p>

              <ul className="space-y-4">
                {prediction.recommendations.map(
                  (rec: string, index: number) => (
                    <li key={index} className="flex items-start">
                      <span className="w-2 h-2 bg-blue-500 rounded-full mt-2 mr-4"></span>
                      <span className="text-gray-300">{rec}</span>
                    </li>
                  ),
                )}
              </ul>
            </div>
          )}
        </div>
      </div>
      {showAlert && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50">
          <div className="bg-gray-950 border border-red-600 rounded-3xl p-10 max-w-md w-full text-center shadow-2xl animate-[fadeIn_0.3s_ease-out]">
            <h3 className="text-2xl font-bold text-red-500 mb-4">
              ⚠ High Risk Detected
            </h3>

            <p className="text-gray-300 mb-6">
              The prediction indicates a high CKD stage or critical risk level.
              Immediate clinical consultation is strongly recommended.
            </p>

            <button
              onClick={() => setShowAlert(false)}
              className="bg-red-600 hover:bg-red-700 transition px-6 py-2 rounded-xl font-semibold"
            >
              Acknowledge
            </button>
          </div>
        </div>
      )}
      {loading && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-md flex items-center justify-center z-50">
          <div className="flex flex-col items-center">
            <div className="animate-spin rounded-full h-14 w-14 border-b-4 border-blue-500"></div>

            <p className="mt-6 text-gray-300 text-lg tracking-wide">
              Analyzing biomarkers...
            </p>

            <p className="text-sm text-gray-500 mt-2">
              AI ensemble model processing clinical parameters
            </p>
          </div>
        </div>
      )}
    </>
  );
}
