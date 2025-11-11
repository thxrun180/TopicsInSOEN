from typing import List, Dict

# Format per line:
# LEVEL | 2025-10-11T12:34:56 | message | tags=a,b
def read_log_file(path: str) -> List[Dict]:
    entries = []
    with open(path, "r", encoding="utf-8") as f:
        for raw in f:
            raw = raw.strip()
            if not raw or raw.startswith("#"):
                continue
            parts = [p.strip() for p in raw.split("|")]
            if len(parts) < 3:
                continue
            level, ts, msg = parts[0], parts[1], parts[2]
            tags = []
            if len(parts) >= 4 and parts[3].startswith("tags="):
                tags = [t.strip() for t in parts[3][5:].split(",") if t.strip()]
            entries.append({"level": level, "ts": ts, "msg": msg, "tags": tags})
    return entries
