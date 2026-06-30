"""Classify interview questions into categories without requiring an LLM call."""

from __future__ import annotations

import re
from typing import Tuple

# ---------- keyword maps ------------------------------------------------

_CATEGORY_PATTERNS: list[Tuple[str, list[str]]] = [
    # --- Data Engineering specifics (check before generic Python/Cloud) ---
    ("PySpark", [
        r"\bpyspark\b", r"\bspark\b", r"\brdd\b", r"\bdataframe\.rdd\b", r"\bbroadcast.?join\b",
        r"\bspark\.sql\b", r"\bsparkcontext\b", r"\bstreaming\b.*\bspark\b",
    ]),
    ("Databricks", [
        r"\bdatabricks\b", r"\bdelta\s?lake\b", r"\bdelta\s?table\b", r"\bdbfs\b",
        r"\bunity\s?catalog\b", r"\bworkspace\b.*\bdatabricks\b",
    ]),
    ("Microsoft Fabric", [
        r"\bfabric\b", r"\bonelake\b", r"\blakehouse\b.*\bfabric\b",
    ]),
    ("Azure", [
        r"\bazure\b", r"\badf\b", r"\bdata\s?factory\b", r"\bsynapse\b",
        r"\bblob\s?storage\b", r"\badls\b", r"\bazure\s?sql\b",
    ]),
    ("Snowflake", [
        r"\bsnowflake\b", r"\bsnowpipe\b", r"\btime\s?travel\b.*\bsnowflake\b",
        r"\bzero.?copy\s?clone\b",
    ]),
    ("Power BI", [
        r"\bpower\s?bi\b", r"\bdax\b", r"\bpbix\b", r"\breport\s?server\b",
        r"\bpowerbi\b",
    ]),
    ("DAX", [
        r"\bdax\b", r"\bcalculate\b.*\bfilter\b", r"\bmeasure\b.*\bpower\s?bi\b",
        r"\brelated\(", r"\bcalculated\s?column\b",
    ]),
    ("ETL", [
        r"\betl\b", r"\bextract.?transform.?load\b", r"\bpipeline\b.*\bdata\b",
        r"\bingestion\b", r"\borchestr\w+\b",
    ]),
    ("Data Warehousing", [
        r"\bdata\s?warehouse\b", r"\bdw\b", r"\bstar\s?schema\b", r"\bsnowflake\s?schema\b",
        r"\bfact\s?table\b", r"\bdimension\s?table\b", r"\bolap\b", r"\bslowly\s?changing\b",
    ]),
    ("Data Engineering", [
        r"\bdata\s?engineer\w*\b", r"\blakehouse\b", r"\bdata\s?lake\b",
        r"\bpartition\w*\b.*\bdata\b", r"\bincremental\s?load\b", r"\bwatermark\b.*\bdata\b",
    ]),
    # --- SQL ---
    ("SQL", [
        r"\bsql\b", r"\bselect\b.*\bfrom\b", r"\bjoin\b", r"\bwhere\b.*\bgroup\b",
        r"\bwindow\s?function\b", r"\bcte\b", r"\bstored\s?proc\w*\b",
        r"\bindex\w*\b.*\btable\b", r"\bquery\b.*\boptim\w+\b",
        r"\bgroup\s?by\b", r"\bhaving\b", r"\bsubquery\b",
    ]),
    # --- DSA ---
    ("DSA", [
        r"\barray\b", r"\blinked\s?list\b", r"\bbinary\s?search\b",
        r"\bdynamic\s?programming\b", r"\bdp\b", r"\btree\b.*\b(traversal|bfs|dfs)\b",
        r"\bgraph\b", r"\bheap\b", r"\btrie\b", r"\bstack\b.*\bqueue\b",
        r"\bsliding\s?window\b", r"\btwo\s?pointer\b", r"\bgreedy\b",
        r"\bbacktrack\w+\b", r"\bunion\s?find\b", r"\bbit\s?manipulation\b",
        r"\btime\s?complexity\b", r"\bspace\s?complexity\b", r"\bbig.?o\b",
    ]),
    # --- System Design ---
    ("System Design", [
        r"\bsystem\s?design\b", r"\bscalabil\w+\b", r"\bload\s?balanc\w+\b",
        r"\bcaching\b", r"\bmessage\s?queue\b", r"\bkafka\b", r"\bmicroservice\w*\b",
        r"\bapi\s?gateway\b", r"\bsharding\b", r"\bcap\s?theorem\b",
        r"\bhigh\s?availability\b", r"\bdistributed\b.*\bsystem\b",
    ]),
    # --- ML / Stats ---
    ("Machine Learning", [
        r"\bmachine\s?learning\b", r"\bneural\s?network\b", r"\bdeep\s?learning\b",
        r"\bregression\b", r"\bclassification\b", r"\bcluster\w+\b",
        r"\btrain\b.*\bmodel\b", r"\bfeature\b.*\bengineering\b", r"\boverfitting\b",
    ]),
    ("Statistics", [
        r"\bstatistic\b", r"\bp.?value\b", r"\bconfidence\s?interval\b",
        r"\bhypothesis\b", r"\bnormal\s?distribut\w+\b", r"\bvariance\b",
        r"\bcorrelation\b",
    ]),
    # --- Cloud (generic) ---
    ("Cloud", [
        r"\baws\b", r"\bgcp\b", r"\bgoogle\s?cloud\b", r"\biam\b",
        r"\bs3\b", r"\bec2\b", r"\blambda\b.*\bfunction\b",
    ]),
    # --- Coding (Python / Java / JS, etc.) ---
    ("Python", [
        r"\bpython\b", r"\bpandas\b", r"\bnumpy\b", r"\blist\s?comprehension\b",
        r"\bdecorator\b", r"\bgenerator\b", r"\basync\b.*\bpython\b",
        r"\bgil\b",
    ]),
    ("Coding", [
        r"\bcode\b", r"\bprogram\w+\b", r"\bfunction\b", r"\balgorithm\b",
        r"\bimplement\b", r"\bwrite\s+a\b", r"\bjava\b", r"\bjavascript\b",
        r"\bc\+\+\b", r"\brust\b", r"\bgolang\b",
    ]),
    # --- APIs ---
    ("APIs", [
        r"\brest\s?api\b", r"\bgraphql\b", r"\bwebhook\b", r"\bhttp\s?method\b",
        r"\bget\b.*\bpost\b.*\bput\b", r"\bapi\s?design\b",
    ]),
    # --- Business Intelligence ---
    ("Business Intelligence", [
        r"\bbusiness\s?intelligence\b", r"\bkpi\b", r"\bdashboard\b", r"\breport\w+\b",
        r"\bdata\s?visualiz\w+\b",
    ]),
    # --- Behavioral ---
    ("Behavioral", [
        r"\btell\s+me\s+about\s+(yourself|a\s+time)\b",
        r"\bstrength\b.*\bweakness\b", r"\bstar\s?method\b",
        r"\bchallenge\b.*\bwork\b", r"\bconflict\b.*\bteam\b",
        r"\bpride\b.*\bproject\b",
    ]),
    # --- HR ---
    ("HR", [
        r"\bsalar\w+\b", r"\bnotice\s?period\b", r"\brelocation\b",
        r"\bbenefits\b", r"\bcurrent\s+(ctc|comp)\b", r"\bexpected\s+(ctc|salary)\b",
        r"\bwhy\s+(do\s+you\s+want|are\s+you\s+leaving)\b",
    ]),
]

_COMPILED = [
    (cat, [re.compile(p, re.IGNORECASE) for p in patterns])
    for cat, patterns in _CATEGORY_PATTERNS
]


def detect_category(text: str) -> str:
    """Return the most likely category for a given question string."""
    scores: dict[str, int] = {}
    for cat, patterns in _COMPILED:
        hits = sum(1 for p in patterns if p.search(text))
        if hits:
            scores[cat] = hits

    if not scores:
        return "General"

    return max(scores, key=lambda c: scores[c])
