import api from "../lib/api";

export function getReports() {
  return api.get("/api/reports");
}
export function downloadReport(id: number) {
  return api.get(`/api/reports/${id}/download`, { responseType: "blob" });
}
