# AI Full-Stack Geological Data Pipeline - Makefile
# Streamlined setup and execution for all 3 modules

.PHONY: help setup install run-all run-data run-cortex run-backend stop clean test health check-ports kill-ports

# Default target
help:
	@echo "🚀 AI Full-Stack Geological Data Pipeline"
	@echo ""
	@echo "Available commands:"
	@echo "  make setup         - Create virtual environment and install all dependencies"
	@echo "  make run-all       - Start all 3 modules in background (with logs)"
	@echo "  make run-foreground- Start all 3 modules in foreground (live console output)"
	@echo "  make run-terminals - Start all 3 modules in separate terminal windows"
	@echo "  make watch-logs    - Watch live logs from all modules"
	@echo "  make run-data      - Start Module 1: Data Foundation (port 8000)"
	@echo "  make run-cortex    - Start Module 2: Cortex Engine (port 3002)"
	@echo "  make run-backend   - Start Module 3: Backend Gateway (port 3003)"
	@echo "  make stop          - Stop all running modules"
	@echo "  make test          - Run health checks on all modules"
	@echo "  make clean         - Clean virtual environment and temp files"
	@echo "  make kill-ports    - Kill processes on ports 8000, 3002, 3003"
	@echo ""
	@echo "Quick Start:"
	@echo "  make setup && make run-all"

# Setup virtual environment and install all dependencies
setup:
	@echo "🔧 Setting up AI Full-Stack Pipeline..."
	@echo "📦 Creating virtual environment..."
	python -m venv .venv
	@echo "📥 Installing root dependencies..."
	.venv/bin/pip install -r requirements.txt
	@echo "📥 Installing Module 1 (Data Foundation) dependencies..."
	.venv/bin/pip install -r data_foundation_project/requirements.txt
	.venv/bin/pip install -e ./data_foundation_project
	@echo "📥 Installing Module 2 (Cortex Engine) dependencies..."
	.venv/bin/pip install -r cortex_engine/requirements.txt
	.venv/bin/pip install -e ./cortex_engine
	@echo "📥 Installing Module 3 (Backend Gateway) dependencies..."
	.venv/bin/pip install -r backend_gateway/requirements.txt
	@echo "✅ Setup complete! Run 'make run-all' to start all modules."

# Install dependencies only (assumes venv exists)
install:
	@echo "📥 Installing/updating all dependencies..."
	.venv/bin/pip install -r requirements.txt
	.venv/bin/pip install -r data_foundation_project/requirements.txt
	.venv/bin/pip install -e ./data_foundation_project
	.venv/bin/pip install -r cortex_engine/requirements.txt
	.venv/bin/pip install -e ./cortex_engine
	.venv/bin/pip install -r backend_gateway/requirements.txt
	@echo "✅ Dependencies updated!"

# Kill any processes on our ports before starting
kill-ports:
	@echo "🔪 Killing processes on ports 8000, 3002, 3003..."
	-lsof -ti:8000 | xargs kill -9 2>/dev/null || true
	-lsof -ti:3002 | xargs kill -9 2>/dev/null || true
	-lsof -ti:3003 | xargs kill -9 2>/dev/null || true
	@sleep 2

# Check if ports are available
check-ports:
	@echo "🔍 Checking port availability..."
	@if lsof -i:8000 >/dev/null 2>&1; then echo "❌ Port 8000 is busy"; else echo "✅ Port 8000 is free"; fi
	@if lsof -i:3002 >/dev/null 2>&1; then echo "❌ Port 3002 is busy"; else echo "✅ Port 3002 is free"; fi
	@if lsof -i:3003 >/dev/null 2>&1; then echo "❌ Port 3003 is busy"; else echo "✅ Port 3003 is free"; fi

