class Struct(object):
    """
    """

    def __init__(self, struct_name, declaration_list, packing = 4):
        self.struct_name      = struct_name
        self.declaration_list = declaration_list
        self.packing          = packing

class Union(object):
    """
    """

    def __init__(self, union_name, declaration_list, packing = 4):
        self.union_name       = union_name
        self.declaration_list = declaration_list
        self.packing          = packing

class Declaration(object):
    """
    """
    
    def __init__(self, type_specifier, identifier, array_length = 1, bitfield = None):
        self.type_specifier = type_specifier
        self.identifier     = identifier
        self.array_length   = array_length
        self.bitfield       = bitfield

class Enumeration(object):

    def __init__(self, enum_name, enumerator_list):
        self.enum_name       = enum_name
        self.enumerator_list = enumerator_list

class Function(object):
    
    def __init__(self):
        pass