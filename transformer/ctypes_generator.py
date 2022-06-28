import os
import sys
sys.path.append("../")

import ctypes
import textwrap

from front_end.parser.parser_99 import C99Parser
from front_end.parser.parser_gnu99 import GNU99Parser
from transformer.generator import Generator
from transformer.python_generator import PythonGenerator

from transformer.common import Endianness

import core.intermediate_representation as ir 

class CTypesGenerator(Generator):
    ROOT_DIR = os.path.abspath(os.path.join(__file__, os.pardir))
    with open(f'{ROOT_DIR}/template/ctypes/enum.py', 'rt') as template:
        ENUM_TEMPLATE = template.read()

    with open(f'{ROOT_DIR}/template/ctypes/struct.py', 'rt') as template:
        STRUCT_TEMPLATE = template.read()

    with open(f'{ROOT_DIR}/template/ctypes/union.py', 'rt') as template:
        UNION_TEMPLATE = template.read()

    def __init__(self, tab_size = 4, endianness = Endianness.LITTLE_ENDIAN):
        super(CTypesGenerator, self).__init__()
        self._tab_size   = tab_size
        self.endianness = endianness
        self._enum_packing_map =    {
                                        1: 'ctypes.c_uint8',
                                        2: 'ctypes.c_uint16',
                                        4: 'ctypes.c_uint32',
                                        8: 'ctypes.c_uint64',
                                    }
        self._python_generator = PythonGenerator()

    def generate_enumeration(self, typedef):
        """
        Generate a ctypes like enumeration. 
        
        :param      typedef:  The typedef
        :type       typedef:  { type_description }
        """
        if typedef.packing in self._enum_packing_map:
            data_type = self._enum_packing_map[typedef.packing]
        else:
            raise Exception('Incorrect packing value found.')

        class_name = ''.join([name.capitalize() for name in typedef.identifier.split('_')])
        base_class = f'''ctypes.{''.join([name.capitalize() for name in self.endianness.name.split('_')])}Structure'''

        enumerator_list = [f'{name} = {value}' for name, value in typedef.enumerator_list]

        return CTypesGenerator.ENUM_TEMPLATE.format(class_name = class_name, base_class = base_class, 
                                                    data_type = data_type, packing = typedef.packing, enumerator_list = textwrap.indent(',\n'.join(enumerator_list), prefix = ' ' * 2 * self._tab_size) )

    def _generate_type_declaration(self, declaration):
        """
        Generate a ctypes like declaration.
        
        :param      declaration:  The declaration
        :type       declaration:  { type_description }
        """
        last_spec_qual = declaration.specifier_qualifier_list[-1]
        
        nested_class     = None
        field = f''

        # Handle nested typedefs
        if isinstance(last_spec_qual, ir.Enumeration):
            nested_class = self.generate_enumeration(last_spec_qual)
        elif isinstance(last_spec_qual, ir.Struct):
            nested_class = self.generate_struct(last_spec_qual)
            field = f'''('{declaration.struct_declarator_list[0]}', {''.join([name.capitalize() for name in last_spec_qual.identifier.split('_')])})'''
        elif isinstance(last_spec_qual, ir.Union):
            nested_class = self.generate_union(last_spec_qual)
        else:
            decl_name = ''
            type_decl = ''
            bitfield  = ''
            is_signed = 'signed' in declaration.specifier_qualifier_list or not 'unsigned' in declaration.specifier_qualifier_list

            for specifier_qualifier in declaration.specifier_qualifier_list:
                if specifier_qualifier not in ['signed', 'unsigned', 'const', 'char', 'short', 'int', 'long', 'float', 'double', 'void', 'size_t', 'ssize_t']:
                    type_decl = ''.join([name.capitalize() for name in specifier_qualifier.split('_')])
                elif specifier_qualifier == 'char':
                    type_decl = 'ctypes.c_int8' if is_signed else 'ctypes.c_uint8'
                elif specifier_qualifier == 'short':
                    type_decl = 'ctypes.c_int16' if is_signed else 'ctypes.c_uint16'
                elif specifier_qualifier == 'int':
                    type_decl = 'ctypes.c_int32' if is_signed else 'ctypes.c_uint32'
                elif specifier_qualifier == 'long':
                    type_decl = 'ctypes.c_int64' if is_signed else 'ctypes.c_uint64'
                elif specifier_qualifier == 'float':
                    type_decl = 'ctypes.c_float'
                elif specifier_qualifier == 'double':
                    type_decl = 'ctypes.c_double'
                elif specifier_qualifier == 'void':
                    type_decl = 'ctypes.c_void'
                elif specifier_qualifier == 'size_t':
                    type_decl = 'ctypes.c_size_t'
                elif specifier_qualifier == 'ssize_t':
                    type_decl = 'ctypes.c_ssize_t'

            for struct_declarator in declaration.struct_declarator_list:
                declarator_type = type(struct_declarator.declarator)

                if declarator_type is str:
                    decl_name = struct_declarator.declarator
    
                    if struct_declarator.bitfield:
                        bitfield = struct_declarator.bitfield
                elif declarator_type is ir.ArrayDeclarator:
                    array_length_list = [struct_declarator.declarator.length]
                    direct_declarator = struct_declarator.declarator.direct_declarator

                    # Handle multi dimensional array
                    while type(direct_declarator) is ir.ArrayDeclarator:
                        array_length_list.append(direct_declarator.length)
                        direct_declarator = direct_declarator.direct_declarator

                    decl_name = direct_declarator
                    type_decl = f'''{type_decl} * {' * '.join([str(length) for length in array_length_list])}'''
                elif declarator_type is ir.Pointer:
                    indirection_level = 1 
                    reference = struct_declarator.declarator.reference
                    direct_declarator = struct_declarator.declarator.direct_declarator
                    
                    # Handle multi indirection layer
                    while reference:
                        indirection_level += 1
                        reference = reference.reference

                    decl_name = direct_declarator
                    type_decl = f'''{'ctypes.POINTER(' * indirection_level}{type_decl}{')'*indirection_level}'''

            field = f'''('{decl_name}', {type_decl}{", " if bitfield else ''}{bitfield})'''

        return nested_class, field

    def generate_struct(self, typedef):
        """
        Generate a ctypes like structure. 
        
        :param      typedef:  The typedef
        :type       typedef:  { type_description }
        """
        class_name = ''.join([name.capitalize() for name in typedef.identifier.split('_')])
        base_class = f'''ctypes.{''.join([name.capitalize() for name in self.endianness.name.split('_')])}Structure'''

        nested_class_list = []
        field_list        = []

        for declaration in typedef.declaration_list:
            nested_class, field = self._generate_type_declaration(declaration)
            field_list.append(field)
            if nested_class:
                nested_class_list.append(nested_class)

        return CTypesGenerator.STRUCT_TEMPLATE.format(  nested_class = textwrap.indent('\n'.join(nested_class_list), prefix=' ' * self._tab_size), class_name = class_name, base_class = base_class,
                                                        packing = typedef.packing, fields = textwrap.indent(',\n'.join(field_list), prefix = ' ' * (5 * self._tab_size) ) + ',')

    def generate_union(self, typedef):
        """
        Generate a ctypes like union. 
        
        :param      typedef:  The typedef
        :type       typedef:  { type_description }
        """
        class_name = ''.join([name.capitalize() for name in typedef.identifier.split('_')])
        base_class = f'''ctypes.{''.join([name.capitalize() for name in self.endianness.name.split('_')])}Union'''
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
        output = f'''import ctypes\nimport enum\n\n'''
        for translation_unit in ast.translation_unit_list:
            if isinstance(translation_unit, ir.Declaration) and translation_unit.is_typedef:
                output += f'''{self.generate_typedef(translation_unit.specifier_list[-1])}\n'''

        return output

if __name__ == '__main__':
    generator = CTypesGenerator(endianness = Endianness.LITTLE_ENDIAN) 
    parser = GNU99Parser(debug = False)

    with open("../examples/elf.i", "rt") as include_file:
        data = include_file.read()

    ast = parser.parse(data)
    
    with open("../output/elf.py", "wt") as py_directive_file:
        py_directive_file.write(generator.generate(ast))