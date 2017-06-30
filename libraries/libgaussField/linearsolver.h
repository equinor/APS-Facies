/*Func: linearsolver 

Name:      linearsolver - Header file 
Syntax:     @linearsolver-syntaks
Description:  


----------------------------------------------------------------
*/

#if !defined(LINEARSOLVER_H)
#define LINEARSOLVER_H  1 


/* Defining symbols */


/* Prototype declarations  */

#ifdef __cplusplus
extern "C"
{
#endif

/*<linearsolver-syntaks:*/
int dgeco(double *a, int *lda, int *n, int *ipvt, 
	   double *rcond,double *z);

int dgefa(double *a, 
	   int *lda, int *n, int *ipvt, int *info);

int dgesl(double *a, int *lda, int *n, int *ipvt, 
	   double *b, int *job);

int cholesky_fact(int *i_mdim,
		  int *i_dim,
		  double *x_mtx);

/*>linearsolver-syntaks:*/

#ifdef __cplusplus
}
#endif




#endif


