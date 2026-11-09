import re
import sqlglot
from sqlglot import exp

ALLOWED_TABLES = {"sales_metrics"}

class SQLGuardError(ValueError):
    pass

def validate_readonly_sql(sql: str) -> None:
    try:
        parse_sql = re.sub(r":[A-Za-z_][A-Za-z0-9_]*", "'__bind__'", sql)
        statements = sqlglot.parse(parse_sql)
    except Exception as exc:
        raise SQLGuardError(f"SQL 无法解析: {exc}") from exc

    if len(statements) != 1:
        raise SQLGuardError("只允许执行单条 SQL")

    statement = statements[0]
    if not isinstance(statement, exp.Select):
        raise SQLGuardError("只允许 SELECT 查询")

    dangerous = (exp.Insert, exp.Update, exp.Delete, exp.Drop, exp.Alter, exp.Create, exp.Command)
    if any(statement.find(node_type) is not None for node_type in dangerous):
        raise SQLGuardError("检测到禁止的 SQL 操作")

    tables = {table.name for table in statement.find_all(exp.Table)}
    if not tables.issubset(ALLOWED_TABLES):
        raise SQLGuardError(f"访问了未授权数据表: {tables - ALLOWED_TABLES}")

    if statement.args.get("limit") is None:
        raise SQLGuardError("生产查询必须包含 LIMIT")
