
/*

  DESCRIPTION:

  Subroutine library for matr handlings.

  THE MODULE CONTAINS THE FOLLOWING FUNCTIONS:

  Public module unit(s):

   void lib_matr_update_var(double *i_obs, int i_n, int i_np,
                           double *x_mu, double **x_var)
   void lib_matr_downdate_var(double *i_obs, int i_n, int i_np,
                           double *x_mu, double **x_var)
   void lib_matr_exp(double **i_mat,int i_n,double i_exp,
                         double **o_mat)
   void lib_matr_prod(double **i_mat1,double **i_mat2,
                          int i_n1,int i_n2,int i_n3,
                          double **o_mat)
   void lib_matr_prodmatvec(double **i_mat, double *i_vec, int i_n1, int i_n2,
                            double *o_vec)
   void lib_matr_add(double **i_y, int i_n1, int i_n2,double **x_x)
   void lib_matr_addvec(double *i_y, int i_n, double *x_x)
   void lib_matr_subtract(double **i_x, double **i_y, int i_n1, int i_n2,
                          double **o_z)
   void lib_matr_subtractvec(double *i_x, double *i_y, int i_n, double *o_z)
   void lib_matr_eigen(double **i_mat,int i_n,
                            double **o_eigvec,double *o_eigval, int *o_error)
   void lib_matr_eigen(double **i_mat,int i_n,
                            double *o_eigval, int *o_error)
   int lib_matr_cholesky(int i_dim, double **x_mat)
   void lib_matr_axeqb(int i_dim, double **i_mat, double *x_vec)

  Private module unit(s):

  static void lib_matr_tred2(int i_n, double **x_a, double o_d[], double o_e[])
  static void lib_matr_tqli(double i_e[], int i_n, double **x_z, double x_d[],
                   int *o_error)
  static void lib_matr_evtred2(int i_n, double **x_a,double o_d[],double o_e[])
  static void lib_matr_evtqli(double i_e[], int i_n, double x_d[],int *o_error)

  File declaring external routines: lib_matr.h

  File(s) with referenced routine(s):

     utl_malloc.c

*/

/*INCLUDE FILES:*/
#include <stdlib.h>
#include <math.h>
#include "lib_matr.h"
#include "utl.h"


/* Module spesific definition */
# define SIGN(a,b) ((b)<0 ? -fabs(a) : fabs(a))

static void lib_matr_tred2(int, double **, double [], double []);
static void lib_matr_tqli(double [], int, double **, double [], int *);
static void lib_matr_evtred2(int, double **, double [], double []);
static void lib_matr_evtqli(double [], int, double [], int *);

void lib_matr_update_var(
   double    *i_obs,
   int      i_n,
   int      i_np,
   double    *x_mu,
   double   **x_var)
/*FUNC******************************************************************

DESCRIPTION:

Updating expectation and variance according to formulas given
in Hand, page 63, corrected for errors.
NOTE: only lower triangle of covariance matrix is updated

HOW TO USE THE FUNCTION:
lib_matr_update_var(i_obs, i_n, i_np, x_mu, x_var);

SIDE-EFFECTS:

RETURN VALUE:

***********************************************************************/
{
 /* local variables */

 int         l_i,l_j;
 double       l_n_1,l_n;

 l_n_1 = (double) (i_n - 1);
 l_n = (double) i_n;

 for(l_i = 1 ; l_i <= i_np ; l_i++)  {
    for(l_j = 1 ; l_j <= l_i ; l_j++)  {
       x_var[l_i][l_j] = (x_var[l_i][l_j] +
          (x_mu[l_i] - i_obs[l_i]) *
          (x_mu[l_j] - i_obs[l_j])/l_n) * l_n_1/l_n;
     }
    x_mu[l_i] = (x_mu[l_i] * l_n_1 + i_obs[l_i])/l_n;
  }
}


