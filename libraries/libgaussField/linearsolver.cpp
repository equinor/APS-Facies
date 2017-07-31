/* linpack.f -- translated by f2c (version of 23 April 1993  18:34:30). */

/*Include Files:*/
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <ctype.h>
#include <cmath>
#include <cassert>
#include "global_def.h"
#include "lib_message.h"
#include "linearsolver.h"


/* Prototype declarations */
static double dasum(int *n, double *dx, int *incx);

static int daxpy(int *n, double *da, double *dx, 
		  int *incx, double *dy, int *incy);

static double ddot(int *n, double *dx, 
		    int *incx, double *dy, int *incy);

static int dscal(int *n, double *da, 
		  double *dx, int *incx);

static int idamax(int *n, double *dx, int *incx);
static double d_sign(double *x, double *y);








/* Table of constant values */

static int c__1 = 1;


/* $Id: linearsolver.C,v 1.1.1.1 2003/01/10 14:26:17 olia Exp $ */

/*     innholdet i denne filen er hentet fra netlib, ved foresp|rselen */
/*     send dgeco, dgefa,dgesl from linpack blas */
/*    Careful! Anything free comes with no guarantee. */
/*    *** from netlib, Sat Mar 24 21:30:20 MET 1990 *** */
/* Subroutine */ 
int dgeco(double *a, int *lda, int *n, int *ipvt, 
	   double *rcond,double *z)
{
    /* System generated locals */
    int a_dim1, a_offset, i__1, i__2;
    double d__1, d__2;


    /* Local variables */
    static int info;
    static int j, k, l;
    static double s, t;
    static double anorm;
    static double ynorm;
    static int kb;
    static double ek, sm, wk;
    static int kp1;
    static double wkm;


/*     dgeco factors a double precision matrix by gaussian elimination */
/*     and estimates the condition of the matrix. */

/*     if  rcond  is not needed, dgefa is slightly faster. */
/*     to solve  a*x = b , follow dgeco by dgesl. */
/*     to compute  inverse(a)*c , follow dgeco by dgesl. */
/*     to compute  determinant(a) , follow dgeco by dgedi. */
/*     to compute  inverse(a) , follow dgeco by dgedi. */

/*     on entry */

/*        a       double precision(lda, n) */
/*                the matrix to be factored. */

/*        lda     int */
/*                the leading dimension of the array  a . */

/*        n       int */
/*                the order of the matrix  a . */

/*     on return */

/*        a       an upper triangular matrix and the multipliers */
/*                which were used to obtain it. */
/*                the factorization can be written  a = l*u  where */
/*                l  is a product of permutation and unit lower */
/*                triangular matrices and  u  is upper triangular. */

/*        ipvt    int(n) */
/*                an int vector of pivot indices. */

/*        rcond   double precision */
/*                an estimate of the reciprocal condition of  a . */
/*                for the system  a*x = b , relative perturbations */
/*                in  a  and  b  of size  epsilon  may cause */
/*                relative perturbations in  x  of size  epsilon/rcond . 
*/
/*                if  rcond  is so small that the logical expression */
/*                           1.0 + rcond .eq. 1.0 */
/*                is true, then  a  may be singular to working */
/*                precision.  in particular,  rcond  is zero  if */
/*                exact singularity is detected or the estimate */
/*                underflows. */

/*        z       double precision(n) */
/*                a work vector whose contents are usually unimportant. */
/*                if  a  is close to a singular matrix, then  z  is */
/*                an approximate null vector in the sense that */
/*                norm(a*z) = rcond*norm(a)*norm(z) . */

/*     linpack. this version dated 08/14/78 . */
/*     cleve moler, university of new mexico, argonne national lab. */

/*     subroutines and functions */

/*     linpack dgefa */
/*     blas daxpy,ddot,dscal,dasum */
/*     fortran dabs,dmax1,dsign */

/*     internal variables */



/*     compute 1-norm of a */

    /* Parameter adjustments */
    --z;
    --ipvt;
    a_dim1 = *lda;
    a_offset = a_dim1 + 1;
    a -= a_offset;

    /* Function Body */
    anorm = 0.;
    i__1 = *n;
    for (j = 1; j <= i__1; ++j) {
/* Computing MAX */
	d__1 = anorm, d__2 = dasum(n, &a[j * a_dim1 + 1], &c__1);
	anorm = MAXIM(d__1,d__2);
/* L10: */
    }

/*     factor */

    dgefa(&a[a_offset], lda, n, &ipvt[1], &info);

/*     rcond = 1/(norm(a)*(estimate of norm(inverse(a)))) . */
/*     estimate = norm(z)/norm(y) where  a*z = y  and  trans(a)*y = e . */
/*     trans(a)  is the transpose of a .  the components of  e  are */
/*     chosen to cause maximum local growth in the elements of w  where */
/*     trans(u)*w = e .  the vectors are frequently rescaled to avoid */
/*     overflow. */

/*     solve trans(u)*w = e */

    ek = 1.;
    i__1 = *n;
    for (j = 1; j <= i__1; ++j) {
	z[j] = 0.;
/* L20: */
    }
    i__1 = *n;
    for (k = 1; k <= i__1; ++k) {
	if (z[k] != 0.) {
	    d__1 = -z[k];
	    ek = d_sign(&ek, &d__1);
	}
	if ((d__1 = ek - z[k], fabs(d__1)) <= (d__2 = a[k + k * a_dim1], fabs(
		d__2))) {
	    goto L30;
	}
	s = (d__1 = a[k + k * a_dim1], fabs(d__1)) / (d__2 = ek - z[k], fabs(
		d__2));
	dscal(n, &s, &z[1], &c__1);
	ek = s * ek;
L30:
	wk = ek - z[k];
	wkm = -ek - z[k];
	s = fabs(wk);
	sm = fabs(wkm);
	if (a[k + k * a_dim1] == 0.) {
	    goto L40;
	}
	wk /= a[k + k * a_dim1];
	wkm /= a[k + k * a_dim1];
	goto L50;
L40:
	wk = 1.;
	wkm = 1.;
L50:
	kp1 = k + 1;
	if (kp1 > *n) {
	    goto L90;
	}
	i__2 = *n;
	for (j = kp1; j <= i__2; ++j) {
	    sm += (d__1 = z[j] + wkm * a[k + j * a_dim1], fabs(d__1));
	    z[j] += wk * a[k + j * a_dim1];
	    s += (d__1 = z[j], fabs(d__1));
/* L60: */
	}
	if (s >= sm) {
	    goto L80;
	}
	t = wkm - wk;
	wk = wkm;
	i__2 = *n;
	for (j = kp1; j <= i__2; ++j) {
	    z[j] += t * a[k + j * a_dim1];
/* L70: */
	}
L80:
L90:
	z[k] = wk;
/* L100: */
    }
    s = 1. / dasum(n, &z[1], &c__1);
    dscal(n, &s, &z[1], &c__1);

/*     solve trans(l)*y = w */

    i__1 = *n;
    for (kb = 1; kb <= i__1; ++kb) {
	k = *n + 1 - kb;
	if (k < *n) {
	    i__2 = *n - k;
	    z[k] += ddot(&i__2, &a[k + 1 + k * a_dim1], &c__1, &z[k + 1], &
		    c__1);
	}
	if ((d__1 = z[k], fabs(d__1)) <= 1.) {
	    goto L110;
	}
	s = 1. / (d__1 = z[k], fabs(d__1));
	dscal(n, &s, &z[1], &c__1);
L110:
	l = ipvt[k];
	t = z[l];
	z[l] = z[k];
	z[k] = t;
/* L120: */
    }
    s = 1. / dasum(n, &z[1], &c__1);
    dscal(n, &s, &z[1], &c__1);

    ynorm = 1.;

/*     solve l*v = y */

    i__1 = *n;
    for (k = 1; k <= i__1; ++k) {
	l = ipvt[k];
	t = z[l];
	z[l] = z[k];
	z[k] = t;
	if (k < *n) {
	    i__2 = *n - k;
	    daxpy(&i__2, &t, &a[k + 1 + k * a_dim1], &c__1, &z[k + 1], &c__1)
		    ;
	}
	if ((d__1 = z[k], fabs(d__1)) <= 1.) {
	    goto L130;
	}
	s = 1. / (d__1 = z[k], fabs(d__1));
	dscal(n, &s, &z[1], &c__1);
	ynorm = s * ynorm;
L130:
/* L140: */
	;
    }
    s = 1. / dasum(n, &z[1], &c__1);
    dscal(n, &s, &z[1], &c__1);
    ynorm = s * ynorm;

/*     solve  u*z = v */

    i__1 = *n;
    for (kb = 1; kb <= i__1; ++kb) {
	k = *n + 1 - kb;
	if ((d__1 = z[k], fabs(d__1)) <= (d__2 = a[k + k * a_dim1], fabs(d__2)))
		 {
	    goto L150;
	}
	s = (d__1 = a[k + k * a_dim1], fabs(d__1)) / (d__2 = z[k], fabs(d__2));
	dscal(n, &s, &z[1], &c__1);
	ynorm = s * ynorm;
L150:
	if (a[k + k * a_dim1] != 0.) {
	    z[k] /= a[k + k * a_dim1];
	}
	if (a[k + k * a_dim1] == 0.) {
	    z[k] = 1.;
	}
	t = -z[k];
	i__2 = k - 1;
	daxpy(&i__2, &t, &a[k * a_dim1 + 1], &c__1, &z[1], &c__1);
/* L160: */
    }
/*     make znorm = 1.0 */
    s = 1. / dasum(n, &z[1], &c__1);
    dscal(n, &s, &z[1], &c__1);
    ynorm = s * ynorm;

    if (anorm != 0.) {
	*rcond = ynorm / anorm;
    }
    if (anorm == 0.) {
	*rcond = 0.;
    }
    return 0;
} /* dgeco */

