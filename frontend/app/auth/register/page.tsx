"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { register } from "../../../services/authService";
import { saveToken } from "../../../lib/auth";
import Link from "next/link";
import { toast } from "sonner";

export default function RegisterPage() {
  const [formData, setFormData] = useState({
    email: "",
    password: "",
    full_name: "",
    role_name: "patient",
  });

  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  const router = useRouter();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const response = await register(formData);
      saveToken(response.data.access_token);

      router.push(
        formData.role_name === "patient"
          ? "/dashboard/patient"
          : "/dashboard/doctor",
      );
      if (formData.role_name === "patient") {
        toast.success("Patient Registered successfully");
      } else {
        toast.success("Doctor Registered successfully");
      }
    } catch (err: any) {
      setError(
        err.response?.data?.detail || "Registration failed. Please try again.",
      );
      toast.error("Registration failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-black via-neutral-950 to-black px-4">
      <div className="w-full max-w-md bg-white/5 backdrop-blur-xl border border-zinc-800 rounded-2xl shadow-2xl p-8 text-white">
        <h1 className="text-3xl font-bold text-center mb-2">Create Account</h1>

        <p className="text-center text-zinc-400 mb-6">
          Join CKD Intelligence Platform
        </p>

        {error && (
          <div className="mb-4 rounded-lg bg-red-500/10 border border-red-500/30 px-4 py-2 text-sm text-red-400">
            {error}
          </div>
        )}

        <form className="space-y-5" onSubmit={handleSubmit}>
          {/* Full Name */}
          <div>
            <label className="block text-sm mb-1 text-zinc-400">
              Full Name
            </label>
            <input
              name="full_name"
              type="text"
              required
              value={formData.full_name}
              onChange={handleChange}
              className="w-full rounded-lg bg-neutral-900 border border-zinc-700 px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-600 transition"
              placeholder="John Doe"
            />
          </div>

          {/* Email */}
          <div>
            <label className="block text-sm mb-1 text-zinc-400">
              Email Address
            </label>
            <input
              name="email"
              type="email"
              required
              value={formData.email}
              onChange={handleChange}
              className="w-full rounded-lg bg-neutral-900 border border-zinc-700 px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-600 transition"
              placeholder="you@example.com"
            />
          </div>

          {/* Password */}
          <div>
            <label className="block text-sm mb-1 text-zinc-400">Password</label>

            <div className="relative">
              <input
                name="password"
                type={showPassword ? "text" : "password"}
                required
                value={formData.password}
                onChange={handleChange}
                className="w-full rounded-lg bg-neutral-900 border border-zinc-700 px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-600 transition"
                placeholder="Minimum 8 characters"
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

          {/* Role Selection */}
          <div>
            <label className="block text-sm mb-3 text-zinc-400">
              Select Role
            </label>

            <div className="grid grid-cols-2 gap-4">
              <button
                type="button"
                onClick={() =>
                  setFormData({ ...formData, role_name: "patient" })
                }
                className={`rounded-xl border p-4 text-sm transition ${
                  formData.role_name === "patient"
                    ? "border-blue-500 bg-blue-600/10 text-white"
                    : "border-zinc-700 text-zinc-400 hover:border-zinc-500"
                }`}
              >
                🧍 Patient
              </button>

              <button
                type="button"
                onClick={() =>
                  setFormData({ ...formData, role_name: "doctor" })
                }
                className={`rounded-xl border p-4 text-sm transition ${
                  formData.role_name === "doctor"
                    ? "border-green-500 bg-green-600/10 text-white"
                    : "border-zinc-700 text-zinc-400 hover:border-zinc-500"
                }`}
              >
                🩺 Doctor
              </button>
            </div>
          </div>

          {/* Submit */}
          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-lg bg-blue-600 hover:bg-blue-700 transition py-2 font-semibold shadow-lg shadow-blue-600/30 disabled:opacity-70"
          >
            {loading ? "Creating account..." : "Create Account"}
          </button>
        </form>

        <p className="text-sm text-center text-zinc-400 mt-6">
          Already have an account?{" "}
          <Link href="/auth/login" className="text-blue-500 hover:underline">
            Log in
          </Link>
        </p>
      </div>
    </div>
  );
}
