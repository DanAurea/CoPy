from pathlib import Path
from utils import debug_production

import intermediate_representation as ir
import ply.lex as lex
import ply.yacc as yacc
import re
import time

LETTER       = r"[a-zA-Z]"
DIGIT        = r"[0-9]"
LETTER_DIGIT = r"[a-zA-Z-0-9]"
HEX_DIGIT    = r"[a-fA-F-0-9]"
E            = f"""[Ee][+-]?{DIGIT}+"""
FLOAT_SUFFIX = r"[fFlL]+"
INT_SUFFIX   = r"[uUlL]+"

COMMENT_RE = re.compile(r'\/\*[\s\S]*?\*\/+|//.*')

class C99PreProcessorLexer(object):
    """
    C99 Preprocessor lexer.
    """

    # Keywords
    reserved = {
                    "#define" : "DEFINE",
                    "defined" : "DEFINED",
                    "#elif" : "ELIF",
                    "#else" : "ELSE",
                    "#endif" : "ENDIF",
                    "#error" : "ERROR",
                    "#if" : "IF",
                    "#ifdef" : "IFDEF",
                    "#ifndef" : "IFNDEF",
                    "#include" : "INCLUDE",
                    "#line" : "LINE",
                    "#pragma" : "PRAGMA",
                    "_Pragma" : "_PRAGMA",
                    "#undef" : "UNDEF",
            }

    # This class attribute should be set because ply
    # is using Python introspection for its internal
    # working.
    tokens = list(reserved.values()) + \
            [
                "CONSTANT",
                "HEADER_NAME",
                "DIRECTIVE",
                "IDENTIFIER",
                "STRING_LITERAL",

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
                "NE_OP",
                "HASH_HASH",
                "LPAREN",
            ]

    literals = [ ';', '{', '}', ',', ':', '=', '(', ')', '[', ']', '.', '&', '!',
                 '~', '-', '+', '*', '/', '%', '<', '>', '^', '|', '?', '"', '@', 
                 '#']

    # Skip whitespaces
    t_ignore = ' \t'

    # Ignored characters for directive
    t_directive_ignore = ' \t'

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
    t_HASH_HASH = r'\#\#'

    states = (
        ('directive','inclusive'),
    )

    def __init__(self, **kwargs):
        self._lexer    = lex.lex(module = self, reflags=re.UNICODE, **kwargs)
        self.nested_if = 0

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

    def t_DIRECTIVE(self, t):
        r'\#[a-zA-Z_][a-zA-Z_0-9]*'

        t.lexer.begin("directive")

        # Check first if it's a standard C directive
        if t.value in self.reserved:
            t.type = self.reserved[t.value]
            
            if t.type == "IF" or t.type == 'IFDEF' or t.type == 'IFNDEF':
                self.nested_if += 1
            elif t.type == "ENDIF":
                self.nested_if -= 1

                if self.nested_if < 0:
                    raise Exception("Number of #endif doesn't match with number of #if.")

        return t

    def t_IDENTIFIER(self, t):
        r'[a-zA-Z_][a-zA-Z_0-9]*'
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
        # to allow easier conversion from Python str to float.
        
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
        # to allow easier conversion from Python str to float.
        
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
        # to allow easier conversion from Python str to float. 

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
        # to allow easier conversion from Python str to float.
        r'L?\'(\\.|[^\'])+\''
        t.type = "CONSTANT"
        return t
 
    # For bad characters, we just skip over it
    def t_directive_error(self, t):
        t.lexer.skip(1)

    # Defining LPAREN in operator_punc and define_directive will lead to ambiguities due to replacement_list
    # to avoid this we only define LPAREN inside directive, this will avoid any further issues with text_line
    # reporting lexer error for LPAREN.
    def t_directive_LPAREN(self, t):
        r'(?<!\s)\('
        # Match a left parenthesis only if not preceded by white space character
        return t

    def t_directive_RPAREN(self, t):
        r'\)'
        t.lexer.begin("INITIAL")
        t.type = ')'
        return t

    # Match any parenthesis and return it as a literal to avoid ambiguity between lparen and '(' in production rule.
    def t_LPAREN(self, t):
        r'\('
        t.type = '('      # Set token type to the expected literal
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

