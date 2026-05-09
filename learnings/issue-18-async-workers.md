# Issue 5: Database Storage & Async Workers

## Technical Overview
In this issue, we transitioned from a synchronous CSV parsing engine to an asynchronous background processing architecture using **Celery** and **Redis**. We also implemented database persistence using **SQLAlchemy 2.0 (Async)**.

### Key Concepts Implemented

#### 1. Background Task Orchestration (Celery + Redis)
- **Problem**: Parsing large CSV files and saving thousands of records to a database is a slow operation. If done in the request-response cycle, it would block the API and lead to timeouts.
- **Solution**: Offload the heavy lifting to a background worker.
- **Components**:
    - **Producer (FastAPI)**: Dispatches the task to the queue.
    - **Broker (Redis)**: Stores the tasks waiting to be processed.
    - **Consumer (Celery Worker)**: Picks up tasks and executes them.
- **Benefit**: The user gets an immediate response with a `task_id`, while the processing happens in the background.

#### 2. Async Database Persistence
- We used **SQLAlchemy 2.0's Async extension** to handle database operations without blocking the event loop.
- **AsyncSession**: Manages the lifecycle of a database transaction in an asynchronous way.
- **Lifespan Events**: Used FastAPI's `lifespan` context manager to initialize the database (creating tables) when the application starts.

#### 3. Task Serialization
- Celery needs to serialize data to send it through Redis. We chose **JSON** serialization.
- **Constraint**: Complex Python objects (like bytes or SQLAlchemy models) cannot be serialized directly. We converted the CSV bytes to a string and IDs to strings before passing them to the task.

---

## Interview Questions & Answers

### Q1: Why use a background worker for file uploads?
**A**: To avoid blocking the API's main thread and the user's connection. File parsing and DB insertion are I/O intensive and time-consuming. Offloading them ensures the API remains responsive and can handle high concurrency.

### Q2: What is a Message Broker, and why did we use Redis?
**A**: A Message Broker is a piece of software that facilitates communication between different parts of a system by passing messages. We used Redis because it is extremely fast, supports pub/sub patterns, and is easy to set up for Celery.

### Q3: How do you handle database sessions in a background worker?
**A**: Since Celery tasks are often long-running and can run in multiple processes, each task should create and close its own database session. In our implementation, we used `asyncio.run` within the task to manage the async session lifecycle.

### Q4: What happens if the worker crashes mid-task?
**A**: If a task fails or the worker crashes, the task can be retried if configured (Visibility Timeout). For financial data, idempotency is key—we should ensure that re-running a task doesn't create duplicate transactions (e.g., using a hash of the raw data as a unique constraint).

### Q5: Why is JSON serialization used for Celery tasks?
**A**: JSON is a standard, language-agnostic format. While `pickle` can serialize more complex Python objects, it is a security risk (remote code execution) and not recommended for production. JSON forces us to pass clean, primitive data types.
