/*
  DESCRIPTION:
  Generating stocastic variables from different distributions
  The module contains the following functions:

  PUBLIC MODULE UNIT(S):
  double lib_ran_unif01(unsigned int *x_seed)
  int lib_ran_iunif(int i_min, int i_max, unsigned int *x_seed)
  void lib_ran_norm01(unsigned int *x_seed, double *o_x1, double *o_x2)
  int lib_ran_mninit(int i_p, double **i_cov, double **o_ud)
  void lib_ran_mn(int i_p, double **i_ud, double *i_e, unsigned int *x_seed,
                  double *o_mn)
  double lib_ran_dunif(double i_min, double i_max, unsigned int *x_seed)
  double lib_ran_triang(double i_min, double i_mode, double i_max,
                        unsigned int *x_seed)
  int lib_ran_binomial(int i_n, double i_p, unsigned int *x_seed)
  int lib_ran_multnomial(double *i_p,int i_k, unsigned int *x_seed)
  double lib_ran_beta(int i_r, int i_s, unsigned int *x_seed)
  double lib_ran_beta_r(double alpha, double beta, unsigned int *x_seed)
  double lib_ran_gammadist(int i_p, double i_theta, unsigned int *x_seed)
  double lib_ran_gamma(double alpha, double beta, unsigned int *x_seed)

  PRIVATE MODULE UNIT(S):

  FILE DECLARING EXTERNAL ROUTINES: "lib_ran.h"

  FILE(S) WITH REFERENCED ROUTINE(S): "lib_matr.c"


*/

/*INCLUDE FILES:*/

#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <limits.h>
//#include "utl.h"
#include "lib_matr.h"
#include "lib_ran.h"



/* MODULE SPESIFIC DEFINITIONS:*/

# define  G_MULTIPLIER   69069
# define  G_SHIFT            1
# define  G_MODULUS      256*256*256*128
# define  G_INVMOD       ( (double) 1 / ((double) G_MODULUS )) / ( (double) 2 )
# define  G_PI           3.1415927

double lib_ran_unif01(
   unsigned int *x_seed)
/*FUNC******************************************************************

DESCRIPTION:

Generates a uniform[0,1] variable using the congruential
generator given in ripley: stochastic simulation, p. 46.

HOW TO USE THE FUNCTION:

l_unif = lib_ran_unif01(x_seed)

SIDE-EFFECTS: The start-seed should be either negativ or big and positiv.

RETURN VALUE: The pseudo-random number in [0,1], both inclusive.

***********************************************************************/
{
 double l_ran;

 *x_seed = G_MULTIPLIER * *x_seed + G_SHIFT;
 l_ran = (double) *x_seed * G_INVMOD;
 return(l_ran);
}



int lib_ran_iunif(
   int          i_min,
   int          i_max,
   unsigned int         *x_seed)
/*FUNC******************************************************************

DESCRIPTION:

Generates a uniformly distributed random integer in the range
[i_min,i_max]. If i_min > i_max, the numbers are swapped.
x_seed is seed for the random number generator lib_ran_unif01()

HOW TO USE THE FUNCTION:

l_int = lib_ran_iunif(i_min,i_max,x_seed)

SIDE-EFFECTS: The start-seed should be either negativ or big and positiv.

RETURN VALUE: The pseudo-random int in [i_min,i_max], both inclusive.

***********************************************************************/
{
 int         l_temp, l_range, l_int;
 double      l_ran;

/* If min > max, swap the (local copies of the) variables. */
 if(i_max < i_min) {
   l_temp = i_max;
   i_max = i_min;
   i_min = l_temp;
 }

 l_ran   = lib_ran_unif01(x_seed);
 l_range = i_max - i_min + 1;
 l_int   = (int) (l_ran * l_range) + i_min;

/* If l_ran is 1.0, l_int will become i_max+1, so we subtract 1 in this case */
 if (l_int == (i_max + 1) )
   l_int = l_int - 1;

 return(l_int);
}


double lib_ran_dunif(
   double i_min,
   double i_max,
   unsigned int *x_seed)
