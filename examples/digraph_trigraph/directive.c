%:define DLEVEL
#ifndef DLEVEL
??=define SIGNAL 1
#else
#define \
SIGNAL \
2 // splitted macro definition
#define FUNC(x, a) (a + x)
static int truc;
#endif

int main ()
{
    static uint8_t i = SIGNAL;
    printf ("i = %d\n", i);
}