
/*Include Files:*/
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <ctype.h>
#include <cmath>
#include <cassert>
#include <errno.h>
#include <float.h>

/* Include files for data structure */
#include "global_def.h"
#include "simGauss2D.h"
#include "linearsolver.h"
#include "lib_message.h"


#define EPS_COND (1.0*DBL_EPSILON)


//
// FUNCTION: SimGaussField2D::SimGaussField2D
//
// PURPOSE: Constructor, version1
//
// RETURN VALUE:
//
// SIDE EFFECTS:
//
// SPECIAL INSTRUCTIONS & NOTES:
//
SimGaussField2D::SimGaussField2D(RandomGenerator &ran):
    RandomGenerator(ran)
{

}




//
// FUNCTION: SimGaussField2D::~SimGaussField2D
//
// PURPOSE: Destructor
//
// RETURN VALUE:
//
// SIDE EFFECTS:
//
// SPECIAL INSTRUCTIONS & NOTES:
//
SimGaussField2D::~SimGaussField2D(void)
{

}



//
// FUNCTION: setCorrelation
//
// PURPOSE:
//
// RETURN VALUE:
//
// SIDE EFFECTS:
//
// SPECIAL INSTRUCTIONS & NOTES:
//
void SimGaussField2D::setCorrelation(Vario2D *corr)
{
    assert(corr);
    correl = corr;
    return;
} /* end of setCorrelation */




//
// FUNCTION: drawGridStandard
//
// PURPOSE: Simulates a gaussian 2D field using "intermediate"
//          size of the number of neighbour points in the
//          simulation algorithm. The simulation algorithm
//          is a translated version of the original fortran
//          function "draw2d_ss_2s".
//          Input: Number of grid nodes and the size of the
//                 rectangular area covered by the grid.
//
// RETURN VALUE: A simulated grid.
//
// SIDE EFFECTS: Write error messages using moduleError and so on.
//
// SPECIAL INSTRUCTIONS & NOTES: Note that numerical unstability
//                               may occur in case the correlation
//                               between neighbour points becomes too
//                               large. In this case error message
//                               might occur. This happens in particular
//                               when using gaussian variograms with long
//                               correlation length.
//

float  *SimGaussField2D::drawGridStandard(int nx, int ny,
					  double xsize, double ysize)
{
  float *resultGrid;
  double *wgrid;
  int m,d;
  assert(correl);
  assert(nx*ny > 4);
  resultGrid = 0;
  resultGrid = (float *) calloc(nx*ny,sizeof(float));

  m = (int) (log((double) (MAXIM(nx,ny)-1))/log(2.0) + 0.99999) ;
  d = (int) ( pow(2.0,(double) m) +1);
  m = d*d;

  moduleMessage(DETAILS,"simGauss2D",
		"Simulating gaussian field with grid size (%d,%d)",nx,ny);
  moduleMessage(DETAILS,"simGauss2D",
		"Area of simulated field is (%f,%f)",xsize,ysize);
  wgrid = 0;
  wgrid = (double *) calloc(m,sizeof(double));

  if(resultGrid == NULL || wgrid == NULL){
    moduleError(ALLOC,"drawGridStandard in class SimGaussField2D",
		"Can not allocate space for grids");
  }


  /* Transform parameters for correlation function to distance in
     grid nodes */

  correl->correlationTransf(nx,ny,xsize,ysize);
/*  printf("nx,ny,xsize,ysize: %d %d %f %f",nx,ny,xsize,ysize); */
  draw2d_ss_2s(&nx,&nx,&ny,resultGrid,wgrid);

  correl->correlationInvTransf(nx,ny,xsize,ysize);


  if(wgrid != NULL) {
    free(wgrid);
    wgrid = NULL;
  }

  return resultGrid;

} /* end of drawGridStandard */



//
// FUNCTION: drawGridSimple
//
// PURPOSE: Simulates a gaussian 2D field using "small"
//          size of the number of neighbour points in the
//          simulation algorithm. The simulation algorithm
//          is a translated version of the original fortran
//          function "draw2d_ss_1s".
//          Input: Number of grid nodes and the size of the
//                 rectangular area covered by the grid.
//
// RETURN VALUE: A simulated grid.
//
// SIDE EFFECTS: Write error messages using moduleError and so on.
//
// SPECIAL INSTRUCTIONS & NOTES: Note that numerical unstability
//                               may occur in case the correlation
//                               between neighbour points becomes too
//                               large. In this case error message
//                               might occur. This happens in particular
//                               when using gaussian variograms with long
//                               correlation length.
//

float  *SimGaussField2D::drawGridSimple(int nx, int ny,
					  double xsize, double ysize)
{
  float *resultGrid;
  double *wgrid;
  int m,d;

  assert(correl);

  resultGrid = (float *) calloc(nx*ny,sizeof(float));

  m = (int) (log((double) (MAXIM(nx,ny)-1))/log(2.0) + 0.99999) ;
  d = (int) ( pow(2.0,(double) m) +1);
  m = d*d;

  moduleMessage(DETAILS,"simGauss2D",
		"Simulating gaussian field with grid size (%d,%d)",nx,ny);

  wgrid = (double *) calloc(m,sizeof(double));

  if(resultGrid == NULL || wgrid == NULL){
    moduleError(ALLOC,"drawGridStandard in class SimGaussField2D",
		"Can not allocate space for grids");
  }


  /* Transform parameters for correlation function to distance in
     grid nodes */

  correl->correlationTransf(nx,ny,xsize,ysize);

  draw2d_ss_1s(&nx,&nx,&ny,resultGrid,wgrid);

  correl->correlationInvTransf(nx,ny,xsize,ysize);


  if(wgrid != NULL) {
    free(wgrid);
    wgrid = NULL;
  }

  return resultGrid;

} /* end of drawGridSimple */



//
// FUNCTION: drawGridDetailed
//
// PURPOSE: Simulates a gaussian 2D field using "large"
//          size of the number of neighbour points in the
//          simulation algorithm. The simulation algorithm
//          is a translated version of the original fortran
//          function "draw2d_ss_3s".
//          Input: Number of grid nodes and the size of the
//                 rectangular area covered by the grid.
//
// RETURN VALUE: A simulated grid.
//
// SIDE EFFECTS: Write error messages using moduleError and so on.
//
// SPECIAL INSTRUCTIONS & NOTES: Note that numerical unstability
//                               may occur in case the correlation
//                               between neighbour points becomes too
//                               large. In this case error message
//                               might occur. This happens in particular
//                               when using gaussian variograms with long
//                               correlation length.
//

float  *SimGaussField2D::drawGridDetailed(int nx, int ny,
					  double xsize, double ysize)
{
  float *resultGrid;
  double *wgrid;
  int m,d;

  assert(correl);

  resultGrid = (float *) calloc(nx*ny,sizeof(float));

  m = (int) (log((double) (MAXIM(nx,ny)-1))/log(2.0) + 0.99999) ;
  d = (int) ( pow(2.0,(double) m) +1);
  m = d*d;

  moduleMessage(DETAILS,"simGauss2D",
		"Simulating gaussian field with grid size (%d,%d)",nx,ny);

  wgrid = (double *) calloc(m,sizeof(double));

  if(resultGrid == NULL || wgrid == NULL){
    moduleError(ALLOC,"drawGridStandard in class SimGaussField2D",
		"Can not allocate space for grids");
  }


  /* Transform parameters for correlation function to distance in
     grid nodes */

  correl->correlationTransf(nx,ny,xsize,ysize);

  draw2d_ss_3s(&nx,&nx,&ny,resultGrid,wgrid);

  correl->correlationInvTransf(nx,ny,xsize,ysize);


  if(wgrid != NULL) {
    free(wgrid);
    wgrid = NULL;
  }

  return resultGrid;

} /* end of drawGridDetailed */




/*

   sim2DdrawGrid.f -- translated by f2c (version of 23 April 1993  18:34:30).
   Modified by : O.Lia Nov 94

   Modifications done:

      -Defined header files
      -Removed seed and correlation function as parameter to the
       simulation functions and introduced two global variables
       that are pointers to structures for random generator and seed
       and correlation function with parameters.
      -Changed intrinsic fortran function call to c function calls
      -Defined ANSII c declarations for parameters and introduced
       prototype declarations of functions.
      -replaced  the min and max functions by the min and max functions
       used in global_def.h

   Documentation: Use the Fortran version in files:

                    sim2DdrawGridFortran.f
                    sim2DdrawGridFortran_param.h
		    sim2DdrawGridFortran_cbl.h

                  as documentation of the converted c code, but take into
		  account the changes mentioned above.
*/



/* Common Block Declarations */

struct simGauss2D_common_block {
    int c_patt__[1800]	/* was [30][30][2] */;
    double c_resvar__[30];
    double c_weights__[900]	/* was [30][30] */;
} ss_cbl__;

#define ss_cbl__1 ss_cbl__


/* Table of constant values */

static int c__2 = 2;
static int c__1 = 1;
static int c__0 = 0;
static int c_n1 = -1;
static int c__3 = 3;
static int c__4 = 4;
static int c__5 = 5;
static int c_n2 = -2;
static int c__6 = 6;
static int c_n3 = -3;
static int c__7 = 7;
static int c__8 = 8;
static int c_n4 = -4;
static int c__9 = 9;
static int c__10 = 10;
static int c__11 = 11;
static int c__12 = 12;
static int c__13 = 13;
static int c__14 = 14;
static int c__15 = 15;
static int c__16 = 16;
static int c__30 = 30;
static int c__31 = 31;
static double c_b4482 = (double)1.;
static int c__25 = 25;



/*F:draw2d_ss_1s*

________________________________________________________________

		draw2d_ss_1s
________________________________________________________________

Name:		draw2d_ss_1s
Syntax:		@draw2d_ss_1s-syntax
Description:

 	 The program generates a unit variance stochasic field on a grid.
	 The variogram-structure is defined by a correlation function
	 defined in 'correlation' which is a function from class Correlation.


	 The dimension of W_GRID is at least (2**dyad_dimension+1)**2,
         where dyad_dimension=INT(LOG(MAX(NX,NY)-1)/LOG(2)+.999999).

Side effects:
Return value: 0 OK,
              1 error singular covariance matrix,
              2 dimension error of grid

________________________________________________________________

*/

/*<draw2d_ss_1s-syntax: */
void SimGaussField2D::draw2d_ss_1s(int *i_dx__,
		  int *i_nx__,
		  int *i_ny__,
		  float *o_grid__,
		  double *w_grid__)
/*>draw2d_ss_1s-syntax: */
{

    /* System generated locals */
    int o_grid_dim1, o_grid_offset, i__1, i__2, i__3;


    /* Local variables */
    static int l_lag__, l_dyaddim__;
    static int l_i__, l_j__, l_x__, l_y__, l_level__, l_mxind__;
    float *grid;
    assert(i_dx__);
    assert(i_nx__);
    assert(i_ny__);
    assert(o_grid__);
    assert(w_grid__);

    /* Parameter adjustments */
    --w_grid__;
    o_grid_dim1 = *i_dx__;
    o_grid_offset = o_grid_dim1 + 1;
    o_grid__ -= o_grid_offset;

    /* Function Body */
    if (*i_nx__ * *i_ny__ <= 1) {
      moduleError(KERNEL,"draw2d_ss_1s",
		  "Illegal definition of grid size");
    }
    l_dyaddim__ = (int )
	(log(MAXIM(*i_nx__,*i_ny__) - (double)1.) / log((double)2.) + (
	    double).9999);
    l_mxind__ = (int) ldexp(1.0, l_dyaddim__) + 1;
    l_lag__ = (int) ldexp(1.0, l_dyaddim__);
/*--------DRAW THE CORNERS---------------------------------------- */
    init_c_patt();
    l_x__ = 1;
    l_y__ = 1;
    init_weights_s(&c__1,  &c__0);
    draw_node(&c__1, &c__0, &l_mxind__, &l_x__, &l_y__, &w_grid__[1]);
    l_x__ = l_mxind__;
    l_y__ = l_mxind__;
    make_patt(&c__1, &l_lag__, &c__1, &c_n1, &c_n1);
    init_weights_s(&c__1,  &c__1);
    draw_node(&c__1, &c__1, &l_mxind__, &l_x__, &l_y__, &w_grid__[1]);
    l_x__ = l_mxind__;
    l_y__ = 1;
    make_patt(&c__1, &l_lag__, &c__1, &c_n1, &c__0);
    make_patt(&c__1, &l_lag__, &c__2, &c__0, &c__1);
    init_weights_s(&c__1,  &c__2);
    draw_node(&c__1, &c__2, &l_mxind__, &l_x__, &l_y__, &w_grid__[1]);
    l_x__ = 1;
    l_y__ = l_mxind__;
    make_patt(&c__1, &l_lag__, &c__1, &c__0, &c_n1);
    make_patt(&c__1, &l_lag__, &c__2, &c__1, &c__0);
    make_patt(&c__1, &l_lag__, &c__3, &c__1, &c_n1);
    init_weights_s(&c__1,  &c__3);
    draw_node(&c__1, &c__3, &l_mxind__, &l_x__, &l_y__, &w_grid__[1]);
/*--------DRAW THE REST OF THE NODES IN A FRACTAL FASHION----------------
-----*/
    i__1 = l_dyaddim__ - 1;
    for (l_level__ = 0; l_level__ <= i__1; ++l_level__) {
	i__2 = l_dyaddim__ - l_level__ - 1;
	l_lag__ = (int) ldexp(1.0, i__2);
/* ----------------------DRAW THE CENTER NODES OF THE SQUARES WITH COR
NERS */
/*                      DEFINED BY THE NODES OF THE PREVIOUS LEVEL */
	make_patt(&c__1, &l_lag__, &c__1, &c_n1, &c_n1);
	make_patt(&c__1, &l_lag__, &c__2, &c_n1, &c__1);
	make_patt(&c__1, &l_lag__, &c__3, &c__1, &c_n1);
	make_patt(&c__1, &l_lag__, &c__4, &c__1, &c__1);
	init_weights_s(&c__1,  &c__4);
	i__2 = (int) ldexp(1.0, l_level__);
	for (l_i__ = 1; l_i__ <= i__2; ++l_i__) {
	    l_x__ = ((l_i__ << 1) - 1) * l_lag__ + 1;
	    i__3 = (int) ldexp(1.0, l_level__);
	    for (l_j__ = 1; l_j__ <= i__3; ++l_j__) {
		l_y__ = ((l_j__ << 1) - 1) * l_lag__ + 1;
		draw_node(&c__1, &c__4, &l_mxind__, &l_x__, &l_y__, &
			w_grid__[1]);
	    }
	}
/*----------------------DRAW THE CENTER NODES OF THE TILTED SQUARES WI
TH CORNERS*/
/*                     DEFINED BY THE NODES OF THIS AND THE THE PREVIO
US LEVEL*/
	make_patt(&c__1, &l_lag__, &c__1, &c__0, &c_n1);
	make_patt(&c__1, &l_lag__, &c__2, &c__0, &c__1);
	make_patt(&c__1, &l_lag__, &c__3, &c_n1, &c__0);
	make_patt(&c__1, &l_lag__, &c__4, &c__1, &c__0);
	init_weights_s(&c__1,  &c__4);
	i__2 = (int) ldexp(1.0, l_level__) - 1;
	for (l_i__ = 1; l_i__ <= i__2; ++l_i__) {
	  l_x__ = (l_i__ << 1) * l_lag__ + 1;
	  i__3 = (int) ldexp(1.0, l_level__);
	  for (l_j__ = 1; l_j__ <= i__3; ++l_j__) {
	    l_y__ = ((l_j__ << 1) - 1) * l_lag__ + 1;
	    draw_node(&c__1, &c__4, &l_mxind__, &l_x__, &l_y__, &
		      w_grid__[1]);
	    draw_node(&c__1, &c__4, &l_mxind__, &l_y__, &l_x__, &
		      w_grid__[1]);
	  }
	}
/* ----------------------DRAW THE BOARDER NODES ON THE FOUR EDGES */

	l_y__ = 1;
	make_patt(&c__1, &l_lag__, &c__1, &c_n1, &c__0);
	make_patt(&c__1, &l_lag__, &c__2, &c__1, &c__0);
	make_patt(&c__1, &l_lag__, &c__3, &c__0, &c__1);
	init_weights_s(&c__1,  &c__3);
	i__2 = (int) ldexp(1.0, l_level__);
	for (l_i__ = 1; l_i__ <= i__2; ++l_i__) {
	  l_x__ = ((l_i__ << 1) - 1) * l_lag__ + 1;
	  draw_node(&c__1, &c__3, &l_mxind__, &l_x__, &l_y__, &w_grid__[1]
		    );
	}
	l_y__ = l_mxind__;
	make_patt(&c__1, &l_lag__, &c__1, &c_n1, &c__0);
	make_patt(&c__1, &l_lag__, &c__2, &c__1, &c__0);
	make_patt(&c__1, &l_lag__, &c__3, &c__0, &c_n1);
	init_weights_s(&c__1,  &c__3);
	i__2 = (int) ldexp(1.0, l_level__);
	for (l_i__ = 1; l_i__ <= i__2; ++l_i__) {
	  l_x__ = ((l_i__ << 1) - 1) * l_lag__ + 1;
	  draw_node(&c__1, &c__3, &l_mxind__, &l_x__, &l_y__, &w_grid__[1]
		    );
	}
	l_x__ = 1;
	make_patt(&c__1, &l_lag__, &c__1, &c__0, &c_n1);
	make_patt(&c__1, &l_lag__, &c__2, &c__0, &c__1);
	make_patt(&c__1, &l_lag__, &c__3, &c__1, &c__0);
	init_weights_s(&c__1,  &c__3);
	i__2 = (int) ldexp(1.0, l_level__);
	for (l_j__ = 1; l_j__ <= i__2; ++l_j__) {
	  l_y__ = ((l_j__ << 1) - 1) * l_lag__ + 1;
	  draw_node(&c__1, &c__3, &l_mxind__, &l_x__, &l_y__, &w_grid__[1]
		    );
	}
	l_x__ = l_mxind__;
	make_patt(&c__1, &l_lag__, &c__1, &c__0, &c_n1);
	make_patt(&c__1, &l_lag__, &c__2, &c__0, &c__1);
	make_patt(&c__1, &l_lag__, &c__3, &c_n1, &c__0);
	init_weights_s(&c__1,  &c__3);
	i__2 = (int) ldexp(1.0, l_level__);
	for (l_j__ = 1; l_j__ <= i__2; ++l_j__) {
	  l_y__ = ((l_j__ << 1) - 1) * l_lag__ + 1;
	  draw_node(&c__1, &c__3, &l_mxind__, &l_x__, &l_y__, &w_grid__[1]
		    );
	}
      }
    i__1 = *i_ny__;
    for (l_y__ = 1; l_y__ <= i__1; ++l_y__) {
      i__2 = *i_nx__;
      for (l_x__ = 1; l_x__ <= i__2; ++l_x__) {
	l_i__ = l_x__ + (l_y__ - 1) * l_mxind__;
	o_grid__[l_x__ + l_y__ * o_grid_dim1] = w_grid__[l_i__];
      }
    }

    grid = o_grid__;
    grid += o_grid_offset;
    if(checkSimulatedVariance(grid,(*i_nx__),(*i_ny__))){
      moduleError(KERNEL,"draw2d_ss_1s",
		  "%s\n%s\n%s",
		  "Numerical problems in simulation of gaussian field.",
		  "Maybe too high correlation between neighbour nodes or",
		  "too high anisotropy");
    }
    return ;
  } /* draw2d_ss_1s */



/*F:draw2d_ss_1o*

________________________________________________________________

		draw2d_ss_1o
________________________________________________________________

Name:		draw2d_ss_1o
Syntax:		@draw2d_ss_1o-syntax
Description:

 	 The program generates a unit variance stochasic field on a grid.
	 The variogram-structure is defined by a correlation function
	 defined by the  function 'correlation' in class Correlation.

	 The dimension of W_GRID is at least (2**dyad_dimension+1)**2,
         where dyad_dimension=INT(LOG(MAX(NX,NY)-1)/LOG(2)+.999999).

Side effects:
Return value: 0 OK,
              1 error singular covariance matrix,
              2 dimension error of grid

________________________________________________________________

*/
/*<draw2d_ss_1o-syntax: */
void SimGaussField2D::draw2d_ss_1o(int *i_dx__,
				   int *i_nx__,
				   int *i_ny__,
				   float *o_grid__,
				   double *w_grid__)
