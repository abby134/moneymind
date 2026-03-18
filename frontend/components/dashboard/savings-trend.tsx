"use client";
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import { MonthlySnapshot } from "@/lib/api";
import { format } from "date-fns";

export function SavingsTrend({ snapshots }: { snapshots: MonthlySnapshot[] }) {
  const data = [...snapshots].reverse().map((s) => ({
    month: format(new Date(s.month), "MMM yy"),
    savings: s.net_savings,
    rate: (s.savings_rate * 100).toFixed(1),
  }));

  return (
    <ResponsiveContainer width="100%" height={220}>
      <AreaChart data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
        <XAxis dataKey="month" tick={{ fontSize: 12 }} />
        <YAxis tick={{ fontSize: 12 }} tickFormatter={(v) => `$${(v / 1000).toFixed(0)}k`} />
        <Tooltip formatter={(v: number) => `$${v.toLocaleString()}`} />
        <Area
          type="monotone"
          dataKey="savings"
          stroke="#10b981"
          fill="#d1fae5"
          strokeWidth={2}
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}
