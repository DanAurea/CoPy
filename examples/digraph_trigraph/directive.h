#include "debug.h"
#if DLEVEL == 1
??=define SIGNAL 1
static int ifVariable;
#else
#define \
SIGNAL \
2 // splitted macro definition
#if DLEVEL != 1
#define SIGNAL 0x43
/*#define SIGNAL 43UL
*/
#define SIGNAL 43.0
#define SIGNAL 43.0E-2
#define SIGNAL 43E2
#define SIGNAL -43U
#define SIGNAL 012UL

#endif
#define FUNC(x, a) a + x
static int elseVariable;
#endif

typedef enum example
{
    ENUM_1 = 2,
    ENUM_2,
    ENUM_3,
    ENUM_4,
    ENUM_5 = 61,
    ENUM_6
}example_t;