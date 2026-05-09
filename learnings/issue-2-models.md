# Interview Learnings: Issue #2 - Core Models & ORM

This document covers the theoretical concepts and interview-style questions related to data modeling and SQLAlchemy.

## 1. SQLAlchemy 2.0 Patterns
**Q: What is the difference between SQLAlchemy 1.x and 2.0 style?**
*   **Declarative Mapping:** 2.0 uses `Mapped` and `mapped_column` for better type hinting and integration with IDEs/Static Analyzers.
*   **Sync vs Async:** 2.0 has first-class support for async engines (`asyncpg`), which prevents blocking the event loop during DB operations.

## 2. Primary Keys: UUID vs Integer
**Q: Why use UUIDs for primary keys in a financial application?**
*   **Security:** Integers are predictable and can be used to guess record counts or scrape data (Insecure Direct Object Reference - IDOR).
*   **Distributed Systems:** UUIDs can be generated on the client or application layer without checking the DB for the "next" ID, which is essential for scaling.
*   **Merging Data:** If you ever need to merge databases, UUIDs will not collide, whereas auto-incrementing integers will.

## 3. Mixins & Code Reuse
**Q: What is a Mixin in SQLAlchemy?**
*   **Concept:** A class that provides functionality (columns/methods) to other classes via inheritance but is not intended to stand alone.
*   **Implementation:** We used `TimestampMixin` to automatically add `created_at` and `updated_at` to every model, ensuring consistent audit trails.

## 4. Financial Data Precision
**Q: Why use `Numeric/Decimal` instead of `Float` for balances and amounts?**
*   **Precision:** Floats use binary representation and lead to rounding errors (e.g., `0.1 + 0.2 != 0.3`).
*   **Accuracy:** `Numeric(12, 2)` ensures exact decimal representation, which is non-negotiable for financial calculations.

## 5. Relationships & Cascades
**Q: What does `cascade="all, delete-orphan"` do?**
*   **Integrity:** It ensures that if a parent record (e.g., a `User`) is deleted, all related records (e.g., their `Accounts`) are also deleted.
*   **Cleanliness:** It prevents "orphaned" records that point to non-existent parents, maintaining database hygiene.

## 6. Database Normalization
**Q: Why separate Transactions from Accounts?**
*   **1NF/2NF/3NF:** By normalizing the data, we ensure each piece of information is stored once. An Account has metadata (institution name, currency), while a Transaction tracks a specific event. Linking them via a Foreign Key (`account_id`) ensures data integrity.
