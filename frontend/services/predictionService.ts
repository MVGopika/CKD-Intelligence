import api from "../lib/api";

export function getPrediction(id: number) {
  return api.get(`/api/predict/${id}`);
}

export function runPrediction(payload: any) {
  return api.post("/api/predict", payload);
}