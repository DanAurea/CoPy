from pathlib import Path
from utils import debug_production

import intermediate_representation as ir
import ply.lex as lex
import ply.yacc as yacc
import re
import time

LETTER = r"[a-zA-Z]"
DIGIT = r"[0-9]"
LETTER_DIGIT = r"[a-zA-Z-0-9]"
E = f"""[Ee][+-]?{DIGIT}+"""
FLOAT_SUFFIX = r"[fF]"
INT_SUFFIX = r"[uU]"

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

    def __init__(self, **kwargs):
        self._lexer        = lex.lex(module = self, **kwargs)
        self.lineno        = 1

    # Define a rule so we can track line numbers
    def t_NEWLINE(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)
        
        self.lineno = t.lexer.lineno
        
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

        # Check first if it's a standard C directive
        if t.value in self.reserved:
            t.type = self.reserved[t.value]

        return t

    def t_IDENTIFIER(self, t):
        r'[a-zA-Z_][a-zA-Z_0-9]*'
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

    def t_LPAREN(self, t):
        r'(?<!\s)\('
        # Match a left parenthesis only if not preceded by white space character
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
        self._current_file = ""
        
        self._lexer = C99PreProcessorLexer()
        self.tokens  = self._lexer.tokens

        self.macro = {} 

        self.define_macro("__DATE__", time.strftime, arg_list = ["%b %d %Y", time.localtime])
        self.define_macro("__FILE__", self._current_file)
        self.define_macro("__LINE__", self._lexer.lineno)
        self.define_macro("__TIME__", time.strftime, arg_list = ["%H:%M:%S", time.localtime])

        self._parser = yacc.yacc(module = self, debug = debug, start = "preprocessing_file", **kwargs)
        self._debug  = debug

    def define_macro(self, name, replacement = None, arg_list = None, variadic = False):
        """
        Define a new Macro using intermediate representation.
        
        :param      name:        The macro name
        :type       name:        str
        :param      replacement:  The replacement list
        :type       replacement:  object
        :param      arg_list:          The argument list
        :type       arg_list:          list or None if no arg list
        :param      variadic:          Variable number of arguments
        :type       variadic:          bool
        """
        self.macro[name] = ir.Macro(name, replacement, arg_list, variadic) 
        return self.macro[name]

    def expand_macro(self, name, arg_list = None):
        """
        Expands the macro.
        
        :param      name:      The name
        :type       name:      str
        :param      arg_list:  The argument list
        :type       arg_list:  list
        """
        if name in self.macro:
            if not self.macro[name].has_been_expanded:
                replacement = self.macro[name].expand(arg_list)

            # TODO : The replacement should be rescanned.
            
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
        system_like     = False
        include_content = ''

        #TODO: Include header content
        if header_name[0] == '<' and header_name[-1] == '>':
            system_like = True

        # Prevent appending of include content with next line in further parsing.
        include_content += '\n'

        return include_content

    def write(self, file_content):
        """
        Write the preprocessed file content to output.
        
        :param      file_content:  The file content
        :type       file_content:  str
        """
        pass

    @debug_production
    def p_preprocessing_file(self, p):
        '''
        preprocessing_file : 
                           | group
        '''
        if len(p) == 2:
            # TODO: Should write to output path only if user request it explicitly
            self.write(p)
            p[0] = p[1]

    @debug_production
    def p_group(self, p):
        '''
        group : group_part
              | group group_part
        '''
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[1].append(p[2])
            p[0] = p[1]

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
        p[0] = p[1]

    @debug_production
    def p_if_section(self, p):
        '''
        if_section  : if_group endif_line
        '''
        if_block = '\n'

        if p[0][0]:
            if_block = p[0][1]

        p[0] = if_block

    @debug_production
    def p_if_section2(self, p):
        '''
        if_section  : if_group elif_groups endif_line
        '''
        p[0] = '\n'

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
        
        p[0] = if_block

    @debug_production
    def p_if_section4(self, p):
        '''
        if_section  : if_group elif_groups else_group endif_line
        '''
        p[0] = '\n'

    @debug_production
    def p_if_group(self, p):
        '''
        if_group : IF constant_expression NEWLINE
                 | IF constant_expression NEWLINE group
        '''
        group = None

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
        group = None
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
        group = None
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
        group = None

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
        group = None

        if len(p) == 4:
            group = p[3]

        p[0] = group

    @debug_production
    def p_endif_line(self, p):
        '''
        endif_line : ENDIF NEWLINE
        '''
        pass

    @debug_production
    def p_define_directive(self, p):
        '''
        define_directive : DEFINE IDENTIFIER replacement_list
        '''
        self.define_macro(p[2], replacement = p[3])
        p[0] = '\n'

    @debug_production
    def p_define_directive_2(self, p):
        '''
        define_directive : DEFINE IDENTIFIER LPAREN ')' replacement_list
        '''
        self.define_macro(p[2], replacement = p[3])
        p[0] = '\n'

    @debug_production
    def p_define_directive_3(self, p):
        '''
        define_directive : DEFINE IDENTIFIER LPAREN identifier_list ')' replacement_list
        '''
        self.define_macro(p[2], replacement = p[6], arg_list = p[4])
        p[0] = '\n'

    @debug_production
    def p_define_directive_4(self, p):
        '''
        define_directive : DEFINE IDENTIFIER LPAREN ELLIPSIS ')' replacement_list
        '''
        self.define_macro(p[2], replacement = p[6], variadic = True)
        p[0] = '\n'

    @debug_production
    def p_define_directive_5(self, p):
        '''
        define_directive : DEFINE IDENTIFIER LPAREN identifier_list ',' ELLIPSIS ')' replacement_list
        '''
        self.define_macro(p[2], replacement = p[8], arg_list = p[4], variadic = True)
        p[0] = '\n'

    @debug_production
    def p_error_directive(self, p):
        '''
        error_directive : ERROR
                        | ERROR token_list
        '''
        if len(p) == 2:
            raise Exception()
        elif len(p) == 3:
            raise Exception(p[2])

    @debug_production
    def p_include_directive(self, p):
        '''
        include_directive : INCLUDE token_list
        '''
        p[0] = self.include(p[2])

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
        p[0] = self.undef_macro(p[2])
    
    @debug_production
    def p_primary_expression(self, p):
        '''primary_expression : IDENTIFIER
        '''
        if p[1] in self.macro:
            p[0] = self.expand_macro(p[1])
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
        p[0] = p[1:]

    def p_conditionally_supported_directive(self, p):
        '''
        conditionally_supported_directive : DIRECTIVE token_list NEWLINE
        '''
        pass
    
    @debug_production
    def p_identifier_list(self, p):
        '''
        identifier_list : IDENTIFIER
                        | identifier_list ',' IDENTIFIER
        '''
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[1].append(p[3])
            p[0] = p[1]

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
            p[0] = " ".join(p[1:])

    def p_token(self, p):
        '''
        token :     IDENTIFIER
        '''
        if p[1] in self.macro:
            p[0] = self.expand_macro(p[1])
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

    def parse(self, data):
        self._parser.parse(data)

