"use client";

interface PredictionResult {
  egfr_predicted: number;
  ckd_stage: string;
  egfr_confidence: number;
  risk_level: string;
  clinical_guidance?: string;
  recommendations?: string[];
}

interface Props {
  result: PredictionResult;
}

const stageStyles: Record<
  string,
  { text: string; bg: string; border: string }
> = {
  "1": {
    text: "text-green-400",
    bg: "bg-green-500/10",
    border: "border-green-500/30",
  },
  "2": {
    text: "text-yellow-400",
    bg: "bg-yellow-500/10",
    border: "border-yellow-500/30",
  },
  "3": {
    text: "text-orange-400",
    bg: "bg-orange-500/10",
    border: "border-orange-500/30",
  },
  "4": {
    text: "text-red-400",
    bg: "bg-red-500/10",
    border: "border-red-500/30",
  },
  "5": {
    text: "text-red-600",
    bg: "bg-red-600/10",
    border: "border-red-600/40",
  },
};

export default function PredictionResults({ result }: Props) {
  const stage = result.ckd_stage;
  const risk = result.risk_level?.toLowerCase();
  const confidencePercent = (result.egfr_confidence * 100).toFixed(1);

  const style = stageStyles[stage] || stageStyles["1"];

  const circumference = 2 * Math.PI * 40;
  const offset = circumference * (1 - Number(confidencePercent) / 100);

  return (
    <div
      className={`rounded-3xl p-8 border ${style.bg} ${style.border} transition-all`}
    >
      {/* HEADER */}
      <h2 className="text-2xl font-semibold mb-8">🧬 AI Prediction Summary</h2>

      {/* eGFR SECTION */}
      <div className="mb-10">
        <p className="text-gray-400 text-sm mb-2">Predicted eGFR</p>
        <p className="text-4xl font-bold text-cyan-400">
          {result.egfr_predicted.toFixed(2)}
          <span className="text-lg ml-2 text-gray-500">mL/min/1.73m²</span>
        </p>
      </div>

      {/* STAGE + RISK GRID */}
      <div className="grid grid-cols-2 gap-10 items-start mb-10">
        {/* Stage */}
        <div className="space-y-2">
          <p className="text-gray-400 text-sm">CKD Stage</p>
          <p className={`text-2xl font-bold ${style.text}`}>Stage {stage}</p>
        </div>

        {/* Risk */}
        <div className="space-y-2">
          <p className="text-gray-400 text-sm">Risk Level</p>
          <span
            className={`inline-block px-4 py-1 rounded-full text-sm font-semibold capitalize
              ${
                risk === "low"
                  ? "bg-green-500/20 text-green-400"
                  : risk === "moderate"
                    ? "bg-yellow-500/20 text-yellow-400"
                    : "bg-red-500/20 text-red-400"
              }`}
          >
            {result.risk_level}
          </span>
        </div>
      </div>

      {/* CONFIDENCE RING */}
      <div className="flex items-center gap-8">
        <div className="relative w-24 h-24">
          <svg className="transform -rotate-90 w-24 h-24">
            <circle
              cx="48"
              cy="48"
              r="40"
              stroke="gray"
              strokeWidth="8"
              fill="transparent"
            />
            <circle
              cx="48"
              cy="48"
              r="40"
              stroke="cyan"
              strokeWidth="8"
              fill="transparent"
              strokeDasharray={circumference}
              strokeDashoffset={offset}
              strokeLinecap="round"
            />
          </svg>
          <div className="absolute inset-0 flex items-center justify-center text-lg font-semibold">
            {confidencePercent}%
          </div>
        </div>

        <div>
          <p className="text-gray-400 text-sm mb-2">Model Confidence</p>
          <p className="text-gray-300 text-sm">
            Higher percentage indicates stronger prediction reliability.
          </p>
        </div>
      </div>

      {/* CLINICAL GUIDANCE */}
      {result.clinical_guidance && (
        <div className="mt-10 pt-6 border-t border-gray-700 text-gray-300">
          {result.clinical_guidance}
        </div>
      )}
    </div>
  );
}
