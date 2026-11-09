import pytest
from app.services.sql_guard import SQLGuardError, validate_readonly_sql

def test_select_allowed():
    validate_readonly_sql("SELECT region, SUM(sales_amount) FROM sales_metrics GROUP BY region LIMIT 10")

def test_delete_rejected():
    with pytest.raises(SQLGuardError):
        validate_readonly_sql("DELETE FROM sales_metrics")