class C99PreProcessor(object):

    def __init__(self, stdlib_path = [], keep_comment = True, debug = False, **kwargs):
        self._current_file = Path()
        
        self._lexer = C99PreProcessorLexer()
        self.tokens = self._lexer.tokens

        self.headers_table = {}
        self.macro         = {} 

        self.define_macro("__DATE__", callback = time.strftime, arg_list = ["%b %d %Y"])
        self.define_macro("__FILE__", callback = self.get_current_filename)
        self.define_macro("__LINE__", callback = self.get_lineno)
        self.define_macro("__TIME__", callback = time.strftime, arg_list = ["%H:%M:%S"])

        self._parser = yacc.yacc(module = self, debug = debug, start = "preprocessing_file", **kwargs)
        self._di_tri_graph_replace_table =  {
                                                # Digraph
                                                '<:' : '[', '>:' : ']', '<%' : '{', '>%' : '}', '%:' : '#',  
                                                # Trigraph
                                                '??=' : '#', '??/' : '\\', '??\'' : '^', '??(' : '[',
                                                '??)' : ']', '??!' : '|', '??<' : '{', '??>' : '}',
                                                '??-' : '~',
                                            }

        if not stdlib_path:
            self._stdlib_path = ["stdlib/",]
        else:
            self._stdlib_path = stdlib_path

        self._keep_comment       = keep_comment
        self._debug              = debug
        self._discard_next_paren = False

    """
    Preprocessor production rules + semantics actions
    """
    @debug_production
    def p_preprocessing_file(self, p):
        '''
        preprocessing_file : 
                           | group
        '''
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = ''

    @debug_production
    def p_group(self, p):
        '''
        group : group_part
              | group group_part
        '''
        if len(p) == 2:
            p[0] = p[1]
        else:
            # No whitespace should be put between group/group_part, each group being separated by a newline
            p[0] = f'{p[1]}{p[2]}'

    @debug_production
    def p_group_part(self, p):
        '''
        group_part : control_line
                   | if_section
                   | text_line
                   | conditionally_supported_directive
        '''
        p[0] = p[1]

    @debug_production
    def p_control_line(self, p):
        '''
        control_line : define_directive NEWLINE
                     | error_directive NEWLINE
                     | include_directive NEWLINE
                     | line_directive NEWLINE
                     | pragma_directive NEWLINE
                     | undef_directive NEWLINE
        '''
        p[0] = f'{p[1]}\n'

    @debug_production
    def p_if_section(self, p):
        '''
        if_section  : if_group endif_line
        '''
        if_block = '\n'

        if p[1][0]:
            if_block = p[1][1]
        
        # Only rescan if we aren't in another if block which might evaluate to False, otherwise useless processing could happens.
        if not self._lexer.nested_if:
            if_block = self.parse(if_block, lexer = self._lexer._lexer.clone())

        p[0] = if_block

    @debug_production
    def p_if_section2(self, p):
        '''
        if_section  : if_group elif_groups endif_line
        '''
        if_block = '\n'

        if p[1][0]:
            if_block = p[1][1]
        else:
            for elif_group in p[2]:
                if elif_group[0]:
                    if_block = elif_group[1]
                    break

        # Only rescan if we aren't in another if block which might evaluate to False, otherwise useless processing could happens.
        if not self._lexer.nested_if:
            if_block = self.parse(if_block, lexer = self._lexer._lexer.clone())

        p[0] = if_block

    @debug_production
    def p_if_section3(self, p):
        '''
        if_section  : if_group else_group endif_line
        '''
        if_block = '\n'

        if p[1][0]:
            if_block = p[1][1]
        else:
            if_block = p[2]

        # Only rescan if we aren't in another if block which might evaluate to False, otherwise useless processing could happens.
        if not self._lexer.nested_if:            
            if_block = self.parse(if_block, lexer = self._lexer._lexer.clone())

        p[0] = if_block

    @debug_production
    def p_if_section4(self, p):
        '''
        if_section  : if_group elif_groups else_group endif_line
        '''

        block_evaluated = False

        if p[1][0]:
            if_block = p[1][1]
            block_evaluated = True
        else:
            for elif_group in p[2]:
                if elif_group[0]:
                    if_block = elif_group[1]
                    block_evaluated = True
                    break

        if not block_evaluated:
            if_block = p[3]

        # Only rescan if we aren't in another if block which might evaluate to False, otherwise useless processing could happens.
        if not self._lexer.nested_if:
            if_block = self.parse(if_block, lexer = self._lexer._lexer.clone())

        p[0] = if_block

    @debug_production
    def p_if_group(self, p):
        '''
        if_group : IF constant_expression NEWLINE
                 | IF constant_expression NEWLINE group
        '''
        group = ''

        if p[2]:
            if len(p) == 5:
                group = p[4]

        p[0] = (p[2], group)

    @debug_production
    def p_if_group2(self, p):
        '''
        if_group : IFDEF IDENTIFIER NEWLINE
                 | IFDEF IDENTIFIER NEWLINE group
        '''
        group = ''
        is_defined = False

        if p[2] in self.macro:
            is_defined = True
            if len(p) == 5:
                group = p[4]

        p[0] = (is_defined, group)

    @debug_production
    def p_if_group3(self, p):
        '''
        if_group : IFNDEF IDENTIFIER NEWLINE
                 | IFNDEF IDENTIFIER NEWLINE group
        '''
        group = ''
        is_defined = True

        if p[2] not in self.macro:
            is_defined = False
            if len(p) == 5:
                group = p[4]

        p[0] = (not is_defined, group)

    @debug_production
    def p_elif_groups(self, p):
        '''
        elif_groups : elif_group
                    | elif_groups elif_group
        '''
        if len(p) == 2:
            p[0] = [p[1]]
        elif len(p) == 3:
            p[1].append(p[2])
            p[0] = p[1]

    @debug_production
    def p_elif_group(self, p):
        '''
        elif_group : ELIF constant_expression NEWLINE
                   | ELIF constant_expression NEWLINE group
        '''
        group = ''

        if p[2]:
            if len(p) == 5:
                group = p[4]

        p[0] = (p[2], group)

    @debug_production
    def p_else_group(self, p):
        '''
        else_group : ELSE NEWLINE
                   | ELSE NEWLINE group
        '''
        group = ''

        if len(p) == 4:
            group = p[3]

        p[0] = group

    @debug_production
    def p_endif_line(self, p):
        '''
        endif_line : ENDIF NEWLINE
        '''
        p[0] = '\n'

    @debug_production
    def p_define_directive(self, p):
        '''
        define_directive : DEFINE IDENTIFIER replacement_list
        '''
        if not self._lexer.nested_if:
            self.define_macro(p[2], replacement = p[3])
            p[0] = '\n'
        else:
            p[0] = f'{p[1]} {p[2]} {p[3]}'

    @debug_production
    def p_define_directive_2(self, p):
        '''
        define_directive : DEFINE IDENTIFIER LPAREN ')' replacement_list
        '''
        if not self._lexer.nested_if:
            self.define_macro(p[2], replacement = p[5])
            p[0] = '\n'
        else:
            p[0] = f'{p[1]} {p[2]}() {p[5]}'

    @debug_production
    def p_define_directive_3(self, p):
        '''
        define_directive : DEFINE IDENTIFIER LPAREN identifier_list ')' replacement_list
        '''
        if not self._lexer.nested_if:
            self.define_macro(p[2], replacement = p[6], arg_list = p[4].split(','))
            p[0] = '\n'
        else:
            p[0] = f'{p[1]} {p[2]}({p[4]}) {p[6]}'

    @debug_production
    def p_define_directive_4(self, p):
        '''
        define_directive : DEFINE IDENTIFIER LPAREN ELLIPSIS ')' replacement_list
        '''
        if not self._lexer.nested_if:
            self.define_macro(p[2], replacement = p[6], variadic = True)
            p[0] = '\n'
        else:
            p[0] = f'{p[1]} {p[2]}(...) {p[6]}'

    @debug_production
    def p_define_directive_5(self, p):
        '''
        define_directive : DEFINE IDENTIFIER LPAREN identifier_list ',' ELLIPSIS ')' replacement_list
        '''
        if not self._lexer.nested_if:
            self.define_macro(p[2], replacement = p[8], arg_list = p[4].split(','), variadic = True)
            p[0] = '\n'
        else:
            p[0] = f'{p[1]} {p[2]}({p[4]},...) {p[8]}'

    @debug_production
    def p_error_directive(self, p):
        '''
        error_directive : ERROR
                        | ERROR token_list
        '''
        if not self._lexer.nested_if:
            if len(p) == 2:
                raise Exception()
            elif len(p) == 3:
                raise Exception(p[2])
        else:
            p[0] = f'{p[1]} {p[2] if len(p) == 2 else ""}'

    @debug_production
    def p_include_directive(self, p):
        '''
        include_directive : INCLUDE token_list
        '''
        if not self._lexer.nested_if:
            p[0] = self.include(p[2])
        else:
            p[0] = f'{p[1]} {p[2]}'

    @debug_production
    def p_line_directive(self, p):
        '''
        line_directive : LINE token_list
        '''
        if not self._lexer.nested_if:
            p[2] = str(p[2])
            token_list = p[2].split(' ')
            p[0] = self.lineno_update(token_list)
        else:
            p[0] = f'{p[1]} {p[2]}'

    @debug_production
    def p_pragma_directive(self, p):
        '''
        pragma_directive : PRAGMA
                         | PRAGMA token_list
                         | _PRAGMA '(' STRING_LITERAL ')'
        '''
        if not self._lexer.nested_if:
            p[0] = self.pragma(p[1:])
        else:
            p[0] = ' '.join(p[1:])

    @debug_production
    def p_undef_directive(self, p):
        '''
        undef_directive : UNDEF IDENTIFIER
        '''
        if not self._lexer.nested_if:
            self.undef_macro(p[2])
            p[0] = '\n'
        else:
            p[0] = f'{p[1]} {p[2]}'
    
    @debug_production
    def p_primary_expression(self, p):
        '''primary_expression : IDENTIFIER
        '''
        if p[1] in self.macro:
            replacement = self.expand_macro(p[1])
            p[0] = replacement if replacement != None else p[1]
        else:
            p[0] = p[1]

    @debug_production
    def p_primary_expression2(self, p):
        '''primary_expression : CONSTANT'''
        p[0] = p[1]

    @debug_production
    def p_primary_expression3(self, p):
        '''primary_expression : '(' constant_expression ')' '''
        p[0] = p[2]

    @debug_production
    def p_unary_expression(self, p):
        '''unary_expression : primary_expression
                            | unary_operator unary_expression
                            | DEFINED '(' IDENTIFIER ')' '''
        if len(p) == 2:
            p[0] = p[1]
        elif len(p) == 3:
            p[0] = p[1], p[2]
        else:
            p[0] = True if p[3] in self.macro else False

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
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = p[1] or p[2]

    @debug_production
    def p_conditional_expression(self, p ):
        '''
        conditional_expression : logical_or_expression
                               | logical_or_expression '?' conditional_expression ':' conditional_expression '''
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = p[1] if p[2] else p[3] 

    @debug_production
    def p_constant_expression(self, p):
        '''
        constant_expression : conditional_expression
        '''
        p[0] = p[1]

    @debug_production
    def p_text_line(self, p):
        '''
        text_line : NEWLINE
                  | token_list NEWLINE
        '''
        p[0] = ' '.join([str(t) for t in p[1:]])

    def p_conditionally_supported_directive(self, p):
        '''
        conditionally_supported_directive : DIRECTIVE token_list NEWLINE
        '''
        p[0] = '\n'
    
    @debug_production
    def p_identifier_list(self, p):
        '''
        identifier_list : IDENTIFIER
                        | identifier_list ',' IDENTIFIER
        '''
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = ''.join(p[1:])

    @debug_production
    def p_replacement_list(self, p):
        '''
        replacement_list : 
                         | token_list
        '''
        if len(p) == 2:
            p[0] = p[1]

    @debug_production
    def p_token_list(self, p):
        '''
        token_list : token
                   | token_list token
        '''
        if len(p) == 2:
            p[0] = p[1]
        else:
            tokens = p[1:]
            
            # TODO: Check if there's a better way to skip open parenthesis once function-like macro
            # has been expanded.
            # 
            # HACK: Because we are looking ahead for function-like macro expansion and PLY internally
            # return matched '(' which is done before identifier is being expanded.
            # So to know we need to skip it a boolean is set when function-like macro is
            # expanded.
            if self._discard_next_paren and tokens[1] == '(':
                tokens.pop()
                self._discard_next_paren = False

            p[0] = ' '.join([str(t) for t in tokens])

    def p_token(self, p):
        '''
        token :     IDENTIFIER
        '''
        if p[1] in self.macro:
            arg_list = []
            replacement = None

            # Lookahead so function like macro will be expanded correctly.
            lexer = p.lexer.clone()

            # We lookahead with a cloned lexer so we are able to backtrack if we see
            # that macro should not be expanded because it's being recursive.
            if lexer.lexmatch.group() == '(':
                next_token = lexer.next().value
                while next_token != ')':
                    if next_token != ',':
                        arg_list.append(str(next_token))
                    next_token = lexer.next().value
            
                replacement = self.expand_macro(p[1], arg_list)
                
                if replacement != None:
                    p.lexer.lexpos = lexer.lexpos
                    self._discard_next_paren = True
            else:
                replacement = self.expand_macro(p[1], arg_list)

            p[0] = replacement if replacement != None else p[1]
        else:
            p[0] = p[1]

    def p_token2(self, p):
        '''
        token :     HEADER_NAME
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
                               | HASH_HASH
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
            print(f'Syntax error: {p}')
        else:
            print("Reach EOF")

    """
    Preprocessor methods
    """
    def get_current_filename(self, *args):
        """
        Gets the current file.
        
        :param      args:  The arguments
        :type       args:  list
        """
        return self._current_file.name

    def get_lineno(self, *args):
        """
        Gets the lineno.
        
        :param      args:  The arguments
        :type       args:  list
        """
        return self._lexer._lexer.lineno

    def parse(self, data, lexer = None):
        """
        Parse the file content using C 99 standard.
        
        :param      data:  The header/source file content
        :type       data:  str
        """
        return self._parser.parse(data, lexer = lexer)

    def define_macro(self, name, **kwargs):
        """
        Define a new Macro using intermediate representation.
        
        :param      name:       The macro name
        :type       name:       str
        :param      kwargs:     The keyword arguments
        :type       kwargs:     dict
        """
        self.macro[name] = ir.Macro(name, **kwargs) 
        return self.macro[name]

    def expand_macro(self, name, arg_list = []):
        """
        Expands the macro.
        
        :param      name:      The name
        :type       name:      str
        :param      arg_list:  The argument list
        :type       arg_list:  list
        """
        if name in self.macro:
            replacement = None
            if not self.macro[name].has_been_expanded:
                replacement = self.macro[name].expand(arg_list)
                
                # Rescanning  yield "Reach EOF" because parser expects the input to be compliant as a source file.
                # So we are appending a newline to the replacement to follow C standard.
                # NB: replacement needs to be casted to str due to return of int/float from lexer (see if it can be handled better).
                lexer = self._lexer._lexer.clone()
                lexer_input = str(replacement) + '\n'
                
                # We remove last char which is the extra newline added previously to allow parsing of the replacement as a source file.
                replacement = self.parse(lexer_input, lexer = lexer)[:-1]
            else:
                print(f'Warning: Macro {name} is recursive')

            # Reset expansion flag to False to allow macro expansion in detection of a further token in current parsed text.
            self.macro[name].has_been_expanded = False

            return replacement
        else:
            raise NameError(f'Macro {name} not defined.')

    def undef_macro(self, name):
        """
        Undefine a macro.
        
        :param      name:  The name
        :type       name:  str
        """
        return self.macro.pop(name, None)

    def include(self, header_name):
        """
        Include a file.
        
        :param      header_name:  The header name
        :type       header_name:  str
        """
        include_content  = ''
        is_include_found = False
        header_path      = header_name[1:-1]

        if header_path in self.headers_table:
            return self.headers_table[header_path]

        if header_name[0] == '"' and header_name[-1] == '"':
            include_path = self._current_file.parent.joinpath(header_path)
            is_include_found = include_path.is_file()

        # If include hasn't been found in relative path or header name is enclosed by <> then looks inside
        # stdlib path.
        if not is_include_found:
            for std_dir in self._stdlib_path:
                include_path = Path(std_dir).joinpath(header_path)
                is_include_found = include_path.is_file()
                if is_include_found:
                    break
        
        if not is_include_found:
            # Neither stdlib/relative path yield an existing file so we have to raise an error.
            raise FileNotFoundError(f'{header_path} doesn\'t resolve to an existing file.')
        else:
            include_content = self.process(include_path, self._lexer._lexer.clone())

        # Prevent appending of include content with next line in further parsing.
        include_content += '\n'

        # Add the preprocessed include inside the headers table so we can later output
        # contents inside intermediate files *.i or avoid reprocessing an already preprocessed
        # header.
        self.headers_table[header_path] = include_content

        return include_content

    def pragma(self, directive):
        """
        Execute the pragma directive
        
        :param      directive:  The directive
        :type       directive:  list
        """
        return '\n'

    def lineno_update(self, directive):
        """
        Update the line numberand source file.
        
        :param      directive:  The directive
        :type       directive:  list
        """
        if len(directive) == 1:
            self._lexer._lexer.lineno = int(directive[0])
        else:
            self._lexer._lexer.lineno = int(directive[0])
            self._current_file        = Path(directive[1].replace('"', ''), encoding = 'utf-8')
        
        return '\n'

    def _replace_di_trigraph(self, file_content):
        """
        Replace all digraphs and trigraphs to their corresponding single character.
        
        :param      file_content:    The header/source file content
        :type       file_content:    str
        """
        for di_trigraph, replacing_char in self._di_tri_graph_replace_table.items():
            file_content = file_content.replace(di_trigraph, replacing_char)

        return file_content

    def _join_backslash(self, file_content):
        """
        Replace all digraphs and trigraphs to their corresponding single character.
        
        :param      file_content:    The header/source file content
        :type       file_content:    str
        """
        return file_content.replace('\\\n', '')

    def _strip_comment(self, file_content):
        """
        Strip all comments from the file content.
        
        :param      file_content:  The header/source file content
        :type       file_content:  str
        """
        return re.sub(COMMENT_RE, ' ', file_content)

    def _is_source_file(self, file_content):
        """
        Determines whether the specified file content is source file.
        
        :param      file_content:  The file content
        :type       file_content:  str
        """
        return len(file_content) and file_content[-1] == '\n'

    def process(self, file_path, lexer = None):
        """
        Preprocess a source file before compiling it to Python code.
        
        The pre processing is responsible of directive execution which
        starts with '#'.

        :param      file_path:  The file path
        :type       file_path:  str
        """
        file = Path(file_path, encoding = 'utf-8')

        # Store temporarily current file in case of include
        current_file_tmp = self._current_file 
        self._current_file = file

        file_content = file.read_text()
        
        if not self._is_source_file(file_content):
            file_content += '\n'

        # Translation phase 1
        file_content = self._replace_di_trigraph(file_content)
        
        # Translation phase 2
        file_content = self._join_backslash(file_content)
        
        # Translation phase 3 and 4 are done in parallel
        if not self._keep_comment:
            file_content = self._strip_comment(file_content)
        
        if not lexer:
            lexer = self._lexer._lexer

        # Clone the lexer to allow recursion without interfering with current tokenization.
        preprocessed_output = self.parse(file_content, lexer = lexer)
        self._current_file = current_file_tmp

        return preprocessed_output

if __name__ == "__main__":
    pre_processor = C99PreProcessor(debug = False, keep_comment = False)

    preprocessed_code = pre_processor.process("examples/digraph_trigraph/directive.c")

    print(preprocessed_code)