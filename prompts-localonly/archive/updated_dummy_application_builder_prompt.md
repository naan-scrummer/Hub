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

# DEPLOYMENT AND INFRASTRUCTURE — OPTIONAL

## IMPORTANT PRINCIPLE

**Do NOT introduce deployment infrastructure unless explicitly requested by the user or required by the application's actual architecture.**

The primary objective is to build a functional application with:

- Python backend
- Selected frontend
- Database-backed functionality
- SQLAlchemy ORM models
- Repository layer
- Service/business layer
- API layer
- Structured application logging
- Automated tests
- Simple local execution

**Application functionality takes priority over deployment infrastructure.**

Do not add infrastructure merely because it is considered common enterprise practice.

---

# DEFAULT DEVELOPMENT MODE

Unless the user explicitly requests containerization or cloud deployment, run the application directly using the native development environment.

Default:

```text
Frontend
    ↓
Python Backend
    ↓
SQLAlchemy
    ↓
SQLite
```

The application must work successfully in this simple configuration before any deployment infrastructure is considered.

---

# DO NOT AUTOMATICALLY ADD

Do NOT create any of the following unless explicitly requested:

- Dockerfile
- docker-compose.yml
- Kubernetes manifests
- Helm charts
- Kubernetes Deployments
- Kubernetes Services
- Kubernetes ConfigMaps
- Kubernetes Secrets
- Ingress
- Service mesh
- Docker Swarm
- OpenTelemetry
- Grafana
- Loki
- Elasticsearch
- Kibana
- OpenSearch
- Prometheus
- Grafana dashboards
- Cloud-specific infrastructure
- Terraform
- Infrastructure-as-Code
- CI/CD deployment pipelines
- Container registries
- Production orchestration
- Load balancers
- Auto-scaling configuration

These technologies are **optional extensions**, not default application requirements.

---

# DEPLOYMENT DECISION GATE

If deployment infrastructure appears useful, STOP before introducing it.

Use:

**Deployment decision required**

**Current application:** ...

**Why infrastructure may be useful:** ...

**Option A — No containerization**

Run the application directly.

**Option B — Docker**

Containerize the application.

**Option C — Docker Compose**

Use Compose only if multiple services genuinely need to run together.

**Option D — Kubernetes**

Use Kubernetes only when there is a genuine orchestration requirement.

**Recommendation:** ...

Wait for the user's decision.

Do not create deployment infrastructure while waiting for approval.

---

# DOCKER — OPTIONAL

Docker may be introduced ONLY when the user explicitly requests:

- Containerization
- Docker deployment
- Environment consistency
- Container-based CI/CD
- Deployment to an environment requiring containers

If Docker is requested, create only the minimum required files.

Normally:

```text
Dockerfile
.dockerignore
```

Do not automatically create Docker Compose when a single container is sufficient.

---

# DOCKER COMPOSE — OPTIONAL

Docker Compose should only be introduced when multiple services genuinely need to run together.

For example:

```text
Frontend
Backend
Database
```

or:

```text
Backend
PostgreSQL
```

Do NOT introduce Compose simply because Docker is being used.

For a single-service application, a Dockerfile is sufficient unless the user requests otherwise.

---

# KUBERNETES — OPTIONAL

Kubernetes is completely optional.

Do NOT create Kubernetes configuration during the initial application implementation.

Introduce Kubernetes only when there is a specific requirement such as:

- Production orchestration
- Multiple independently deployable services
- Horizontal scaling
- Rolling deployments
- Service discovery
- High availability
- Environment-specific cluster deployment
- Existing organizational Kubernetes infrastructure

If none of these requirements exist:

**Do not use Kubernetes.**

Do not create:

```text
k8s/
helm/
deployment.yaml
service.yaml
configmap.yaml
secret.yaml
ingress.yaml
```

unless explicitly requested.

---

# OBSERVABILITY — KEEP APPLICATION LOGGING SIMPLE

Application logging should be implemented independently of any external observability platform.

Default:

```text
Application
    ↓
Structured JSON logs
    ↓
stdout/stderr or local development output
```

At minimum, logs should capture:

```text
timestamp
level
service
environment
request_id
method
path
status_code
duration_ms
event
message
exception information
```

Never log:

- Passwords
- Tokens
- Secrets
- Authentication credentials
- Sensitive information unnecessarily

---

