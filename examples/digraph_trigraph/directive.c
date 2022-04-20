#include "directive.h"

int main ()
{
    static uint8_t i = SIGNAL;
    static uint8_t j = FUNC (3,2);
    printf ("i = %d\n", i);
    printf ("__DATE__ = %s\n", __DATE__);
    printf ("__FILE__ = %s\n", __FILE__);
    printf ("__TIME__ = %s\n", __TIME__);
    printf ("__LINE__ = %s\n", __LINE__);
    #line 45
    printf ("__LINE__ = %s\n", __LINE__);
    #line 48 "not_directive.c"
    printf ("__LINE__ = %s\n", __LINE__);
    printf ("__FILE__ = %s\n", __FILE__);
    RECURSIVE()
    RECURSIVE()
}
