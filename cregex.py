LETTER       = r"[a-zA-Z]"
DIGIT        = r"[0-9]"
LETTER_DIGIT = r"[a-zA-Z-0-9]"
HEX_DIGIT    = r"[a-fA-F-0-9]"
E            = f"""[Ee][+-]?{DIGIT}+"""
FLOAT_SUFFIX = r"[fFlL]"
INT_SUFFIX   = r"[uUlL]"

COMMENT_RE = r'\/\*[\s\S]*?\*\/+|//.*'