# Development Steps - Detailed Explanation

## **Step 1: Environment Setup**

### **What is a Virtual Environment?**
```bash
python -m venv venv
```

**What this does:**
- Creates an isolated Python environment in a folder called `venv`
- Prevents dependency conflicts between projects
- Keeps your system Python clean

**Think of it like:** Each project gets its own toolbox, so tools from different projects don't interfere with each other.

### **Activating the Environment**
```bash
# On Mac/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

**What this does:**
- Switches your terminal to use the isolated Python environment
- When activated, you'll see `(venv)` at the start of your command line
- All Python commands now use this environment's packages

**Visual indicator:**
```bash
# Before activation:
user@computer:~/data-foundation$ 

# After activation:
(venv) user@computer:~/data-foundation$ 
```

### **Installing Dependencies**
```bash
pip install -r requirements.txt
```

**What this does:**
- Reads the `requirements.txt` file
- Downloads and installs all listed packages (FastAPI, uvicorn, pydantic)
- Installs them ONLY in the virtual environment

**requirements.txt contains:**
```
fastapi==0.104.1    # Web framework for building APIs
uvicorn==0.24.0     # ASGI server to run FastAPI
pydantic==2.5.0     # Data validation library
```

---

## **Step 2: Running the Application**

### **Start the Server**
```bash
python main.py
```

**What happens:**
1. Python executes `main.py`
2. FastAPI creates a web server
3. Uvicorn starts the server on `http://localhost:3001`
4. Server waits for HTTP requests

**You'll see output like:**
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:3001 (Press CTRL+C to quit)
```

**What this means:**
- Server is running and ready
- Accessible at `http://localhost:3001`
- Press `Ctrl+C` to stop the server

---

## **Step 3: Testing the API**

### **Health Check Test**
```bash
curl http://localhost:3001/api/data/health
```

**What curl does:**
- Makes an HTTP GET request to the health endpoint
- Shows the response from your API

**Expected response:**
```json
{
  "status": "healthy",
  "record_count": 3
}
```

**What this proves:**
- Your API server is running
- The health endpoint works
- Database connection is working (shows record count)

### **Data Retrieval Test**
```bash
curl http://localhost:3001/api/data/geological-sites
```

**Expected response:**
```json
[
  {
    "id": 1,
    "name": "Kalgoorlie Gold Mine",
    "latitude": -30.7489,
    "longitude": 121.4656,
    "mineral_type": "gold"
  },
  {
    "id": 2,
    "name": "Mount Gibson Iron",
    "latitude": -29.1167,
    "longitude": 117.2167,
    "mineral_type": "iron_ore"
  }
]
```

**What this proves:**
- Your API can serve geological data
- JSON serialization works
- Other modules can call this endpoint

### **Alternative Testing Methods**

**Using a web browser:**
```
Open: http://localhost:3001/api/data/health
Open: http://localhost:3001/api/data/geological-sites
```

**Using FastAPI's built-in docs:**
```
Open: http://localhost:3001/docs
```
This gives you an interactive API documentation interface.

---

## **Step 4: Docker Deployment**

### **Building the Docker Image**
```bash
docker build -t data-foundation .
```

**What this command does:**
- Reads the `Dockerfile` in current directory (`.`)
- Creates a Docker image named `data-foundation` (`-t` flag)
- Packages your entire application into a container

**Docker build process:**
1. **Base Image**: Starts with Python 3.11 slim
2. **Dependencies**: Installs packages from requirements.txt
3. **Code Copy**: Copies your application files
4. **Configuration**: Sets up port 3001 and startup command

### **Running the Docker Container**
```bash
docker run -p 3001:3001 data-foundation
```

**What this does:**
- Starts a new container from the `data-foundation` image
- Maps port 3001 from container to port 3001 on your machine (`-p 3001:3001`)
- Your API is now accessible at `http://localhost:3001`

**Why use Docker?**
- **Consistency**: Runs the same way on any machine
- **Isolation**: Doesn't interfere with other applications
- **Deployment**: Easy to deploy to cloud platforms
- **Scalability**: Easy to run multiple instances

---

## **Complete Workflow Example**

```bash
# 1. Start fresh
cd data-foundation
python -m venv venv
source venv/bin/activate  # You'll see (venv) appear

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start the server
python main.py
# Leave this running, open a new terminal for testing

# 4. Test in new terminal window
curl http://localhost:3001/api/data/health
# Should see: {"status": "healthy", "record_count": 3}

curl http://localhost:3001/api/data/geological-sites
# Should see: Array of geological sites

# 5. Stop the server (in original terminal)
# Press Ctrl+C

# 6. Build and run with Docker
docker build -t data-foundation .
docker run -p 3001:3001 data-foundation
# Server now runs in Docker container

# 7. Test Docker deployment
curl http://localhost:3001/api/data/health
# Should work the same way
```

---

## **Common Issues & Solutions**

### **Virtual Environment Issues**
```bash
# Problem: Command not found
# Solution: Make sure Python is installed
python --version

# Problem: Permission denied
# Solution: Use python3 instead
python3 -m venv venv
```

### **Port Already in Use**
```bash
# Problem: Port 3001 is busy
# Solution: Kill existing process
sudo lsof -i :3001
kill -9 <process_id>

# Or use different port
uvicorn main:app --port 3002
```

### **Docker Issues**
```bash
# Problem: Docker not installed
# Solution: Install Docker Desktop

# Problem: Permission denied
# Solution: Add user to docker group (Linux)
sudo usermod -aG docker $USER
```

This step-by-step approach ensures you understand **exactly what each command does** and **why it's necessary** for professional development workflow.