/* Subroutine */ 
int dgefa(double *a, 
	   int *lda, int *n, int *ipvt, int *info)
{
    /* System generated locals */
    int a_dim1, a_offset, i__1, i__2, i__3;

    /* Local variables */
    static int j, k, l;
    static double t;
    static int kp1, nm1;


/*     dgefa factors a double precision matrix by gaussian elimination. */

/*     dgefa is usually called by dgeco, but it can be called */
/*     directly with a saving in time if  rcond  is not needed. */
/*     (time for dgeco) = (1 + 9/n)*(time for dgefa) . */

/*     on entry */

/*        a       double precision(lda, n) */
/*                the matrix to be factored. */

/*        lda     int */
/*                the leading dimension of the array  a . */

/*        n       int */
/*                the order of the matrix  a . */

/*     on return */

/*        a       an upper triangular matrix and the multipliers */
/*                which were used to obtain it. */
/*                the factorization can be written  a = l*u  where */
/*                l  is a product of permutation and unit lower */
/*                triangular matrices and  u  is upper triangular. */

/*        ipvt    int(n) */
/*                an int vector of pivot indices. */

/*        info    int */
/*                = 0  normal value. */
/*                = k  if  u(k,k) .eq. 0.0 .  this is not an error */
/*                     condition for this subroutine, but it does */
/*                     indicate that dgesl or dgedi will divide by zero */
/*                     if called.  use  rcond  in dgeco for a reliable */
/*                     indication of singularity. */

/*     linpack. this version dated 08/14/78 . */
/*     cleve moler, university of new mexico, argonne national lab. */

/*     subroutines and functions */

/*     blas daxpy,dscal,idamax */

/*     internal variables */



/*     gaussian elimination with partial pivoting */

    /* Parameter adjustments */
    --ipvt;
    a_dim1 = *lda;
    a_offset = a_dim1 + 1;
    a -= a_offset;

    /* Function Body */
    *info = 0;
    nm1 = *n - 1;
    if (nm1 < 1) {
	goto L70;
    }
    i__1 = nm1;
    for (k = 1; k <= i__1; ++k) {
	kp1 = k + 1;

/*        find l = pivot index */

	i__2 = *n - k + 1;
	l = idamax(&i__2, &a[k + k * a_dim1], &c__1) + k - 1;
	ipvt[k] = l;

/*        zero pivot implies this column already triangularized */

	if (a[l + k * a_dim1] == 0.) {
	    goto L40;
	}

/*           interchange if necessary */

	if (l == k) {
	    goto L10;
	}
	t = a[l + k * a_dim1];
	a[l + k * a_dim1] = a[k + k * a_dim1];
	a[k + k * a_dim1] = t;
L10:

/*           compute multipliers */

	t = -1. / a[k + k * a_dim1];
	i__2 = *n - k;
	dscal(&i__2, &t, &a[k + 1 + k * a_dim1], &c__1);

/*           row elimination with column indexing */

	i__2 = *n;
	for (j = kp1; j <= i__2; ++j) {
	    t = a[l + j * a_dim1];
	    if (l == k) {
		goto L20;
	    }
	    a[l + j * a_dim1] = a[k + j * a_dim1];
	    a[k + j * a_dim1] = t;
L20:
	    i__3 = *n - k;
	    daxpy(&i__3, &t, &a[k + 1 + k * a_dim1], &c__1, &a[k + 1 + j * 
		    a_dim1], &c__1);
/* L30: */
	}
	goto L50;
L40:
	*info = k;
L50:
/* L60: */
	;
    }
L70:
    ipvt[*n] = *n;
    if (a[*n + *n * a_dim1] == 0.) {
	*info = *n;
    }
    return 0;
} /* dgefa */

