%:define DLEVEL
#ifdef DLEVEL
??=define SIGNAL 1
#else
#define \
SIGNAL \
2 // splitted macro definition
#endif

int main()
{
    static uint8_t i = SIGNAL;
    printf("i = %d\n", i);
}