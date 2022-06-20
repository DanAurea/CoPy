import ctypes
import enum

class ExampleT(enum.IntEnum):
    ENUM_1 = 0x02
    ENUM_2 = 0x03
    ENUM_3 = 0x04
    ENUM_4 = 0x05
    ENUM_5 = 0x3D
    ENUM_6 = 0x3E

class CTypesExampleT(ctypes.LittleEndianStructure):
    _pack_   = 4
    _fields_ = [
                    ('_value', ctypes.c_uint32),
               ]

    @property
    def value(self):
        return ExampleT(self._value)
class AnotherstructT(ctypes.LittleEndianStructure):

    _pack_   = 4
    _fields_ = [
                    ('p', ctypes.c_int32),
                ]
class StructT(ctypes.LittleEndianStructure):
    class NestedstructT(ctypes.LittleEndianStructure):

        _pack_   = 4
        _fields_ = [
                        ('p', ctypes.c_int32),
                    ]
    class AnothernestedstructT(ctypes.LittleEndianStructure):
        class NestednestedStruct(ctypes.LittleEndianStructure):

            _pack_   = 4
            _fields_ = [
                            ('c', ctypes.c_int32),
                        ]
        _pack_   = 4
        _fields_ = [
                        ('p', ctypes.c_int32),
                        ('nestednested_struct', NestednestedStruct),
                    ]
    _pack_   = 4
    _fields_ = [
                    ('t', ctypes.c_int8 * 2 * 5),
                    ('t2', ctypes.c_int16 * 5),
                    ('a', ctypes.c_uint32, 5),
                    ('', ctypes.c_uint32, 5),
                    ('pointer', ctypes.POINTER(ctypes.c_float)),
                    ('pointer2', ctypes.POINTER(ctypes.POINTER(ctypes.c_double))),
                    ('nestedStruct_t', NestedstructT),
                    ('anotherNestedStruct_t', AnothernestedstructT),
                    ('s', AnotherstructT),
                ]
class JuT(ctypes.LittleEndianStructure):

    _pack_   = 4
    _fields_ = [
                    ('baton', ctypes.c_int32),
                    ('cosmo', ctypes.c_float),
                ]
