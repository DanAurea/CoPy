import ply.lex as lex
import re
import grammar

LETTER = r"[a-zA-Z]"
DIGIT = r"[0-9]"
LETTER_DIGIT = r"[a-zA-Z-0-9]"
E = f"""[Ee][+-]?{DIGIT}+"""
FLOAT_SUFFIX = r"[fF]"
INT_SUFFIX = r"[uU]"

class CLexer(object):
    """
    Produce a token list from a C source code.
    """

    # Keywords
    reserved = {
                 "auto" : "AUTO",
                 "break" : "BREAK",
                 "case" : "CASE",
                 "char" : "CHAR",
                 "const" : "CONST",
                 "continue" : "CONTINUE",
                 "default" : "DEFAULT",
                 "do" : "DO",
                 "double" : "DOUBLE",
                 "else" : "ELSE",
                 "enum" : "ENUM",
                 "extern" : "EXTERN",
                 "float" : "FLOAT",
                 "for" : "FOR",
                 "goto" : "GOTO",
                 "if" : "IF",
                 "int" : "INT",
                 "long" : "LONG",
                 "register" : "REGISTER",
                 "return" : "RETURN",
                 "short" : "SHORT",
                 "signed" : "SIGNED",
                 "sizeof" : "SIZEOF",
                 "static" : "STATIC",
                 "struct" : "STRUCT",
                 "switch" : "SWITCH",
                 "typedef" : "TYPEDEF",
                 "union" : "UNION",
                 "unsigned" : "UNSIGNED",
                 "void" : "VOID",
                 "volatile" : "VOLATILE",
                 "while" : "WHILE"
            }

    # This class attribute should be set because ply
    # is using Python introspection for its internal
    # working.
    tokens = [
                "COMMENT",

                "PREPROC_DIRECTIVE",

                "IDENTIFIER",
                "CONSTANT",
                "STRING_LITERAL",

                # Operators
                "PLUS",
                "MINUS",
                "TIMES",
                "DIVIDE",
                "LPAREN",
                "RPAREN",
                "LBRACE",
                "RBRACE",
                "LBRACKET",
                "RBRACKET",
                "ELLIPSIS",
                "LEFT_ASSIGN",
                "RIGHT_ASSIGN",
                "ADD_ASSIGN",
                "SUB_ASSIGN",
                "MUL_ASSIGN",
                "DIV_ASSIGN",
                "MOD_ASSIGN",
                "AND_ASSIGN",
                "XOR_ASSIGN",
                "OR_ASSIGN",
                "LEFT_OP",
                "RIGHT_OP",
                "INC_OP",
                "DEC_OP",
                "PTR_OP",
                "AND_OP",
                "OR_OP",
                "LE_OP",
                "GE_OP",
                "EQ_OP",
                "NE_OP",
                "SEMI_COLON",
                "COMMA",
                "COLON",
                "ASSIGN",
                "DOT",
                "AND",
                "NEG",
                "NOT",
                "ADD",
                "SUB",
                "MUL",
                "DIV",
                "MOD",
                "GREATER_THAN",
                "LESS_THAN",
                "XOR",
                "OR",
                "TERNARY_OP",
            ] + list(reserved.values())

    # Skip whitespaces
    t_ignore = ' \t\n'
    
    # Operators
    t_LPAREN = r'\('
    t_RPAREN = r'\)'
    t_LBRACE = r'{'
    t_RBRACE = r'}'
    t_LBRACKET = r'\['
    t_RBRACKET = r'\]'
    t_ELLIPSIS = r'\.\.\.'
    t_LEFT_ASSIGN = r'<<='
    t_RIGHT_ASSIGN = r'>>='
    t_ADD_ASSIGN = r'\+='
    t_SUB_ASSIGN = r'-='
    t_MUL_ASSIGN = r'\*='
    t_DIV_ASSIGN = r'/='
    t_MOD_ASSIGN = r'%='
    t_AND_ASSIGN = r'&='
    t_XOR_ASSIGN = r'\^='
    t_OR_ASSIGN = r'\|='
    t_RIGHT_OP = r'>>'
    t_LEFT_OP = r'<<'
    t_INC_OP = r'\+\+'
    t_DEC_OP = r'\-\-'
    t_PTR_OP = r'\->'
    t_AND_OP = r'&&'
    t_OR_OP = r'\|\|'
    t_LE_OP = r'<='
    t_GE_OP = r'>='
    t_EQ_OP = r'=='
    t_NE_OP = r'!='
    t_SEMI_COLON = r';'
    t_COMMA = r','
    t_COLON = r':'
    t_ASSIGN = r'='
    t_DOT = r'\.'
    t_AND = r'&'
    t_NEG = r'\!'
    t_NOT = r'~'
    t_SUB = r'\-'
    t_ADD = r'\+'
    t_MUL = r'\*'
    t_DIV = r'\/'
    t_MOD = r'%'
    t_LESS_THAN = r'<'
    t_GREATER_THAN = r'>'
    t_XOR = r'\^'
    t_OR = r'\|'
    t_TERNARY_OP = r'\?'

    def __init__(self, **kwargs):
        self.lexer = lex.lex(module = self, **kwargs)

    PREPROC_DIRECTIVE = "|".join(['\#' + directive for directive in [
                                                        "include",
                                                        "define",
                                                        "pragma",
                                                    ]
                                    ])

    @lex.TOKEN(PREPROC_DIRECTIVE)
    def t_PREPROC_DIRECTIVE(self, t):
        return t

    def t_STRING_LITERAL(self, t):
        r'L?"(\\.|[^\\\"])*"'
        return t

    def t_IDENTIFIER(self, t):
        r'[a-zA-Z_][a-zA-Z_0-9]*'
        t.type = self.reserved.get(t.value, 'IDENTIFIER')    # Check for reserved words
        return t

    CONSTANT_RE = "|".join([
                                f"""{DIGIT}+{E}{FLOAT_SUFFIX}?""",
                                f"""{DIGIT}*\.{DIGIT}+({E})?{FLOAT_SUFFIX}?""",
                                f"""{DIGIT}+\.{DIGIT}*({E})?{FLOAT_SUFFIX}?""",
                                f"""0[xX]{LETTER_DIGIT}+{INT_SUFFIX}?""",
                                f"""0{DIGIT}+{INT_SUFFIX}?""",
                                f"""{DIGIT}+{INT_SUFFIX}?""",
                                f"""L?'(\\.|[^\\'])+'""",
                            ])
    
    @lex.TOKEN(CONSTANT_RE)
    def t_CONSTANT(self, t):
        # Data types are not handled because Python
        # doesn't embed a way to differentiate
        # signed and unsigned, this can be done on
        # post process with intermediate code generation.
        return t

    def t_COMMENT(self, t):
        r'\/\*[\s\S]*?\*\/+|//.*'
        pass

    # Error handling when an incorrect character is
    # being processed by the lexer.
    def t_error(self, t):
        print("Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)

    def parse(self, data):
        """
        Parse data and returns a token list.
        """
        token_list = []

        self.lexer.input(data)

        while True:
            tok = self.lexer.token()
            
            if not tok:
                break

            token_list.append(tok)

        return token_list

if __name__ == "__main__":
    lexer = CLexer()

    with open("examples/example.c", "rt") as file:
        data = file.read()

    token_list = lexer.parse(data)