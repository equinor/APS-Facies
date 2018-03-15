//
// PURPOSE Implementation of class RandomGenerator
//


/*INCLUDE FILES:*/

#include <cmath>
#include <errno.h>
#include <iostream>
#include "lib_message.h"
#include "Grid1D_template.h"
#include "Grid2D_template.h"
#include "randomFuncs.h"
#include "lib_matr.h"
#include "utl.h"
#include "lib_ran.h"

#define  EPSILON 0.00000001

#define  G_MULTIPLIER  69069
#define  G_SHIFT           1
#define  G_MODULUS  256*256*256*128
#define  G_INVMOD  ( (double) 1 / ((double) G_MODULUS )) / ( (double) 2 )

const double PI =  3.14159265358979323 ;


using namespace std ;


/*F:RandomGenerator::RandomGenerator*
________________________________________________________________
		RandomGenerator::RandomGenerator
________________________________________________________________
Name:		RandomGenerator::RandomGenerator
Syntax:		@RandomGenerator::RandomGenerator-syntax
Description: Constructor initializing seed value
________________________________________________________________*/
/*<RandomGenerator::RandomGenerator-syntax: */
RandomGenerator::RandomGenerator(unsigned  int iseed)
/*>RandomGenerator::RandomGenerator-syntax: */
{
    seed = iseed;
    cout << "RandomGenerator constructor: " << seed << endl;  /* TESTING */
    allocationMN = 0;
    initMN = 0;
    seedIsRead = 1;
}	/* end of RandomGenerator::RandomGenerator */


/*F:RandomGenerator::RandomGenerator*
________________________________________________________________
		RandomGenerator::RandomGenerator
________________________________________________________________
Name:		RandomGenerator::RandomGenerator
Syntax:		@RandomGenerator::RandomGenerator-syntax
Description: Constructor initializing seed value
________________________________________________________________*/
/*<RandomGenerator::RandomGenerator-syntax: */
RandomGenerator::RandomGenerator(void)
/*>RandomGenerator::RandomGenerator-syntax: */
{
    allocationMN = 0;
    initMN = 0;
    return;
}	/* end of RandomGenerator::RandomGenerator */



/*F:RandomGenerator::RandomGenerator*
________________________________________________________________
		RandomGenerator::RandomGenerator
________________________________________________________________
Name:		RandomGenerator::RandomGenerator
Syntax:		@RandomGenerator::RandomGenerator-syntax
Description: Constructor reading seed file.
________________________________________________________________*/
/*<RandomGenerator::RandomGenerator-syntax: */
RandomGenerator::RandomGenerator(char *filename)
/*>RandomGenerator::RandomGenerator-syntax: */
{
    FILE * file;
    file = fopen(filename,"r");
    if(file == 0)
    {
	moduleError(OPENFILE,"RandomGenerator",
		    "Seed file: %s",filename);
    }
    fscanf(file,"%d",&seed);
    fclose(file);
    allocationMN = 0;
    initMN = 0;
    seedIsRead = 1;
}	/* end of RandomGenerator::RandomGenerator */


/*F:RandomGenerator::RandomGenerator*
________________________________________________________________
		RandomGenerator::RandomGenerator
________________________________________________________________
Name:		RandomGenerator::RandomGenerator
Syntax:		@RandomGenerator::RandomGenerator-syntax
Description:    Copy Constructor.
________________________________________________________________*/
/*<RandomGenerator::RandomGenerator-syntax: */
RandomGenerator::RandomGenerator(RandomGenerator &ran)
/*>RandomGenerator::RandomGenerator-syntax: */
{
    seed = ran.seed;
    cout << "RandomGenerator constructor: " << seed << endl;  /* TESTING */
    allocationMN = 0;
    initMN = 0;
    seedIsRead = ran.seedIsRead;
}	/* end of RandomGenerator::RandomGenerator */




