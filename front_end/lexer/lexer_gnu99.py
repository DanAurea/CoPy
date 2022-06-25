import sys
sys.path.append('../../')

from front_end.lexer.lexer_99 import C99Lexer

class GNU99Lexer(C99Lexer):
    """
    Produce a token list from a C source code.
    """
    attribute_list =    [  
                            "access", "aligned", "alloc_size", "alloc_size", "cold", "copy", 
                            "deprecated", "designated_init", "fallthrough", "hot", "may_alias", 
                            "mode", "objc_root_class", "packed", "scalar_storage_order", 
                            "transparent_union", "unavailable", "unused", "vector_size", 
                            "visibility", "warn_if_not_aligned"
                        ]

    # Define reserved keyword for GNU 99 extension
    reserved_subset =   {
                            "__attribute__": "__ATTRIBUTE__",
                            **{f'''__{attribute}__''' : f'''__{attribute.upper()}__''' for attribute in attribute_list}, 
                            **{attribute : f'''{attribute.upper()}''' for attribute in attribute_list}
                        }

    # Extends tokens and reserved values
    reserved = {**C99Lexer.reserved, **reserved_subset}
    C99Lexer.tokens += list(reserved_subset.values())

if __name__ == "__main__":
    lexer = GNU99Lexer()

    with open("../../examples/elf.i", "rt") as include_file:
        data = include_file.read()

    token_list = lexer.tokenize(data)
    print(token_list)