/*FUNC**********************************************************************

DESCRIPTION:
  Generates a uniform distributed random number (double) in the range
[i_min,i_max]. If i_min > i_max the numbers are swapped. x_seed is seed for
lib_ran_unif01.

HOW TO USE THE FUNCTION:
  l_uni = lib_ran_dunif(i_min, i_max, x_seed);

SIDE-EFFECTS: The start-seed should be either negativ or big and positiv.

RETURN VALUE: The pseudo-random double number.

***************************************************************************/
{
  double l_temp, l_range, l_u;

  if (i_max < i_min) {
    l_temp = i_max;
    i_max = i_min;
    i_min = l_temp;
  }

  l_u = lib_ran_unif01(x_seed);
  l_range = i_max - i_min;
  l_u = (l_u * l_range) + i_min;

  return(l_u);
}



void lib_ran_norm01(
   unsigned int *x_seed,
   double *o_x1,
   double *o_x2)
/*FUNC***********************************************************************

DESCRIPTION:

Generate two independent normal(0,1)-distributed numbers, using the
Box-Muller method.  Reference: Ripley p.54.

HOW TO USE THE FUNCTION:

lib_ran_norm01(unsigned int x_seed, double o_x1, double o_x2)

SIDE-EFFECTS: The start-seed should be either negativ or big and positiv.

RETURN VALUE: void

***************************************************************************/
{
  double l_u1, l_u2;

/* First generate two uniform(0,1)-numbers: */
  l_u1 = lib_ran_unif01(x_seed);
  l_u2 = lib_ran_unif01(x_seed);

/* Then compute two normal(0,1)-numbers: */
  *o_x1 = sqrt(-2.0*log(l_u1)) * cos(2.0*G_PI*l_u2);
  *o_x2 = sqrt(-2.0*log(l_u1)) * sin(2.0*G_PI*l_u2);
}



int lib_ran_mninit(
   int i_p,  /* The dimension of the multinormal vector. */
   double **i_cov,   /* The covariance matrix.  */
   double **o_ud)  /* The spectral decomposition: i_cov=o_ud*o_ud' */
/*FUNC*************************************************************************

DESCRIPTION:
Initializes the matrix o_ud for use in lib_ran_mn.  The matrix o_ud is the
product of the SVD-decomposition of the covariance matrix i_cov and the
square root of the eigenvalues.
This function can be used to check positive definiteness of a covariance
matrix.

HOW TO USE THE FUNCTION:

i = lib_ran_mninit(i_p, i_cov, o_ud)

SIDE-EFFECTS:

RETURN VALUE: 0 if ok, 1 if the some eigenvalues undetermined, or i_cov
              not pos. def.

**************************************************************************/
{
/* local variables  */
  int l_i, l_j, l_neg_eig;
  int l_error = 0;
  int l_return = 0, *l_negind;
  double l_a, **l_eigvec, *l_eigval;

  l_eigvec = (double **) Mmatrix_2d(0,i_p-1,0,i_p-1,sizeof(double),1);
  l_eigval = (double *) Mmatrix_1d(0,i_p-1,sizeof(double),1);
  l_negind = (int *) Mmatrix_1d(0, i_p-1, sizeof(int),1);

  lib_matr_eigen(i_cov, i_p, l_eigvec, l_eigval, &l_error);
  if (l_error > 0) {
    fprintf(stderr, "Error: Unsuccesful decomposition, ");
    fprintf(stderr, "not all eigenvalues determined.\n");
    l_return = 1;
  }

  l_neg_eig = 0;
  for (l_i=0; l_i <= i_p-1; l_i++) {
    l_a = l_eigval[l_i];
    if (l_a >= 0.0) {
      l_a = sqrt(l_a);
      for (l_j=0; l_j <= i_p-1; l_j++)
	o_ud[l_j][l_i] = l_eigvec[l_j][l_i] * l_a;
    }
    else {
      l_negind[l_neg_eig] = l_i;
      l_neg_eig++;
    }
  }

  if (l_neg_eig > 0) {
    fprintf(stderr,"Error: Unsuccesful decomposition: %d ", l_neg_eig);
    fprintf(stderr,"negative eigenvalue(s):\n");
    for (l_i=0; l_i < l_neg_eig; l_i++)
      fprintf(stderr, "Eigenvalue no. %d : %f\n",l_negind[l_i],
	      l_eigval[l_negind[l_i]]);
    l_return = 1;
  }

  l_negind = (int *) Fmatrix_1d(&l_negind[0]);
  l_eigval = (double *) Fmatrix_1d(&l_eigval[0]);
  l_eigvec = (double **)Fmatrix_2d(&l_eigvec[0][0], &l_eigvec[0]);

  return(l_return);
}


