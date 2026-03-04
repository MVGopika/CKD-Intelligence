"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { login } from "../../../services/authService";
import { saveToken } from "../../../lib/auth";
import Link from "next/link";
import { getToken } from "../../../lib/auth";
import { useEffect } from "react";
import { toast } from "sonner";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const resp = await login({ email, password });
      saveToken(resp.data.access_token);
      const role = resp.data.user.role_id;
      if (role === 12 || role === 2) {
        router.push("/dashboard/doctor");
        toast.success("Doctor Logged in successfully");
        setTimeout(() => {
          window.location.reload();
        }, 2000);
      } else {
        router.push("/dashboard/patient");
        toast.success("Patient Logged in successfully");
        setTimeout(() => {
          window.location.reload();
        }, 2000);
      }
    } catch {
      toast.error("Invalid email or password. Please try again.");
      setError("Invalid email or password. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-black via-neutral-950 to-black px-4">
      <div className="w-full max-w-md bg-white/5 backdrop-blur-xl border border-gray-800 rounded-2xl shadow-2xl p-8 text-white">
        <h1 className="text-3xl font-bold mb-2 text-center">Welcome Back</h1>

        <p className="text-center text-zinc-400 mb-6">
          Sign in to continue to CKD Intelligence
        </p>

        {error && (
          <div className="mb-4 rounded-lg bg-red-500/10 border border-red-500/30 px-4 py-2 text-sm text-red-400">
            {error}
          </div>
        )}

        <form className="space-y-5" onSubmit={handleSubmit}>
          {/* Email */}
          <div>
            <label className="block text-sm mb-1 text-zinc-400">
              Email Address
            </label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full rounded-lg bg-neutral-900 border border-zinc-700 px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-600 transition"
              placeholder="you@example.com"
            />
          </div>

          {/* Password */}
          <div>
            <label className="block text-sm mb-1 text-zinc-400">Password</label>

            <div className="relative">
              <input
                type={showPassword ? "text" : "password"}
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full rounded-lg bg-neutral-900 border border-zinc-700 px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-600 transition"
                placeholder="••••••••"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-2 text-sm text-zinc-400 hover:text-white"
              >
                {showPassword ? "Hide" : "Show"}
              </button>
            </div>
          </div>

          {/* Submit */}
          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-lg bg-blue-600 hover:bg-blue-700 transition py-2 font-semibold shadow-lg shadow-blue-600/30 disabled:opacity-70"
          >
            {loading ? "Signing in..." : "Log In"}
          </button>
        </form>

        {/* Footer */}
        <p className="text-sm text-center text-zinc-400 mt-6">
          Don’t have an account?{" "}
          <Link href="/auth/register" className="text-blue-500 hover:underline">
            Create one
          </Link>
        </p>
      </div>
    </div>
  );
}