/*>draw2d_ss_1o-syntax: */
{
    /* System generated locals */
    int o_grid_dim1, o_grid_offset, i__1, i__2, i__3;


    /* Local variables */
    static int l_lag__, l_dyaddim__;
    static int l_i__, l_j__, l_x__, l_y__, l_level__, l_mxind__;
    float *grid;

    assert(i_dx__);
    assert(i_nx__);
    assert(i_ny__);
    assert(o_grid__);
    assert(w_grid__);

    /* Parameter adjustments */
    --w_grid__;
    o_grid_dim1 = *i_dx__;
    o_grid_offset = o_grid_dim1 + 1;
    o_grid__ -= o_grid_offset;

    /* Function Body */
    if (*i_nx__ * *i_ny__ <= 1) {
      moduleError(KERNEL,"draw2d_ss_1o",
		  "Illegal definition of grid size");
    }
    l_dyaddim__ = (int)
	(log(MAXIM(*i_nx__,*i_ny__) - (double)1.) / log((double)2.) + (
	    double).9999);
    l_mxind__ = (int) ldexp(1.0, l_dyaddim__) + 1;
    l_lag__ = (int) ldexp(1.0, l_dyaddim__);
/*--------DRAW THE CORNERS-----------------------------------------------
--*/
    init_c_patt();
    l_x__ = 1;
    l_y__ = 1;
    init_weights_o(&c__1,  &c__0);
    draw_node(&c__1, &c__0, &l_mxind__, &l_x__, &l_y__, &w_grid__[1]);
    l_x__ = l_mxind__;
    l_y__ = l_mxind__;
    make_patt(&c__1, &l_lag__, &c__1, &c_n1, &c_n1);
    init_weights_o(&c__1,  &c__1);
    draw_node(&c__1, &c__1, &l_mxind__, &l_x__, &l_y__, &w_grid__[1]);
    l_x__ = l_mxind__;
    l_y__ = 1;
    make_patt(&c__1, &l_lag__, &c__1, &c_n1, &c__0);
    make_patt(&c__1, &l_lag__, &c__2, &c__0, &c__1);
    init_weights_o(&c__1,  &c__2);
    draw_node(&c__1, &c__2, &l_mxind__, &l_x__, &l_y__, &w_grid__[1]);
    l_x__ = 1;
    l_y__ = l_mxind__;
    make_patt(&c__1, &l_lag__, &c__1, &c__0, &c_n1);
    make_patt(&c__1, &l_lag__, &c__2, &c__1, &c__0);
    make_patt(&c__1, &l_lag__, &c__3, &c__1, &c_n1);
    init_weights_o(&c__1,  &c__3);
    draw_node(&c__1, &c__3, &l_mxind__, &l_x__, &l_y__, &w_grid__[1]);
/*--------DRAW THE REST OF THE NODES IN A FRACTAL FASHION----------------
-----*/
    i__1 = l_dyaddim__ - 1;
    for (l_level__ = 0; l_level__ <= i__1; ++l_level__) {
	i__2 = l_dyaddim__ - l_level__ - 1;
	l_lag__ = (int) ldexp(1.0, i__2);
/* ----------------------DRAW THE CENTER NODES OF THE SQUARES WITH COR
NERS */
/*                      DEFINED BY THE NODES OF THE PREVIOUS LEVEL */
	make_patt(&c__1, &l_lag__, &c__1, &c_n1, &c_n1);
	make_patt(&c__1, &l_lag__, &c__2, &c_n1, &c__1);
	make_patt(&c__1, &l_lag__, &c__3, &c__1, &c_n1);
	make_patt(&c__1, &l_lag__, &c__4, &c__1, &c__1);
	init_weights_o(&c__1,  &c__4);
	i__2 = (int) ldexp(1.0, l_level__);
	for (l_i__ = 1; l_i__ <= i__2; ++l_i__) {
	    l_x__ = ((l_i__ << 1) - 1) * l_lag__ + 1;
	    i__3 = (int) ldexp(1.0, l_level__);
	    for (l_j__ = 1; l_j__ <= i__3; ++l_j__) {
		l_y__ = ((l_j__ << 1) - 1) * l_lag__ + 1;
		draw_node(&c__1, &c__4, &l_mxind__, &l_x__, &l_y__, &
			w_grid__[1]);
	    }
	}
/*----------------------DRAW THE CENTER NODES OF THE TILTED SQUARES WI
TH CORNERS*/
/*                     DEFINED BY THE NODES OF THIS AND THE THE PREVIO
US LEVEL*/
	make_patt(&c__1, &l_lag__, &c__1, &c__0, &c_n1);
	make_patt(&c__1, &l_lag__, &c__2, &c__0, &c__1);
	make_patt(&c__1, &l_lag__, &c__3, &c_n1, &c__0);
	make_patt(&c__1, &l_lag__, &c__4, &c__1, &c__0);
	init_weights_o(&c__1,  &c__4);
	i__2 = (int) ldexp(1.0, l_level__) - 1;
	for (l_i__ = 1; l_i__ <= i__2; ++l_i__) {
	    l_x__ = (l_i__ << 1) * l_lag__ + 1;
	    i__3 = (int) ldexp(1.0, l_level__);
	    for (l_j__ = 1; l_j__ <= i__3; ++l_j__) {
		l_y__ = ((l_j__ << 1) - 1) * l_lag__ + 1;
		draw_node(&c__1, &c__4, &l_mxind__, &l_x__, &l_y__, &
			w_grid__[1]);
		draw_node(&c__1, &c__4, &l_mxind__, &l_y__, &l_x__, &
			w_grid__[1]);
	    }
	}
/* ----------------------DRAW THE BOARDER NODES ON THE FOUR EDGES */

	l_y__ = 1;
	make_patt(&c__1, &l_lag__, &c__1, &c_n1, &c__0);
	make_patt(&c__1, &l_lag__, &c__2, &c__1, &c__0);
	make_patt(&c__1, &l_lag__, &c__3, &c__0, &c__1);
	init_weights_o(&c__1,  &c__3);
	i__2 = (int) ldexp(1.0, l_level__);
	for (l_i__ = 1; l_i__ <= i__2; ++l_i__) {
	    l_x__ = ((l_i__ << 1) - 1) * l_lag__ + 1;
	    draw_node(&c__1, &c__3, &l_mxind__, &l_x__, &l_y__, &w_grid__[1]
		    );
	}
	l_y__ = l_mxind__;
	make_patt(&c__1, &l_lag__, &c__1, &c_n1, &c__0);
	make_patt(&c__1, &l_lag__, &c__2, &c__1, &c__0);
	make_patt(&c__1, &l_lag__, &c__3, &c__0, &c_n1);
	init_weights_o(&c__1,  &c__3);
	i__2 = (int) ldexp(1.0, l_level__);
	for (l_i__ = 1; l_i__ <= i__2; ++l_i__) {
	    l_x__ = ((l_i__ << 1) - 1) * l_lag__ + 1;
	    draw_node(&c__1, &c__3, &l_mxind__, &l_x__, &l_y__, &w_grid__[1]
		    );
	}
	l_x__ = 1;
	make_patt(&c__1, &l_lag__, &c__1, &c__0, &c_n1);
	make_patt(&c__1, &l_lag__, &c__2, &c__0, &c__1);
	make_patt(&c__1, &l_lag__, &c__3, &c__1, &c__0);
	init_weights_o(&c__1,  &c__3);
	i__2 = (int) ldexp(1.0, l_level__);
	for (l_j__ = 1; l_j__ <= i__2; ++l_j__) {
	    l_y__ = ((l_j__ << 1) - 1) * l_lag__ + 1;
	    draw_node(&c__1, &c__3, &l_mxind__, &l_x__, &l_y__, &w_grid__[1]
		    );
	}
	l_x__ = l_mxind__;
	make_patt(&c__1, &l_lag__, &c__1, &c__0, &c_n1);
	make_patt(&c__1, &l_lag__, &c__2, &c__0, &c__1);
	make_patt(&c__1, &l_lag__, &c__3, &c_n1, &c__0);
	init_weights_o(&c__1,  &c__3);
	i__2 = (int) ldexp(1.0, l_level__);
	for (l_j__ = 1; l_j__ <= i__2; ++l_j__) {
	    l_y__ = ((l_j__ << 1) - 1) * l_lag__ + 1;
	    draw_node(&c__1, &c__3, &l_mxind__, &l_x__, &l_y__, &w_grid__[1]
		    );
	}
    }
    i__1 = *i_ny__;
    for (l_y__ = 1; l_y__ <= i__1; ++l_y__) {
	i__2 = *i_nx__;
	for (l_x__ = 1; l_x__ <= i__2; ++l_x__) {
	    l_i__ = l_x__ + (l_y__ - 1) * l_mxind__;
	    o_grid__[l_x__ + l_y__ * o_grid_dim1] = w_grid__[l_i__];
	}
    }

    grid = o_grid__;
    grid += o_grid_offset;
    if(checkSimulatedVariance(grid,(*i_nx__),(*i_ny__))){
      moduleError(KERNEL,"draw2d_ss_1o",
		  "%s\n%s",
		  "Numerical problems in simulation of gaussian field.",
		  "Maybe too high correlation between neighbour nodes.");
    }

    return  ;
} /* draw2d_ss_1o */


void SimGaussField2D::draw2d_ss_2s(int *i_dx__,
				   int *i_nx__,
				   int *i_ny__,
				   float *o_grid__,
				   double *w_grid__)
{
    /* System generated locals */
    int o_grid_dim1, o_grid_offset, i__1, i__2, i__3;

    /* Builtin functions */



    /* Local variables */
    static int l_lag__, l_dyaddim__;
    static int l_i__, l_j__, l_x__, l_y__, l_level__, l_mxind__;
    float *grid;

    assert(i_dx__);
    assert(i_nx__);
    assert(i_ny__);
    assert(o_grid__);
    assert(w_grid__);

    /* Parameter adjustments */
    --w_grid__;
    o_grid_dim1 = *i_dx__;
    o_grid_offset = o_grid_dim1 + 1;
    o_grid__ -= o_grid_offset;

    /* Function Body */
    if (*i_nx__ * *i_ny__ <= 1) {
      moduleError(KERNEL,"draw2d_ss_2s",
		  "Illegal definition of grid size");
    }
    l_dyaddim__ = (int)
	(log(MAXIM(*i_nx__,*i_ny__) - (double)1.) / log((double)2.) + (
	    double).9999);
    l_mxind__ = (int) ldexp(1.0, l_dyaddim__) + 1;
    l_lag__ = (int) ldexp(1.0, l_dyaddim__);
/*--------DRAW THE CORNERS-----------------------------------------------
--*/
    init_c_patt();
    l_x__ = 1;
    l_y__ = 1;
    init_weights_s(&c__1,  &c__0);
    draw_node(&c__1, &c__0, &l_mxind__, &l_x__, &l_y__, &w_grid__[1]);
    l_x__ = l_mxind__;
    l_y__ = l_mxind__;
    make_patt(&c__1, &l_lag__, &c__1, &c_n1, &c_n1);
    init_weights_s(&c__1,  &c__1);
    draw_node(&c__1, &c__1, &l_mxind__, &l_x__, &l_y__, &w_grid__[1]);
    l_x__ = l_mxind__;
    l_y__ = 1;
    make_patt(&c__1, &l_lag__, &c__1, &c_n1, &c__0);
    make_patt(&c__1, &l_lag__, &c__2, &c__0, &c__1);
    init_weights_s(&c__1,  &c__2);
    draw_node(&c__1, &c__2, &l_mxind__, &l_x__, &l_y__, &w_grid__[1]);
    l_x__ = 1;
    l_y__ = l_mxind__;
    make_patt(&c__1, &l_lag__, &c__1, &c__0, &c_n1);
    make_patt(&c__1, &l_lag__, &c__2, &c__1, &c__0);
    make_patt(&c__1, &l_lag__, &c__3, &c__1, &c_n1);
    init_weights_s(&c__1,  &c__3);
    draw_node(&c__1, &c__3, &l_mxind__, &l_x__, &l_y__, &w_grid__[1]);
/*--------DRAW THE REST OF THE NODES IN A FRACTAL FASHION----------------
-----*/
    i__1 = l_dyaddim__ - 1;
    for (l_level__ = 0; l_level__ <= i__1; ++l_level__) {
	i__2 = l_dyaddim__ - l_level__ - 1;
	l_lag__ = (int) ldexp(1.0, i__2);
/* ----------------------DRAW THE CENTER NODES OF THE SQUARES WITH COR
NERS */
/*                      DEFINED BY THE NODES OF THE PREVIOUS LEVEL */
	make_patt(&c__1, &l_lag__, &c__1, &c_n1, &c_n1);
	make_patt(&c__1, &l_lag__, &c__2, &c_n1, &c__1);
	make_patt(&c__1, &l_lag__, &c__3, &c__1, &c_n1);
	make_patt(&c__1, &l_lag__, &c__4, &c__1, &c__1);
	make_patt(&c__2, &l_lag__, &c__1, &c_n1, &c_n1);
	make_patt(&c__2, &l_lag__, &c__2, &c_n1, &c__1);
	make_patt(&c__2, &l_lag__, &c__3, &c__1, &c_n1);
	make_patt(&c__2, &l_lag__, &c__4, &c__1, &c__1);
	make_patt(&c__2, &l_lag__, &c__5, &c_n2, &c__0);
	make_patt(&c__3, &l_lag__, &c__1, &c_n1, &c_n1);
	make_patt(&c__3, &l_lag__, &c__2, &c_n1, &c__1);
	make_patt(&c__3, &l_lag__, &c__3, &c__1, &c_n1);
	make_patt(&c__3, &l_lag__, &c__4, &c__1, &c__1);
	make_patt(&c__3, &l_lag__, &c__5, &c__0, &c_n2);
	make_patt(&c__4, &l_lag__, &c__1, &c_n1, &c_n1);
	make_patt(&c__4, &l_lag__, &c__2, &c_n1, &c__1);
	make_patt(&c__4, &l_lag__, &c__3, &c__1, &c_n1);
	make_patt(&c__4, &l_lag__, &c__4, &c__1, &c__1);
	make_patt(&c__4, &l_lag__, &c__5, &c_n2, &c__0);
	make_patt(&c__4, &l_lag__, &c__6, &c__0, &c_n2);
	init_weights_s(&c__1,  &c__4);
	init_weights_s(&c__2,  &c__5);
	init_weights_s(&c__3,  &c__5);
	init_weights_s(&c__4,  &c__6);
	l_y__ = l_lag__ + 1;
	l_x__ = l_lag__ + 1;
	draw_node(&c__1, &c__4, &l_mxind__, &l_x__, &l_y__, &w_grid__[1]);
	i__2 = (int) ldexp(1.0, l_level__);
	for (l_i__ = 2; l_i__ <= i__2; ++l_i__) {
	    l_x__ = ((l_i__ << 1) - 1) * l_lag__ + 1;
	    draw_node(&c__2, &c__5, &l_mxind__, &l_x__, &l_y__, &w_grid__[1]
		    );
	}
	l_x__ = l_lag__ + 1;
	i__2 = (int) ldexp(1.0, l_level__);
	for (l_j__ = 2; l_j__ <= i__2; ++l_j__) {
	    l_y__ = ((l_j__ << 1) - 1) * l_lag__ + 1;
	    draw_node(&c__3, &c__5, &l_mxind__, &l_x__, &l_y__, &w_grid__[1]
		    );
	}
	i__2 = (int) ldexp(1.0, l_level__);
	for (l_i__ = 2; l_i__ <= i__2; ++l_i__) {
	    l_x__ = ((l_i__ << 1) - 1) * l_lag__ + 1;
	    i__3 = (int) ldexp(1.0, l_level__);
	    for (l_j__ = 2; l_j__ <= i__3; ++l_j__) {
		l_y__ = ((l_j__ << 1) - 1) * l_lag__ + 1;
		draw_node(&c__4, &c__6, &l_mxind__, &l_x__, &l_y__, &
			w_grid__[1]);
	    }
	}
/*----------------------DRAW THE CENTER NODES OF THE TILTED SQUARES WI
TH CORNERS*/
/*                     DEFINED BY THE NODES OF THIS AND THE THE PREVIO
US LEVEL*/
	make_patt(&c__1, &l_lag__, &c__1, &c__0, &c_n1);
	make_patt(&c__1, &l_lag__, &c__2, &c__0, &c__1);
	make_patt(&c__1, &l_lag__, &c__3, &c_n1, &c__0);
	make_patt(&c__1, &l_lag__, &c__4, &c__1, &c__0);
	make_patt(&c__2, &l_lag__, &c__1, &c__0, &c_n1);
	make_patt(&c__2, &l_lag__, &c__2, &c__0, &c__1);
	make_patt(&c__2, &l_lag__, &c__3, &c_n1, &c__0);
	make_patt(&c__2, &l_lag__, &c__4, &c__1, &c__0);
	make_patt(&c__2, &l_lag__, &c__5, &c_n1, &c_n1);
	make_patt(&c__3, &l_lag__, &c__1, &c__0, &c_n1);
	make_patt(&c__3, &l_lag__, &c__2, &c__0, &c__1);
	make_patt(&c__3, &l_lag__, &c__3, &c_n1, &c__0);
	make_patt(&c__3, &l_lag__, &c__4, &c__1, &c__0);
	make_patt(&c__3, &l_lag__, &c__5, &c__1, &c_n1);
	make_patt(&c__4, &l_lag__, &c__1, &c__0, &c_n1);
	make_patt(&c__4, &l_lag__, &c__2, &c__0, &c__1);
	make_patt(&c__4, &l_lag__, &c__3, &c_n1, &c__0);
	make_patt(&c__4, &l_lag__, &c__4, &c__1, &c__0);
	make_patt(&c__4, &l_lag__, &c__5, &c_n1, &c_n1);
	make_patt(&c__4, &l_lag__, &c__6, &c__1, &c_n1);
	init_weights_s(&c__1,  &c__4);
	init_weights_s(&c__2,  &c__5);
	init_weights_s(&c__3,  &c__5);
	init_weights_s(&c__4,  &c__6);
	l_y__ = l_lag__ + 1;
	i__2 = (int) ldexp(1.0, l_level__) - 1;
	for (l_i__ = 1; l_i__ <= i__2; ++l_i__) {
	    l_x__ = (l_i__ << 1) * l_lag__ + 1;
	    draw_node(&c__1, &c__4, &l_mxind__, &l_x__, &l_y__, &w_grid__[1]
		    );
	}
	i__2 = (int) ldexp(1.0, l_level__) - 1;
	for (l_j__ = 1; l_j__ <= i__2; ++l_j__) {
	    l_x__ = l_mxind__ - l_lag__;
	    l_y__ = (l_j__ << 1) * l_lag__ + 1;
	    draw_node(&c__2, &c__5, &l_mxind__, &l_x__, &l_y__, &w_grid__[1]
		    );
	    l_x__ = l_lag__ + 1;
	    draw_node(&c__3, &c__5, &l_mxind__, &l_x__, &l_y__, &w_grid__[1]
		    );
	    i__3 = (int) ldexp(1.0, l_level__) - 1;
	    for (l_i__ = 2; l_i__ <= i__3; ++l_i__) {
		l_x__ = ((l_i__ << 1) - 1) * l_lag__ + 1;
		draw_node(&c__4, &c__6, &l_mxind__, &l_x__, &l_y__, &
			w_grid__[1]);
	    }
	    l_y__ = ((l_j__ << 1) + 1) * l_lag__ + 1;
	    i__3 = (int) ldexp(1.0, l_level__) - 1;
	    for (l_i__ = 1; l_i__ <= i__3; ++l_i__) {
		l_x__ = (l_i__ << 1) * l_lag__ + 1;
		draw_node(&c__4, &c__6, &l_mxind__, &l_x__, &l_y__, &
			w_grid__[1]);
	    }
	}
/* ----------------------DRAW THE BOARDER NODES ON THE FOUR EDGES */

	make_patt(&c__1, &l_lag__, &c__1, &c_n1, &c__0);
	make_patt(&c__1, &l_lag__, &c__2, &c__1, &c__0);
	make_patt(&c__1, &l_lag__, &c__3, &c__0, &c__1);
	make_patt(&c__1, &l_lag__, &c__4, &c__1, &c__1);
	make_patt(&c__2, &l_lag__, &c__1, &c__0, &c_n1);
	make_patt(&c__2, &l_lag__, &c__2, &c__0, &c__1);
	make_patt(&c__2, &l_lag__, &c__3, &c__1, &c_n1);
	make_patt(&c__2, &l_lag__, &c__4, &c__1, &c__0);
	make_patt(&c__2, &l_lag__, &c__5, &c__1, &c__1);
	make_patt(&c__3, &l_lag__, &c__1, &c_n1, &c__0);
	make_patt(&c__3, &l_lag__, &c__2, &c__1, &c__0);
	make_patt(&c__3, &l_lag__, &c__3, &c_n1, &c_n1);
	make_patt(&c__3, &l_lag__, &c__4, &c__0, &c_n1);
	make_patt(&c__3, &l_lag__, &c__5, &c__1, &c_n1);
	make_patt(&c__4, &l_lag__, &c__1, &c__0, &c_n1);
	make_patt(&c__4, &l_lag__, &c__2, &c__0, &c__1);
	make_patt(&c__4, &l_lag__, &c__3, &c_n1, &c_n1);
	make_patt(&c__4, &l_lag__, &c__4, &c_n1, &c__0);
	make_patt(&c__4, &l_lag__, &c__5, &c_n1, &c__1);
	make_patt(&c__5, &l_lag__, &c__1, &c_n1, &c__0);
	make_patt(&c__5, &l_lag__, &c__2, &c__1, &c__0);
	make_patt(&c__5, &l_lag__, &c__3, &c_n1, &c__1);
	make_patt(&c__5, &l_lag__, &c__4, &c__0, &c__1);
	make_patt(&c__5, &l_lag__, &c__5, &c__1, &c__1);
	init_weights_s(&c__1,  &c__4);
	init_weights_s(&c__2,  &c__5);
	init_weights_s(&c__3,  &c__5);
	init_weights_s(&c__4,  &c__5);
	init_weights_s(&c__5,  &c__5);
	l_x__ = l_lag__ + 1;
	l_y__ = 1;
	draw_node(&c__1, &c__4, &l_mxind__, &l_x__, &l_y__, &w_grid__[1]);
	l_x__ = 1;
	i__2 = (int) ldexp(1.0, l_level__);
	for (l_j__ = 1; l_j__ <= i__2; ++l_j__) {
	    l_y__ = ((l_j__ << 1) - 1) * l_lag__ + 1;
	    draw_node(&c__2, &c__5, &l_mxind__, &l_x__, &l_y__, &w_grid__[1]
		    );
	}
	l_y__ = l_mxind__;
	i__2 = (int) ldexp(1.0, l_level__);
	for (l_i__ = 1; l_i__ <= i__2; ++l_i__) {
	    l_x__ = ((l_i__ << 1) - 1) * l_lag__ + 1;
	    draw_node(&c__3, &c__5, &l_mxind__, &l_x__, &l_y__, &w_grid__[1]
		    );
	}
	l_x__ = l_mxind__;
	for (l_j__ = (int) ldexp(1.0, l_level__); l_j__ >= 1; --l_j__) {
	    l_y__ = ((l_j__ << 1) - 1) * l_lag__ + 1;
	    draw_node(&c__4, &c__5, &l_mxind__, &l_x__, &l_y__, &w_grid__[1]
		    );
	}
	l_y__ = 1;
	for (l_i__ = (int) ldexp(1.0, l_level__); l_i__ >= 1; --l_i__) {
	    l_x__ = ((l_i__ << 1) - 1) * l_lag__ + 1;
	    draw_node(&c__5, &c__5, &l_mxind__, &l_x__, &l_y__, &w_grid__[1]
		    );
	}
    }
    i__1 = *i_ny__;
    for (l_y__ = 1; l_y__ <= i__1; ++l_y__) {
	i__2 = *i_nx__;
	for (l_x__ = 1; l_x__ <= i__2; ++l_x__) {
	    l_i__ = l_x__ + (l_y__ - 1) * l_mxind__;
	    o_grid__[l_x__ + l_y__ * o_grid_dim1] = w_grid__[l_i__];
	}
    }

    grid = o_grid__;
    grid += o_grid_offset;
    if(checkSimulatedVariance(grid,(*i_nx__),(*i_ny__))){
      moduleError(KERNEL,"draw2d_ss_2s",
		  "%s\n%s\n%s",
		  "Numerical problems in simulation of gaussian field.",
		  "Maybe too high correlation between neighbour nodes or",
		  "too high anisotropy");
    }

    return  ;
} /* draw2d_ss_2s */