void lib_matr_downdate_var(
   double    *i_obs,
   int      i_n,
   int      i_np,
   double    *x_mu,
   double   **x_var)
/*FUNC******************************************************************

DESCRIPTION:

Updating expectation and variance according to formulas given
in Hand, page 63, corrected for errors.
NOTE: only lower triangle of covariance matrix is updated

HOW TO USE THE FUNCTION:
lib_matr_downdate_var(i_obs, i_n, i_np, x_mu, x_var);

SIDE-EFFECTS:

RETURN VALUE:

***********************************************************************/
{
 /* local variables */

 int         l_i,l_j;
 double       l_n_1,l_n;

 l_n_1 = (double) (i_n - 1);
 l_n = (double) i_n;

 for(l_i = 1 ; l_i <= i_np ; l_i++)  {
    for(l_j = 1 ; l_j <= l_i ; l_j++)  {
       x_var[l_i][l_j] = x_var[l_i][l_j]*l_n/l_n_1 -
          (x_mu[l_i] - i_obs[l_i]) *
          (x_mu[l_j] - i_obs[l_j])/l_n;
     }
    x_mu[l_i] = (x_mu[l_i] * l_n - i_obs[l_i])/l_n_1;
  }
}


void lib_matr_exp(
    double      **i_mat,
    int          i_n,
    double        i_exp,
    double      **o_mat)
/*FUNC******************************************************************

DESCRIPTION:

Calculate mat^exp by eigenvalue decomposition

HOW TO USE THE FUNCTION:

SIDE-EFFECTS:

RETURN VALUE:

***********************************************************************/
{
 /* local variables */
 int         l_i,l_j,l_k;
 double      *l_eigval;
 double     **l_eigvec;
 int         l_error;

 l_eigval = (double *) Mmatrix_1d(0,i_n-1,sizeof(double),1);
 l_eigvec = (double **) Mmatrix_2d(0,i_n-1,0,i_n-1,sizeof(double),1);

 lib_matr_eigen(i_mat,i_n,l_eigvec,l_eigval,&l_error);

 for(l_i = 0 ; l_i <= i_n-1 ; l_i++)
   {
    if(l_eigval[l_i] > 0.0)
      l_eigval[l_i] = pow(l_eigval[l_i],i_exp);
    else
      {
       printf("lib_matr_exp: Matrix not positive definite");
       exit(1);
     }
  }
 for(l_i = 0 ; l_i <= i_n-1 ; l_i++)
 for(l_j = 0 ; l_j <= i_n-1 ; l_j++)
   {
    o_mat[l_i][l_j] = l_eigval[0] * l_eigvec[0][l_i] *
                      l_eigvec[0][l_j];
    for(l_k = 1 ; l_k <= i_n-1 ; l_k++)
       o_mat[l_i][l_j] = o_mat[l_i][l_j] +
                         l_eigval[l_k] * l_eigvec[l_k][l_i] *
                         l_eigvec[l_k][l_j];
  }

 l_eigval=(double *)Fmatrix_1d((char *)&l_eigval);
 l_eigvec=(double **)Fmatrix_2d((char **)&l_eigvec[0][0], (char*)&l_eigvec[0]);

}

void lib_matr_prod(
   double      **i_mat1,
   double      **i_mat2,
   int         i_n1,
   int         i_n2,
   int         i_n3,
   double      **o_mat)
/*FUNC******************************************************************

DESCRIPTION:

Calculate the matrix product of a n1 x n2 matrix and a n2 x n3
matrix

HOW TO USE THE FUNCTION:

SIDE-EFFECTS:

RETURN VALUE:

***********************************************************************/

{
 /* local variables */

 int         l_i,l_j,l_k;
 double       l_x;

 for(l_i = 0 ; l_i <= i_n1-1 ; l_i++)
    for(l_j = 0 ; l_j <= i_n3-1 ; l_j++)
      {
       l_x = 0.0000000000000;
       for(l_k = 0 ; l_k <= i_n2-1 ; l_k++)
          l_x = l_x + i_mat1[l_i][l_k] * i_mat2[l_k][l_j];
       o_mat[l_i][l_j] = l_x;
     }

}


