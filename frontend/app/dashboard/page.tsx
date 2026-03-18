"use client";
import { useEffect, useState } from "react";
import { api, MonthlySnapshot } from "@/lib/api";
import { SpendingChart } from "@/components/dashboard/spending-chart";
import { CategoryBreakdown } from "@/components/dashboard/category-breakdown";
import { format } from "date-fns";

export default function DashboardPage() {
  const [snapshots, setSnapshots] = useState<MonthlySnapshot[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.snapshots.list().then(setSnapshots).finally(() => setLoading(false));
  }, []);

  const latest = snapshots[0];

  if (loading) return <div className="text-center py-20 text-gray-400">Loading...</div>;

  if (!latest) {
    return (
      <div className="text-center py-20">
        <p className="text-gray-500 text-lg mb-4">No data yet. Upload your first CSV to get started.</p>
        <a href="/dashboard/upload" className="bg-emerald-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-emerald-700 transition">
          Upload CSV
        </a>
      </div>
    );
  }

  const savingsRate = (latest.savings_rate * 100).toFixed(1);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Overview</h1>
        <p className="text-gray-500">
          Latest: {format(new Date(latest.month), "MMMM yyyy")}
        </p>
      </div>

      <div className="grid grid-cols-4 gap-4">
        {[
          { label: "Income", value: `$${latest.total_income.toLocaleString()}`, color: "text-emerald-600" },
          { label: "Expenses", value: `$${latest.total_expenses.toLocaleString()}`, color: "text-red-500" },
          { label: "Saved", value: `$${latest.net_savings.toLocaleString()}`, color: "text-blue-600" },
          { label: "Savings Rate", value: `${savingsRate}%`, color: "text-purple-600" },
        ].map((stat) => (
          <div key={stat.label} className="bg-white rounded-xl p-6 shadow-sm">
            <p className="text-sm text-gray-500 mb-1">{stat.label}</p>
            <p className={`text-2xl font-bold ${stat.color}`}>{stat.value}</p>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-2 gap-6">
        <div className="bg-white rounded-xl p-6 shadow-sm">
          <h2 className="font-semibold text-gray-900 mb-4">Spending Trend</h2>
          <SpendingChart snapshots={snapshots} />
        </div>
        <div className="bg-white rounded-xl p-6 shadow-sm">
          <h2 className="font-semibold text-gray-900 mb-4">This Month by Category</h2>
          <CategoryBreakdown categories={latest.top_categories} />
        </div>
      </div>
    </div>
  );
}
