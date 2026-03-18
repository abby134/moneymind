"use client";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";

const CATEGORY_LABELS: Record<string, string> = {
  food_dining: "Food & Dining",
  groceries: "Groceries",
  rent_housing: "Rent",
  transport: "Transport",
  entertainment: "Entertainment",
  subscriptions: "Subscriptions",
  healthcare: "Healthcare",
  shopping: "Shopping",
  utilities: "Utilities",
  other: "Other",
};

export function CategoryBreakdown({ categories }: { categories: Record<string, number> }) {
  const data = Object.entries(categories)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 6)
    .map(([key, value]) => ({
      name: CATEGORY_LABELS[key] || key,
      amount: Math.round(value),
    }));

  return (
    <ResponsiveContainer width="100%" height={220}>
      <BarChart data={data} layout="vertical">
        <XAxis type="number" tick={{ fontSize: 12 }} tickFormatter={(v) => `$${v}`} />
        <YAxis type="category" dataKey="name" tick={{ fontSize: 12 }} width={90} />
        <Tooltip formatter={(v: number) => `$${v.toLocaleString()}`} />
        <Bar dataKey="amount" fill="#10b981" radius={[0, 4, 4, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}