void lib_matr_prodmatvec(
   double      **i_mat,
   double      *i_vec,
   int         i_n1,
   int         i_n2,
   double      *o_vec)
/*FUNC******************************************************************

DESCRIPTION:

Calculate the product of a n1 x n2 matrix and a n2 x 1 vector and puts it into
the n1 x 1 vector o_vec.

HOW TO USE THE FUNCTION:

SIDE-EFFECTS:

RETURN VALUE:

***********************************************************************/

{
 /* local variables */

 int         l_i,l_k;
 double       l_x;

 for(l_i = 0 ; l_i <= i_n1-1 ; l_i++)
      {
       l_x = 0.0000000000000;
       for(l_k = 0 ; l_k <= i_n2-1 ; l_k++)
          l_x = l_x + i_mat[l_i][l_k] * i_vec[l_k];
       o_vec[l_i] = l_x;
     }

}


void lib_matr_add(
   double      **i_y,
   int         i_n1,  /* number of rows */
   int         i_n2,  /* number of columns */
   double      **x_x)
/*FUNC*******************************************************************

DESCRIPTION:

Calculates the sum x_x = x_x + i_y. Both matrices have dimension i_n1*i_n2.

HOW TO USE THE FUNCTION:

lib_matr_add(i_y, i_n1, i_n2, x_x)

SIDE-EFFECTS:

RETURN VALUE: void

*************************************************************************/
{
/* local variables */
  int l_i, l_j;

  for (l_i=0; l_i<=i_n1-1; l_i++)
    for (l_j=0; l_j<=i_n2-1; l_j++)
      x_x[l_i][l_j] = i_y[l_i][l_j] + x_x[l_i][l_j];

}


void lib_matr_addvec(
   double      *i_y,
   int         i_n,  /* number of rows */
   double      *x_x)
/*FUNC*******************************************************************

DESCRIPTION:

Calculates the sum x_x = x_x + i_y. Both vectors have dimension i_n1*1.

HOW TO USE THE FUNCTION:

lib_matr_add(i_y, i_n, x_x)

SIDE-EFFECTS:

RETURN VALUE: void

*************************************************************************/
{
/* local variables */
  int l_i;

  for (l_i=0; l_i<=i_n-1; l_i++)
      x_x[l_i] = i_y[l_i] + x_x[l_i];
}


void lib_matr_subtract(
   double      **i_x,
   double      **i_y,
   int         i_n1,  /* number of rows */
   int         i_n2,  /* number of columns */
   double      **o_z)
/*FUNC*******************************************************************

DESCRIPTION:

Calculates the difference o_z=i_x-i_y. All matrices have dimension i_n1*i_n2.

HOW TO USE THE FUNCTION:

lib_matr_add(i_x, i_y, i_n1, i_n2, o_z)

SIDE-EFFECTS:

RETURN VALUE: void

*************************************************************************/
{
/* local variables */
  int l_i, l_j;

  for (l_i=0; l_i<=i_n1-1; l_i++)
    for (l_j=0; l_j<=i_n2-1; l_j++)
      o_z[l_i][l_j] = i_x[l_i][l_j] - i_y[l_i][l_j];
}


void lib_matr_subtractvec(
   double      *i_x,
   double      *i_y,
   int         i_n,  /* number of rows */
   double      *o_z)
/*FUNC*******************************************************************

DESCRIPTION:

Calculates the difference o_z=i_x-i_y. All vectors have dimension i_n * 1.

HOW TO USE THE FUNCTION:

lib_matr_add(i_x, i_y, i_n, o_z)

SIDE-EFFECTS:

RETURN VALUE: void

*************************************************************************/
{
/* local variables */
  int l_i;

  for (l_i=0; l_i<=i_n-1; l_i++)
      o_z[l_i] = i_x[l_i] - i_y[l_i];
}


