#ifndef GLOBAL_DEF_H
#define GLOBAL_DEF_H

#define RMISSING -999.0
#define IMISSING -999
#define MAXLEN   10000  /* Max length of filenames */

#define MAX_PATH_GLOBAL_DEF  10000  /* Max length of filenames */

#define MAX_STRING 50  /* Max length of string parameters */

#ifndef PI
#define PI  3.14159265358979323846
#endif

#define MAXIM(A,B) ((A) > (B) ? (A) : (B))
#define MINIM(A,B) ((A) < (B) ? (A) : (B))
#define MINMAX(a,b,c) ((a) > (b) ? (a) : ((b) > (c) ? (c) : (b)))

#define MALLOC(type) (type *) calloc(1,sizeof(type))
#define CALLOC(size,type) (type *) calloc(size + 1,sizeof(type))
#define REALLOC(p,size,type) p = (type *) realloc(p,(size + 1) * sizeof(type))
#define FREE(p) {free(p);p=NULL;}

#define OK 0
#define ERR 1

#endif
