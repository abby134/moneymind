"use client";
import { useEffect, useState } from "react";
import { api, Report, MonthlySnapshot } from "@/lib/api";
import Link from "next/link";
import { format } from "date-fns";

export default function ReportsPage() {
  const [reports, setReports] = useState<Report[]>([]);
  const [snapshots, setSnapshots] = useState<MonthlySnapshot[]>([]);
  const [analyzing, setAnalyzing] = useState<string | null>(null);

  useEffect(() => {
    api.reports.list().then(setReports);
    api.snapshots.list().then(setSnapshots);
  }, []);

  const snapshotsWithoutReport = snapshots.filter(
    (s) => !reports.find((r) => r.snapshot_id === s.id)
  );

  async function handleAnalyze(snapshotId: string) {
    setAnalyzing(snapshotId);
    try {
      await api.snapshots.analyze(snapshotId);
      setTimeout(() => {
        api.reports.list().then(setReports);
        setAnalyzing(null);
      }, 3000);
    } catch {
      setAnalyzing(null);
    }
  }

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Reports</h1>

      {snapshotsWithoutReport.length > 0 && (
        <div className="bg-amber-50 border border-amber-200 rounded-xl p-4">
          <p className="text-amber-800 font-medium text-sm mb-3">Ready to analyze:</p>
          <div className="space-y-2">
            {snapshotsWithoutReport.map((s) => (
              <div key={s.id} className="flex items-center justify-between">
                <span className="text-sm text-gray-700">
                  {format(new Date(s.month), "MMMM yyyy")} · {s.uploads_included} file(s)
                </span>
                <button
                  onClick={() => handleAnalyze(s.id)}
                  disabled={analyzing === s.id}
                  className="bg-emerald-600 text-white text-sm px-4 py-1.5 rounded-lg hover:bg-emerald-700 disabled:opacity-50"
                >
                  {analyzing === s.id ? "Analyzing..." : "Run Analysis"}
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="space-y-3">
        {reports.length === 0 && (
          <div className="text-center py-12 text-gray-400">No reports yet.</div>
        )}
        {reports.map((report) => (
          <Link
            key={report.id}
            href={`/dashboard/reports/${report.id}`}
            className="block bg-white rounded-xl p-5 shadow-sm hover:shadow-md transition"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium text-gray-900">
                  {format(new Date(report.created_at), "MMMM yyyy")} Report
                </p>
                <p className="text-sm text-gray-400">
                  {format(new Date(report.created_at), "MMM d, yyyy")}
                </p>
              </div>
              <span className="text-emerald-600 text-sm">View →</span>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
