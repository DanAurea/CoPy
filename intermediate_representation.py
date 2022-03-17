class Struct(object):
    """
    """

    def __init__(self, identifier, declaration_list, packing = 4):
        self.identifier      = identifier
        self.declaration_list = declaration_list
        self.packing          = packing

    def __repr__(self):
        s = f'''
                Struct name: {self.identifier} 
                Declaration list: {self.declaration_list} 
                Packing: {self.packing} 
            '''
        return s

class Union(object):
    """
    """

    def __init__(self, identifier, declaration_list, packing = 4):
        self.identifier       = identifier
        self.declaration_list = declaration_list
        self.packing          = packing

    def __repr__(self):
        s = f'''
                Union name: {self.union_name} 
                Declaration list: {self.declaration_list} 
                Packing: {self.packing} 
            '''
        return s

class Declaration(object):
    """
    """
    
    def __init__(self, type_specifier, identifier, array_length = 1, bitfield = None):
        self.type_specifier = type_specifier
        self.identifier     = identifier
        self.array_length   = array_length
        self.bitfield       = bitfield

    def __repr__(self):
        s = f'''
                {self.type_specifier} {self.identifier}[{self.array_length}]:{self.bitfield}
            '''
        return s

class Enumeration(object):

    def __init__(self, identifier = None, enumerator_list = None, packing = 4):
        self.identifier = identifier
        self.enumerator_list = enumerator_list
        self.packing          = packing

    def __repr__(self):
        s = f'''
                Enumeration name: {self.identifier}
                Enumerator list: {self.enumerator_list}
                Packing : {self.packing}'''
        return s

class Function(object):
    
    def __init__(self):
        pass