/* Subroutine */ 
int dgesl(double *a, int *lda, int *n, int *ipvt, 
	   double *b, int *job)
{
    /* System generated locals */
    int a_dim1, a_offset, i__1, i__2;

    /* Local variables */
    static int k, l;
    static double t;
    static int kb, nm1;


/*     dgesl solves the double precision system */
/*     a * x = b  or  trans(a) * x = b */
/*     using the factors computed by dgeco or dgefa. */

/*     on entry */

/*        a       double precision(lda, n) */
/*                the output from dgeco or dgefa. */

/*        lda     int */
/*                the leading dimension of the array  a . */

/*        n       int */
/*                the order of the matrix  a . */

/*        ipvt    int(n) */
/*                the pivot vector from dgeco or dgefa. */

/*        b       double precision(n) */
/*                the right hand side vector. */

/*        job     int */
/*                = 0         to solve  a*x = b , */
/*                = nonzero   to solve  trans(a)*x = b  where */
/*                            trans(a)  is the transpose. */

/*     on return */

/*        b       the solution vector  x . */

/*     error condition */

/*        a division by zero will occur if the input factor contains a */
/*        zero on the diagonal.  technically this indicates singularity */
/*        but it is often caused by improper arguments or improper */
/*        setting of lda .  it will not occur if the subroutines are */
/*        called correctly and if dgeco has set rcond .gt. 0.0 */
/*        or dgefa has set info .eq. 0 . */

/*     to compute  inverse(a) * c  where  c  is a matrix */
/*     with  p  columns */
/*           call dgeco(a,lda,n,ipvt,rcond,z) */
/*           if (rcond is too small) go to ... */
/*           do 10 j = 1, p */
/*              call dgesl(a,lda,n,ipvt,c(1,j),0) */
/*        10 continue */

/*     linpack. this version dated 08/14/78 . */
/*     cleve moler, university of new mexico, argonne national lab. */

/*     subroutines and functions */

/*     blas daxpy,ddot */

/*     internal variables */


    /* Parameter adjustments */
    --b;
    --ipvt;
    a_dim1 = *lda;
    a_offset = a_dim1 + 1;
    a -= a_offset;

    /* Function Body */
    nm1 = *n - 1;
    if (*job != 0) {
	goto L50;
    }

/*        job = 0 , solve  a * x = b */
/*        first solve  l*y = b */

    if (nm1 < 1) {
	goto L30;
    }
    i__1 = nm1;
    for (k = 1; k <= i__1; ++k) {
	l = ipvt[k];
	t = b[l];
	if (l == k) {
	    goto L10;
	}
	b[l] = b[k];
	b[k] = t;
L10:
	i__2 = *n - k;
	daxpy(&i__2, &t, &a[k + 1 + k * a_dim1], &c__1, &b[k + 1], &c__1);
/* L20: */
    }
L30:

/*        now solve  u*x = y */

    i__1 = *n;
    for (kb = 1; kb <= i__1; ++kb) {
	k = *n + 1 - kb;
	b[k] /= a[k + k * a_dim1];
	t = -b[k];
	i__2 = k - 1;
	daxpy(&i__2, &t, &a[k * a_dim1 + 1], &c__1, &b[1], &c__1);
/* L40: */
    }
    goto L100;
L50:

/*        job = nonzero, solve  trans(a) * x = b */
/*        first solve  trans(u)*y = b */

    i__1 = *n;
    for (k = 1; k <= i__1; ++k) {
	i__2 = k - 1;
	t = ddot(&i__2, &a[k * a_dim1 + 1], &c__1, &b[1], &c__1);
	b[k] = (b[k] - t) / a[k + k * a_dim1];
/* L60: */
    }

/*        now solve trans(l)*x = y */

    if (nm1 < 1) {
	goto L90;
    }
    i__1 = nm1;
    for (kb = 1; kb <= i__1; ++kb) {
	k = *n - kb;
	i__2 = *n - k;
	b[k] += ddot(&i__2, &a[k + 1 + k * a_dim1], &c__1, &b[k + 1], &c__1);
	l = ipvt[k];
	if (l == k) {
	    goto L70;
	}
	t = b[l];
	b[l] = b[k];
	b[k] = t;
L70:
/* L80: */
	;
    }
L90:
L100:
    return 0;
} /* dgesl */