void SimGaussField2D::draw2d_ss_2o(int *i_dx__,
				   int *i_nx__,
				   int *i_ny__,
				   float *o_grid__,
				   double *w_grid__)
{
    /* System generated locals */
    int o_grid_dim1, o_grid_offset, i__1, i__2, i__3;

    /* Builtin functions */


    /* Local variables */
    static int l_lag__, l_dyaddim__;
    static int l_i__, l_j__, l_x__, l_y__, l_level__, l_mxind__;
    float *grid;

    assert(i_dx__);
    assert(i_nx__);
    assert(i_ny__);
    assert(o_grid__);
    assert(w_grid__);

    /* Parameter adjustments */
    --w_grid__;
    o_grid_dim1 = *i_dx__;
    o_grid_offset = o_grid_dim1 + 1;
    o_grid__ -= o_grid_offset;

    /* Function Body */
    if (*i_nx__ * *i_ny__ <= 1) {
      moduleError(KERNEL,"draw2d_ss_2o",
		  "Illegal definition of grid size");
    }
    l_dyaddim__ = (int)
	(log(MAXIM(*i_nx__,*i_ny__) - (double)1.) / log((double)2.) + (
	    double).9999);
    l_mxind__ = (int) ldexp(1.0, l_dyaddim__) + 1;
    l_lag__ = (int) ldexp(1.0, l_dyaddim__);

/*--------DRAW THE CORNERS-----------------------------------------------
--*/
    init_c_patt();
    l_x__ = 1;
    l_y__ = 1;
    init_weights_o(&c__1,  &c__0);
    draw_node(&c__1, &c__0, &l_mxind__, &l_x__, &l_y__, &w_grid__[1]);
    l_x__ = l_mxind__;
    l_y__ = l_mxind__;
    make_patt(&c__1, &l_lag__, &c__1, &c_n1, &c_n1);
    init_weights_o(&c__1,  &c__1);
    draw_node(&c__1, &c__1, &l_mxind__, &l_x__, &l_y__, &w_grid__[1]);
    l_x__ = l_mxind__;
    l_y__ = 1;
    make_patt(&c__1, &l_lag__, &c__1, &c_n1, &c__0);
    make_patt(&c__1, &l_lag__, &c__2, &c__0, &c__1);
    init_weights_o(&c__1,  &c__2);
    draw_node(&c__1, &c__2, &l_mxind__, &l_x__, &l_y__, &w_grid__[1]);
    l_x__ = 1;
    l_y__ = l_mxind__;
    make_patt(&c__1, &l_lag__, &c__1, &c__0, &c_n1);
    make_patt(&c__1, &l_lag__, &c__2, &c__1, &c__0);
    make_patt(&c__1, &l_lag__, &c__3, &c__1, &c_n1);
    init_weights_o(&c__1,  &c__3);
    draw_node(&c__1, &c__3, &l_mxind__, &l_x__, &l_y__, &w_grid__[1]);
/*--------DRAW THE REST OF THE NODES IN A FRACTAL FASHION----------------
-----*/
    i__1 = l_dyaddim__ - 1;
    for (l_level__ = 0; l_level__ <= i__1; ++l_level__) {
	i__2 = l_dyaddim__ - l_level__ - 1;
	l_lag__ = (int) ldexp(1.0, i__2);
/* ----------------------DRAW THE CENTER NODES OF THE SQUARES WITH COR
NERS */
/*                      DEFINED BY THE NODES OF THE PREVIOUS LEVEL */
	make_patt(&c__1, &l_lag__, &c__1, &c_n1, &c_n1);
	make_patt(&c__1, &l_lag__, &c__2, &c_n1, &c__1);
	make_patt(&c__1, &l_lag__, &c__3, &c__1, &c_n1);
	make_patt(&c__1, &l_lag__, &c__4, &c__1, &c__1);
	make_patt(&c__2, &l_lag__, &c__1, &c_n1, &c_n1);
	make_patt(&c__2, &l_lag__, &c__2, &c_n1, &c__1);
	make_patt(&c__2, &l_lag__, &c__3, &c__1, &c_n1);
	make_patt(&c__2, &l_lag__, &c__4, &c__1, &c__1);
	make_patt(&c__2, &l_lag__, &c__5, &c_n2, &c__0);
	make_patt(&c__3, &l_lag__, &c__1, &c_n1, &c_n1);
	make_patt(&c__3, &l_lag__, &c__2, &c_n1, &c__1);
	make_patt(&c__3, &l_lag__, &c__3, &c__1, &c_n1);
	make_patt(&c__3, &l_lag__, &c__4, &c__1, &c__1);
	make_patt(&c__3, &l_lag__, &c__5, &c__0, &c_n2);
	make_patt(&c__4, &l_lag__, &c__1, &c_n1, &c_n1);
	make_patt(&c__4, &l_lag__, &c__2, &c_n1, &c__1);
	make_patt(&c__4, &l_lag__, &c__3, &c__1, &c_n1);
	make_patt(&c__4, &l_lag__, &c__4, &c__1, &c__1);
	make_patt(&c__4, &l_lag__, &c__5, &c_n2, &c__0);
	make_patt(&c__4, &l_lag__, &c__6, &c__0, &c_n2);
	init_weights_o(&c__1,  &c__4);
	init_weights_o(&c__2,  &c__5);
	init_weights_o(&c__3,  &c__5);
	init_weights_o(&c__4,  &c__6);
	l_y__ = l_lag__ + 1;
	l_x__ = l_lag__ + 1;
	draw_node(&c__1, &c__4, &l_mxind__, &l_x__, &l_y__, &w_grid__[1]);
	i__2 = (int) ldexp(1.0, l_level__);
	for (l_i__ = 2; l_i__ <= i__2; ++l_i__) {
	    l_x__ = ((l_i__ << 1) - 1) * l_lag__ + 1;
	    draw_node(&c__2, &c__5, &l_mxind__, &l_x__, &l_y__, &w_grid__[1]
		    );
	}
	l_x__ = l_lag__ + 1;
	i__2 = (int) ldexp(1.0, l_level__);
	for (l_j__ = 2; l_j__ <= i__2; ++l_j__) {
	    l_y__ = ((l_j__ << 1) - 1) * l_lag__ + 1;
	    draw_node(&c__3, &c__5, &l_mxind__, &l_x__, &l_y__, &w_grid__[1]
		    );
	}
	i__2 = (int) ldexp(1.0, l_level__);
	for (l_i__ = 2; l_i__ <= i__2; ++l_i__) {
	    l_x__ = ((l_i__ << 1) - 1) * l_lag__ + 1;
	    i__3 = (int) ldexp(1.0, l_level__);
	    for (l_j__ = 2; l_j__ <= i__3; ++l_j__) {
		l_y__ = ((l_j__ << 1) - 1) * l_lag__ + 1;
		draw_node(&c__4, &c__6, &l_mxind__, &l_x__, &l_y__, &
			w_grid__[1]);
	    }
	}
/*----------------------DRAW THE CENTER NODES OF THE TILTED SQUARES WI
TH CORNERS*/
/*                     DEFINED BY THE NODES OF THIS AND THE THE PREVIO
US LEVEL*/
	make_patt(&c__1, &l_lag__, &c__1, &c__0, &c_n1);
	make_patt(&c__1, &l_lag__, &c__2, &c__0, &c__1);
	make_patt(&c__1, &l_lag__, &c__3, &c_n1, &c__0);
	make_patt(&c__1, &l_lag__, &c__4, &c__1, &c__0);
	make_patt(&c__2, &l_lag__, &c__1, &c__0, &c_n1);
	make_patt(&c__2, &l_lag__, &c__2, &c__0, &c__1);
	make_patt(&c__2, &l_lag__, &c__3, &c_n1, &c__0);
	make_patt(&c__2, &l_lag__, &c__4, &c__1, &c__0);
	make_patt(&c__2, &l_lag__, &c__5, &c_n1, &c_n1);
	make_patt(&c__3, &l_lag__, &c__1, &c__0, &c_n1);
	make_patt(&c__3, &l_lag__, &c__2, &c__0, &c__1);
	make_patt(&c__3, &l_lag__, &c__3, &c_n1, &c__0);
	make_patt(&c__3, &l_lag__, &c__4, &c__1, &c__0);
	make_patt(&c__3, &l_lag__, &c__5, &c__1, &c_n1);
	make_patt(&c__4, &l_lag__, &c__1, &c__0, &c_n1);
	make_patt(&c__4, &l_lag__, &c__2, &c__0, &c__1);
	make_patt(&c__4, &l_lag__, &c__3, &c_n1, &c__0);
	make_patt(&c__4, &l_lag__, &c__4, &c__1, &c__0);
	make_patt(&c__4, &l_lag__, &c__5, &c_n1, &c_n1);
	make_patt(&c__4, &l_lag__, &c__6, &c__1, &c_n1);
	init_weights_o(&c__1,  &c__4);
	init_weights_o(&c__2,  &c__5);
	init_weights_o(&c__3,  &c__5);
	init_weights_o(&c__4,  &c__6);
	l_y__ = l_lag__ + 1;
	i__2 = (int) ldexp(1.0, l_level__) - 1;
	for (l_i__ = 1; l_i__ <= i__2; ++l_i__) {
	    l_x__ = (l_i__ << 1) * l_lag__ + 1;
	    draw_node(&c__1, &c__4, &l_mxind__, &l_x__, &l_y__, &w_grid__[1]
		    );
	}
	i__2 = (int) ldexp(1.0, l_level__) - 1;
	for (l_j__ = 1; l_j__ <= i__2; ++l_j__) {
	    l_x__ = l_mxind__ - l_lag__;
	    l_y__ = (l_j__ << 1) * l_lag__ + 1;
	    draw_node(&c__2, &c__5, &l_mxind__, &l_x__, &l_y__, &w_grid__[1]
		    );
	    l_x__ = l_lag__ + 1;
	    draw_node(&c__3, &c__5, &l_mxind__, &l_x__, &l_y__, &w_grid__[1]
		    );
	    i__3 = (int) ldexp(1.0, l_level__) - 1;
	    for (l_i__ = 2; l_i__ <= i__3; ++l_i__) {
		l_x__ = ((l_i__ << 1) - 1) * l_lag__ + 1;
		draw_node(&c__4, &c__6, &l_mxind__, &l_x__, &l_y__, &
			w_grid__[1]);
	    }
	    l_y__ = ((l_j__ << 1) + 1) * l_lag__ + 1;
	    i__3 = (int) ldexp(1.0, l_level__) - 1;
	    for (l_i__ = 1; l_i__ <= i__3; ++l_i__) {
		l_x__ = (l_i__ << 1) * l_lag__ + 1;
		draw_node(&c__4, &c__6, &l_mxind__, &l_x__, &l_y__, &
			w_grid__[1]);
	    }
	}
/* ----------------------DRAW THE BOARDER NODES ON THE FOUR EDGES */

	make_patt(&c__1, &l_lag__, &c__1, &c_n1, &c__0);
	make_patt(&c__1, &l_lag__, &c__2, &c__1, &c__0);
	make_patt(&c__1, &l_lag__, &c__3, &c__0, &c__1);
	make_patt(&c__1, &l_lag__, &c__4, &c__1, &c__1);
	make_patt(&c__2, &l_lag__, &c__1, &c__0, &c_n1);
	make_patt(&c__2, &l_lag__, &c__2, &c__0, &c__1);
	make_patt(&c__2, &l_lag__, &c__3, &c__1, &c_n1);
	make_patt(&c__2, &l_lag__, &c__4, &c__1, &c__0);
	make_patt(&c__2, &l_lag__, &c__5, &c__1, &c__1);
	make_patt(&c__3, &l_lag__, &c__1, &c_n1, &c__0);
	make_patt(&c__3, &l_lag__, &c__2, &c__1, &c__0);
	make_patt(&c__3, &l_lag__, &c__3, &c_n1, &c_n1);
	make_patt(&c__3, &l_lag__, &c__4, &c__0, &c_n1);
	make_patt(&c__3, &l_lag__, &c__5, &c__1, &c_n1);
	make_patt(&c__4, &l_lag__, &c__1, &c__0, &c_n1);
	make_patt(&c__4, &l_lag__, &c__2, &c__0, &c__1);
	make_patt(&c__4, &l_lag__, &c__3, &c_n1, &c_n1);
	make_patt(&c__4, &l_lag__, &c__4, &c_n1, &c__0);
	make_patt(&c__4, &l_lag__, &c__5, &c_n1, &c__1);
	make_patt(&c__5, &l_lag__, &c__1, &c_n1, &c__0);
	make_patt(&c__5, &l_lag__, &c__2, &c__1, &c__0);
	make_patt(&c__5, &l_lag__, &c__3, &c_n1, &c__1);
	make_patt(&c__5, &l_lag__, &c__4, &c__0, &c__1);
	make_patt(&c__5, &l_lag__, &c__5, &c__1, &c__1);
	init_weights_o(&c__1,  &c__4);
	init_weights_o(&c__2,  &c__5);
	init_weights_o(&c__3,  &c__5);
	init_weights_o(&c__4,  &c__5);
	init_weights_o(&c__5,  &c__5);
	l_x__ = l_lag__ + 1;
	l_y__ = 1;
	draw_node(&c__1, &c__4, &l_mxind__, &l_x__, &l_y__, &w_grid__[1]);
	l_x__ = 1;
	i__2 = (int) ldexp(1.0, l_level__);
	for (l_j__ = 1; l_j__ <= i__2; ++l_j__) {
	    l_y__ = ((l_j__ << 1) - 1) * l_lag__ + 1;
	    draw_node(&c__2, &c__5, &l_mxind__, &l_x__, &l_y__, &w_grid__[1]
		    );
	}
	l_y__ = l_mxind__;
	i__2 = (int) ldexp(1.0, l_level__);
	for (l_i__ = 1; l_i__ <= i__2; ++l_i__) {
	    l_x__ = ((l_i__ << 1) - 1) * l_lag__ + 1;
	    draw_node(&c__3, &c__5, &l_mxind__, &l_x__, &l_y__, &w_grid__[1]
		    );
	}
	l_x__ = l_mxind__;
	for (l_j__ = (int) ldexp(1.0, l_level__); l_j__ >= 1; --l_j__) {
	    l_y__ = ((l_j__ << 1) - 1) * l_lag__ + 1;
	    draw_node(&c__4, &c__5, &l_mxind__, &l_x__, &l_y__, &w_grid__[1]
		    );
	}
	l_y__ = 1;
	for (l_i__ = (int) ldexp(1.0, l_level__); l_i__ >= 1; --l_i__) {
	    l_x__ = ((l_i__ << 1) - 1) * l_lag__ + 1;
	    draw_node(&c__5, &c__5, &l_mxind__, &l_x__, &l_y__, &w_grid__[1]
		    );
	}
    }
    i__1 = *i_ny__;
    for (l_y__ = 1; l_y__ <= i__1; ++l_y__) {
	i__2 = *i_nx__;
	for (l_x__ = 1; l_x__ <= i__2; ++l_x__) {
	    l_i__ = l_x__ + (l_y__ - 1) * l_mxind__;
	    o_grid__[l_x__ + l_y__ * o_grid_dim1] = w_grid__[l_i__];
	}
    }

    grid = o_grid__;
    grid += o_grid_offset;
    if(checkSimulatedVariance(grid,(*i_nx__),(*i_ny__))){
      moduleError(KERNEL,"draw2d_ss_2o",
		  "%s\n%s",
		  "Numerical problems in simulation of gaussian field.",
		  "Maybe too high correlation between neighbour nodes.");
    }

    return  ;
} /* draw2d_ss_2o */

