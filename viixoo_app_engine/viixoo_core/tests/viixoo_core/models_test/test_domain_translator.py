"""Tests for the DomainTranslator class."""

from viixoo_core.models.domain import DomainTranslator
from typing import Any, List


class TestDomainTranslator:
    """Test the DomainTranslator class."""

    def test_translate_empty_domain(self):
        """Test translate method with an empty domain."""
        # Arrange
        domain: List[Any] = []

        # Act
        sql_query, params = DomainTranslator.translate(domain)

        # Assert
        assert sql_query == "1=1"
        assert params == []

    def test_translate_simple_domain(self):
        """Test translate method with a simple domain (single condition)."""
        # Arrange
        domain = [("name", "=", "John")]

        # Act
        sql_query, params = DomainTranslator.translate(domain)

        # Assert
        assert sql_query == "WHERE name = %s"
        assert params == ["John"]

    def test_translate_multiple_conditions_and(self):
        """Test translate method with multiple conditions joined by AND."""
        # Arrange
        domain = [("name", "like", "John"), ("age", ">", 30)]

        # Act
        sql_query, params = DomainTranslator.translate(domain)

        # Assert
        assert sql_query == "WHERE name LIKE %s AND age > %s"
        assert params == ["John", 30]

    def test_translate_multiple_conditions_or(self):
        """Test translate method with multiple conditions joined by OR."""
        # Arrange
        domain = [
            ("name", "like", "John"),
            "|",
            ("age", ">", 30),
            ("city", "=", "New York"),
        ]

        # Act
        sql_query, params = DomainTranslator.translate(domain)

        # Assert
        assert sql_query == "WHERE name LIKE %s AND (age > %s OR city = %s)"
        assert params == ["John", 30, "New York"]

    def test_translate_not_condition(self):
        """Test translate method with a NOT condition."""
        # Arrange
        domain = ["!", ("status", "=", "inactive")]

        # Act
        sql_query, params = DomainTranslator.translate(domain)

        # Assert
        assert sql_query == "WHERE NOT (status = %s)"
        assert params == ["inactive"]

    def test_translate_complex_domain(self):
        """Test translate method with a complex domain."""
        # Arrange
        domain = [
            ("name", "ilike", "John"),
            ("age", ">=", 30),
            ("id", "in", [1, 2, 3]),
            ("active", "is not null", None),
            "|",
            ("name", "like", "Doe"),
            ("email", "ilike", "example.com"),
            "!",
            ("status", "=", "inactive"),
        ]

        # Act
        sql_query, params = DomainTranslator.translate(domain)
        expec_name = "name ILIKE %s"
        expec_age = "age >= %s"
        expec_id = "id IN (%s, %s, %s)"
        expec_active = "active IS NOT NULL"
        expec_name_like = "name LIKE %s"
        expec_email_ilike = "email ILIKE %s"
        expec_status = "NOT (status = %s)"
        expected = f"{expec_name} AND {expec_age} AND {expec_id} AND {expec_active}"
        expected += (
            f" AND ({expec_name_like} OR {expec_email_ilike}) AND {expec_status}"
        )
        # Assert
        assert sql_query == "WHERE " + expected
        assert params == ["John", 30, 1, 2, 3, "Doe", "example.com", "inactive"]

    def test_translate_ilike_conditions(self):
        """Test translate method with ILIKE conditions."""
        # Arrange
        domain = [("name", "ilike", "john"), ("email", "not ilike", "test.com")]

        # Act
        sql_query, params = DomainTranslator.translate(domain)

        # Assert
        assert sql_query == "WHERE name ILIKE %s AND email NOT ILIKE %s"
        assert params == ["john", "test.com"]

    def test_translate_like_conditions(self):
        """Test translate method with LIKE conditions."""
        # Arrange
        domain = [("name", "like", "john"), ("email", "not like", "test.com")]

        # Act
        sql_query, params = DomainTranslator.translate(domain)

        # Assert
        assert sql_query == "WHERE name LIKE %s AND email NOT LIKE %s"
        assert params == ["john", "test.com"]

    def test_translate_startswith_conditions(self):
        """Test translate method with startswith conditions."""
        # Arrange
        domain = [("name", "startswith", "John")]

        # Act
        sql_query, params = DomainTranslator.translate(domain)

        # Assert
        assert sql_query == "WHERE name LIKE %s"
        assert params == ["John%"]

    def test_translate_endswith_conditions(self):
        """Test translate method with endswith conditions."""
        # Arrange
        domain = [("name", "endswith", "Doe")]

        # Act
        sql_query, params = DomainTranslator.translate(domain)

        # Assert
        assert sql_query == "WHERE name LIKE %s"
        assert params == ["%Doe"]

    def test_translate_contains_conditions(self):
        """Test translate method with contains conditions."""
        # Arrange
        domain = [("name", "contains", "test")]

        # Act
        sql_query, params = DomainTranslator.translate(domain)

        # Assert
        assert sql_query == "WHERE name LIKE %s"
        assert params == ["%test%"]

    def test_translate_in_conditions(self):
        """Test translate method with IN conditions."""
        # Arrange
        domain = [("id", "in", [1, 2, 3]), ("age", "not in", (10, 20))]

        # Act
        sql_query, params = DomainTranslator.translate(domain)

        # Assert
        assert sql_query == "WHERE id IN (%s, %s, %s) AND age NOT IN (%s, %s)"
        assert params == [1, 2, 3, 10, 20]

    def test_translate_is_null_conditions(self):
        """Test translate method with IS NULL conditions."""
        # Arrange
        domain = [("name", "is null", None), ("id", "is not null", None)]

        # Act
        sql_query, params = DomainTranslator.translate(domain)

        # Assert
        assert sql_query == "WHERE name IS NULL AND id IS NOT NULL"
        assert params == []

    def test_translate_child_of_condition(self):
        """Test translate method with child_of condition."""
        # Arrange
        domain = [("parent_id", "child_of", 5)]

        # Act
        sql_query, params = DomainTranslator.translate(domain)

        # Assert
        assert (
            sql_query
            == "WHERE parent_id IN (SELECT id FROM some_table WHERE parent_id = %s)"
        )
        assert params == [5]

    def test_translate_simple_not_condition(self):
        """Test translate method with a NOT condition."""
        # Arrange
        domain = [("name", "!=", "Jack")]

        # Act
        sql_query, params = DomainTranslator.translate(domain)

        # Assert
        assert sql_query == "WHERE name != %s"
        assert params == ["Jack"]

    def test_translate_multiple_not(self):
        """Test translate method with multiple not condition."""
        # Arrange
        domain = [
            "&",
            "&",
            "&",
            ("name1", "!=", "Jack"),
            ("name2", "!=", "Sam"),
            ("name3", "!=", "Daniel"),
        ]

        # Act
        sql_query, params = DomainTranslator.translate(domain)

        # Assert
        assert sql_query == "WHERE (name1 != %s AND name2 != %s AND name3 != %s)"
        assert params == ["Jack", "Sam", "Daniel"]

    def test_translate_multiple_not_or(self):
        """Test translate method with multiple not or condition."""
        # Arrange
        domain = [
            "!",
            "|",
            "|",
            ("name", "=", "Jack"),
            ("name", "=", "Sam"),
            ("name", "=", "Daniel"),
        ]
        # Act
        sql_query, params = DomainTranslator.translate(domain)

        # Assert
        assert sql_query == "WHERE NOT ((name = %s OR name = %s OR name = %s))"
        assert params == ["Jack", "Sam", "Daniel"]

    def test_translate_multiple_and(self):
        """Test translate method with multiple not or condition."""
        # Arrange
        domain = [
            ("name", "=", "Jack"),
            ("name", "=", "Sam"),
            ("name", "=", "Daniel"),
        ]
        # Act
        sql_query, params = DomainTranslator.translate(domain)

        # Assert
        assert sql_query == "WHERE name = %s AND name = %s AND name = %s"
        assert params == ["Jack", "Sam", "Daniel"]

    def test_translate_multiple_or(self):
        """Test translate method with multiple not or condition."""
        # Arrange
        domain = [
            "|",
            "|",
            "|",
            ("name", "=", "Jack"),
            ("name", "=", "Sam"),
            ("name", "=", "Daniel"),
        ]
        # Act
        sql_query, params = DomainTranslator.translate(domain)

        # Assert
        assert sql_query == "WHERE (name = %s OR name = %s OR name = %s)"
        assert params == ["Jack", "Sam", "Daniel"]

    def test_translate_multiple_and_or(self):
        """Test translate method with multiple not or condition."""
        # Arrange
        domain = [
            "|",
            ("name", "=", "Jack"),
            "&",
            ("field1", "=", "Sam"),
            ("field2", "=", "Daniel"),
        ]
        # Act
        sql_query, params = DomainTranslator.translate(domain)

        # Assert
        assert sql_query == "WHERE (name = %s OR (field1 = %s AND field2 = %s))"
        assert params == ["Jack", "Sam", "Daniel"]
