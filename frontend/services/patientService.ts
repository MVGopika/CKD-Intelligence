import api from "../lib/api";

export function createProfile(data: any) {
  return api.post("/api/patient/profile", data);
}

export function getProfile() {
  return api.get("/api/patient/profile");
}

export function submitLabResults(data: any) {
  return api.post("/api/patient/lab-results", data);
}

export function getLabResults() {
  return api.get("/api/patient/lab-results");
}