/*F:RandomGenerator::~RandomGenerator*
________________________________________________________________
		RandomGenerator::~RandomGenerator
________________________________________________________________
Name:		RandomGenerator::~RandomGenerator
Syntax:		@RandomGenerator::~RandomGenerator-syntax
Description: Destructor
________________________________________________________________*/
/*<RandomGenerator::~RandomGenerator-syntax: */
RandomGenerator::~RandomGenerator(void)
/*>RandomGenerator::~RandomGenerator-syntax: */
{
    if(allocationMN)
    {
	Fmatrix_2d(&(covMatMN[0][0]),&(covMatMN[0]));
	covMatMN = 0;
	Fmatrix_2d(&(udMN[0][0]),&(udMN[0]));
	udMN = 0;
	free(resultMN);

	Fmatrix_2d(&(eigenVector[0][0]),&(eigenVector[0]));
	eigenVector = 0;
	Fmatrix_1d(&(eigenValue[0]));
	eigenValue = 0;
	Fmatrix_1d(&(negative[0]));
	negative = 0;

	Fmatrix_2d(&(lmn[0][0]),&(lmn[0]));
	lmn = 0;
	Fmatrix_2d(&(lnorm[0][0]),&(lnorm[0]));
	lnorm = 0;
	Fmatrix_2d(&(le[0][0]),&(le[0]));
	le = 0;

	allocationMN = 0;
    }

}	/* end of RandomGenerator::~RandomGenerator */





/*F:RandomGenerator::unif01*
________________________________________________________________
		RandomGenerator::unif01
________________________________________________________________
Name:		RandomGenerator::unif01
Syntax:		@RandomGenerator::unif01-syntax
Description:
              Generates a uniform[0,1] variable using the congruential
              generator given in ripley: stochastic simulation, p. 46.
              The start-seed should be either negative, or big and positive.
              The seed is changed in this function.
              NOTE: Requires that a  int is 32 bits because the
              algorithm requires that modulus 2^32 is taken.
	      This is done implicit using 32bits integer.

Side effects:
              The start-seed should be either negative, or big and positive.
              The seed is changed in this function.

Return value: The pseudo-random number in [0,1], both inclusive.
Example: l_unif = lib_ran_unif01()

________________________________________________________________*/
/*<RandomGenerator::unif01-syntax: */
double RandomGenerator::unif01(void)
/*>RandomGenerator::unif01-syntax: */
{
 double l_ran;
 seed = G_MULTIPLIER * seed + G_SHIFT; /* Modulus 2^32 implicit */
 l_ran = (double) seed * G_INVMOD;
 return(l_ran);
}	/* end of RandomGenerator::unif01 */





/*F:RandomGenerator::unif*
________________________________________________________________
		RandomGenerator::unif
________________________________________________________________
Name:		RandomGenerator::unif
Syntax:		@RandomGenerator::unif-syntax
Description:
              Generates a uniform[min,max] variable using
	      transformation of a uniform[0,1] variable

Side effects:

Return value: The pseudo-random number in [min,max], both inclusive.
Example: l_unif = lib_ran_unif01()

________________________________________________________________*/
/*<RandomGenerator::unif-syntax: */
double RandomGenerator::unif(double min,double max)
/*>RandomGenerator::unif-syntax: */
{
  return min + (max - min) * unif01();

}	/* end of RandomGenerator::unif */





/*F:RandomGenerator::iUnif*
________________________________________________________________
		RandomGenerator::iUnif
________________________________________________________________
Name:		RandomGenerator::iUnif
Syntax:		@RandomGenerator::iUnif-syntax
Description:
              Generates a variable from uniform distribution for integers
	      in [min,max]  by transformation of a uniform[0,1] variable

Side effects:

Return value: The pseudo-random number in [min,max], both inclusive.
Example: l_unif = lib_ran_unif01()

________________________________________________________________*/
/*<RandomGenerator::iUnif-syntax: */
int RandomGenerator::iUnif(int min,int max)
/*>RandomGenerator::iUnif-syntax: */
{
  assert(max >= min);

  double ran = unif01();
  int range = max - min + 1;
  int value = (int) (ran * range) + min;
  if (value == max + 1) value -= 1;

  return value;

}	/* end of RandomGenerator::iUnif */





