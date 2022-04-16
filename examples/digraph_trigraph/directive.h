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
#define SIGNAL -43

#endif
#define FUNC(x, a) (a + x)
static int elseVariable;
#endif