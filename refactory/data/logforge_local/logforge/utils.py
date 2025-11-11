# INTENTIONAL NEAR-DUPLICATES (for Refactory to unify)
def normalize_line_a(s: str) -> str:
    s = s.strip()
    while "  " in s:
        s = s.replace("  ", " ")
    return s

def normalize_line_b(s: str) -> str:
    s = s.strip()
    while "  " in s:
        s = s.replace("  ", " ")
    if s.endswith(" "):
        s = s[:-1]
    return s

def safe_lower(x):
    # dead branch — never used; left here on purpose
    if False:
        return x.upper()
    return x.lower()