/*F:RandomGenerator::intProb*
________________________________________________________________
		RandomGenerator::intProb
________________________________________________________________
Name:		RandomGenerator::intProb
Syntax:		@RandomGenerator::intProb-syntax
Description:
              Generates a variable from discrete distribution on the
	      integers on [0,n] with cummulative distribution given in prob

Side effects:

Return value: The pseudo-random number in [0,n], both inclusive.
Example:

________________________________________________________________*/
/*<RandomGenerator::intProb-syntax: */
int RandomGenerator::intProb(int n,const Grid1D<double>& prob)
/*>RandomGenerator::intProb-syntax: */
{
  double p = unif01() * prob(n - 1);
  int min = 0;
  int max = n - 1;
  while (max - min > 4)
  {
      int middle;
      middle = min + (int) (((double) (max - min)) / 2.0);
      if (prob(middle) < p)
	min = middle;
      else
	max = middle;
  }
  int i;
  for (i = min; prob(i) < p; i++);

  return i;

}	/* end of RandomGenerator::intProb */





/*F:RandomGenerator::normal01*
________________________________________________________________
		RandomGenerator::normal01
________________________________________________________________
Name:		RandomGenerator::normal01
Syntax:		@RandomGenerator::normal01-syntax
Description:
              Generate two independent normal(0,1)-distributed numbers,
              using the Box-Muller method.  Reference: Ripley p.54.
	      The start-seed should be either negative, or big and positive.

Example: lib_ran_norm01(double &o_x1, double &o_x2)

________________________________________________________________*/
/*<RandomGenerator::normal01-syntax: */
void RandomGenerator::normal01(double &o_x1, double &o_x2)
/*>RandomGenerator::normal01-syntax: */
{
  double l_u1, l_u2;

/* First generate two uniform(0,1)-numbers: */
  l_u1 = unif01();
  l_u2 = unif01();

/* Then compute two normal(0,1)-numbers: */
  o_x1 = sqrt(-2.0*log(l_u1)) * cos(2.0*PI*l_u2);
  o_x2 = sqrt(-2.0*log(l_u1)) * sin(2.0*PI*l_u2);
  return;
}





/*F:RandomGenerator::initMultiNormalWorkSpace*
________________________________________________________________
		RandomGenerator::initMultiNormalWorkSpace
________________________________________________________________
Name:		RandomGenerator::initMultiNormalWorkSpace
Syntax:		@RandomGenerator::initMultiNormalWorkSpace-syntax
Description:
              Initialize working space for simulation of
	      multinormally distributed variables with specified dimension.

Side effects: Initialize internal data working space.

Return value: 0 if allocation OK, 1 if error
Example:

________________________________________________________________*/
/*<RandomGenerator::initMultiNormalWorkSpace-syntax: */
int RandomGenerator::
initMultiNormalWorkSpace(int dimension)
/*>RandomGenerator::initMultiNormalWorkSpace-syntax: */
{
    assert(dimension > 0);
    dim = dimension;
    if(allocationMN)
    {
	// Delete space that has been used previously
	Fmatrix_2d(&(covMatMN[0][0]),&(covMatMN[0]));
	covMatMN = 0;
	Fmatrix_2d(&(udMN[0][0]),&(udMN[0]));
	udMN = 0;
	Fmatrix_2d(&(eigenVector[0][0]),&(eigenVector[0]));
	eigenVector = 0;
	Fmatrix_1d(&(eigenValue[0]));
	eigenValue = 0;
	Fmatrix_1d(&(negative[0]));
	negative = 0;
	Fmatrix_2d(&(lmn[0][0]),&(lmn[0]));
	lmn = 0;
	Fmatrix_2d(&(lnorm[0][0]),&(lnorm[0]));
	lnorm = 0;
	Fmatrix_2d(&(le[0][0]),&(le[0]));
	le = 0;
	free(resultMN);
    }

    // Allocate space for this dimension
    covMatMN = (double**) Mmatrix_2d(0,dim-1,0,dim-1,sizeof(double),1);
    udMN     = (double**) Mmatrix_2d(0,dim-1,0,dim-1,sizeof(double),1);
    resultMN = (double*) calloc(dim,sizeof(double));

    eigenVector = (double **) Mmatrix_2d(0,dim-1,0,dim-1,sizeof(double),1);
    eigenValue  = (double *)  Mmatrix_1d(0,dim-1,sizeof(double),1);
    negative    = (int *)     Mmatrix_1d(0,dim-1, sizeof(int),1);

    le = (double **)    Mmatrix_2d(0,dim,0,0,sizeof(double),1);
    lnorm = (double **) Mmatrix_2d(0,dim,0,0,sizeof(double),1);
    lmn = (double **)   Mmatrix_2d(0,dim,0,0,sizeof(double),1);


    if(covMatMN == 0 || udMN == 0 ||  resultMN == 0 ||
       eigenVector == 0 || eigenValue == 0 || negative == 0 ||
       le == 0 || lnorm == 0 || lmn == 0)
    {
	return 1;
    }
    allocationMN = 1;

    return 0;
}	/* end of RandomGenerator::initMultiNormalWorkSpace */






