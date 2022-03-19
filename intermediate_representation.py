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

class StructDeclaration(object):
    """
    specifier_qualifier_list struct_declarator_list
    """
    def __init__(self, specifier_qualifier_list, struct_declarator_list):
        self.specifier_qualifier_list = specifier_qualifier_list
        self.struct_declarator_list   = struct_declarator_list

    def __repr__(self):
        new_line = '\n' 
        s = f'''
                {" ".join(self.specifier_qualifier_list)} {" ".join(self.struct_declarator_list)};
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