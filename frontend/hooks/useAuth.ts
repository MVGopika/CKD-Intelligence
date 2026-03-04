"use client";

import { useState, useEffect } from "react";
import { getCurrentUser } from "../services/authService";
import { saveToken, clearToken } from "../lib/auth";
import { User } from "../types/user";

export default function useAuth() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchUser() {
      try {
        const response = await getCurrentUser();
        setUser(response.data);
      } catch (err) {
        setUser(null);
      } finally {
        setLoading(false);
      }
    }
    fetchUser();
  }, []);

  function logout() {
    clearToken();
    setUser(null);
  }

  return { user, loading, logout };
}
