# Implementation Stage: Local Mode & Fallback Support (Modules 1-3)

## Overview

This document summarizes the current implementation stage of the first three modules in the AI Full-Stack Geological Data Pipeline, with a special focus on local mode support and fallback mechanisms.

---

## Modules Covered

- **Module 1: Data Foundation**
- **Module 2: Cortex Engine**
- **Module 3: Backend Gateway**

---

## Local Mode Support

All three modules are designed to run locally for development and testing. The default configuration and Makefile targets use `localhost` and standard ports:

- **Module 1:** http://localhost:8000
- **Module 2:** http://localhost:3002
- **Module 3:** http://localhost:3003

You can start all modules locally using:

```bash
make run-all
```

Or start them individually:

```bash
make run-data      # Module 1
make run-cortex    # Module 2
make run-backend   # Module 3
```

### Key Points

- No cloud infrastructure is required for local development.
- All APIs and services are accessible via localhost.
- Local mode is the default for all quick start and development workflows.

---

## Fallback Mechanisms

### Module 2: Cortex Engine

- **Azure OpenAI Dependency:** By default, Module 2 uses Azure OpenAI for embeddings and RAG (Retrieval-Augmented Generation).
- **Fallback Mode:** If Azure OpenAI credentials are not configured, Module 2 will fall back to generating random embeddings. This allows development and testing without incurring cloud costs or requiring cloud access.
- **Configuration:**
  - If `.env` is missing or incomplete, fallback mode is automatically enabled.
  - This is useful for rapid prototyping and for environments without Azure access.

### Module 1 & 3

- No external cloud dependencies are required for local mode.
- All data and APIs are served from local files and processes.

---

## Cloud Deployment (Optional)

- All modules can be containerized and deployed to cloud platforms (e.g., Azure, AWS, GCP) for production.
- Local mode remains fully supported and is recommended for development and testing.

---

## Summary Table

| Module              | Local Mode | Fallback Support  | Cloud Dependency (Default) |
| ------------------- | ---------- | ----------------- | -------------------------- |
| Data Foundation (1) | Yes        | N/A               | No                         |
| Cortex Engine (2)   | Yes        | Random embeddings | Azure OpenAI (optional)    |
| Backend Gateway (3) | Yes        | N/A               | No                         |

---

## References

- See `README.md`, `QUICK_START.md`, and `Makefile` for more details on running locally.
- For Azure OpenAI fallback, see `cortex_engine/docs/EXECUTION.md`.

---

**Last updated:** $(date +%Y-%m-%d)
