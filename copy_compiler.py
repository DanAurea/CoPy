from preprocessor import CPreProcessor
from parser_ansi import CANSIParser
from parser_99 import C99Parser

class CoPYCompiler(object):
    '''
    This class represent a compiler that translates C struct
    to Python ctypes structure.

    Comments found inside structures will be kept intact.
    '''
    def __init__(self):
        self._pre_processor = CPreProcessor()

    def compile(self, input_path):
        self._pre_processor.process(input_path)

class CoPyANSICompiler(CoPYCompiler):
    '''
    This class represent the C89/C90 compatible compiler that translates C struct
    to Python ctypes structure.

    Comments found inside structures will be kept intact.
    '''

    def __init__(self):
        super(CoPyANSICompiler, self).__init__()
        self._parser = CANSIParser()

    def compile(self, input_path):
        super(CoPyANSICompiler, self).compile(input_path)

class CoPy99Compiler(CoPYCompiler):
    '''
    This class represent the C99 compatible compiler that translates C struct
    to Python ctypes structure.

    Comments found inside structures will be kept intact.
    '''

    def __init__(self):
        super(CoPy99Compiler, self).__init__()
        self._parser = C99Parser()

    def compile(self, input_path):
        super(CoPy99Compiler, self).compile(input_path)

if __name__ == "__main__":
    compiler = CoPy99Compiler()
    compiler.compile("examples/")