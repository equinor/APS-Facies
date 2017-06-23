
/* External functions */

#ifdef __cplusplus
extern "C"
{
#endif

#include "utl.h"
extern double lib_ran_unif01(unsigned int *);
extern int lib_ran_iunif(int, int, unsigned int *);
extern void lib_ran_norm01(unsigned int *, double *, double *);
extern int lib_ran_mninit(int, double **, double **);
extern void lib_ran_mn(int, double **, double *, unsigned int *, double *);
extern double lib_ran_dunif(double, double, unsigned int *);
extern double lib_ran_triang(double, double, double, unsigned int *);
extern int lib_ran_binomial(int, double, unsigned int *);
extern double lib_ran_beta(int, int, unsigned int * );
extern double lib_ran_beta_r(double alpha, double beta, unsigned int *x_seed);
extern double lib_ran_gammadist(int , double , unsigned int *);
extern double lib_ran_gamma(double alpha, double beta, unsigned int *x_seed);
extern int lib_ran_multnomial(double *, int, unsigned int *);
extern double normalCumProb(double x);
extern double PHI_Inverse(double y);
extern void PHIMinusyAndphi(double x,double *Phi,double *phi);
extern double rtsafe(void (*funcd)(double,double *,double *),double x1,double x2,double xacc,int MaxIt);


#ifdef __cplusplus
}
#endif

