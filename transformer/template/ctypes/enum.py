class {class_name}({base_class}):
    _pack_ = {packing}
    _fields_ = [
                    ('_value', {data_type}),
               ]

    @property
    def value(self):
        return {class_name}(self._value)