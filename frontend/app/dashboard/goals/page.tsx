"use client";
import { useEffect, useState } from "react";
import { api, Goal } from "@/lib/api";
import { format, differenceInDays } from "date-fns";

// ── helpers ──────────────────────────────────────────────────────────────────

function progressPercent(goal: Goal) {
  return Math.min(100, Math.round((goal.current_amount / goal.target_amount) * 100));
}

function daysLeft(goal: Goal) {
  return differenceInDays(new Date(goal.target_date), new Date());
}

function monthsNeeded(goal: Goal) {
  const remaining = goal.target_amount - goal.current_amount;
  const days = daysLeft(goal);
  if (days <= 0 || remaining <= 0) return null;
  const months = days / 30;
  return (remaining / months).toFixed(0);
}

function statusColor(status: Goal["status"]) {
  return {
    active: "bg-emerald-100 text-emerald-800",
    achieved: "bg-blue-100 text-blue-800",
    abandoned: "bg-gray-100 text-gray-500",
  }[status];
}

function progressColor(pct: number) {
  if (pct >= 100) return "bg-blue-500";
  if (pct >= 60) return "bg-emerald-500";
  if (pct >= 30) return "bg-yellow-400";
  return "bg-red-400";
}

// ── sub-components ────────────────────────────────────────────────────────────

