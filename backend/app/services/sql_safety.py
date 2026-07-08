from __future__ import annotations

from dataclasses import dataclass, field

from sqlglot import exp, parse_one
from sqlglot.errors import ParseError

from app.schemas import SQLValidationResponse
from app.settings import Settings


BLOCKED_EXPRESSIONS = tuple(
    getattr(exp, name)
    for name in [
        "Insert",
        "Update",
        "Delete",
        "Create",
        "Drop",
        "Alter",
        "TruncateTable",
        "Grant",
        "Revoke",
        "Copy",
        "Call",
        "Merge",
    ]
    if hasattr(exp, name)
)

SIDE_EFFECT_FUNCTIONS = {"pg_sleep", "dblink_connect", "lo_import"}


@dataclass
class SafetyAnalysis:
    is_valid: bool
    is_readonly: bool
    blocked_reason: str | None
    risk_level: str
    detected_statement_type: str
    referenced_tables: list[str] = field(default_factory=list)
    referenced_columns: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    normalized_sql: str | None = None
    suggested_sql: str | None = None

    def to_response(self) -> SQLValidationResponse:
        return SQLValidationResponse(**self.__dict__)


class SQLSafetyValidator:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def validate(self, sql: str, *, allow_write: bool = False) -> SafetyAnalysis:
        candidate = sql.strip()
        if not candidate:
            return self._blocked("SQL is empty.", "unknown")
        trimmed = candidate.rstrip(";").strip()
        if ";" in trimmed:
            return self._blocked("Multiple SQL statements are blocked.", "multiple")
        if "--" in trimmed or "/*" in trimmed:
            suspicious = "SQL contains comments. Review carefully for obfuscation."
        else:
            suspicious = None
        try:
            expression = parse_one(trimmed, dialect="postgres")
        except ParseError as exc:
            return self._blocked(f"SQL could not be parsed safely: {exc}", "parse_error")

        normalized = expression.sql(dialect="postgres", pretty=False)
        statement_type = expression.key.upper()
        referenced_tables = sorted({table.sql(dialect="postgres") for table in expression.find_all(exp.Table)})
        referenced_columns = sorted({column.sql(dialect="postgres") for column in expression.find_all(exp.Column)})
        warnings: list[str] = []
        if suspicious:
            warnings.append(suspicious)

        blocked_reason: str | None = None
        if self._is_blocked_command(normalized):
            blocked_reason = "Administrative or procedural SQL commands are blocked in this MVP."
        elif expression.find(BLOCKED_EXPRESSIONS):
            blocked_reason = "Write, DDL, privilege, or procedural SQL is blocked in this MVP."
        elif not allow_write and not self._is_readonly_shape(expression):
            blocked_reason = "Only read-only SELECT-style statements are allowed."
        elif self._is_explain_command(normalized) and "ANALYZE" in normalized.upper() and not self.settings.sql_enable_explain_analyze:
            blocked_reason = "EXPLAIN ANALYZE is disabled by configuration."
        elif "SECURITY DEFINER" in normalized.upper():
            blocked_reason = "SECURITY DEFINER statements are blocked."
        elif "SET ROLE" in normalized.upper() or normalized.upper().startswith("VACUUM"):
            blocked_reason = "Administrative statements are blocked."
        elif self._uses_side_effect_function(expression):
            blocked_reason = "Known side-effect functions are blocked in read-only mode."

        if "SELECT *" in normalized.upper():
            warnings.append("SELECT * can expose unnecessary columns and increase result size.")
        if "CROSS JOIN" in normalized.upper():
            warnings.append("CROSS JOIN can create very large result sets.")
        if self._looks_like_cartesian_join(normalized):
            warnings.append("Query may contain an implicit cartesian join.")
        if self._contains_sensitive_columns(expression):
            warnings.append("Query references potentially sensitive columns.")
        if self._uses_side_effect_function(expression):
            warnings.append("Query calls functions that may have side effects.")

        suggested_sql = self._ensure_limit(expression, self.settings.db_default_row_limit)
        if suggested_sql != normalized:
            warnings.append("Query had no LIMIT, so a bounded LIMIT was suggested.")

        risk_level = self._risk_level(blocked_reason, warnings)
        return SafetyAnalysis(
            is_valid=blocked_reason is None,
            is_readonly=blocked_reason is None,
            blocked_reason=blocked_reason,
            risk_level=risk_level,
            detected_statement_type=statement_type,
            referenced_tables=referenced_tables,
            referenced_columns=referenced_columns,
            warnings=list(dict.fromkeys(warnings)),
            normalized_sql=normalized,
            suggested_sql=suggested_sql,
        )

    def _blocked(self, reason: str, statement_type: str) -> SafetyAnalysis:
        return SafetyAnalysis(
            is_valid=False,
            is_readonly=False,
            blocked_reason=reason,
            risk_level="high",
            detected_statement_type=statement_type,
        )

    def _is_readonly_shape(self, expression: exp.Expression) -> bool:
        allowed = (exp.Select, exp.Union, exp.Intersect, exp.Except)
        if isinstance(expression, allowed):
            return True
        if isinstance(expression, exp.With) and expression.this is not None:
            return self._is_readonly_shape(expression.this)
        if expression.key.upper() == "COMMAND":
            return self._is_explain_command(expression.sql(dialect="postgres", pretty=False))
        return False

    def enforce_limit(self, sql: str, row_limit: int) -> str:
        expression = parse_one(sql.strip().rstrip(";"), dialect="postgres")
        return self._ensure_limit(expression, row_limit)

    def _ensure_limit(self, expression: exp.Expression, row_limit: int) -> str:
        copied = expression.copy()
        if copied.key.upper() == "COMMAND":
            return copied.sql(dialect="postgres", pretty=False)
        target = copied
        if isinstance(target, exp.With) and target.this is not None:
            target = target.this
        if isinstance(target, exp.Select):
            self._set_limit_if_needed(target, row_limit)
            return copied.sql(dialect="postgres", pretty=False)
        if isinstance(target, (exp.Union, exp.Intersect, exp.Except)):
            self._set_limit_if_needed(target, row_limit)
            return copied.sql(dialect="postgres", pretty=False)
        return copied.sql(dialect="postgres", pretty=False)

    def _set_limit_if_needed(self, expression: exp.Expression, row_limit: int) -> None:
        current_limit = expression.args.get("limit")
        current_value = self._literal_limit_value(current_limit) if current_limit is not None else None
        if current_limit is None or current_value is None or current_value > row_limit:
            expression.set("limit", exp.Limit(expression=exp.Literal.number(row_limit)))

    def _literal_limit_value(self, limit_expression: exp.Expression | None) -> int | None:
        if not isinstance(limit_expression, exp.Limit):
            return None
        expression = limit_expression.args.get("expression")
        if isinstance(expression, exp.Literal) and expression.is_number:
            try:
                return int(expression.this)
            except ValueError:
                return None
        return None

    def _contains_sensitive_columns(self, expression: exp.Expression) -> bool:
        patterns = self.settings.sensitive_column_patterns
        for column in expression.find_all(exp.Column):
            if any(pattern in column.name.lower() for pattern in patterns):
                return True
        return False

    def _uses_side_effect_function(self, expression: exp.Expression) -> bool:
        for func in expression.find_all(exp.Func):
            if func.name.lower() in SIDE_EFFECT_FUNCTIONS:
                return True
        return False

    def _looks_like_cartesian_join(self, sql: str) -> bool:
        upper = sql.upper()
        return " JOIN " in upper and " ON " not in upper and " USING " not in upper and " NATURAL JOIN " not in upper

    def _risk_level(self, blocked_reason: str | None, warnings: list[str]) -> str:
        if blocked_reason:
            return "high"
        if warnings:
            return "medium"
        return "low"

    def _is_explain_command(self, normalized_sql: str) -> bool:
        return normalized_sql.upper().startswith("EXPLAIN ")

    def _is_blocked_command(self, normalized_sql: str) -> bool:
        upper = normalized_sql.upper()
        if self._is_explain_command(upper):
            return False
        return upper.startswith(("VACUUM", "DO ", "CALL ", "SET ROLE", "SHOW ", "RESET ", "DISCARD "))
