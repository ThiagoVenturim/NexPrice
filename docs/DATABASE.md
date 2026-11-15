# Database configuration

NexPrice uses a pluggable storage layer built on SQLAlchemy Core with parameterized SQL queries.

## Default: SQLite (zero configuration)

If `DB_URL` is not set in the environment or in `.env`, NexPrice defaults to a local SQLite database at `nexprice.db`:

```
sqlite:///nexprice.db
```

No external database server is required to get started.

## Custom database via DB_URL

To point NexPrice to an external database, configure the `DB_URL` variable either in your shell environment or in a local `.env` file. You can start by copying the provided `.env.example`:

```bash
cp .env.example .env
```

The database URL follows standard SQLAlchemy URL formats.

### PostgreSQL

Install the optional PostgreSQL driver:

```bash
pip install -e ".[postgres]"
```

Configure `DB_URL`:

```env
DB_URL=postgresql+psycopg://username:password@localhost:5432/nexprice
```

### MySQL / MariaDB

Install the optional MySQL driver:

```bash
pip install -e ".[mysql]"
```

Configure `DB_URL`:

```env
DB_URL=mysql+pymysql://username:password@localhost:3306/nexprice
```

### Microsoft SQL Server (ODBC)

Install the optional ODBC driver wrapper:

```bash
pip install -e ".[mssql]"
```

Configure `DB_URL` with your system's installed ODBC driver:

```env
DB_URL=mssql+pyodbc://username:password@localhost:1433/nexprice?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes
```

## Running with Docker and Docker Compose

A `docker-compose.yml` file is provided at the repository root.

- By default, `docker compose up` runs NexPrice using local container storage (`/data/nexprice.db`).
- To start a bundled PostgreSQL database alongside the app, use the `postgres` profile:

```bash
docker compose --profile postgres up
```

## Running on Kubernetes

Example manifests are available in `k8s/`:

- `k8s/deployment.yaml`: Deployment spec with resource requests/limits and volume mounts.
- `k8s/service.yaml`: ClusterIP service.
- `k8s/configmap.yaml`: Non-sensitive configuration (`LOG_LEVEL`).
- `k8s/secret.yaml`: Sensitive credentials (`DB_URL`).

## Execution scripts

Multiplatform helper scripts are located in `scripts/`:

- Windows (PowerShell): `.\scripts\run.ps1 [local|test|docker|docker-postgres|help]`
- Linux / macOS (Bash): `./scripts/run.sh [local|test|docker|docker-postgres|help]`