static double dasum(int *n, double *dx, int *incx)
{
    /* System generated locals */
    int i__1, i__2;
    double ret_val, d__1, d__2, d__3, d__4, d__5, d__6;

    /* Local variables */
    static int i, m;
    static double dtemp;
    static int nincx, mp1;


/*     takes the sum of the absolute values. */
/*     jack dongarra, linpack, 3/11/78. */


    /* Parameter adjustments */
    --dx;

    /* Function Body */
    ret_val = 0.;
    dtemp = 0.;
    if (*n <= 0) {
	return ret_val;
    }
    if (*incx == 1) {
	goto L20;
    }

/*        code for increment not equal to 1 */

    nincx = *n * *incx;
    i__1 = nincx;
    i__2 = *incx;
    for (i = 1; i__2 < 0 ? i >= i__1 : i <= i__1; i += i__2) {
	dtemp += (d__1 = dx[i], fabs(d__1));
/* L10: */
    }
    ret_val = dtemp;
    return ret_val;

/*        code for increment equal to 1 */


/*        clean-up loop */

L20:
    m = *n % 6;
    if (m == 0) {
	goto L40;
    }
    i__2 = m;
    for (i = 1; i <= i__2; ++i) {
	dtemp += (d__1 = dx[i], fabs(d__1));
/* L30: */
    }
    if (*n < 6) {
	goto L60;
    }
L40:
    mp1 = m + 1;
    i__2 = *n;
    for (i = mp1; i <= i__2; i += 6) {
	dtemp = dtemp + (d__1 = dx[i], fabs(d__1)) + (d__2 = dx[i + 1], fabs(
		d__2)) + (d__3 = dx[i + 2], fabs(d__3)) + (d__4 = dx[i + 3], 
		fabs(d__4)) + (d__5 = dx[i + 4], fabs(d__5)) + (d__6 = dx[i + 5]
		, fabs(d__6));
/* L50: */
    }
L60:
    ret_val = dtemp;
    return ret_val;
} /* dasum */

