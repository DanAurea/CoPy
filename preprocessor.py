class CPreProcessor(object):
    '''
    Pre process include files.
    The pre processor is in charge of macro expansion such as macro function, pragma, include or define.
    '''
    
    def __init__(self):
        self._stdlib_path = "./stdlib/"

    def process(self, input_path):
        pass

if __name__ == "__main__":
    pre_processor = CPreProcessor()

    pre_processor.process("examples/")