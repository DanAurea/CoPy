from lexer import CLexer
import ply.yacc as yacc

class CParser(object):
    """
    Produce a parser that create an AST from C source/header files
    and will provide a compatible interface to Python ctypes library.
    """

    def __init__(self, lexer = None, **kwargs):
        if not lexer:
            lexer = CLexer()
        else:
            lexer = lexer

        self.tokens = lexer.tokens
        self._parser = yacc.yacc(module = self, **kwargs)

    def p_translation_unit(self, p):
        '''translation_unit : external_declaration 
                            | translation_unit external_declaration'''
        pass
    
    def p_primary_expression(self, p):
        '''primary_expression : IDENTIFIER
                              | CONSTANT
                              | STRING_LITERAL
                              | '(' expression ')' '''
        pass

    def p_postfix_expression(self, p):
        '''postfix_expression : primary_expression
                              | postfix_expression '[' expression ']' 
                              | postfix_expression '(' ')' 
                              | postfix_expression '(' argument_expression_list ')' 
                              | postfix_expression '.' IDENTIFIER 
                              | postfix_expression PTR_OP IDENTIFIER 
                              | postfix_expression INC_OP 
                              | postfix_expression DEC_OP '''
        pass

    def p_argument_expression_list(self, p):
        '''argument_expression_list : assignment_expression
                                    | argument_expression_list ',' assignment_expression '''
        pass

    def p_unary_expression(self, p):
        '''unary_expression : postfix_expression
                            | INC_OP unary_expression 
                            | DEC_OP unary_expression 
                            | unary_operator cast_expression 
                            | SIZEOF unary_expression 
                            | SIZEOF '(' type_name ')' '''
        pass

    def p_unary_operator(self, p):
        '''unary_operator : '&'
                          | '*'  
                          | '+'  
                          | '-'  
                          | '~'  
                          | '!' '''
        pass

    def p_cast_expression(self, p):
        '''cast_expression : unary_expression
                           | '(' type_name ')' cast_expression '''
        pass

    def p_multiplicative_expression(self, p):
        '''multiplicative_expression : cast_expression
                                     | multiplicative_expression '*' cast_expression
                                     | multiplicative_expression '/' cast_expression
                                     | multiplicative_expression '%' cast_expression '''
        pass

    def p_additive_expression(self, p):
        '''additive_expression : multiplicative_expression
                               | additive_expression '+' multiplicative_expression
                               | additive_expression '-' multiplicative_expression '''
        pass

    def p_shift_expression(self, p):
        '''shift_expression : additive_expression
                            | shift_expression LEFT_OP additive_expression
                            | shift_expression RIGHT_OP additive_expression '''
        pass 

    def p_relational_expression(self, p):
        '''relational_expression : shift_expression
                                 | relational_expression '<' shift_expression
                                 | relational_expression '>' shift_expression
                                 | relational_expression LE_OP shift_expression
                                 | relational_expression GE_OP shift_expression '''
        pass

    def p_equality_expression(self, p):
        '''equality_expression : relational_expression
                               | equality_expression EQ_OP relational_expression
                               | equality_expression NE_OP relational_expression '''
        pass

    def p_and_expression(self, p):
        '''and_expression : equality_expression
                          | and_expression '&' equality_expression '''
        pass

    def p_exclusive_or_expression(self, p):
        '''exclusive_or_expression : and_expression
                                   | exclusive_or_expression '^' and_expression '''
        pass

    def p_inclusive_or_expression(self, p):
        '''inclusive_or_expression : exclusive_or_expression
                                   | inclusive_or_expression '|' exclusive_or_expression '''
        pass

    def p_logical_and_expression(self, p):
        '''logical_and_expression : inclusive_or_expression
                                  | logical_and_expression AND_OP inclusive_or_expression '''
        pass

    def p_logical_or_expression(self, p):
        '''logical_or_expression : logical_and_expression
                                 | logical_or_expression OR_OP logical_and_expression '''
        pass

    def p_conditional_expression(self, p):
        '''conditional_expression : logical_or_expression
                                  | logical_or_expression '?' expression ':' conditional_expression '''
        pass

    def p_assignment_expression(self, p):
        '''assignment_expression : conditional_expression
                                 | unary_expression assignment_operator assignment_expression'''
        pass

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
        pass

    def p_expression(self, p):
        '''expression : assignment_expression
                      | expression ',' assignment_expression '''
        pass

    def p_constant_expression(self, p):
        '''constant_expression : conditional_expression '''
        pass

    def p_declaration(self, p):
        '''declaration : declaration_specifiers ';'
                       | declaration_specifiers init_declarator_list ';' '''
        pass

    def p_init_declarator_list(self, p):
        '''init_declarator_list : init_declarator
                                | init_declarator_list ',' init_declarator '''
        pass

    def p_init_declarator(self, p):
        '''init_declarator : declarator
                           | declarator '=' initializer '''
        pass 

    def p_storage_class_specifier(self, p):
        '''storage_class_specifier : TYPEDEF
                                   | EXTERN
                                   | STATIC
                                   | AUTO
                                   | REGISTER '''
        pass

    # TODO : Check why IDENTIFIER token make type_specifier not working properly
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
                          | struct_or_union_specifier
                          | enum_specifier'''
        pass

    def p_struct_or_union_specifier(self, p):
        '''struct_or_union_specifier : struct_or_union IDENTIFIER '{' struct_declaration_list '}' 
                                     | struct_or_union '{' '}'
                                     | struct_or_union '{' struct_declaration_list '}'
                                     | struct_or_union IDENTIFIER '''
        pass

    def p_struct_or_union(self, p):
        '''struct_or_union : STRUCT
                           | UNION '''
        pass

    def p_struct_declaration_list(self, p):
        '''struct_declaration_list : struct_declaration
                                   | struct_declaration_list struct_declaration '''
        pass

    def p_struct_declaration(self, p):
        '''struct_declaration : specifier_qualifier_list struct_declarator_list ';' '''
        pass

    def p_specifier_qualifier_list(self, p):
        '''specifier_qualifier_list : type_specifier specifier_qualifier_list
                                    | type_specifier
                                    | type_qualifier specifier_qualifier_list
                                    | type_qualifier '''
        pass

    def p_struct_declarator_list(self, p):
        '''struct_declarator_list : struct_declarator
                                  | struct_declarator_list ',' struct_declarator '''
        pass

    def p_struct_declarator(self, p):
        '''struct_declarator : declarator
                               | ':' constant_expression
                               | declarator ':' constant_expression'''
        pass

    def p_enum_specifier(self, p):
        '''enum_specifier : ENUM '{' enumerator_list '}'
                          | ENUM IDENTIFIER '{' enumerator_list '}'
                          | ENUM IDENTIFIER'''
        pass

    def p_enumerator_list(self, p):
        '''enumerator_list : enumerator
                           | enumerator_list ',' enumerator '''
        pass

    def p_enumerator(self, p):
        '''enumerator : IDENTIFIER
                      | IDENTIFIER '=' constant_expression '''
        pass

    def p_type_qualifier(self, p):
        '''type_qualifier : CONST
                          | VOLATILE '''
        pass

    def p_declarator(self, p):
        '''declarator : pointer direct_declarator
                      | direct_declarator '''
        pass

    def p_direct_declarator(self, p):
        '''direct_declarator : IDENTIFIER
                             | '(' declarator ')'
                             | direct_declarator '[' constant_expression ']' 
                             | direct_declarator '[' ']' 
                             | direct_declarator '(' parameter_type_list ')'
                             | direct_declarator '(' identifier_list ')'  
                             | direct_declarator '('  ')' '''
        pass

    def p_pointer(self, p):
        '''pointer : '*'
                   | '*' type_qualifier_list
                   | '*' pointer
                   | '*' type_qualifier_list pointer '''
        pass

    def p_type_qualifier_list(self, p):
        '''type_qualifier_list : type_qualifier
                               | type_qualifier_list type_qualifier '''
        pass

    def p_parameter_type_list(self, p):
        '''parameter_type_list : parameter_list
                               | parameter_list ',' ELLIPSIS '''
        pass

    def p_parameter_list(self, p):
        '''parameter_list : parameter_declaration
                          | parameter_list ',' parameter_declaration '''
        pass

    def p_parameter_declaration(self, p):
        '''parameter_declaration : declaration_specifiers declarator
                                 | declaration_specifiers abstract_declarator
                                 | declaration_specifiers '''
        pass

    def p_identifier_list(self, p):
        '''identifier_list : IDENTIFIER
                           | identifier_list ',' IDENTIFIER '''
        pass

    def p_type_name(self, p):
        '''type_name : specifier_qualifier_list
                     | specifier_qualifier_list abstract_declarator '''
        pass

    def p_abstract_declarator(self, p):
        '''abstract_declarator : pointer
                               | direct_abstract_declarator
                               | pointer direct_abstract_declarator '''
        pass

    def p_direct_abstract_declarator(self, p):
        '''direct_abstract_declarator : '(' abstract_declarator ')'
                                      | '[' ']'
                                      | '[' constant_expression ']'
                                      | direct_abstract_declarator '[' ']'
                                      | direct_abstract_declarator '[' constant_expression ']' 
                                      | '(' ')'
                                      | '(' parameter_type_list ')'
                                      | direct_abstract_declarator '(' ')'
                                      | direct_abstract_declarator '(' parameter_type_list ')' '''
        pass

    def p_initializer(self, p):
        '''initializer : assignment_expression
                       | '(' initializer_list ')'
                       | '{' initializer_list '}' '''
        pass

    def p_initializer_list(self, p):
        '''initializer_list : initializer
                            | initializer_list ',' initializer '''
        pass

    def p_statement(self, p):
        '''statement : labeled_statement
                     | compound_statement
                     | expression_statement
                     | selection_statement
                     | iteration_statement
                     | jump_statement '''
        pass

    def p_labeled_statement(self, p):
        '''labeled_statement : IDENTIFIER ':' statement
                             | CASE constant_expression ':' statement
                             | DEFAULT ':' statement '''
        pass

    def p_compound_statement(self, p):
        '''compound_statement : '{' '}'
                              | '{' statement_list '}'
                              | '{' declaration_list '}'
                              | '{' declaration_list statement_list '}' '''
        pass

    def p_declaration_list(self, p):
        '''declaration_list : declaration
                            | declaration_list declaration '''
        pass

    def p_statement_list(self, p):
        '''statement_list : statement
                          | statement_list statement '''
        pass

    def p_expression_statement(self, p):
        '''expression_statement : ';'
                                | expression ';' '''
        pass

    def p_selection_statement(self, p):
        '''selection_statement : IF '(' expression ')' statement
                               | IF '(' expression ')' statement ELSE statement
                               | SWITCH '(' expression ')' statement ''' 
        pass

    def p_iteration_statement(self, p):
        '''iteration_statement : WHILE '(' expression ')'
                               | DO statement WHILE '(' expression ')' ';'
                               | FOR '(' expression_statement expression_statement ')' statement
                               | FOR '(' expression_statement expression_statement expression ')' statement '''
        pass

    def p_jump_statement(self, p):
        '''jump_statement : GOTO IDENTIFIER ';'
                          | CONTINUE ';'
                          | BREAK ';'
                          | RETURN ';'
                          | RETURN expression ';' '''
        pass

    def p_external_declaration(self, p):
        '''external_declaration : function_definition
                                | declaration '''
        pass

    def p_function_definition(self, p):
        '''function_definition : declaration_specifiers declarator declaration_list compound_statement
                                | declaration_specifiers declarator compound_statement
                                | declarator declaration_list compound_statement
                                | declarator compound_statement '''
        pass

    def p_declaration_specifiers(self, p):
        '''declaration_specifiers : storage_class_specifier
                                  | storage_class_specifier declaration_specifiers 
                                  | type_specifier 
                                  | type_specifier declaration_specifiers 
                                  | type_qualifier 
                                  | type_qualifier declaration_specifiers '''
        pass 

    def p_error(self, p ):
        print(p)
        pass

    def parse(self, data):
        self._parser.parse(data)

if __name__ == "__main__":
    parser = CParser(debug = False)

    data = '''
        typedef struct {
            float test;
            double test2;
        }test;
    '''
    parser.parse(data)