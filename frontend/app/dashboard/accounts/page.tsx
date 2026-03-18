"use client";
import { useEffect, useState } from "react";
import { api, BankAccount } from "@/lib/api";

const ACCOUNT_TYPES = ["checking", "savings", "credit", "investment"];
const BANKS = ["Chase", "Bank of America", "Wells Fargo", "Citi", "Capital One", "American Express", "Other"];

export default function AccountsPage() {
  const [accounts, setAccounts] = useState<BankAccount[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ nickname: "", bank_name: "", account_type: "checking" });
  const [loading, setLoading] = useState(false);

  async function load() {
    const data = await api.accounts.list();
    setAccounts(data);
  }

  useEffect(() => { load(); }, []);

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    try {
      await api.accounts.create(form);
      setShowForm(false);
      setForm({ nickname: "", bank_name: "", account_type: "checking" });
      await load();
    } finally {
      setLoading(false);
    }
  }

  async function handleDelete(id: string) {
    await api.accounts.delete(id);
    await load();
  }

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Bank Accounts</h1>
          <p className="text-gray-500">Manage the accounts you upload CSVs from</p>
        </div>
        <button
          onClick={() => setShowForm(!showForm)}
          className="bg-emerald-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-emerald-700 transition"
        >
          + Add account
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleCreate} className="bg-white rounded-xl p-6 shadow-sm space-y-4">
          <h2 className="font-semibold text-gray-900">New account</h2>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Nickname</label>
            <input
              value={form.nickname}
              onChange={(e) => setForm({ ...form, nickname: e.target.value })}
              placeholder="e.g. Chase Checking"
              className="w-full border border-gray-300 rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-emerald-500"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Bank</label>
            <select
              value={form.bank_name}
              onChange={(e) => setForm({ ...form, bank_name: e.target.value })}
              className="w-full border border-gray-300 rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-emerald-500"
              required
            >
              <option value="">Select bank...</option>
              {BANKS.map((b) => <option key={b} value={b}>{b}</option>)}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Account type</label>
            <select
              value={form.account_type}
              onChange={(e) => setForm({ ...form, account_type: e.target.value })}
              className="w-full border border-gray-300 rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-emerald-500"
            >
              {ACCOUNT_TYPES.map((t) => <option key={t} value={t}>{t}</option>)}
            </select>
          </div>
          <div className="flex gap-3">
            <button type="submit" disabled={loading} className="bg-emerald-600 text-white px-6 py-2.5 rounded-lg font-medium hover:bg-emerald-700 disabled:opacity-50">
              {loading ? "Saving..." : "Save"}
            </button>
            <button type="button" onClick={() => setShowForm(false)} className="border border-gray-300 text-gray-700 px-6 py-2.5 rounded-lg font-medium hover:bg-gray-50">
              Cancel
            </button>
          </div>
        </form>
      )}

      <div className="space-y-3">
        {accounts.length === 0 && (
          <div className="text-center py-12 text-gray-400">No accounts yet. Add one to get started.</div>
        )}
        {accounts.map((account) => (
          <div key={account.id} className="bg-white rounded-xl p-5 shadow-sm flex items-center justify-between">
            <div>
              <p className="font-medium text-gray-900">{account.nickname}</p>
              <p className="text-sm text-gray-500">{account.bank_name} · {account.account_type} · {account.currency}</p>
            </div>
            <button
              onClick={() => handleDelete(account.id)}
              className="text-sm text-gray-400 hover:text-red-500 transition"
            >
              Remove
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
