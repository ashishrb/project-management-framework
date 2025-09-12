## GAP SCAN — Application Assessment

This assessment inventories current pages, routes, APIs, models, and websockets; highlights mock/static data usage; and proposes a minimal change plan aligned to the Prime Rules and enhancement scope.

### Inventory

- Pages (templates/*) and primary scripts (static/js/*):
  - Home (`home.html`)
  - Dashboard (`dashboard.html`) → `static/js/dashboard.js`
  - Comprehensive Dashboard (`comprehensive_dashboard.html`) → `static/js/comprehensive_dashboard.js`
  - Projects (`projects.html`) → `static/js/projects.js`
  - Project Detail (`project_detail.html`) → `static/js/project_detail.js`
  - Resources (`resources.html`) → `static/js/projects.js` (shared patterns)
  - Backlog (`backlog.html`) → `static/js/backlog.js`
  - Work Plan (`work_plan.html`) → `static/js/work_plan.js`
  - Risks (`risk_management.html`)
  - Gantt (`gantt_chart.html`)
  - Reports (`generic.html`)
  - AI Copilot (`ai_copilot.html`) → `static/js/ai_copilot.js`

- API routers (under `/api/v1`):
  - projects.py (CRUD; tasks/features; backlog items)
  - dashboards.py (summary metrics; genai metrics)
  - analytics.py (trend, predictive, comparative, real-time, export)
  - comprehensive_dashboard.py (KPI + charts)
  - ai_analysis.py, ai_dashboard.py, ai_insights.py, ai_copilot.py, ai.py, ai_services.py
  - lookup.py, resources.py, features.py, risks.py, backlogs.py
  - rag.py (RAG orchestration), logs.py (frontend logging), performance.py, monitoring.py, health.py, reports.py, user.py, approval_workflow.py, file_upload.py

- Websockets (`/ws/*`):
  - `/ws/dashboard`, `/ws/projects`, `/ws/resources`, `/ws/risks`, `/ws/general`
  - HTTP helpers: `/ws/stats`, `/ws/broadcast`, `/ws/queue`

- Models (SQLAlchemy):
  - Core tables: Project, Task, Feature, Backlog, Resource, Risk, Approval, Charter
  - Lookups: Function, Platform, Priority, Status, Portfolio, Application, InvestmentType, JourneyMap, ProjectType, ProjectStatusClassification, ProjectPriorityClassification, ProjectCriticalityLevel, BusinessUnit, InvestmentClass, BenefitCategory
  - Project detail models and lookups for comprehensive view
  - Junctions: ProjectFunction/Platform, TaskFunction/Platform/Resource, FeatureFunction/Platform, ProjectResource

### Current Mock/Static Data Usage

- Work Plan (`work_plan.js`):
  - Uses `sampleTasks` (static) for Gantt and task list. Not yet bound to `/api/v1/projects/{id}/tasks`.

- AI Analysis (`ai_analysis.py` responses):
  - Returns rich HTML strings (mock analysis) instead of structured JSON; UI panels render provided HTML directly.

- Some dashboard sub-tabs (comprehensive) synthesize demo-like tables/charts in JS where API coverage is not yet complete.

### Minimal Change Plan (by file/function)

1) Configuration & DEMO_MODE
   - `app/config.py`: add `DEMO_MODE: bool = True/False` (read from env). Expose via `settings`.
   - `app/api/v1/endpoints/projects.py:get_projects`: when `settings.DEMO_MODE`, apply `ORDER BY updated_at DESC LIMIT 10` server-side. Do not mutate DB.
   - Dashboards/analytics endpoints: when DEMO_MODE, scope aggregates to the same 10 project IDs.

2) Auth + Roles + Demo Users
   - Create `templates/login.html`; add SSR route in `app/routes/views.py`.
   - Add `/api/v1/auth/login` endpoint to verify creds, issue httpOnly cookie (compatible with current security middleware).
   - Add roles enum: OWNER, PORTFOLIO, ADMIN; create `User`, `Role`, `UserRole` models/migration if missing.
   - Add RBAC guard middleware in `app/middleware/security.py` or dedicated dependency in `app/api/deps.py` (e.g., `require_roles`).
   - Landing routes per role: add SSR endpoints `/dashboard/manager`, `/dashboard/portfolio`, `/admin` and role-aware nav fragments in `base.html` (Jinja conditionals). 
   - `/api/v1/admin/seed-demo` (ADMIN-only): insert demo users and assign OWNER to 10 most-recent projects; generate sprints/tasks/risks for charts.

3) Data-binding cleanup
   - Work Plan: add `/api/v1/projects/{id}/tasks` if gaps; include `start_date` and `due_date`. Update `work_plan.js` to fetch tasks for the selected project; keep SSR shell and controls.
   - AI analysis: refactor `ai_analysis.py` endpoints to return JSON structures `{insights:[...], metrics:{...}, evidence:[...], links:[...]}` while preserving route signatures; update `comprehensive_dashboard.js` to render via client-side templates. Keep SSR panels.

4) Manager & Portfolio dashboards
   - Add SSR pages: `templates/manager_dashboard.html`, `templates/portfolio_dashboard.html`; routes in `app/routes/views.py`.
   - Backing endpoints (extend existing):
     - Manager KPIs: augment `/api/v1/dashboards/summary-metrics` to accept `owner_user_id` filter; or add `/api/v1/dashboards/manager-kpis`.
     - Analytics helpers for velocity, risk matrix if missing; otherwise adapt existing endpoints with query params.
   - Chart click handlers (in `dashboard.js`/new JS) route to SSR pages with query params; add breadcrumbs.

5) AI Assistant (command bar)
   - UI: right-side panel attached to `base.html` (hidden by default) and `static/js/ai_copilot.js` as controller.
   - Server: orchestrator endpoint under `/api/v1/ai/copilot/command` that translates intent to existing endpoint calls; respects RBAC; redact PII.
   - Use existing AI service adapter and RAG grounding; respond with JSON including `sources`.

6) AI Analytics (self-intelligence)
   - Add `/api/v1/analytics/insights` to compute: health score, anomalies, spillover risk; return JSON `{insights:[{score, drivers, links}]}`.
   - UI: show chips on dashboard cards; click applies filters or navigates.

7) Websockets live refresh
   - On mutations in projects/tasks/risks endpoints, broadcast minimal change events via `/ws/{room}` using `connection_manager`.
   - In `dashboard.js`, `projects.js`, attach idempotent handlers to patch in-place state.

8) Admin Lite
   - `/admin` SSR to view users/roles and run demo seed (button calls `/api/v1/admin/seed-demo`).
   - Activity log viewer reading from existing logs with filters.

### Notes

- All enhancements are additive and reuse existing endpoints/styles; SSR shells remain intact; JS entry files preserved.
- DEMO_MODE is server-side filtering only; no DB writes.
- Role landing preserves UX while aligning with RBAC and acceptance checklist.