# Start all modules (background mode with logs)
run-all: kill-ports
	@echo "🚀 Starting all 3 modules..."
	@echo "📊 Module 1: Data Foundation (port 8000)..."
	@mkdir -p data_foundation_project/logs
	cd data_foundation_project/src && ../../.venv/bin/uvicorn api.main:app --host localhost --port 8000 --reload > ../logs/data_foundation.log 2>&1 & echo $$! > ../data_foundation.pid
	@sleep 3
	@echo "🤖 Module 2: Cortex Engine (port 3002)..."
	@mkdir -p cortex_engine/logs
	cd cortex_engine && ../.venv/bin/uvicorn src.main:app --port 3002 > logs/cortex_engine.log 2>&1 & echo $$! > cortex_engine.pid
	@sleep 3
	@echo "🔗 Module 3: Backend Gateway (port 3003)..."
	@mkdir -p backend_gateway/logs
	cd backend_gateway && ../.venv/bin/uvicorn src.api.main:app --reload --host localhost --port 3003 > logs/backend_gateway.log 2>&1 & echo $$! > backend_gateway.pid
	@sleep 3
	@echo ""
	@echo "🎉 All modules started! Check status with 'make test'"
	@echo ""
	@echo "📍 Service URLs:"
	@echo "  • Data Foundation: http://localhost:8000"
	@echo "  • Cortex Engine: http://localhost:3002"
	@echo "  • Backend Gateway: http://localhost:3003"
	@echo ""
	@echo "📋 API Documentation:"
	@echo "  • Cortex Engine API: http://localhost:3002/docs"
	@echo "  • Backend Gateway API: http://localhost:3003/docs"
	@echo ""
	@echo "💡 To see live logs: make watch-logs"
	@echo "🛑 To stop all modules: make stop"

# Start all modules in foreground (single terminal with live output)
run-foreground: kill-ports
	@echo "🚀 Starting all 3 modules in FOREGROUND mode..."
	@echo "⚠️  Press Ctrl+C to stop all modules"
	@echo ""
	@mkdir -p data_foundation_project/logs cortex_engine/logs backend_gateway/logs
	@echo "📊 Starting Module 1: Data Foundation (port 8000)..."
	cd data_foundation_project/src && ../../.venv/bin/uvicorn api.main:app --host localhost --port 8000 --reload 2>&1 | sed 's/^/[DATA] /' &
	@sleep 3
	@echo "🤖 Starting Module 2: Cortex Engine (port 3002)..."
	cd cortex_engine && ../.venv/bin/uvicorn src.main:app --port 3002 2>&1 | sed 's/^/[CORTEX] /' &
	@sleep 3
	@echo "🔗 Starting Module 3: Backend Gateway (port 3003)..."
	cd backend_gateway && ../.venv/bin/uvicorn src.api.main:app --reload --host localhost --port 3003 2>&1 | sed 's/^/[GATEWAY] /' &
	@echo ""
	@echo "🎉 All modules running in foreground!"
	@echo "📍 Service URLs: Data:8000 | Cortex:3002 | Gateway:3003"
	@echo "⚠️  Press Ctrl+C to stop all modules"
	@wait

