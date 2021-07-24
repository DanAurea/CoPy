import re
import grammar

class Lexer(object):
    """
    Produce a token list from source code.
    """

    def __init__(self):
        self.token_re = self._compile_token_re()

    def _compile_token_re(self):
        """
        Initialize grammar rules and compiles it with re
        module, this will save processing time.
        """
        token_list_re = {}
        for rule in grammar.CToken:
            token_list_re[rule.name] = re.compile(rule.value) 

        print(token_list_re)
        return token_list_re

    def scan(self):
        pass

    def parse(self, file):
        pass

if __name__ == "__main__":
    lexer = Lexer()