void SimGaussField2D::draw2d_ss_3s(int *i_dx__,
				   int *i_nx__,
				   int *i_ny__,
				   float *o_grid__,
				   double *w_grid__)
{
    /* System generated locals */
    int o_grid_dim1, o_grid_offset, i__1, i__2, i__3;

    /* Builtin functions */


    /* Local variables */
    static int l_lag__, l_dyaddim__;
    static int l_i__, l_j__, l_x__, l_y__, l_level__, l_mxind__;
    float *grid;

    assert(i_dx__);
    assert(i_nx__);
    assert(i_ny__);
    assert(o_grid__);
    assert(w_grid__);

    /* Parameter adjustments */
    --w_grid__;
    o_grid_dim1 = *i_dx__;
    o_grid_offset = o_grid_dim1 + 1;
    o_grid__ -= o_grid_offset;

    /* Function Body */
    if (*i_nx__ * *i_ny__ <= 1) {
      moduleError(KERNEL,"draw2d_ss_3s",
		  "Illegal definition of grid size");
    }
    l_dyaddim__ = (int)
	(log(MAXIM(*i_nx__,*i_ny__) - (double)1.) / log((double)2.) + (
	    double).9999);
    l_mxind__ = (int) ldexp(1.0, l_dyaddim__) + 1;
    l_lag__ = (int) ldexp(1.0, l_dyaddim__);

/* --------DRAW THE CORNERS AND  TWO LEVELS BY MATRIX INVERSION------ */
    init_c_patt();
    inits_grid( &l_mxind__, &w_grid__[1]);
/*--------DRAW THE REST OF THE NODES IN A FRACTAL FASHION----------------
-----*/
    i__1 = l_dyaddim__ - 1;
    for (l_level__ = 2; l_level__ <= i__1; ++l_level__) {
	i__2 = l_dyaddim__ - l_level__ - 1;
	l_lag__ = (int) ldexp(1.0, i__2);
/* ----------------------DRAW THE CENTER NODES OF THE SQUARES WITH COR
NERS */
/*                      DEFINED BY THE NODES OF THE PREVIOUS LEVEL */
	make_patt(&c__1, &l_lag__, &c__1, &c_n1, &c_n1);
	make_patt(&c__1, &l_lag__, &c__2, &c_n1, &c__1);
	make_patt(&c__1, &l_lag__, &c__3, &c__1, &c_n1);
	make_patt(&c__1, &l_lag__, &c__4, &c__1, &c__1);
	make_patt(&c__1, &l_lag__, &c__5, &c__3, &c__3);
	make_patt(&c__2, &l_lag__, &c__1, &c_n1, &c_n1);
	make_patt(&c__2, &l_lag__, &c__2, &c_n1, &c__1);
	make_patt(&c__2, &l_lag__, &c__3, &c__1, &c_n1);
	make_patt(&c__2, &l_lag__, &c__4, &c__1, &c__1);
	make_patt(&c__2, &l_lag__, &c__5, &c_n2, &c__0);
	make_patt(&c__2, &l_lag__, &c__6, &c_n3, &c__3);
	make_patt(&c__2, &l_lag__, &c__7, &c__3, &c__3);
	make_patt(&c__3, &l_lag__, &c__1, &c_n1, &c_n1);
	make_patt(&c__3, &l_lag__, &c__2, &c_n1, &c__1);
	make_patt(&c__3, &l_lag__, &c__3, &c__1, &c_n1);
	make_patt(&c__3, &l_lag__, &c__4, &c__1, &c__1);
	make_patt(&c__3, &l_lag__, &c__5, &c_n2, &c__0);
	make_patt(&c__3, &l_lag__, &c__6, &c_n3, &c__3);
	make_patt(&c__3, &l_lag__, &c__7, &c__3, &c__3);
	make_patt(&c__3, &l_lag__, &c__8, &c_n4, &c__0);
	make_patt(&c__4, &l_lag__, &c__1, &c_n1, &c_n1);
	make_patt(&c__4, &l_lag__, &c__2, &c_n1, &c__1);
	make_patt(&c__4, &l_lag__, &c__3, &c__1, &c_n1);
	make_patt(&c__4, &l_lag__, &c__4, &c__1, &c__1);
	make_patt(&c__4, &l_lag__, &c__5, &c_n2, &c__0);
	make_patt(&c__4, &l_lag__, &c__6, &c_n3, &c__3);
	make_patt(&c__4, &l_lag__, &c__7, &c_n4, &c__0);
	make_patt(&c__5, &l_lag__, &c__1, &c_n1, &c_n1);
	make_patt(&c__5, &l_lag__, &c__2, &c_n1, &c__1);
	make_patt(&c__5, &l_lag__, &c__3, &c__1, &c_n1);
	make_patt(&c__5, &l_lag__, &c__4, &c__1, &c__1);
	make_patt(&c__5, &l_lag__, &c__5, &c__0, &c_n2);
	make_patt(&c__5, &l_lag__, &c__6, &c__2, &c_n2);
	make_patt(&c__5, &l_lag__, &c__7, &c__3, &c__3);
	make_patt(&c__6, &l_lag__, &c__1, &c_n1, &c_n1);
	make_patt(&c__6, &l_lag__, &c__2, &c_n1, &c__1);
	make_patt(&c__6, &l_lag__, &c__3, &c__1, &c_n1);
	make_patt(&c__6, &l_lag__, &c__4, &c__1, &c__1);
	make_patt(&c__6, &l_lag__, &c__5, &c__0, &c_n2);
	make_patt(&c__6, &l_lag__, &c__6, &c__2, &c_n2);
	make_patt(&c__6, &l_lag__, &c__7, &c__3, &c__3);
	make_patt(&c__6, &l_lag__, &c__8, &c_n2, &c_n2);
	make_patt(&c__6, &l_lag__, &c__9, &c_n2, &c__0);
	make_patt(&c__6, &l_lag__, &c__10, &c_n3, &c__3);
	make_patt(&c__7, &l_lag__, &c__1, &c_n1, &c_n1);
	make_patt(&c__7, &l_lag__, &c__2, &c_n1, &c__1);
	make_patt(&c__7, &l_lag__, &c__3, &c__1, &c_n1);
	make_patt(&c__7, &l_lag__, &c__4, &c__1, &c__1);
	make_patt(&c__7, &l_lag__, &c__5, &c__0, &c_n2);
	make_patt(&c__7, &l_lag__, &c__6, &c__2, &c_n2);
	make_patt(&c__7, &l_lag__, &c__7, &c__3, &c__3);
	make_patt(&c__7, &l_lag__, &c__8, &c_n2, &c_n2);
	make_patt(&c__7, &l_lag__, &c__9, &c_n2, &c__0);
	make_patt(&c__7, &l_lag__, &c__10, &c_n4, &c__0);
	make_patt(&c__7, &l_lag__, &c__11, &c_n3, &c__3);
	make_patt(&c__8, &l_lag__, &c__1, &c_n1, &c_n1);
	make_patt(&c__8, &l_lag__, &c__2, &c_n1, &c__1);
	make_patt(&c__8, &l_lag__, &c__3, &c__1, &c_n1);
	make_patt(&c__8, &l_lag__, &c__4, &c__1, &c__1);
	make_patt(&c__8, &l_lag__, &c__5, &c__0, &c_n2);
	make_patt(&c__8, &l_lag__, &c__6, &c_n2, &c_n2);
	make_patt(&c__8, &l_lag__, &c__7, &c_n2, &c__0);
	make_patt(&c__8, &l_lag__, &c__8, &c_n4, &c__0);
	make_patt(&c__8, &l_lag__, &c__9, &c_n3, &c__3);
	make_patt(&c__9, &l_lag__, &c__1, &c_n1, &c_n1);
	make_patt(&c__9, &l_lag__, &c__2, &c_n1, &c__1);
	make_patt(&c__9, &l_lag__, &c__3, &c__1, &c_n1);
	make_patt(&c__9, &l_lag__, &c__4, &c__1, &c__1);
	make_patt(&c__9, &l_lag__, &c__5, &c__0, &c_n2);
	make_patt(&c__9, &l_lag__, &c__6, &c__0, &c_n4);
	make_patt(&c__9, &l_lag__, &c__7, &c__2, &c_n2);
	make_patt(&c__9, &l_lag__, &c__8, &c__3, &c__3);
	make_patt(&c__10, &l_lag__, &c__1, &c_n1, &c_n1);
	make_patt(&c__10, &l_lag__, &c__2, &c_n1, &c__1);
	make_patt(&c__10, &l_lag__, &c__3, &c__1, &c_n1);
	make_patt(&c__10, &l_lag__, &c__4, &c__1, &c__1);
	make_patt(&c__10, &l_lag__, &c__5, &c__0, &c_n2);
	make_patt(&c__10, &l_lag__, &c__6, &c__0, &c_n4);
	make_patt(&c__10, &l_lag__, &c__7, &c__2, &c_n2);
	make_patt(&c__11, &l_lag__, &c__1, &c_n1, &c_n1);
	make_patt(&c__11, &l_lag__, &c__2, &c_n1, &c__1);
	make_patt(&c__11, &l_lag__, &c__3, &c__1, &c_n1);
	make_patt(&c__11, &l_lag__, &c__4, &c__1, &c__1);
	make_patt(&c__11, &l_lag__, &c__5, &c__0, &c_n2);
	make_patt(&c__11, &l_lag__, &c__6, &c__0, &c_n4);
	make_patt(&c__11, &l_lag__, &c__7, &c__2, &c_n2);
	make_patt(&c__11, &l_lag__, &c__8, &c__3, &c__3);
	make_patt(&c__11, &l_lag__, &c__9, &c_n2, &c_n2);
	make_patt(&c__11, &l_lag__, &c__10, &c_n2, &c__0);
	make_patt(&c__11, &l_lag__, &c__11, &c_n3, &c__3);
	make_patt(&c__12, &l_lag__, &c__1, &c_n1, &c_n1);
	make_patt(&c__12, &l_lag__, &c__2, &c_n1, &c__1);
	make_patt(&c__12, &l_lag__, &c__3, &c__1, &c_n1);
	make_patt(&c__12, &l_lag__, &c__4, &c__1, &c__1);
	make_patt(&c__12, &l_lag__, &c__5, &c__0, &c_n2);
	make_patt(&c__12, &l_lag__, &c__6, &c__0, &c_n4);
	make_patt(&c__12, &l_lag__, &c__7, &c__2, &c_n2);
	make_patt(&c__12, &l_lag__, &c__8, &c_n2, &c_n2);
	make_patt(&c__12, &l_lag__, &c__9, &c_n2, &c__0);
	make_patt(&c__13, &l_lag__, &c__1, &c_n1, &c_n1);
	make_patt(&c__13, &l_lag__, &c__2, &c_n1, &c__1);
	make_patt(&c__13, &l_lag__, &c__3, &c__1, &c_n1);
	make_patt(&c__13, &l_lag__, &c__4, &c__1, &c__1);
	make_patt(&c__13, &l_lag__, &c__5, &c__0, &c_n2);
	make_patt(&c__13, &l_lag__, &c__6, &c__0, &c_n4);
	make_patt(&c__13, &l_lag__, &c__7, &c__2, &c_n2);
	make_patt(&c__13, &l_lag__, &c__8, &c_n2, &c_n2);
	make_patt(&c__13, &l_lag__, &c__9, &c_n2, &c__0);
	make_patt(&c__13, &l_lag__, &c__10, &c_n4, &c__0);
	make_patt(&c__13, &l_lag__, &c__11, &c__3, &c__3);
	make_patt(&c__13, &l_lag__, &c__12, &c_n3, &c__3);
	make_patt(&c__14, &l_lag__, &c__1, &c_n1, &c_n1);
	make_patt(&c__14, &l_lag__, &c__2, &c_n1, &c__1);
	make_patt(&c__14, &l_lag__, &c__3, &c__1, &c_n1);
	make_patt(&c__14, &l_lag__, &c__4, &c__1, &c__1);
	make_patt(&c__14, &l_lag__, &c__5, &c__0, &c_n2);
	make_patt(&c__14, &l_lag__, &c__6, &c__0, &c_n4);
	make_patt(&c__14, &l_lag__, &c__7, &c_n2, &c_n2);
	make_patt(&c__14, &l_lag__, &c__8, &c_n2, &c__0);
	make_patt(&c__14, &l_lag__, &c__9, &c_n4, &c__0);
	make_patt(&c__14, &l_lag__, &c__10, &c_n3, &c__3);
	make_patt(&c__15, &l_lag__, &c__1, &c_n1, &c_n1);
	make_patt(&c__15, &l_lag__, &c__2, &c_n1, &c__1);
	make_patt(&c__15, &l_lag__, &c__3, &c__1, &c_n1);
	make_patt(&c__15, &l_lag__, &c__4, &c__1, &c__1);
	make_patt(&c__15, &l_lag__, &c__5, &c__0, &c_n2);
	make_patt(&c__15, &l_lag__, &c__6, &c__0, &c_n4);
	make_patt(&c__15, &l_lag__, &c__7, &c_n2, &c_n2);
	make_patt(&c__15, &l_lag__, &c__8, &c_n2, &c__0);
	make_patt(&c__15, &l_lag__, &c__9, &c_n4, &c__0);
	make_patt(&c__15, &l_lag__, &c__10, &c__2, &c_n2);
	make_patt(&c__16, &l_lag__, &c__1, &c_n1, &c_n1);
	make_patt(&c__16, &l_lag__, &c__2, &c_n1, &c__1);
	make_patt(&c__16, &l_lag__, &c__3, &c__1, &c_n1);
	make_patt(&c__16, &l_lag__, &c__4, &c__1, &c__1);
	make_patt(&c__16, &l_lag__, &c__5, &c__0, &c_n2);
	make_patt(&c__16, &l_lag__, &c__6, &c__0, &c_n4);
	make_patt(&c__16, &l_lag__, &c__7, &c_n2, &c_n2);
	make_patt(&c__16, &l_lag__, &c__8, &c_n2, &c__0);
	make_patt(&c__16, &l_lag__, &c__9, &c_n4, &c__0);
	init_weights_s(&c__1,  &c__5);
	init_weights_s(&c__2,  &c__7);
	init_weights_s(&c__3,  &c__8);
	init_weights_s(&c__4,  &c__7);
	init_weights_s(&c__5,  &c__7);
	init_weights_s(&c__6,  &c__10);
	init_weights_s(&c__7,  &c__11);
	init_weights_s(&c__8,  &c__9);
	init_weights_s(&c__9,  &c__8);
	init_weights_s(&c__10,  &c__7);
	init_weights_s(&c__11,  &c__11);
	init_weights_s(&c__12,  &c__9);
	init_weights_s(&c__13,  &c__12);
	init_weights_s(&c__14,  &c__10);
	init_weights_s(&c__15,  &c__10);
	init_weights_s(&c__16,  &c__9);
/* ---------------------FIRST LINE */
	l_y__ = l_lag__ + 1;
	l_x__ = l_lag__ + 1;
	draw_node(&c__1, &c__5, &l_mxind__, &l_x__, &l_y__, &w_grid__[1]);
	l_x__ = l_lag__ * 3 + 1;
	draw_node(&c__2, &c__7, &l_mxind__, &l_x__, &l_y__, &w_grid__[1]);
	i__2 = (int) ldexp(1.0, l_level__) - 1;
	for (l_i__ = 3; l_i__ <= i__2; ++l_i__) {
	    l_x__ = ((l_i__ << 1) - 1) * l_lag__ + 1;
	    draw_node(&c__3, &c__8, &l_mxind__, &l_x__, &l_y__, &w_grid__[1]
		    );
	}
	l_x__ = l_mxind__ - l_lag__;
	draw_node(&c__4, &c__7, &l_mxind__, &l_x__, &l_y__, &w_grid__[1]);
/* ---------------------SECOND LINE */
	l_y__ = l_lag__ * 3 + 1;
	l_x__ = l_lag__ + 1;
	draw_node(&c__5, &c__7, &l_mxind__, &l_x__, &l_y__, &w_grid__[1]);
	l_x__ = l_lag__ * 3 + 1;
	draw_node(&c__6, &c__10, &l_mxind__, &l_x__, &l_y__, &w_grid__[1]);
	i__2 = (int) ldexp(1.0, l_level__) - 1;
	for (l_i__ = 3; l_i__ <= i__2; ++l_i__) {
	    l_x__ = ((l_i__ << 1) - 1) * l_lag__ + 1;
	    draw_node(&c__7, &c__11, &l_mxind__, &l_x__, &l_y__, &w_grid__[
		    1]);
	}
	l_x__ = l_mxind__ - l_lag__;
	draw_node(&c__8, &c__9, &l_mxind__, &l_x__, &l_y__, &w_grid__[1]);
/* ---------------------FIRST COLUMN */
	l_x__ = l_lag__ + 1;
	i__2 = (int) ldexp(1.0, l_level__) - 1;
	for (l_j__ = 3; l_j__ <= i__2; ++l_j__) {
	    l_y__ = ((l_j__ << 1) - 1) * l_lag__ + 1;
	    draw_node(&c__9, &c__8, &l_mxind__, &l_x__, &l_y__, &w_grid__[1]
		    );
	}
	l_y__ = l_mxind__ - l_lag__;
	draw_node(&c__10, &c__7, &l_mxind__, &l_x__, &l_y__, &w_grid__[1]);
/* ---------------------SECOND COLUMN */
	l_x__ = l_lag__ * 3 + 1;
	i__2 = (int) ldexp(1.0, l_level__) - 1;
	for (l_j__ = 3; l_j__ <= i__2; ++l_j__) {
	    l_y__ = ((l_j__ << 1) - 1) * l_lag__ + 1;
	    draw_node(&c__11, &c__11, &l_mxind__, &l_x__, &l_y__, &w_grid__[
		    1]);
	}
	l_y__ = l_mxind__ - l_lag__;
	draw_node(&c__12, &c__9, &l_mxind__, &l_x__, &l_y__, &w_grid__[1]);
/* ---------------------INTERIOR NODES */
	i__2 = (int) ldexp(1.0, l_level__) - 1;
	for (l_j__ = 3; l_j__ <= i__2; ++l_j__) {
	    l_y__ = ((l_j__ << 1) - 1) * l_lag__ + 1;
	    i__3 = (int) ldexp(1.0, l_level__) - 1;
	    for (l_i__ = 3; l_i__ <= i__3; ++l_i__) {
		l_x__ = ((l_i__ << 1) - 1) * l_lag__ + 1;
		draw_node(&c__13, &c__12, &l_mxind__, &l_x__, &l_y__, &
			w_grid__[1]);
	    }
/*                     LAST COLUMN */
	    l_x__ = l_mxind__ - l_lag__;
	    draw_node(&c__14, &c__10, &l_mxind__, &l_x__, &l_y__, &w_grid__[
		    1]);
	}
/* ---------------------LAST LINE */
	l_y__ = l_mxind__ - l_lag__;
	i__2 = (int) ldexp(1.0, l_level__) - 1;
	for (l_i__ = 3; l_i__ <= i__2; ++l_i__) {
	    l_x__ = ((l_i__ << 1) - 1) * l_lag__ + 1;
	    draw_node(&c__15, &c__10, &l_mxind__, &l_x__, &l_y__, &w_grid__[
		    1]);
	}
	l_x__ = l_mxind__ - l_lag__;
	draw_node(&c__16, &c__9, &l_mxind__, &l_x__, &l_y__, &w_grid__[1]);
/*----------------------DRAW THE CENTER NODES OF THE TILTED SQUARES WI
TH CORNERS*/
/*                     DEFINED BY THE NODES OF THIS AND THE THE PREVIO
US LEVEL*/
	make_patt(&c__1, &l_lag__, &c__1, &c__0, &c_n1);
	make_patt(&c__1, &l_lag__, &c__2, &c__0, &c__1);
	make_patt(&c__1, &l_lag__, &c__3, &c_n1, &c__0);
	make_patt(&c__1, &l_lag__, &c__4, &c__1, &c__0);
	make_patt(&c__1, &l_lag__, &c__5, &c__3, &c__0);
	make_patt(&c__1, &l_lag__, &c__6, &c__0, &c__3);
	make_patt(&c__2, &l_lag__, &c__1, &c__0, &c_n1);
	make_patt(&c__2, &l_lag__, &c__2, &c__0, &c__1);
	make_patt(&c__2, &l_lag__, &c__3, &c_n1, &c__0);
	make_patt(&c__2, &l_lag__, &c__4, &c__1, &c__0);
	make_patt(&c__2, &l_lag__, &c__5, &c__3, &c__0);
	make_patt(&c__2, &l_lag__, &c__6, &c__0, &c__3);
	make_patt(&c__2, &l_lag__, &c__7, &c_n2, &c__0);
	make_patt(&c__3, &l_lag__, &c__1, &c__0, &c_n1);
	make_patt(&c__3, &l_lag__, &c__2, &c__0, &c__1);
	make_patt(&c__3, &l_lag__, &c__3, &c_n1, &c__0);
	make_patt(&c__3, &l_lag__, &c__4, &c__1, &c__0);
	make_patt(&c__3, &l_lag__, &c__5, &c__0, &c__3);
	make_patt(&c__3, &l_lag__, &c__6, &c__2, &c__0);
	make_patt(&c__4, &l_lag__, &c__1, &c__0, &c_n1);
	make_patt(&c__4, &l_lag__, &c__2, &c__0, &c__1);
	make_patt(&c__4, &l_lag__, &c__3, &c_n1, &c__0);
	make_patt(&c__4, &l_lag__, &c__4, &c__1, &c__0);
	make_patt(&c__4, &l_lag__, &c__5, &c__0, &c__3);
	make_patt(&c__4, &l_lag__, &c__6, &c__3, &c__0);
	make_patt(&c__4, &l_lag__, &c__7, &c__1, &c_n1);
	make_patt(&c__5, &l_lag__, &c__1, &c__0, &c_n1);
	make_patt(&c__5, &l_lag__, &c__2, &c__0, &c__1);
	make_patt(&c__5, &l_lag__, &c__3, &c_n1, &c__0);
	make_patt(&c__5, &l_lag__, &c__4, &c__1, &c__0);
	make_patt(&c__5, &l_lag__, &c__5, &c__0, &c__3);
	make_patt(&c__5, &l_lag__, &c__6, &c__3, &c__0);
	make_patt(&c__5, &l_lag__, &c__7, &c__1, &c_n1);
	make_patt(&c__5, &l_lag__, &c__8, &c_n1, &c_n1);
	make_patt(&c__5, &l_lag__, &c__9, &c_n2, &c__0);
	make_patt(&c__6, &l_lag__, &c__1, &c__0, &c_n1);
	make_patt(&c__6, &l_lag__, &c__2, &c__0, &c__1);
	make_patt(&c__6, &l_lag__, &c__3, &c_n1, &c__0);
	make_patt(&c__6, &l_lag__, &c__4, &c__1, &c__0);
	make_patt(&c__6, &l_lag__, &c__5, &c__0, &c__3);
	make_patt(&c__6, &l_lag__, &c__6, &c_n1, &c_n1);
	make_patt(&c__6, &l_lag__, &c__7, &c_n2, &c__0);
	make_patt(&c__7, &l_lag__, &c__1, &c__0, &c_n1);
	make_patt(&c__7, &l_lag__, &c__2, &c__0, &c__1);
	make_patt(&c__7, &l_lag__, &c__3, &c_n1, &c__0);
	make_patt(&c__7, &l_lag__, &c__4, &c__1, &c__0);
	make_patt(&c__7, &l_lag__, &c__5, &c__0, &c__3);
	make_patt(&c__7, &l_lag__, &c__6, &c__1, &c_n1);
	make_patt(&c__7, &l_lag__, &c__7, &c_n1, &c_n1);
	make_patt(&c__7, &l_lag__, &c__8, &c__0, &c_n2);
	make_patt(&c__7, &l_lag__, &c__9, &c__2, &c_n2);
	make_patt(&c__7, &l_lag__, &c__10, &c__3, &c__0);
	make_patt(&c__8, &l_lag__, &c__1, &c__0, &c_n1);
	make_patt(&c__8, &l_lag__, &c__2, &c__0, &c__1);
	make_patt(&c__8, &l_lag__, &c__3, &c_n1, &c__0);
	make_patt(&c__8, &l_lag__, &c__4, &c__1, &c__0);
	make_patt(&c__8, &l_lag__, &c__5, &c__0, &c__3);
	make_patt(&c__8, &l_lag__, &c__6, &c__1, &c_n1);
	make_patt(&c__8, &l_lag__, &c__7, &c_n1, &c_n1);
	make_patt(&c__8, &l_lag__, &c__8, &c_n2, &c__0);
	make_patt(&c__8, &l_lag__, &c__9, &c__3, &c__0);
	make_patt(&c__8, &l_lag__, &c__10, &c_n2, &c_n2);
	make_patt(&c__8, &l_lag__, &c__11, &c__0, &c_n2);
	make_patt(&c__8, &l_lag__, &c__12, &c__2, &c_n2);
	make_patt(&c__9, &l_lag__, &c__1, &c__0, &c_n1);
	make_patt(&c__9, &l_lag__, &c__2, &c__0, &c__1);
	make_patt(&c__9, &l_lag__, &c__3, &c_n1, &c__0);
	make_patt(&c__9, &l_lag__, &c__4, &c__1, &c__0);
	make_patt(&c__9, &l_lag__, &c__5, &c__0, &c__3);
	make_patt(&c__9, &l_lag__, &c__6, &c__1, &c_n1);
	make_patt(&c__9, &l_lag__, &c__7, &c_n1, &c_n1);
	make_patt(&c__9, &l_lag__, &c__8, &c_n2, &c__0);
	make_patt(&c__9, &l_lag__, &c__9, &c_n2, &c_n2);
	make_patt(&c__9, &l_lag__, &c__10, &c__0, &c_n2);
	make_patt(&c__10, &l_lag__, &c__1, &c__0, &c_n1);
	make_patt(&c__10, &l_lag__, &c__2, &c__0, &c__1);
	make_patt(&c__10, &l_lag__, &c__3, &c_n1, &c__0);
	make_patt(&c__10, &l_lag__, &c__4, &c__1, &c__0);
	make_patt(&c__10, &l_lag__, &c__5, &c__0, &c__3);
	make_patt(&c__10, &l_lag__, &c__6, &c__1, &c_n1);
	make_patt(&c__10, &l_lag__, &c__7, &c__0, &c_n2);
	make_patt(&c__10, &l_lag__, &c__8, &c__2, &c_n2);
	make_patt(&c__10, &l_lag__, &c__9, &c__3, &c__0);
	make_patt(&c__11, &l_lag__, &c__1, &c__0, &c_n1);
	make_patt(&c__11, &l_lag__, &c__2, &c__0, &c__1);
	make_patt(&c__11, &l_lag__, &c__3, &c_n1, &c__0);
	make_patt(&c__11, &l_lag__, &c__4, &c__1, &c__0);
	make_patt(&c__11, &l_lag__, &c__5, &c__0, &c__3);
	make_patt(&c__11, &l_lag__, &c__6, &c_n1, &c_n1);
	make_patt(&c__11, &l_lag__, &c__7, &c_n2, &c__0);
	make_patt(&c__11, &l_lag__, &c__8, &c_n2, &c_n2);
	make_patt(&c__11, &l_lag__, &c__9, &c__0, &c_n2);
	make_patt(&c__12, &l_lag__, &c__1, &c__0, &c_n1);
	make_patt(&c__12, &l_lag__, &c__2, &c__0, &c__1);
	make_patt(&c__12, &l_lag__, &c__3, &c_n1, &c__0);
	make_patt(&c__12, &l_lag__, &c__4, &c__1, &c__0);
	make_patt(&c__12, &l_lag__, &c__5, &c__1, &c_n1);
	make_patt(&c__12, &l_lag__, &c__6, &c__0, &c_n2);
	make_patt(&c__12, &l_lag__, &c__7, &c__2, &c_n2);
	make_patt(&c__12, &l_lag__, &c__8, &c__3, &c__0);
	make_patt(&c__13, &l_lag__, &c__1, &c__0, &c_n1);
	make_patt(&c__13, &l_lag__, &c__2, &c__0, &c__1);
	make_patt(&c__13, &l_lag__, &c__3, &c_n1, &c__0);
	make_patt(&c__13, &l_lag__, &c__4, &c__1, &c__0);
	make_patt(&c__13, &l_lag__, &c__5, &c__1, &c_n1);
	make_patt(&c__13, &l_lag__, &c__6, &c_n1, &c_n1);
	make_patt(&c__13, &l_lag__, &c__7, &c_n2, &c__0);
	make_patt(&c__13, &l_lag__, &c__8, &c__3, &c__0);
	make_patt(&c__13, &l_lag__, &c__9, &c_n2, &c_n2);
	make_patt(&c__13, &l_lag__, &c__10, &c__0, &c_n2);
	make_patt(&c__13, &l_lag__, &c__11, &c__2, &c_n2);
	make_patt(&c__14, &l_lag__, &c__1, &c__0, &c_n1);
	make_patt(&c__14, &l_lag__, &c__2, &c__0, &c__1);
	make_patt(&c__14, &l_lag__, &c__3, &c_n1, &c__0);
	make_patt(&c__14, &l_lag__, &c__4, &c__1, &c__0);
	make_patt(&c__14, &l_lag__, &c__5, &c_n1, &c_n1);
	make_patt(&c__14, &l_lag__, &c__6, &c_n2, &c__0);
	make_patt(&c__14, &l_lag__, &c__7, &c_n2, &c_n2);
	make_patt(&c__14, &l_lag__, &c__8, &c__0, &c_n2);
	make_patt(&c__15, &l_lag__, &c__1, &c__0, &c_n1);
	make_patt(&c__15, &l_lag__, &c__2, &c__0, &c__1);
	make_patt(&c__15, &l_lag__, &c__3, &c_n1, &c__0);
	make_patt(&c__15, &l_lag__, &c__4, &c__1, &c__0);
	make_patt(&c__15, &l_lag__, &c__5, &c__1, &c_n1);
	make_patt(&c__15, &l_lag__, &c__6, &c_n1, &c_n1);
	make_patt(&c__15, &l_lag__, &c__7, &c__0, &c_n2);
	make_patt(&c__15, &l_lag__, &c__8, &c__2, &c_n2);
	make_patt(&c__16, &l_lag__, &c__1, &c__0, &c_n1);
	make_patt(&c__16, &l_lag__, &c__2, &c__0, &c__1);
	make_patt(&c__16, &l_lag__, &c__3, &c_n1, &c__0);
	make_patt(&c__16, &l_lag__, &c__4, &c__1, &c__0);
	make_patt(&c__16, &l_lag__, &c__5, &c__1, &c_n1);
	make_patt(&c__16, &l_lag__, &c__6, &c_n1, &c_n1);
	make_patt(&c__16, &l_lag__, &c__7, &c_n2, &c__0);
	make_patt(&c__16, &l_lag__, &c__8, &c_n2, &c_n2);
	make_patt(&c__16, &l_lag__, &c__9, &c__0, &c_n2);
	init_weights_s(&c__1,  &c__6);
	init_weights_s(&c__2,  &c__7);
	init_weights_s(&c__3,  &c__6);
	init_weights_s(&c__4,  &c__7);
	init_weights_s(&c__5,  &c__9);
	init_weights_s(&c__6,  &c__7);
	init_weights_s(&c__7,  &c__10);
	init_weights_s(&c__8,  &c__12);
	init_weights_s(&c__9,  &c__10);
	init_weights_s(&c__10,  &c__9);
	init_weights_s(&c__11,  &c__9);
	init_weights_s(&c__12,  &c__8);
	init_weights_s(&c__13,  &c__11);
	init_weights_s(&c__14,  &c__8);
	init_weights_s(&c__15,  &c__8);
	init_weights_s(&c__16,  &c__9);
	l_x__ = (l_lag__ << 1) + 1;
	l_y__ = l_lag__ + 1;
	draw_node(&c__1, &c__6, &l_mxind__, &l_x__, &l_y__, &w_grid__[1]);
	i__2 = (int) ldexp(1.0, l_level__) - 2;
	for (l_i__ = 2; l_i__ <= i__2; ++l_i__) {
	    l_x__ = (l_i__ << 1) * l_lag__ + 1;
	    draw_node(&c__2, &c__7, &l_mxind__, &l_x__, &l_y__, &w_grid__[1]
		    );
	}
	l_x__ = l_mxind__ - (l_lag__ << 1);
	draw_node(&c__3, &c__6, &l_mxind__, &l_x__, &l_y__, &w_grid__[1]);
	l_x__ = l_lag__ + 1;
	l_y__ = (l_lag__ << 1) + 1;
	draw_node(&c__4, &c__7, &l_mxind__, &l_x__, &l_y__, &w_grid__[1]);
	i__2 = (int) ldexp(1.0, l_level__) - 1;
	for (l_i__ = 2; l_i__ <= i__2; ++l_i__) {
	    l_x__ = ((l_i__ << 1) - 1) * l_lag__ + 1;
	    draw_node(&c__5, &c__9, &l_mxind__, &l_x__, &l_y__, &w_grid__[1]
		    );
	}
	l_x__ = l_mxind__ - l_lag__;
	draw_node(&c__6, &c__7, &l_mxind__, &l_x__, &l_y__, &w_grid__[1]);
	i__2 = (int) ldexp(1.0, l_level__) - 1;
	for (l_j__ = 2; l_j__ <= i__2; ++l_j__) {
	    l_x__ = (l_lag__ << 1) + 1;
	    l_y__ = ((l_j__ << 1) - 1) * l_lag__ + 1;
	    draw_node(&c__7, &c__10, &l_mxind__, &l_x__, &l_y__, &w_grid__[
		    1]);
	    i__3 = (int) ldexp(1.0, l_level__) - 2;
	    for (l_i__ = 2; l_i__ <= i__3; ++l_i__) {
		l_x__ = (l_i__ << 1) * l_lag__ + 1;
		draw_node(&c__8, &c__12, &l_mxind__, &l_x__, &l_y__, &
			w_grid__[1]);
	    }
	    l_x__ = l_mxind__ - (l_lag__ << 1);
	    draw_node(&c__9, &c__10, &l_mxind__, &l_x__, &l_y__, &w_grid__[
		    1]);
	    if (l_j__ < (int) ldexp(1.0, l_level__) - 1) {
		l_x__ = l_lag__ + 1;
		l_y__ = (l_j__ << 1) * l_lag__ + 1;
		draw_node(&c__10, &c__9, &l_mxind__, &l_x__, &l_y__, &
			w_grid__[1]);
		i__3 = (int) ldexp(1.0, l_level__) - 1;
		for (l_i__ = 2; l_i__ <= i__3; ++l_i__) {
		    l_x__ = ((l_i__ << 1) - 1) * l_lag__ + 1;
		    draw_node(&c__8, &c__12, &l_mxind__, &l_x__, &l_y__, &
			    w_grid__[1]);
		}
		l_x__ = l_mxind__ - l_lag__;
		draw_node(&c__11, &c__9, &l_mxind__, &l_x__, &l_y__, &
			w_grid__[1]);
	    }
	}
	l_x__ = l_lag__ + 1;
	l_y__ = l_mxind__ - (l_lag__ << 1);
	draw_node(&c__12, &c__8, &l_mxind__, &l_x__, &l_y__, &w_grid__[1]);
	i__2 = (int) ldexp(1.0, l_level__) - 1;
	for (l_i__ = 2; l_i__ <= i__2; ++l_i__) {
	    l_x__ = ((l_i__ << 1) - 1) * l_lag__ + 1;
	    draw_node(&c__13, &c__11, &l_mxind__, &l_x__, &l_y__, &w_grid__[
		    1]);
	}
	l_x__ = l_mxind__ - l_lag__;
	draw_node(&c__14, &c__8, &l_mxind__, &l_x__, &l_y__, &w_grid__[1]);
	l_x__ = (l_lag__ << 1) + 1;
	l_y__ = l_mxind__ - l_lag__;
	draw_node(&c__15, &c__8, &l_mxind__, &l_x__, &l_y__, &w_grid__[1]);
	i__2 = (int) ldexp(1.0, l_level__) - 2;
	for (l_i__ = 2; l_i__ <= i__2; ++l_i__) {
	    l_x__ = (l_i__ << 1) * l_lag__ + 1;
	    draw_node(&c__13, &c__11, &l_mxind__, &l_x__, &l_y__, &w_grid__[
		    1]);
	}
	l_x__ = l_mxind__ - (l_lag__ << 1);
	draw_node(&c__16, &c__9, &l_mxind__, &l_x__, &l_y__, &w_grid__[1]);
/* ----------------------DRAW THE BOARDER NODES ON THE FOUR EDGES */

	make_patt(&c__1, &l_lag__, &c__1, &c__0, &c_n1);
	make_patt(&c__1, &l_lag__, &c__2, &c__0, &c__1);
	make_patt(&c__1, &l_lag__, &c__3, &c__1, &c__0);
	make_patt(&c__1, &l_lag__, &c__4, &c__1, &c__1);
	make_patt(&c__1, &l_lag__, &c__5, &c__2, &c__0);
	make_patt(&c__1, &l_lag__, &c__6, &c__2, &c__2);
	make_patt(&c__1, &l_lag__, &c__7, &c__0, &c__3);
	make_patt(&c__2, &l_lag__, &c__1, &c__0, &c_n1);
	make_patt(&c__2, &l_lag__, &c__2, &c__0, &c__1);
	make_patt(&c__2, &l_lag__, &c__3, &c__1, &c__0);
	make_patt(&c__2, &l_lag__, &c__4, &c__1, &c__1);
	make_patt(&c__2, &l_lag__, &c__5, &c__2, &c__0);
	make_patt(&c__2, &l_lag__, &c__6, &c__2, &c__2);
	make_patt(&c__2, &l_lag__, &c__7, &c__0, &c__3);
	make_patt(&c__2, &l_lag__, &c__8, &c__1, &c_n1);
	make_patt(&c__2, &l_lag__, &c__9, &c__0, &c_n2);
	make_patt(&c__2, &l_lag__, &c__10, &c__2, &c_n2);
	make_patt(&c__3, &l_lag__, &c__1, &c__0, &c_n1);
	make_patt(&c__3, &l_lag__, &c__2, &c__0, &c__1);
	make_patt(&c__3, &l_lag__, &c__3, &c__1, &c__0);
	make_patt(&c__3, &l_lag__, &c__4, &c__2, &c__0);
	make_patt(&c__3, &l_lag__, &c__5, &c__1, &c_n1);
	make_patt(&c__3, &l_lag__, &c__6, &c__0, &c_n2);
	make_patt(&c__3, &l_lag__, &c__7, &c__2, &c_n2);
	make_patt(&c__4, &l_lag__, &c__1, &c_n1, &c__0);
	make_patt(&c__4, &l_lag__, &c__2, &c__1, &c__0);
	make_patt(&c__4, &l_lag__, &c__3, &c__0, &c_n1);
	make_patt(&c__4, &l_lag__, &c__4, &c_n1, &c_n1);
	make_patt(&c__4, &l_lag__, &c__5, &c__1, &c_n1);
	make_patt(&c__4, &l_lag__, &c__6, &c__0, &c_n2);
	make_patt(&c__4, &l_lag__, &c__7, &c__2, &c_n2);
	make_patt(&c__4, &l_lag__, &c__8, &c__3, &c__0);
	make_patt(&c__5, &l_lag__, &c__1, &c_n1, &c__0);
	make_patt(&c__5, &l_lag__, &c__2, &c__1, &c__0);
	make_patt(&c__5, &l_lag__, &c__3, &c__0, &c_n1);
	make_patt(&c__5, &l_lag__, &c__4, &c_n1, &c_n1);
	make_patt(&c__5, &l_lag__, &c__5, &c__1, &c_n1);
	make_patt(&c__5, &l_lag__, &c__6, &c__0, &c_n2);
	make_patt(&c__5, &l_lag__, &c__7, &c__2, &c_n2);
	make_patt(&c__5, &l_lag__, &c__8, &c__3, &c__0);
	make_patt(&c__5, &l_lag__, &c__9, &c_n2, &c__0);
	make_patt(&c__5, &l_lag__, &c__10, &c_n2, &c_n2);
	make_patt(&c__6, &l_lag__, &c__1, &c_n1, &c__0);
	make_patt(&c__6, &l_lag__, &c__2, &c__1, &c__0);
	make_patt(&c__6, &l_lag__, &c__3, &c__0, &c_n1);
	make_patt(&c__6, &l_lag__, &c__4, &c_n1, &c_n1);
	make_patt(&c__6, &l_lag__, &c__5, &c__0, &c_n2);
	make_patt(&c__6, &l_lag__, &c__6, &c_n2, &c__0);
	make_patt(&c__6, &l_lag__, &c__7, &c_n2, &c_n2);
	make_patt(&c__7, &l_lag__, &c__1, &c__0, &c__1);
	make_patt(&c__7, &l_lag__, &c__2, &c_n1, &c__1);
	make_patt(&c__7, &l_lag__, &c__3, &c_n1, &c__0);
	make_patt(&c__7, &l_lag__, &c__4, &c_n1, &c_n1);
	make_patt(&c__7, &l_lag__, &c__5, &c__0, &c_n1);
	make_patt(&c__7, &l_lag__, &c__6, &c_n2, &c__0);
	make_patt(&c__7, &l_lag__, &c__7, &c__0, &c_n3);
	make_patt(&c__7, &l_lag__, &c__8, &c_n2, &c_n2);
	make_patt(&c__8, &l_lag__, &c__1, &c__0, &c__1);
	make_patt(&c__8, &l_lag__, &c__2, &c_n1, &c__1);
	make_patt(&c__8, &l_lag__, &c__3, &c_n1, &c__0);
	make_patt(&c__8, &l_lag__, &c__4, &c_n1, &c_n1);
	make_patt(&c__8, &l_lag__, &c__5, &c__0, &c_n1);
	make_patt(&c__8, &l_lag__, &c__6, &c_n2, &c__0);
	make_patt(&c__8, &l_lag__, &c__7, &c__0, &c_n3);
	make_patt(&c__8, &l_lag__, &c__8, &c_n2, &c_n2);
	make_patt(&c__8, &l_lag__, &c__9, &c_n2, &c__2);
	make_patt(&c__8, &l_lag__, &c__10, &c__0, &c__2);
	make_patt(&c__9, &l_lag__, &c__1, &c__0, &c__1);
	make_patt(&c__9, &l_lag__, &c__2, &c_n1, &c__1);
	make_patt(&c__9, &l_lag__, &c__3, &c_n1, &c__0);
	make_patt(&c__9, &l_lag__, &c__4, &c__0, &c_n1);
	make_patt(&c__9, &l_lag__, &c__5, &c_n2, &c__0);
	make_patt(&c__9, &l_lag__, &c__6, &c_n2, &c__2);
	make_patt(&c__9, &l_lag__, &c__7, &c__0, &c__2);
	make_patt(&c__10, &l_lag__, &c__1, &c_n1, &c__0);
	make_patt(&c__10, &l_lag__, &c__2, &c__1, &c__0);
	make_patt(&c__10, &l_lag__, &c__3, &c_n1, &c__1);
	make_patt(&c__10, &l_lag__, &c__4, &c__0, &c__1);
	make_patt(&c__10, &l_lag__, &c__5, &c__1, &c__1);
	make_patt(&c__10, &l_lag__, &c__6, &c__0, &c__2);
	make_patt(&c__10, &l_lag__, &c__7, &c_n2, &c__2);
	make_patt(&c__10, &l_lag__, &c__8, &c_n3, &c__0);
	make_patt(&c__11, &l_lag__, &c__1, &c_n1, &c__0);
	make_patt(&c__11, &l_lag__, &c__2, &c__1, &c__0);
	make_patt(&c__11, &l_lag__, &c__3, &c_n1, &c__1);
	make_patt(&c__11, &l_lag__, &c__4, &c__0, &c__1);
	make_patt(&c__11, &l_lag__, &c__5, &c__1, &c__1);
	make_patt(&c__11, &l_lag__, &c__6, &c__0, &c__2);
	make_patt(&c__11, &l_lag__, &c__7, &c_n2, &c__2);
	make_patt(&c__11, &l_lag__, &c__8, &c_n3, &c__0);
	make_patt(&c__11, &l_lag__, &c__9, &c__2, &c__2);
	make_patt(&c__11, &l_lag__, &c__10, &c__2, &c__0);
	make_patt(&c__12, &l_lag__, &c__1, &c_n1, &c__0);
	make_patt(&c__12, &l_lag__, &c__2, &c__1, &c__0);
	make_patt(&c__12, &l_lag__, &c__3, &c_n1, &c__1);
	make_patt(&c__12, &l_lag__, &c__4, &c__0, &c__1);
	make_patt(&c__12, &l_lag__, &c__5, &c__1, &c__1);
	make_patt(&c__12, &l_lag__, &c__6, &c__0, &c__2);
	make_patt(&c__12, &l_lag__, &c__7, &c__2, &c__2);
	make_patt(&c__12, &l_lag__, &c__8, &c__2, &c__0);
	init_weights_s(&c__1,  &c__7);
	init_weights_s(&c__2,  &c__10);
	init_weights_s(&c__3,  &c__7);
	init_weights_s(&c__4,  &c__8);
	init_weights_s(&c__5,  &c__10);
	init_weights_s(&c__6,  &c__7);
	init_weights_s(&c__7,  &c__8);
	init_weights_s(&c__8,  &c__10);
	init_weights_s(&c__9,  &c__7);
	init_weights_s(&c__10,  &c__8);
	init_weights_s(&c__11,  &c__10);
	init_weights_s(&c__12,  &c__8);
	l_x__ = 1;
	l_y__ = l_lag__ + 1;
	draw_node(&c__1, &c__7, &l_mxind__, &l_x__, &l_y__, &w_grid__[1]);
	i__2 = (int) ldexp(1.0, l_level__) - 1;
	for (l_j__ = 2; l_j__ <= i__2; ++l_j__) {
	    l_y__ = ((l_j__ << 1) - 1) * l_lag__ + 1;
	    draw_node(&c__2, &c__10, &l_mxind__, &l_x__, &l_y__, &w_grid__[
		    1]);
	}
	l_y__ = l_mxind__ - l_lag__;
	draw_node(&c__3, &c__7, &l_mxind__, &l_x__, &l_y__, &w_grid__[1]);
	l_x__ = l_lag__ + 1;
	l_y__ = l_mxind__;
	draw_node(&c__4, &c__8, &l_mxind__, &l_x__, &l_y__, &w_grid__[1]);
	i__2 = (int) ldexp(1.0, l_level__) - 1;
	for (l_i__ = 2; l_i__ <= i__2; ++l_i__) {
	    l_x__ = ((l_i__ << 1) - 1) * l_lag__ + 1;
	    draw_node(&c__5, &c__10, &l_mxind__, &l_x__, &l_y__, &w_grid__[
		    1]);
	}
	l_x__ = l_mxind__ - l_lag__;
	draw_node(&c__6, &c__7, &l_mxind__, &l_x__, &l_y__, &w_grid__[1]);
	l_x__ = l_mxind__;
	l_y__ = l_mxind__ - l_lag__;
	draw_node(&c__7, &c__8, &l_mxind__, &l_x__, &l_y__, &w_grid__[1]);
	for (l_j__ = (int) ldexp(1.0, l_level__) - 1; l_j__ >= 2; --l_j__) {
	    l_y__ = ((l_j__ << 1) - 1) * l_lag__ + 1;
	    draw_node(&c__8, &c__10, &l_mxind__, &l_x__, &l_y__, &w_grid__[
		    1]);
	}
	l_y__ = l_lag__ + 1;
	draw_node(&c__9, &c__7, &l_mxind__, &l_x__, &l_y__, &w_grid__[1]);
	l_x__ = l_mxind__ - l_lag__;
	l_y__ = 1;
	draw_node(&c__10, &c__8, &l_mxind__, &l_x__, &l_y__, &w_grid__[1]);
	for (l_i__ = (int) ldexp(1.0, l_level__) - 1; l_i__ >= 2; --l_i__) {
	    l_x__ = ((l_i__ << 1) - 1) * l_lag__ + 1;
	    draw_node(&c__11, &c__10, &l_mxind__, &l_x__, &l_y__, &w_grid__[
		    1]);
	}
	l_x__ = l_lag__ + 1;
	draw_node(&c__12, &c__8, &l_mxind__, &l_x__, &l_y__, &w_grid__[1]);
    }
    i__1 = *i_ny__;
    for (l_y__ = 1; l_y__ <= i__1; ++l_y__) {
	i__2 = *i_nx__;
	for (l_x__ = 1; l_x__ <= i__2; ++l_x__) {
	    l_i__ = l_x__ + (l_y__ - 1) * l_mxind__;
	    o_grid__[l_x__ + l_y__ * o_grid_dim1] = w_grid__[l_i__];
	}
    }

    grid = o_grid__;
    grid += o_grid_offset;
    if(checkSimulatedVariance(grid,(*i_nx__),(*i_ny__))){
      moduleError(KERNEL,"draw2d_ss_3s",
		  "%s\n%s\n%s",
		  "Numerical problems in simulation of gaussian field.",
		  "Maybe too high correlation between neighbour nodes or",
		  "too high anisotropy");
    }

    return  ;
} /* draw2d_ss_3s */

