"""Tests for helper functions in server.py."""

import pytest
import sys
import os

# Add parent directory to path to import server module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server import format_number, format_percent


class TestFormatNumber:
    """Tests for format_number helper function."""

    def test_format_none_returns_na(self):
        """Should return N/A for None values."""
        assert format_number(None) == "N/A"

    def test_format_small_number(self):
        """Should format small numbers with dollar sign and commas."""
        assert format_number(1234.56) == "$1,234.56"
        assert format_number(999.99) == "$999.99"
        assert format_number(0) == "$0.00"

    def test_format_millions(self):
        """Should format millions with M suffix."""
        assert format_number(1000000) == "$1.00M"
        assert format_number(5500000) == "$5.50M"
        assert format_number(999999999) == "$1000.00M"

    def test_format_billions(self):
        """Should format billions with B suffix."""
        assert format_number(1000000000) == "$1.00B"
        assert format_number(2870000000000) == "$2.87T"  # Apple market cap

    def test_format_trillions(self):
        """Should format trillions with T suffix."""
        assert format_number(1000000000000) == "$1.00T"
        assert format_number(3500000000000) == "$3.50T"

    def test_format_negative_numbers(self):
        """Should handle negative numbers correctly."""
        assert format_number(-1000000) == "$-1.00M"
        assert format_number(-1000000000) == "$-1.00B"

    def test_format_custom_decimals(self):
        """Should respect custom decimal places."""
        assert format_number(1234.5678, decimals=0) == "$1,235"
        assert format_number(1234.5678, decimals=4) == "$1,234.5678"
        assert format_number(1000000, decimals=1) == "$1.0M"

    def test_format_integer_input(self):
        """Should handle integer input."""
        assert format_number(1000) == "$1,000.00"
        assert format_number(5000000) == "$5.00M"


class TestFormatPercent:
    """Tests for format_percent helper function."""

    def test_format_none_returns_na(self):
        """Should return N/A for None values."""
        assert format_percent(None) == "N/A"

    def test_format_positive_percent(self):
        """Should format positive percentages with + sign."""
        assert format_percent(5.5) == "+5.50%"
        assert format_percent(100.0) == "+100.00%"
        assert format_percent(0.01) == "+0.01%"

    def test_format_negative_percent(self):
        """Should format negative percentages with - sign."""
        assert format_percent(-3.25) == "-3.25%"
        assert format_percent(-50.0) == "-50.00%"

    def test_format_zero_percent(self):
        """Should format zero correctly."""
        assert format_percent(0) == "+0.00%"

    def test_format_small_decimals(self):
        """Should handle small decimal values."""
        assert format_percent(0.001) == "+0.00%"
        assert format_percent(0.005) == "+0.01%"

    def test_format_large_percent(self):
        """Should handle large percentage values."""
        assert format_percent(1500.75) == "+1500.75%"
        assert format_percent(-999.99) == "-999.99%"
