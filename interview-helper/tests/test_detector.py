"""Unit tests for question category detection."""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.ai.detector import detect_category


def test_sql():
    assert detect_category("What is the difference between INNER JOIN and LEFT JOIN?") == "SQL"

def test_dsa():
    assert detect_category("Explain dynamic programming with an example") == "DSA"

def test_pyspark():
    assert detect_category("How do you handle skewed data in PySpark joins?") == "PySpark"

def test_system_design():
    assert detect_category("How would you design a scalable microservices architecture?") == "System Design"

def test_behavioral():
    assert detect_category("Tell me about a time you had a conflict with a team member") == "Behavioral"

def test_python():
    assert detect_category("What is a Python decorator and when would you use one?") == "Python"

def test_snowflake():
    assert detect_category("What is Time Travel in Snowflake and how does it work?") == "Snowflake"

def test_azure():
    assert detect_category("Explain Azure Data Factory and its key components") == "Azure"

def test_general_fallback():
    cat = detect_category("Hello")
    assert cat == "General"


if __name__ == "__main__":
    tests = [v for k, v in list(globals().items()) if k.startswith("test_")]
    passed = 0
    for t in tests:
        try:
            t()
            print(f"  ✅ {t.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"  ❌ {t.__name__}: {e}")
    print(f"\n{passed}/{len(tests)} tests passed")