void SimGaussField2D::draw2d_ss_3o(int *i_dx__,
				   int *i_nx__,
				   int *i_ny__,
				   float *o_grid__,
				   double *w_grid__)
{
    /* System generated locals */
    int o_grid_dim1, o_grid_offset, i__1, i__2, i__3;

    /* Builtin functions */


    /* Local variables */
    static int l_lag__, l_dyaddim__;
    static int l_i__, l_j__, l_x__, l_y__, l_level__, l_mxind__;
    float *grid;

    assert(i_dx__);
    assert(i_nx__);
    assert(i_ny__);
    assert(o_grid__);
    assert(w_grid__);

    /* Parameter adjustments */
    --w_grid__;
    o_grid_dim1 = *i_dx__;
    o_grid_offset = o_grid_dim1 + 1;
    o_grid__ -= o_grid_offset;

    /* Function Body */
    if (*i_nx__ * *i_ny__ <= 1) {
      moduleError(KERNEL,"draw2d_ss_3o",
		  "Illegal definition of grid size");
    }
    l_dyaddim__ = (int)
	(log(MAXIM(*i_nx__,*i_ny__) - (double)1.) / log((double)2.) + (
	    double).9999);
    l_mxind__ = (int) ldexp(1.0, l_dyaddim__) + 1;
    l_lag__ = (int) ldexp(1.0, l_dyaddim__);

/* --------DRAW THE CORNERS AND TWO LEVELS BY MATRIX INVERSION------ */
    init_c_patt();
    inito_grid( &l_mxind__, &w_grid__[1]);
/*--------DRAW THE REST OF THE NODES IN A FRACTAL FASHION----------------
-----*/
    i__1 = l_dyaddim__ - 1;
    for (l_level__ = 2; l_level__ <= i__1; ++l_level__) {
	i__2 = l_dyaddim__ - l_level__ - 1;
	l_lag__ = (int) ldexp(1.0, i__2);
/* ----------------------DRAW THE CENTER NODES OF THE SQUARES WITH COR
NERS */
/*                      DEFINED BY THE NODES OF THE PREVIOUS LEVEL */
	make_patt(&c__1, &l_lag__, &c__1, &c_n1, &c_n1);
	make_patt(&c__1, &l_lag__, &c__2, &c_n1, &c__1);
	make_patt(&c__1, &l_lag__, &c__3, &c__1, &c_n1);
	make_patt(&c__1, &l_lag__, &c__4, &c__1, &c__1);
	make_patt(&c__1, &l_lag__, &c__5, &c__3, &c__3);
	make_patt(&c__2, &l_lag__, &c__1, &c_n1, &c_n1);
	make_patt(&c__2, &l_lag__, &c__2, &c_n1, &c__1);
	make_patt(&c__2, &l_lag__, &c__3, &c__1, &c_n1);
	make_patt(&c__2, &l_lag__, &c__4, &c__1, &c__1);
	make_patt(&c__2, &l_lag__, &c__5, &c_n2, &c__0);
	make_patt(&c__2, &l_lag__, &c__6, &c_n3, &c__3);
	make_patt(&c__2, &l_lag__, &c__7, &c__3, &c__3);
	make_patt(&c__3, &l_lag__, &c__1, &c_n1, &c_n1);
	make_patt(&c__3, &l_lag__, &c__2, &c_n1, &c__1);
	make_patt(&c__3, &l_lag__, &c__3, &c__1, &c_n1);
	make_patt(&c__3, &l_lag__, &c__4, &c__1, &c__1);
	make_patt(&c__3, &l_lag__, &c__5, &c_n2, &c__0);
	make_patt(&c__3, &l_lag__, &c__6, &c_n3, &c__3);
	make_patt(&c__3, &l_lag__, &c__7, &c__3, &c__3);
	make_patt(&c__3, &l_lag__, &c__8, &c_n4, &c__0);
	make_patt(&c__4, &l_lag__, &c__1, &c_n1, &c_n1);
	make_patt(&c__4, &l_lag__, &c__2, &c_n1, &c__1);
	make_patt(&c__4, &l_lag__, &c__3, &c__1, &c_n1);
	make_patt(&c__4, &l_lag__, &c__4, &c__1, &c__1);
	make_patt(&c__4, &l_lag__, &c__5, &c_n2, &c__0);
	make_patt(&c__4, &l_lag__, &c__6, &c_n3, &c__3);
	make_patt(&c__4, &l_lag__, &c__7, &c_n4, &c__0);
	make_patt(&c__5, &l_lag__, &c__1, &c_n1, &c_n1);
	make_patt(&c__5, &l_lag__, &c__2, &c_n1, &c__1);
	make_patt(&c__5, &l_lag__, &c__3, &c__1, &c_n1);
	make_patt(&c__5, &l_lag__, &c__4, &c__1, &c__1);
	make_patt(&c__5, &l_lag__, &c__5, &c__0, &c_n2);
	make_patt(&c__5, &l_lag__, &c__6, &c__2, &c_n2);
	make_patt(&c__5, &l_lag__, &c__7, &c__3, &c__3);
	make_patt(&c__6, &l_lag__, &c__1, &c_n1, &c_n1);
	make_patt(&c__6, &l_lag__, &c__2, &c_n1, &c__1);
	make_patt(&c__6, &l_lag__, &c__3, &c__1, &c_n1);
	make_patt(&c__6, &l_lag__, &c__4, &c__1, &c__1);
	make_patt(&c__6, &l_lag__, &c__5, &c__0, &c_n2);
	make_patt(&c__6, &l_lag__, &c__6, &c__2, &c_n2);
	make_patt(&c__6, &l_lag__, &c__7, &c__3, &c__3);
	make_patt(&c__6, &l_lag__, &c__8, &c_n2, &c_n2);
	make_patt(&c__6, &l_lag__, &c__9, &c_n2, &c__0);
	make_patt(&c__6, &l_lag__, &c__10, &c_n3, &c__3);
	make_patt(&c__7, &l_lag__, &c__1, &c_n1, &c_n1);
	make_patt(&c__7, &l_lag__, &c__2, &c_n1, &c__1);
	make_patt(&c__7, &l_lag__, &c__3, &c__1, &c_n1);
	make_patt(&c__7, &l_lag__, &c__4, &c__1, &c__1);
	make_patt(&c__7, &l_lag__, &c__5, &c__0, &c_n2);
	make_patt(&c__7, &l_lag__, &c__6, &c__2, &c_n2);
	make_patt(&c__7, &l_lag__, &c__7, &c__3, &c__3);
	make_patt(&c__7, &l_lag__, &c__8, &c_n2, &c_n2);
	make_patt(&c__7, &l_lag__, &c__9, &c_n2, &c__0);
	make_patt(&c__7, &l_lag__, &c__10, &c_n4, &c__0);
	make_patt(&c__7, &l_lag__, &c__11, &c_n3, &c__3);
	make_patt(&c__8, &l_lag__, &c__1, &c_n1, &c_n1);
	make_patt(&c__8, &l_lag__, &c__2, &c_n1, &c__1);
	make_patt(&c__8, &l_lag__, &c__3, &c__1, &c_n1);
	make_patt(&c__8, &l_lag__, &c__4, &c__1, &c__1);
	make_patt(&c__8, &l_lag__, &c__5, &c__0, &c_n2);
	make_patt(&c__8, &l_lag__, &c__6, &c_n2, &c_n2);
	make_patt(&c__8, &l_lag__, &c__7, &c_n2, &c__0);
	make_patt(&c__8, &l_lag__, &c__8, &c_n4, &c__0);
	make_patt(&c__8, &l_lag__, &c__9, &c_n3, &c__3);
	make_patt(&c__9, &l_lag__, &c__1, &c_n1, &c_n1);
	make_patt(&c__9, &l_lag__, &c__2, &c_n1, &c__1);
	make_patt(&c__9, &l_lag__, &c__3, &c__1, &c_n1);
	make_patt(&c__9, &l_lag__, &c__4, &c__1, &c__1);
	make_patt(&c__9, &l_lag__, &c__5, &c__0, &c_n2);
	make_patt(&c__9, &l_lag__, &c__6, &c__0, &c_n4);
	make_patt(&c__9, &l_lag__, &c__7, &c__2, &c_n2);
	make_patt(&c__9, &l_lag__, &c__8, &c__3, &c__3);
	make_patt(&c__10, &l_lag__, &c__1, &c_n1, &c_n1);
	make_patt(&c__10, &l_lag__, &c__2, &c_n1, &c__1);
	make_patt(&c__10, &l_lag__, &c__3, &c__1, &c_n1);
	make_patt(&c__10, &l_lag__, &c__4, &c__1, &c__1);
	make_patt(&c__10, &l_lag__, &c__5, &c__0, &c_n2);
	make_patt(&c__10, &l_lag__, &c__6, &c__0, &c_n4);
	make_patt(&c__10, &l_lag__, &c__7, &c__2, &c_n2);
	make_patt(&c__11, &l_lag__, &c__1, &c_n1, &c_n1);
	make_patt(&c__11, &l_lag__, &c__2, &c_n1, &c__1);
	make_patt(&c__11, &l_lag__, &c__3, &c__1, &c_n1);
	make_patt(&c__11, &l_lag__, &c__4, &c__1, &c__1);
	make_patt(&c__11, &l_lag__, &c__5, &c__0, &c_n2);
	make_patt(&c__11, &l_lag__, &c__6, &c__0, &c_n4);
	make_patt(&c__11, &l_lag__, &c__7, &c__2, &c_n2);
	make_patt(&c__11, &l_lag__, &c__8, &c__3, &c__3);
	make_patt(&c__11, &l_lag__, &c__9, &c_n2, &c_n2);
	make_patt(&c__11, &l_lag__, &c__10, &c_n2, &c__0);
	make_patt(&c__11, &l_lag__, &c__11, &c_n3, &c__3);
	make_patt(&c__12, &l_lag__, &c__1, &c_n1, &c_n1);
	make_patt(&c__12, &l_lag__, &c__2, &c_n1, &c__1);
	make_patt(&c__12, &l_lag__, &c__3, &c__1, &c_n1);
	make_patt(&c__12, &l_lag__, &c__4, &c__1, &c__1);
	make_patt(&c__12, &l_lag__, &c__5, &c__0, &c_n2);
	make_patt(&c__12, &l_lag__, &c__6, &c__0, &c_n4);
	make_patt(&c__12, &l_lag__, &c__7, &c__2, &c_n2);
	make_patt(&c__12, &l_lag__, &c__8, &c_n2, &c_n2);
	make_patt(&c__12, &l_lag__, &c__9, &c_n2, &c__0);
	make_patt(&c__13, &l_lag__, &c__1, &c_n1, &c_n1);
	make_patt(&c__13, &l_lag__, &c__2, &c_n1, &c__1);
	make_patt(&c__13, &l_lag__, &c__3, &c__1, &c_n1);
	make_patt(&c__13, &l_lag__, &c__4, &c__1, &c__1);
	make_patt(&c__13, &l_lag__, &c__5, &c__0, &c_n2);
	make_patt(&c__13, &l_lag__, &c__6, &c__0, &c_n4);
	make_patt(&c__13, &l_lag__, &c__7, &c__2, &c_n2);
	make_patt(&c__13, &l_lag__, &c__8, &c_n2, &c_n2);
	make_patt(&c__13, &l_lag__, &c__9, &c_n2, &c__0);
	make_patt(&c__13, &l_lag__, &c__10, &c_n4, &c__0);
	make_patt(&c__13, &l_lag__, &c__11, &c__3, &c__3);
	make_patt(&c__13, &l_lag__, &c__12, &c_n3, &c__3);
	make_patt(&c__14, &l_lag__, &c__1, &c_n1, &c_n1);
	make_patt(&c__14, &l_lag__, &c__2, &c_n1, &c__1);
	make_patt(&c__14, &l_lag__, &c__3, &c__1, &c_n1);
	make_patt(&c__14, &l_lag__, &c__4, &c__1, &c__1);
	make_patt(&c__14, &l_lag__, &c__5, &c__0, &c_n2);
	make_patt(&c__14, &l_lag__, &c__6, &c__0, &c_n4);
	make_patt(&c__14, &l_lag__, &c__7, &c_n2, &c_n2);
	make_patt(&c__14, &l_lag__, &c__8, &c_n2, &c__0);
	make_patt(&c__14, &l_lag__, &c__9, &c_n4, &c__0);
	make_patt(&c__14, &l_lag__, &c__10, &c_n3, &c__3);
	make_patt(&c__15, &l_lag__, &c__1, &c_n1, &c_n1);
	make_patt(&c__15, &l_lag__, &c__2, &c_n1, &c__1);
	make_patt(&c__15, &l_lag__, &c__3, &c__1, &c_n1);
	make_patt(&c__15, &l_lag__, &c__4, &c__1, &c__1);
	make_patt(&c__15, &l_lag__, &c__5, &c__0, &c_n2);
	make_patt(&c__15, &l_lag__, &c__6, &c__0, &c_n4);
	make_patt(&c__15, &l_lag__, &c__7, &c_n2, &c_n2);
	make_patt(&c__15, &l_lag__, &c__8, &c_n2, &c__0);
	make_patt(&c__15, &l_lag__, &c__9, &c_n4, &c__0);
	make_patt(&c__15, &l_lag__, &c__10, &c__2, &c_n2);
	make_patt(&c__16, &l_lag__, &c__1, &c_n1, &c_n1);
	make_patt(&c__16, &l_lag__, &c__2, &c_n1, &c__1);
	make_patt(&c__16, &l_lag__, &c__3, &c__1, &c_n1);
	make_patt(&c__16, &l_lag__, &c__4, &c__1, &c__1);
	make_patt(&c__16, &l_lag__, &c__5, &c__0, &c_n2);
	make_patt(&c__16, &l_lag__, &c__6, &c__0, &c_n4);
	make_patt(&c__16, &l_lag__, &c__7, &c_n2, &c_n2);
	make_patt(&c__16, &l_lag__, &c__8, &c_n2, &c__0);
	make_patt(&c__16, &l_lag__, &c__9, &c_n4, &c__0);
	init_weights_o(&c__1,  &c__5);
	init_weights_o(&c__2,  &c__7);
	init_weights_o(&c__3,  &c__8);
	init_weights_o(&c__4,  &c__7);
	init_weights_o(&c__5,  &c__7);
	init_weights_o(&c__6,  &c__10);
	init_weights_o(&c__7,  &c__11);
	init_weights_o(&c__8,  &c__9);
	init_weights_o(&c__9,  &c__8);
	init_weights_o(&c__10,  &c__7);
	init_weights_o(&c__11,  &c__11);
	init_weights_o(&c__12,  &c__9);
	init_weights_o(&c__13,  &c__12);
	init_weights_o(&c__14,  &c__10);
	init_weights_o(&c__15,  &c__10);
	init_weights_o(&c__16,  &c__9);
/* ---------------------FIRST LINE */
	l_y__ = l_lag__ + 1;
	l_x__ = l_lag__ + 1;
	draw_node(&c__1, &c__5, &l_mxind__, &l_x__, &l_y__, &w_grid__[1]);
	l_x__ = l_lag__ * 3 + 1;
	draw_node(&c__2, &c__7, &l_mxind__, &l_x__, &l_y__, &w_grid__[1]);
	i__2 = (int) ldexp(1.0, l_level__) - 1;
	for (l_i__ = 3; l_i__ <= i__2; ++l_i__) {
	    l_x__ = ((l_i__ << 1) - 1) * l_lag__ + 1;
	    draw_node(&c__3, &c__8, &l_mxind__, &l_x__, &l_y__, &w_grid__[1]
		    );
	}
	l_x__ = l_mxind__ - l_lag__;
	draw_node(&c__4, &c__7, &l_mxind__, &l_x__, &l_y__, &w_grid__[1]);
/* ---------------------SECOND LINE */
	l_y__ = l_lag__ * 3 + 1;
	l_x__ = l_lag__ + 1;
	draw_node(&c__5, &c__7, &l_mxind__, &l_x__, &l_y__, &w_grid__[1]);
	l_x__ = l_lag__ * 3 + 1;
	draw_node(&c__6, &c__10, &l_mxind__, &l_x__, &l_y__, &w_grid__[1]);
	i__2 = (int) ldexp(1.0, l_level__) - 1;
	for (l_i__ = 3; l_i__ <= i__2; ++l_i__) {
	    l_x__ = ((l_i__ << 1) - 1) * l_lag__ + 1;
	    draw_node(&c__7, &c__11, &l_mxind__, &l_x__, &l_y__, &w_grid__[
		    1]);
	}
	l_x__ = l_mxind__ - l_lag__;
	draw_node(&c__8, &c__9, &l_mxind__, &l_x__, &l_y__, &w_grid__[1]);
/* ---------------------FIRST COLUMN */
	l_x__ = l_lag__ + 1;
	i__2 = (int) ldexp(1.0, l_level__) - 1;
	for (l_j__ = 3; l_j__ <= i__2; ++l_j__) {
	    l_y__ = ((l_j__ << 1) - 1) * l_lag__ + 1;
	    draw_node(&c__9, &c__8, &l_mxind__, &l_x__, &l_y__, &w_grid__[1]
		    );
	}
	l_y__ = l_mxind__ - l_lag__;
	draw_node(&c__10, &c__7, &l_mxind__, &l_x__, &l_y__, &w_grid__[1]);
/* ---------------------SECOND COLUMN */
	l_x__ = l_lag__ * 3 + 1;
	i__2 = (int) ldexp(1.0, l_level__) - 1;
	for (l_j__ = 3; l_j__ <= i__2; ++l_j__) {
	    l_y__ = ((l_j__ << 1) - 1) * l_lag__ + 1;
	    draw_node(&c__11, &c__11, &l_mxind__, &l_x__, &l_y__, &w_grid__[
		    1]);
	}
	l_y__ = l_mxind__ - l_lag__;
	draw_node(&c__12, &c__9, &l_mxind__, &l_x__, &l_y__, &w_grid__[1]);
/* ---------------------INTERIOR NODES */
	i__2 = (int) ldexp(1.0, l_level__) - 1;
	for (l_j__ = 3; l_j__ <= i__2; ++l_j__) {
	    l_y__ = ((l_j__ << 1) - 1) * l_lag__ + 1;
	    i__3 = (int) ldexp(1.0, l_level__) - 1;
	    for (l_i__ = 3; l_i__ <= i__3; ++l_i__) {
		l_x__ = ((l_i__ << 1) - 1) * l_lag__ + 1;
		draw_node(&c__13, &c__12, &l_mxind__, &l_x__, &l_y__, &
			w_grid__[1]);
	    }
/*                     LAST COLUMN */
	    l_x__ = l_mxind__ - l_lag__;
	    draw_node(&c__14, &c__10, &l_mxind__, &l_x__, &l_y__, &w_grid__[
		    1]);
	}
/* ---------------------LAST LINE */
	l_y__ = l_mxind__ - l_lag__;
	i__2 = (int) ldexp(1.0, l_level__) - 1;
	for (l_i__ = 3; l_i__ <= i__2; ++l_i__) {
	    l_x__ = ((l_i__ << 1) - 1) * l_lag__ + 1;
	    draw_node(&c__15, &c__10, &l_mxind__, &l_x__, &l_y__, &w_grid__[
		    1]);
	}
	l_x__ = l_mxind__ - l_lag__;
	draw_node(&c__16, &c__9, &l_mxind__, &l_x__, &l_y__, &w_grid__[1]);
/*----------------------DRAW THE CENTER NODES OF THE TILTED SQUARES WI
TH CORNERS*/
/*                     DEFINED BY THE NODES OF THIS AND THE THE PREVIO
US LEVEL*/
	make_patt(&c__1, &l_lag__, &c__1, &c__0, &c_n1);
	make_patt(&c__1, &l_lag__, &c__2, &c__0, &c__1);
	make_patt(&c__1, &l_lag__, &c__3, &c_n1, &c__0);
	make_patt(&c__1, &l_lag__, &c__4, &c__1, &c__0);
	make_patt(&c__1, &l_lag__, &c__5, &c__3, &c__0);
	make_patt(&c__1, &l_lag__, &c__6, &c__0, &c__3);
	make_patt(&c__2, &l_lag__, &c__1, &c__0, &c_n1);
	make_patt(&c__2, &l_lag__, &c__2, &c__0, &c__1);
	make_patt(&c__2, &l_lag__, &c__3, &c_n1, &c__0);
	make_patt(&c__2, &l_lag__, &c__4, &c__1, &c__0);
	make_patt(&c__2, &l_lag__, &c__5, &c__3, &c__0);
	make_patt(&c__2, &l_lag__, &c__6, &c__0, &c__3);
	make_patt(&c__2, &l_lag__, &c__7, &c_n2, &c__0);
	make_patt(&c__3, &l_lag__, &c__1, &c__0, &c_n1);
	make_patt(&c__3, &l_lag__, &c__2, &c__0, &c__1);
	make_patt(&c__3, &l_lag__, &c__3, &c_n1, &c__0);
	make_patt(&c__3, &l_lag__, &c__4, &c__1, &c__0);
	make_patt(&c__3, &l_lag__, &c__5, &c__0, &c__3);
	make_patt(&c__3, &l_lag__, &c__6, &c__2, &c__0);
	make_patt(&c__4, &l_lag__, &c__1, &c__0, &c_n1);
	make_patt(&c__4, &l_lag__, &c__2, &c__0, &c__1);
	make_patt(&c__4, &l_lag__, &c__3, &c_n1, &c__0);
	make_patt(&c__4, &l_lag__, &c__4, &c__1, &c__0);
	make_patt(&c__4, &l_lag__, &c__5, &c__0, &c__3);
	make_patt(&c__4, &l_lag__, &c__6, &c__3, &c__0);
	make_patt(&c__4, &l_lag__, &c__7, &c__1, &c_n1);
	make_patt(&c__5, &l_lag__, &c__1, &c__0, &c_n1);
	make_patt(&c__5, &l_lag__, &c__2, &c__0, &c__1);
	make_patt(&c__5, &l_lag__, &c__3, &c_n1, &c__0);
	make_patt(&c__5, &l_lag__, &c__4, &c__1, &c__0);
	make_patt(&c__5, &l_lag__, &c__5, &c__0, &c__3);
	make_patt(&c__5, &l_lag__, &c__6, &c__3, &c__0);
	make_patt(&c__5, &l_lag__, &c__7, &c__1, &c_n1);
	make_patt(&c__5, &l_lag__, &c__8, &c_n1, &c_n1);
	make_patt(&c__5, &l_lag__, &c__9, &c_n2, &c__0);
	make_patt(&c__6, &l_lag__, &c__1, &c__0, &c_n1);
	make_patt(&c__6, &l_lag__, &c__2, &c__0, &c__1);
	make_patt(&c__6, &l_lag__, &c__3, &c_n1, &c__0);
	make_patt(&c__6, &l_lag__, &c__4, &c__1, &c__0);
	make_patt(&c__6, &l_lag__, &c__5, &c__0, &c__3);
	make_patt(&c__6, &l_lag__, &c__6, &c_n1, &c_n1);
	make_patt(&c__6, &l_lag__, &c__7, &c_n2, &c__0);
	make_patt(&c__7, &l_lag__, &c__1, &c__0, &c_n1);
	make_patt(&c__7, &l_lag__, &c__2, &c__0, &c__1);
	make_patt(&c__7, &l_lag__, &c__3, &c_n1, &c__0);
	make_patt(&c__7, &l_lag__, &c__4, &c__1, &c__0);
	make_patt(&c__7, &l_lag__, &c__5, &c__0, &c__3);
	make_patt(&c__7, &l_lag__, &c__6, &c__1, &c_n1);
	make_patt(&c__7, &l_lag__, &c__7, &c_n1, &c_n1);
	make_patt(&c__7, &l_lag__, &c__8, &c__0, &c_n2);
	make_patt(&c__7, &l_lag__, &c__9, &c__2, &c_n2);
	make_patt(&c__7, &l_lag__, &c__10, &c__3, &c__0);
	make_patt(&c__8, &l_lag__, &c__1, &c__0, &c_n1);
	make_patt(&c__8, &l_lag__, &c__2, &c__0, &c__1);
	make_patt(&c__8, &l_lag__, &c__3, &c_n1, &c__0);
	make_patt(&c__8, &l_lag__, &c__4, &c__1, &c__0);
	make_patt(&c__8, &l_lag__, &c__5, &c__0, &c__3);
	make_patt(&c__8, &l_lag__, &c__6, &c__1, &c_n1);
	make_patt(&c__8, &l_lag__, &c__7, &c_n1, &c_n1);
	make_patt(&c__8, &l_lag__, &c__8, &c_n2, &c__0);
	make_patt(&c__8, &l_lag__, &c__9, &c__3, &c__0);
	make_patt(&c__8, &l_lag__, &c__10, &c_n2, &c_n2);
	make_patt(&c__8, &l_lag__, &c__11, &c__0, &c_n2);
	make_patt(&c__8, &l_lag__, &c__12, &c__2, &c_n2);
	make_patt(&c__9, &l_lag__, &c__1, &c__0, &c_n1);
	make_patt(&c__9, &l_lag__, &c__2, &c__0, &c__1);
	make_patt(&c__9, &l_lag__, &c__3, &c_n1, &c__0);
	make_patt(&c__9, &l_lag__, &c__4, &c__1, &c__0);
	make_patt(&c__9, &l_lag__, &c__5, &c__0, &c__3);
	make_patt(&c__9, &l_lag__, &c__6, &c__1, &c_n1);
	make_patt(&c__9, &l_lag__, &c__7, &c_n1, &c_n1);
	make_patt(&c__9, &l_lag__, &c__8, &c_n2, &c__0);
	make_patt(&c__9, &l_lag__, &c__9, &c_n2, &c_n2);
	make_patt(&c__9, &l_lag__, &c__10, &c__0, &c_n2);
	make_patt(&c__10, &l_lag__, &c__1, &c__0, &c_n1);
	make_patt(&c__10, &l_lag__, &c__2, &c__0, &c__1);
	make_patt(&c__10, &l_lag__, &c__3, &c_n1, &c__0);
	make_patt(&c__10, &l_lag__, &c__4, &c__1, &c__0);
	make_patt(&c__10, &l_lag__, &c__5, &c__0, &c__3);
	make_patt(&c__10, &l_lag__, &c__6, &c__1, &c_n1);
	make_patt(&c__10, &l_lag__, &c__7, &c__0, &c_n2);
	make_patt(&c__10, &l_lag__, &c__8, &c__2, &c_n2);
	make_patt(&c__10, &l_lag__, &c__9, &c__3, &c__0);
	make_patt(&c__11, &l_lag__, &c__1, &c__0, &c_n1);
	make_patt(&c__11, &l_lag__, &c__2, &c__0, &c__1);
	make_patt(&c__11, &l_lag__, &c__3, &c_n1, &c__0);
	make_patt(&c__11, &l_lag__, &c__4, &c__1, &c__0);
	make_patt(&c__11, &l_lag__, &c__5, &c__0, &c__3);
	make_patt(&c__11, &l_lag__, &c__6, &c_n1, &c_n1);
	make_patt(&c__11, &l_lag__, &c__7, &c_n2, &c__0);
	make_patt(&c__11, &l_lag__, &c__8, &c_n2, &c_n2);
	make_patt(&c__11, &l_lag__, &c__9, &c__0, &c_n2);
	make_patt(&c__12, &l_lag__, &c__1, &c__0, &c_n1);
	make_patt(&c__12, &l_lag__, &c__2, &c__0, &c__1);
	make_patt(&c__12, &l_lag__, &c__3, &c_n1, &c__0);
	make_patt(&c__12, &l_lag__, &c__4, &c__1, &c__0);
	make_patt(&c__12, &l_lag__, &c__5, &c__1, &c_n1);
	make_patt(&c__12, &l_lag__, &c__6, &c__0, &c_n2);
	make_patt(&c__12, &l_lag__, &c__7, &c__2, &c_n2);
	make_patt(&c__12, &l_lag__, &c__8, &c__3, &c__0);
	make_patt(&c__13, &l_lag__, &c__1, &c__0, &c_n1);
	make_patt(&c__13, &l_lag__, &c__2, &c__0, &c__1);
	make_patt(&c__13, &l_lag__, &c__3, &c_n1, &c__0);
	make_patt(&c__13, &l_lag__, &c__4, &c__1, &c__0);
	make_patt(&c__13, &l_lag__, &c__5, &c__1, &c_n1);
	make_patt(&c__13, &l_lag__, &c__6, &c_n1, &c_n1);
	make_patt(&c__13, &l_lag__, &c__7, &c_n2, &c__0);
	make_patt(&c__13, &l_lag__, &c__8, &c__3, &c__0);
	make_patt(&c__13, &l_lag__, &c__9, &c_n2, &c_n2);
	make_patt(&c__13, &l_lag__, &c__10, &c__0, &c_n2);
	make_patt(&c__13, &l_lag__, &c__11, &c__2, &c_n2);
	make_patt(&c__14, &l_lag__, &c__1, &c__0, &c_n1);
	make_patt(&c__14, &l_lag__, &c__2, &c__0, &c__1);
	make_patt(&c__14, &l_lag__, &c__3, &c_n1, &c__0);
	make_patt(&c__14, &l_lag__, &c__4, &c__1, &c__0);
	make_patt(&c__14, &l_lag__, &c__5, &c_n1, &c_n1);
	make_patt(&c__14, &l_lag__, &c__6, &c_n2, &c__0);
	make_patt(&c__14, &l_lag__, &c__7, &c_n2, &c_n2);
	make_patt(&c__14, &l_lag__, &c__8, &c__0, &c_n2);
	make_patt(&c__15, &l_lag__, &c__1, &c__0, &c_n1);
	make_patt(&c__15, &l_lag__, &c__2, &c__0, &c__1);
	make_patt(&c__15, &l_lag__, &c__3, &c_n1, &c__0);
	make_patt(&c__15, &l_lag__, &c__4, &c__1, &c__0);
	make_patt(&c__15, &l_lag__, &c__5, &c__1, &c_n1);
	make_patt(&c__15, &l_lag__, &c__6, &c_n1, &c_n1);
	make_patt(&c__15, &l_lag__, &c__7, &c__0, &c_n2);
	make_patt(&c__15, &l_lag__, &c__8, &c__2, &c_n2);
	make_patt(&c__16, &l_lag__, &c__1, &c__0, &c_n1);
	make_patt(&c__16, &l_lag__, &c__2, &c__0, &c__1);
	make_patt(&c__16, &l_lag__, &c__3, &c_n1, &c__0);
	make_patt(&c__16, &l_lag__, &c__4, &c__1, &c__0);
	make_patt(&c__16, &l_lag__, &c__5, &c__1, &c_n1);
	make_patt(&c__16, &l_lag__, &c__6, &c_n1, &c_n1);
	make_patt(&c__16, &l_lag__, &c__7, &c_n2, &c__0);
	make_patt(&c__16, &l_lag__, &c__8, &c_n2, &c_n2);
	make_patt(&c__16, &l_lag__, &c__9, &c__0, &c_n2);
	init_weights_o(&c__1,  &c__6);
	init_weights_o(&c__2,  &c__7);
	init_weights_o(&c__3,  &c__6);
	init_weights_o(&c__4,  &c__7);
	init_weights_o(&c__5,  &c__9);
	init_weights_o(&c__6,  &c__7);
	init_weights_o(&c__7,  &c__10);
	init_weights_o(&c__8,  &c__12);
	init_weights_o(&c__9,  &c__10);
	init_weights_o(&c__10,  &c__9);
	init_weights_o(&c__11,  &c__9);
	init_weights_o(&c__12,  &c__8);
	init_weights_o(&c__13,  &c__11);
	init_weights_o(&c__14,  &c__8);
	init_weights_o(&c__15,  &c__8);
	init_weights_o(&c__16,  &c__9);
	l_x__ = (l_lag__ << 1) + 1;
	l_y__ = l_lag__ + 1;
	draw_node(&c__1, &c__6, &l_mxind__, &l_x__, &l_y__, &w_grid__[1]);
	i__2 = (int) ldexp(1.0, l_level__) - 2;
	for (l_i__ = 2; l_i__ <= i__2; ++l_i__) {
	    l_x__ = (l_i__ << 1) * l_lag__ + 1;
	    draw_node(&c__2, &c__7, &l_mxind__, &l_x__, &l_y__, &w_grid__[1]
		    );
	}
	l_x__ = l_mxind__ - (l_lag__ << 1);
	draw_node(&c__3, &c__6, &l_mxind__, &l_x__, &l_y__, &w_grid__[1]);
	l_x__ = l_lag__ + 1;
	l_y__ = (l_lag__ << 1) + 1;
	draw_node(&c__4, &c__7, &l_mxind__, &l_x__, &l_y__, &w_grid__[1]);
	i__2 = (int) ldexp(1.0, l_level__) - 1;
	for (l_i__ = 2; l_i__ <= i__2; ++l_i__) {
	    l_x__ = ((l_i__ << 1) - 1) * l_lag__ + 1;
	    draw_node(&c__5, &c__9, &l_mxind__, &l_x__, &l_y__, &w_grid__[1]
		    );
	}
	l_x__ = l_mxind__ - l_lag__;
	draw_node(&c__6, &c__7, &l_mxind__, &l_x__, &l_y__, &w_grid__[1]);
	i__2 = (int) ldexp(1.0, l_level__) - 1;
	for (l_j__ = 2; l_j__ <= i__2; ++l_j__) {
	    l_x__ = (l_lag__ << 1) + 1;
	    l_y__ = ((l_j__ << 1) - 1) * l_lag__ + 1;
	    draw_node(&c__7, &c__10, &l_mxind__, &l_x__, &l_y__, &w_grid__[
		    1]);
	    i__3 = (int) ldexp(1.0, l_level__) - 2;
	    for (l_i__ = 2; l_i__ <= i__3; ++l_i__) {
		l_x__ = (l_i__ << 1) * l_lag__ + 1;
		draw_node(&c__8, &c__12, &l_mxind__, &l_x__, &l_y__, &
			w_grid__[1]);
	    }
	    l_x__ = l_mxind__ - (l_lag__ << 1);
	    draw_node(&c__9, &c__10, &l_mxind__, &l_x__, &l_y__, &w_grid__[
		    1]);
	    if (l_j__ < (int) ldexp(1.0, l_level__) - 1) {
		l_x__ = l_lag__ + 1;
		l_y__ = (l_j__ << 1) * l_lag__ + 1;
		draw_node(&c__10, &c__9, &l_mxind__, &l_x__, &l_y__, &
			w_grid__[1]);
		i__3 = (int) ldexp(1.0, l_level__) - 1;
		for (l_i__ = 2; l_i__ <= i__3; ++l_i__) {
		    l_x__ = ((l_i__ << 1) - 1) * l_lag__ + 1;
		    draw_node(&c__8, &c__12, &l_mxind__, &l_x__, &l_y__, &
			    w_grid__[1]);
		}
		l_x__ = l_mxind__ - l_lag__;
		draw_node(&c__11, &c__9, &l_mxind__, &l_x__, &l_y__, &
			w_grid__[1]);
	    }
	}
	l_x__ = l_lag__ + 1;
	l_y__ = l_mxind__ - (l_lag__ << 1);
	draw_node(&c__12, &c__8, &l_mxind__, &l_x__, &l_y__, &w_grid__[1]);
	i__2 = (int) ldexp(1.0, l_level__) - 1;
	for (l_i__ = 2; l_i__ <= i__2; ++l_i__) {
	    l_x__ = ((l_i__ << 1) - 1) * l_lag__ + 1;
	    draw_node(&c__13, &c__11, &l_mxind__, &l_x__, &l_y__, &w_grid__[
		    1]);
	}
	l_x__ = l_mxind__ - l_lag__;
	draw_node(&c__14, &c__8, &l_mxind__, &l_x__, &l_y__, &w_grid__[1]);
	l_x__ = (l_lag__ << 1) + 1;
	l_y__ = l_mxind__ - l_lag__;
	draw_node(&c__15, &c__8, &l_mxind__, &l_x__, &l_y__, &w_grid__[1]);
	i__2 = (int) ldexp(1.0, l_level__) - 2;
	for (l_i__ = 2; l_i__ <= i__2; ++l_i__) {
	    l_x__ = (l_i__ << 1) * l_lag__ + 1;
	    draw_node(&c__13, &c__11, &l_mxind__, &l_x__, &l_y__, &w_grid__[
		    1]);
	}
	l_x__ = l_mxind__ - (l_lag__ << 1);
	draw_node(&c__16, &c__9, &l_mxind__, &l_x__, &l_y__, &w_grid__[1]);
/* ----------------------DRAW THE BOARDER NODES ON THE FOUR EDGES */

	make_patt(&c__1, &l_lag__, &c__1, &c__0, &c_n1);
	make_patt(&c__1, &l_lag__, &c__2, &c__0, &c__1);
	make_patt(&c__1, &l_lag__, &c__3, &c__1, &c__0);
	make_patt(&c__1, &l_lag__, &c__4, &c__1, &c__1);
	make_patt(&c__1, &l_lag__, &c__5, &c__2, &c__0);
	make_patt(&c__1, &l_lag__, &c__6, &c__2, &c__2);
	make_patt(&c__1, &l_lag__, &c__7, &c__0, &c__3);
	make_patt(&c__2, &l_lag__, &c__1, &c__0, &c_n1);
	make_patt(&c__2, &l_lag__, &c__2, &c__0, &c__1);
	make_patt(&c__2, &l_lag__, &c__3, &c__1, &c__0);
	make_patt(&c__2, &l_lag__, &c__4, &c__1, &c__1);
	make_patt(&c__2, &l_lag__, &c__5, &c__2, &c__0);
	make_patt(&c__2, &l_lag__, &c__6, &c__2, &c__2);
	make_patt(&c__2, &l_lag__, &c__7, &c__0, &c__3);
	make_patt(&c__2, &l_lag__, &c__8, &c__1, &c_n1);
	make_patt(&c__2, &l_lag__, &c__9, &c__0, &c_n2);
	make_patt(&c__2, &l_lag__, &c__10, &c__2, &c_n2);
	make_patt(&c__3, &l_lag__, &c__1, &c__0, &c_n1);
	make_patt(&c__3, &l_lag__, &c__2, &c__0, &c__1);
	make_patt(&c__3, &l_lag__, &c__3, &c__1, &c__0);
	make_patt(&c__3, &l_lag__, &c__4, &c__2, &c__0);
	make_patt(&c__3, &l_lag__, &c__5, &c__1, &c_n1);
	make_patt(&c__3, &l_lag__, &c__6, &c__0, &c_n2);
	make_patt(&c__3, &l_lag__, &c__7, &c__2, &c_n2);
	make_patt(&c__4, &l_lag__, &c__1, &c_n1, &c__0);
	make_patt(&c__4, &l_lag__, &c__2, &c__1, &c__0);
	make_patt(&c__4, &l_lag__, &c__3, &c__0, &c_n1);
	make_patt(&c__4, &l_lag__, &c__4, &c_n1, &c_n1);
	make_patt(&c__4, &l_lag__, &c__5, &c__1, &c_n1);
	make_patt(&c__4, &l_lag__, &c__6, &c__0, &c_n2);
	make_patt(&c__4, &l_lag__, &c__7, &c__2, &c_n2);
	make_patt(&c__4, &l_lag__, &c__8, &c__3, &c__0);
	make_patt(&c__5, &l_lag__, &c__1, &c_n1, &c__0);
	make_patt(&c__5, &l_lag__, &c__2, &c__1, &c__0);
	make_patt(&c__5, &l_lag__, &c__3, &c__0, &c_n1);
	make_patt(&c__5, &l_lag__, &c__4, &c_n1, &c_n1);
	make_patt(&c__5, &l_lag__, &c__5, &c__1, &c_n1);
	make_patt(&c__5, &l_lag__, &c__6, &c__0, &c_n2);
	make_patt(&c__5, &l_lag__, &c__7, &c__2, &c_n2);
	make_patt(&c__5, &l_lag__, &c__8, &c__3, &c__0);
	make_patt(&c__5, &l_lag__, &c__9, &c_n2, &c__0);
	make_patt(&c__5, &l_lag__, &c__10, &c_n2, &c_n2);
	make_patt(&c__6, &l_lag__, &c__1, &c_n1, &c__0);
	make_patt(&c__6, &l_lag__, &c__2, &c__1, &c__0);
	make_patt(&c__6, &l_lag__, &c__3, &c__0, &c_n1);
	make_patt(&c__6, &l_lag__, &c__4, &c_n1, &c_n1);
	make_patt(&c__6, &l_lag__, &c__5, &c__0, &c_n2);
	make_patt(&c__6, &l_lag__, &c__6, &c_n2, &c__0);
	make_patt(&c__6, &l_lag__, &c__7, &c_n2, &c_n2);
	make_patt(&c__7, &l_lag__, &c__1, &c__0, &c__1);
	make_patt(&c__7, &l_lag__, &c__2, &c_n1, &c__1);
	make_patt(&c__7, &l_lag__, &c__3, &c_n1, &c__0);
	make_patt(&c__7, &l_lag__, &c__4, &c_n1, &c_n1);
	make_patt(&c__7, &l_lag__, &c__5, &c__0, &c_n1);
	make_patt(&c__7, &l_lag__, &c__6, &c_n2, &c__0);
	make_patt(&c__7, &l_lag__, &c__7, &c__0, &c_n3);
	make_patt(&c__7, &l_lag__, &c__8, &c_n2, &c_n2);
	make_patt(&c__8, &l_lag__, &c__1, &c__0, &c__1);
	make_patt(&c__8, &l_lag__, &c__2, &c_n1, &c__1);
	make_patt(&c__8, &l_lag__, &c__3, &c_n1, &c__0);
	make_patt(&c__8, &l_lag__, &c__4, &c_n1, &c_n1);
	make_patt(&c__8, &l_lag__, &c__5, &c__0, &c_n1);
	make_patt(&c__8, &l_lag__, &c__6, &c_n2, &c__0);
	make_patt(&c__8, &l_lag__, &c__7, &c__0, &c_n3);
	make_patt(&c__8, &l_lag__, &c__8, &c_n2, &c_n2);
	make_patt(&c__8, &l_lag__, &c__9, &c_n2, &c__2);
	make_patt(&c__8, &l_lag__, &c__10, &c__0, &c__2);
	make_patt(&c__9, &l_lag__, &c__1, &c__0, &c__1);
	make_patt(&c__9, &l_lag__, &c__2, &c_n1, &c__1);
	make_patt(&c__9, &l_lag__, &c__3, &c_n1, &c__0);
	make_patt(&c__9, &l_lag__, &c__4, &c__0, &c_n1);
	make_patt(&c__9, &l_lag__, &c__5, &c_n2, &c__0);
	make_patt(&c__9, &l_lag__, &c__6, &c_n2, &c__2);
	make_patt(&c__9, &l_lag__, &c__7, &c__0, &c__2);
	make_patt(&c__10, &l_lag__, &c__1, &c_n1, &c__0);
	make_patt(&c__10, &l_lag__, &c__2, &c__1, &c__0);
	make_patt(&c__10, &l_lag__, &c__3, &c_n1, &c__1);
	make_patt(&c__10, &l_lag__, &c__4, &c__0, &c__1);
	make_patt(&c__10, &l_lag__, &c__5, &c__1, &c__1);
	make_patt(&c__10, &l_lag__, &c__6, &c__0, &c__2);
	make_patt(&c__10, &l_lag__, &c__7, &c_n2, &c__2);
	make_patt(&c__10, &l_lag__, &c__8, &c_n3, &c__0);
	make_patt(&c__11, &l_lag__, &c__1, &c_n1, &c__0);
	make_patt(&c__11, &l_lag__, &c__2, &c__1, &c__0);
	make_patt(&c__11, &l_lag__, &c__3, &c_n1, &c__1);
	make_patt(&c__11, &l_lag__, &c__4, &c__0, &c__1);
	make_patt(&c__11, &l_lag__, &c__5, &c__1, &c__1);
	make_patt(&c__11, &l_lag__, &c__6, &c__0, &c__2);
	make_patt(&c__11, &l_lag__, &c__7, &c_n2, &c__2);
	make_patt(&c__11, &l_lag__, &c__8, &c_n3, &c__0);
	make_patt(&c__11, &l_lag__, &c__9, &c__2, &c__2);
	make_patt(&c__11, &l_lag__, &c__10, &c__2, &c__0);
	make_patt(&c__12, &l_lag__, &c__1, &c_n1, &c__0);
	make_patt(&c__12, &l_lag__, &c__2, &c__1, &c__0);
	make_patt(&c__12, &l_lag__, &c__3, &c_n1, &c__1);
	make_patt(&c__12, &l_lag__, &c__4, &c__0, &c__1);
	make_patt(&c__12, &l_lag__, &c__5, &c__1, &c__1);
	make_patt(&c__12, &l_lag__, &c__6, &c__0, &c__2);
	make_patt(&c__12, &l_lag__, &c__7, &c__2, &c__2);
	make_patt(&c__12, &l_lag__, &c__8, &c__2, &c__0);
	init_weights_o(&c__1,  &c__7);
	init_weights_o(&c__2,  &c__10);
	init_weights_o(&c__3,  &c__7);
	init_weights_o(&c__4,  &c__8);
	init_weights_o(&c__5,  &c__10);
	init_weights_o(&c__6,  &c__7);
	init_weights_o(&c__7,  &c__8);
	init_weights_o(&c__8,  &c__10);
	init_weights_o(&c__9,  &c__7);
	init_weights_o(&c__10,  &c__8);
	init_weights_o(&c__11,  &c__10);
	init_weights_o(&c__12,  &c__8);
	l_x__ = 1;
	l_y__ = l_lag__ + 1;
	draw_node(&c__1, &c__7, &l_mxind__, &l_x__, &l_y__, &w_grid__[1]);
	i__2 = (int) ldexp(1.0, l_level__) - 1;
	for (l_j__ = 2; l_j__ <= i__2; ++l_j__) {
	    l_y__ = ((l_j__ << 1) - 1) * l_lag__ + 1;
	    draw_node(&c__2, &c__10, &l_mxind__, &l_x__, &l_y__, &w_grid__[
		    1]);
	}
	l_y__ = l_mxind__ - l_lag__;
	draw_node(&c__3, &c__7, &l_mxind__, &l_x__, &l_y__, &w_grid__[1]);
	l_x__ = l_lag__ + 1;
	l_y__ = l_mxind__;
	draw_node(&c__4, &c__8, &l_mxind__, &l_x__, &l_y__, &w_grid__[1]);
	i__2 = (int) ldexp(1.0, l_level__) - 1;
	for (l_i__ = 2; l_i__ <= i__2; ++l_i__) {
	    l_x__ = ((l_i__ << 1) - 1) * l_lag__ + 1;
	    draw_node(&c__5, &c__10, &l_mxind__, &l_x__, &l_y__, &w_grid__[
		    1]);
	}
	l_x__ = l_mxind__ - l_lag__;
	draw_node(&c__6, &c__7, &l_mxind__, &l_x__, &l_y__, &w_grid__[1]);
	l_x__ = l_mxind__;
	l_y__ = l_mxind__ - l_lag__;
	draw_node(&c__7, &c__8, &l_mxind__, &l_x__, &l_y__, &w_grid__[1]);
	for (l_j__ = (int) ldexp(1.0, l_level__) - 1; l_j__ >= 2; --l_j__) {
	    l_y__ = ((l_j__ << 1) - 1) * l_lag__ + 1;
	    draw_node(&c__8, &c__10, &l_mxind__, &l_x__, &l_y__, &w_grid__[
		    1]);
	}
	l_y__ = l_lag__ + 1;
	draw_node(&c__9, &c__7, &l_mxind__, &l_x__, &l_y__, &w_grid__[1]);
	l_x__ = l_mxind__ - l_lag__;
	l_y__ = 1;
	draw_node(&c__10, &c__8, &l_mxind__, &l_x__, &l_y__, &w_grid__[1]);
	for (l_i__ = (int) ldexp(1.0, l_level__) - 1; l_i__ >= 2; --l_i__) {
	    l_x__ = ((l_i__ << 1) - 1) * l_lag__ + 1;
	    draw_node(&c__11, &c__10, &l_mxind__, &l_x__, &l_y__, &w_grid__[
		    1]);
	}
	l_x__ = l_lag__ + 1;
	draw_node(&c__12, &c__8, &l_mxind__, &l_x__, &l_y__, &w_grid__[1]);
    }
    i__1 = *i_ny__;
    for (l_y__ = 1; l_y__ <= i__1; ++l_y__) {
	i__2 = *i_nx__;
	for (l_x__ = 1; l_x__ <= i__2; ++l_x__) {
	    l_i__ = l_x__ + (l_y__ - 1) * l_mxind__;
	    o_grid__[l_x__ + l_y__ * o_grid_dim1] = w_grid__[l_i__];
	}
    }

    grid = o_grid__;
    grid += o_grid_offset;
    if(checkSimulatedVariance(grid,(*i_nx__),(*i_ny__))){
      moduleError(KERNEL,"draw2d_ss_3o",
		  "%s\n%s",
		  "Numerical problems in simulation of gaussian field.",
		  "Maybe too high correlation between neighbour nodes.");
    }

    return ;
} /* draw2d_ss_3o */