# Start all modules in separate terminals (macOS/Linux)
run-terminals: kill-ports
	@echo "🚀 Starting all 3 modules in SEPARATE TERMINALS..."
	@mkdir -p data_foundation_project/logs cortex_engine/logs backend_gateway/logs
	@if command -v osascript >/dev/null 2>&1; then \
		echo "🍎 Detected macOS - using Terminal.app..."; \
		osascript -e 'tell application "Terminal" to do script "cd \"$(PWD)/data_foundation_project/src\" && ../../.venv/bin/uvicorn api.main:app --host localhost --port 8000 --reload"'; \
		sleep 2; \
		osascript -e 'tell application "Terminal" to do script "cd \"$(PWD)/cortex_engine\" && ../.venv/bin/uvicorn src.main:app --port 3002"'; \
		sleep 2; \
		osascript -e 'tell application "Terminal" to do script "cd \"$(PWD)/backend_gateway\" && ../.venv/bin/uvicorn src.api.main:app --reload --host localhost --port 3003"'; \
		echo "✅ Opened 3 Terminal windows"; \
	elif command -v gnome-terminal >/dev/null 2>&1; then \
		echo "🐧 Detected Linux - using gnome-terminal..."; \
		gnome-terminal -- bash -c "cd data_foundation_project/src && ../../.venv/bin/uvicorn api.main:app --host localhost --port 8000 --reload; exec bash" & \
		sleep 2; \
		gnome-terminal -- bash -c "cd cortex_engine && ../.venv/bin/uvicorn src.main:app --port 3002; exec bash" & \
		sleep 2; \
		gnome-terminal -- bash -c "cd backend_gateway && ../.venv/bin/uvicorn src.api.main:app --reload --host localhost --port 3003; exec bash" & \
		echo "✅ Opened 3 gnome-terminal windows"; \
	else \
		echo "❌ Multiple terminals not supported on this system"; \
		echo "💡 Use 'make run-foreground' instead"; \
		exit 1; \
	fi
	@echo ""
	@echo "🎉 All modules started in separate terminals!"
	@echo "📍 Service URLs: Data:8000 | Cortex:3002 | Gateway:3003"

# Watch live logs from all modules
watch-logs:
	@echo "📋 Watching live logs from all modules..."
	@echo "⚠️  Press Ctrl+C to stop watching"
	@echo ""
	@if [ -f data_foundation_project/logs/data_foundation.log ] && [ -f cortex_engine/logs/cortex_engine.log ] && [ -f backend_gateway/logs/backend_gateway.log ]; then \
		tail -f data_foundation_project/logs/data_foundation.log cortex_engine/logs/cortex_engine.log backend_gateway/logs/backend_gateway.log | \
		sed -e 's|^==> data_foundation_project/logs/data_foundation.log <==|📊 [DATA FOUNDATION]|' \
		    -e 's|^==> cortex_engine/logs/cortex_engine.log <==|🤖 [CORTEX ENGINE]|' \
		    -e 's|^==> backend_gateway/logs/backend_gateway.log <==|🔗 [BACKEND GATEWAY]|'; \
	else \
		echo "❌ Log files not found. Make sure modules are running with 'make run-all'"; \
	fi

# Start individual modules
run-data: kill-ports
	@echo "📊 Starting Module 1: Data Foundation (port 8000)..."
	@mkdir -p data_foundation_project/logs
	cd data_foundation_project/src && ../../.venv/bin/uvicorn api.main:app --host localhost --port 8000 --reload

run-cortex:
	@echo "🤖 Starting Module 2: Cortex Engine (port 3002)..."
	@mkdir -p cortex_engine/logs
	cd cortex_engine && ../.venv/bin/uvicorn src.main:app --port 3002

run-backend:
	@echo "🔗 Starting Module 3: Backend Gateway (port 3003)..."
	@mkdir -p backend_gateway/logs
	cd backend_gateway && ../.venv/bin/uvicorn src.api.main:app --reload --host localhost --port 3003

# Stop all modules
stop:
	@echo "🛑 Stopping all modules..."
	@if [ -f data_foundation_project/data_foundation.pid ]; then \
		kill `cat data_foundation_project/data_foundation.pid` 2>/dev/null || true; \
		rm -f data_foundation_project/data_foundation.pid; \
	fi
	@if [ -f cortex_engine/cortex_engine.pid ]; then \
		kill `cat cortex_engine/cortex_engine.pid` 2>/dev/null || true; \
		rm -f cortex_engine/cortex_engine.pid; \
	fi
	@if [ -f backend_gateway/backend_gateway.pid ]; then \
		kill `cat backend_gateway/backend_gateway.pid` 2>/dev/null || true; \
		rm -f backend_gateway/backend_gateway.pid; \
	fi
	@echo "🔪 Killing any remaining processes on ports..."
	-lsof -ti:8000 | xargs kill -9 2>/dev/null || true
	-lsof -ti:3002 | xargs kill -9 2>/dev/null || true
	-lsof -ti:3003 | xargs kill -9 2>/dev/null || true
	@echo "✅ All modules stopped."

