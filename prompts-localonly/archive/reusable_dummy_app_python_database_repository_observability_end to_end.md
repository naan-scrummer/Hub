# DUMMY APPLICATION BUILDER

## TECHNOLOGY — USER MUST DEFINE THIS FIRST

```yaml
Backend: Python
Frontend: CHOOSE_ONE
  - Vanilla JavaScript
  - React

Role: CHOOSE_ONE
  - Junior Software Engineer
  - Senior Software Engineer
  - Software Architect

Icons: Lucide Icons only
Database: SQLite for development / PostgreSQL for production by default
ORM: SQLAlchemy 2.x
Migrations: Alembic
Repository Pattern: Explicit repository classes
Local Deployment: Docker Compose when multiple services are required
Observability: Structured JSON logs + Grafana Loki by default
```

**The values at the top are the source of truth. Do not silently change them.**

---

# ROLE BEHAVIOR

### Junior Software Engineer
- Prefer simple, readable, maintainable implementations.
- Follow existing conventions.
- Avoid unnecessary abstraction and infrastructure.
- Ask before crucial architectural/product decisions.

### Senior Software Engineer
- Take stronger ownership of engineering decisions.
- Consider maintainability, testing, reliability, security, and scalability.
- Ask before major product, architectural, destructive, or irreversible decisions.

### Software Architect
- Analyze architecture, boundaries, integrations, data flow, scalability, security, reliability, and deployment.
- Explain important trade-offs.
- Ask before committing to major architectural or product decisions.
- Do not introduce enterprise complexity without a real requirement.

---

# PRIMARY OBJECTIVE

Build a realistic **dummy but functional application** with:

- Login.
- Authenticated application shell.
- Side navigation.
- Dashboard.
- KPI cards.
- Analytics.
- Multiple charts.
- Dummy but persistent data.
- Python backend.
- Selected frontend.
- Database-backed models.
- Repository layer.
- API/service layer.
- Structured logging.
- Local deployment.
- User testing after deployment.

The application should be easy to evolve from a prototype into a real application.

---

# CRITICAL DECISION GATE

Before making a decision that materially changes:

- Architecture.
- Database.
- Authentication.
- API contracts.
- Repository strategy.
- Deployment.
- Security.
- External dependencies.
- Data persistence.
- Existing functionality.

STOP and ask the user.

Use:

**Decision required**

**Context:** ...

**Option A:** ...

**Option B:** ...

**Recommendation:** ...

Wait for the user when the decision is genuinely consequential.

Do not interrupt for trivial coding choices.

---

# DATABASE ARCHITECTURE

Use a relational database.

## Development

Default to:

```text
SQLite
```

Advantages:

- Zero external database server.
- Easy local setup.
- Excellent for simple prototypes.
- Easy to replace with PostgreSQL through SQLAlchemy.

## Production

Default to:

```text
PostgreSQL
```

Do not change application business logic just because the database changes.

The database URL must be configuration-driven:

```text
DATABASE_URL
```

Never hardcode credentials.

---

# PYTHON MODEL LAYER — JPA-LIKE APPROACH

The user wants a Java JPA-style object/model approach.

Implement the equivalent using **SQLAlchemy ORM**.

Use declarative Python classes.

Conceptually:

```text
Python Class
      ↓
SQLAlchemy ORM Model
      ↓
Database Table
```

Example pattern:

```python
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True, index=True)
    name: Mapped[str]
```

Prefer SQLAlchemy 2.x typed declarative mappings where appropriate.

Keep models focused on persistence representation.

Do not place large amounts of business logic inside ORM models.

---

# REPOSITORY PATTERN

Use explicit repository classes between the service/business layer and SQLAlchemy.

Example:

```text
API
 ↓
Service
 ↓
Repository
 ↓
SQLAlchemy Session
 ↓
Database
```

Example repository responsibilities:

```text
UserRepository
DashboardRepository
ProjectRepository
ReportRepository
```

Repositories should handle:

- Create.
- Read.
- Update.
- Delete.
- Queries.
- Persistence-related operations.

Services should handle business rules.

Routes/controllers should handle HTTP concerns.

Do not put SQL queries directly into API route handlers unless the application is genuinely trivial and the user approves that simplification.

---

# SESSION MANAGEMENT

Use a clear database-session lifecycle.

For example:

```text
Request
  ↓
Database Session
  ↓
Repository
  ↓
Commit / Rollback
  ↓
Session Close
```

Do not create uncontrolled global database sessions.