int SimGaussField2D:: init_weights_s(int *i_pattn__,
			  int *i_n__)
{
    /* System generated locals */
    int i__1, i__2;


    /* Local variables */
    static int l_wpivot__[30];
    static double l_vec__[30];
    static int l_dix__, l_diy__;
    static double l_wvec__[30], l_wmtx__[900]	/* was [30][30] */;
    static int l_i__, l_j__;
    static double l_r__;

    double rcond;
    double *w;


    w = (double *) calloc(*i_n__,sizeof(double));



    i__1 = *i_n__;
    for (l_i__ = 1; l_i__ <= i__1; ++l_i__) {
	l_wmtx__[l_i__ + l_i__ * 30 - 31] = (double)1.;
	l_dix__ = ss_cbl__1.c_patt__[*i_pattn__ + (l_i__ + 30) * 30 - 931];
	l_diy__ = ss_cbl__1.c_patt__[*i_pattn__ + (l_i__ + 60) * 30 - 931];
	l_wvec__[l_i__ - 1] = correl->corr(l_dix__, l_diy__);
	l_vec__[l_i__ - 1] = l_wvec__[l_i__ - 1];
	i__2 = *i_n__;
	for (l_j__ = l_i__ + 1; l_j__ <= i__2; ++l_j__) {
	    l_dix__ = ss_cbl__1.c_patt__[*i_pattn__ + (l_i__ + 30) * 30 - 931]
		     - ss_cbl__1.c_patt__[*i_pattn__ + (l_j__ + 30) * 30 -
		    931];
	    l_diy__ = ss_cbl__1.c_patt__[*i_pattn__ + (l_i__ + 60) * 30 - 931]
		     - ss_cbl__1.c_patt__[*i_pattn__ + (l_j__ + 60) * 30 -
		    931];
	    l_wmtx__[l_i__ + l_j__ * 30 - 31] =
	      correl->corr(l_dix__, l_diy__);
	    l_wmtx__[l_j__ + l_i__ * 30 - 31] = l_wmtx__[l_i__ + l_j__ * 30 -
		    31];
	}
    }
    if (*i_n__ > 0) {

	dgeco(l_wmtx__, &c__30, i_n__, l_wpivot__, &rcond,w);
	if(fabs(rcond) < EPS_COND){
	    moduleError(KERNEL,"init_weights_s",
			"%s\n%s\n%s\n%s",
			"Singular covariance matrix when simulating",
			"gaussian 2D field.",
			"Perhaps too large correlations between",
			"neighbouring grid nodes.");
	}
/*
	dgefa(l_wmtx__, &c__30, i_n__, l_wpivot__, &l_err__);
	if (l_err__ != 0) {
	    moduleError(KERNEL,"init_weights_s",
			"%s\n%s\n%s\n%s",
			"Singular covariance matrix when simulating",
			"gaussian 2D field.",
			"Perhaps too large correlations between",
			"neighbouring grid nodes.");
	}
*/

	dgesl(l_wmtx__, &c__30, i_n__, l_wpivot__, l_wvec__, &c__0);
    }
    l_r__ = (double)1.;
    i__1 = *i_n__;
    for (l_i__ = 1; l_i__ <= i__1; ++l_i__) {
	ss_cbl__1.c_weights__[*i_pattn__ + l_i__ * 30 - 31] = l_wvec__[l_i__
		- 1];
	l_r__ -= l_wvec__[l_i__ - 1] * l_vec__[l_i__ - 1];
    }
    ss_cbl__1.c_resvar__[*i_pattn__ - 1] = l_r__;
    if (ss_cbl__1.c_resvar__[*i_pattn__ - 1] < (double)0.) {
/*        PRINT *,C_RESVAR(I_PATTN),I_PATTN,I_N */
	ss_cbl__1.c_resvar__[*i_pattn__ - 1] = (double)0.;
/*        PRINT *,'NEGATIVE CONDITIONAL VARIANCE !!' */
/*        STOP */
    }


    free(w);


    return 0;
} /* init_weights_s */


