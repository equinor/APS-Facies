/*
   Include file for utl
   $Id: utl.h,v 1.1.1.1 2003/01/10 14:26:17 olia Exp $
   This file should be included to prototype the parameters.
*/

#include <stdio.h>
#define ZERO_TOL 0.000001
				/* define almost equal */
#define AEQ(a,b) ( fabs( (double)(a) - (double)(b) ) <= ZERO_TOL )

/*Variables*/
extern char *utl_prog_name;

/*utl fuctions */

#ifdef __cplusplus
extern "C"
{
#endif

void *Mmatrix_1d(int, int, int, int);
void *Mmatrix_2d(int, int, int, int, int, int);
void *Mmatrix_3d(int, int, int, int, int, int, int, int);
void *Mmatrix_4d(int, int, int, int, int, int, int, int, int, int);
void *Mmatrix_5d(int, int, int, int, int, int, int, int, int, int, int, int);
void utl_minmax( double *, int , double *, double * );
char * utl_today(char *);

double utl_mn_constant(int , double );
double utl_mn_d(int , double , double *, double *, double **);

double utl_inreal(FILE *, char *, int *);

void *Fmatrix_1d(void *);
void *Fmatrix_2d(void *, void *);
void *Fmatrix_3d(void *, void *, void *);
void *Fmatrix_4d(void *, void *, void *, void *);
void *Fmatrix_5d(void *, void *, void *, void *, void *);

int matrix_inversion(double **, int , double **, double *);
int utl_eigval(double **, int , double *, double *);
int utl_inint(FILE *, char *, int *);
int utl_skip_comments(FILE *);
int utl_yesp();

void utl_error(int, char *, ...);

double utl_cumnorm(double);
double utl_genmahalanobis(double * ,
			  double * ,
			  double ** ,
			  double ** ,
			  int );
double utl_mahalanobis(double * ,
		       double * ,
		       double ** ,
		       int );
double utl_mean( double *, int  );
double utl_median( double *, int  );
double utl_stdev( double *, int , double );


#ifdef __cplusplus
}
#endif