void  lib_matr_eigen(
   double      **i_mat,
   int         i_n,
   double      **o_eigvec,
   double       *o_eigval,
   int         *o_error) /* 0 if ok, 1 if not all eigenvalues determined.
                            input to the function tqli. */
/*FUNC******************************************************************

DESCRIPTION:

Calculate the eigenvectors and eigenvalues of a real, symmetric
matrix using the Householders algorithm described in 'Numerical recipes in C',
p 353-381. To do this we use the two local functions 'tred2' and 'tqli'.

HOW TO USE THE FUNCTION:

lib_matr_eigen(i_mat, i_n, o_eigvec, o_eigval, o_error);

SIDE-EFFECTS:

RETURN VALUE:

*********************************************************************/
{
 /* local variables */

  double *l_d, *l_e, **l_mat;
  int i,j;

/* Since the input to the functions tred2 and tqli will be destroyed, we
   make a copy of i_mat.  */

  l_mat = (double **) Mmatrix_2d(0, i_n-1, 0, i_n-1, sizeof(double), 1);
  l_d = (double *) Mmatrix_1d(0,i_n-1, sizeof(double), 1);
  l_e = (double *) Mmatrix_1d(0,i_n-1, sizeof(double), 1);

  for (i=0; i<=i_n-1; i++)
    for (j=0; j<=i_n-1; j++)
      l_mat[i][j] = i_mat[i][j];

  lib_matr_tred2(i_n, l_mat, l_d, l_e);
  lib_matr_tqli(l_e, i_n, l_mat, l_d, o_error);

  if (*o_error > 0) return;

  for (i=0; i<=i_n-1; i++) {
    o_eigval[i] = l_d[i];
    for (j=0; j<=i_n-1; j++)
      o_eigvec[i][j] = l_mat[i][j];
  }

  l_mat = (double **)Fmatrix_2d((char **)&l_mat[0][0], (char *)&l_mat[0]);
  l_d = (double *)Fmatrix_1d((char *)&l_d[0]);
  l_e = (double *)Fmatrix_1d((char *)&l_e[0]);
}


void  lib_matr_eigenvalues(
   double      **i_mat,
   int         i_n,
   double      *o_eigval,
   int         *o_error) /* 0 if ok, 1 if not all eigenvalues determined.
                            input to the function tqli. */
/*FUNC******************************************************************

DESCRIPTION:

Calculate the eigenvalues of a real, symmetric
matrix using the Householders algorithm described in 'Numerical recipes in C',
p 353-381. To do this we use the two local functions 'evtred2' and 'evtqli'.

HOW TO USE THE FUNCTION:

lib_matr_eigen(i_mat, i_n, o_eigvec, o_eigval, o_error);

SIDE-EFFECTS:

RETURN VALUE:

*********************************************************************/
{
 /* local variables */

  double *l_d, *l_e, **l_mat;
  int i,j;

/* Since the input to the functions tred2 and tqli will be destroyed, we
   make a copy of i_mat.  */

  l_mat = (double **) Mmatrix_2d(0, i_n-1, 0, i_n-1, sizeof(double), 1);
  l_d = (double *) Mmatrix_1d(0,i_n-1, sizeof(double), 1);
  l_e = (double *) Mmatrix_1d(0,i_n-1, sizeof(double), 1);

  for (i=0; i<=i_n-1; i++)
    for (j=0; j<=i_n-1; j++)
      l_mat[i][j] = i_mat[i][j];

  lib_matr_evtred2(i_n, l_mat, l_d, l_e);
  lib_matr_evtqli(l_e, i_n, l_d, o_error);

  if (*o_error > 0) return;

  for (i=0; i<=i_n-1; i++)
    o_eigval[i] = l_d[i];

  l_mat = (double **)Fmatrix_2d((char **)&l_mat[0][0], (char *)&l_mat[0]);
  l_d = (double *)Fmatrix_1d((char *)&l_d[0]);
  l_e = (double *)Fmatrix_1d((char *)&l_e[0]);
}