/* Subroutine */ 
static int daxpy(int *n, double *da, double *dx, 
		  int *incx, double *dy, int *incy)
{
    /* System generated locals */
    int i__1;

    /* Local variables */
    static int i, m, ix, iy, mp1;


/*     constant times a vector plus a vector. */
/*     uses unrolled loops for increments equal to one. */
/*     jack dongarra, linpack, 3/11/78. */


    /* Parameter adjustments */
    --dy;
    --dx;

    /* Function Body */
    if (*n <= 0) {
	return 0;
    }
    if (*da == 0.) {
	return 0;
    }
    if (*incx == 1 && *incy == 1) {
	goto L20;
    }

/*        code for unequal increments or equal increments */
/*          not equal to 1 */

    ix = 1;
    iy = 1;
    if (*incx < 0) {
	ix = (-(*n) + 1) * *incx + 1;
    }
    if (*incy < 0) {
	iy = (-(*n) + 1) * *incy + 1;
    }
    i__1 = *n;
    for (i = 1; i <= i__1; ++i) {
	dy[iy] += *da * dx[ix];
	ix += *incx;
	iy += *incy;
/* L10: */
    }
    return 0;

/*        code for both increments equal to 1 */


/*        clean-up loop */

L20:
    m = *n % 4;
    if (m == 0) {
	goto L40;
    }
    i__1 = m;
    for (i = 1; i <= i__1; ++i) {
	dy[i] += *da * dx[i];
/* L30: */
    }
    if (*n < 4) {
	return 0;
    }
L40:
    mp1 = m + 1;
    i__1 = *n;
    for (i = mp1; i <= i__1; i += 4) {
	dy[i] += *da * dx[i];
	dy[i + 1] += *da * dx[i + 1];
	dy[i + 2] += *da * dx[i + 2];
	dy[i + 3] += *da * dx[i + 3];
/* L50: */
    }
    return 0;
} /* daxpy */