# Health check all modules
test:
	@echo "🧪 Testing all modules..."
	@echo "📊 Module 1 (Data Foundation):"
	@curl -s http://localhost:8000/reports?limit=1 >/dev/null && echo "  ✅ ONLINE" || echo "  ❌ OFFLINE"
	@echo "🤖 Module 2 (Cortex Engine):"
	@curl -s http://localhost:3002/health >/dev/null && echo "  ✅ ONLINE" || echo "  ❌ OFFLINE"
	@echo "🔗 Module 3 (Backend Gateway):"
	@curl -s http://localhost:3003/api/backend/health >/dev/null && echo "  ✅ ONLINE" || echo "  ❌ OFFLINE"

# Detailed health check
health:
	@echo "🔍 Detailed Health Check..."
	@echo ""
	@echo "📊 Module 1 - Data Foundation (port 8000):"
	@curl -s http://localhost:8000/reports?limit=1 | head -3 2>/dev/null || echo "  ❌ Not responding"
	@echo ""
	@echo "🤖 Module 2 - Cortex Engine (port 3002):"
	@curl -s http://localhost:3002/health 2>/dev/null || echo "  ❌ Not responding"
	@echo ""
	@echo "🔗 Module 3 - Backend Gateway (port 3003):"
	@curl -s http://localhost:3003/api/backend/health 2>/dev/null || echo "  ❌ Not responding"

# Clean up environment
clean: stop
	@echo "🧹 Cleaning up..."
	rm -rf data_foundation_project/logs
	rm -rf cortex_engine/logs
	rm -rf backend_gateway/logs
	rm -f data_foundation_project/data_foundation.pid
	rm -f cortex_engine/cortex_engine.pid
	rm -f backend_gateway/backend_gateway.pid
	@echo "✅ Cleanup complete."

# Quick pipeline test
demo:
	@echo "🎯 Running Quick Pipeline Demo..."
	@echo "⏳ Please wait for all modules to be ready..."
	@sleep 5
	@echo ""
	@echo "1️⃣ Testing Data Foundation:"
	curl -s "http://localhost:8000/reports?limit=2" | head -5
	@echo ""
	@echo "2️⃣ Testing Cortex Engine:"
	curl -s -X POST http://localhost:3002/embed -H "Content-Type: application/json" -d '{"data": ["geological test"]}' | head -3
	@echo ""
	@echo "3️⃣ Testing Backend Gateway (requires login):"
	@TOKEN=$$(curl -s -X POST "http://localhost:3003/api/backend/auth/login" -H "Content-Type: application/json" -d '{"username": "admin", "password": "admin123"}' | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null) && \
	curl -s -X POST "http://localhost:3003/api/backend/geological-query" \
		-H "Authorization: Bearer $$TOKEN" \
		-H "Content-Type: application/json" \
		-d '{"query": "geological formations", "limit": 2}' | head -5 || echo "❌ Authentication failed"
	@echo ""
	@echo "✅ Demo complete!"

# Development shortcuts
dev: setup run-all

logs:
	@echo "📋 Recent logs from all modules:"
	@echo "📊 Data Foundation:"
	@tail -10 data_foundation_project/logs/data_foundation.log 2>/dev/null || echo "  No logs found"
	@echo "🤖 Cortex Engine:"
	@tail -10 cortex_engine/logs/cortex_engine.log 2>/dev/null || echo "  No logs found"
	@echo "🔗 Backend Gateway:"
	@tail -10 backend_gateway/logs/backend_gateway.log 2>/dev/null || echo "  No logs found"
