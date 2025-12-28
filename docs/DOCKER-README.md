# Docker Setup Guide - Smart Money Divergence Index

## Overview
This guide covers Docker setup for the Smart Money Divergence Index project, including both development and production configurations.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Development Mode](#development-mode)
- [Production Mode](#production-mode)
- [Common Commands](#common-commands)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

### 1. Install Docker Desktop on Windows

**System Requirements:**
- Windows 10/11 64-bit (Pro, Enterprise, or Education)
- OR Windows 10/11 Home with WSL 2
- Minimum 4GB RAM (8GB+ recommended)
- Virtualization enabled in BIOS

**Installation Steps:**

1. **Enable WSL 2**

   Open PowerShell as Administrator:
   ```powershell
   wsl --install
   ```
   Restart your computer.

2. **Download Docker Desktop**
   - Visit: https://www.docker.com/products/docker-desktop/
   - Download "Docker Desktop for Windows"
   - Run the installer
   - Check "Use WSL 2 instead of Hyper-V"
   - Complete installation and restart

3. **Verify Installation**

   Open Git Bash:
   ```bash
   docker --version
   docker compose version
   ```

4. **Test Docker**
   ```bash
   docker run hello-world
   ```
   If you see "Hello from Docker!", you're ready!

---

## Quick Start

### First-Time Setup

1. **Clone the repository** (if you haven't already)
   ```bash
   cd /d/Project/The\ Smart\ Money\ Divergence\ Index
   ```

2. **Create your environment file**
   ```bash
   cp .env.example .env
   ```

   Edit `.env` and add your API credentials as needed.

3. **Build and run in development mode**
   ```bash
   docker compose up app-dev
   ```

4. **Access the dashboard**

   Open your browser: http://localhost:8501

That's it! The dashboard is now running in a container with SQLite.

---

## Development Mode

Development mode uses SQLite and mounts your local code for live editing.

### Start Development Container

```bash
# Start in foreground (see logs)
docker compose up app-dev

# Start in background (detached)
docker compose up -d app-dev
```

### What You Get
- ✅ SQLite database (no separate database container needed)
- ✅ Live code reloading (edit files locally, changes reflect immediately)
- ✅ Data persisted in `./data` directory
- ✅ Streamlit dashboard on http://localhost:8501

### Stop Development Container

```bash
# Stop and remove containers
docker compose down

# Stop, remove containers, and delete volumes
docker compose down -v
```

### View Logs

```bash
# Follow logs in real-time
docker compose logs -f app-dev

# View last 100 lines
docker compose logs --tail=100 app-dev
```

### Access Container Shell

```bash
docker compose exec app-dev bash
```

---

## Production Mode

Production mode uses PostgreSQL with a separate database container.

### Start Production Containers

```bash
# Start all production services (app + PostgreSQL)
docker compose --profile production up

# Start in background
docker compose --profile production up -d
```

### What You Get
- ✅ PostgreSQL database in a separate container
- ✅ Persistent database storage (survives container restarts)
- ✅ Health checks for database connectivity
- ✅ Production-optimized configuration
- ✅ Streamlit dashboard on http://localhost:8501

### Database Management UI (Optional)

Start pgAdmin for database management:

```bash
docker compose --profile tools up pgadmin
```

Access pgAdmin at: http://localhost:5050
- **Email:** admin@smartmoney.local
- **Password:** admin

Add PostgreSQL server in pgAdmin:
- **Host:** postgres
- **Port:** 5432
- **Database:** divergence_db
- **Username:** smartmoney
- **Password:** smartmoney_password

### Stop Production Containers

```bash
# Stop all production services
docker compose --profile production down

# Stop and delete database volume (WARNING: deletes all data!)
docker compose --profile production down -v
```

---

## Common Commands

### Building

```bash
# Build images (after code changes)
docker compose build

# Build without cache (clean build)
docker compose build --no-cache

# Build specific service
docker compose build app-dev
```

### Container Management

```bash
# List running containers
docker compose ps

# View resource usage
docker stats

# Restart a service
docker compose restart app-dev

# Remove stopped containers
docker compose rm
```

### Data Management

```bash
# List volumes
docker volume ls

# Inspect a volume
docker volume inspect smart-money-postgres-data

# Remove all unused volumes
docker volume prune
```

### Database Operations (Production Mode)

```bash
# Connect to PostgreSQL
docker compose exec postgres psql -U smartmoney -d divergence_db

# Backup database
docker compose exec postgres pg_dump -U smartmoney divergence_db > backup.sql

# Restore database
cat backup.sql | docker compose exec -T postgres psql -U smartmoney -d divergence_db

# Run database migrations
docker compose exec app-prod alembic upgrade head
```

### Cleaning Up

```bash
# Remove all stopped containers, unused networks, dangling images
docker system prune

# Remove everything including volumes (WARNING: deletes data!)
docker system prune -a --volumes
```

---

## Environment Variables

### Required Variables

Edit `.env` file and set:

# API Credentials (If needed)
# ADD_YOUR_KEYS_HERE=value

### Optional Variables

```bash
# Database (auto-configured in docker-compose)
DATABASE_URL=sqlite:///data/divergence.db  # Dev mode
# DATABASE_URL=postgresql://...  # Prod mode (set automatically)

# Application
ENVIRONMENT=development
LOG_LEVEL=INFO
DATA_START_DATE=2024-01-01
```

See [.env.example](../../.env.example) for all available options.

---

## Troubleshooting

### Docker Desktop Not Starting

**Problem:** Docker Desktop fails to start or shows "Docker engine stopped"

**Solutions:**
1. Open Docker Desktop settings
2. Enable WSL 2 integration
3. Restart Docker Desktop
4. If still failing, restart your computer

---

### Port Already in Use

**Problem:** `Error: bind: address already in use`

**Solution:**
```bash
# Find what's using port 8501
netstat -ano | findstr :8501

# Stop the process or change port in docker-compose.yml
ports:
  - "8502:8501"  # Use port 8502 instead
```

---

### Database Connection Errors (Production Mode)

**Problem:** App can't connect to PostgreSQL

**Solutions:**

1. **Check if PostgreSQL is healthy:**
   ```bash
   docker compose ps
   ```
   Look for `postgres (healthy)` status.

2. **Wait for database to be ready:**
   PostgreSQL takes 5-10 seconds to initialize on first run.

3. **Check logs:**
   ```bash
   docker compose logs postgres
   ```

4. **Verify connection:**
   ```bash
   docker compose exec postgres psql -U smartmoney -d divergence_db
   ```

---

### Volume Mounting Issues (Windows)

**Problem:** Code changes not reflecting in container

**Solution:**

1. **Check Docker Desktop settings:**
   - Settings → Resources → File Sharing
   - Ensure your project directory is shared

2. **Use WSL 2 backend:**
   - Settings → General → Use WSL 2 based engine

3. **Verify mount paths in docker-compose.yml:**
   ```yaml
   volumes:
     - ./:/app  # Should mount current directory
   ```

---

### Build Failures

**Problem:** `docker compose build` fails

**Solutions:**

1. **Clear Docker cache:**
   ```bash
   docker compose build --no-cache
   ```

2. **Remove old images:**
   ```bash
   docker image prune -a
   ```

3. **Check disk space:**
   ```bash
   docker system df
   ```

4. **Check requirements file exists:**
   ```bash
   ls requirements-minimal.txt
   ```

---

### Container Exits Immediately

**Problem:** Container starts then stops

**Solutions:**

1. **Check logs:**
   ```bash
   docker compose logs app-dev
   ```

2. **Common causes:**
   - Missing `.env` file → Copy from `.env.example`
   - Python syntax errors → Check logs for traceback
   - Missing `app.py` → Ensure main application file exists

3. **Run container interactively to debug:**
   ```bash
   docker compose run --rm app-dev bash
   ```

---

### Slow Performance

**Problem:** Dashboard loads slowly in Docker

**Solutions:**

1. **Increase Docker resources:**
   - Docker Desktop → Settings → Resources
   - Increase CPUs to 4
   - Increase Memory to 8GB

2. **Use development mode (faster):**
   ```bash
   docker compose up app-dev  # SQLite is faster than PostgreSQL
   ```

3. **Optimize WSL 2:**
   - Close unnecessary applications
   - Restart Docker Desktop

---

### Network Issues

**Problem:** Can't access dashboard at localhost:8501

**Solutions:**

1. **Check container is running:**
   ```bash
   docker compose ps
   ```

2. **Verify port mapping:**
   ```bash
   docker compose port app-dev 8501
   ```

3. **Check Windows Firewall:**
   - Allow Docker Desktop through firewall

4. **Try 127.0.0.1 instead of localhost:**
   http://127.0.0.1:8501

---

## Best Practices

### For Development
- ✅ Use `app-dev` service (faster with SQLite)
- ✅ Keep `.env` file updated with your credentials
- ✅ Commit often, Docker volumes are persistent
- ✅ Run `docker compose down` when done to free resources

### For Production Testing
- ✅ Test with `--profile production` before deploying
- ✅ Backup database regularly
- ✅ Monitor container logs for errors
- ✅ Use environment-specific `.env` files

### For Data Persistence
- ✅ SQLite data: Stored in `./data/` (backed up with Git)
- ✅ PostgreSQL data: Stored in named volume `smart-money-postgres-data`
- ✅ Backup volumes before running `docker compose down -v`

---

## Next Steps

After successfully running Docker:

1. **Configure API Keys** - Edit `.env` with your credentials
2. **Run Data Collection** - Follow [Data Collection Guide](../data-collection/README.md)
3. **Explore Dashboard** - Access at http://localhost:8501
4. **Review Architecture** - See [TECHNICAL-SPEC.md](../TECHNICAL-SPEC.md)

---

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Reference](https://docs.docker.com/compose/compose-file/)
- [PostgreSQL Docker Image](https://hub.docker.com/_/postgres)
- [Streamlit Documentation](https://docs.streamlit.io/)

---

**Questions or Issues?**

Check the [main project documentation](../../README.md) or open an issue on GitHub.
