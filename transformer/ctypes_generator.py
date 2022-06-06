import os
import sys
sys.path.append("../")

import ctypes

from front_end.parser.parser_99 import C99Parser
from transformer.python_generator import PythonGenerator

from transformer.common import Endianness

import core.intermediate_representation as ir 

class CTypesGenerator(PythonGenerator):
    ROOT_DIR = os.path.abspath(os.path.join(__file__, os.pardir))
    with open(f'{ROOT_DIR}/template/ctypes/enum.py', 'rt') as template:
        ENUM_TEMPLATE = template.read()

    with open(f'{ROOT_DIR}/template/ctypes/struct.py', 'rt') as template:
        STRUCT_TEMPLATE = template.read()

    with open(f'{ROOT_DIR}/template/ctypes/union.py', 'rt') as template:
        UNION_TEMPLATE = template.read()

    def __init__(self, endianness = Endianness.LITTLE_ENDIAN):
        super(CTypesGenerator, self).__init__()
        self.endianness = endianness

    def generate_enumeration(self, typedef):
        """
        Generate a ctypes like enumeration. 
        
        :param      typedef:  The typedef
        :type       typedef:  { type_description }
        """
        data_type = 'ctypes.c_uint32'

        if typedef.packing == 1:
            data_type = 'ctypes.c_uint8'
        elif typedef.packing == 2:
            data_type = 'ctypes.c_uint16'
        elif typedef.packing == 4:
            data_type = 'ctypes.c_uint32'
        elif typedef.packing == 8:
            data_type = 'ctypes.c_uint64'
        else:
            raise Exception('Incorrect packing value found.')

        class_name = "".join([name.capitalize() for name in typedef.identifier.split('_')])
        base_class = f'''ctypes.{"".join([name.capitalize() for name in self.endianness.name.split('_')])}Structure'''

        python_enum = super(CTypesGenerator, self).generate_enumeration(typedef) + '\n'
        return python_enum + CTypesGenerator.ENUM_TEMPLATE.format(class_name = "CTypes" + class_name, base_class = base_class, 
                                                    data_type = data_type, packing = typedef.packing)

    def generate_struct(self, typedef):
        """
        Generate a ctypes like structure. 
        
        :param      typedef:  The typedef
        :type       typedef:  { type_description }
        """
        class_name = "".join([name.capitalize() for name in typedef.identifier.split('_')])
        base_class = f'''ctypes.{"".join([name.capitalize() for name in self.endianness.name.split('_')])}Structure'''
        fields = []
        nested_class = ''
        
        for declaration in typedef.declaration_list:
            last_spec_qual = declaration.specifier_qualifier_list[-1]
            
            # Handle nested typedefs
            if isinstance(last_spec_qual, ir.Enumeration):
                nested_enum = self.generate_enumeration(last_spec_qual)
            elif isinstance(last_spec_qual, ir.Struct):
                nested_struct = self.generate_struct(last_spec_qual)
            elif isinstance(last_spec_qual, ir.Union):
                nested_union = self.generate_union(last_spec_qual)
            else:
                pass

        return CTypesGenerator.STRUCT_TEMPLATE.format(  nested_class = nested_class, class_name = class_name, base_class = base_class,
                                                        packing = typedef.packing, fields = '\n\t'.join(fields))

    def generate_union(self, typedef):
        """
        Generate a ctypes like union. 
        
        :param      typedef:  The typedef
        :type       typedef:  { type_description }
        """
        class_name = "".join([name.capitalize() for name in typedef.identifier.split('_')])
        base_class = f'''ctypes.{"".join([name.capitalize() for name in self.endianness.name.split('_')])}Union'''
        fields = []

        for declaration in typedef.declaration_list:
            pass

        return CTypesGenerator.UNION_TEMPLATE.format(   class_name = class_name, base_class = base_class, 
                                                        packing = typedef.packing, fields = '\n\t'.join(fields))

    def generate_typedef(self, typedef):
        """
        Generate a ctypes typedef like representation.
        
        :param      typedef:  The typedef
        :type       typedef:  { type_description }
        """
        if isinstance(typedef, ir.Enumeration):
            return self.generate_enumeration(typedef)
        elif isinstance(typedef, ir.Struct):
            return self.generate_struct(typedef)
        elif isinstance(typedef, ir.Union):
            return self.generate_union(typedef)

    def generate(self, ast):
        """
        Parse an AST and construct a Ctypes representation of its content. 
        
        Currently only works for typedef declaration but could be extend afterwards.

        :param      ast:  The ast
        :type       ast:  { type_description }
        """
        generated_tree  = []

        for translation_unit in ast.translation_unit_list:
            if isinstance(translation_unit, ir.Declaration) and translation_unit.is_typedef:
                print(self.generate_typedef(translation_unit.specifier_list[-1]))

if __name__ == '__main__':
    generator = CTypesGenerator() 
    parser = C99Parser(debug = False)

    with open("../output/directive.i", "rt") as include_file:
        data = include_file.read()

    ast = parser.parse(data)

    generator.generate(ast)