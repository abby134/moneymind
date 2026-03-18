# MoneyMind — Entity Relationship Diagram

## Tables

### users
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| email | VARCHAR(255) UNIQUE | |
| name | VARCHAR(100) | |
| timezone | VARCHAR(50) | for reminder scheduling |
| income_range | VARCHAR(50) | e.g. "50k-75k" |
| created_at | TIMESTAMPTZ | |
| updated_at | TIMESTAMPTZ | |

---

### monthly_snapshots
One row per user per month. The core longitudinal record.

| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| user_id | UUID FK → users | |
| month | DATE | first day of month |
| total_income | NUMERIC(12,2) | |
| total_expenses | NUMERIC(12,2) | |
| net_savings | NUMERIC(12,2) | income - expenses |
| savings_rate | NUMERIC(5,4) | 0.0–1.0 |
| net_worth_estimate | NUMERIC(12,2) | optional, user-provided |
| top_categories | JSONB | {"food": 420, "rent": 1800, ...} |
| created_at | TIMESTAMPTZ | |

---

### transactions
Raw line items from uploaded CSV.

| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| user_id | UUID FK → users | |
| snapshot_id | UUID FK → monthly_snapshots | |
| date | DATE | |
| description | TEXT | raw bank description |
| amount | NUMERIC(12,2) | negative = expense |
| category | VARCHAR(100) | AI-classified |
| subcategory | VARCHAR(100) | |
| merchant | VARCHAR(255) | cleaned merchant name |
| is_recurring | BOOLEAN | |
| is_flagged | BOOLEAN | anomaly or review needed |
| created_at | TIMESTAMPTZ | |

---

### subscriptions
Recurring charges identified by the Subscription Agent.

| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| user_id | UUID FK → users | |
| name | VARCHAR(255) | e.g. "Netflix" |
| amount | NUMERIC(8,2) | monthly charge |
| billing_cycle | VARCHAR(20) | monthly / annual |
| first_detected | DATE | |
| last_seen | DATE | |
| status | VARCHAR(20) | active / zombie / cancelled |
| zombie_since | DATE | NULL if active |
| created_at | TIMESTAMPTZ | |

---

### goals
Financial goals tracked over time.

| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| user_id | UUID FK → users | |
| name | VARCHAR(255) | e.g. "House down payment" |
| target_amount | NUMERIC(12,2) | |
| current_amount | NUMERIC(12,2) | updated each month |
| target_date | DATE | |
| status | VARCHAR(20) | active / achieved / abandoned |
| created_at | TIMESTAMPTZ | |
| achieved_at | TIMESTAMPTZ | NULL if not yet |

---

### goal_checkpoints
Monthly progress snapshots for each goal.

| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| goal_id | UUID FK → goals | |
| snapshot_id | UUID FK → monthly_snapshots | |
| amount_at_checkpoint | NUMERIC(12,2) | |
| on_track | BOOLEAN | |
| variance | NUMERIC(12,2) | actual vs expected |
| recorded_at | TIMESTAMPTZ | |

---

### agent_runs
Audit log of every pipeline execution.

| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| user_id | UUID FK → users | |
| snapshot_id | UUID FK → monthly_snapshots | |
| status | VARCHAR(20) | pending / running / completed / failed |
| started_at | TIMESTAMPTZ | |
| completed_at | TIMESTAMPTZ | |
| agents_invoked | JSONB | ["planner","pattern","anomaly",...] |
| fact_check_flags | JSONB | claims that were corrected |
| error_message | TEXT | NULL if success |

---

### reports
Generated monthly narrative reports.

| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| user_id | UUID FK → users | |
| snapshot_id | UUID FK → monthly_snapshots | |
| agent_run_id | UUID FK → agent_runs | |
| content_md | TEXT | full markdown report |
| email_sent_at | TIMESTAMPTZ | NULL if not sent |
| viewed_at | TIMESTAMPTZ | NULL if not opened |
| created_at | TIMESTAMPTZ | |

---

## Relationships

```
users ──────────────────────────────────────────────────┐
  │                                                      │
  ├── monthly_snapshots (1:N)                            │
  │       │                                              │
  │       ├── transactions (1:N)                         │
  │       ├── goal_checkpoints (1:N) ──── goals (N:1) ───┤
  │       ├── agent_runs (1:1)                           │
  │       └── reports (1:1)                              │
  │                                                      │
  ├── subscriptions (1:N)                                │
  └── goals (1:N) ─────────────────────────────────────-┘
```

---

## Memory MCP Schema (Knowledge Graph)

Separate from PostgreSQL. Stores behavioral patterns and insights in a JSON knowledge graph.

```json
{
  "entities": [
    {
      "name": "user_abby_spending_pattern",
      "entityType": "behavioral_pattern",
      "observations": [
        "Overspends on food delivery every month 3 (March)",
        "Savings rate drops below 15% in Q4 consistently",
        "Has broken the 'reduce dining out' goal 2 times"
      ]
    },
    {
      "name": "goal_house_downpayment",
      "entityType": "financial_goal",
      "observations": [
        "Set in 2025-01 with target $50,000 by 2027-06",
        "On track as of 2025-11",
        "Contributions increased after salary raise in 2025-07"
      ]
    },
    {
      "name": "subscription_adobe",
      "entityType": "subscription",
      "observations": [
        "Charged $54.99/month since 2023-03",
        "No related transactions detected since 2024-09",
        "Flagged as zombie subscription 2025-02"
      ]
    }
  ],
  "relations": [
    {
      "from": "user_abby_spending_pattern",
      "to": "goal_house_downpayment",
      "relationType": "threatens_when_triggered"
    }
  ]
}
```

**Why Memory MCP instead of just PostgreSQL:**
PostgreSQL stores raw facts. Memory MCP stores *interpreted meaning* — the agent's understanding of who this user is financially. This is what enables the system to say "this is part of a pattern" rather than just "you spent $X."