void lib_ran_mn(int i_p, /* Dimension of the stochastic vector */
                double **i_ud, /*The singular value dec. of the cov. matrix */
		double *i_e, /* The expectation vector of mn-distribution */
		unsigned int *x_seed,  /*Seed to the random generator */
		double *o_mn)  /*Multinormal distributed vector */
/*FUNC*************************************************************************

DESCRIPTION:

Generates a stochastic i_p dimensional vector multinormaly distributed.
Before the routine is called the matrix i_ud must be initialised by a call
lib_ran_mninit.

HOW TO USE THE FUNCTION:

lib_ran_mn(i_p, i_ud, i_e, x_seed, o_mn);

SIDE-EFFECTS:

RETURN VALUE:  void

**************************************************************************/
{
/* local variables  */
  int l_i;
  double **l_norm,**l_mn, **l_e, l_x1, l_x2;

  l_e = (double **) Mmatrix_2d(0,i_p,0,0,sizeof(double),1);
  l_norm = (double **) Mmatrix_2d(0,i_p,0,0,sizeof(double),1);
  l_mn = (double **) Mmatrix_2d(0,i_p,0,0,sizeof(double),1);

  /* Creates i_p N(0,1) pseudo-random numbers in l_norm */

  for (l_i=0; l_i<=i_p-1; l_i=l_i+2) {
    lib_ran_norm01(x_seed, &l_x1, &l_x2);
    l_norm[l_i][0] = l_x1;
    l_norm[l_i+1][0] = l_x2;
  }
  for (l_i=0; l_i<=i_p-1; l_i++)
    l_e[l_i][0] = i_e[l_i];

  /* Multiply random-vector l_norm by the SVD decomposition i_ud.
     Add the expectation.  */

  lib_matr_prod(i_ud, l_norm, i_p, i_p, 1, l_mn);
  lib_matr_add(l_e, i_p, 1, l_mn);

  for (l_i=0; l_i <= i_p-1; l_i++)
    o_mn[l_i] = l_mn[l_i][0];

  l_mn = (double **)Fmatrix_2d((char **) &l_mn[0][0], (char *)&l_mn[0]);
  l_norm = (double **)Fmatrix_2d((char **) &l_norm[0][0], (char *)&l_norm[0]);
  l_e = (double **)Fmatrix_2d((char **) &l_e[0][0], (char *)&l_e[0]);
}


double lib_ran_triang(
   double i_min,
   double i_mode,
   double i_max,
   unsigned int *x_seed)
/*FUNC***********************************************************************

DESCRIPTION:

Generates a triangular(i_min, i_mode, i_max) distributed number. If not
i_min <= i_mode <= i_max the three numbers will be repermuted to match this
requirement.

HOW TO USE THE FUNCTION:

l_triang = lib_ran_triang(i_min, i_mode, i_max, x_seed);

SIDE-EFFECTS: The start-seed should be either negativ or big and positiv.

RETURN VALUE: A double triangular distributed number.

*****************************************************************************/
{
  double l_temp, l_uni, l_triang;

/* First make i_min < i_max */
  if (i_min > i_max) {
    l_temp = i_max;
    i_max = i_min;
    i_min = l_temp;
  }

/* Then make i_mode < i_max */
  if (i_mode > i_max) {
    l_temp = i_mode;
    i_mode =i_max;
    i_max = l_temp;
  }

/* And finally make i_min < i_mode  */
  if (i_mode < i_min) {
    l_temp = i_mode;
    i_mode = i_min;
    i_min = l_temp;
  }

/* Generate a random(0,1) - number */

  l_uni = lib_ran_unif01(x_seed);

/* Generate the triangular distributed number */

  if (i_min == i_max) l_triang = i_min;
  else if (l_uni < ((i_mode - i_min) / (i_max - i_min)))
    l_triang = i_min + sqrt(l_uni * (i_mode - i_min) * (i_max - i_min));
  else
    l_triang = i_max - sqrt((1 - l_uni) * (i_max - i_mode) * (i_max - i_min));

  return(l_triang);

}


int lib_ran_binomial(
   int i_n,
   double i_p,
   unsigned int *x_seed)
