# Running with Docker

## Quick Start

1. **Clone the repository:**
   ```bash
   git clone git@github.com:anik107/demo_project_for_baltd.git
   cd demo_project_for_baltd
   ```

2. **Start the application:**
   ```bash
   # Using docker compose (recommended - newer syntax)
   docker compose up --build

   # Or using docker-compose (older syntax)
   docker-compose up --build
   ```

3. **Access the application:**
   - Application: http://localhost:8000
   - Database: localhost:5433 (postgres/postgres)

## Services

- **app**: FastAPI application (Port 8000)
- **db**: PostgreSQL database (Port 5433)

## Useful Commands

```bash
# Start services in background (recommended)
sudo docker compose up -d --build

# Start services with logs visible
sudo docker compose up --build

# View logs from all services
sudo docker compose logs -f

# View logs from specific service
docker compose logs -f app
docker compose logs -f db

# Stop services
docker compose down

# Stop services and remove volumes (warning: deletes database data)
docker compose down -v

# Restart specific service
docker compose restart app

# Check service status
docker compose ps

# Access database shell
docker compose exec db psql -U postgres -d appointment_system

# Access application container shell
docker compose exec app bash

# Rebuild specific service
docker compose build app
docker compose up -d app
```

## Running with Docker Compose

Your project uses a `docker-compose.yml` file to define and run multiple containers. Here are the different ways to run it:

### Method 1: Direct docker compose command
```bash
# Start all services defined in docker-compose.yml
docker compose up --build

# Start in background (detached mode)
docker compose up -d --build

# Stop all services
docker compose down
```

### Method 2: Specify the compose file explicitly
```bash
# If you have multiple compose files or want to be explicit
docker compose -f docker-compose.yml up --build

# Using the older docker-compose command
docker-compose -f docker-compose.yml up --build
```

### Method 3: Run specific services
```bash
# Start only the database
docker compose up db

# Start only the application (will start db automatically due to dependency)
docker compose up app
```

## Environment Variables

Copy `.env.example` to `.env` and modify if needed:

```bash
cp .env.example .env
```

The default configuration works for development.
