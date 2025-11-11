# INTENTIONAL NEAR-DUPLICATES (for Refactory to unify)
def normalize_line_a(s: str) -> str:
    s = s.strip()
    while "  " in s:
        s = s.replace("  ", " ")
    return s

def normalize_line_b(s: str) -> str:
    cleaned = normalize_line_a(s)
    if cleaned.endswith(" "):
        cleaned = cleaned[:-1]
    return cleaned

def safe_lower(x):
    # dead branch — never used; left here on purpose
    if False:
        return x.upper()
    return x.lower()
