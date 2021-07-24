import enum

class SimplestRe(enum.Enum):
    """
    Enumeration of all simplest regexp that could be used
    for lexem pattern.
    """

    LETTER = "[a-zA-Z]"
    DIGIT = "[0-9]"
    LETTER_DIGIT = "[a-zA-Z-0-9]"
    E = f"""[Ee][+-]?{DIGIT}+"""
    FLOAT_SUFFIX = "(f|F|l|L)"
    INT_SUFFIX = "(u|U|l|L)*"

class CToken(enum.Enum):
    """
    Enumeration of grammar rules respectively to ANSI C.

    Ref. https://www.lysator.liu.se/c/ANSI-C-grammar-y.html
    """
    COMMENT = "\/\*[\s\S]*?\*\/+|\/\/.*$"

    # Keywords
    AUTO = "auto"
    BREAK = "break"
    CASE = "case"
    CHAR = "char"
    CONST = "const"
    CONTINUE = "continue"
    DEFAULT = "default"
    DO = "do"
    DOUBLE = "double"
    ELSE = "else"
    ENUM = "enum"
    EXTERN = "extern"
    FLOAT = "float"
    FOR = "for"
    GOTO = "goto"
    IF = "if"
    INT = "int"
    LONG = "long"
    REGISTER = "register"
    RETURN = "return"
    SHORT = "short"
    SIGNED = "signed"
    SIZEOF = "sizeof"
    STATIC = "static"
    STRUCT = "struct"
    SWITCH = "switch"
    TYPEDEF = "typedef"
    UNION = "union"
    UNSIGNED = "unsigned"
    VOID = "void"
    VOLATILE = "volatile"
    WHILE = "while"

    # Identifiers
    TYPE = f"""{SimplestRe.LETTER}({SimplestRe.LETTER}|{SimplestRe.DIGIT}*)"""
    STRING_LITTERAL = "L?\"(\\.|[^\\\"])*\""    

    # Operators
    ELLIPSIS = "..."
    RIGHT_ASSIGN = ">>="
    LEFT_ASSIGN = "<<="
    ADD_ASSIGN = "\+="
    SUB_ASSIGN = "\-="
    MUL_ASSIGN = "\*="
    DIV_ASSIGN = "/="
    MOD_ASSIGN = "%="
    AND_ASSIGN = "&="
    XOR_ASSIGN = "\^="
    OR_ASSIGN = "\|="
    RIGHT_OP = ">>"
    LEFT_OP = "<<"
    INC_OP = "\+\+"
    DEC_OP = "\-\-"
    PTR_OP = "\->"
    AND_OP = "&&"
    OR_OP = "\|\|"
    LE_OP = "<="
    GE_OP = ">="
    EQ_OP = "=="
    NE_OP = "!="
    SEMI_COLON = ";"
    L_BRACE = "{"
    R_BRACE = "}"
    COMMA = ","
    COLON = ":"
    ASSIGN = "="
    L_PAREN = "\("
    R_PAREN = "\)"
    L_BRACKET = "\["
    R_BRACKET = "\]"
    DOT = "\."
    AND = "&"
    NEG = "\!"
    NOT = "~"
    SUB = "\-"
    ADD = "\+"
    MUL = "\*"
    DIV = "\/"
    MOD = "%"
    LESS_THAN = "<"
    GREATER_THAN = ">"
    XOR = "\^"
    OR = "\|"
    TERNARY_OP = "\?"

    WHITESPACES = "[ \t\v\n\f]"

# Small hack to add properly constant rules as one single rule into grammar.

_CONSTANT_RE_LIST = "|".join([
                                    f"""0[xX]{SimplestRe.LETTER_DIGIT.value}+{SimplestRe.INT_SUFFIX.value}?""",
                                    f"""0{SimplestRe.DIGIT.value}+{SimplestRe.INT_SUFFIX.value}?""",
                                    f"""{SimplestRe.DIGIT.value}+{SimplestRe.INT_SUFFIX.value}?""",
                                    f"""L?'(\\.|[^\\'])+'""",
                                    f"""{SimplestRe.DIGIT.value}+{SimplestRe.E.value}{SimplestRe.FLOAT_SUFFIX.value}?""",
                                    f"""{SimplestRe.DIGIT.value}*\.{SimplestRe.DIGIT.value}+({SimplestRe.E.value})?{SimplestRe.FLOAT_SUFFIX.value}?""",
                                    f"""{SimplestRe.DIGIT.value}+\.{SimplestRe.DIGIT.value}*({SimplestRe.E.value})?{SimplestRe.FLOAT_SUFFIX.value}?""",
                                ])

__TOKEN_DICT__ = dict([(t.name, t.value) for t in CToken] + [("CONSTANT", _CONSTANT_RE_LIST)])

Token = enum.Enum("Token", __TOKEN_DICT__)

class Grammar(object):
    pass