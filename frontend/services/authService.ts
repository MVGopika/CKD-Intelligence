import api from "../lib/api";

export function login(payload: { email: string; password: string }) {
  return api.post("/api/auth/login", payload);
}

export function register(payload: {
  email: string;
  password: string;
  full_name: string;
  role_name: string;
}) {
  return api.post("/api/auth/register", payload);
}

export function getCurrentUser() {
  return api.get("/api/auth/me");
}
