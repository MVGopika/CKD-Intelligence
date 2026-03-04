"use client";

import { useEffect, useState } from "react";
import { getReports, downloadReport } from "../../services/reportService";
import { formatDate, formatDateTime } from "../../lib/utils";
import { toast } from "sonner";

export default function ReportsPage() {
  const [reports, setReports] = useState<any[]>([]);
  const [filteredReports, setFilteredReports] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [downloadingId, setDownloadingId] = useState<number | null>(null);

  useEffect(() => {
    async function loadReports() {
      try {
        const response = await getReports();
        const data = response.data.reports || [];
        setReports(data);
        setFilteredReports(data);
      } catch (err) {
        toast.error("Failed to load reports");
        console.error("Failed to load reports", err);
      } finally {
        setLoading(false);
      }
    }
    loadReports();
  }, []);

  useEffect(() => {
    const filtered = reports.filter((r) =>
      r.title.toLowerCase().includes(search.toLowerCase()),
    );
    setFilteredReports(filtered);
  }, [search, reports]);

  const handleDownload = async (reportId: number, title: string) => {
    try {
      setDownloadingId(reportId);
      const response = await downloadReport(reportId);
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", `ckd_report_${reportId}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      toast.success(`Report "${title}" downloaded successfully`);
    } catch (err) {
      toast.error(`Failed to download report "${title}"`);
      console.error("Download failed", err);
    } finally {
      setDownloadingId(null);
    }
  };

  const getStageColor = (stage: string) => {
    if (stage.includes("1")) return "bg-emerald-500/20 text-emerald-400";
    if (stage.includes("2")) return "bg-yellow-500/20 text-yellow-400";
    if (stage.includes("3")) return "bg-orange-500/20 text-orange-400";
    if (stage.includes("4")) return "bg-red-500/20 text-red-400";
    return "bg-gray-700 text-gray-300";
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-black">
        <div className="animate-spin rounded-full h-14 w-14 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-black text-white px-6 py-6">
      <div className="relative mb-8 rounded-3xl border border-neutral-800 bg-gradient-to-br from-neutral-950 via-black to-neutral-950 p-12 shadow-[0_0_80px_rgba(59,130,246,0.08)] overflow-hidden">
        <div className="absolute -top-32 -left-32 h-[400px] w-[400px] bg-blue-500/10 rounded-full blur-3xl" />
        <div className="absolute -bottom-32 -right-32 h-[400px] w-[400px] bg-purple-500/10 rounded-full blur-3xl" />

        <div className="relative z-10 flex flex-col md:flex-row md:justify-between md:items-center gap-6">
          <div>
            <h1 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-blue-400 to-cyan-300 bg-clip-text text-transparent">
              📄 Medical Reports
            </h1>
            <p className="mt-4 text-gray-400 text-lg max-w-3xl leading-relaxed">
              Browse all generated clinical prediction reports. View patient CKD
              stage, eGFR estimates, and download personalized PDF reports
              instantly.
            </p>
          </div>
          <div className="flex items-center bg-neutral-900 border border-neutral-700 rounded-xl px-4 py-2 w-full md:w-96 focus-within:border-blue-500 transition">
            <search className="w-4 h-4 text-gray-400 mr-2" />
            <input
              type="text"
              placeholder="Search reports..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="bg-transparent outline-none text-sm w-full placeholder:text-gray-500 text-white"
            />
          </div>
        </div>
      </div>

      <div className="mx-auto">
        <div className="mb-6 flex items-center justify-between">
          <p className="text-sm text-gray-400">
            Total Reports:{" "}
            <span className="font-semibold text-white">
              {filteredReports.length}
            </span>
          </p>
        </div>

        {filteredReports.length === 0 ? (
          <div className="bg-black border border-neutral-800 rounded-2xl p-16 text-center shadow-xl">
            <h3 className="text-lg font-semibold text-gray-300">
              No reports found
            </h3>
            <p className="text-gray-500 mt-2">
              Complete a prediction to generate a clinical report
            </p>
          </div>
        ) : (
          <div className="h-[450px] overflow-y-auto rounded-2xl border border-neutral-800 bg-black shadow-2xl">
            <table className="min-w-full text-sm">
              <thead className="bg-gray-950 text-gray-400 uppercase text-xs tracking-wider border-b border-neutral-800">
                <tr>
                  <th className="px-6 py-4 text-left">Report Title</th>
                  <th className="px-6 py-4 text-left">Stage</th>
                  <th className="px-6 py-4 text-left">Created At</th>
                  <th className="px-6 py-4 text-right">Action</th>
                </tr>
              </thead>

              <tbody className="divide-y divide-neutral-800">
                {filteredReports.map((report) => {
                  const stage = report.title.match(/Stage \d/)?.[0] || "—";

                  return (
                    <tr
                      key={report.id}
                      className="hover:bg-neutral-900/60 transition-all duration-200"
                    >
                      <td className="px-6 py-5">
                        <div className="font-medium text-white">
                          {report.title}
                        </div>
                        <div className="text-gray-500 text-xs mt-1">
                          Report ID: {report.id}
                        </div>
                      </td>

                      <td className="px-6 py-5">
                        <span
                          className={`px-3 py-1 rounded-full text-xs font-semibold ${getStageColor(stage)}`}
                        >
                          {stage}
                        </span>
                      </td>

                      <td className="px-6 py-5 text-gray-400">
                        {formatDateTime(report.created_at)}
                      </td>

                      <td className="px-6 py-5 text-right">
                        <button
                          onClick={() =>
                            handleDownload(report.id, report.title)
                          }
                          disabled={downloadingId === report.id}
                          className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white text-xs font-medium rounded-lg transition shadow-md disabled:opacity-50"
                        >
                          {downloadingId === report.id
                            ? "Downloading..."
                            : "Download PDF"}
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