/*F:RandomGenerator::initMultiNormalCovariance*
________________________________________________________________
		RandomGenerator::initMultiNormalCovariance
________________________________________________________________
Name:		RandomGenerator::initMultiNormalCovariance
Syntax:		@RandomGenerator::initMultiNormalCovariance-syntax
Description:
              Initialize the covariance matrix used when drawing
	      from multinormal distribution.

Side effects: Requires that the function initMultiNormalWorkSpace
              has been called with the correct dimension.

Return value: 1 if the covariance matrix specified is not valid.
              0 if OK
Example:

________________________________________________________________*/
/*<RandomGenerator::initMultiNormalCovariance-syntax: */
int RandomGenerator::
initMultiNormalCovariance(const Grid2D<double> & covMatrix)
/*>RandomGenerator::initMultiNormalCovariance-syntax: */
{
    assert(dim == covMatrix.xdim());
    assert(allocationMN);
    int i,j;
    int ii,jj;
    for( j = 0; j < dim; j++)
    {
	jj = j + covMatrix.xstart();
	for( i = 0; i < dim; i++)
	{
	    ii = i + covMatrix.xstart();
	    covMatMN[i][j] = covMatrix(ii,jj);
	}
    }

    int err = 0;
/* local variables  */
    int l_i, l_j, l_neg_eig;
    int l_error = 0;
    double l_a;

    lib_matr_eigen(covMatMN, dim, eigenVector, eigenValue, &l_error);
    if (l_error > 0)
    {
	moduleError(KERNEL,"RandomGenerator::initMultiNormalCovariance",
		    "%s\n%s",
		    "Unsuccesful decomposition,",
		    "not all eigenvalues determined.");
	err = 1;
    }

    l_neg_eig = 0;
    for (l_i=0; l_i <= dim-1; l_i++)
    {
	l_a = eigenValue[l_i];
	if (l_a >= 0.0)
	{
	    l_a = sqrt(l_a);
	    for (l_j=0; l_j <= dim-1; l_j++)
		udMN[l_j][l_i] = eigenVector[l_j][l_i] * l_a;
	}
	else
	{
	    negative[l_neg_eig] = l_i;
	    l_neg_eig++;
	}
    }

    if (l_neg_eig > 0)
    {
	moduleWarning(CORRECT,"RandomGenerator::initMultiNormalCovariance",
		      "%s\n%d %s",
		      "Unsuccesful decomposition,",
		      l_neg_eig,
		      "negative eigenvalues.");
	for (l_i=0; l_i < l_neg_eig; l_i++)
	    printf("Eigenvalue no. %d : %f\n",negative[l_i],
		    eigenValue[negative[l_i]]);
	err = 1;
    }

/*
    int err = lib_ran_mninit(dim,covMatMN,udMN);
*/

    if(err == 0)
    {
	initMN = 1;	
    }
    return err;
}	/* end of RandomGenerator::initMultiNormalCovariance */




