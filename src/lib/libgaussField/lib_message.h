/*Func: lib_message.h 

Name:      lib_message.h - Header file
Syntax:     @lib_message-syntaks
Description:Function prototypes for library functions in lib_message.c  

----------------------------------------------------------------
*/

#ifndef LIB_MESSAGE_H
#define LIB_MESSAGE_H 1

/* Defining symbols */

#define NERRORS   9

#define OK        0
#define NODEFAULT 1
#define OPENFILE  2
#define READFILE  3
#define ALLOC     4
#define MODEL     5
#define KERNEL    6
#define WRITEFILE 7
#define DATACHECK 8
#define CLOSEFILE 9

#define NMESSTYPES 2

#define STATUS 1
#define DETAILS 2

#define NWARNTYPES 2

#define CORRECT 1
#define CHECK 2


/* Prototype declarations  */

/*<lib_message-syntaks:*/

#include <stdio.h>
#include <stdlib.h>
#include <stdarg.h>
#include <string.h>
#include <ctype.h>

#ifdef __cplusplus
extern "C"
{
#endif

void initMessage(int argc, char *[], char *usage);
void moduleError(int , const char *, const char *, ...);
void modelFileError(char *, ...);
void moduleWarning(int , const char *, const char *, ...);
void moduleMessage(int , const char *, const char *, ...);
void moduleErrorSetNoExit(int);
int  uiErrorSetBuffer(char *message, ...);
void moduleErrorLog(FILE*,int , char *, char *, ...);
void moduleWarningLog(FILE*,int , char *, char *, ...);
void moduleMessageLog(FILE*,int , char *, char *, ...);

/*>lib_message-syntaks:*/

#ifdef __cplusplus
}
#endif


#endif /* LIB_MESSAGE_H */











