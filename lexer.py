import re
import grammar

class Lexer(object):
    """
    Produce a token list from source code.
    """

    def __init__(self):
        self.grammar_rules = self._compile_grammar()

    def _compile_grammar(self):
        """
        Initialize grammar rules and compiles it with re
        module, this will save processing time.
        """
        grammar_rules = {}
        for rule in grammar.Grammar:
            grammar_rules[rule.name] = re.compile(rule.value) 

        return grammar_rules

    def tokenize(self):
        pass

if __name__ == "__main__":
    lexer = Lexer()