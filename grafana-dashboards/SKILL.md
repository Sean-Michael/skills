---
name: grafana-dashboards
description: >
  Use when building, editing, or reviewing Grafana dashboards. Triggers include:
  any request to create a dashboard, add panels, write PromQL or LogQL for 
  visualization, design an observability layout, or improve an existing dashboard.
  Also use when the user mentions Grafana alongside Mimir, Prometheus, Loki, or 
  any LGTM-stack component.
---

# Grafana Dashboard Engineering

## Live Data Access — Do This First
Before writing any dashboard JSON or panel query:

1. Find the Prometheus/Mimir (or Loki) endpoint. Ask the user, or discover it
   by exploring the environment: `kubectl get svc -A`, existing Grafana
   datasource config, in-cluster DNS, port-forwards, environment variables.

2. Validate **every** PromQL/LogQL query against that live endpoint before
   committing it to a panel. A query that returns no data or an error must be
   fixed or escalated — never silently written into a dashboard.

Never write a panel with an unvalidated query.

---

## Dashboard Structure

### Header Row (always first)
- 3–5 `Stat` panels covering the most critical KPIs for the subject domain.
- Use `background` color mode, not `value`.
- Thresholds must be meaningful: Green = healthy, Yellow = degraded, Red = action required.
- This row answers the 5-second rule (see below) on its own.

### Section Separators
- Use `Text` panels as H2-level row headers to divide logical groups
  (e.g., "Ingestion", "Query Latency", "Error Budget", "Cardinality").
- Never stack 20+ panels without separators.

### Drill-down Flow
Top → aggregate health  
Middle → per-component or per-service breakdown  
Bottom → raw logs and traces panels

---

## Variables — Every Dashboard

```
datasource   type: datasource    query: prometheus
cluster      type: query         query: label_values(up, cluster)
namespace    type: query         chained on $cluster
interval     type: interval      values: 1m,5m,15m,30m,1h
```

- All panels use `$datasource` — never hardcoded datasource UIDs.
- All label matchers include `{cluster="$cluster", namespace="$namespace"}`.
- Drill-down links carry `$cluster`, `$namespace`, and the current time range
  into the target dashboard via variable interpolation.

---

## PromQL Hygiene

- Use `$__rate_interval` for `rate()` and `increase()` — never hardcoded windows.
- **Use `p95` or `p99` for all latency metrics. Never `avg`.** Averages hide
  tail latency and produce misleading on-call signals.
- Prefer recording-rule-backed metrics over raw counter math where available.
- Every panel description must answer: "What does this measure, and what should
  I do if it's red?"

---

## Units

Every panel must have explicit units — never leave units as "short" or unset.

| Signal       | Unit                        |
|--------------|-----------------------------|
| Latency      | `ms` or `s`                 |
| Throughput   | `reqps`                     |
| Memory/Disk  | `bytes` (Grafana auto-scales)|
| CPU          | `percent (0-100)` or `cores`|
| Error rate   | `percent (0.0-1.0)` or `pps`|

---

## Visual Standards

- **Time series**: default panel type for trends; use `fill below to 0` for
  error rate bands.
- **Stat panels**: `background` color mode for header KPIs; set
  `transparent: true` so background colors pop.
- **Tables**: hide redundant columns; set explicit column widths.
- **Multi-series color**: use Grafana's `Classic palette`.
- **Threshold colors** (fixed): `red=#F2495C`, `yellow=#FFB357`, `green=#73BF69`.
- Never use random or unspecified colors.
- Whitespace is intentional — use it to reduce cognitive load between sections.

---

## The 5-Second Rule

> A dashboard passes if an on-call engineer can determine whether the system
> is healthy within 5 seconds of opening it.

Design every dashboard to this standard:

- Every panel: title ≤ 6 words, description 1–2 sentences.
- No legend with > 8 series unless a filtering variable narrows it.
- Empty panels show `No value` — never blank.
- The header stat row must be sufficient for the 5-second assessment on its own.

---

## Drill-down Links

Every high-level summary panel should link forward to detail. Examples:

- Aggregate error rate stat → time series breakdown dashboard
- Service p99 latency → Tempo traces filtered to that service
- Pod restart count → Loki logs filtered to that pod

Links must use variable interpolation (`$cluster`, `$namespace`, current time
range). Never hardcode a time range or UID in a data link.

---

## Output Format

1. **Dashboard JSON** — valid, ready to POST to `/api/dashboards/db` or apply
   via the Grafana operator `GrafanaDashboard` CRD.
2. Variable definitions embedded in the JSON.
3. Brief panel-by-panel rationale after the JSON for any non-obvious choices.

When the Grafana MCP is available in context, prefer creating/updating
dashboards via the MCP over returning raw JSON.

---

## Anti-patterns

- Hardcoded datasource UIDs or time ranges
- `rate()[1m]` — always `$__rate_interval`
- `avg` for latency — always `p95` or `p99`
- Missing units on any panel
- Unvalidated queries committed to panels
- 20+ panels without section separators
- Missing header KPI row
- Drill-down links without variable interpolation