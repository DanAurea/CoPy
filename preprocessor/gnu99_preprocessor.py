import os
import sys
sys.path.append("../")

from enum import IntEnum
from preprocessor.c99_preprocessor import C99PreProcessor

class PreProcessorFlags(IntEnum):
    START_FILE     = 1
    RETURN_TO_FILE = 2
    SYSTEM_HEADER  = 3
    EXTERN_C       = 4

class GNU99PreProcessor(C99PreProcessor):
    
    def _create_line_control(self, filename, flag_list = []):
        return f'#{self._lexer._lexer.lineno} "{filename}" {" ".join([str(flag.value) for flag in flag_list])}\n'

    def include(self, header_name):
        """
        Include a file.
        
        :param      header_name:  The header name
        :type       header_name:  str
        """

        line_control_start_flag = [PreProcessorFlags.START_FILE]

        if header_name[0] == '<' and header_name[-1] == '>':
            line_control_start_flag.append(PreProcessorFlags.SYSTEM_HEADER)

        include_content = self._create_line_control(header_name[1:-1], line_control_start_flag)
        include_content += super(GNU99PreProcessor, self).include(header_name)
        include_content += self._create_line_control(os.path.basename(self._current_file), [PreProcessorFlags.RETURN_TO_FILE])

        return include_content
    
    # TODO: Add missing line control. GNU preprocessor adds a line control when returning/starting to preprocess of the current file.
    # TODO: Add missing line control when extern "C" is encountered.

if __name__ == "__main__":
    pre_processor = GNU99PreProcessor(debug = False, keep_comment = False)

    preprocessed_code = pre_processor.process("../examples/digraph_trigraph/directive.c")

    with open("../output/directive.i" , "wt") as preprocessed_file:
        preprocessed_file.write(preprocessed_code)