int lib_matr_cholesky(
int i_dim, /*The dimension of the input matrix. */
double **x_mat) /*The matrix beeing decomposed on input, on output the lower
		  triangel contains the L-matrix. */
/*FUNC********************************************************************

DESCRIPTION:

Factorizes the positive definite, symmetric matrix 'x_mat' into
L * L(transposed), when L is a lower triangular matrix. L is stored in the
lower part of 'x_mat' on output.

HOW TO USE THE FUNCTION:
lib_matr_cholesky(i_dim, x_mat);

SIDE-EFFECTS: The input matrix 'x_mat' is destroyed on output.

RETURN VALUE: 0 if everything O.K.
              1 if illegal matrix

************************************************************************/
{
  int l_i, l_j, l_k, r_value = 0;
  double l_r;

  for (l_i=0; l_i < i_dim; l_i++)
    if (x_mat[l_i][l_i] <= 0.0000000001) {
      fprintf(stderr, "Matrix to be Cholesky factorized not valid! %s\n",
	      "Diagonal-element near 0.0");
      r_value = 1;
      return(r_value);
    } else {
      for (l_j=0; l_j < l_i; l_j++) {
	l_r = 0.0;
	for (l_k = 0; l_k < l_j; l_k++)
	  l_r += x_mat[l_i][l_k] * x_mat[l_j][l_k];
	x_mat[l_i][l_j] = (x_mat[l_i][l_j] - l_r) / x_mat[l_j][l_j];
      }
      l_r = 0.0;
      for (l_k=0; l_k < l_i; l_k++)
	  l_r += x_mat[l_i][l_k] * x_mat[l_i][l_k];
      l_r = x_mat[l_i][l_i] - l_r;
      if (l_r <= 0.000000000001) {
	fprintf(stderr, "Matrix to be Cholesky factorized not valid !\n");
	r_value = 1;
	return(r_value);
      }
      x_mat[l_i][l_i] = sqrt(l_r);
    }
  return(r_value);
}


void lib_matr_axeqb(
int i_dim, /*The dimension of the equation system to solve. */
double **i_mat, /*The LU-decomp. of the A-matrix in the equation-system.*/
double *x_vec) /*On input the vector b, on output the solution x.*/
/*FUNC*****************************************************************
DESCRIPTION:

Solves the set of i_dim linear equations A * x = b. Here the matrix A is input
as its LU-decomposition. The function 'lib_matr_cholesky' should be used on
A before this function is called.

HOW TO USE THE FUNCTION:
lib_matr_axeqb(i_dim, i_mat, x_vec);

SIDE-EFFECTS: The input-vector b is destroyed on output.

RETURN VALUE: void.

************************************************************************/
{
  int l_i, l_j;
  double l_x;

  for (l_i = 0; l_i < i_dim; l_i++) {
    l_x = x_vec[l_i];
    for (l_j = 0; l_j < l_i; l_j++)
      l_x -= x_vec[l_j] * i_mat[l_i][l_j];
    x_vec[l_i] = l_x / i_mat[l_i][l_i];
  }

  for (l_i = i_dim - 1; l_i >= 0; l_i--) {
    l_x = x_vec[l_i];
    for (l_j = i_dim - 1; l_j > l_i; l_j--)
      l_x = l_x - x_vec[l_j] * i_mat[l_j][l_i];
    x_vec[l_i] = l_x / i_mat[l_i][l_i];
  }
}


