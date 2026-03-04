import api from "../lib/api";

export function createConsultation(input: {
  input_type: string;
  raw_input?: string;
  transcription?: string;
  structured_data?: any;
}) {
  return api.post("/api/consultation", input);
}

export function getConsultations() {
  return api.get("/api/consultation");
}
