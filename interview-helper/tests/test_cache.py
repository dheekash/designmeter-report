"""Unit tests for response cache."""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.utils.cache import ResponseCache


def test_set_and_get():
    c = ResponseCache(max_size=10)
    c.set("what is sql", "SQL", "openai", {"answer": "structured query language"})
    result = c.get("what is sql", "SQL", "openai")
    assert result is not None
    assert result["answer"] == "structured query language"

def test_miss():
    c = ResponseCache(max_size=10)
    assert c.get("nothing", "SQL", "openai") is None

def test_eviction():
    c = ResponseCache(max_size=3)
    for i in range(5):
        c.set(f"q{i}", "General", "openai", {"answer": f"a{i}"})
    assert len(c) <= 3

def test_clear():
    c = ResponseCache(max_size=10)
    c.set("q", "SQL", "openai", {"answer": "a"})
    c.clear()
    assert len(c) == 0


if __name__ == "__main__":
    for name, fn in [(k, v) for k, v in globals().items() if k.startswith("test_")]:
        try:
            fn()
            print(f"  ✅ {name}")
        except Exception as e:
            print(f"  ❌ {name}: {e}")
