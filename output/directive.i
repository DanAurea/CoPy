






















static int elseVariable ; 
typedef enum example 
{ 
ENUM_1 = 2 , 
ENUM_2 , 
ENUM_3 , 
ENUM_4 , 
ENUM_5 = 61 , 
ENUM_6 
} example_t ; 


int main ( ) 
{ 
static uint8_t i = 10 L  ; 
static uint8_t j = 2 + 3  ; 
printf ( "i = %d\n" , i ) ; 
printf ( "__DATE__ = %s\n" , "Jun 29 2022"  ) ; 
printf ( "__FILE__ = %s\n" , "directive.c"  ) ; 
printf ( "__TIME__ = %s\n" , "01:22:30"  ) ; 
printf ( "__LINE__ = %s\n" , 11  ) ; 


printf ( "__LINE__ = %s\n" , 45  ) ; 


printf ( "__LINE__ = %s\n" , 48  ) ; 
printf ( "__FILE__ = %s\n" , "not_directive.c"  ) ; 
I am RECURSIVE ( )  
I am RECURSIVE ( )  
} 