/*F:RandomGenerator::multiNormal*
________________________________________________________________
		RandomGenerator::multiNormal
________________________________________________________________
Name:		RandomGenerator::multiNormal
Syntax:		@RandomGenerator::multiNormal-syntax
Description:
              Draw a multinormal vector with the given expectation.
	      Requires that initMultiNormalCovariance defining the
	      covariance matrix has been called
	      and that initMultiNormalWorkSpace defining the dimension
	      has been called.

Side effects:

Return value: void
Example:

________________________________________________________________*/
/*<RandomGenerator::multiNormal-syntax: */
void RandomGenerator::
multiNormal(const Grid1D<double> & expectation, Grid1D<double> & value)
/*>RandomGenerator::multiNormal-syntax: */
{
    assert(initMN);
    assert(expectation.xdim() == dim);
    assert(value.xdim() == dim);
    expMN = (double *) expectation.getArray();
    assert(expMN);

/* local variables  */
    int i;
    double  x1, x2;

    /* Creates dim N(0,1) pseudo-random numbers in lnorm */

    for (i=0; i<=dim-1; i=i+2)
    {
	normal01(x1,x2);
	lnorm[i][0] = x1;
	lnorm[i+1][0] = x2;
    }
    for (i=0; i<=dim-1; i++)
	le[i][0] = expMN[i];

    /* Multiply random-vector lnorm by the SVD decomposition udMN.
       Add the expectation.  */

    lib_matr_prod(udMN, lnorm, dim, dim, 1, lmn);
    lib_matr_add(le, dim, 1, lmn);

    for (i=0; i <= dim-1; i++)
	resultMN[i] = lmn[i][0];




/*
    lib_ran_mn(dim,udMN,expMN,&iseed,resultMN);
    seed = (unsigned  int)iseed;
*/
    value.assign(resultMN);
    return;
}	/* end of RandomGenerator::multiNormal */



/*F:RandomGenerator::potentialFromNormal*
________________________________________________________________
		RandomGenerator::potentialFromNormal
________________________________________________________________
Name:		RandomGenerator::potentialFromNormal
Syntax:		@RandomGenerator::potentialFromNormal-syntax
Description:
              Calculate minus log of the probability density
	      of a normal distribution at the point x.

                -log(N(expectation,sdev)(x))

Return value: The potential
________________________________________________________________*/
/*<RandomGenerator::potentialFromNormal-syntax: */
double RandomGenerator::
potentialFromNormal(double expectation, double stdev, double x) const
/*>RandomGenerator::potentialFromNormal-syntax: */
{
    assert(stdev > 0.0);
    double var = stdev*stdev;
    double y   = x - expectation;
    double potential = 0.5*(log(2.0*PI*var) + ((y*y)/var));
    return potential;
}	/* end of RandomGenerator::potentialFromNormal */



/*F:RandomGenerator::potentialFromMultiNormal*
________________________________________________________________
		RandomGenerator::potentialFromMultiNormal
________________________________________________________________
Name:		RandomGenerator::potentialFromMultiNormal
Syntax:		@RandomGenerator::potentialFromMultiNormal-syntax
Description:
              Calculate minus log of the probability density
	      of a multi normal distribution at the specified point.

                -log(MN(expectation,cov)(point))

		This function requires that initMultiNormalCovariance
		has been called previously with the covariance matrix
		of correct dimension.
		The dimension must have been initialized by calling
		initMultiNormalWorkSpace before that again.

Return value: The potential
Example:

________________________________________________________________*/
/*<RandomGenerator::potentialFromMultiNormal-syntax: */
double RandomGenerator::
potentialFromMultiNormal(const Grid1D<double>& expectation,
			 const Grid1D<double>& point) const
/*>RandomGenerator::potentialFromMultiNormal-syntax: */
{
    assert(initMN);
    assert(expectation.xdim() == dim);
    assert(point.xdim() == dim);

    // Determinant of covariance matrix
    double determinant;
    determinant = 1.0;
    int i;
    for(i= 0; i < dim ;i++)
    {
	determinant *= eigenValue[i];
    }
    assert(determinant > 0);
    double y1,y2,q1,q2;
    int j,l;
    double sum = 0.0;
    double d;
    for(i = 0; i < dim; i++)
    {
	y2 = point(i) - expectation(i);
	for(j = 0; j < dim; j++)
	{
	    q2 = eigenVector[i][j];
	    d  = 1.0/eigenValue[j];
	    for(l = 0; l < dim; l++)
	    {
		y1 = point(l) - expectation(l);
		q1 = eigenVector[l][j];
		sum +=  q1*q2*y1*y2*d;
	    }
	}
    }

    sum *= 0.5;

    double potential = sum + 0.5*(log(determinant) + dim * log(2.0*PI));

    return potential;
}	/* end of RandomGenerator::potentialFromMultiNormal */