static void lib_matr_tred2(int i_n, double **x_a, double o_d[], double o_e[])
/*FUNC**********************************************************************

DESCRIPTION:

Householder reduction of a real, symmetric, matrix a[0,...,n-1][0,...,n-1].
On output, x_a is replaced by the orthogonal matrix Q effecting the
transformation. d[0,...,n-1] returns the diagonal elements of the
tridiagonal matrix, and e[0,...,n-1] the off diagonal elements, e[0]=0.
Several statements, as noted in comments, can be omitted if only eigenvalues
are to be found, in which case x_a contains no useful information on output.
Otherwise they are to be included.
This implementation is the same as stated in 'Numerical recipes in C' p. 373,
except that here the arrays and matrices starts in 0.

HOW TO USE THE FUNCTION:

tred2(i_n, x_a, o_d, o_e);

SIDE-EFFECTS:

RETURN VALUE:

****************************************************************************/
{
  int l, k, j, i;
  double scale, hh, h, g, f;

  for (i = i_n - 1; i>=1; i--) {
    l = i-1;
    h = scale = 0.0;
    if (l > 0) {
      for (k=0; k<=l; k++)
	scale += fabs(x_a[i][k]);
      if (scale == 0)
	o_e[i] = x_a[i][l];
      else {
	for (k=0; k<= l; k++) {
	  x_a[i][k] /= scale;
	  h += x_a[i][k]*x_a[i][k];
	}
	f = x_a[i][l];
	g = f>0 ? -sqrt(h) : sqrt(h);
	o_e[i]=scale*g;
	h -= f*g;
	x_a[i][l] = f-g;
	f = 0.0;
	for (j=0; j<=l; j++) {
	/* Next statement can be omitted if eigenvectors not wanted */
	  x_a[j][i] = x_a[i][j]/h;
	  g = 0.0;
	  for (k=0; k<=j; k++)
	    g += x_a[j][k]*x_a[i][k];
	  for (k=j+1; k<=l; k++)
	    g += x_a[k][j]*x_a[i][k];
	  o_e[j] = g/h;
	  f += o_e[j]*x_a[i][j];
	}
	hh = f/(h+h);
	for (j=0; j<=l; j++) {
	  f = x_a[i][j];
	  o_e[j] = g = o_e[j]-hh*f;
	  for (k=0; k<=j; k++)
	    x_a[j][k] -= (f*o_e[k] + g*x_a[i][k]);
	}
      }
    }
    else
      o_e[i] = x_a[i][l];
    o_d[i] = h;
  }
  /* Next statement can be omitted if eigenvectors not wanted */
  o_d[0] = 0.0;
  o_e[0] = 0.0;
  /* Contents of this loop can be omitted if eigenvectors not wanted except
     for statement o_d[i] = x_a[i][i];  */
  for (i=0; i <= i_n-1; i++) {
    l = i-1;
    if (o_d[i]) {
      for (j=0; j <= l; j++) {
	g = 0.0;
	for (k=0; k<=l; k++)
	  g += x_a[i][k]*x_a[k][j];
	for (k=0; k<=l; k++)
	  x_a[k][j] -= g*x_a[k][i];
      }
    }
    o_d[i] = x_a[i][i];
    x_a[i][i] = 1.0;
    for (j=0; j<=l; j++)
      x_a[j][i]=x_a[i][j]=0.0;
  }
}



static void lib_matr_tqli(double i_e[], int i_n, double **x_z, double x_d[],
		 int *o_error)

