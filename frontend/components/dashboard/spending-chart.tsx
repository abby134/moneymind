"use client";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from "recharts";
import { MonthlySnapshot } from "@/lib/api";
import { format } from "date-fns";

export function SpendingChart({ snapshots }: { snapshots: MonthlySnapshot[] }) {
  const data = [...snapshots].reverse().map((s) => ({
    month: format(new Date(s.month), "MMM yy"),
    Income: s.total_income,
    Expenses: s.total_expenses,
    Saved: s.net_savings,
  }));

  return (
    <ResponsiveContainer width="100%" height={220}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
        <XAxis dataKey="month" tick={{ fontSize: 12 }} />
        <YAxis tick={{ fontSize: 12 }} tickFormatter={(v) => `$${(v / 1000).toFixed(0)}k`} />
        <Tooltip formatter={(v: number) => `$${v.toLocaleString()}`} />
        <Legend />
        <Line type="monotone" dataKey="Income" stroke="#10b981" strokeWidth={2} dot={false} />
        <Line type="monotone" dataKey="Expenses" stroke="#ef4444" strokeWidth={2} dot={false} />
        <Line type="monotone" dataKey="Saved" stroke="#6366f1" strokeWidth={2} dot={false} />
      </LineChart>
    </ResponsiveContainer>
  );
}
