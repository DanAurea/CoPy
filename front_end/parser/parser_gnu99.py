import sys

sys.path.append('../../')

from core.utils import debug_production
from front_end.lexer.lexer_gnu99 import GNU99Lexer 
from front_end.parser.parser_99 import C99Parser 
from preprocessor.gnu99_preprocessor import PreProcessorFlags 

import core.intermediate_representation as ir

class LineMarker(object):

    def __init__(self, linenum, filename, flag_list = []):
        self.linenum   = linenum
        self.filename  = filename
        self.flag_list = flag_list

    def __repr__(self):
        s = f'''Line: {self.linenum} Filename: {self.filename} Flags: {[PreProcessorFlags(flag) for flag in  self.flag_list]}'''
        return s

class Attribute(object):

    def __init__(self, name, arg_list = []):
        self.name     = name
        self.arg_list = arg_list

    def __repr__(self):
        s = f'''Attribute name: {self.name}\nArgument list: {self.arg_list}'''
        return s

class GNU99Parser(C99Parser):
    """
    Produce a parser that create an AST from C source/header files
    and will provide a compatible interface to Python ctypes library.
    """
    
    # Because we are inheriting a parser we need to explicitly set starting symbol
    start = 'translation_unit'

    def __init__(self, lexer = None, debug = None, **kwargs):
        super(GNU99Parser, self).__init__(GNU99Lexer(), debug, **kwargs)

    def _apply_attribute_list(self, ir_object, attribute_list):
        '''
        Apply all attribute to the IR object.
        '''        
        # TODO: Check if ambiguous attributes (packed with aligned for instance)

        # TODO: Callback function and map might be preferable instead of if/else statements.
        for attribute in attribute_list:
            if attribute.name == "packed":
                ir_object.packing = 1
            elif attribute.name == "aligned":
                ir_object.packing = attribute.arg_list[0]

    def p_external_declaration_linemarker(self, p):
        '''external_declaration : linemarker
        '''
        p[0] = p[1]

    @debug_production
    def p_linemarker(self, p):
        '''linemarker : '#' CONSTANT STRING_LITERAL flag_list
        '''
        linenum   = p[2]
        filename  = p[3]
        flag_list = p[4]
        
        # TODO: Update parser state using the linemarker content
        p[0] = LineMarker(linenum, filename, flag_list)

    def p_flag_list(self, p):
        '''flag_list : 
                     | CONSTANT
                     | flag_list CONSTANT
        '''
        p[0] = []
        if len(p) == 2:
            p[0].append(p[1])
        elif len(p) == 3:
            p[0] = p[1]
            p[0].append(p[2])

    @debug_production
    def p_enum_specifier_former_attribute(self, p):
        '''enum_specifier : ENUM attribute_specifier_list '{' enumerator_list '}'
                          | ENUM attribute_specifier_list '{' enumerator_list  ',' '}' '''
        attribute_specifier_list = p[2]
        p.slice.pop(2)
        self.p_enum_specifier(p)
        self._apply_attribute_list(p[0], attribute_specifier_list)

    @debug_production
    def p_enum_specifier2_former_attribute(self, p):
        '''enum_specifier : ENUM attribute_specifier_list IDENTIFIER '{' enumerator_list '}'
                          | ENUM attribute_specifier_list IDENTIFIER '{' enumerator_list  ',' '}' '''
        # To avoid code duplication, attribute specifier list is removed from production rule and remaining production rule is parsed by C99 parser.
        attribute_specifier_list = p[2]
        p.slice.pop(2)
        self.p_enum_specifier2(p)
        self._apply_attribute_list(p[0], attribute_specifier_list)
    
    @debug_production
    def p_enum_specifier3_former_attribute(self, p):
        '''enum_specifier : ENUM attribute_specifier_list IDENTIFIER '''
        # To avoid code duplication, attribute specifier list is removed from production rule and remaining production rule is parsed by C99 parser.
        attribute_specifier_list = p[2]
        p.slice.pop(2)
        self.p_enum_specifier3(p)
        self._apply_attribute_list(p[0], attribute_specifier_list)

    @debug_production
    def p_enum_specifier_later_attribute(self, p):
        '''enum_specifier : ENUM '{' enumerator_list '}' attribute_specifier_list'''
        attribute_specifier_list = p[5]
        p.slice.pop()
        self.p_enum_specifier(p)
        self._apply_attribute_list(p[0], attribute_specifier_list)

    @debug_production
    def p_enum_specifier_later_attribute2(self, p):
        '''enum_specifier : ENUM '{' enumerator_list  ',' '}' attribute_specifier_list'''
        attribute_specifier_list = p[6]
        p.slice.pop()
        self.p_enum_specifier(p)
        self._apply_attribute_list(p[0], attribute_specifier_list)

    @debug_production
    def p_enum_specifier2_later_attribute(self, p):
        '''enum_specifier : ENUM IDENTIFIER '{' enumerator_list '}' attribute_specifier_list'''
        # To avoid code duplication, attribute specifier list is removed from production rule and remaining production rule is parsed by C99 parser.
        attribute_specifier_list = p[6]
        p.slice.pop()
        self.p_enum_specifier2(p)
        self._apply_attribute_list(p[0], attribute_specifier_list)    

    @debug_production
    def p_enum_specifier2_later_attribute2(self, p):
        '''enum_specifier : ENUM IDENTIFIER '{' enumerator_list  ',' '}' attribute_specifier_list'''
        # To avoid code duplication, attribute specifier list is removed from production rule and remaining production rule is parsed by C99 parser.
        attribute_specifier_list = p[7]
        p.slice.pop()
        self.p_enum_specifier2(p)
        self._apply_attribute_list(p[0], attribute_specifier_list)

    @debug_production
    def p_struct_or_union_specifier_former_attribute(self, p):
        '''struct_or_union_specifier : struct_or_union attribute_specifier_list '{' struct_declaration_list '}'
                                     | struct_or_union attribute_specifier_list IDENTIFIER 
                                     | struct_or_union attribute_specifier_list IDENTIFIER '{' struct_declaration_list '}'
                                     '''
        # To avoid code duplication, attribute specifier list is removed from production rule and remaining production rule is parsed by C99 parser.
        attribute_specifier_list = p[2]
        p.slice.pop(2)
        self.p_struct_or_union_specifier(p)
        self._apply_attribute_list(p[0], attribute_specifier_list)

    @debug_production
    def p_struct_or_union_specifier_later_attribute(self, p):
        '''struct_or_union_specifier : struct_or_union '{' struct_declaration_list '}' attribute_specifier_list
                                     '''
        # To avoid code duplication, attribute specifier list is removed from production rule and remaining production rule is parsed by C99 parser.
        attribute_specifier_list = p[5]
        p.slice.pop()
        self.p_struct_or_union_specifier(p)
        self._apply_attribute_list(p[0], attribute_specifier_list)    

    @debug_production
    def p_struct_or_union_specifier_later_attribute2(self, p):
        '''struct_or_union_specifier : struct_or_union IDENTIFIER '{' struct_declaration_list '}' attribute_specifier_list 
                                     '''
        # To avoid code duplication, attribute specifier list is removed from production rule and remaining production rule is parsed by C99 parser.
        attribute_specifier_list = p[6]
        p.slice.pop()
        self.p_struct_or_union_specifier(p)
        self._apply_attribute_list(p[0], attribute_specifier_list)

    def p_attribute_specifier_list(self, p):
        '''
        attribute_specifier_list : attribute_specifier
                                 | attribute_specifier_list attribute_specifier
        '''
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = p[1]
            p[0].extend(p[2])

    def p_attribute_specifier(self, p):
        '''
        attribute_specifier : __ATTRIBUTE__ '(' '(' attribute_list ')' ')'
        '''
        p[0] = p[4]
    
    def p_attribute_list(self, p):
        '''
        attribute_list : 
                       | attribute
                       | attribute_list ',' 
                       | attribute_list ',' attribute 
        '''
        p[0] = []

        if len(p) == 2:
            p[0] = [p[1]]
        elif len(p) == 3:
            p[0] = p[1]
        elif len(p) == 4:
            p[0] = p[1]
            p[0].append(p[3])
    
    def p_attribute(self, p ):
        '''
        attribute : attribute_token
                  | attribute_token '(' attribute_argument_list ')'
        '''
        attribute = Attribute(p[1])

        if len(p) == 5:
            attribute.arg_list = p[3]

        p[0] = attribute

    def p_attribute_argument_list(self, p):
        '''
        attribute_argument_list : attribute_argument
                                | attribute_argument_list ',' attribute_argument
        '''
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = p[1]
            p[0].append(p[3])

    def p_attribute_argument(self, p):
        '''
        attribute_argument : assignment_expression
        '''
        p[0] = p[1]

    def p_attribute_token(self, p):
        '''
        attribute_token : enumerator_attribute
                        | function_attribute
                        | label_attribute
                        | type_attribute
                        | statement_attribute
        '''
        p[0] = p[1]

    def p_enumerator_attribute(self, p):
        '''
        enumerator_attribute : DEPRECATED
                             | __DEPRECATED__
                             | UNAVAILABLE
                             | __UNAVAILABLE__
        '''
        p[0] = p[1]
    
    def p_function_attribute(self, p):
        '''
        function_attribute : ACCESS
                           | __ACCESS__
                           | UNAVAILABLE
                           | __UNAVAILABLE__
        '''
        p[0] = p[1]

    def p_label_attribute(self, p):
        '''
        label_attribute : COLD
                        | __COLD__
                        | HOT
                        | __HOT__
                        | UNUSED
                        | __UNUSED__
        '''
        p[0] = p[1]
    
    def p_statement_attribute(self, p):
        '''
        statement_attribute : FALLTHROUGH
                            | __FALLTHROUGH__
        '''
        p[0] = p[1]

    def p_type_attribute(self, p):
        '''
        type_attribute : ALIGNED
                       | __ALIGNED__
                       | ALLOC_SIZE
                       | __ALLOC_SIZE__
                       | COPY
                       | __COPY__
                       | DEPRECATED
                       | __DEPRECATED__
                       | DESIGNATED_INIT
                       | __DESIGNATED_INIT__
                       | MAY_ALIAS
                       | __MAY_ALIAS__
                       | MODE
                       | __MODE__
                       | OBJC_ROOT_CLASS
                       | __OBJC_ROOT_CLASS__
                       | PACKED
                       | __PACKED__
                       | SCALAR_STORAGE_ORDER
                       | __SCALAR_STORAGE_ORDER__
                       | TRANSPARENT_UNION
                       | __TRANSPARENT_UNION__
                       | UNAVAILABLE
                       | __UNAVAILABLE__
                       | UNUSED
                       | __UNUSED__
                       | VECTOR_SIZE
                       | __VECTOR_SIZE__
                       | VISIBILITY
                       | __VISIBILITY__
                       | WARN_IF_NOT_ALIGNED
                       | __WARN_IF_NOT_ALIGNED__
        '''
        p[0] = p[1]

if __name__ == "__main__":
    parser = GNU99Parser(debug = False)

    with open("../../examples/elf.i", "rt") as include_file:
        data = include_file.read()

    print(parser.parse(data))