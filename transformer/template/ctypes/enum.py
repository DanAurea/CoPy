class {class_name}({base_class}):
    class Value(enum.IntEnum):
{enumerator_list}
    _pack_   = {packing}
    _fields_ = [
                    ('_value', {data_type}),
               ]

    @property
    def value(self):
        return self.Value(self._value)