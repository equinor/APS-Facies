/*Func: SimGauss2D

Name:      SimGauss2D - Header file
Syntax:     @SimGauss2D-syntaks
Description:  Header file for class simGauss2D
End:

----------------------------------------------------------------*/

#if !defined(SIMGAUSS2D_H)
#define SIMGAUSS2D_H  1
#include "randomFuncs.h"
#include "vario2D.h"

/*<SimGauss2D-syntaks:*/

class SimGaussField2D: public RandomGenerator
{

   public:

      SimGaussField2D(RandomGenerator &ran);
      SimGaussField2D(SimGaussField2D &simGF);

      ~SimGaussField2D();

  void setCorrelation(Vario2D *corr);
  float *drawGridStandard(int nx, int ny, double xsize, double ysize);
  float *drawGridSimple  (int nx, int ny, double xsize, double ysize);
  float *drawGridDetailed(int nx, int ny, double xsize, double ysize);


 private:

  Vario2D *correl;

  void draw2d_ss_1s(int *nxmax, int *nx, int *ny,
		    float *ogrid, double *wgrid);

  void draw2d_ss_2s(int *nxmax, int *nx, int *ny,
		    float *ogrid, double *wgrid);

  void draw2d_ss_3s(int *nxmax, int *nx, int *ny,
		    float *ogrid, double *wgrid);

  void draw2d_ss_1o(int *nxmax, int *nx, int *ny,
		    float *ogrid, double *wgrid);

  void draw2d_ss_2o(int *nxmax, int *nx, int *ny,
		    float *ogrid, double *wgrid);

  void draw2d_ss_3o(int *nxmax, int *nx, int *ny,
		    float *ogrid, double *wgrid);

  int init_weights_s(int *i_pattn,int *i_n);

  int init_weights_o(int *i_pattn,int *i_n);

  int make_patt(int *i_pattn,int *i_lag,
		int *i_num, int *i_dx,int *i_dy);

  int draw_node(int *i_pattn,int *i_n,
		int *i_dim, int *i_x,
		int *i_y, double *x_grid);

  int inits_grid(int *i_dim,double *o_grid);

  int inito_grid(int *i_dim, double *o_grid);

  int init_c_patt();

  double normal(double *variance);

  int checkSimulatedVariance(float *grid, int nx, int ny);
};



/*>SimGauss2D-syntaks:*/



#endif











