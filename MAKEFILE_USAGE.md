# 🚀 Makefile Usage Guide

The **Makefile** provides a streamlined way to set up and run the entire AI Full-Stack Geological Data Pipeline.

## ⚡ Quick Start (2 commands)

```bash
# 1. Setup everything (virtual env + dependencies)
make setup

# 2. Run all 3 modules
make run-all
```

**That's it!** 🎉 All modules will be running on their respective ports.

## 📋 Available Commands

### 🔧 Setup & Installation

```bash
make setup       # Complete setup: venv + all dependencies
make install     # Install/update dependencies only
```

### 🚀 Running Services

```bash
make run-all     # Start all 3 modules in background
make run-data    # Start only Data Foundation (port 8000)
make run-cortex  # Start only Cortex Engine (port 3002)
make run-backend # Start only Backend Gateway (port 3003)
```

### 🧪 Testing & Health Checks

```bash
make test        # Quick health check of all modules
make health      # Detailed health check with responses
make demo        # Full pipeline demonstration
```

### 🛠️ Utilities

```bash
make stop        # Stop all running modules
make clean       # Clean up everything (venv, logs, pids)
make kill-ports  # Kill processes on ports 8000, 3002, 3003
make check-ports # Check if ports are available
make logs        # View recent logs from all modules
```

### 📖 Help

```bash
make help        # Show all available commands
make             # Same as 'make help' (default)
```

## 📍 Service URLs

Once running with `make run-all`:

| Service             | URL                   | Description          |
| ------------------- | --------------------- | -------------------- |
| **Data Foundation** | http://localhost:8000 | Geological data API  |
| **Cortex Engine**   | http://localhost:3002 | AI/Vector processing |
| **Backend Gateway** | http://localhost:3003 | Unified API gateway  |

## 📋 API Documentation

| Service             | API Docs                   |
| ------------------- | -------------------------- |
| **Cortex Engine**   | http://localhost:3002/docs |
| **Backend Gateway** | http://localhost:3003/docs |

## 🎯 Typical Workflow

```bash
# First time setup
make setup

# Start development
make run-all

# Check everything is working
make test

# View logs if needed
make logs

# Stop everything when done
make stop
```

## 🔧 Troubleshooting

### Ports Already in Use?

```bash
make kill-ports  # Kill any processes on our ports
make run-all     # Try again
```

### Need to Reinstall Dependencies?

```bash
make clean       # Clean everything
make setup       # Reinstall from scratch
```

### Individual Module Issues?

```bash
# Check which modules are up/down
make test

# Start individual modules
make run-data      # Just data foundation
make run-cortex    # Just cortex engine
make run-backend   # Just backend gateway
```

### View Recent Logs

```bash
make logs
```

## 🚀 Development Tips

-   **Background Mode**: `run-all` runs services in the background with PID tracking
-   **Log Files**: All output is captured in `{module}/logs/{module}.log`
-   **Auto Reload**: Data Foundation and Backend Gateway have auto-reload enabled
-   **Clean Shutdown**: `make stop` properly terminates all processes

## 💡 Pro Tips

1. **Quick Pipeline Test**: `make demo` runs a full end-to-end test
2. **Development Mode**: `make dev` = `make setup && make run-all`
3. **Port Management**: Makefile automatically handles port conflicts
4. **Process Tracking**: Uses PID files for clean service management

---

**⚡ Total setup time: ~2 minutes**  
**🎯 Ready for development and testing!**
