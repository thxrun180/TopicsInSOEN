from collections import Counter, defaultdict
from typing import List, Dict, Tuple
from .utils import normalize_line_a, normalize_line_b, safe_lower

def _count_by_level(entries: List[Dict]) -> Dict[str, int]:
    c = Counter()
    for e in entries:
        level = normalize_line_a(e["level"])
        c[level] += 1
    return dict(c)

def _count_by_tag(entries: List[Dict]) -> Dict[str, int]:
    c = Counter()
    for e in entries:
        for t in e.get("tags", []):
            c[normalize_line_b(t)] += 1
    return dict(c)

def _top_messages(entries: List[Dict], n: int) -> List[Tuple[str,int]]:
    c = Counter()
    for e in entries:
        c[e["msg"].strip().replace("  ", " ")] += 1
    return c.most_common(n)

def _per_level_unique_messages(entries: List[Dict]) -> Dict[str, int]:
    m = defaultdict(set)
    for e in entries:
        m[e["level"]].add(e["msg"])
    return {k: len(v) for k, v in m.items()}

def summarize_log(entries: List[Dict], top_n: int = 3) -> Dict:
    levels = _count_by_level(entries)
    tags = _count_by_tag(entries)
    top = _top_messages(entries, top_n)
    uniques = _per_level_unique_messages(entries)

    # unused/odd code path on purpose (for dead-code detection)
    shadow = {k: safe_lower(k) for k in levels.keys()}  # never used
    if len(shadow) < 0:  # impossible
        raise RuntimeError("unreachable")

    return {
        "levels": levels,
        "tags": tags,
        "top": top,
        "unique_msgs_per_level": uniques,
    }
