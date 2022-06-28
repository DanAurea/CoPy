import ctypes
import enum

class FiletypeE(ctypes.LittleEndianStructure):
    class Value(enum.IntEnum):
        NONE = 0,
        REPOSITIONABLE = 1,
        EXECUTABLE = 2,
        SHARED_OBJECT = 3,
        CORE = 4
    _pack_   = 4
    _fields_ = [
                    ('_value', ctypes.c_uint32),
               ]

    @property
    def value(self):
        return self.Value(self._value)
class MachineE(ctypes.LittleEndianStructure):
    class Value(enum.IntEnum):
        NONE_M = 0,
        SPARC = 2,
        INTEL_80386 = 3,
        MOTOROLA_68000 = 4,
        INTEL_I860 = 7,
        MIPS_I = 8,
        INTEL_I960 = 19,
        POWERPC = 20,
        ARM_M = 40,
        INTEL_IA64 = 50,
        X64_M = 62,
        RISC_V = 243
    _pack_   = 4
    _fields_ = [
                    ('_value', ctypes.c_uint32),
               ]

    @property
    def value(self):
        return self.Value(self._value)
class VersionE(ctypes.LittleEndianStructure):
    class Value(enum.IntEnum):
        NONE_V = 0,
        CURRENT = 1
    _pack_   = 4
    _fields_ = [
                    ('_value', ctypes.c_uint32),
               ]

    @property
    def value(self):
        return self.Value(self._value)
class X8664E(ctypes.LittleEndianStructure):
    class Value(enum.IntEnum):
        NONE_X = 0,
        X86 = 1,
        X64_X = 2
    _pack_   = 4
    _fields_ = [
                    ('_value', ctypes.c_uint32),
               ]

    @property
    def value(self):
        return self.Value(self._value)
class EndiannessE(ctypes.LittleEndianStructure):
    class Value(enum.IntEnum):
        NONE_E = 0,
        LSB = 1,
        MSB = 2
    _pack_   = 4
    _fields_ = [
                    ('_value', ctypes.c_uint32),
               ]

    @property
    def value(self):
        return self.Value(self._value)
class AbiE(ctypes.LittleEndianStructure):
    class Value(enum.IntEnum):
        UNIX = 0,
        HP_X = 1,
        NET_BSD = 2,
        LINUX = 3,
        SUN_SOLARIS = 6,
        IBM_AIX = 7,
        SGI_IRIX = 8,
        FREEBSD = 9,
        COMPAQ_TRU64 = 10,
        NOVELL_MODESTO = 11,
        OPENBSD = 12,
        ARM_EABI = 64,
        ARM_A = 97,
        STANDALONE = 255
    _pack_   = 4
    _fields_ = [
                    ('_value', ctypes.c_uint32),
               ]

    @property
    def value(self):
        return self.Value(self._value)
class IdentificationT(ctypes.LittleEndianStructure):

    _pack_   = 8
    _fields_ = [
                    ('magicNumber', ctypes.c_uint8 * 4),
                    ('platform', X8664E),
                    ('endianness', EndiannessE),
                    ('version', ctypes.c_int8),
                    ('abi', AbiE),
                    ('abiVersion', ctypes.c_int8),
                    ('padding', ctypes.c_int8 * 7),
                    ('size', ctypes.c_int8),
                ]
class Elf32HdrT(ctypes.LittleEndianStructure):

    _pack_   = 1
    _fields_ = [
                    ('identification', IdentificationT),
                    ('type_u16', ctypes.c_int16),
                    ('targetMachine_u16', MachineE),
                    ('version_u32', VersionE),
                    ('entryPoint_u32', ctypes.c_int32),
                    ('pHDROffset_u32', ctypes.c_int32),
                    ('sHROffset_u32', ctypes.c_int32),
                    ('flag_u32', ctypes.c_int32),
                    ('hdrSize_u16', ctypes.c_int16),
                    ('entryPSize_u16', ctypes.c_int16),
                    ('numPEntry_u16', ctypes.c_int16),
                    ('entrySSize_u16', ctypes.c_int16),
                    ('numSEntry_u16', ctypes.c_int16),
                    ('sIdx_u16', ctypes.c_int16),
                ]