/*FUNC************************************************************************

DESCRIPTION:

QL-algorithm with implicit shifts, to determine the eigenvalues and
eigenvectors of a real, symmetric, tridiagonal matrix, or of a real, symmetric
matrix previously reduced by 'tred2'. On input x_d[0,...i_n-1] contains the
diagonal elements of the tridiagonal matrix. On output, it returns the
eigenvalues. The vector i_e[0,...,i_n-1] inputs the subdiagonal elements of the
tridiagonal matrix, with i_e[0] arbitrary. On output i_e is destroyed. When
finding only the eigenvalues, several lines may be omitted, as noted in the
comments. If the eigenvectors of a tridiagonal matrix are desired, the matrix
x_z[0,...,i_n-1][0,...,i_n-1] is input as the identity matrix.
If the eigenvectors of a matrix that has been reduced by 'tred2' are
required, then x_z is input as the matrix output by 'tred2'.
In either case, the kth column of x_z
returns the normalized eigenvector corresponding to d[k].

HOW TO USE THE FUNCTION:

tqli(i_n, i_e, x_d, x_z);

SIDE-EFFECTS:

RETURN VALUE:

***************************************************************************/
{
  int m, l, iter, i, k;
  double s, r, p, g, f, dd, c, b;

  *o_error = 0;
  for (i=1; i<=i_n-1; i++) i_e[i-1] = i_e[i];
  i_e[i_n-1] = 0.0;
  for (l=0; l<=i_n-1; l++) {
    iter=0;
    do {
      for (m=l; m<=i_n-2; m++) {
	dd = fabs(x_d[m]) + fabs(x_d[m+1]);
	if (fabs(i_e[m])+dd == dd) break;
      }
      if (m != l) {
	if (iter++ == 30) {*o_error = 1; return;}
	g = (x_d[l+1] - x_d[l]) / (2.0*i_e[l]);
	r = sqrt((g*g) + 1.0);
	g = x_d[m] - x_d[l] + i_e[l] /(g + SIGN(r,g));
	s = c = 1.0;
	p = 0.0;
	for (i=m-1; i>=l; i--) {
	  f = s*i_e[i];
	  b = c*i_e[i];
	  if (fabs(f) >= fabs(g)) {
	    c = g/f;
	    r = sqrt((c*c) + 1.0);
	    i_e[i+1] = f*r;
	    c *= (s=1.0/r);
	  } else {
	      s = f/g;
	      r = sqrt((s*s) + 1.0);
	      i_e[i+1] = g*r;
	      s *= (c=1.0/r);
	    }
	  g = x_d[i+1] - p;
	  r = (x_d[i]-g) * s + 2.0 * c * b;
	  p = s*r;
	  x_d[i+1] = g + p;
	  g = c*r-b;
	  /* Next loop can be omitted if eigenvectors not wanted */
	  for (k=0; k<=i_n-1; k++) {
	    f = x_z[k][i+1];
	    x_z[k][i+1] = s*x_z[k][i] + c*f;
	    x_z[k][i] = c*x_z[k][i]-s*f;
	  }
	}
	x_d[l] = x_d[l]-p;
	i_e[l] = g;
	i_e[m] = 0.0;
      }
    } while (m != l);
  }
}


static void lib_matr_evtred2(int i_n, double **i_a, double o_d[], double o_e[])
/*FUNC**********************************************************************

DESCRIPTION:

Householder reduction of a real, symmetric, matrix a[0,...,n-1][0,...,n-1].
On output, i_a is replaced by the orthogonal matrix Q effecting the
transformation. d[0,...,n-1] returns the diagonal elements of the
tridiagonal matrix, and e[0,...,n-1] the off diagonal elements, e[0]=0.
Since this function only is used to find eigenvalues, it is the same as the
function tred2 above except that some statements are omitted, and i_a contains
no useful information on output.

HOW TO USE THE FUNCTION:

tred2(i_n, i_a, o_d, o_e);

SIDE-EFFECTS:

RETURN VALUE:

****************************************************************************/
{
  int l, k, j, i;
  double scale, hh, h, g, f;

  for (i = i_n - 1; i>=1; i--) {
    l = i-1;
    h = scale = 0.0;
    if (l > 0) {
      for (k=0; k<=l; k++)
	scale += fabs(i_a[i][k]);
      if (scale == 0)
	o_e[i] = i_a[i][l];
      else {
	for (k=0; k<= l; k++) {
	  i_a[i][k] /= scale;
	  h += i_a[i][k]*i_a[i][k];
	}
	f = i_a[i][l];
	g = f>0 ? -sqrt(h) : sqrt(h);
	o_e[i]=scale*g;
	h -= f*g;
	i_a[i][l] = f-g;
	f = 0.0;
	for (j=0; j<=l; j++) {
	  g = 0.0;
	  for (k=0; k<=j; k++)
	    g += i_a[j][k]*i_a[i][k];
	  for (k=j+1; k<=l; k++)
	    g += i_a[k][j]*i_a[i][k];
	  o_e[j] = g/h;
	  f += o_e[j]*i_a[i][j];
	}
	hh = f/(h+h);
	for (j=0; j<=l; j++) {
	  f = i_a[i][j];
	  o_e[j] = g = o_e[j]-hh*f;
	  for (k=0; k<=j; k++)
	    i_a[j][k] -= (f*o_e[k] + g*i_a[i][k]);
	}
      }
    }
    else
      o_e[i] = i_a[i][l];
    o_d[i] = h;
  }
  o_e[0] = 0.0;
  for (i=0; i <= i_n-1; i++)
    o_d[i] = i_a[i][i];
}