/*F:RandomGenerator::getSeed*
________________________________________________________________
		RandomGenerator::getSeed
________________________________________________________________
Name:		RandomGenerator::getSeed
Syntax:		@RandomGenerator::getSeed-syntax
Description: Function for returning current seed value.

________________________________________________________________*/
/*<RandomGenerator::getSeed-syntax: */
unsigned  int RandomGenerator::getSeed(void) const
/*>RandomGenerator::getSeed-syntax: */
{
    return seed;
}	/* end of RandomGenerator::getSeed */



/*F:RandomGenerator::setSeed*
________________________________________________________________
		RandomGenerator::setSeed
________________________________________________________________
Name:		RandomGenerator::setSeed
Syntax:		@RandomGenerator::setSeed-syntax
Description:    Function for setting current seed value.

________________________________________________________________*/
/*<RandomGenerator::setSeed-syntax: */
void RandomGenerator::setSeed(unsigned  int newSeed)
/*>RandomGenerator::setSeed-syntax: */
{
    seed = newSeed;
}	/* end of RandomGenerator::setSeed */








/*F:RandomGenerator::writeSeedFile*
________________________________________________________________
		RandomGenerator::writeSeedFile
________________________________________________________________
Name:		RandomGenerator::writeSeedFile
Syntax:		@RandomGenerator::writeSeedFile-syntax
Description: Write seed to file

________________________________________________________________*/
/*<RandomGenerator::writeSeedFile-syntax: */
void RandomGenerator::writeSeedFile(char *filename) const
/*>RandomGenerator::writeSeedFile-syntax: */
{
    FILE *file;
    file = fopen(filename,"w");
    if(file == 0)
    {
	moduleError(OPENFILE,"RandomGenerator::writeSeedFile",
		    "File: %s",filename);
    }
    fprintf(file,"%d",seed);
    if(fclose(file))
	{
	    moduleError(WRITEFILE,"RandomGenerator::writeSeedFile",
			"Error closing file: %s",
			strerror(errno));
	}
    return;
}	/* end of RandomGenerator::writeSeedFile */



//
// FUNCTION: triangular
//
// PURPOSE Generates a triangular(min, mode, max) distributed number.
//         If not min <= mode <= max the three numbers will
//         be repermuted to match this requirement.
//
// RETURN VALUE A double value  which is distributed according to the
//              specified triangular distribution
//
double RandomGenerator::
triangular(double min, double mode, double max)
{
  double temp, uni, triang;

/* First make min < max */
  if (min > max) {
    temp = max;
    max = min;
    min = temp;
  }

/* Then make mode < max */
  if (mode > max) {
    temp = mode;
    mode =max;
    max = temp;
  }

/* And finally make min < mode  */
  if (mode < min) {
    temp = mode;
    mode = min;
    min = temp;
  }

/* Generate a random(0,1) - number */

  uni = unif01();

/* Generate the triangular distributed number */

  if (min == max) triang = min;
  else if (uni < ((mode - min) / (max - min)))
    triang = min + sqrt(uni * (mode - min) * (max - min));
  else
    triang = max - sqrt((1 - uni) * (max - mode) * (max - min));

  return(triang);

}



/*F:RandomGenerator::normalTruncated*
________________________________________________________________
		RandomGenerator::normalTruncated
________________________________________________________________
Name:		RandomGenerator::normalTruncated
Syntax:		@RandomGenerator::normalTruncated-syntax
Description:    Draws from a normal truncated gaussian field
Side effects:   None
Return value:   The value drawn, a double
Global or static variables used:
________________________________________________________________*/
/*<RandomGenerator::normalTruncated-syntax: */
double
RandomGenerator::normalTruncated(double mean, double std,
				 double min, double max)
/*>RandomGenerator::normalTruncated-syntax: */
{
  if(min > max)
  {
    moduleError(KERNEL,"RandomGenerator::normalTruncated","%s%f%s%f%s\n",
		"Wrong input, should have min <= max), (min, max) = (",
		min,", ",max,")");
  }

  if(std == 0.0)
  {
    if(min <= mean && mean <= max)
    {
      return mean;
    }
    else
    {
      moduleError(KERNEL,"RandomGenerator::normalTruncated","%s\n",
		  "Can not draw from a truncated distribution with zero ",
		  "variance, when the mean is outside the truncation values");
    }
  }
  double abscissa;
  double ru01 = unif01();
  double phiMin = normalCumProb((min-mean)/std);
  double phiMax = normalCumProb((max-mean)/std);
  double ordinate = phiMin + ru01 * (phiMax - phiMin);

  if (ordinate < EPSILON)
  {
    abscissa = max;
  }
  else if (ordinate > 1.0 - EPSILON)
  {
    abscissa = min;
  }
  else
  {
    abscissa = PHI_Inverse(ordinate);
    abscissa *= std;
    abscissa += mean;
  }

  return abscissa;
}	/* end of RandomGenerator::normalTruncated */



