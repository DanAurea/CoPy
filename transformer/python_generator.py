import os
import sys

sys.path.append('../')

from transformer.generator import Generator

class PythonGenerator(Generator):
    """
    This class describes a python generator using AST
    generated previously by a Parser.
    """
    ROOT_DIR = os.path.abspath(os.path.join(__file__, os.pardir))
    with open(f'{ROOT_DIR}/template/python/enum.py', 'rt') as template:
        ENUM_TEMPLATE = template.read()

    def __init__(self):
        pass

    def generate_enumeration(self, typedef):
        """
        Generate a Python like enumeration.
        
        :param      typedef:  The typedef
        :type       typedef:  { type_description }
        """
        enum_name = "".join([name.capitalize() for name in typedef.identifier.split('_')])
        enumerator_list = f'''\n{' ' * 4}'''.join([f'''{enumerator.name.upper()} = 0x{format(enumerator.value,'02x').upper()}''' for enumerator in typedef.enumerator_list])

        return PythonGenerator.ENUM_TEMPLATE.format(class_name = enum_name, enumerator_list = enumerator_list)