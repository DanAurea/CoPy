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
                    "_Pragma" : "_PRAGMA",
                    "undef" : "UNDEF",
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
                "NEWLINE",

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
        self._symbol_table = {
                                "__DATE__" : "CURRENT_DATE", # TODO : CALLBACK should be set instead
                                "__FILE__" : "FILENAME", # TODO : CALLBACK should be set instead
                                "__LINE__" : "CURRENT_LINE", # TODO : CALLBACK should be set instead
                                "__TIME__" : "TIME", # TODO : CALLBACK should be set instead
                            }

    # Define a rule so we can track line numbers
    def t_NEWLINE(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)
        return t

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

        #There's no type checking as we are only in translation phase 3 and not defining yet custom/user defined types.    
        return t

    def t_STRING_LITERAL(self, t):
        r'L?"(\\.|[^\\\"])*"'
        return t

    CONSTANT_RE = "|".join([
                                fr"""{DIGIT}+{E}{FLOAT_SUFFIX}?""",
                                fr"""{DIGIT}*\.{DIGIT}+({E})?{FLOAT_SUFFIX}?""",
                                fr"""{DIGIT}+\.{DIGIT}*({E})?{FLOAT_SUFFIX}?""",
                                fr"""0[xX]{LETTER_DIGIT}+{INT_SUFFIX}?""",
                                fr"""0{DIGIT}+{INT_SUFFIX}?""",
                                fr"""{DIGIT}+{INT_SUFFIX}?""",
                                fr"""L?'(\\.|[^\\'])+'""",
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
    def p_group(self, p):
        '''
        group : group_part
              | group group_part
        '''

    @debug_production
    def p_group_part(self, p):
        '''
        group_part : control_line
                   | if_section
                   | text_line
                   | '#' conditionally_supported_directive
        '''
        pass

    @debug_production
    def p_control_line(self, p):
        '''
        control_line : '#' define_directive NEWLINE
                     | '#' error_directive NEWLINE
                     | '#' include_directive NEWLINE
                     | '#' line_directive NEWLINE
                     | '#' pragma_directive NEWLINE
                     | '#' undef_directive NEWLINE
                     | '#' NEWLINE
        '''
        pass

    @debug_production
    def p_if_section(self, p):
        '''
        if_section  : if_group endif_line
                    | if_group elif_groups endif_line
                    | if_group else_group endif_line
                    | if_group elif_groups else_group endif_line
        '''
        pass

    @debug_production
    def p_if_group(self, p):
        '''
        if_group : '#' IF constant_expression NEWLINE
                 | '#' IF constant_expression NEWLINE group
                 | '#' IFDEF IDENTIFIER NEWLINE
                 | '#' IFDEF IDENTIFIER NEWLINE group
                 | '#' IFNDEF IDENTIFIER NEWLINE
                 | '#' IFNDEF IDENTIFIER NEWLINE group
        '''
        pass

    @debug_production
    def p_elif_groups(self, p):
        '''
        elif_groups : elif_group
                    | elif_groups elif_group
        '''
        pass

    @debug_production
    def p_elif_group(self, p):
        '''
        elif_group : '#' ELIF constant_expression NEWLINE
                   | '#' ELIF constant_expression NEWLINE group
        '''
        pass

    @debug_production
    def p_else_group(self, p):
        '''
        else_group : '#' ELSE NEWLINE
                   | '#' ELSE NEWLINE group
        '''
        pass

    @debug_production
    def p_endif_line(self, p):
        '''
        endif_line : '#' ENDIF NEWLINE
        '''
        pass

    @debug_production
    def p_define_directive(self, p):
        '''
        define_directive : DEFINE IDENTIFIER replacement_list
                         | DEFINE '(' ')' replacement_list
                         | DEFINE '(' identifier_list ')' replacement_list
                         | DEFINE '(' ELLIPSIS ')' replacement_list
                         | DEFINE '(' identifier_list ',' ELLIPSIS ')' replacement_list
        '''
        pass
    
    @debug_production
    def p_error_directive(self, p):
        '''
        error_directive : ERROR
                        | ERROR token_list
        '''
        pass

    @debug_production
    def p_include_directive(self, p):
        '''
        include_directive : INCLUDE token_list
        '''
        pass

    @debug_production
    def p_line_directive(self, p):
        '''
        line_directive : LINE token_list
        '''
        pass

    @debug_production
    def p_pragma_directive(self, p):
        '''
        pragma_directive : PRAGMA
                         | PRAGMA token_list
                         | _PRAGMA '(' STRING_LITERAL ')'
        '''
        pass

    @debug_production
    def p_undef_directive(self, p):
        '''
        undef_directive : UNDEF IDENTIFIER
        '''
        pass
    
    @debug_production
    def p_primary_expression(self, p):
        '''primary_expression : IDENTIFIER
                              | CONSTANT
                              | '(' constant_expression ')' '''
        if len(p) == 3:
            p[0] = p[2]
        else:
            p[0] = p[1]

    @debug_production
    def p_unary_expression(self, p):
        '''unary_expression : primary_expression
                            | unary_operator unary_expression
                            | DEFINED '(' IDENTIFIER ')' '''
        if len(p) == 2:
            p[0] = p[1]
        else:
            pass

    @debug_production
    def p_unary_operator(self, p):
        '''unary_operator : '&'
                          | '*'  
                          | '+'  
                          | '-'  
                          | '~'  
                          | '!' '''
        p[0] = p[1]

    @debug_production
    def p_multiplicative_expression(self, p):
        '''multiplicative_expression : unary_expression
                                     | multiplicative_expression '*' unary_expression
                                     | multiplicative_expression '/' unary_expression
                                     | multiplicative_expression '%' unary_expression '''
        if len(p) == 2:
            p[0] = p[1]
        else:
            if p[2] == '*':
                p[0] = p[1] * p[3]
            elif p[2] == '/':
                p[0] = p[1] / p[3]
            elif p[2] == '%':
                p[0] = p[1] % p[3]

    @debug_production
    def p_additive_expression(self, p):
        '''additive_expression : multiplicative_expression
                               | additive_expression '+' multiplicative_expression
                               | additive_expression '-' multiplicative_expression '''
        if len(p) == 2:
            p[0] = p[1]
        else:
            if p[2] == '+':
                p[0] = p[1] + p[3]
            elif p[2] == '-':
                p[0] = p[1] - p[3]

    @debug_production
    def p_shift_expression(self, p):
        '''shift_expression : additive_expression
                            | shift_expression LEFT_OP additive_expression
                            | shift_expression RIGHT_OP additive_expression '''
        if len(p) == 2:
            p[0] = p[1]
        else:
            if p[2] == '<<':
                p[0] = p[1] << p[3]
            elif p[2] == '>>':
                p[0] = p[1] >> p[3]

    @debug_production
    def p_relational_expression(self, p):
        '''relational_expression : shift_expression
                                 | relational_expression '<' shift_expression
                                 | relational_expression '>' shift_expression
                                 | relational_expression LE_OP shift_expression
                                 | relational_expression GE_OP shift_expression '''
        if len(p) == 2:
            p[0] = p[1]
        else:
            if p[2] == '<':
                p[0] = p[1] < p[3]
            elif p[2] == '>':
                p[0] = p[1] > p[3]
            elif p[2] == '<=':
                p[0] = p[1] <= p[3]
            elif p[2] == '>=':
                p[0] = p[1] >= p[3]

    @debug_production
    def p_equality_expression(self, p):
        '''equality_expression : relational_expression
                               | equality_expression EQ_OP relational_expression
                               | equality_expression NE_OP relational_expression '''
        if len(p) == 2:
            p[0] = p[1]
        else:
            if p[2] == '==':
                p[0] = p[1] == p[3]
            elif p[2] == '!=':
                p[0] = p[1] != p[3]

    @debug_production
    def p_and_expression(self, p):
        '''and_expression : equality_expression
                          | and_expression '&' equality_expression '''
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = p[1] & p[3]

    @debug_production
    def p_exclusive_or_expression(self, p):
        '''exclusive_or_expression : and_expression
                                   | exclusive_or_expression '^' and_expression '''
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = p[1] ^ p[3]

    @debug_production
    def p_inclusive_or_expression(self, p):
        '''inclusive_or_expression : exclusive_or_expression
                                   | inclusive_or_expression '|' exclusive_or_expression '''
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = p[1] | p[3]

    @debug_production
    def p_logical_and_expression(self, p):
        '''logical_and_expression : inclusive_or_expression
                                  | logical_and_expression AND_OP inclusive_or_expression '''
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = p[1] and p[3]

    @debug_production
    def p_logical_or_expression(self, p):
        '''
        logical_or_expression : logical_and_expression
                              | logical_or_expression OR_OP logical_and_expression '''
        pass

    @debug_production
    def p_conditional_expression(self, p ):
        '''
        conditional_expression : logical_or_expression
                               | logical_or_expression '?' conditional_expression ':' conditional_expression '''
        pass

    @debug_production
    def p_constant_expression(self, p):
        '''
        constant_expression : conditional_expression
        '''
        pass

    @debug_production
    def p_text_line(self, p):
        '''
        text_line : NEWLINE
                  | token_list NEWLINE
        '''
        pass

    def p_conditionally_supported_directive(self, p):
        '''
        conditionally_supported_directive : token_list NEWLINE
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
    def p_replacement_list(self, p):
        '''
        replacement_list : 
                         | token_list
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

    def p_token(self, p):
        '''
        token :     IDENTIFIER
                |   HEADER_NAME
                |   CONSTANT
                |   STRING_LITERAL
                |   operator_punc
        '''
        p[0] = p[1]

    def p_operator_punc(self, p):
        '''operator_punc :     '='
                               | AND_OP
                               | MUL_ASSIGN 
                               | DIV_ASSIGN
                               | MOD_ASSIGN 
                               | ADD_ASSIGN 
                               | SUB_ASSIGN 
                               | LEFT_ASSIGN 
                               | RIGHT_ASSIGN 
                               | AND_ASSIGN 
                               | XOR_ASSIGN 
                               | OR_ASSIGN 
                               | DEC_OP
                               | ELLIPSIS
                               | EQ_OP
                               | GE_OP
                               | INC_OP
                               | LEFT_OP
                               | LE_OP
                               | NE_OP
                               | PTR_OP
                               | OR_OP
                               | RIGHT_OP
                               | ';'
                               | '{'
                               | '}'
                               | ',' 
                               | ':'
                               | '('
                               | ')'
                               | '['
                               | ']'
                               | '.'
                               | '&'
                               | '!'
                               | '~'
                               | '-'
                               | '+'
                               | '*'
                               | '/'
                               | '%'
                               | '<'
                               | '>'
                               | '^'
                               | '|'
                               | '?'
                               | '"'
                               | '@'
                               | '#'
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


    data_example = '''
#define DLEVEL 1
#if DLEVEL == 1
    #define SIGNAL 1
#else
    #define SIGNAL 2
#endif
'''

    pre_processor_parser.parse(data_example)