from cregex import *
import ply.lex as lex

class C99Lexer(object):
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
                    "inline" : "INLINE",
                    "long" : "LONG",
                    "register" : "REGISTER",
                    "restrict" : "RESTRICT",
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
                    "while" : "WHILE",
                    "_Bool": "BOOLEAN",
                    "_Complex": "COMPLEX",
                    "_Imaginary": "IMAGINARY",
            }

    # This class attribute should be set because ply
    # is using Python introspection for its internal
    # working.
    tokens = list(reserved.values()) + \
            [
                "TYPEDEF_NAME",
                
                "IDENTIFIER",
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
    t_ignore = ' \t'
    
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
        self._lexer           = lex.lex(module = self, **kwargs)
        self._symbol_table    = {}
        self._tag_table       = {}
        self._user_type_table = {}

    def add_tag(self, tag, obj):
        """
        Adds a tag.
        
        :param      tag:  The tag
        :type       tag:  { type_description }
        :param      obj:  The object
        :type       obj:  { type_description }
        """
        if tag not in self._tag_table:
            self._tag_table[tag] = obj
            return True
        else:
            return False

    def tag_exist(self, tag):
        return tag in self._tag_table

    def get_tag(self, tag):
        return self._tag_table[tag]

    def add_symbol(self, symbol, value):
        """
        Adds a symbol to the internal symbol table
        to follow redefinition.
        
        :param      symbol:  The symbol
        :type       symbol:  { type_description }
        :param      value:   The value
        :type       value:   { type_description }
        """
        # We need to value because lexer will first see a symbol as identifier so in case we list enumerators
        # to avoid raising exception because of enumerator redefinition we do this check.
        if (symbol not in self._symbol_table):
            self._symbol_table[symbol] = value
            return True
        else:
            return False

    def add_type(self, name, value):
        """
        Adds a type.
        
        :param      name:  The name
        :type       name:  { type_description }
        """
        if (name not in self._user_type_table):
            self._user_type_table[name] = value
            return True
        else:
            return False

    def t_IDENTIFIER(self, t):
        r'[a-zA-Z_][a-zA-Z_0-9]*'

        # Check first if identifier is a reserved word
        if t.value in self.reserved:
            t.type = self.reserved[t.value] 
        else:
            if t.value in self._user_type_table:
                t.type = "TYPEDEF_NAME"

        return t

    def t_STRING_LITERAL(self, t):
        r'L?"(\\.|[^\\\"])*"'
        return t

    FLOAT_RE = fr'({DIGIT}+{E}|{DIGIT}*\.{DIGIT}+({E})?|{DIGIT}+\.{DIGIT}*({E})?)(?P<float_suffix>{FLOAT_SUFFIX})?'
    @lex.TOKEN(FLOAT_RE)
    def t_FLOAT(self, t):
        # Float values are constant but defined as a single rule
        # to allow easier conversion from Python str to float.
        
        # TODO: Handle suffix
        # PLY mix all token regexes into a single big regex with captured group
        # so we can't rely on group position. So we are defining named group to ease
        # trimming of suffixes.
        # 
        # We are testing all named suffixes for float because Python doesn't allow reuse
        # of same name.
        suffix = t.lexer.lexmatch.group('float_suffix')
        t.value = float(t.value.rstrip(suffix))
        t.type  = "CONSTANT"
        return t    
    
    HEX_RE = fr'0[xX]{HEX_DIGIT}+(?P<hex_suffix>{INT_SUFFIX})?'
    @lex.TOKEN(HEX_RE)
    def t_HEX(self, t):
        # Hex values are constant but defined as a single rule
        # to allow easier conversion from Python str to hex.
        
        # TODO: Handle suffix
        # PLY mix all token regexes into a single big regex with captured group
        # so we can't rely on group position. So we are defining named group to ease
        # trimming of suffixes.
        suffix = t.lexer.lexmatch.group('hex_suffix')
        t.value = int(t.value.rstrip(suffix), base = 16)
        t.type = "CONSTANT"
        return t

    # DIGIT is not limited to [0-7] to avoid ambiguity between integer base 8 or 10.
    OCT_RE = fr'0{DIGIT}+(?P<oct_suffix>{INT_SUFFIX})?'
    @lex.TOKEN(OCT_RE)
    def t_OCTAL(self, t):
        # Octal values are constant but defined as a single rule
        # to allow easier conversion from Python str to octal.
        
        # TODO: Handle suffix
        # PLY mix all token regexes into a single big regex with captured group
        # so we can't rely on group position. So we are defining named group to ease
        # trimming of suffixes.
        suffix = t.lexer.lexmatch.group('oct_suffix')

        t.value = int(t.value.rstrip(suffix), base = 8)
        t.type = "CONSTANT"
        return t

    INTEGER_RE = fr'{DIGIT}+(?P<int_suffix>{INT_SUFFIX})?'
    @lex.TOKEN(INTEGER_RE)
    def t_INTEGER(self, t):
        # Integer values are constant but defined as a single rule
        # to allow easier conversion from Python str to int. 

        # TODO: Handle suffix
        # PLY mix all token regexes into a single big regex with captured group
        # so we can't rely on group position. So we are defining named group to ease
        # trimming of suffixes.
        suffix = t.lexer.lexmatch.group('int_suffix')
        t.value = int(t.value.rstrip(suffix))
        t.type = "CONSTANT"
        return t

    def t_LITERAL(self, t):
        # Literal values are constant but defined as a single rule
        # to allow easier conversion from Python str to char.
        r'L?\'(\\.|[^\'])+\''
        t.value = ord(t.value)
        t.type = "CONSTANT"
        return t

    @lex.TOKEN(COMMENT_RE)
    def t_COMMENT(self, t):
        # Comments should be stored into a data structure based on header files and then restored during code generation
        pass

    # Define a rule so we can track line numbers
    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)

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
    lexer = C99Lexer()

    with open("output/directive.i", "rt") as file:
        data = file.read()

    token_list = lexer.tokenize(data)
    print(token_list)