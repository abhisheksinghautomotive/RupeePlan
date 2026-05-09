# Interview Learnings: Issue #3 - Docker & Containerization

This document covers the theoretical concepts and interview-style questions related to containerizing a Python application with Docker and Docker Compose.

## 1. Docker vs. Virtual Machines
**Q: What is the main difference between Docker and a VM?**
*   **Kernel Sharing:** Docker containers share the host OS kernel, making them lightweight and fast to start. VMs include a full guest OS, which consumes more resources and is slower.
*   **Isolation:** Containers provide process-level isolation, whereas VMs provide hardware-level isolation.

## 2. Multi-Container Orchestration (Docker Compose)
**Q: Why use Docker Compose for local development?**
*   **Infrastructure as Code:** It allows you to define your entire stack (API, DB, Redis) in a single YAML file.
*   **Service Dependency:** Using `depends_on` with `condition: service_healthy` ensures that the API only starts after the database is ready to accept connections.
*   **Networking:** Docker Compose automatically creates a virtual network where containers can talk to each other using their service names (e.g., `db:5432`).

## 3. Dockerfile Optimization
**Q: Why use `python:3.11-slim` instead of just `python:3.11`?**
*   **Image Size:** `slim` images remove unnecessary packages, reducing the attack surface and making deployment faster.
*   **Layer Caching:** By copying `requirements.txt` and installing dependencies *before* copying the rest of the code, we ensure that Docker only re-installs packages if the requirements change, saving build time.

## 4. Environment Variables in Docker
**Q: How do you handle secrets in Docker Compose?**
*   **Env Files:** We use `.env` files to pass configuration to containers. In production, these would be managed by a secrets manager (like AWS Secrets Manager or K8s Secrets).
*   **Default Values:** Using `${VAR:-default}` in `docker-compose.yml` provides fallback values if the environment variable isn't set.

## 5. Persistence with Volumes
**Q: What happens to your database data when a container is deleted?**
*   **Ephemeral vs. Persistent:** By default, data inside a container is lost when it's removed. We use **Volumes** (`postgres_data:/var/lib/postgresql/data/`) to map a directory on the host (or a managed volume) to the container, ensuring data persists across restarts.

## 6. Healthchecks
**Q: Why are healthchecks important in Docker?**
*   **Ready for Traffic:** A container might be "running" but not yet "ready" (e.g., Postgres is starting up). Healthchecks allow Docker and orchestrators to know when a service is actually functional, preventing connection errors in dependent services.
