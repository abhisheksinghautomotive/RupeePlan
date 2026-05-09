import pytest
from decimal import Decimal
from app.services.parser import CSVParserService

def test_parser_decimal_precision():
    """
    Test that the parser uses Decimal and avoids floating point errors.
    """
    csv_content = b"Date,Description,Amount\n2024-01-01,Test,100.10"
    result = CSVParserService.parse_statement(csv_content, "test.csv", "66e0689b-8913-40a2-990a-a03577317789")
    
    amount = result["data"][0]["amount"]
    assert isinstance(amount, Decimal)
    assert amount == Decimal("100.10")

def test_parser_indian_bank_debit_credit():
    """
    Test that the parser correctly handles Withdrawal/Deposit columns.
    """
    csv_content = (
        "Date,Narration,Withdrawal,Deposit\n"
        "01-Jan-24,Rent,50000.00,0.00\n"
        "02-Jan-24,Salary,0.00,120000.00"
    ).encode("utf-8")
    
    result = CSVParserService.parse_statement(csv_content, "hdfc.csv", "66e0689b-8913-40a2-990a-a03577317789")
    
    assert result["successful_records"] == 2
    
    # Rent should be negative
    rent_tx = result["data"][0]
    assert rent_tx["amount"] == Decimal("-50000.00")
    
    # Salary should be positive
    salary_tx = result["data"][1]
    assert salary_tx["amount"] == Decimal("120000.00")

def test_parser_idempotency_digest():
    """
    Test that the digest remains consistent for the same data.
    """
    csv_content = b"Date,Description,Amount\n2024-01-01,Lunch,250.50"
    account_id = "66e0689b-8913-40a2-990a-a03577317789"
    
    result1 = CSVParserService.parse_statement(csv_content, "file1.csv", account_id)
    result2 = CSVParserService.parse_statement(csv_content, "file2.csv", account_id)
    
    assert result1["data"][0]["digest"] == result2["data"][0]["digest"]
