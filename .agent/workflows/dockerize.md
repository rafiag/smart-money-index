---
description: Containerize the application with Docker
---
1. Analyze the codebase to detect the language (Node, Python, Go) and dependencies (e.g., package.json, requirements.txt, go.mod).
2. Create a `Dockerfile` optimized for production, using multi-stage builds where appropriate for the detected language.
3. Create a `.dockerignore` file to exclude `node_modules`, `.git`, `.env`, and other non-essential files.
4. Check the codebase for database configurations or dependencies; if detected, create a `docker-compose.yml` file to orchestrate the application and its database.
