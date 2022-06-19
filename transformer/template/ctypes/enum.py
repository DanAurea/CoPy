class {class_name}({base_class}):
    _pack_   = {packing}
    _fields_ = [
                    ('_value', {data_type}),
               ]

    @property
    def value(self):
        return {python_enum_name}(self._value)