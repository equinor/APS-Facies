//
// PURPOSE Declaration of class RandomGenerator
//
//
//
//

#ifndef _RAND_FUNCS_H
#define _RAND_FUNCS_H 1
#include "lib_message.h"
#include "Grid1D_template.h"
#include "Grid2D_template.h"
#include "lib_ran.h"

class RandomGenerator
{
public:
    RandomGenerator(char *filename);
    RandomGenerator(unsigned  int iseed);
    RandomGenerator(RandomGenerator &ran);
    RandomGenerator(void);
    virtual ~RandomGenerator();
    int checkIfSeedIsDefined(void) const;
    void initialize(void);
    void normal01(double &, double &);
    double unif01(void);
    double unif(double min,double max);
    double normal(double expectation, double stdev);
    int intProb(int n,const Grid1D<double>& prob);
    int iUnif(int min,int max);
    double triangular(double min, double mode, double max);

    int  initMultiNormalWorkSpace(int dimension);
    int  initMultiNormalCovariance(const Grid2D<double> & covMatrix);
    void multiNormal(const Grid1D<double> & expectation,
		     Grid1D<double> & value);

    double potentialFromNormal(double expectation, double stdev, double x) const;
    double potentialFromMultiNormal(const Grid1D<double>& expectation,
				    const Grid1D<double>& point) const;

    unsigned  int getSeed(void) const;
    void setSeed(unsigned  int newSeed);
    void writeSeedFile(char* filename) const;
    double normalTruncated(double mean, double var, double min, double max);
    double normalTruncatedLower(double mean, double var, double min);
    double normalTruncatedUpper(double mean, double var, double max);
    int poisson(double lamda);

protected:
    static unsigned  int seed;
    static int seedIsRead;

private:

    // Variables used internally for multinormal distribution
    int allocationMN;
    int initMN;
    int dim;
    double** covMatMN;
    double** udMN;
    double* expMN;
    double* resultMN;
    double** eigenVector;
    double*  eigenValue;
    int*     negative;
    double** lnorm;
    double** le;
    double** lmn;

};

inline double RandomGenerator::
normal(double expectation,double stdev)
{
    double x1,x2;
    normal01(x1,x2);
    return (expectation + x1*stdev);
}

#endif





