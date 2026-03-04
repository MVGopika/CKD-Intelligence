"use client";

import { useEffect, useState, useMemo } from "react";
import { useRouter } from "next/navigation";
import { getCurrentUser } from "../../../services/authService";
import api from "../../../lib/api";
import { formatDate } from "../../../lib/utils";

export default function DoctorDashboard() {
  const [user, setUser] = useState<any>(null);
  const [patients, setPatients] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const router = useRouter();

  useEffect(() => {
    async function loadData() {
      try {
        const userResponse = await getCurrentUser();
        setUser(userResponse.data);

        const patientsResponse = await api.get("/api/doctor/patients");
        setPatients(patientsResponse.data.patients);
      } catch {
        router.push("/auth/login");
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, [router]);

  const filteredPatients = useMemo(() => {
    return patients.filter((p) =>
      p.full_name.toLowerCase().includes(search.toLowerCase()),
    );
  }, [patients, search]);

  const stats = {
    total: patients.length,
    highRisk: patients.filter(
      (p) => p.risk_level === "high" || p.risk_level === "critical",
    ).length,
    stage45: patients.filter(
      (p) => p.latest_ckd_stage === "4" || p.latest_ckd_stage === "5",
    ).length,
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-black px-6 py-10">
      {/* HEADER */}
      {/* HEADER */}
      <div className="relative mb-12 overflow-hidden rounded-3xl border border-gray-800 bg-gradient-to-br from-gray-950 via-black to-gray-950 p-8 shadow-[0_0_60px_rgba(59,130,246,0.08)]">
        {/* Glow Effects */}
        <div className="absolute -top-20 -left-20 h-72 w-72 rounded-full bg-blue-500/10 blur-3xl" />
        <div className="absolute -bottom-20 -right-20 h-72 w-72 rounded-full bg-purple-500/10 blur-3xl" />

        <div className="relative z-10 flex flex-col md:flex-row md:items-center md:justify-between gap-6">
          {/* Left Section */}
          <div>
            <h1 className="text-4xl md:text-5xl font-bold bg-gradient-to-r text-white from-blue-400 to-cyan-300 bg-clip-text ">
              👨‍⚕️ Doctor Dashboard
            </h1>
            <p className="mt-3 text-gray-400 text-lg">
              Welcome back,{" "}
              <span className="text-white font-semibold">
                Dr. {user?.full_name}
              </span>
            </p>
          </div>
        </div>
      </div>

      {/* STATS */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">
        <StatCard title="Total Patients" value={stats.total} color="blue" />
        <StatCard title="High Risk" value={stats.highRisk} color="red" />
        <StatCard title="Stage 4-5" value={stats.stage45} color="orange" />
      </div>

      {/* SEARCH */}
      <div className="mb-6">
        <input
          type="text"
          placeholder="Search patients..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full md:w-96 px-4 py-2 rounded-xl border border-gray-800 focus:ring-2 focus:ring-blue-500 outline-none bg-slate-950"
        />
      </div>

      {/* TABLE */}
      <div className="bg-gray-950 rounded-2xl shadow-2xl overflow-hidden border border-gray-800">
        {filteredPatients.length === 0 ? (
          <div className="p-16 text-center text-gray-400 text-lg">
            🩺 No patients assigned yet
          </div>
        ) : (
          <table className="min-w-full text-sm">
            <thead className="bg-gray-900 text-gray-400 uppercase text-xs border-b border-gray-800">
              <tr>
                <th className="px-6 py-4 text-left">Patient</th>
                <th className="px-6 py-4 text-left">CKD Stage</th>
                <th className="px-6 py-4 text-left">eGFR</th>
                <th className="px-6 py-4 text-left">Risk</th>
                <th className="px-6 py-4 text-left">Last Test</th>
              </tr>
            </thead>

            <tbody>
              {filteredPatients.map((patient) => (
                <tr
                  key={patient.id}
                  className="border-b border-gray-800 hover:bg-gray-900/60 transition"
                >
                  <td className="px-6 py-4 font-medium text-white">
                    {patient.full_name}
                  </td>

                  <td className="px-6 py-4">
                    <StageBadge stage={patient.latest_ckd_stage} />
                  </td>

                  <td className="px-6 py-4 text-gray-300">
                    {patient.latest_egfr
                      ? patient.latest_egfr.toFixed(1)
                      : "N/A"}
                  </td>

                  <td className="px-6 py-4">
                    <RiskBadge level={patient.risk_level} />
                  </td>

                  <td className="px-6 py-4 text-gray-400">
                    {patient.latest_test_date
                      ? formatDate(patient.latest_test_date)
                      : "N/A"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}

function StatCard({ title, value, color }: any) {
  const colorMap: any = {
    blue: "bg-blue-500/10 text-blue-400 border-blue-500/20",
    red: "bg-red-500/10 text-red-400 border-red-500/20",
    orange: "bg-orange-500/10 text-orange-400 border-orange-500/20",
  };

  return (
    <div className="bg-gray-950 rounded-2xl p-6 border border-gray-800 hover:border-gray-700 transition shadow-xl">
      <h3 className="text-gray-400 text-sm">{title}</h3>
      <div
        className={`mt-4 text-3xl font-bold px-4 py-2 inline-block rounded-xl border ${colorMap[color]}`}
      >
        {value}
      </div>
    </div>
  );
}

function StageBadge({ stage }: any) {
  const map: any = {
    "1": "bg-green-100 text-green-700",
    "2": "bg-green-100 text-green-700",
    "3": "bg-yellow-100 text-yellow-700",
    "4": "bg-orange-100 text-orange-700",
    "5": "bg-red-100 text-red-700",
  };

  return (
    <span
      className={`px-3 py-1 rounded-full text-xs font-semibold ${map[stage] || "bg-gray-200 text-gray-600"}`}
    >
      Stage {stage || "N/A"}
    </span>
  );
}

function RiskBadge({ level }: any) {
  const map: any = {
    low: "bg-green-100 text-green-700",
    moderate: "bg-yellow-100 text-yellow-700",
    high: "bg-orange-100 text-orange-700",
    critical: "bg-red-100 text-red-700",
  };

  return (
    <span
      className={`px-3 py-1 rounded-full text-xs font-semibold capitalize ${map[level] || "bg-gray-100 text-gray-600"}`}
    >
      {level || "N/A"}
    </span>
  );
}
