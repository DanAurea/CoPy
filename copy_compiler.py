from front_end.parser.parser_ansi import CANSIParser
from front_end.parser.parser_99 import C99Parser
from preprocessor.c99_preprocessor import C99PreProcessor
from transformer.ctypes_generator import CTypesGenerator

import os

class CoPYCompiler(object):
    '''
    This class represent a compiler that translates C struct
    to Python ctypes structure.

    Comments found inside structures will be kept intact.
    '''
    def __init__(self, output_path):
        self._output_path   = output_path
        self._pre_processor = C99PreProcessor()

    def compile(self, input_path):
        self._pre_processor.process(input_path)

class CoPyANSICompiler(CoPYCompiler):
    '''
    This class represent the C89/C90 compatible compiler that translates C struct
    to Python ctypes structure.

    Comments found inside structures will be kept intact.
    '''

    def __init__(self, output_path):
        super(CoPyANSICompiler, self).__init__(output_path)
        self._parser = CANSIParser()

    def compile(self, input_path):
        super(CoPyANSICompiler, self).compile(input_path)

class CoPy99Compiler(CoPYCompiler):
    '''
    This class represent the C99 compatible compiler that translates C struct
    to Python ctypes structure.

    Comments found inside structures will be kept intact.
    '''

    def __init__(self, output_path):
        super(CoPy99Compiler, self).__init__(output_path)
        self._parser    = C99Parser()
        self._generator = CTypesGenerator()

    def compile(self, input_path):
        super(CoPy99Compiler, self).compile(input_path)
        
        preprocessed_output = self._pre_processor.process(input_path)
        ast                 = self._parser.parse(preprocessed_output)
        generated_code      = self._generator.generate(ast)
        
        output_filepath = os.path.join(self._output_path, f'{os.path.splitext(input_path)[0]}.py')

        os.makedirs(os.path.dirname(output_filepath), exist_ok=True)

        with open(output_filepath, 'wt') as output_file:
            output_file.write(generated_code)

if __name__ == "__main__":
    compiler = CoPy99Compiler("output/")
    compiler.compile("examples/unprocessed.h")