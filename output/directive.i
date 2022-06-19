
















static int elseVariable = 3; 

typedef enum  
{ 
ENUM_1 = 2 , 
ENUM_2 , 
ENUM_3 , 
ENUM_4 , 
ENUM_5 = 61 , 
ENUM_6 
} example_t, truc_t ; 

struct struct_tag;

typedef struct{
    int p;
}anotherStruct_t;

typedef struct struct_tag
{
    char t[5U][const static 2];
    short t2[5U];
    unsigned int a:5;
    unsigned int :5;
    float * pointer;
    double ** const pointer2;

    struct{
        int p;
    }nestedStruct_t;

    struct{
        int p;
        struct
        {
            int c;
        }nestednested_struct;
    }anotherNestedStruct_t;

    anotherStruct_t s;
}struct_t;