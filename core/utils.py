from functools import wraps

def debug_production(func):
    """
    Debug print for production rules
    
    :param      func:  The function
    :type       func:  { type_description }
    """
    @wraps(func)
    def inner(self, p):
        # If func is not called then production rules won't return anything.
        func(self, p)
        if self._debug:
            print(f'''Production rule: {func.__name__} produced {p[1:]} ''')
            print("-" * 80)

    inner.co_firstlineno = func.__code__.co_firstlineno
    return inner