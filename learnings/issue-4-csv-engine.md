# Issue 4: CSV Ingestion Engine (Revised)

## Technical Overview
The CSV Ingestion Engine is the primary entry point for financial data into RupeePlan. This implementation prioritizes **data integrity** and **idempotency** over simple parsing.

### Key Engineering Constraints

#### 1. The "Float Trap" & Financial Precision
- **The Problem**: Floating-point numbers (`float`) in Python and many other languages are based on binary fractions (IEEE 754). This leads to rounding errors (e.g., `0.1 + 0.2 != 0.3`). In a financial app, a few cents/paise lost every day can lead to massive discrepancies over time.
- **The Solution**: We use Python's `Decimal` module. `Decimal` provides fixed-point and floating-point arithmetic with the precision required for financial transactions.
- **Implementation**:
    ```python
    from decimal import Decimal
    amount = Decimal(amount_str.replace(",", ""))
    ```

#### 2. Idempotency & Duplicate Prevention
- **The Problem**: Users often upload the same bank statement multiple times. Without protection, this would double their reported spending/income.
- **The Solution**: Every transaction row is hashed into a unique **digest**. We use SHA-256 to hash a combination of `account_id`, `date`, `amount`, and `description`.
- **Enforcement**: The `digest` column in the database has a `UNIQUE` constraint. Any attempt to insert a duplicate record will fail at the database level, ensuring data consistency even if the application logic attempts a double-insert.

#### 3. Real-World Bank Formats (Debit/Credit)
- **The Problem**: Standard CSV parsers look for an "amount" column. Real-world bank statements (especially Indian banks like HDFC, ICICI, SBI) separate transactions into "Withdrawal" (Debit) and "Deposit" (Credit) columns.
- **The Solution**: Our parser checks for both columns. It treats debits as negative values and credits as positive values, normalizing the data into a single `amount` field for the database.

---

## Interview Questions & Answers

### Q1: Why is `Decimal` better than `float` for financial applications?
**A**: `Decimal` has a user-alterable precision and can represent numbers exactly as humans do (base 10). `float` is base 2, which cannot exactly represent many decimal fractions (like 0.1), leading to cumulative errors in large datasets.

### Q2: How do you handle idempotency in a distributed system?
**A**: By using a unique natural key or a hash of the resource's content. In our case, we hash the transaction details. This "digest" acts as a fingerprint. By making this field unique in the database, we use the database's ACID properties to prevent duplicates across any number of concurrent workers.

### Q3: What is the benefit of storing `raw_data` for each transaction?
**A**: Auditability. If the parsing logic changes or a bug is discovered in how we handle certain bank formats, we can re-process the `raw_data` without asking the user to re-upload their files. It also helps in debugging edge cases where the parser fails to extract a field correctly.
