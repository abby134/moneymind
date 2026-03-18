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

### bank_accounts
One row per bank account the user registers. Supports multiple accounts per user.

| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| user_id | UUID FK → users | |
| nickname | VARCHAR(100) | e.g. "Chase Checking", "Amex Gold" |
| bank_name | VARCHAR(100) | e.g. "Chase", "Bank of America" |
| account_type | VARCHAR(20) | checking / savings / credit / investment |
| currency | VARCHAR(3) | default "USD" |
| is_active | BOOLEAN | soft delete |
| created_at | TIMESTAMPTZ | |

---

### csv_uploads
Tracks each file upload. A user may upload multiple CSVs per month (one per account).

| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| user_id | UUID FK → users | |
| account_id | UUID FK → bank_accounts | |
| month | DATE | first day of month, e.g. 2025-03-01 |
| original_filename | VARCHAR(255) | |
| row_count | INT | number of transactions parsed |
| status | VARCHAR(20) | uploaded / parsing / parsed / failed |
| uploaded_at | TIMESTAMPTZ | |
| parsed_at | TIMESTAMPTZ | NULL until processing done |

---

### monthly_snapshots
One row per user per month. Aggregates across ALL accounts.

| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| user_id | UUID FK → users | |
| month | DATE | first day of month |
| uploads_included | INT | how many CSV files were merged |
| total_income | NUMERIC(12,2) | excludes inter-account transfers |
| total_expenses | NUMERIC(12,2) | excludes inter-account transfers |
| net_savings | NUMERIC(12,2) | income - expenses |
| savings_rate | NUMERIC(5,4) | 0.0–1.0 |
| net_worth_estimate | NUMERIC(12,2) | optional, user-provided |
| top_categories | JSONB | {"food": 420, "rent": 1800, ...} |
| is_complete | BOOLEAN | false if user hasn't uploaded all accounts yet |
| created_at | TIMESTAMPTZ | |

---

### transactions
Raw line items from uploaded CSVs. Each row knows which account it came from.

| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| user_id | UUID FK → users | |
| account_id | UUID FK → bank_accounts | |
| upload_id | UUID FK → csv_uploads | |
| snapshot_id | UUID FK → monthly_snapshots | |
| date | DATE | |
| description | TEXT | raw bank description |
| amount | NUMERIC(12,2) | negative = expense, positive = income |
| category | VARCHAR(100) | AI-classified |
| subcategory | VARCHAR(100) | |
| merchant | VARCHAR(255) | cleaned merchant name |
| is_recurring | BOOLEAN | |
| is_transfer | BOOLEAN | inter-account transfer, excluded from totals |
| transfer_pair_id | UUID | links the two sides of a transfer (nullable) |
| is_flagged | BOOLEAN | anomaly or needs review |
| created_at | TIMESTAMPTZ | |

---

### subscriptions
Recurring charges identified by the Subscription Agent, across all accounts.

| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| user_id | UUID FK → users | |
| account_id | UUID FK → bank_accounts | which account it charges |
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
users
  ├── bank_accounts (1:N)
  │       │
  │       └── csv_uploads (1:N)
  │               │
  │               └── transactions (1:N)
  │
  ├── monthly_snapshots (1:N)   ← aggregates all accounts for that month
  │       │
  │       ├── transactions (1:N, via snapshot_id)
  │       ├── goal_checkpoints (1:N) ──── goals (N:1)
  │       ├── agent_runs (1:1)
  │       └── reports (1:1)
  │
  ├── subscriptions (1:N)
  └── goals (1:N)
```

---

## Multi-Account Upload Flow

```
User has 3 accounts: Chase Checking, BofA Savings, Amex Credit

March upload sequence:
  1. Upload Chase CSV   → csv_uploads row, transactions parsed
  2. Upload BofA CSV    → csv_uploads row, transactions parsed
  3. Upload Amex CSV    → csv_uploads row, transactions parsed
  4. User clicks "Run Analysis for March"
       │
       ▼
  Planner Agent merges all three, runs Transfer Detection Agent
       │
       ▼
  Transfer Detection Agent finds:
    Chase: -$500 "Transfer to Savings"  ←──┐ same amount
    BofA:  +$500 "Transfer from Chase"  ←──┘ same date ±2 days
    → marks both as is_transfer=true, links via transfer_pair_id
       │
       ▼
  monthly_snapshot calculated excluding transfers
  uploads_included = 3, is_complete = true
```

---

## Memory MCP Schema (Knowledge Graph)

Separate from PostgreSQL. Stores behavioral patterns and insights.

```json
{
  "entities": [
    {
      "name": "user_abby_spending_pattern",
      "entityType": "behavioral_pattern",
      "observations": [
        "Overspends on food delivery every March",
        "Savings rate drops below 15% in Q4 consistently",
        "Has broken the 'reduce dining out' goal 2 times"
      ]
    },
    {
      "name": "account_chase_checking",
      "entityType": "bank_account",
      "observations": [
        "Primary spending account",
        "Rent always paid from this account on the 1st",
        "Regular transfer of ~$500 to BofA Savings each month"
      ]
    },
    {
      "name": "goal_house_downpayment",
      "entityType": "financial_goal",
      "observations": [
        "Set in 2025-01 with target $50,000 by 2027-06",
        "On track as of 2025-11",
        "Contributions come from BofA Savings account"
      ]
    }
  ],
  "relations": [
    {
      "from": "user_abby_spending_pattern",
      "to": "goal_house_downpayment",
      "relationType": "threatens_when_triggered"
    },
    {
      "from": "account_chase_checking",
      "to": "account_bofa_savings",
      "relationType": "regular_transfer_to"
    }
  ]
}
```

**Why Memory MCP instead of just PostgreSQL:**
PostgreSQL stores raw facts. Memory MCP stores *interpreted meaning* — the agent's understanding of who this user is financially, including cross-account behavioral patterns.
