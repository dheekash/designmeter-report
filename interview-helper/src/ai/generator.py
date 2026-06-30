"""Answer generation — orchestrates provider + prompt assembly."""

from __future__ import annotations

from typing import Callable, Generator, Optional

from .base import AIProvider
from .detector import detect_category
from ..utils.logger import get_logger

log = get_logger("ai.generator")

# ---------- system prompt -------------------------------------------

_SYSTEM_BASE = """You are an elite interview coach and senior technical expert with 15+ years of experience
in data engineering, software development, and system design. Your role is to help candidates excel in
technical interviews by providing clear, accurate, production-quality answers.

When answering:
- Be concise for the short answer (20-30 second verbal delivery)
- Provide depth in the detailed section
- Include real-world context and examples
- Show best practices and common pitfalls
- Format code with proper syntax
- Be interview-ready: structured, confident, and professional
"""

_CATEGORY_ADDONS: dict[str, str] = {
    "SQL": "Focus on query correctness, optimization, and execution plan awareness.",
    "PySpark": "Emphasize distributed computing concepts, optimizations, and production patterns.",
    "DSA": "Provide brute-force → optimal progression, complexity analysis, and edge cases.",
    "System Design": "Use structured approach: requirements → capacity → components → trade-offs.",
    "Behavioral": "Use the STAR method (Situation, Task, Action, Result) with specific examples.",
    "Coding": "Prioritize correctness, readability, then optimization. Explain your reasoning.",
    "Data Engineering": "Cover architecture, scalability, reliability, and production considerations.",
    "Machine Learning": "Cover theory, practical implementation, and real-world trade-offs.",
    "HR": "Be professional, honest, and positive. Focus on value alignment.",
}

# ---------- prompt templates ----------------------------------------

_CODING_TEMPLATE = """
Question: {question}

Provide a complete response with these sections:

## 🎯 Problem Summary
(1-2 sentences)

## 🤔 Clarifying Questions
(2-3 good questions to ask the interviewer)

## 💡 Approach
(Brute force → Better → Optimal)

## ✅ Solution
```{lang}
{code_placeholder}
```

## 📊 Complexity Analysis
- **Time:** O(?)
- **Space:** O(?)

## 🧪 Dry Run
(Walk through with an example)

## ⚠️ Edge Cases
- ...

## 🧪 Test Cases
```python
# test cases
```

## 💬 How to Explain in Interview
(2-3 sentences spoken explanation)

## ❓ Possible Follow-up Questions
- ...
"""

_GENERAL_TEMPLATE = """
Question: {question}
Category: {category}

Provide a complete interview response with these sections:

## ⚡ Short Answer (20-30 seconds)
(What you'd say verbally in 20-30 seconds)

## 📖 Detailed Explanation
(Thorough explanation with depth)

## 💻 Code / Example
```
(relevant code, query, or concrete example)
```

## 🌍 Real-World Example
(Where you'd use this in production)

## ✅ Best Practices
- ...

## ❌ Common Mistakes
- ...

## ⚙️ Performance Considerations
- ...

## 🔄 Alternative Approaches
- ...

## ❓ Common Follow-up Questions
1. ...
2. ...
3. ...
"""

_CODING_CATEGORIES = {"DSA", "Coding", "SQL", "Python", "PySpark"}


def _build_prompt(question: str, category: str) -> tuple[str, str]:
    addon = _CATEGORY_ADDONS.get(category, "")
    system = _SYSTEM_BASE + (f"\n\nSpecial focus: {addon}" if addon else "")

    if category in _CODING_CATEGORIES:
        lang_map = {
            "SQL": "sql", "Python": "python", "PySpark": "python",
            "Coding": "python", "DSA": "python",
        }
        lang = lang_map.get(category, "python")
        user = _CODING_TEMPLATE.format(
            question=question, lang=lang, code_placeholder="# write your solution here"
        )
    else:
        user = _GENERAL_TEMPLATE.format(question=question, category=category)

    return system, user


# ---------- public API -----------------------------------------------

class AnswerGenerator:
    def __init__(self, provider: AIProvider, resume_text: Optional[str] = None):
        self._provider = provider
        self._resume_text = resume_text

    def generate(
        self, question: str, on_chunk: Optional[Callable[[str], None]] = None
    ) -> dict:
        """Generate an answer and return a result dict.

        Args:
            question: The interview question text.
            on_chunk: Optional callback for streaming — called with each text chunk.

        Returns:
            {question, category, answer, provider}
        """
        category = detect_category(question)
        system, user = _build_prompt(question, category)

        if self._resume_text:
            system += f"\n\nCandidate resume context:\n{self._resume_text[:2000]}"

        log.info("Generating answer [%s] via %s", category, self._provider.name)

        if on_chunk:
            chunks: list[str] = []
            try:
                for chunk in self._provider.stream(system, user, max_tokens=3000):
                    chunks.append(chunk)
                    on_chunk(chunk)
                answer = "".join(chunks)
            except Exception as e:
                log.error("Streaming failed: %s — falling back to blocking", e)
                answer = self._provider.complete(system, user, max_tokens=3000)
                on_chunk(answer)
        else:
            answer = self._provider.complete(system, user, max_tokens=3000)

        return {
            "question": question,
            "category": category,
            "answer": answer,
            "provider": self._provider.name,
        }
