# Interview Learnings: Issue #1 - Project Initialization

This document covers the theoretical concepts and interview-style questions related to project bootstrapping and architectural setup.

## 1. Project Structure & Scaffolding
**Q: Why separate the application into `api`, `core`, `db`, `models`, and `services`?**
*   **Separation of Concerns (SoC):** Ensures that business logic (`services`), data definitions (`models`), and interface logic (`api`) are decoupled. This makes the codebase easier to test, maintain, and scale.
*   **Modular Growth:** As the project grows, new features can be added as new modules without affecting the core engine.

## 2. Trunk-Based Development
**Q: What is Trunk-Based Development and why use it over GitFlow?**
*   **Concept:** Developers merge small, frequent updates to a single branch ("trunk" or `main`).
*   **Advantages:** 
    *   Reduces "merge hell" by avoiding long-lived feature branches.
    *   Encourages continuous integration.
    *   Enables faster feedback loops.
*   **Best Practice:** Use short-lived branches (hours/days) for PRs, ensuring the trunk is always in a deployable state.

## 3. Dependency Management
**Q: Why use `requirements.txt` instead of just installing globally?**
*   **Reproducibility:** Ensures that every developer and the CI/CD pipeline use the exact same versions of libraries.
*   **Isolation:** Prevents version conflicts between different projects on the same machine.

## 4. Environment Configuration
**Q: What is the purpose of `.env.example`?**
*   **Documentation:** Acts as a template for required secrets (API keys, DB credentials) without exposing actual sensitive data to version control.
*   **Onboarding:** Helps new developers quickly identify what configuration is needed to run the app locally.

## 5. Framework Choice: FastAPI
**Q: Why FastAPI for a FinOps project?**
*   **Performance:** Built on Starlette and Pydantic, it's one of the fastest Python frameworks available.
*   **Async Support:** Native support for `async/await`, which is crucial for I/O bound tasks like database queries and API calls.
*   **Auto-Documentation:** Generates Swagger/OpenAPI docs automatically, facilitating faster frontend-backend integration.