Handle:

- Commit.
- Rollback.
- Connection errors.
- Transaction boundaries.

---

# DATABASE MIGRATIONS

Use **Alembic**.

Required principles:

- Models define the desired database structure.
- Alembic migrations evolve the database schema.
- Do not delete/recreate production tables automatically.
- Do not depend on `create_all()` as the production migration strategy.
- Migration files must be committed to the repository.

For a new project, create an initial migration after the models are defined.

---

# DATABASE CONFIGURATION

Use environment variables/configuration.

Example:

```text
DATABASE_URL=sqlite:///./app.db
```

Production example:

```text
DATABASE_URL=postgresql+psycopg://...
```

Never commit passwords, tokens, or secrets.

Provide:

```text
.env.example
```

with placeholder values only.

---

# BACKEND ARCHITECTURE

Prefer a structure similar to:

```text
backend/
  app/
    api/
    models/
    repositories/
    services/
    schemas/
    db/
    core/
    logging/
    main.py

  migrations/
  tests/
```

Adapt this to the existing repository instead of blindly replacing its structure.

Suggested responsibilities:

```text
models/        → SQLAlchemy persistence models
schemas/       → request/response models
repositories/  → database access
services/      → business logic
api/           → HTTP routes
db/            → engine/session configuration
core/          → configuration/security
logging/       → structured logging configuration
```

---

# API

Use Python API endpoints appropriate to the application.

Example:

```text
POST /api/login

GET /api/dashboard
GET /api/analytics
GET /api/users
GET /api/reports
GET /api/projects
```

The frontend should consume these APIs.

Do not hardcode dashboard results into the frontend when the purpose is to demonstrate backend/database integration.

---

# FRONTEND

## If Vanilla JavaScript is selected

Use:

- HTML.
- CSS.
- Vanilla JavaScript.

Do not use React, Vue, Angular, jQuery, or TypeScript unless explicitly requested.

## If React is selected

Use:

- React.
- JavaScript/JSX unless TypeScript is explicitly requested.
- Reusable components.
- Appropriate routing.
- API service layer.

Do not add Redux or another global-state framework without a real requirement.

---

# LOGIN

Create:

- Username/email.
- Password.
- Login button.
- Validation.
- Loading state.
- Error state.
- Dummy/local authentication.
- Logout.

Successful authentication should lead to the dashboard.

For a prototype, authentication can be deliberately simple, but do not present it as production-secure authentication.

---

# APPLICATION SHELL

After login:

```text
Sidebar
Header
Main Content
```

Sidebar examples:

- Dashboard.
- Analytics.
- Users.
- Reports.
- Projects.
- Settings.

Use **Lucide Icons only**.

## NEVER USE EMOJI

No emoji anywhere in the interface.

---

# DASHBOARD

Include:

## KPI CARDS

Examples:

- Total Users.
- Active Users.
- Revenue.
- Growth.
- Conversion Rate.

## CHARTS

At least:

1. Trend chart.
2. Comparison chart.
3. Distribution chart.

The values should come from backend APIs and ultimately from the database/repository layer.

Use meaningful dummy seed data.

---

# DUMMY DATA / SEEDING

Create deterministic seed data for local development.

Provide a clear mechanism such as:

```text
python -m app.seed
```

or an equivalent project command.

Seed data should populate:

- Users.
- Projects.
- Reports.
- Analytics records where appropriate.

Do not generate random data every time the application starts unless explicitly requested.

---

# LOGGING AND SESSION OUTPUT

## REQUIRED

Every meaningful application session/request should generate structured logs.

At minimum capture:

```text
timestamp
level
service
environment
request_id
session_id where applicable
user_id where appropriate and safe
method
path
status_code
duration_ms
event
message
exception information for failures
```

Never log:

- Passwords.
- Access tokens.
- Secrets.
- Full authentication credentials.
- Sensitive personal data unnecessarily.

---

# SESSION SUMMARY

At the end of an application/test session, generate a structured session summary where appropriate.

Example:

```json
{
  "event": "session_completed",
  "session_id": "..."
  "requests": 18,
  "successful_requests": 17,
  "failed_requests": 1,
  "duration_ms": 45231
}
```

For web applications, do not block or crash the application waiting for log delivery.

Logging must be asynchronous/non-blocking where practical.

---

# LOGGING STACK

## Default recommendation

Use:

```text
Application
   ↓
JSON stdout/stderr
   ↓
Docker / Kubernetes log collection
   ↓
Grafana Loki
   ↓
Grafana
```

