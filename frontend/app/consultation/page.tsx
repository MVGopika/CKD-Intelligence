"use client";

import { useState, useEffect } from "react";
import Vapi from "@vapi-ai/web";
import { PhoneCall, PhoneOff, Circle } from "lucide-react";
import { toast } from "sonner";
import { CreateAssistantDTO } from "@vapi-ai/web/dist/api";
import { createConsultation } from "../../services/consultationService";
import { runPrediction } from "../../services/predictionService";
import PredictionResults from "../../components/ui/PredictionResults";
import ShapChart from "../../components/charts/ShapChart";
import { submitLabResults } from "../../services/patientService";

export default function ConsultationPage() {
  const [callStarted, setCallStarted] = useState(false);
  const [vapiInstance, setVapiInstance] = useState<any>(null);
  const [messages, setMessages] = useState<any[]>([]);
  const [liveTranscript, setLiveTranscript] = useState("");
  const [currentRole, setCurrentRole] = useState<string | null>(null);
  const [duration, setDuration] = useState(0);
  const [loading, setLoading] = useState(false);
  const [showPredictionPrompt, setShowPredictionPrompt] = useState(false);
  const [prediction, setPrediction] = useState<any>(null);
  const [showAlert, setShowAlert] = useState(false);
  const [structuredData, setStructuredData] = useState<any>(null);

  let timer: NodeJS.Timeout;

  const StartCall = async () => {
    setLoading(true);

    const vapi = new Vapi(process.env.NEXT_PUBLIC_VAPI_API_KEY!);
    setVapiInstance(vapi);

    const config: CreateAssistantDTO = {
      name: "AI Kidney Specialist",
      firstMessage:
        "Hello. Thank you for connecting with this kidney health consultation. May I know your name?",
      transcriber: {
        provider: "assembly-ai",
        language: "en",
      },
      voice: {
        provider: "vapi",
        voiceId: "Elliot",
      },
      model: {
        provider: "openai",
        model: "gpt-4",
        messages: [
          {
            role: "system",
            content: `
You are a senior consultant kidney specialist conducting a structured medical consultation.

COMMUNICATION STYLE:
- Professional, respectful, and calm.
- No emojis.
- No casual language.
- No abbreviations.
- Always use full medical terminology.
- Ask only ONE question at a time.
- Wait for the patient's response before continuing.
- If a numeric value is unclear, ask for clarification.
- If numeric values are spoken in fragments (for example "four point" then "four"), combine them logically before confirming.
- Always repeat interpreted numeric values for confirmation before proceeding.

CONSULTATION FLOW:

1. After receiving the patient's name, say:
   "Thank you, [Name]. I will ask you a few important questions to assess kidney health."

2. Collect ONLY these mandatory inputs first:
   - Age in years
   - Biological sex
   - Most recent serum creatinine value (in milligrams per deciliter)
   - Most recent systolic blood pressure reading (in millimeters of mercury)
   - Most recent diastolic blood pressure reading (in millimeters of mercury)
   - Most recent glycated hemoglobin test result (percentage)
   - Serum albumin level (grams per deciliter)
   - Body mass index
   - C-reactive protein level (milligrams per liter)
   - Cystatin C level (milligrams per liter)
   - Relevant medical history
   - Current medications

Do NOT proceed to optional questions until ALL mandatory inputs are collected and confirmed.

3. After mandatory inputs are collected and confirmed, ask:
   "Would you like to provide any additional laboratory results such as blood urea, sodium, potassium, calcium, albumin, hemoglobin, body mass index, C-reactive protein, or cystatin C levels?"

If yes, collect them one at a time.
If no, proceed to analysis.

4. Perform clinical assessment using:
   - Serum creatinine
   - Blood pressure
   - Glycated hemoglobin
   - Medical history

Clinical reference ranges:
   - Serum creatinine: approximately 0.6 to 1.3 milligrams per deciliter
   - Normal blood pressure: below 120 over 80
   - Glycated hemoglobin: below 5.7 percent

5. If findings suggest kidney dysfunction:
   Clearly state:
   "There are clinical indicators suggestive of possible kidney dysfunction."
   Provide risk level: Low, Moderate, or High.
   Recommend evaluation by a nephrologist.

If findings appear within acceptable range:
   Clearly state:
   "There is no strong clinical evidence of kidney dysfunction based on the provided information."
   Recommend routine monitoring.

6. End consultation professionally:
   "Thank you for providing your information. If you experience new symptoms or have further concerns, please consult your healthcare provider. I wish you good health."

STRUCTURED OUTPUT REQUIREMENT (MANDATORY):

After completing the consultation, you MUST output a structured JSON object.
This JSON must appear at the end of the conversation.
It must not contain explanations.
It must be valid JSON.

Use EXACTLY this structure:

{
  "age": number or null,
  "biological_sex": string or null,
  "serum_creatinine_mg_per_dl": number or null,
  "systolic_blood_pressure_mm_hg": number or null,
  "diastolic_blood_pressure_mm_hg": number or null,
  "glycated_hemoglobin_percent": number or null,
  "medical_history": string or null,
  "current_medications": string or null,
  "albumin_g_per_dl": number or null,
  "bmi": number or null,
  "crp": number or null,
  "cystatin_c": number or null,
  "risk_level": "Low" | "Moderate" | "High" | null
}

If any value was not provided, set it to null.

You must ALWAYS output this JSON object even if the consultation was incomplete.
`,
          },
        ],
      },
    };

    try {
      await vapi.start(config);
      toast.success("Consultation started");
    } catch {
      toast.error("Failed to start call");
      setLoading(false);
      return;
    }

    vapi.on("call-start", () => {
      setCallStarted(true);
      setDuration(0);
      timer = setInterval(() => {
        setDuration((prev) => prev + 1);
      }, 1000);
    });

    vapi.on("call-end", () => {
      setCallStarted(false);
      clearInterval(timer);
    });

    vapi.on("message", (msg: any) => {
      if (msg.type === "transcript") {
        const { role, transcriptType, transcript } = msg;

        if (transcriptType === "partial") {
          setCurrentRole(role);
          setLiveTranscript(transcript);
        } else {
          setMessages((prev) => [...prev, { role, text: transcript }]);
          setLiveTranscript("");
          setCurrentRole(null);
          if (
        role === "assistant" &&
        transcript.includes(
          "Thank you for providing your information. If you experience new symptoms or have further concerns, please consult your healthcare provider. I wish you good health."
        )
      ) {
        EndCall();
      }
        }
      }
    });

    setLoading(false);
  };

  const checkMissingFields = (structured: any) => {
    const mandatoryFields = [
      "age",
      "sex",
      "serum_creatinine",
      "systolic_blood_pressure",
      "diastolic_blood_pressure",
      "glycated_hemoglobin",
      "albumin",
      "bmi",
      "crp",
      "cystatin_c",
    ];
    const missingFields = mandatoryFields.filter(
      (field) => structured[field] === null || structured[field] === undefined,
    );

    if (missingFields.length > 0) {
      toast.warning(`Missing fields: ${missingFields.join(", ")}`);
      return true;
    }

    return false;
  };

  const EndCall = async () => {
    if (!vapiInstance) return;

    vapiInstance.stop();
    vapiInstance.removeAllListeners();
    setCallStarted(false);

    // const fullConversation =
    //   "assistant: Hello. Thank you for connecting with this kidney health consultation.\nassistant: May I know your name?\nuser: Yoga.\nassistant: Thank you, Yoga. I will ask you a few important questions.\nassistant: To assess.\nassistant: Kidney.\nuser: Yes.\nassistant: Man. I know your age. And yours.\nuser: 22.\nassistant: Thank you, yoga.\nassistant: Could you please provide?\nassistant: Your biological sex.\nuser: Fem.\nuser: Le.\nassistant: Thank you. Yoga, could you please provide your serum creatinine level?\nassistant: Measured in milligrams per deciliter.\nassistant: Mjodal.\nuser: Two.\nassistant: Thank you, yoga.\nassistant: Could you please provide your systolic blood pressure?\nassistant: In millimeters of mercury.\nuser: 80.\nassistant: Thank you. Yoga. Could you please provide your diastolic blood pressure value in millimeters of mercury?\nuser: Two.\nassistant: Thank you, Yoga. Could you provide your glycated hemoglobin HbA1c value in percentage?\nuser: 72.\nassistant: Thank you, Yoga. Could you now provide your serum albumin level?\nassistant: In grams per deciliter.\nuser: 2.2.\nassistant: Thank you, yoga.\nassistant: Could you provide your body mass index?\nassistant: Bmi value if known.\nuser: 7.5.\nassistant: Thank you. Yoga. Could you now provide your creactive protein?\nassistant: CRP level in milligrams per liter.\nuser: 3.5.\nassistant: Thank you. Yoga. Could you provide your assistatin C level in milligrams per liter?\nuser: On point.\nuser: One.\nassistant: Thank you, yoga.\nassistant: Could you now share any relevant medical history?\nassistant: Such as any known known conditions or diagnoses.";
    try {
      const fullConversation = messages
        .map((m) => `${m.role}: ${m.text}`)
        .join("\n");

      const patientTranscript = fullConversation;

      const userTranscript = messages
        .filter((m) => m.role === "user")
        .map((m) => m.text)
        .join(" ");
      console.log("patientTranscript", patientTranscript);
      // Function to parse numbers from text (handles "two point two" → 2.2)
      const parseNumberFromText = (text: string) => {
        const wordToNum: Record<string, string> = {
          zero: "0",
          one: "1",
          two: "2",
          three: "3",
          four: "4",
          five: "5",
          six: "6",
          seven: "7",
          eight: "8",
          nine: "9",
        };

        let t = text.toLowerCase();
        Object.keys(wordToNum).forEach((word) => {
          const re = new RegExp(`\\b${word}\\b`, "g");
          t = t.replace(re, wordToNum[word]);
        });

        t = t.replace(/\bpoint\b/g, ".");

        const match = t.match(/(\d+(\.\d+)?)/);
        return match ? parseFloat(match[1]) : null;
      };

      // Extract sex from transcript
      const sexMatch = /female|male/i.exec(patientTranscript);
      const sex = sexMatch ? sexMatch[0].toLowerCase() : null;

      const age = parseNumberFromText(
        patientTranscript.match(/age.*?(\d+)/i)?.[0] || patientTranscript,
      );
      const serum_creatinine = parseNumberFromText(
        patientTranscript.match(/creatinine/i)?.input || patientTranscript,
      );
      const systolic_blood_pressure = parseNumberFromText(
        patientTranscript.match(/systolic/i)?.input || patientTranscript,
      );
      const diastolic_blood_pressure = parseNumberFromText(
        patientTranscript.match(/diastolic/i)?.input || patientTranscript,
      );
      const glycated_hemoglobin = parseNumberFromText(
        patientTranscript.match(/glycated hemoglobin/i)?.input ||
          patientTranscript,
      );
      const albumin = parseNumberFromText(
        patientTranscript.match(/albumin/i)?.input || patientTranscript,
      );
      const bmi = parseNumberFromText(
        patientTranscript.match(/body mass index/i)?.input || patientTranscript,
      );
      const crp = parseNumberFromText(
        patientTranscript.match(/c-?reactive protein/i)?.input ||
          patientTranscript,
      );
      const cystatin_c = parseNumberFromText(
        patientTranscript.match(/cystatin c/i)?.input || patientTranscript,
      );

      const structured = {
        age,
        sex: sex,
        serum_creatinine: serum_creatinine,
        systolic_blood_pressure: systolic_blood_pressure,
        diastolic_blood_pressure: diastolic_blood_pressure,
        glycated_hemoglobin: glycated_hemoglobin,
        albumin: albumin,
        bmi,
        crp,
        cystatin_c,
        medical_history: null,
        current_medications: null,
        risk_level: null,
      };

      const hasMissing = checkMissingFields(structured);
      if (hasMissing) {
        return;
      }
      await createConsultation({
        input_type: "voice",
        raw_input: fullConversation,
        transcription: userTranscript,
        structured_data: structured,
      });

      setStructuredData(structured);
      toast.success("Consultation saved successfully");

      if (structured) {
        setShowPredictionPrompt(true);
      }
    } catch (error) {
      console.error(error);
      toast.error("Failed to save consultation");
    }

    // Reset state
    setVapiInstance(null);
    setMessages([]);
    setLiveTranscript("");
    setDuration(0);
  };

  const handleRunPrediction = async () => {
    if (!structuredData) return;

    try {
      setLoading(true);
      setShowPredictionPrompt(false);

      const payload = {
        test_date: new Date().toISOString(),
        age: structuredData?.age ? Number(structuredData.age) : null,
        sex: structuredData?.sex || null,
        serum_creatinine: structuredData?.serum_creatinine
          ? Number(structuredData.serum_creatinine)
          : null,
        hba1c: structuredData?.glycated_hemoglobin
          ? Number(structuredData.glycated_hemoglobin)
          : null,
        blood_pressure_sys: structuredData?.systolic_blood_pressure
          ? Number(structuredData.systolic_blood_pressure)
          : null,
        blood_pressure_dia: structuredData?.diastolic_blood_pressure
          ? Number(structuredData.diastolic_blood_pressure)
          : null,
        albumin: structuredData?.albumin
          ? Number(structuredData.albumin)
          : null,
        bmi: structuredData?.bmi ? Number(structuredData.bmi) : null,
        crp: structuredData?.crp ? Number(structuredData.crp) : null,
        cystatin_c: structuredData?.cystatin_c
          ? Number(structuredData.cystatin_c)
          : null,
      };

      await submitLabResults(payload);
      const response = await runPrediction(payload);

      setPrediction(response.data);
    } catch {
      toast.error("Prediction failed");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!prediction) return;
    if (Number(prediction.ckd_stage) >= 4) {
      setShowAlert(true);
    }
  }, [prediction]);

  return (
    <div className="min-h-screen bg-black text-white px-6 py-6">
      <div className="relative mb-6 rounded-3xl border border-neutral-800 bg-gradient-to-br from-neutral-950 via-black to-neutral-950 p-12 shadow-[0_0_80px_rgba(59,130,246,0.08)] overflow-hidden">
        {/* Neon blurred circles */}
        <div className="absolute -top-32 -left-32 h-[400px] w-[400px] bg-cyan-500/10 rounded-full blur-3xl" />
        <div className="absolute -bottom-32 -right-32 h-[400px] w-[400px] bg-blue-500/10 rounded-full blur-3xl" />
        <div className="relative z-10 text-center md:text-left">
          <h1 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text">
            🩺 AI Kidney Specialist Consultation
          </h1>
          <p className="mt-4 text-gray-400 text-lg max-w-3xl mx-auto md:mx-0 leading-relaxed">
            Discuss your symptoms with our intelligent nephrology assistant. Get
            structured clinical insights and next-step medical guidance in
            real-time.
          </p>
        </div>
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-10">
        <div className="relative overflow-hidden rounded-2xl border border-white/10 bg-gradient-to-br from-neutral-900 via-black to-neutral-950 p-6 shadow-[0_0_40px_rgba(59,130,246,0.08)] backdrop-blur-xl">
          <div className="absolute -top-10 -left-10 w-40 h-40 bg-cyan-500/10 blur-3xl rounded-full" />
          <div className="absolute -bottom-10 -right-10 w-40 h-40 bg-blue-500/10 blur-3xl rounded-full" />
          <div className="relative flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="relative flex items-center justify-center">
                <span
                  className={`absolute inline-flex h-4 w-4 rounded-full ${
                    callStarted ? "bg-green-500 animate-ping" : "bg-red-500"
                  }`}
                />
                <span
                  className={`relative inline-flex h-4 w-4 rounded-full ${
                    callStarted ? "bg-green-500" : "bg-red-500"
                  }`}
                />
              </div>

              <div>
                <p className="text-sm text-gray-400">Session Status</p>
                <p className="font-semibold text-lg">
                  {callStarted
                    ? "Live Consultation Active"
                    : "Awaiting Connection"}
                </p>
              </div>
            </div>

            <div className="text-right">
              <p className="text-sm text-gray-400">Duration</p>
              <p className="font-mono text-2xl tracking-wider text-cyan-400">
                {new Date(duration * 1000).toISOString().substr(14, 5)}
              </p>
            </div>
          </div>

          {/* Chat Window */}
          <div className="absolute -top-24 -left-24 w-72 h-72 bg-cyan-500/10 blur-3xl rounded-full" />
          <div className="absolute -bottom-24 -right-24 w-72 h-72 bg-blue-500/10 blur-3xl rounded-full" />
          <div className="relative z-10 text-center">
            <div className="relative mx-auto w-32 h-32 mb-6 flex items-center justify-center">
              {callStarted && (
                <div className="absolute w-40 h-40 rounded-full border border-cyan-500/40 animate-pulse" />
              )}

              <div className="w-32 h-32 rounded-full bg-gradient-to-br from-cyan-500/20 to-blue-500/20 flex items-center justify-center text-5xl shadow-inner">
                🩺
              </div>
            </div>

            <h2 className="text-2xl font-bold bg-gradient-to-r from-cyan-400 to-blue-400 bg-clip-text text-transparent">
              AI Kidney Specialist
            </h2>

            <p className="text-gray-400 mt-2 text-sm tracking-wide">
              Intelligent Nephrology Voice Consultation System
            </p>

            <div className="mt-8 bg-black/40 border border-white/10 rounded-2xl p-6 max-h-72 overflow-y-auto backdrop-blur-md shadow-inner text-left space-y-3">
              {messages.slice(-6).map((msg, index) => (
                <div
                  key={index}
                  className={`text-sm ${
                    msg.role === "assistant" ? "text-cyan-300" : "text-gray-300"
                  }`}
                >
                  <span className="font-semibold capitalize">
                    {msg.role === "assistant" ? "Doctor" : "Patient"}:
                  </span>{" "}
                  {msg.text}
                </div>
              ))}

              {liveTranscript && (
                <div className="italic text-gray-500 text-sm">
                  {currentRole === "assistant" ? "Doctor" : "Patient"}:{" "}
                  {liveTranscript}
                </div>
              )}
            </div>

            <div className="mt-10 relative">
              {!callStarted ? (
                <button
                  onClick={StartCall}
                  disabled={loading}
                  className="relative w-full group overflow-hidden rounded-2xl px-6 py-4 font-semibold text-lg transition-all duration-300"
                >
                  <span className="absolute inset-0 rounded-2xl bg-black opacity-70 blur-lg group-hover:opacity-100 transition" />
                  <span className="relative flex items-center justify-center gap-3 rounded-2xl bg-gradient-to-r from-green-500 to-emerald-600 px-6 py-4 text-white shadow-lg transition-all duration-300 group-hover:scale-[1.02] group-active:scale-[0.98]">
                    {loading ? (
                      <>
                        <span className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                        Establishing Secure Connection...
                      </>
                    ) : (
                      <>
                        <PhoneCall className="w-5 h-5" />
                        Initiate Consultation
                      </>
                    )}
                  </span>
                </button>
              ) : (
                <button
                  onClick={EndCall}
                  className="relative w-full group overflow-hidden rounded-2xl px-6 py-4 font-semibold text-lg transition-all duration-300"
                >
                  <span className="absolute inset-0 rounded-2xl bg-black opacity-70 blur-lg animate-pulse" />

                  <span className="relative flex items-center justify-center gap-3 rounded-2xl bg-gradient-to-r from-red-600 to-rose-600 px-6 py-4 text-white shadow-lg transition-all duration-300 group-hover:scale-[1.02] group-active:scale-[0.98]">
                    <span className="w-3 h-3 bg-white rounded-full animate-pulse" />
                    <PhoneOff className="w-5 h-5" />
                    Terminate Consultation
                  </span>
                </button>
              )}
            </div>
          </div>
        </div>

        <div className="rounded-3xl border border-white/10 bg-gradient-to-br from-neutral-950 via-black to-neutral-950 p-10 shadow-[0_0_60px_rgba(59,130,246,0.08)]">
          {(prediction || structuredData || messages.length > 0) && (
            <div className="flex justify-end mb-2">
              <button
                onClick={() => {
                  setPrediction(null);
                  setStructuredData(null);
                  setMessages([]);
                  setLiveTranscript("");
                  setCallStarted(false);
                  setShowAlert(false);
                  setShowPredictionPrompt(false);
                  setDuration(0);
                  if (vapiInstance) {
                    vapiInstance.stop();
                    vapiInstance.removeAllListeners();
                    setVapiInstance(null);
                  }
                }}
                className="px-6 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-700 transition font-semibold text-white"
              >
                Reset Consultation
              </button>
            </div>
          )}
          <h2 className="text-2xl font-semibold text-cyan-400 mb-6">
            Stage-wise CKD Prediction
          </h2>

          {!prediction && (
            <div className="text-gray-500 space-y-3">
              <p>
                The prediction will be generated based on the completed clinical
                consultation and collected biomarker data.
              </p>
              <p className="text-sm text-gray-600">
                Please complete the voice consultation and confirm all mandatory
                laboratory values to enable stage-wise Chronic Kidney Disease
                risk assessment.
              </p>
            </div>
          )}

          {prediction && <PredictionResults result={prediction} />}
          {/* {prediction.top_contributing_features && (
            <ShapChart features={prediction.top_contributing_features} />
          )} */}
        </div>
      </div>

      {prediction?.recommendations && (
        <div className="mt-12 rounded-3xl border border-gray-800 p-10 bg-gradient-to-br from-neutral-950 via-black to-neutral-950 shadow-[0_0_60px_rgba(0,255,255,0.05)]">
          <h2 className="text-2xl font-semibold text-cyan-400 mb-6">
            Clinical Recommendations
          </h2>

          <ul className="space-y-3 text-gray-300">
            {prediction.recommendations.map((rec: string, index: number) => (
              <li key={index}>• {rec}</li>
            ))}
          </ul>
        </div>
      )}
      {showPredictionPrompt && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-md flex items-center justify-center z-50">
          <div className="bg-gray-950 border border-blue-600 rounded-3xl p-10 max-w-lg w-full shadow-2xl">
            <h3 className="text-2xl font-bold text-blue-400 mb-4">
              Kidney Disease Stage-wise Prediction
            </h3>

            <p className="text-gray-300 mb-6 leading-relaxed">
              The clinical consultation has been completed successfully. Would
              you like to generate a stage-wise Chronic Kidney Disease
              prediction based on the collected biomarkers and clinical inputs?
            </p>

            <div className="flex justify-end gap-4">
              <button
                onClick={() => setShowPredictionPrompt(false)}
                className="px-5 py-2 rounded-xl border border-gray-600 hover:bg-gray-800 transition"
              >
                No, Skip
              </button>

              <button
                onClick={handleRunPrediction}
                className="px-6 py-2 rounded-xl bg-blue-600 hover:bg-blue-700 transition font-semibold"
              >
                Yes, Generate Prediction
              </button>
            </div>
          </div>
        </div>
      )}
      {showAlert && (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50">
          <div className="bg-gray-950 border border-red-600 rounded-3xl p-10 max-w-md w-full text-center">
            <h3 className="text-2xl font-bold text-red-500 mb-4">
              High CKD Stage Detected
            </h3>
            <p>
              Stage four or higher detected. Immediate nephrology consultation
              recommended.
            </p>
            <button
              onClick={() => setShowAlert(false)}
              className="mt-6 px-6 py-2 bg-red-600 rounded-xl"
            >
              Acknowledge
            </button>
          </div>
        </div>
      )}
      {loading && (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50">
          <div className="animate-spin rounded-full h-14 w-14 border-b-4 border-blue-500"></div>
        </div>
      )}
    </div>
  );
}