static double ddot(int *n, double *dx, 
		    int *incx, double *dy, int *incy)
{
    /* System generated locals */
    int i__1;
    double ret_val;

    /* Local variables */
    static int i, m;
    static double dtemp;
    static int ix, iy, mp1;


/*     forms the dot product of two vectors. */
/*     uses unrolled loops for increments equal to one. */
/*     jack dongarra, linpack, 3/11/78. */


    /* Parameter adjustments */
    --dy;
    --dx;

    /* Function Body */
    ret_val = 0.;
    dtemp = 0.;
    if (*n <= 0) {
	return ret_val;
    }
    if (*incx == 1 && *incy == 1) {
	goto L20;
    }

/*        code for unequal increments or equal increments */
/*          not equal to 1 */

    ix = 1;
    iy = 1;
    if (*incx < 0) {
	ix = (-(*n) + 1) * *incx + 1;
    }
    if (*incy < 0) {
	iy = (-(*n) + 1) * *incy + 1;
    }
    i__1 = *n;
    for (i = 1; i <= i__1; ++i) {
	dtemp += dx[ix] * dy[iy];
	ix += *incx;
	iy += *incy;
/* L10: */
    }
    ret_val = dtemp;
    return ret_val;

/*        code for both increments equal to 1 */


/*        clean-up loop */

L20:
    m = *n % 5;
    if (m == 0) {
	goto L40;
    }
    i__1 = m;
    for (i = 1; i <= i__1; ++i) {
	dtemp += dx[i] * dy[i];
/* L30: */
    }
    if (*n < 5) {
	goto L60;
    }
L40:
    mp1 = m + 1;
    i__1 = *n;
    for (i = mp1; i <= i__1; i += 5) {
	dtemp = dtemp + dx[i] * dy[i] + dx[i + 1] * dy[i + 1] + dx[i + 2] * 
		dy[i + 2] + dx[i + 3] * dy[i + 3] + dx[i + 4] * dy[i + 4];
/* L50: */
    }
L60:
    ret_val = dtemp;
    return ret_val;
} /* ddot */

/* Subroutine */ 
static int dscal(int *n, double *da, 
		  double *dx, int *incx)
{
    /* System generated locals */
    int i__1, i__2;

    /* Local variables */
    static int i, m, nincx, mp1;


/*     scales a vector by a constant. */
/*     uses unrolled loops for increment equal to one. */
/*     jack dongarra, linpack, 3/11/78. */


    /* Parameter adjustments */
    --dx;

    /* Function Body */
    if (*n <= 0) {
	return 0;
    }
    if (*incx == 1) {
	goto L20;
    }

/*        code for increment not equal to 1 */

    nincx = *n * *incx;
    i__1 = nincx;
    i__2 = *incx;
    for (i = 1; i__2 < 0 ? i >= i__1 : i <= i__1; i += i__2) {
	dx[i] = *da * dx[i];
/* L10: */
    }
    return 0;

/*        code for increment equal to 1 */


/*        clean-up loop */

L20:
    m = *n % 5;
    if (m == 0) {
	goto L40;
    }
    i__2 = m;
    for (i = 1; i <= i__2; ++i) {
	dx[i] = *da * dx[i];
/* L30: */
    }
    if (*n < 5) {
	return 0;
    }
L40:
    mp1 = m + 1;
    i__2 = *n;
    for (i = mp1; i <= i__2; i += 5) {
	dx[i] = *da * dx[i];
	dx[i + 1] = *da * dx[i + 1];
	dx[i + 2] = *da * dx[i + 2];
	dx[i + 3] = *da * dx[i + 3];
	dx[i + 4] = *da * dx[i + 4];
/* L50: */
    }
    return 0;
} /* dscal */