Kubernetes captures container stdout/stderr, while cluster-level logging requires a separate backend. citeturn0search0

Loki is the preferred lightweight open-source-oriented default for this project because it is designed specifically for log aggregation and uses a label-oriented indexing model. citeturn0search16

## OpenTelemetry

Use OpenTelemetry when the project needs:

- Distributed tracing.
- Metrics.
- Cross-service correlation.
- More advanced observability.

OpenTelemetry Python supports telemetry generation for traces, metrics, and logs, with traces and metrics currently stable in the Python implementation. citeturn0search8

Do not introduce full distributed tracing into a tiny prototype unless there is a real need.

---

# KIBANA VS GRAFANA + LOKI

Do not treat Kubernetes and Kibana as alternatives.

They solve different problems:

```text
Kubernetes
= Container orchestration

Kibana
= Visualization/search UI for Elasticsearch

Elasticsearch
= Search/indexing backend

Grafana
= Visualization/observability UI

Loki
= Log aggregation backend
```

For this project, prefer:

```text
Docker Compose
+
Grafana
+
Loki
```

before introducing Kubernetes.

Elasticsearch + Kibana remains a valid alternative when full-text log search and Elasticsearch's ecosystem are more important. Elastic currently provides free usage options, but its licensing should be reviewed before selecting it for a long-term deployment model. citeturn0search2turn0search6

---

# LOCAL DEPLOYMENT

## Phase 1 — Simple Local

Run:

```text
Python backend
SQLite
Frontend
```

## Phase 2 — Multi-service Local

When observability is enabled:

```text
Frontend
Backend
PostgreSQL
Grafana
Loki
```

Use Docker Compose.

## Phase 3 — Kubernetes

Only introduce Kubernetes when there is a real requirement such as:

- Multiple services.
- Horizontal scaling.
- Health management.
- Rolling deployments.
- Environment separation.
- Service discovery.
- Production orchestration.

Do not introduce Kubernetes simply because it is popular.

Kubernetes itself does not provide cluster-level log storage; a separate logging backend is still required. citeturn0search0

---

# HEALTH CHECKS

Add appropriate endpoints such as:

```text
GET /health
GET /ready
```

Where appropriate:

- `/health` verifies the process is alive.
- `/ready` verifies required dependencies such as the database are available.

These should be useful for Docker/Kubernetes probes.

---

# CONTAINERIZATION

When Docker is requested or useful, create:

```text
Dockerfile
docker-compose.yml
.dockerignore
```

The container should:

- Run as a non-root user where practical.
- Receive configuration through environment variables.
- Write logs to stdout/stderr.
- Have a predictable startup command.
- Support health checks.

---

# KUBERNETES READINESS

If Kubernetes is selected, create appropriate:

```text
k8s/
  deployment.yaml
  service.yaml
  configmap.yaml
  secret.example.yaml
```

or an equivalent Helm structure if the project is sufficiently complex.

Do not commit real secrets.

Use readiness/liveness probes.

Send application logs to stdout/stderr rather than relying on application-managed log files.

---

# TESTING

At minimum test:

## API

- Login.
- Dashboard.
- CRUD repository operations.
- Validation errors.
- Database errors.
- Health endpoint.

## Database

- Model creation.
- Repository operations.
- Transactions.
- Rollback behavior.
- Migration execution.

## Frontend

- Login.
- Navigation.
- Dashboard.
- Charts.
- API failure state.
- Loading state.
- Empty state.

## Integration

Verify:

```text
Frontend
   ↓
API
   ↓
Service
   ↓
Repository
   ↓
SQLAlchemy
   ↓
Database
```

---

# VALIDATION

Before completion, verify:

- [ ] Application starts.
- [ ] Database starts/opens.
- [ ] Migrations execute.
- [ ] Seed data works.
- [ ] API works.
- [ ] Repository layer works.
- [ ] Login works.
- [ ] Dashboard works.
- [ ] Charts work.
- [ ] Navigation works.
- [ ] Logs are generated.
- [ ] Logs are structured.
- [ ] No secrets appear in logs.
- [ ] Health endpoint works.
- [ ] No significant frontend console errors.
- [ ] No significant backend errors.
- [ ] Docker setup works when enabled.
- [ ] Observability stack works when enabled.

---

# LOCAL DEPLOYMENT — REQUIRED

After implementation:

