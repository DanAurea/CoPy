from pathlib import Path
from utils import debug_production

import ply.lex as lex
import ply.yacc as yacc

LETTER = r"[a-zA-Z]"
DIGIT = r"[0-9]"
LETTER_DIGIT = r"[a-zA-Z-0-9]"
E = f"""[Ee][+-]?{DIGIT}+"""
FLOAT_SUFFIX = r"[fF]"
INT_SUFFIX = r"[uU]"

class C99PreProcessorLexer(object):
    """
    C99 Preprocessor lexer.
    """

    # Keywords
    reserved = {
                    "define" : "DEFINE",
                    "defined" : "DEFINED",
                    "elif" : "ELIF",
                    "else" : "ELSE",
                    "endif" : "ENDIF",
                    "error" : "ERROR",
                    "if" : "IF",
                    "ifdef" : "IFDEF",
                    "ifndef" : "IFNDEF",
                    "include" : "INCLUDE",
                    "line" : "LINE",
                    "pragma" : "PRAGMA",
                    "undef" : "UNDEF",
                    "__DATE__" : "CURRENT_DATE",
                    "__FILE__" : "FILENAME",
                    "__LINE__" : "CURRENT_LINE",
                    "__TIME__" : "TIME",
            }

    # This class attribute should be set because ply
    # is using Python introspection for its internal
    # working.
    tokens = list(reserved.values()) + \
            [
                "CONSTANT",
                "HEADER_NAME",
                "IDENTIFIER",
                "STRING_LITERAL",

                "MACRO_NAME",

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
                "NE_OP"
            ]

    literals = [ ';', '{', '}', ',', ':', '=', '(', ')', '[', ']', '.', '&', '!',
                 '~', '-', '+', '*', '/', '%', '<', '>', '^', '|', '?', '"', '\\',
                 '@', '#']

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
        self._lexer        = lex.lex(module = self, **kwargs)
        self._symbol_table = {}

    # Define a rule so we can track line numbers
    def t_NEWLINE(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    HEADER_NAME_RE = "|".join([
                                f"""<[^<>]+>""",
                                f"""\"[^\"]+\" """,
                            ])
    
    @lex.TOKEN(HEADER_NAME_RE)
    def t_HEADER_NAME(self, t):
        return t

    def t_IDENTIFIER(self, t):
        r'[a-zA-Z_][a-zA-Z_0-9]*'

        # Check first if identifier is a reserved word
        if t.value in self.reserved:
            t.type = self.reserved[t.value] 
        else:
            if t.value not in self._symbol_table:
                self._symbol_table[t.value] = {"type": "IDENTIFIER", "value": None}

            t.type = self._symbol_table[t.value]["type"]
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

class C99PreProcessorParser(object):

    def __init__(self, debug = False, **kwargs):
        self._lexer = C99PreProcessorLexer()

        self.tokens  = self._lexer.tokens
        self._parser = yacc.yacc(module = self, debug = debug, **kwargs)
        self._debug  = debug

    @debug_production
    def p_macro(self, p):
        '''
        macro : '#' directive
                | '#' directive macro 
        '''
        pass

    @debug_production
    def p_directive(self, p):
        '''
        directive :  define_directive
                   | include_directive
                   | pragma_directive
        '''
        pass
    
    @debug_production
    def p_define_directive(self, p):
        '''
        define_directive :  DEFINE IDENTIFIER token_list
                   | DEFINE '(' identifier_list ')' token_list
        '''
        pass

    @debug_production
    def p_include_directive(self, p):
        '''
        include_directive : INCLUDE HEADER_NAME
        '''
        pass

    @debug_production
    def p_pragma_directive(self, p):
        '''
        pragma_directive : PRAGMA token_list
        '''
        pass

    @debug_production
    def p_identifier_list(self, p):
        '''
        identifier_list : IDENTIFIER
                        | identifier_list ',' IDENTIFIER
        '''
        pass

    @debug_production
    def p_token_list(self, p):
        '''
        token_list : token
                    | token_list token
        '''
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            # TODO : Produce a string instead of a list would be easier for text replacement
            p[1].append(p[2])
            p[0] = p[1]

    @debug_production
    def p_token(self, p):
        '''
        token :     IDENTIFIER
                |   CONSTANT
        '''
        p[0] = p[1]

    def p_error(self, p):
        if p:
            print(p)
        else:
            print("Reach EOF")

    def parse(self, data):
        self._parser.parse(data)

class C99PreProcessor(object):
    '''
    Pre process include files.
    The pre processor is in charge of macro expansion such as macro function, pragma, include or define.
    '''
    
    def __init__(self, output_path, system_path = None):
        self._output_path = output_path
        self._parser = C99PreProcessorParser()
            
        self._headers_table = {}

        if not system_path:
            self._system_path = [
                                    "stdlib/",
                                ]
        else:
            self._system_path = system_path

        for path in self._system_path:
            self._link_header(path)

    def _link_header(self, input_path):
        """
        Link STD libs and set their location in the main dictionnary.
        """
        for path in Path(input_path).rglob('*.h'):
            self._headers_table[path.name] = path

    def _parse(self, header):
        """
        Parse the data
        
        :param      data:  The data
        :type       data:  { type_description }
        """

        # Read the content of the header and parse it in purpose to
        # construct the macro table and a token list.
        data = header.read()
        self._parser.parse(data)

    def process(self, input_path):
        """
        Preprocess a project before compiling it to Python code.
        
        The pre processing is responsible of macro expansion which
        starts with '#'.

        :param      input_path:  The input path
        :type       input_path:  { type_description }
        """
        self._link_header(input_path)
        
        # First pass will parse every headers to build macro tables and token list.
        for path in Path(input_path, encoding = 'utf-8').rglob('*.h'):
            with open(path, 'rt') as header:
                self._parse(header)

if __name__ == "__main__":
    # pre_processor = C99PreProcessor("output/")

    # pre_processor.process("examples/")    

    pre_processor_parser = C99PreProcessorParser(debug = True)


    data_example =  '''
                    #define CONSTANT 40 2
                    #include "fat32_constant.h"
                    '''

    pre_processor_parser.parse(data_example)