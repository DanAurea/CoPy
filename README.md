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
// example.h
#include "dependency.h"

typedef struct example
{
    uint32_t oneField_u32;
    uint32_t secondField_u32:16;
    uint32_t thirdField_u32:15;
    uint32_t fourthField_u32:1;
    structDependency_t dep_s; 
}example_t;

// dependency.h

typedef struct structDependency
{
    char c;
    int i;
}structDependency_t;
```
and generate below Python representation
```python
# example.py
import dependency

class Example(Structure):
    _fields_ = [
                    ("oneField_u32", c_uint32),
                    ("secondField_u32", c_uint32, 16),
                    ("thirdField_u32", c_uint32, 15),
                    ("fourthField_u32", c_uint32, 1),
                    ("dep_s", structDependency),
                ]

# dependency.py
class Dependency(Structure):
    _fields_ = [
                    ("c", c_char),
                    ("i", c_int32),
                ]
```

## What is currently possible ?

C 99 preprocessor seems fully operational, only missing feature is pragma handling but it's planned to be implemented as well.
A simple C front end is already available but some refactoring are required to ease further maintainance and create some abstraction level to add compiler dependent implementation such as packing from MSVC/GCC etc...

c99_preprocessor.py has been the main focus because a PoC was the main purpose before proposing a project that could work with complex project that relies alot on compiler dependent feature, running c99_preprocessor.py will show that preprocessed_code can be generated.