class C99PreProcessor(object):
    '''
    Pre process include files.
    The pre processor is in charge of macro expansion such as macro function, pragma, include or define.
    '''
    
    def __init__(self, output_path, system_path = [], keep_comment = True, **kwargs):
        self._output_path = output_path
        self._parser = C99PreProcessorParser(**kwargs)
            
        self._headers_table = {}
        
        self._di_tri_graph_replace_table =  {
                                                # Digraph
                                                '<:' : '[', '>:' : ']', '<%' : '{', '>%' : '}', '%:' : '#',  
                                                # Trigraph
                                                '??=' : '#', '??/' : '\\', '??\'' : '^', '??(' : '[',
                                                '??)' : ']', '??!' : '|', '??<' : '{', '??>' : '}',
                                                '??-' : '~',
                                            }

        if not system_path:
            self._system_path = ["stdlib/",]
        else:
            self._system_path = system_path

        self._keep_comment = keep_comment

        for path in self._system_path:
            self._link_header(path)

    def _link_header(self, input_path):
        """
        Link STD libs and set their location in the main dictionnary.
        """
        for path in Path(input_path).rglob('*.h'):
            self._headers_table[path.name] = path

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

    def _parse(self, file_content):
        """
        Parse the file content using C 99 standard.
        
        :param      data:  The header/source file content
        :type       data:  str
        """
        # Read the content of the header and parse it in purpose to
        # construct the macro table and a token list.
        self._parser.parse(file_content)

    def _is_source_file(self, file_content):
        return file_content[-1] == '\n'

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
        for path in Path(input_path, encoding = 'utf-8').rglob('*.[hc]'):
            with open(path, 'rt') as header:
                self._current_file = path.name
                file_content = header.read()
                
                if not self._is_source_file(file_content):
                    file_content += '\n'

                # Translation phase 1
                file_content = self._replace_di_trigraph(file_content)
                
                # Translation phase 2
                file_content = self._join_backslash(file_content)
                
                # Translation phase 3 and 4 are done in parallel
                if not self._keep_comment:
                    file_content = self._strip_comment(file_content)
                
                self._parse(file_content)

if __name__ == "__main__":
    pre_processor = C99PreProcessor("output/", debug = True, keep_comment = False)

    pre_processor.process("examples/digraph_trigraph")