/*FUNC***********************************************************************

DESCRIPTION:

Generates a binomial(i_n,i_p) distributed number, by the simplest (and not most
efficient) method. Generates i_n uniformly distributed numbers and return the
number of these which are < i_p.

HOW TO USE THE FUNCTION:

l_bin = lib_ran_binomial(i_n, i_p, x_seed);

SIDE-EFFECTS: The start-seed should by either negativ or big and positiv.

RETURN VALUE: A binomial distributed integer.

****************************************************************************/
{
  int l_i, l_count = 0;
  double l_u;

  for (l_i = 1; l_i <= i_n; l_i++) {
    l_u = lib_ran_unif01(x_seed);
    if (l_u < i_p)
      l_count++;
  }

  return(l_count);
}


int lib_ran_multnomial(
   double *i_p,
   int i_k,
   unsigned int *x_seed)
/*FUNC***********************************************************************

DESCRIPTION:

Generates a multinomial distributed number, by the simplest (and not most
efficient) method. i_p is a vector consisting the probabilities. Return
value is class number. The sum of probabilities has to be 1.

HOW TO USE THE FUNCTION:

l_mult = lib_ran_multnomial(i_p, &x_seed);

SIDE-EFFECTS: The start-seed should by either negativ or big and positiv.

RETURN VALUE: A multinomial distributed variabel.

****************************************************************************/
{
  int l_class = 0;
  double l_u,l_sump;

  l_u = lib_ran_unif01(x_seed);
  l_sump=i_p[0];
  while(l_u>l_sump)
    {
     l_class +=1;
     l_sump += i_p[l_class];
   }
  return(l_class);
}





double lib_ran_beta(int i_r, int i_s, unsigned int *x_seed)
/*FUNC********************************************************************

DESCRIPTION:

Generates a beta(r,s) distributed random number (double).  x_seed is seed
for lib_ran_unif01.

The following properties are used:

If U is uniform[0,1], then -ln(U) is gamma(1,1).

If Y1 is gamma(p,t) and Y2 is gamma(q,t), then Y1 + Y2 is gamma(p+q,t)
                                    and Y1/(Y1+Y2) is beta(p,q).

NB:  See also lib_ran_beta_r, that takes nonintegral parameters!


HOW TO USE THE FUNCTION:   l_beta = lib_ran_beta(r,s,x_seed)

SIDE-EFFECTS:  The start-seed should be either negative or big and positive.

RETURN VALUE:  The beta distributed random variable.

*************************************************************************/
{
  double l_y1, l_y2, l_unif;
  int    l_m;
  double r_beta;

  l_y1=0;
  l_y2=0;

  for (l_m = 1; l_m <= i_r; l_m++) {
    do {
      l_unif = lib_ran_unif01(x_seed);
    } while (l_unif <= 0);
    l_y1 = l_y1 - log(l_unif);
  }

  for (l_m = 1; l_m <= i_s; l_m++) {
    do {
      l_unif = lib_ran_unif01(x_seed);
    } while (l_unif <= 0);
    l_y2 = l_y2 - log(l_unif);
  }

  r_beta = l_y1 / (l_y1 + l_y2);

  return r_beta;
}


double lib_ran_beta_r(double alpha, double beta,unsigned int *x_seed)
/*FUNC*************************************************************

Name:		lib_ran_beta_r
Syntax:
Description:   Generates a beta random value with
nonintegral parameters alpha and beta, Using  Theorem 3.6.2 p.82
in R. Y. Rubensteins book Simulation and the monte carlo method.
Let U_{1} and U_{2} be two uniform variates from U(0,1) and
let Y_{1}=U_{1}^{1/alpha} and Y_{2}=U_{2}^{1/beta}. If Y_{1}+Y_{2} >1,
then
          Y_{1}
X = --------------- is from Be(alpha,beta)
     Y_{1} + Y_{2}


*********************************************************/
{
  double uniform01,y1,y2,x;

  uniform01=lib_ran_unif01(x_seed);
  y1 = pow(uniform01,1.0/alpha);
  uniform01=lib_ran_unif01(x_seed);
  y2 = pow(uniform01,1.0/beta);
  while(y1+y2>1.0) {
    uniform01=lib_ran_unif01(x_seed);
    y1 = pow(uniform01,1/alpha);
    uniform01=lib_ran_unif01(x_seed);
    y2 = pow(uniform01,1/beta);
  }

  x=y1/(y1+y2);

  return x;

}		/* end of lib_ran_beta_r */



