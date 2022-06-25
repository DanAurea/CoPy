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
}identification_t __attribute__((packed));

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