# EXTERNAL OBSERVABILITY PLATFORMS — OPTIONAL

Do NOT automatically install or configure:

- Grafana
- Loki
- Prometheus
- OpenTelemetry
- Elasticsearch
- Kibana
- OpenSearch

Only introduce them if the user explicitly requests observability infrastructure or the project has a demonstrated requirement for it.

Application-level structured logging must remain useful even when no observability platform is installed.

---

# DATABASE DEPLOYMENT

For the initial/simple application:

```text
SQLite
```

remains the default development database.

Use:

```text
DATABASE_URL
```

for configuration.

The application architecture should allow SQLite to be replaced by PostgreSQL later without rewriting the business layer.

However:

**Do not create PostgreSQL deployment infrastructure merely because PostgreSQL may be used in the future.**

Only configure PostgreSQL when:

- The user explicitly requests PostgreSQL, or
- The application genuinely requires PostgreSQL-specific capabilities.

---

# PRODUCTION CONFIGURATION

Do not build complete production infrastructure unless explicitly requested.

Do not automatically create:

- Production database infrastructure
- Kubernetes infrastructure
- Cloud infrastructure
- Monitoring infrastructure
- Logging clusters
- Load balancing
- Auto-scaling
- Secrets-management infrastructure
- CI/CD pipelines

Instead, keep the application **deployment-ready without being deployment-heavy**.

---

# HEALTH ENDPOINT

A simple health endpoint may be implemented if useful:

```text
GET /health
```

This should be a lightweight application endpoint.

Do NOT create Kubernetes-specific readiness/liveness configuration unless Kubernetes is explicitly requested.

---

# DEVELOPMENT PRIORITY

Always follow this priority:

```text
1. Functional requirements
        ↓
2. Database/model layer
        ↓
3. Repository layer
        ↓
4. Service/business layer
        ↓
5. API layer
        ↓
6. Frontend
        ↓
7. Testing
        ↓
8. Structured application logging
        ↓
9. User validation
        ↓
10. Deployment infrastructure — ONLY IF REQUESTED
```

Never reverse this priority.

---

# MINIMALISM RULE

When two technically valid solutions exist, prefer the solution with:

- Fewer dependencies
- Fewer configuration files
- Fewer services
- Fewer infrastructure components
- Easier local setup
- Easier debugging
- Easier testing
- Lower operational complexity

Do not introduce enterprise infrastructure into a simple prototype without a concrete requirement.

---

# FINAL DEPLOYMENT RULE

The application is considered complete when it can:

1. Start successfully.
2. Connect to its configured database.
3. Run migrations.
4. Seed required dummy data.
5. Start the backend.
6. Start the frontend.
7. Execute API calls successfully.
8. Perform database operations.
9. Generate structured application logs.
10. Pass the required tests.
11. Be manually tested by the user.

**Docker, Docker Compose, Kubernetes, Grafana, Loki, OpenTelemetry, Kibana, Elasticsearch, cloud infrastructure, and CI/CD are separate optional phases and must NOT block completion of the core application.**

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

## RECOMMENDED CORE APPLICATION STACK

For the simple Python application, use the following default stack unless the user explicitly chooses otherwise:

```yaml
Backend:
  Python

API:
  FastAPI when a Python web API is required

Frontend:
  User-selected frontend

Database:
  SQLite for development

ORM:
  SQLAlchemy 2.x

Migration:
  Alembic

Repository Pattern:
  Explicit repository classes around SQLAlchemy sessions

Validation:
  Pydantic / Pydantic models where appropriate

Logging:
  Structured JSON application logging to stdout/stderr
```

The architecture should keep the database configuration-driven through `DATABASE_URL`, so PostgreSQL can be introduced later without rewriting the business/service/repository architecture.

For the requested "JPA-like" Python model approach, use SQLAlchemy ORM declarative models. Python classes represent database tables, and Python objects represent rows/entities.

Keep repositories separate from API/business logic so the data-access implementation can evolve without tightly coupling the rest of the application to SQL.

Use Alembic for schema migrations. Do not rely on automatically recreating production tables from Python model definitions.

External observability platforms and deployment infrastructure are optional and must not be introduced unless explicitly requested.

## CORE ARCHITECTURE

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

For logging:

```text
Application
  ↓
Structured stdout/stderr
```

Build simply first, validate thoroughly, deploy only when deployment is explicitly required, and let the user test before the next iteration.
