#define A_CONSTANT 1U
#define ANOTHER_CONSTANT 3.0F
#define A_LAST_CONSTANT 8 * 512

struct __attribute__((packed, aligned(4)))
{
    float f_f32;
    double d_f64;
    long l_64;
}no_typedef_struct;

typedef struct __attribute__((packed, aligned(4)))
{
    float f_f32;
    double d_f64;
    long l_64;
}another_struct;

typedef struct __attribute__((packed, aligned(1))){
    float f_f32;
    double d_f64;
    int32_t i_32;
    uint32_t i_u32[A_LAST_CONSTANT];
    uint8_t i_u8[A_CONSTANT];
    another_struct s;
    struct no_typedef_struct s2;
} my_struct;