static int idamax(int *n, double *dx, int *incx)
{
    /* System generated locals */
    int ret_val, i__1;
    double d__1;

    /* Local variables */
    static double  dmax_;
    static int i, ix;


/*     finds the index of element having max. absolute value. */
/*     jack dongarra, linpack, 3/11/78. */


    /* Parameter adjustments */
    --dx;

    /* Function Body */
    ret_val = 0;
    if (*n < 1) {
	return ret_val;
    }
    ret_val = 1;
    if (*n == 1) {
	return ret_val;
    }
    if (*incx == 1) {
	goto L20;
    }

/*        code for increment not equal to 1 */

    ix = 1;
    dmax_ = fabs(dx[1]);
    ix += *incx;
    i__1 = *n;
    for (i = 2; i <= i__1; ++i) {
	if ((d__1 = dx[ix], fabs(d__1)) <= dmax_) {
	    goto L5;
	}
	ret_val = i;
	dmax_ = (d__1 = dx[ix], fabs(d__1));
L5:
	ix += *incx;
/* L10: */
    }
    return ret_val;

/*        code for increment equal to 1 */

L20:
    dmax_ = fabs(dx[1]);
    i__1 = *n;
    for (i = 2; i <= i__1; ++i) {
	if ((d__1 = dx[i], fabs(d__1)) <= dmax_) {
	    goto L30;
	}
	ret_val = i;
	dmax_ = (d__1 = dx[i], fabs(d__1));
L30:
	;
    }
    return ret_val;
} /* idamax */


static double d_sign(double *x, double *y)
{
  double z;
  if(*y >= 0){
    z = fabs(*x);
  }
  else {
    z = -fabs(*x);
  }
  return z;
}



/* Subroutine */ 
int cholesky_fact(int *i_mdim__,
		  int *i_dim__,
		  double *x_mtx__)
{
    /* System generated locals */
    int x_mtx_dim1, x_mtx_offset, i__1, i__2, i__3;
    double d__1;

    /* Local variables */
    static int l_i__, l_j__, l_k__;
    static double l_r__;


/*     Description: */
/*     Factorizes the positive symmetric matrix I_MTX */
/*     into G times Gtransposed, when G is a lower */
/*     triangular matrix. G is stored in the lower part of */
/*     I_MTX on output. */

/*     Created  by:KS\                        Date: 001190 */

/*     Modified by:                        Date: */

/* -----------------------------------------------CHOLESKY_FACT */


/*     Input variable(s): */
/*                  . */
/*     Input/output variable(s): */
/*                  Matrix to be decomposed on input, decomposed */
/*                  matrix stored in lower triangular part on output. */
/*                  . */
/*     Output variable(s): */
/*                  . */
/*     Workspace: */
/*                  . */
/* -----------------------------------------------CHOLESKY_FACT */

/*     Local variable(s): */
/*                  . */
/*     External function(s): */
/*                  . */
/* ===============================================CHOLESKY_FACT */

    /* Parameter adjustments */
    x_mtx_dim1 = *i_mdim__;
    x_mtx_offset = x_mtx_dim1 + 1;
    x_mtx__ -= x_mtx_offset;

    /* Function Body */
    i__1 = *i_dim__;
    for (l_i__ = 1; l_i__ <= i__1; ++l_i__) {
	if (x_mtx__[l_i__ + l_i__ * x_mtx_dim1] <= 1e-10) {
	    goto L900;
	}
	i__2 = l_i__ - 1;
	for (l_j__ = 1; l_j__ <= i__2; ++l_j__) {
	    l_r__ = 0.;
	    i__3 = l_j__ - 1;
	    for (l_k__ = 1; l_k__ <= i__3; ++l_k__) {
		l_r__ += x_mtx__[l_i__ + l_k__ * x_mtx_dim1] * x_mtx__[l_j__ 
			+ l_k__ * x_mtx_dim1];
	    }
	    x_mtx__[l_i__ + l_j__ * x_mtx_dim1] = (x_mtx__[l_i__ + l_j__ * 
		    x_mtx_dim1] - l_r__) / x_mtx__[l_j__ + l_j__ * x_mtx_dim1]
		    ;
	}
	l_r__ = 0.;
	i__2 = l_i__ - 1;
	for (l_k__ = 1; l_k__ <= i__2; ++l_k__) {
/* Computing 2nd power */
	    d__1 = x_mtx__[l_i__ + l_k__ * x_mtx_dim1];
	    l_r__ += d__1 * d__1;
	}
	l_r__ = x_mtx__[l_i__ + l_i__ * x_mtx_dim1] - l_r__;
	if (l_r__ <= 1e-12) {
	    goto L900;
	}
	x_mtx__[l_i__ + l_i__ * x_mtx_dim1] = sqrt(l_r__);
    }
    goto L1000;
L900:
    moduleError(KERNEL,"cholesky_fact",
		"%s\n%s",
		"Singular matrix to be cholesky factorized.",
		"Perhaps the correlation between neighbour nodes are too large?");
L1000:
    return 0;
} /* cholesky_fact */









