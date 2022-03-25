from lexer_99 import C99Lexer
from utils import debug_production

import intermediate_representation as ir
import ply.yacc as yacc

class C99Parser(object):
    """
    Produce a parser that create an AST from C source/header files
    and will provide a compatible interface to Python ctypes library.
    """

    def __init__(self, lexer = None, debug = False, **kwargs):
        if not lexer:
            self._lexer = C99Lexer()
        else:
            self._lexer = lexer

        self.tokens        = self._lexer.tokens
        self._parser       = yacc.yacc(module = self, debug = debug, **kwargs)
        self._debug        = debug

    @debug_production
    def p_translation_unit(self, p):
        '''translation_unit : external_declaration 
                            | translation_unit external_declaration'''

    @debug_production
    def p_primary_expression(self, p):
        '''primary_expression : IDENTIFIER
                              | CONSTANT
                              | STRING_LITERAL
                              | '(' expression ')' '''
        if len(p) == 3:
            p[0] = p[2]
        else:
            p[0] = p[1]

    @debug_production
    def p_postfix_expression(self, p):
        '''postfix_expression : primary_expression
                              | postfix_expression '[' expression ']'
                              | postfix_expression '(' ')'
                              | postfix_expression '(' argument_expression_list ')'
                              | postfix_expression '.' IDENTIFIER
                              | postfix_expression PTR_OP IDENTIFIER
                              | postfix_expression INC_OP
                              | postfix_expression DEC_OP
                              | '(' type_name ')' '{' initializer_list '}' 
                              | '(' type_name ')' '{' initializer_list  ',' '}' 
                              '''
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = p[1:]

    @debug_production
    def p_argument_expression_list(self, p):
        '''argument_expression_list : assignment_expression
                                    | argument_expression_list ',' assignment_expression '''
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[1].append(p[3])
            p[0] = p[1]

    @debug_production
    def p_unary_expression(self, p):
        '''unary_expression : postfix_expression
                            | INC_OP unary_expression
                            | DEC_OP unary_expression
                            | unary_operator cast_expression
                            | SIZEOF unary_expression
                            | SIZEOF '(' type_name ')' '''
        if len(p) == 2:
            p[0] = p[1]
        else:
            # TODO : Handle other expression, currently I'm only interested with postfix
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
    def p_cast_expression(self, p):
        '''cast_expression : unary_expression
                           | '(' type_name ')' cast_expression '''
        if len(p) == 2:
            p[0] = p[1]
        else:
            # TODO : Handle casting
            pass

    @debug_production
    def p_multiplicative_expression(self, p):
        '''multiplicative_expression : cast_expression
                                     | multiplicative_expression '*' cast_expression
                                     | multiplicative_expression '/' cast_expression
                                     | multiplicative_expression '%' cast_expression '''
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
        '''logical_or_expression : logical_and_expression
                                 | logical_or_expression OR_OP logical_and_expression '''
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = p[1] or p[3]

    @debug_production
    def p_conditional_expression(self, p):
        '''conditional_expression : logical_or_expression
                                  | logical_or_expression '?' expression ':' conditional_expression '''
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = p[3] if p[1] else p[5]

    @debug_production
    def p_assignment_expression(self, p):
        '''assignment_expression : conditional_expression
                                 | unary_expression assignment_operator assignment_expression'''
        if len(p) == 2:
            p[0] = p[1]
        else:
            # TODO : Handle assignment operators 
            pass

    @debug_production
    def p_assignment_operator(self, p):
        '''assignment_operator : '='
                               | MUL_ASSIGN 
                               | DIV_ASSIGN 
                               | MOD_ASSIGN 
                               | ADD_ASSIGN 
                               | SUB_ASSIGN 
                               | LEFT_ASSIGN 
                               | RIGHT_ASSIGN 
                               | AND_ASSIGN 
                               | XOR_ASSIGN 
                               | OR_ASSIGN '''
        p[0] = p[1]

    @debug_production
    def p_expression(self, p):
        '''expression : assignment_expression
                      | expression ',' assignment_expression '''
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[1].append(p[2])
            p[0] = p[1]

    @debug_production
    def p_constant_expression(self, p):
        '''constant_expression : conditional_expression '''
        p[0] = p[1]

    @debug_production
    def p_declaration(self, p):
        '''declaration : declaration_specifiers ';' 
                       | declaration_specifiers init_declarator_list ';' '''
        if len(p) == 4:
            declaration_specifiers = p[1]
            
            # TODO: Handle all aliases            
            declaration_specifiers[1].identifier = p[2][0]

            if p[1][0] == "typedef" and declaration_specifiers[1].identifier:
                # TODO: Handle all aliases
                self._lexer._symbol_table[declaration_specifiers[1].identifier]["type"] = "TYPEDEF_NAME"
                self._lexer._symbol_table[declaration_specifiers[1].identifier]["value"] = declaration_specifiers[1]

    @debug_production
    def p_declaration_specifiers(self, p):
        '''declaration_specifiers : storage_class_specifier
                                  | storage_class_specifier declaration_specifiers
                                  | type_specifier
                                  | type_specifier declaration_specifiers
                                  | type_qualifier
                                  | type_qualifier declaration_specifiers
                                  | function_specifier
                                  | function_specifier declaration_specifiers'''
        #TODO: Handle different rules (type qualifier/specifier, storage)

        if len(p) == 2:
            p[0] = p[1]
        elif len(p) == 3:
            p[0] = p[1], p[2]

    @debug_production
    def p_init_declarator_list(self, p):
        '''init_declarator_list : init_declarator
                                | init_declarator_list ',' init_declarator '''
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[1].append(p[3])
            p[0] = p[1]

    @debug_production
    def p_init_declarator(self, p):
        '''init_declarator : declarator
                           | declarator '=' initializer '''
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = p[1], p[3]

    @debug_production
    def p_storage_class_specifier(self, p):
        '''storage_class_specifier : TYPEDEF
                                   | EXTERN
                                   | STATIC
                                   | AUTO
                                   | REGISTER '''
        p[0] = p[1]

    @debug_production
    def p_type_specifier(self, p):
        '''type_specifier : VOID
                          | CHAR
                          | SHORT
                          | INT
                          | LONG
                          | FLOAT
                          | DOUBLE
                          | SIGNED
                          | UNSIGNED
                          | BOOLEAN
                          | COMPLEX
                          | IMAGINARY
                          | struct_or_union_specifier
                          | enum_specifier
                          | TYPEDEF_NAME '''
        p[0] = p[1]

    @debug_production
    def p_struct_or_union_specifier(self, p):
        '''struct_or_union_specifier : struct_or_union '{' struct_declaration_list '}'
                                     | struct_or_union IDENTIFIER '{' struct_declaration_list '}'
                                     | struct_or_union IDENTIFIER '''
        if p[1] == 'struct':
            if len(p) == 5:
                struct = ir.Struct(identifier = None, declaration_list = p[3])
            elif len(p) == 6:
                struct = ir.Struct(identifier = p[2], declaration_list = p[4])
            else:
                struct = ir.Struct(identifier = p[2], declaration_list = None)
            p[0] = struct
        elif p[1] == 'union':
            pass

    @debug_production
    def p_struct_or_union(self, p):
        '''struct_or_union : STRUCT
                           | UNION '''
        p[0] = p[1]

    @debug_production
    def p_struct_declaration_list(self, p):
        '''struct_declaration_list : struct_declaration
                                   | struct_declaration_list struct_declaration '''
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[1].append(p[2])
            p[0] = p[1]

    @debug_production
    def p_struct_declaration(self, p):
        '''struct_declaration : specifier_qualifier_list struct_declarator_list ';' '''
        p[0] = ir.StructDeclaration(p[1], p[2])

    @debug_production
    # TODO: Handle error whenever type is a typedef not yet declared. (Ambiguity with IDENTIFIER otherwise)
    def p_specifier_qualifier_list(self, p):
        '''specifier_qualifier_list : type_specifier
                                    | type_specifier specifier_qualifier_list
                                    | type_qualifier 
                                    | type_qualifier specifier_qualifier_list'''
        if len(p) == 3:
            p[0] = [p[1],]
            p[0].extend(p[2])
        else:
            p[0] = [p[1],]

    @debug_production
    def p_struct_declarator_list(self, p):
        '''struct_declarator_list : struct_declarator
                                  | struct_declarator_list ',' struct_declarator'''
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[1].append(p[3])
            p[0] = p[1]

    @debug_production
    def p_struct_declarator(self, p):
        '''struct_declarator : declarator
                             | ':' constant_expression
                             | declarator ':' constant_expression '''
        
        # Return a splitted representation of struct declarator
        if len(p) == 2:
            p[0] = [p[1],]
        elif len(p) == 3:
            p[0] = [p[2],]
        else:
            p[0] = [p[1], p[3],]

    @debug_production
    def p_enum_specifier(self, p):
        '''enum_specifier : ENUM '{' enumerator_list '}'
                          | ENUM IDENTIFIER '{' enumerator_list '}'
                          | ENUM '{' enumerator_list  ',' '}'
                          | ENUM IDENTIFIER '{' enumerator_list  ',' '}'
                          | ENUM IDENTIFIER'''
        #TODO: Handle enumeration with identifier        
        if len(p) == 5:
            p[0] = ir.Enumeration(enumerator_list = p[3])

    @debug_production
    def p_enumerator_list(self, p):
        '''enumerator_list : enumerator
                           | enumerator_list ',' enumerator'''
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[1].append(p[3])
            p[0] = p[1]

    @debug_production
    def p_enumerator(self, p):
        '''enumerator : IDENTIFIER
                      | IDENTIFIER '=' constant_expression '''
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = p[1], p[3]

    @debug_production
    def p_function_specifier(self, p):
        '''function_specifier : INLINE '''
        p[0] = p[1]

    @debug_production
    def p_type_qualifier(self, p):
        '''type_qualifier : CONST
                          | RESTRICT
                          | VOLATILE '''
        p[0] = p[1]

    @debug_production
    def p_declarator(self, p):
        '''declarator : direct_declarator
                      | pointer direct_declarator '''
        # Return only direct declarator
        if len(p) == 2:
            p[0] = p[1]
        else:
            # TODO : Handle pointer case
            pass

    @debug_production
    def p_direct_declarator(self, p):
        '''direct_declarator : IDENTIFIER
                             | '(' declarator ')'
                             | direct_declarator '[' ']'
                             | direct_declarator '[' type_qualifier_list ']'
                             | direct_declarator '[' type_qualifier_list assignment_expression ']'
                             | direct_declarator '[' assignment_expression ']'
                             | direct_declarator '[' STATIC assignment_expression ']'
                             | direct_declarator '[' STATIC type_qualifier_list assignment_expression ']'
                             | direct_declarator '[' type_qualifier_list STATIC assignment_expression ']'
                             | direct_declarator '[' '*' ']'
                             | direct_declarator '[' type_qualifier_list '*' ']'
                             | direct_declarator '(' parameter_type_list ')'
                             | direct_declarator '(' ')'
                             | direct_declarator '(' identifier_list ')'
                             '''
        
        # We are only interested about struct declaration that aren't 
        # function pointer or pointer on array values. So they aren't
        # handled.

        # Will return identifier and it's array length.
        if len(p) == 2:
            p[0] = p[1]
        elif len(p) == 5:
            # Only handle array case
            if p[2] == '[':
                p[0] = f'''{p[1]}[{p[3]}]'''

    @debug_production
    def p_pointer(self, p):
        '''pointer : '*'
                   | '*' type_qualifier_list
                   | '*' pointer
                   | '*' type_qualifier_list pointer '''
        pass

    @debug_production
    def p_type_qualifier_list(self, p):
        '''type_qualifier_list : type_qualifier
                               | type_qualifier_list type_qualifier '''
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[1].append(p[2])
            p[0] = p[1]

    @debug_production
    def p_parameter_type_list(self, p):
        '''parameter_type_list : parameter_list
                               | parameter_list ',' ELLIPSIS'''
        pass

    @debug_production
    def p_parameter_list(self, p):
        '''parameter_list : parameter_declaration
                          | parameter_list ',' parameter_declaration '''
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[1].append(p[2])
            p[0] = p[1]

    @debug_production
    def p_parameter_declaration(self, p):
        '''parameter_declaration : declaration_specifiers declarator
                                 | declaration_specifiers
                                 | declaration_specifiers abstract_declarator '''
        pass

    @debug_production
    def p_identifier_list(self, p):
        '''identifier_list : IDENTIFIER
                           | identifier_list ',' IDENTIFIER '''
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[1].append(p[2])
            p[0] = p[1]

    @debug_production
    def p_type_name(self, p):
        '''type_name : specifier_qualifier_list
                     | specifier_qualifier_list abstract_declarator '''
        pass

    @debug_production
    def p_abstract_declarator(self, p):
        '''abstract_declarator : pointer
                               | direct_abstract_declarator
                               | pointer direct_abstract_declarator '''
        pass

    @debug_production
    def p_direct_abstract_declarator(self, p):
        '''direct_abstract_declarator : '(' abstract_declarator ')'
                                      | '[' ']'
                                      | '[' assignment_expression ']'
                                      | '[' type_qualifier_list ']'
                                      | '[' type_qualifier_list assignment_expression ']'
                                      | direct_abstract_declarator '[' assignment_expression ']'
                                      | direct_abstract_declarator '[' type_qualifier_list assignment_expression ']'
                                      | '[' STATIC assignment_expression ']'
                                      | '[' STATIC type_qualifier_list assignment_expression ']'
                                      | '[' type_qualifier_list STATIC assignment_expression ']'
                                      | direct_abstract_declarator '[' STATIC assignment_expression ']'
                                      | direct_abstract_declarator '[' STATIC type_qualifier_list assignment_expression ']'
                                      | direct_abstract_declarator '[' type_qualifier_list STATIC assignment_expression ']'
                                      | '[' '*' ']'
                                      | direct_abstract_declarator '[' '*' ']'
                                      | '(' ')'
                                      | '(' parameter_type_list ')'
                                      | direct_abstract_declarator '(' ')'
                                      | direct_abstract_declarator '(' parameter_type_list ')' '''
        pass

    @debug_production
    def p_initializer(self, p):
        '''initializer : assignment_expression
                       | '{' initializer_list '}'
                       | '{' initializer_list ',' '}' '''
        pass

    @debug_production
    def p_initializer_list(self, p):
        '''initializer_list : initializer
                            | designation initializer
                            | initializer_list ',' initializer 
                            | initializer_list ',' designation initializer '''
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[1].append(p[2])
            p[0] = p[1]

    @debug_production
    def p_designation(self, p):
        '''designation : designator_list '=' '''
        pass

    @debug_production
    def p_designator_list(self, p):
        '''designator_list : designator
                           | designator_list designator '''
        pass

    @debug_production
    def p_designator(self, p):
        '''designator : '[' constant_expression  ']'
                      | '.' IDENTIFIER '''
        pass

    @debug_production
    def p_statement(self, p):
        '''statement : labeled_statement
                     | compound_statement
                     | expression_statement
                     | selection_statement
                     | iteration_statement
                     | jump_statement '''
        p[0] = p[1]

    @debug_production
    def p_labeled_statement(self, p):
        '''labeled_statement : IDENTIFIER ':' statement
                             | CASE constant_expression ':' statement
                             | DEFAULT ':' statement '''
        pass

    @debug_production
    def p_compound_statement(self, p):
        '''compound_statement : '{' '}'
                              | '{' block_item_list '}' '''
        pass
        # if len(p) == 3:
        #     p[0] = []
        # elif len(p) == 4:
        #     p[0] = p[2]
        # else:
        #     p[0] = [p[2], p[3]]

    @debug_production
    def p_block_item_list(self, p):
        '''block_item_list : block_item
                           | block_item_list block_item '''
        pass

    @debug_production
    def p_block_item(self, p):
        '''block_item : declaration
                      | statement '''
        pass

    @debug_production
    def p_declaration_list(self, p):
        '''declaration_list : declaration
                            | declaration_list declaration '''
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[1].append(p[2])
            p[0] = p[1]

    @debug_production    
    def p_expression_statement(self, p):
        '''expression_statement : ';'
                                | expression ';' '''
        pass

    @debug_production
    def p_selection_statement(self, p):
        '''selection_statement : IF '(' expression ')' statement
                               | IF '(' expression ')' statement ELSE statement
                               | SWITCH '(' expression ')' statement ''' 
        pass
    
    @debug_production
    def p_iteration_statement(self, p):
        '''iteration_statement : WHILE '(' expression ')' statement
                               | DO statement WHILE '(' expression ')' ';'
                               | FOR '(' expression_statement expression_statement ')' statement
                               | FOR '(' declaration expression_statement expression_statement ')' statement '''
        pass

    @debug_production
    def p_jump_statement(self, p):
        '''jump_statement : GOTO IDENTIFIER ';'
                          | CONTINUE ';'
                          | BREAK ';'
                          | RETURN ';'
                          | RETURN expression ';' '''
        pass

    @debug_production
    def p_external_declaration(self, p):
        '''external_declaration : function_definition
                                | declaration '''
        p[0] = p[1]

    @debug_production
    def p_function_definition(self, p):
        '''function_definition : declaration_specifiers declarator declaration_list compound_statement
                                | declaration_specifiers declarator compound_statement'''
        function = ir.Function()

    def p_error(self, p):
        if p:
            print(f'''Error: {p}''')
            # Just discard the token and tell the parser it's okay.
            self._parser.errok()
        else:
            print("Reach EOF")

    def parse(self, data):
        self._parser.parse(data)

if __name__ == "__main__":
    parser = C99Parser(debug = True)

    with open("examples/fat32.h", "rt") as include_file:
        data = include_file.read()

    parser.parse(data)