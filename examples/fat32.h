#include <stdint.h>
#include "fat32_constant.h"

typedef enum
{
    /* Enumeration representing the media being used */
    EIGHT_INCH = 0xE5,
    FIVE_INCH = 0xED,
    NON_STANDARD_CUSTOM = 0xEE,
    NON_STANDARD_SUPERFLOPPY = 0xEF,
    THREE_INCH = 0xF0,
    DOUBLE_DENSITY = 0xF4,
    FIXED_DISK_4_SIDED = 0xF5,
    FIXED_DISK = 0xF8,
    THREE_INCH_DOUBLE_SIDED = 0xF9,
    THREE_AND_FIVE_INCH_SINGLE = 0xFA,
    THREE_AND_FIVE_INCH_DOUBLE = 0xFB,
    FIVE_INCH_SINGLE_SIDED_9_TRACK = 0xFC,
    FIVE_INCH_DOUBLE_SIDED_9_TRACK = 0xFD,
    FIVE_INCH_SINGLE_SIDED_8_TRACK = 0xFE,
    FIVE_INCH_DOUBLE_SIDED_8_TRACK = 0xFF
}mediaDescriptor_t;

typedef struct
{
    uint16_t bytesPerSec;
    uint8_t logicalSectorPerClus;
    uint16_t countReservedLogicalSec;
    uint8_t numberFAT;
    uint16_t maxNumberFAT12_16RootDirEnt;
    uint16_t totalLogicalSectors;
    mediaDescriptor_t fatID; /* 1 byte long so packing should be used */
    uint16_t logicalSectorPerFAT;
}biosParameterBlock_t;

typedef struct
{
    uint8_t jumpBoot[3];
    uint8_t OEMName[8];
    biosParameterBlock_t bpb;
    uint16_t bootSectorSignature;
}bootSector_t;

typedef struct fsInformationSector
{
    uint32_t sectorSignatureCompat;
    uint8_t reserved[RESERVED_ARRAY_LEN]; /*Non used values*/
    uint32_t sectorSignature;
    uint32_t numberFreeCluster;
    uint32_t numberAllocatedCluster;
    uint8_t reserved2[RESERVED2_ARRAY_LEN];
    uint32_t sectorSignatureEnd;
}fsInformationSector_t;

typedef struct FATPartition
{
    /* Information sector (boot + file system) */
    bootSector_t boot;
    fsInformationSector_t fsInformation;
    
    /* FAT structure and its data (this is not the real structure layout but simply a similar one) */
    uint8_t FATRegion[FAT_REGION_SIZE];
    uint8_t rootDirRegion[ROOT_DIR_SIZE];
    uint8_t dataRegion[DATA_SIZE];
}FATPartition_t;