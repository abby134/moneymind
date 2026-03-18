const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("token");
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = getToken();
  const res = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    },
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Request failed" }));
    throw new Error(err.detail || "Request failed");
  }
  return res.json();
}

export const api = {
  auth: {
    register: (data: { email: string; name: string; password: string }) =>
      request<{ access_token: string }>("/api/auth/register", {
        method: "POST",
        body: JSON.stringify(data),
      }),
    login: (data: { email: string; password: string }) =>
      request<{ access_token: string }>("/api/auth/login", {
        method: "POST",
        body: JSON.stringify(data),
      }),
    me: () => request<{ id: string; email: string; name: string }>("/api/auth/me"),
  },
  accounts: {
    list: () => request<BankAccount[]>("/api/accounts/"),
    create: (data: { nickname: string; bank_name: string; account_type: string }) =>
      request<BankAccount>("/api/accounts/", { method: "POST", body: JSON.stringify(data) }),
    delete: (id: string) => request(`/api/accounts/${id}`, { method: "DELETE" }),
  },
  uploads: {
    upload: async (accountId: string, month: string, file: File) => {
      const token = getToken();
      const form = new FormData();
      form.append("account_id", accountId);
      form.append("month", month);
      form.append("file", file);
      const res = await fetch(`${API_URL}/api/uploads/`, {
        method: "POST",
        headers: token ? { Authorization: `Bearer ${token}` } : {},
        body: form,
      });
      if (!res.ok) throw new Error("Upload failed");
      return res.json();
    },
  },
  snapshots: {
    list: () => request<MonthlySnapshot[]>("/api/snapshots/"),
    analyze: (id: string) =>
      request<AgentRun>(`/api/snapshots/${id}/analyze`, { method: "POST" }),
  },
  reports: {
    list: () => request<Report[]>("/api/reports/"),
    get: (id: string) => request<Report>(`/api/reports/${id}`),
  },
  goals: {
    list: () => request<Goal[]>("/api/goals/"),
    create: (data: { name: string; target_amount: number; current_amount: number; target_date: string }) =>
      request<Goal>("/api/goals/", { method: "POST", body: JSON.stringify(data) }),
    update: (id: string, data: { current_amount?: number; status?: string }) =>
      request<Goal>(`/api/goals/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
    delete: (id: string) => request(`/api/goals/${id}`, { method: "DELETE" }),
  },
};

export interface BankAccount {
  id: string;
  nickname: string;
  bank_name: string;
  account_type: string;
  currency: string;
  is_active: boolean;
}

export interface MonthlySnapshot {
  id: string;
  month: string;
  uploads_included: number;
  total_income: number;
  total_expenses: number;
  net_savings: number;
  savings_rate: number;
  top_categories: Record<string, number>;
  is_complete: boolean;
}

export interface Report {
  id: string;
  snapshot_id: string;
  content_md: string;
  created_at: string;
}

export interface AgentRun {
  id: string;
  status: string;
  agents_invoked: string[];
  fact_check_flags: unknown[];
}

export interface GoalCheckpoint {
  id: string;
  amount_at_checkpoint: number;
  on_track: boolean;
  variance: number;
  recorded_at: string;
}

export interface Goal {
  id: string;
  name: string;
  target_amount: number;
  current_amount: number;
  target_date: string;
  status: "active" | "achieved" | "abandoned";
  created_at: string;
  achieved_at: string | null;
  checkpoints: GoalCheckpoint[];
}
