# CoPY, the C to Python transpiler

Author: Brandon Cousin

## Introduction

CoPY is a transpiler which main goal is to ease automation of C code testing through Python as well as translating 
C struct as their Python counter equivalent through usage of ctypes.
This would speed up interfacing of C dll with Python as well as reverse engineer or generate Python decoder for binary data.

CoPy implements a full C preprocessor and a C front end + a transpiler that translate C struct definition to Python ctypes definition.
Complex project which embed a lot of dependencies and that rely on a lot of C features such as bitfield, anonymous struct are expected
to be fully understood.

## Dependencies

- Python >= 3.6
- ply >= 3.11

## Features

- C preprocessor
    - Pragma handling is missing (currently)
    - All C99 standard preprocessing should works (include, line, define, undef, if/elif/else)
    - Code can already be preprocessed, some reviews will be done to follow as much as possible ISO then compiler dependent implementation (gcc,msvc) will probably be added afterwards

- C front end
    - Tokenization
    - Parsing
    - Symbol tables (AST could be created as well)

- C transpiler
    - Translation of C struct into Python ctypes
    - Parameter based functions for Python struct generated

## What it will look like ?

An entry point will be required for the transpiler so it will be able to reconstruct the project hierarchy based on header inclusion.
Each dependencies will be resolved and a corresponding Python implementation will be generated following the project structure parsed.

For instance:

The transpiler will parse below C struct
```c
typedef enum
{
    NONE = 0,
    REPOSITIONABLE = 1,
    EXECUTABLE = 2,
    SHARED_OBJECT = 3,
    CORE = 4,
}fileType_e;

typedef enum
{
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
    RISC_V = 243,
}machine_e;

typedef enum
{
    NONE_V = 0x00,
    CURRENT = 0x01,
}version_e;

typedef enum
{
    NONE_X = 0,
    X86 = 1,
    X64_X = 2,
}x86_64_e;

typedef enum
{
    NONE_E = 0,
    LSB = 1,
    MSB = 2,
}endianness_e;

typedef enum
{
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
    STANDALONE = 255,
}abi_e;

typedef struct
{
    unsigned char magicNumber[4U];
    x86_64_e platform;
    endianness_e endianness;
    char version;
    abi_e abi;
    char abiVersion;
    char padding[7U];
    char size;
}identification_t;

typedef struct elf32_hdr
{
    identification_t identification;
    short type_u16;
    machine_e targetMachine_u16;
    version_e version_u32;
    int entryPoint_u32;
    int pHDROffset_u32;
    int sHROffset_u32;
    int flag_u32;
    short hdrSize_u16;
    short entryPSize_u16;
    short numPEntry_u16;
    short entrySSize_u16;
    short numSEntry_u16;
    short sIdx_u16;
} elf32_hdr_t;
```
and generate below Python representation
```python
# elf.py
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

    _pack_   = 4
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

    _pack_   = 4
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
```

## What is currently possible ?

C 99 preprocessor seems fully operational, only missing feature is pragma handling but it's planned to be implemented as well.
A simple C front end is already available but some refactoring are required to ease further maintainance and create some abstraction level to add compiler dependent implementation such as packing from MSVC/GCC etc...

c99_preprocessor.py has been the main focus because a PoC was the main purpose before proposing a project that could work with complex project that relies alot on compiler dependent feature, running c99_preprocessor.py will show that preprocessed_code can be generated.

A first ctypes generator has been added to show what can be achieved based on current project state.
Output directory show up a directive.py being generated from this generator and using directive.i which has been as well preprocessed by the project C preprocessor.
The final output follows the C struct even if initial struct is quite complex and contains a lot of different type of member declaration such as anonymous member, nested member, enumerations, bitfields, multidimensional array or pointers.