1. Run database migrations.
2. Seed dummy data.
3. Start backend.
4. Start frontend.
5. Start observability services if configured.
6. Verify health endpoints.
7. Verify login.
8. Verify dashboard.
9. Verify database-backed API calls.
10. Verify logs.
11. Report the local URLs.

Do not claim deployment succeeded unless it was actually verified.

---

# USER TESTING GATE — REQUIRED

After successful local deployment, stop and ask the user to test.

Ask the user to verify:

- Login.
- Dashboard.
- Navigation.
- Charts.
- CRUD/dummy interactions.
- Database-backed behavior.
- Error handling.
- Application responsiveness.

If observability is enabled, also ask the user to verify:

- Application logs.
- Session logs.
- Error logs.
- Dashboard/log viewer.

Wait for user feedback.

---

# DEVELOPMENT PRINCIPLE

Use:

```text
Model
  ↓
Repository
  ↓
Service
  ↓
API
  ↓
Frontend
```

and:

```text
Application
  ↓
Structured stdout/stderr
  ↓
Log Collector
  ↓
Loki
  ↓
Grafana
```

Build simply first, validate thoroughly, deploy locally, then let the user test before the next iteration.

## RECOMMENDED DATA, ORM, REPOSITORY, AND OBSERVABILITY STACK

For a simple Python application that should later be deployable in containers/Kubernetes, use the following default architecture unless the user explicitly chooses otherwise:

```yaml
Database:
  Development: SQLite
  Production: PostgreSQL

ORM:
  SQLAlchemy 2.x

Migration:
  Alembic

Repository Pattern:
  Explicit repository classes around SQLAlchemy sessions

API:
  FastAPI when a Python web API is required

Validation:
  Pydantic / Pydantic models where appropriate

Logging:
  Python structured JSON logging to stdout/stderr

Observability:
  OpenTelemetry where tracing/metrics are required

Local Log Stack:
  Grafana + Loki

Container Orchestration:
  Docker Compose for local multi-service development
  Kubernetes only when the application actually needs orchestration

Optional Log Search Alternative:
  Elasticsearch + Kibana or OpenSearch
```

### Why this stack

Use **SQLite for local development** because it is simple and requires no database server. Use **PostgreSQL for production** because the application can retain the same SQLAlchemy model/repository layer while moving to a proper database server. FastAPI's documentation explicitly demonstrates SQLite for simple applications and PostgreSQL as a production-oriented database option. SQLAlchemy provides the ORM layer and supports PostgreSQL. citeturn0search4turn0search7

For the requested "JPA-like" Python model approach, use **SQLAlchemy ORM declarative models**. Python classes represent database tables, and Python objects represent rows/entities. Keep repositories separate from API/business logic so the data-access implementation can evolve without coupling the rest of the application to SQL. citeturn0search7

Use **Alembic** for schema migrations. Do not rely on automatically recreating production tables from Python model definitions.

For logging, write structured logs to **stdout/stderr** rather than designing the application around local log files. Kubernetes is designed to capture container stdout/stderr, while cluster-level logging requires a separate backend. citeturn0search0

For a free/open-source-oriented observability stack, prefer **Grafana + Loki** for logs. Loki is designed as an open-source log aggregation system and indexes log labels rather than fully indexing every log line, which can reduce operational/storage overhead. citeturn0search16

**Kibana is not the logging backend itself.** It is the visualization/UI layer normally used with Elasticsearch. Elasticsearch + Kibana can be used, and Elastic currently provides free usage options, but its licensing is more nuanced than a straightforward Apache-licensed stack. citeturn0search6turn0search2

**Kubernetes is not a replacement for Kibana or Loki.** Kubernetes is the orchestration platform. The application should first work locally with Docker Compose and then have Kubernetes manifests/Helm configuration added when deployment actually requires Kubernetes. Kubernetes itself does not provide a native cluster-level log storage solution. citeturn0search0turn0search10

Recommended progression:

```text
Phase 1:
Python + FastAPI
        ↓
SQLAlchemy ORM
        ↓
SQLite
        ↓
Alembic
        ↓
Structured stdout logging

Phase 2:
Docker Compose
        ↓
PostgreSQL
        ↓
Grafana + Loki

Phase 3:
Kubernetes
        ↓
Application containers
        ↓
PostgreSQL
        ↓
Loki / Grafana
        ↓
OpenTelemetry when distributed tracing/metrics are needed
```

Do not introduce Kubernetes merely because it is available. Start simple and make the deployment architecture evolve with actual requirements.
