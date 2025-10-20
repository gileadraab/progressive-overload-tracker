# Docker Setup Explanation

## What We Built

### 1. **Dockerfile - The Recipe for Your Application Container**

We created a **multi-stage build** which is like a two-step cooking process:

**Stage 1 - Builder (the prep kitchen):**
```dockerfile
FROM python:3.11-slim as builder
```
- Starts with a lightweight Python image
- Installs heavy build tools (gcc, postgresql-client) needed to compile Python packages
- Installs all your Python dependencies (FastAPI, SQLAlchemy, etc.)
- This stage is "thrown away" after - we only keep what we need from it

**Stage 2 - Runtime (the serving area):**
```dockerfile
FROM python:3.11-slim
COPY --from=builder /usr/local/lib/python3.11/site-packages ...
```
- Starts fresh with another clean Python image
- **Copies only the installed packages** from the builder (not the build tools)
- Adds your application code
- Creates a non-root user (`appuser`) for security - containers shouldn't run as root
- Result: **Much smaller image** (~200MB vs ~400MB) because we don't include gcc and build tools

### 2. **docker-compose.yml - Orchestrating Multiple Containers**

Think of this as your local development environment blueprint:

```yaml
services:
  db:
    image: postgres:15
    # Your database container

  api:
    build: .
    depends_on:
      db:
        condition: service_healthy
    # Your FastAPI app container
```

**Key concepts:**
- **Services**: Each container is a "service" (database, API, etc.)
- **Networking**: Docker creates a private network where containers can talk to each other by name (your API connects to `db:5432`, not `localhost:5432`)
- **Health checks**: The API waits for the database to be healthy before starting
- **Volumes**: `./src:/app/src` means changes to your local `src/` folder instantly appear in the container (hot reload during development)

### 3. **docker-compose.prod.yml - Production Configuration**

This is the production-ready version with important differences:

```yaml
api:
  environment:
    DATABASE_URL: ${DATABASE_URL}  # From environment variables
  # NO volumes - code is baked into the image
  restart: unless-stopped  # Auto-restart if crashes
```

**Production differences:**
- No volume mounts (you don't edit code in production)
- Environment variables from the host system (keeps secrets out of the compose file)
- Restart policies for reliability
- Database port not exposed externally (only the API can access it)

## How This Works in Production

### Local Development (What We're Doing Now):
1. Run `docker-compose up`
2. Docker builds your image from the Dockerfile
3. Starts both containers (db and api)
4. You edit code locally, it syncs to the container
5. FastAPI auto-reloads on changes

### Production Deployment:

**Option 1 - Simple VPS (DigitalOcean, AWS EC2, etc.):**
```bash
# On your server:
git pull
docker-compose -f docker-compose.prod.yml up -d
```
- The `-d` flag runs containers in the background
- Environment variables come from the server's environment
- Containers restart automatically if they crash

**Option 2 - Container Orchestration (Kubernetes, ECS, etc.):**
1. Build your image: `docker build -t my-api:v1.0 .`
2. Push to a registry: `docker push my-registry/my-api:v1.0`
3. Deploy to cluster: The orchestrator pulls your image and runs it across multiple machines
4. Benefits: Auto-scaling, load balancing, zero-downtime deployments

## Why This Matters

**Before Docker:**
- "It works on my machine!" - different Python versions, different OS, missing dependencies
- Complex deployment: install Python, PostgreSQL, configure everything manually

**With Docker:**
- **Consistency**: Same environment everywhere (your laptop, staging, production)
- **Isolation**: Your app and its dependencies are packaged together
- **Portability**: Works on any machine with Docker installed
- **Scalability**: Easy to run multiple instances behind a load balancer

## Your Setup Specifically

```
┌─────────────────────────────────────┐
│  Docker Network (bridge)            │
│                                     │
│  ┌──────────┐      ┌──────────┐   │
│  │   API    │─────→│    DB    │   │
│  │  :8000   │      │  :5432   │   │
│  └────┬─────┘      └──────────┘   │
│       │                             │
└───────┼─────────────────────────────┘
        │
    localhost:8000 (exposed to your machine)
```

- Database is **only accessible to the API** inside Docker's network
- Only port 8000 is exposed to your host machine
- In production, you'd add NGINX/load balancer in front, HTTPS certificates, etc.

## Common Docker Commands

### Development
```bash
# Start all services
docker-compose up

# Start in background
docker-compose up -d

# Stop all services
docker-compose down

# Rebuild after code changes
docker-compose up --build

# View logs
docker-compose logs -f api

# Run commands inside container
docker-compose exec api bash
```

### Production
```bash
# Deploy with production config
docker-compose -f docker-compose.prod.yml up -d

# View running containers
docker ps

# Check container health
docker-compose ps

# Restart a service
docker-compose restart api
```
