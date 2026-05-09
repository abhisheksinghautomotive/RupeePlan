import csv
import io
import hashlib
from datetime import datetime
from decimal import Decimal
from typing import List, Dict, Any

class CSVParserService:
    @staticmethod
    def generate_digest(account_id: str, date_str: str, amount: Decimal, description: str) -> str:
        """
        Generates a unique SHA-256 hash for a transaction to ensure idempotency.
        """
        payload = f"{account_id}|{date_str}|{amount}|{description.strip()}"
        return hashlib.sha256(payload.encode()).hexdigest()

    @classmethod
    def parse_statement(cls, content: bytes, filename: str, account_id: str) -> Dict[str, Any]:
        """
        Parses a bank statement CSV and returns a summary of the result.
        Handles Indian bank statement formats (Debit/Credit columns).
        Ensures idempotency by generating a unique digest for each row.
        """
        decoded_content = content.decode("utf-8")
        file_io = io.StringIO(decoded_content)
        reader = csv.DictReader(file_io)
        
        records = []
        errors = []
        success_count = 0
        fail_count = 0
        
        for i, row in enumerate(reader):
            try:
                # Basic validation logic
                clean_row = {k.lower().strip(): v for k, v in row.items()}
                
                # 1. Handle Date
                date_str = None
                for k in ["date", "transaction date", "value date"]:
                    if k in clean_row:
                        date_str = clean_row[k]
                        break
                
                if not date_str:
                    raise ValueError(f"Row {i+1}: Missing date field")
                
                parsed_date = None
                # Support common formats including Indian bank variations like 01-Jan-24
                for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%d-%b-%y", "%d-%m-%Y"):
                    try:
                        parsed_date = datetime.strptime(date_str, fmt).date()
                        break
                    except ValueError:
                        continue
                
                if not parsed_date:
                    raise ValueError(f"Row {i+1}: Invalid date format '{date_str}'")
                
                # 2. Handle Amount (Debit/Credit Logic)
                # We NEVER use floats for currency to avoid precision errors.
                amount = Decimal("0.00")
                
                # Check for single 'amount' column first
                if "amount" in clean_row and clean_row["amount"]:
                    amount_str = clean_row["amount"].replace(",", "").strip()
                    amount = Decimal(amount_str)
                else:
                    # Check for Debit/Credit columns (common in Indian banks like HDFC/ICICI)
                    debit_str = clean_row.get("withdrawal", clean_row.get("debit", "0")).replace(",", "").strip()
                    credit_str = clean_row.get("deposit", clean_row.get("credit", "0")).replace(",", "").strip()
                    
                    debit = Decimal(debit_str) if debit_str and debit_str != "0" else Decimal("0")
                    credit = Decimal(credit_str) if credit_str and credit_str != "0" else Decimal("0")
                    
                    if debit > 0:
                        amount = -debit
                    elif credit > 0:
                        amount = credit
                
                if amount == 0 and not (debit_str == "0" and credit_str == "0"):
                     # Skip empty rows or header-like artifacts
                     continue

                # 3. Handle Description
                description = "No Description"
                for k in ["description", "narration", "transaction details", "particulars"]:
                    if k in clean_row and clean_row[k]:
                        description = clean_row[k]
                        break
                
                # 4. Generate Idempotency Digest
                # This ensures that uploading the same file twice won't create duplicate records.
                digest = cls.generate_digest(account_id, str(parsed_date), amount, description)

                records.append({
                    "date": parsed_date,
                    "amount": amount,
                    "description": description,
                    "digest": digest,
                    "raw_data": str(row)
                })
                success_count += 1
                
            except Exception as e:
                errors.append(str(e))
                fail_count += 1
                
        return {
            "filename": filename,
            "total_records": success_count + fail_count,
            "successful_records": success_count,
            "failed_records": fail_count,
            "errors": errors,
            "data": records
        }