double lib_ran_gammadist(int i_p, double i_theta, unsigned int *x_seed)
/*FUNC********************************************************************

DESCRIPTION:

Generates a gamma(p,theta) distributed random number (double).  x_seed is seed
for lib_ran_unif01.

The following properties are used:

If U is uniform[0,1], then -ln(U) is gamma(1,1).

If Y1 is gamma(p,t) and Y2 is gamma(q,t), then Y1 + Y2 is gamma(p+q,t).

If Y is gamma(p,1), then Y/t is gamma(p,t).


NB: See also lib_ran_gamma, that takes two double parameters!


HOW TO USE THE FUNCTION:   l_gamma = lib_ran_gammadist(p,theta,x_seed)

SIDE-EFFECTS:  The start-seed should be either negative or big and positive.

RETURN VALUE:  The gamma distributed random variable.

*************************************************************************/
{
  double l_sum, l_unif;
  int l_i;
  double r_gamma;

  l_sum = 0;
  for(l_i = 1; l_i <= i_p; l_i++) {
    do {
      l_unif = lib_ran_unif01(x_seed);
    } while (l_unif <= 0) ;
    l_sum = l_sum - log(l_unif);
  }
  r_gamma = l_sum / i_theta;

  return r_gamma;
}





double lib_ran_gamma(double alpha, double beta,unsigned int *x_seed)
/*FUNC***************************************************************
Name:		lib_ran_gamma
Syntax:		
Description:

Generates a gamma(alpha,beta) distributed random number (double).

x_seed is seed for lib_ran_unif01.

The following properties are used:

If U is uniform[0,1], then -ln(U) is gamma(1,1) or exp(1).

If Y1 is Er(p,t) and Y2 is Er(q,t), then Y1 + Y2 is Er(p+q,t).

If Y is Er(p,1), then Y/t is Er(p,t). Er(*,*) is the Erlang distribution
which is the same as a gamma distribution with integer parameters.

This routine generates a beta random number (double) with
nonintegral parameters alpha and beta using  Theorem 3.6.1 p.72
in R. Y. Rubensteins book Simulation and the monte carlo method.

Let W and V be two independent variates from Be(delta,1-delta) and
exp(1), respectively. Then X=1/beta*V*W is a variat with G(delta,beta),
0<delta<1. To generate a variate from G(alpha,beta) we generate
an Y from Er(m,beta) (Erlang distribution). Then compute X=1/beta*(Y+V*W)

************************************************************************/
{

  double l_unif,delta,w,v;
  int l_i,m;
  double r_gamma=0.0;

  m=(int) floor(alpha);
  delta = alpha - (double) m;

  for(l_i = 1; l_i <= m; l_i++) {
    l_unif = lib_ran_unif01(x_seed);
    r_gamma = r_gamma - log(l_unif);
  }

  if (delta > 0.0) {
    l_unif = lib_ran_unif01(x_seed);
    v = - log(l_unif);
    w=lib_ran_beta_r(delta,1.0-delta,x_seed);
    r_gamma=r_gamma+v*w;
  }
  r_gamma = r_gamma / beta;

  return r_gamma;


}		/* end of lib_ran_gamma */



/* normalCumProb *********************************************************

DESCRIPTION: Compute PHI(x) with PHI() being the cummulative probability
             function for a standard Gaussian distributed variable. It is
	     based on the function erfcc given in numerical recipies, page
	     220 third edition, which garanties a fractional error for
	     the complementary error function of less than 1.2 * 10^-7.
	     PHI(X) = 1 - 0.5 * "the complementary error function".

SIDE EFFECTS: none

RETURN VALUE: PHI(x)

***************************************************************************/
double normalCumProb(double x)
{
  double t,z,erfc,ans,phi;

  x /= sqrt(2.0);

  z = (x > 0) ? x : (-x);
  t = 1.0 / (1.0 + 0.5 * z);
  ans = t * exp(- z * z - 1.265512223 + t *
        ( 1.00002368 + t * (0.37409196 + t * (0.09678418 + t *
	(-0.18628806 + t * (0.27886807 + t * (-1.13520398 + t *
        (1.48851587 + t * (-0.82215223 + t * 0.17087277)))))))));

  erfc = (x >= 0.0) ? ans : 2.0 - ans;

  phi = 1 - 0.5 * erfc;

  return phi;
}


