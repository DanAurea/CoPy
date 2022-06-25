import sys

sys.path.append('../../')

from core.utils import debug_production
from front_end.lexer.lexer_gnu99 import GNU99Lexer 
from front_end.parser.parser_99 import C99Parser 

import core.intermediate_representation as ir

class GNU99Parser(C99Parser):
    """
    Produce a parser that create an AST from C source/header files
    and will provide a compatible interface to Python ctypes library.
    """
    
    # Because we are inheriting a parser we need to explicitly set starting symbol
    start = 'translation_unit'

    def __init__(self, lexer = None, debug = None, **kwargs):
        super(GNU99Parser, self).__init__(GNU99Lexer(), debug, **kwargs)

    def p_attribute_specifier_list(self, p):
        '''
        attribute_specifier_list : attribute_specifier
                                 | attribute_specifier attribute_specifier_list
        '''
        pass# 
    
    def p_attribute_specifier(self, p):
        '''
        attribute_specifier : __ATTRIBUTE__ '(' '(' attribute_list ')' ')'
        '''
        pass
    
    def p_attribute_list(self, p):
        '''
        attribute_list : attribute
                       | attribute ',' attribute_list
        '''
        pass
    
    def p_attribute(self, p):
        '''
        attribute : 
                  | enumerator_attribute
                  | function_attribute
                  | label_attribute
                  | type_attribute
                  | statement_attribute
        '''
        pass

    def p_enumerator_attribute(self, p):
        '''
        enumerator_attribute : DEPRECATED
                             | __DEPRECATED__
                             | UNAVAILABLE
                             | __UNAVAILABLE__
        '''
        pass
    
    def p_function_attribute(self, p):
        '''
        function_attribute : ACCESS
                           | __ACCESS__
                           | UNAVAILABLE
                           | __UNAVAILABLE__
        '''
        pass

    def p_label_attribute(self, p):
        '''
        label_attribute : COLD
                        | __COLD__
                        | HOT
                        | __HOT__
                        | UNUSED
                        | __UNUSED__
        '''
        pass
    
    def p_statement_attribute(self, p):
        '''
        statement_attribute : FALLTHROUGH
                            | __FALLTHROUGH__
        '''
        pass

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
        pass

if __name__ == "__main__":
    parser = GNU99Parser(debug = False)

    with open("../../examples/elf.i", "rt") as include_file:
        data = include_file.read()

    print(parser.parse(data))