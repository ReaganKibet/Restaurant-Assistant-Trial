# Docker Setup for Restaurant Assistant

This project includes comprehensive Docker configuration for both production and development environments.

## 🚀 Quick Start

### Production Deployment

1. **Build and run the production container:**
   ```bash
   docker-compose up --build
   ```

2. **Access the application:**
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Frontend: Served by the backend at http://localhost:8000

### Development Environment

1. **Run the development environment:**
   ```bash
   docker-compose -f docker-compose.dev.yml up --build
   ```

2. **Access the development services:**
   - Backend API: http://localhost:8000 (with hot reload)
   - Frontend: http://localhost:3000 (with hot reload)

## 📁 Docker Configuration Files

### Production Files
- `Dockerfile` - Multi-stage build for production
- `docker-compose.yml` - Production orchestration
- `.dockerignore` - Optimizes build context

### Development Files
- `docker-compose.dev.yml` - Development orchestration
- `frontend/Dockerfile.dev` - Frontend development container

## 🏗️ Architecture

### Multi-Stage Build Process

1. **Frontend Builder Stage:**
   - Uses Node.js 18 Alpine
   - Builds React/TypeScript frontend
   - Creates optimized production build

2. **Backend Builder Stage:**
   - Uses Python 3.11 Slim
   - Installs Python dependencies
   - Compiles any required extensions

3. **Production Stage:**
   - Minimal Python 3.11 Slim image
   - Copies only necessary files
   - Runs as non-root user for security
   - Includes health checks

## 🔧 Configuration Options

### Environment Variables

You can customize the application by setting environment variables:

```bash
# In docker-compose.yml or as environment variables
PYTHONUNBUFFERED=1
PYTHONPATH=/app
ENVIRONMENT=production
```

### Volume Mounts

- `./data:/app/data:ro` - Read-only access to data files
- `./logs:/app/logs` - Persistent log storage
- `./app:/app/app` - Source code (development only)

## 🛠️ Development Workflow

### Hot Reloading

The development setup includes hot reloading for both frontend and backend:

- **Backend:** Uses uvicorn with `--reload` flag
- **Frontend:** Uses Vite development server

### Making Changes

1. **Backend changes:** Automatically reloaded when you save files
2. **Frontend changes:** Automatically reloaded in the browser
3. **Dependency changes:** Rebuild containers with `--build` flag

## 📊 Monitoring and Health Checks

### Health Check Configuration

The production container includes health checks:

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

### Logging

- Application logs are persisted to `./logs/`
- Container logs can be viewed with `docker-compose logs`

## 🔒 Security Features

### Production Security

- Runs as non-root user (`appuser`)
- Minimal base image (Python slim)
- No development dependencies in production
- Read-only data mounts where possible

### Development Security

- Separate development containers
- Source code mounted for debugging
- Development dependencies included

## 🚀 Deployment Commands

### Production Commands

```bash
# Build and start production
docker-compose up --build -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild and restart
docker-compose up --build --force-recreate
```

### Development Commands

```bash
# Start development environment
docker-compose -f docker-compose.dev.yml up --build

# View development logs
docker-compose -f docker-compose.dev.yml logs -f

# Stop development services
docker-compose -f docker-compose.dev.yml down
```

## 🔧 Troubleshooting

### Common Issues

1. **Port conflicts:**
   ```bash
   # Check what's using the ports
   netstat -tulpn | grep :8000
   netstat -tulpn | grep :3000
   ```

2. **Permission issues:**
   ```bash
   # Fix log directory permissions
   sudo chown -R $USER:$USER logs/
   ```

3. **Build failures:**
   ```bash
   # Clean build cache
   docker system prune -a
   docker-compose build --no-cache
   ```

### Debugging

1. **Access container shell:**
   ```bash
   # Production
   docker-compose exec restaurant-assistant bash
   
   # Development
   docker-compose -f docker-compose.dev.yml exec restaurant-assistant-dev bash
   ```

2. **View container resources:**
   ```bash
   docker stats
   ```

## 📝 Notes

- The production build includes both frontend and backend in a single container
- Development setup separates frontend and backend for better debugging
- All sensitive data should be managed through environment variables
- The `.dockerignore` file optimizes build performance by excluding unnecessary files