function GoalCard({
  goal,
  onUpdate,
  onDelete,
}: {
  goal: Goal;
  onUpdate: (id: string, amount: number) => void;
  onDelete: (id: string) => void;
}) {
  const [editing, setEditing] = useState(false);
  const [newAmount, setNewAmount] = useState(String(goal.current_amount));
  const [saving, setSaving] = useState(false);

  const pct = progressPercent(goal);
  const days = daysLeft(goal);
  const needed = monthsNeeded(goal);
  const isActive = goal.status === "active";

  async function handleSave() {
    setSaving(true);
    await onUpdate(goal.id, parseFloat(newAmount));
    setEditing(false);
    setSaving(false);
  }

  return (
    <div className={`bg-white rounded-2xl shadow-sm p-6 ${goal.status === "abandoned" ? "opacity-50" : ""}`}>
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div>
          <h3 className="font-semibold text-gray-900 text-lg">{goal.name}</h3>
          <p className="text-sm text-gray-400 mt-0.5">
            Target: {format(new Date(goal.target_date), "MMM d, yyyy")}
            {days > 0 ? ` · ${days} days left` : " · Overdue"}
          </p>
        </div>
        <span className={`text-xs font-medium px-2.5 py-1 rounded-full ${statusColor(goal.status)}`}>
          {goal.status}
        </span>
      </div>

      {/* Progress bar */}
      <div className="mb-4">
        <div className="flex justify-between text-sm mb-1.5">
          <span className="text-gray-600">
            ${goal.current_amount.toLocaleString()}
          </span>
          <span className="font-medium text-gray-900">
            ${goal.target_amount.toLocaleString()}
          </span>
        </div>
        <div className="w-full bg-gray-100 rounded-full h-3">
          <div
            className={`h-3 rounded-full transition-all duration-500 ${progressColor(pct)}`}
            style={{ width: `${pct}%` }}
          />
        </div>
        <div className="flex justify-between text-xs text-gray-400 mt-1">
          <span>{pct}% complete</span>
          <span>${(goal.target_amount - goal.current_amount).toLocaleString()} to go</span>
        </div>
      </div>

      {/* Monthly needed callout */}
      {isActive && needed && days > 0 && (
        <div className="bg-emerald-50 rounded-lg px-4 py-2.5 mb-4 text-sm text-emerald-800">
          Save <strong>${Number(needed).toLocaleString()}/month</strong> to hit your goal on time
        </div>
      )}

      {/* Checkpoint history */}
      {goal.checkpoints.length > 0 && (
        <div className="mb-4">
          <p className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-2">History</p>
          <div className="space-y-1.5 max-h-28 overflow-y-auto">
            {goal.checkpoints.map((cp) => (
              <div key={cp.id} className="flex items-center justify-between text-sm">
                <span className="text-gray-500">
                  {format(new Date(cp.recorded_at), "MMM yyyy")}
                </span>
                <div className="flex items-center gap-2">
                  <span className="text-gray-900">${cp.amount_at_checkpoint.toLocaleString()}</span>
                  <span className={cp.on_track ? "text-emerald-500 text-xs" : "text-red-400 text-xs"}>
                    {cp.on_track ? "✓ on track" : `${cp.variance > 0 ? "+" : ""}$${Math.round(cp.variance).toLocaleString()} off`}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Actions */}
      {isActive && (
        <div className="flex gap-2 pt-2 border-t border-gray-100">
          {editing ? (
            <>
              <input
                type="number"
                value={newAmount}
                onChange={(e) => setNewAmount(e.target.value)}
                className="flex-1 border border-gray-300 rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500"
                placeholder="Current amount"
              />
              <button
                onClick={handleSave}
                disabled={saving}
                className="bg-emerald-600 text-white px-4 py-1.5 rounded-lg text-sm font-medium hover:bg-emerald-700 disabled:opacity-50"
              >
                {saving ? "Saving..." : "Save"}
              </button>
              <button
                onClick={() => setEditing(false)}
                className="border border-gray-200 text-gray-600 px-3 py-1.5 rounded-lg text-sm hover:bg-gray-50"
              >
                Cancel
              </button>
            </>
          ) : (
            <>
              <button
                onClick={() => setEditing(true)}
                className="flex-1 border border-gray-200 text-gray-700 py-1.5 rounded-lg text-sm font-medium hover:bg-gray-50 transition"
              >
                Update amount
              </button>
              <button
                onClick={() => onDelete(goal.id)}
                className="text-gray-400 hover:text-red-500 px-3 py-1.5 text-sm transition"
              >
                Abandon
              </button>
            </>
          )}
        </div>
      )}

      {goal.status === "achieved" && goal.achieved_at && (
        <p className="text-sm text-blue-600 font-medium pt-2 border-t border-gray-100">
          Achieved on {format(new Date(goal.achieved_at), "MMM d, yyyy")} 🎉
        </p>
      )}
    </div>
  );
}

function NewGoalForm({ onCreated }: { onCreated: () => void }) {
  const [form, setForm] = useState({
    name: "",
    target_amount: "",
    current_amount: "0",
    target_date: "",
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      await api.goals.create({
        name: form.name,
        target_amount: parseFloat(form.target_amount),
        current_amount: parseFloat(form.current_amount),
        target_date: form.target_date,
      });
      setForm({ name: "", target_amount: "", current_amount: "0", target_date: "" });
      onCreated();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to create goal");
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="bg-white rounded-2xl shadow-sm p-6 border-2 border-dashed border-emerald-200">
      <h3 className="font-semibold text-gray-900 mb-4">New goal</h3>
      <div className="space-y-3">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Goal name</label>
          <input
            value={form.name}
            onChange={(e) => setForm({ ...form, name: e.target.value })}
            placeholder="e.g. House down payment"
            className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500"
            required
          />
        </div>
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Target amount ($)</label>
            <input
              type="number"
              value={form.target_amount}
              onChange={(e) => setForm({ ...form, target_amount: e.target.value })}
              placeholder="50000"
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Already saved ($)</label>
            <input
              type="number"
              value={form.current_amount}
              onChange={(e) => setForm({ ...form, current_amount: e.target.value })}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500"
            />
          </div>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Target date</label>
          <input
            type="date"
            value={form.target_date}
            onChange={(e) => setForm({ ...form, target_date: e.target.value })}
            className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500"
            required
          />
        </div>
        {error && <p className="text-red-500 text-sm">{error}</p>}
        <button
          type="submit"
          disabled={loading}
          className="w-full bg-emerald-600 text-white py-2.5 rounded-lg text-sm font-semibold hover:bg-emerald-700 transition disabled:opacity-50"
        >
          {loading ? "Creating..." : "Create goal"}
        </button>
      </div>
    </form>
  );
}

// ── page ──────────────────────────────────────────────────────────────────────

export default function GoalsPage() {
  const [goals, setGoals] = useState<Goal[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [loading, setLoading] = useState(true);

  async function load() {
    const data = await api.goals.list();
    setGoals(data);
    setLoading(false);
  }

  useEffect(() => { load(); }, []);

  async function handleUpdate(id: string, amount: number) {
    await api.goals.update(id, { current_amount: amount });
    await load();
  }

  async function handleDelete(id: string) {
    await api.goals.delete(id);
    await load();
  }

  const active = goals.filter((g) => g.status === "active");
  const achieved = goals.filter((g) => g.status === "achieved");
  const abandoned = goals.filter((g) => g.status === "abandoned");

  // Summary stats
  const totalTargeted = active.reduce((s, g) => s + g.target_amount, 0);
  const totalSaved = active.reduce((s, g) => s + g.current_amount, 0);
  const overallPct = totalTargeted > 0 ? Math.round((totalSaved / totalTargeted) * 100) : 0;

  if (loading) return <div className="text-center py-20 text-gray-400">Loading...</div>;

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Financial Goals</h1>
          <p className="text-gray-500">Track progress toward what matters most</p>
        </div>
        <button
          onClick={() => setShowForm(!showForm)}
          className="bg-emerald-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-emerald-700 transition"
        >
          + New goal
        </button>
      </div>

      {/* Summary bar — only when there are active goals */}
      {active.length > 0 && (
        <div className="bg-white rounded-2xl shadow-sm p-6">
          <div className="flex items-center justify-between mb-3">
            <div>
              <p className="text-sm text-gray-500">Total across {active.length} active goal{active.length !== 1 ? "s" : ""}</p>
              <p className="text-2xl font-bold text-gray-900 mt-0.5">
                ${totalSaved.toLocaleString()}
                <span className="text-base font-normal text-gray-400"> / ${totalTargeted.toLocaleString()}</span>
              </p>
            </div>
            <span className="text-3xl font-bold text-emerald-600">{overallPct}%</span>
          </div>
          <div className="w-full bg-gray-100 rounded-full h-3">
            <div
              className="h-3 rounded-full bg-emerald-500 transition-all duration-500"
              style={{ width: `${overallPct}%` }}
            />
          </div>
        </div>
      )}

      {/* New goal form */}
      {showForm && (
        <NewGoalForm
          onCreated={() => { setShowForm(false); load(); }}
        />
      )}

      {/* Active goals */}
      {active.length === 0 && !showForm && (
        <div className="text-center py-16 text-gray-400">
          <p className="text-lg mb-3">No active goals yet</p>
          <button
            onClick={() => setShowForm(true)}
            className="text-emerald-600 font-medium hover:underline"
          >
            Create your first goal
          </button>
        </div>
      )}

      {active.length > 0 && (
        <div>
          <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-3">
            Active · {active.length}
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {active.map((goal) => (
              <GoalCard
                key={goal.id}
                goal={goal}
                onUpdate={handleUpdate}
                onDelete={handleDelete}
              />
            ))}
          </div>
        </div>
      )}

      {/* Achieved goals */}
      {achieved.length > 0 && (
        <div>
          <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-3">
            Achieved · {achieved.length}
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {achieved.map((goal) => (
              <GoalCard
                key={goal.id}
                goal={goal}
                onUpdate={handleUpdate}
                onDelete={handleDelete}
              />
            ))}
          </div>
        </div>
      )}

      {/* Abandoned goals */}
      {abandoned.length > 0 && (
        <div>
          <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-3">
            Abandoned · {abandoned.length}
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {abandoned.map((goal) => (
              <GoalCard
                key={goal.id}
                goal={goal}
                onUpdate={handleUpdate}
                onDelete={handleDelete}
              />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