int SimGaussField2D:: init_weights_o(int *i_pattn__,
				     int *i_n__)
{
    /* System generated locals */
    int i__1, i__2;

    /* Builtin functions */


    /* Local variables */
    static int l_wpivot__[31];
    static double l_vec__[30];
    static int l_dix__, l_diy__;
    static double l_wvec__[31], l_wmtx__[961]	/* was [31][31] */;
    static int l_i__, l_j__;
    static double l_r__;
    double rcond;
    double *w;


    w = (double *) calloc((*i_n__ + 1),sizeof(double));



    i__1 = *i_n__;
    for (l_i__ = 1; l_i__ <= i__1; ++l_i__) {
	l_wmtx__[l_i__ + l_i__ * 31 - 32] = (double)0.;
	l_dix__ = ss_cbl__1.c_patt__[*i_pattn__ + (l_i__ + 30) * 30 - 931];
	l_diy__ = ss_cbl__1.c_patt__[*i_pattn__ + (l_i__ + 60) * 30 - 931];
	l_wvec__[l_i__ - 1] = correl->corr(l_dix__, l_diy__);
	l_vec__[l_i__ - 1] = l_wvec__[l_i__ - 1];
	i__2 = *i_n__;
	for (l_j__ = l_i__ + 1; l_j__ <= i__2; ++l_j__) {
	    l_dix__ = ss_cbl__1.c_patt__[*i_pattn__ + (l_i__ + 30) * 30 - 931]
		     - ss_cbl__1.c_patt__[*i_pattn__ + (l_j__ + 30) * 30 -
		    931];
	    l_diy__ = ss_cbl__1.c_patt__[*i_pattn__ + (l_i__ + 60) * 30 - 931]
		     - ss_cbl__1.c_patt__[*i_pattn__ + (l_j__ + 60) * 30 -
		    931];
	    l_wmtx__[l_i__ + l_j__ * 31 - 32] =
	      correl->corr(l_dix__, l_diy__);
	    l_wmtx__[l_j__ + l_i__ * 31 - 32] = l_wmtx__[l_i__ + l_j__ * 31 -
		    32];
	}
    }
    l_wvec__[*i_n__] = (double)1.;
    l_wmtx__[*i_n__ + 1 + (*i_n__ + 1) * 31 - 32] = (double)0.;
    i__1 = *i_n__;
    for (l_i__ = 1; l_i__ <= i__1; ++l_i__) {
	l_wmtx__[l_i__ + (*i_n__ + 1) * 31 - 32] = (double)1.;
	l_wmtx__[*i_n__ + 1 + l_i__ * 31 - 32] = (double)1.;
    }
    if (*i_n__ > 0) {
	i__1 = *i_n__ + 1;


	dgeco(l_wmtx__, &c__31, &i__1, l_wpivot__, &rcond,w);
	if(fabs(rcond) < EPS_COND){
	    moduleError(KERNEL,"init_weights_o",
			"%s\n%s\n%s\n%s",
			"Singular covariance matrix when simulating",
			"gaussian 2D field.",
			"Perhaps too large correlations between",
			"neighbouring grid nodes.");
	}
/*
	dgefa(l_wmtx__, &c__31, &i__1, l_wpivot__, &l_err__);
	if (l_err__ != 0) {
	  moduleError(KERNEL,"init_weights_o",
		      "Singular covariance matrix");
	}
*/
	i__1 = *i_n__ + 1;
	dgesl(l_wmtx__, &c__31, &i__1, l_wpivot__, l_wvec__, &c__0);
    }
    l_r__ = (double)0.;
    i__1 = *i_n__;
    for (l_i__ = 1; l_i__ <= i__1; ++l_i__) {
	ss_cbl__1.c_weights__[*i_pattn__ + l_i__ * 30 - 31] = l_wvec__[l_i__
		- 1];
	l_r__ += l_wvec__[l_i__ - 1] * l_vec__[l_i__ - 1];
    }
    if (*i_n__ > 0) {
	l_r__ += l_wvec__[*i_n__];
    }
    ss_cbl__1.c_resvar__[*i_pattn__ - 1] = l_r__;
    if (ss_cbl__1.c_resvar__[*i_pattn__ - 1] < (double)0.) {
	ss_cbl__1.c_resvar__[*i_pattn__ - 1] = (double)0.;
    }

    free(w);

    return 0;
} /* init_weights_o */


