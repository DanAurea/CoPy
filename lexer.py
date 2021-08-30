import ply.lex as lex

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
    tokens = list(reserved.values()) + \
            [
                "COMMENT",

                "PREPROC_DIRECTIVE",

                "IDENTIFIER",
                "TYPE_NAME",
                "CONSTANT",
                "STRING_LITERAL",

                # Operators
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
            ]

    literals = [ ';', '{', '}', ',', ':', '=', '(', ')', '[', ']', '.', '&', 
                 '!', '~', '-', '+', '*', '/', '%', '<', '>', '^', '|', '?']

    # Skip whitespaces
    t_ignore = ' \t\n'
    
    # Operators
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

    def __init__(self, **kwargs):
        self._lexer = lex.lex(module = self, **kwargs)

    PREPROC_DIRECTIVE = r"|".join([r'\#' + directive for directive in [
                                                                            'include',
                                                                            'define',
                                                                            'pragma',
                                                                        ]
                                    ])

    @lex.TOKEN(PREPROC_DIRECTIVE)
    def t_PREPROC_DIRECTIVE(self, t):
        return t

    def t_IDENTIFIER(self, t):
        r'[a-zA-Z_][a-zA-Z_0-9]*'
        t.type = self.reserved.get(t.value, 'IDENTIFIER')    # Check for reserved words
        return t
    
    def t_STRING_LITERAL(self, t):
        r'L?"(\\.|[^\\\"])*"'
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

    def tokenize(self, data):
        """
        Parse data and returns a token list.
        """
        token_list = []

        self._lexer.input(data)

        while True:
            tok = self._lexer.token()
            
            if not tok:
                break

            token_list.append(tok)

        return token_list

if __name__ == "__main__":
    lexer = CLexer()

    with open("examples/example.h", "rt") as file:
        data = file.read()

    token_list = lexer.tokenize(data)
    print(token_list)