static void lib_matr_evtqli(double i_e[], int i_n, double x_d[], int *o_error)

/*FUNC************************************************************************

DESCRIPTION:

QL-algorithm with implicit shifts, to determine the eigenvalues
of a real, symmetric, tridiagonal matrix, or of a real, symmetric
matrix previously reduced by 'tred2'. On input x_d[0,...i_n-1] contains the
diagonal elements of the tridiagonal matrix. On output, it returns the
eigenvalues. The vector i_e[0,...,i_n-1] inputs the subdiagonal elements of the
tridiagonal matrix, with i_e[0] arbitrary. On output i_e is destroyed.
Since we use this function only to find eigenvalues, it is the same as tqli
above, except that some statements are omitted
finding only the eigenvalues, several lines may be omitted, as noted in the
comments.

HOW TO USE THE FUNCTION:

tqli(i_n, i_e, x_d, x_z);

SIDE-EFFECTS:

RETURN VALUE:

***************************************************************************/
{
  int m, l, iter, i;
  double s, r, p, g, f, dd, c, b;

  *o_error = 0;
  for (i=1; i<=i_n-1; i++) i_e[i-1] = i_e[i];
  i_e[i_n-1] = 0.0;
  for (l=0; l<=i_n-1; l++) {
    iter=0;
    do {
      for (m=l; m<=i_n-2; m++) {
	dd = fabs(x_d[m]) + fabs(x_d[m+1]);
	if (fabs(i_e[m])+dd == dd) break;
      }
      if (m != l) {
	if (iter++ == 30) {*o_error = 1; return;}
	g = (x_d[l+1] - x_d[l]) / (2.0*i_e[l]);
	r = sqrt((g*g) + 1.0);
	g = x_d[m] - x_d[l] + i_e[l] /(g + SIGN(r,g));
	s = c = 1.0;
	p = 0.0;
	for (i=m-1; i>=l; i--) {
	  f = s*i_e[i];
	  b = c*i_e[i];
	  if (fabs(f) >= fabs(g)) {
	    c = g/f;
	    r = sqrt((c*c) + 1.0);
	    i_e[i+1] = f*r;
	    c *= (s=1.0/r);
	  } else {
	      s = f/g;
	      r = sqrt((s*s) + 1.0);
	      i_e[i+1] = g*r;
	      s *= (c=1.0/r);
	    }
	  g = x_d[i+1] - p;
	  r = (x_d[i]-g) * s + 2.0 * c * b;
	  p = s*r;
	  x_d[i+1] = g + p;
	  g = c*r-b;
	}
	x_d[l] = x_d[l]-p;
	i_e[l] = g;
	i_e[m] = 0.0;
      }
    } while (m != l);
  }
}