static double yInFunctionPHIMinusuAndphi;
         /* variable used by functions: PHIMinusyAndphi and PHI_Inverse   */


/* PHI_Inverse ****************************************************************

DESCRIPTION: Compute PHI^{-1}(x) with PHI() being the cummulative probability
             function for a standard Gaussian distributed variable.
             The value is found by numerically solving the equation

	     f(x) = PHI(x) - y = 0

	     by a Newton-Raphson algorithm.


SIDE EFFECTS: none

RETURN VALUE: PHI^{-1}(y)

******************************************************************************/
double PHI_Inverse(double y)
{
  double lowerLimit,upperLimit;

  if (y < 0.0 || y > 1.0)
    {
      printf("y in PHI_Inverse must in [0,1]\n");
      exit(-1);
    }

  if (y == 0.0) return - exp(1000.0);
  if (y == 1.0) return exp(1000.0);


  if (y > 0.5)
    {
      lowerLimit = 0.0;
      upperLimit = 1.0;
      while (normalCumProb(upperLimit) < y)
	{
	  lowerLimit = upperLimit;
	  upperLimit *= 10.0;
	}
    }
  else if (y < 0.5)
    {
      upperLimit = 0.0;
      lowerLimit = -1.0;
      while (normalCumProb(lowerLimit) > y)
	{
	  upperLimit = lowerLimit;
	  lowerLimit *= 10.0;
	}
    }
  else
    return 0.0;

  if (normalCumProb(upperLimit) == y) return upperLimit;
  if (normalCumProb(lowerLimit) == y) return lowerLimit;


  yInFunctionPHIMinusuAndphi = y;

  return rtsafe(PHIMinusyAndphi,upperLimit,lowerLimit,1.0e-10,1000);
}





/* PHIMinusyAndphi ************************************************************

DESCRIPTION: computes PHI(x) - y and phi(x) with y being a global variable
             and PHI() and phi() being cummulative
             and density of standard Gaussian distribution


SIDE EFFECTS: none

RETURN VALUE: none

******************************************************************************/
void PHIMinusyAndphi(double x,double *Phi,double *phi)
{

  *Phi = normalCumProb(x) - yInFunctionPHIMinusuAndphi;
  *phi = exp(- x*x/2.0) / sqrt(2.0*G_PI);

  return;
}

/* rtsafe *********************************************************************

DESCRIPTION: find roots of specified function by Newton-Raphson algorithm.
             Function is taken from numerical recipes.

SIDE EFFECTS: none

RETURN VALUE: root

******************************************************************************/
double rtsafe(void (*funcd)(double,double *,double *),double x1,double x2,double xacc,int MaxIt)
{
	int j;
	double df,dx,dxold,f,fh,fl;
	double temp,xh,xl,rts;
	void nrerror();

	(*funcd)(x1,&fl,&df);
	(*funcd)(x2,&fh,&df);
	if (fl*fh >= 0.0)
	  {
	    printf("Root must be bracketed in RTSAFE\n");
	    exit(-1);
	  }
	if (fl < 0.0) {
		xl=x1;
		xh=x2;
	} else {
		xh=x1;
		xl=x2;
	}
	rts=0.5*(x1+x2);
	dxold=fabs(x2-x1);
	dx=dxold;
	(*funcd)(rts,&f,&df);
	for (j=1;j<=MaxIt;j++) {
		if ((((rts-xh)*df-f)*((rts-xl)*df-f) >= 0.0)
			|| (fabs(2.0*f) > fabs(dxold*df))) {
			dxold=dx;
			dx=0.5*(xh-xl);
			rts=xl+dx;
			if (xl == rts) return rts;
		} else {
			dxold=dx;
			dx=f/df;
			temp=rts;
			rts -= dx;
			if (temp == rts) return rts;
		}
		if (fabs(dx) < xacc) return rts;
		(*funcd)(rts,&f,&df);
		if (f < 0.0)
			xl=rts;
		else
			xh=rts;
	}
	printf("Maximum number of iterations exceeded in RTSAFE");
	exit(-1);

	return 0.0;
}