int SimGaussField2D:: make_patt(int *i_pattn__,
				int *i_lag__,
				int *i_num__,
				int *i_dx__,
				int *i_dy__)
{
    ss_cbl__1.c_patt__[*i_pattn__ + (*i_num__ + 30) * 30 - 931] = *i_dx__ * *
	    i_lag__;
    ss_cbl__1.c_patt__[*i_pattn__ + (*i_num__ + 60) * 30 - 931] = *i_dy__ * *
	    i_lag__;
    return 0;
} /* make_patt  */



int SimGaussField2D:: draw_node(int *i_pattn__,
				int *i_n__,
				int *i_dim__,
				int *i_x__,
				int *i_y__,
				double *x_grid__)
{
    /* System generated locals */
    int x_grid_dim1, x_grid_offset, i__1;

    /* Local variables */
    static int l_i__;
    static double l_r__;
    static int l_x__, l_y__;



    /* Parameter adjustments */
    x_grid_dim1 = *i_dim__;
    x_grid_offset = x_grid_dim1 + 1;
    x_grid__ -= x_grid_offset;

    /* Function Body */
    l_x__ = *i_x__ + ss_cbl__1.c_patt__[*i_pattn__ - 1];
    l_y__ = *i_y__ + ss_cbl__1.c_patt__[*i_pattn__ + 899];
    l_r__ = x_grid__[l_x__ + l_y__ * x_grid_dim1] * ss_cbl__1.c_weights__[*
	    i_pattn__ - 1];
    i__1 = *i_n__;
    for (l_i__ = 2; l_i__ <= i__1; ++l_i__) {
	l_x__ = *i_x__ + ss_cbl__1.c_patt__[*i_pattn__ + (l_i__ + 30) * 30 -
		931];
	l_y__ = *i_y__ + ss_cbl__1.c_patt__[*i_pattn__ + (l_i__ + 60) * 30 -
		931];
	l_r__ += x_grid__[l_x__ + l_y__ * x_grid_dim1] *
		ss_cbl__1.c_weights__[*i_pattn__ + l_i__ * 30 - 31];
    }
    x_grid__[*i_x__ + *i_y__ * x_grid_dim1] = l_r__ + normal(&
	    ss_cbl__1.c_resvar__[*i_pattn__ - 1]);
    return 0;
} /* draw_node  */



/*FUNC: normal ***************************************************************

DESCRIPTION:

HOW TO USE THE FUNCTION:

SIDE-EFFECTS:

RETURN VALUE: a normal distributed value with variance equal to *var

******************************************************************************/
double SimGaussField2D:: normal(double *var) {
  static double r1,r2;
  static int refresh = 1;

  if (refresh) {
    normal01(r1,r2);
    refresh = 0;
    r1 *= sqrt(*var);
   return r1;
  }
  else {
    refresh = 1;
    r2 *= sqrt(*var);
    return r2;
  }
}



int SimGaussField2D:: inits_grid(int *i_dim__,
				 double *o_grid__)
{
    /* System generated locals */
    int o_grid_dim1, o_grid_offset, i__1;

    /* Local variables */
    static int l_dix__, l_diy__;
    static double l_cmtx__[625]	/* was [25][25] */;
    static int l_d__, l_i__, l_j__, l_k__, l_l__, l_m__, l_n__;
    static double l_r__, l_noise__[25];



    /* Parameter adjustments */
    o_grid_dim1 = *i_dim__;
    o_grid_offset = o_grid_dim1 + 1;
    o_grid__ -= o_grid_offset;

    /* Function Body */
    l_d__ = (*i_dim__ - 1) / 4;
    for (l_i__ = 1; l_i__ <= 25; ++l_i__) {
	l_noise__[l_i__ - 1] = normal(&c_b4482);
    }
    for (l_i__ = 1; l_i__ <= 5; ++l_i__) {
	for (l_j__ = 1; l_j__ <= 5; ++l_j__) {
	    l_k__ = l_j__ + (l_i__ - 1) * 5;
	    l_cmtx__[l_k__ + l_k__ * 25 - 26] = (double)1.;
	    i__1 = l_k__ - 1;
	    for (l_n__ = 1; l_n__ <= i__1; ++l_n__) {
		l_l__ = (l_n__ - 1) / 5 + 1;
		l_m__ = l_n__ - (l_l__ - 1) * 5;
		l_dix__ = (l_i__ - l_l__) * l_d__;
		l_diy__ = (l_j__ - l_m__) * l_d__;
		l_cmtx__[l_k__ + l_n__ * 25 - 26] =
		  correl->corr(l_dix__, l_diy__);
		l_cmtx__[l_n__ + l_k__ * 25 - 26] = l_cmtx__[l_k__ + l_n__ *
			25 - 26];
	    }
	}
    }
    cholesky_fact(&c__25, &c__25, l_cmtx__);
    for (l_i__ = 1; l_i__ <= 5; ++l_i__) {
	for (l_j__ = 1; l_j__ <= 5; ++l_j__) {
	    l_k__ = l_j__ + (l_i__ - 1) * 5;
	    l_r__ = (double)0.;
	    i__1 = l_k__;
	    for (l_l__ = 1; l_l__ <= i__1; ++l_l__) {
		l_r__ += l_cmtx__[l_k__ + l_l__ * 25 - 26] * l_noise__[l_l__
			- 1];
	    }
	    o_grid__[l_d__ * (l_i__ - 1) + 1 + (l_d__ * (l_j__ - 1) + 1) *
		    o_grid_dim1] = l_r__;
	}
    }
    return 0;
} /* inits_grid */


int SimGaussField2D:: inito_grid(int *i_dim__,
				 double *o_grid__)
{
    /* System generated locals */
    int o_grid_dim1, o_grid_offset, i__1, i__2;

    /* Local variables */
    static int l_dix__, l_diy__;
    static double l_cmtx__[625]	/* was [25][25] */;
    static double l_c__;
    static int l_d__, l_i__, l_j__, l_k__, l_l__, l_m__, l_n__;
    static double l_r__, l_noise__[25];



    /* Parameter adjustments */
    o_grid_dim1 = *i_dim__;
    o_grid_offset = o_grid_dim1 + 1;
    o_grid__ -= o_grid_offset;

    /* Function Body */
    i__1 = *i_dim__ - 1;
    i__2 = *i_dim__ - 1;
    l_c__ = correl->corr(i__1, i__2);
    l_d__ = (*i_dim__ - 1) / 4;
    for (l_i__ = 1; l_i__ <= 25; ++l_i__) {
	l_noise__[l_i__ - 1] = normal(&c_b4482);
    }
    for (l_i__ = 1; l_i__ <= 5; ++l_i__) {
	for (l_j__ = 1; l_j__ <= 5; ++l_j__) {
	    l_k__ = l_j__ + (l_i__ - 1) * 5;
	    l_cmtx__[l_k__ + l_k__ * 25 - 26] = l_c__;
	    i__1 = l_k__ - 1;
	    for (l_n__ = 1; l_n__ <= i__1; ++l_n__) {
		l_l__ = (l_n__ - 1) / 5 + 1;
		l_m__ = l_n__ - (l_l__ - 1) * 5;
		l_dix__ = (l_i__ - l_l__) * l_d__;
		l_diy__ = (l_j__ - l_m__) * l_d__;
		l_cmtx__[l_k__ + l_n__ * 25 - 26] = l_c__ -
		  correl->corr(l_dix__,l_diy__);
		l_cmtx__[l_n__ + l_k__ * 25 - 26] = l_cmtx__[l_k__ + l_n__ *
			25 - 26];
	    }
	}
    }
    cholesky_fact(&c__25, &c__25, l_cmtx__);
    for (l_i__ = 1; l_i__ <= 5; ++l_i__) {
	for (l_j__ = 1; l_j__ <= 5; ++l_j__) {
	    l_k__ = l_j__ + (l_i__ - 1) * 5;
	    l_r__ = (double)0.;
	    i__1 = l_k__;
	    for (l_l__ = 1; l_l__ <= i__1; ++l_l__) {
		l_r__ += l_cmtx__[l_k__ + l_l__ * 25 - 26] * l_noise__[l_l__
			- 1];
	    }
	    o_grid__[l_d__ * (l_i__ - 1) + 1 + (l_d__ * (l_j__ - 1) + 1) *
		    o_grid_dim1] = l_r__;
	}
    }
    return 0;
} /* inito_grid */


int SimGaussField2D::init_c_patt()
{
    static int l_i__, l_j__;

    for (l_i__ = 1; l_i__ <= 30; ++l_i__) {
	for (l_j__ = 1; l_j__ <= 30; ++l_j__) {
	    ss_cbl__1.c_patt__[l_i__ + (l_j__ + 30) * 30 - 931] = 0;
	    ss_cbl__1.c_patt__[l_i__ + (l_j__ + 60) * 30 - 931] = 0;
	}
    }
    return 0;
} /* init_c_patt */


#define TOLERANCE_SDEV  5.0
#define TOLERANCE_MEAN  5.0

/*F:checkSimulatedVariance*

________________________________________________________________

		checkSimulatedVariance
________________________________________________________________

Name:		checkSimulatedVariance
Syntax:		@checkSimulatedVariance-syntax
Description:  Calculates the variance over all grid blocks
              in a 2D grid.
Side effects:
Return value: 0 OK, 1 error NaN in grid.
Global or static variables used:
________________________________________________________________

*/

/*<checkSimulatedVariance-syntax: */
int SimGaussField2D::checkSimulatedVariance(float *grid, int nx, int ny)
/*>checkSimulatedVariance-syntax: */
{

  int i;
  double var,mean,d,value;

  mean = grid[0];
  var = 0.0;
  for(i=1;i< nx*ny;i++){
    value = grid[i];
//    if(!finite(value))return 1;
    d = value - mean;
    var  = (i-1)*var/((double)i) + (d*d)/((double)(i+1));
    mean = mean + d/((double) (i+1));
  }
  if(fabs(mean)>TOLERANCE_MEAN){
    moduleWarning(CHECK,"checkSimulatedVariance",
		  "%s\n%s %f %s %f\n%s",
		  "The unconditional simulated gaussian",
		  "field has mean value ",mean," > ",TOLERANCE_MEAN,
		  "Should have been close to 0.0");
  }
  var = sqrt(var);
  if(fabs(var) > TOLERANCE_SDEV){
    moduleWarning(CHECK,"checkSimulatedVariance",
		  "%s\n%s %f %s %f\n%s",
		  "The unconditional simulated gaussian",
		  "field has standard deviation ",var,
		  " > ",TOLERANCE_SDEV,
		  "Should have been close to 1.0");
  }
  return 0;
}	/* end of checkSimulatedVariance */




SimGaussField2D:: SimGaussField2D(SimGaussField2D &simGF)
{
   correl = simGF.correl;
}





