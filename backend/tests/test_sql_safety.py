import pytest

from app.services.sql_safety import SQLSafetyValidator
from app.settings import Settings


validator = SQLSafetyValidator(Settings())


def test_select_allowed() -> None:
    result = validator.validate("SELECT id FROM users LIMIT 10")
    assert result.is_valid is True


def test_with_select_allowed() -> None:
    result = validator.validate("WITH recent AS (SELECT id FROM users) SELECT * FROM recent LIMIT 10")
    assert result.is_valid is True


def test_explain_select_allowed() -> None:
    result = validator.validate("EXPLAIN SELECT id FROM users LIMIT 10")
    assert result.is_valid is True


def test_drop_blocked() -> None:
    assert validator.validate("DROP TABLE users").is_valid is False


def test_delete_blocked() -> None:
    assert validator.validate("DELETE FROM users").is_valid is False


def test_update_blocked() -> None:
    assert validator.validate("UPDATE users SET name = 'x'").is_valid is False


def test_insert_blocked() -> None:
    assert validator.validate("INSERT INTO users(id) VALUES (1)").is_valid is False


def test_alter_blocked() -> None:
    assert validator.validate("ALTER TABLE users ADD COLUMN x int").is_valid is False


def test_create_blocked() -> None:
    assert validator.validate("CREATE TABLE demo(id int)").is_valid is False


def test_truncate_blocked() -> None:
    assert validator.validate("TRUNCATE TABLE users").is_valid is False


def test_copy_blocked() -> None:
    assert validator.validate("COPY users TO STDOUT").is_valid is False


def test_multiple_statements_blocked() -> None:
    assert validator.validate("SELECT 1; SELECT 2").is_valid is False


def test_select_without_limit_warning() -> None:
    result = validator.validate("SELECT id FROM users")
    assert any("LIMIT" in warning for warning in result.warnings)


def test_select_star_warning() -> None:
    result = validator.validate("SELECT * FROM users LIMIT 10")
    assert any("SELECT *" in warning for warning in result.warnings)


def test_cross_join_warning() -> None:
    result = validator.validate("SELECT * FROM users CROSS JOIN orders LIMIT 10")
    assert any("CROSS JOIN" in warning for warning in result.warnings)


def test_sensitive_column_warning() -> None:
    result = validator.validate("SELECT email FROM users LIMIT 10")
    assert any("sensitive" in warning.lower() for warning in result.warnings)


def test_side_effect_function_blocked() -> None:
    result = validator.validate("SELECT dblink_connect('dbname=other') LIMIT 1")
    assert result.is_valid is False
    assert result.blocked_reason is not None


def test_enforce_limit_reduces_large_limit() -> None:
    limited = validator.enforce_limit("SELECT id FROM users LIMIT 5000", 25)
    assert "LIMIT 25" in limited


@pytest.mark.parametrize(
    "sql",
    [
        "GRANT SELECT ON users TO app_user",
        "REVOKE SELECT ON users FROM app_user",
        "CALL refresh_cache()",
        "DO $$ BEGIN RAISE NOTICE 'x'; END $$",
        "VACUUM users",
        "SET ROLE admin",
        "CREATE FUNCTION x() RETURNS int LANGUAGE sql SECURITY DEFINER AS $$ SELECT 1 $$",
    ],
)
def test_additional_admin_or_procedural_sql_blocked(sql: str) -> None:
    result = validator.validate(sql)
    assert result.is_valid is False


def test_comment_obfuscation_warning() -> None:
    result = validator.validate("SELECT id FROM users -- inspect\nLIMIT 10")
    assert any("comments" in warning.lower() for warning in result.warnings)
