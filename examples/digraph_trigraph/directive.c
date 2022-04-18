#include "directive.h"

int main ()
{
    static uint8_t i = SIGNAL;
    static uint8_t j = FUNC(3,2);
    printf ("i = %d\n", i);
}