/*F:RandomGenerator::normalTruncatedUpper*
________________________________________________________________
		RandomGenerator::normalTruncatedUpper
________________________________________________________________
Name:		RandomGenerator::normalTruncatedUpper
Syntax:		@RandomGenerator::normalTruncatedUpper-syntax
Description:    Draws from a normal upper truncated gaussian field
Side effects:   None
Return value:   The value drawn, a double
Global or static variables used:
________________________________________________________________*/
/*<RandomGenerator::normalTruncated-Uppersyntax: */
double
RandomGenerator::normalTruncatedUpper(double mean, double std, double max)
/*>RandomGenerator::normalTruncatedUpper-syntax: */
{
  if(std == 0.0)
  {
    if(mean <= max)
    {
      return mean;
    }
    else
    {
      moduleError(KERNEL,"RandomGenerator::normalTruncatedUpper","%s%s\n",
		  "Can not draw from a upper truncated distribution with zero",
		  " variance when the mean is above the truncation value");
    }
  }
  double abscissa;
  double ru01 = unif01();
  double phiMin = 0.0;
  double phiMax = normalCumProb((max-mean)/std);
  double ordinate = phiMin + ru01 * (phiMax - phiMin);

  if (ordinate < EPSILON)
  {
    abscissa = max;
  }
  else
  {
    abscissa = PHI_Inverse(ordinate);
    abscissa *= std;
    abscissa += mean;
  }

  return abscissa;
}	/* end of RandomGenerator::normalTruncatedUpper */



/*F:RandomGenerator::normalTruncatedLower*
________________________________________________________________
		RandomGenerator::normalTruncatedLower
________________________________________________________________
Name:		RandomGenerator::normalTruncatedLower
Syntax:		@RandomGenerator::normalTruncatedLower-syntax
Description:    Draws from a normal lower truncated gaussian field
Side effects:   None
Return value:   The value drawn, a double
Global or static variables used:
________________________________________________________________*/
/*<RandomGenerator::normalTruncatedLower-syntax: */
double
RandomGenerator::normalTruncatedLower(double mean, double std, double min)
/*>RandomGenerator::normalTruncatedLower-syntax: */
{
  if(std == 0.0)
  {
    if(mean >= min)
    {
      return mean;
    }
    else
    {
      moduleError(KERNEL,"RandomGenerator::normalTruncatedLower","%s%s\n",
		  "Can not draw from a lower truncated distribution with zero",
		  " variance when the mean is below the truncation value");
    }
  }
  double abscissa;
  double ru01 = unif01();
  double phiMin = normalCumProb((min-mean)/std);
  double phiMax = 1.0;
  double ordinate = phiMin + ru01 * (phiMax - phiMin);

if (ordinate > 1.0 - EPSILON)
  {
    abscissa = min;
  }
  else
  {
    abscissa = PHI_Inverse(ordinate);
    abscissa *= std;
    abscissa += mean;
  }

  return abscissa;
}	/* end of RandomGenerator::normalTruncatedLower */


int
RandomGenerator::poisson(double lamda) {
  int i = 0;
  double pc = exp(-lamda);
  double p0 = unif01();

  while(pc < p0 && pc < 0.9999)
  {
    i++;
    pc += exp(- lamda + (i * log(lamda)) - lgamma(i+1));
  }
  return(i);


}

void RandomGenerator::
initialize(void)
{
   seedIsRead = 0;
}

int RandomGenerator::
checkIfSeedIsDefined(void) const
{
   return seedIsRead;
}


/* Defining static members */
   unsigned  int RandomGenerator::seed; /* Definition of static member */
int RandomGenerator::seedIsRead;

