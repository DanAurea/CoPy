class SourceFile(object):

    def __init__(self):
        self.translation_unit_list = []

    def append(self, translation_unit):
        self.translation_unit_list.append(translation_unit)

    # TODO: Uncomment once every translation unit will be handled
    def __repr__(self):
        s = f'''{(self.translation_unit_list)}'''
        return s

class Struct(object):
    """
    """

    def __init__(self, declaration_list = [], packing = 4):
        self.declaration_list = declaration_list
        self.packing          = packing

    def is_incomplete(self):
        return not len(self.declaration_list)

    def __repr__(self):
        s = f'''
                Declaration list: {self.declaration_list} 
                Packing: {self.packing} 
            '''
        return s

class Union(object):
    """
    """

    def __init__(self, declaration_list = [], packing = 4):
        self.declaration_list = declaration_list
        self.packing          = packing

    def is_incomplete(self):
        return not len(self.declaration_list)

    def __repr__(self):
        s = f'''
                Declaration list: {self.declaration_list} 
                Packing: {self.packing} 
            '''
        return s

class StructDeclaration(object):
    """
    """

    def __init__(self, specifier_qualifier_list, struct_declarator_list):
        self.specifier_qualifier_list = specifier_qualifier_list
        self.struct_declarator_list   = struct_declarator_list

    def __repr__(self):
        new_line = '\n' 
        s = f'''
                {" ".join(self.specifier_qualifier_list)} {self.struct_declarator_list[:]};
            '''
        return s

class StructDeclarator(object):
    """
    """
    def __init__(self, declarator = '', bitfield = None):
        self.declarator = declarator
        self.bitfield = bitfield

    def __repr__(self):
        return f'''{self.declarator}{f':{self.bitfield}' if self.bitfield else ''}'''

class Enumeration(object):

    def __init__(self, enumerator_list = [], packing = 4):
        self.enumerator_list = enumerator_list
        self.packing         = packing

    def is_incomplete(self):
        return not len(self.enumerator_list)

    def __repr__(self):
        s = f'''Enumerator list: {self.enumerator_list}
                Packing : {self.packing}'''
        return s

class Function(object):
    
    def __init__(self):
        pass

class Macro(object):

    def __init__(self, name, replacement = '', arg_list = [], variadic = False, callback = None):
        self.name              = name
        self.replacement       = replacement
        self.arg_list          = arg_list
        self.variadic          = variadic
        self.callback          = callback
        self.has_been_expanded = False

    def expand(self, arg_list = []):
        """
        Expand a macro. 

        :param      arg_list:  The argument list
        :type       arg_list:  { type_description }
        """
        replacement = self.replacement

        if arg_list:
            if not self.variadic and len(arg_list) != len(self.arg_list):
                raise Exception("Number of arguments not matching with expected list length.")

            if self.callback:
                raise Exception("Callback macro can't be called with user provided argument list.")

            for label, arg in zip(self.arg_list, arg_list): 
                replacement = replacement.replace(label, arg)

        elif self.callback:
            callback_return = self.callback(*self.arg_list)
            if type(callback_return) == str:
                replacement = f'"{callback_return}"'
            else:
                replacement = str(callback_return)
        elif self.arg_list and not arg_list:
            raise Exception("Function like macro needs argument list.")

        self.has_been_expanded = True

        return replacement

    def __repr__(self):
        s = f'''
                Macro name: {self.name}
                Replacement text: {self.replacement}
                Argument list : {self.arg_list}
                Variadic : {self.variadic}'''
        return s

class Declaration(object):
    
    def __init__(self):
        self.init_declarator_list = []
        self.specifier_list       = []
        
        self.is_auto              = False
        self.is_const             = False
        self.is_extern            = False
        self.is_inline            = False
        self.is_register          = False
        self.is_restrict          = False
        self.is_static            = False
        self.is_typedef           = False
        self.is_volatile          = False

    def add_specifier(self, specifier):
        """
        Adds a specifier to declaration and update
        internal member depending on specifier value.
        
        :param      specifier:  The specifier
        :type       specifier:  str
        """
        if specifier == None:
            return

        if "auto" == specifier:
            self.is_auto     = True
        
        if "const" == specifier:
            self.is_const    = True
        
        if "extern" == specifier:
            self.is_extern   = True
        
        if "inline" == specifier:
            self.is_inline   = True
        
        if "register" == specifier:
            self.is_register = True
        
        if "restrict" == specifier:
            self.is_restrict = True
        
        if "static" == specifier:
            self.is_static   = True
        
        if "typedef" == specifier:
            self.is_typedef  = True

        if "volatile" == specifier:
            self.is_volatile = True

        self.specifier_list.append(specifier)

    def add_specifier_list(self, specifier_list):
        """
        Adds a specifier to declaration and update
        internal member depending on specifier value.
        
        :param      specifier:  The specifier
        :type       specifier:  str
        """
        for specifier in specifier_list:
            self.add_specifier(specifier)

    def add_init_declarator(self, init_declarator):
        """
        Adds an initialized declarator.
        
        :param      init_declarator:  The initialized declarator
        :type       init_declarator:  str
        """
        self.init_declarator_list.append(init_declarator)

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        s = f'''
            {self.specifier_list} {self.init_declarator_list};
            '''
        return s