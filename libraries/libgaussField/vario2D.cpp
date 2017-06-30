//
// PURPOSE
//
// SPECIAL INSTRUCTIONS & NOTES
//
//

#include <cassert>
#include <cstdlib>
#include <cmath>
#include "vario2D.h"
#include "rms/global_def.h"



//
// FUNCTION 
//
// PURPOSE
// Vario2D class constructor.
//
// RETURN VALUE
//
// SIDE EFFECTS
//
// SPECIAL INSTRUCTIONS & NOTES
//             
Vario2D::Vario2D(const double range1,
		 const double range2, 
		 const double ang,
		 const double si)
{
    assert(!(si <= 0.0));
    assert(!(range1 <= 0.0));
    assert(!(range2 <= 0.0));
	
    range =  range1;
    subRange = range2;
    angle = ang;
    sill = si;
    transformed = 0;

    corrFactors();
}



//
// FUNCTION 
//
// PURPOSE
// Vario2D class destructor.
//
// RETURN VALUE
//
// SIDE EFFECTS
//
// SPECIAL INSTRUCTIONS & NOTES
//             
Vario2D::~Vario2D()
{
}



//
// FUNCTION : Vario2D::vario
//
// PURPOSE
//
// RETURN VALUE 
// Value of variogram for given distance
//
// SIDE EFFECTS 
// 
// SPECIAL INSTRUCTIONS & NOTES
//
double 
Vario2D::vario(const double dx,
		      const double dy) const
{
    	return sill * (1 - corr(dx, dy));
}



//
// FUNCTION : Vario2D::corrFactors
//
// PURPOSE
// Compute anisotrophy factors txx, tyy and txy when rotation of
// the anisotropy ellipsis is taken into account. An explicit call
// to this function is not necessary. It is called implicitly in
// the constructor. If however the length scale is changed this
// function must be called again like in the
// correlationTransf and correlationInvTransf
//
// RETURN VALUE
// void
//
// SIDE EFFECTS 
//
// SPECIAL INSTRUCTIONS & NOTES
//             
void 
Vario2D::corrFactors(void)
{
    	double cosRot;
    	double sinRot;  
    	double fac1;
    	double fac2;     

    	cosRot = cos(angle);
    	sinRot = sin(angle);
    	fac1 = 1.0/(range * range);
    	fac2 = 1.0/(subRange * subRange);

    	txx = cosRot*cosRot*fac1 + sinRot*sinRot*fac2;
    	tyy = sinRot*sinRot*fac1 + cosRot*cosRot*fac2;
    	txy = 2*cosRot*sinRot*(fac1 - fac2);

    	return;
}



//
// FUNCTION : ExpVario2D::ExpVario2D
//
// PURPOSE
// ExpVario2D class constructor.
//
// RETURN VALUE
//
// SIDE EFFECTS
//
// SPECIAL INSTRUCTIONS & NOTES
//             
ExpVario2D::ExpVario2D(const double range1,
		       const double range2,
		       const double ang,
		       const double si) :
    Vario2D(range1, range2, ang, si)
{
}



//
// FUNCTION : ExpVario2D::~ExpVario2D
//
// PURPOSE
// ExpVario2D class destructor.
//
// RETURN VALUE
//
// SIDE EFFECTS
//
// SPECIAL INSTRUCTIONS & NOTES
//             
ExpVario2D::~ExpVario2D()
{
}



//
// FUNCTION : ExpVario2D::corr
//
// PURPOSE
// To find the correlation between two points with distance dx and dy
// for an exponential variogram function.
//
// RETURN VALUE
// The correlation.
//
// SIDE EFFECTS
//
// SPECIAL INSTRUCTIONS & NOTES
// There exists two overloaded versions,
// one with "int" and one with "double" input parameters.
//             
double 
ExpVario2D::corr(	const double dx,
			const double dy) const
{
    	double dist = corrDistance(dx,dy);
    	return exp(- 3.0 * dist); 
}

double 
ExpVario2D::corr(	const int dx,
			const int dy) const
{
  	double dist = corrDistance(dx,dy);
  	return exp(- 3.0 * dist); 
}

//
// FUNCTION: ExpVario2D::write
//
// PURPOSE: Write type and parameters to file
//
void 
ExpVario2D::write(FILE* file)const
{
    fprintf(file,"%s ", "exponential");
    writeRange(file);
    fprintf(file,"\n");
    return;
} 


//
// FUNCTION 
//
// PURPOSE
//
// RETURN VALUE
//
// SIDE EFFECTS
//
// SPECIAL INSTRUCTIONS & NOTES
//

VarioType
ExpVario2D::getType(void) const
{
	return(exponential);
}             

//
// FUNCTION : SphVario2D::SphVario2D
//
// PURPOSE
// SphVario2D class constructor.
//
// RETURN VALUE
//
// SIDE EFFECTS
//
// SPECIAL INSTRUCTIONS & NOTES
//             
SphVario2D::SphVario2D(const double range1,
		       const double range2,
		       const double ang, 
		       const double si) : 
    Vario2D(range1, range2, ang, si)
{
}



//
// FUNCTION : SphVario2D::~SphVario2D
//
// PURPOSE
// SphVario2D class destructor.
//
// RETURN VALUE
//
// SIDE EFFECTS
//
// SPECIAL INSTRUCTIONS & NOTES
//             
SphVario2D::~SphVario2D()
{
}



//
// FUNCTION SphVario2D::corr
//
// PURPOSE
// To find the correlation between two points for a 3-dimensional
// spherical variogram function.
//
// RETURN VALUE
// The correlation.
//
// SIDE EFFECTS
//
// SPECIAL INSTRUCTIONS & NOTES
// There exists two overloaded versions,
// one with "int" and one with "double" input parameters.
//             
double 
SphVario2D::corr(	const double dx,
			const double dy) const
{
    double dist = corrDistance(dx,dy);

    if(dist < 1.0)
    {
	return (1.0 - dist * (1.5 - (0.5*dist*dist)));
    }
    else
    {
	return 0.0;
    }
}

double 
SphVario2D::corr(	const int dx,
			const int dy) const
{
  double dist = corrDistance(dx,dy);
  if(dist < 1.0){
      return (1.0 - dist * (1.5 - (0.5*dist*dist)));
  }
  else {
      return 0.0;
  }
}

//
// FUNCTION: SphVario2D::write
//
// PURPOSE: Write type and parameters to file
//
void 
SphVario2D::write(FILE* file)const
{
    fprintf(file,"%s ", "spherical");
    writeRange(file);
    fprintf(file,"\n");
    return;
} 

//
// FUNCTION 
//
// PURPOSE
//
// RETURN VALUE
//
// SIDE EFFECTS
//
// SPECIAL INSTRUCTIONS & NOTES
//

VarioType
SphVario2D::getType(void) const
{
	return(spherical);
}             

//
// FUNCTION : GauVario2D::GauVario2D
//
// PURPOSE
// GauVario2D class constructor.
//
// RETURN VALUE
//
// SIDE EFFECTS
//
// SPECIAL INSTRUCTIONS & NOTES
//             
GauVario2D::GauVario2D(const double range1,
		       const double range2,
		       const double ang, 
		       const double si) : 
    Vario2D(range1, range2, ang, si)
{
}



//
// FUNCTION : GauVario2D::~GauVario2D
//
// PURPOSE
// GauVario2D class destructor.
//
// RETURN VALUE
//
// SIDE EFFECTS
//
// SPECIAL INSTRUCTIONS & NOTES
//             
GauVario2D::~GauVario2D()
{
}



//
// FUNCTION : GauVario2D::corr
//
// PURPOSE
// To find the correlation between two points with distance dx and dy
// for an Gaussian variogram function.
//
// RETURN VALUE
// The correlation.
//
// SIDE EFFECTS
//
// SPECIAL INSTRUCTIONS & NOTES
// There exists two overloaded versions,
// one with "int" and one with "double" input parameters.
//             
double 
GauVario2D::corr(	const double dx,
			const double dy) const
{
    double dist = corrDistance(dx,dy);
    return exp(- 3.0 * dist*dist); 
}

double 
GauVario2D::corr(	const int dx,
			const int dy) const
{
  double dist = corrDistance(dx,dy);
  return exp(- 3.0 * dist*dist);
}

//
// FUNCTION: GauVario2D::write
//
// PURPOSE: Write type and parameters to file
//
void 
GauVario2D::write(FILE* file)const
{
    fprintf(file,"%s ", "gaussian");
    writeRange(file);
    fprintf(file,"\n");
    return;
} 

//
// FUNCTION 
//
// PURPOSE
//
// RETURN VALUE
//
// SIDE EFFECTS
//
// SPECIAL INSTRUCTIONS & NOTES
//

VarioType
GauVario2D::getType(void) const
{
	return(gaussian);
}             

//
// FUNCTION : GenExpVario2D::GenExpVario2D
//
// PURPOSE
// GenExpVario2D class constructor.
//
// RETURN VALUE
//
// SIDE EFFECTS
//
// SPECIAL INSTRUCTIONS & NOTES
//             
GenExpVario2D::GenExpVario2D(const double range1,
			     const double range2,
			     const double ang, 
			     const double si,
			     const double po) : 
    Vario2D(range1, range2, ang, si)
{
    assert((po > 0.00)&&(po <= 2.00));
    power = po;
}



//
// FUNCTION : GenExpVario2D::~GenExpVario2D
//
// PURPOSE
// GenExpVario2D class destructor.
//
// RETURN VALUE
//
// SIDE EFFECTS
//
// SPECIAL INSTRUCTIONS & NOTES
//             
GenExpVario2D::~GenExpVario2D()
{
}



//
// FUNCTION : GenExpVario2D::corr
//
// PURPOSE
// To find the correlation between two points with distance dx and dy
// for an general exponential variogram function.
//
// RETURN VALUE
// The correlation.
//
// SIDE EFFECTS
//
// SPECIAL INSTRUCTIONS & NOTES
// There exists two overloaded versions,
// one with "int" and one with "double" input parameters.
// The power of the variogram function must be set in the constructor.
//             
double 
GenExpVario2D::corr(	const double dx,
			const double dy) const
{
    double dist = corrDistance(dx,dy);
    return exp(-3.0 * pow(dist,power));
}

double 
GenExpVario2D::corr(	const int dx,
			const int dy) const
{
    double dist = corrDistance(dx,dy);
    return exp(-3.0 * pow(dist,power));
}

//
// FUNCTION: GenExpVario2D::write
//
// PURPOSE: Write type and parameters to file
//
void 
GenExpVario2D::write(FILE* file)const
{
    fprintf(file,"%s ", "general exponential");
    writeRange(file);
    fprintf(file," %f ",power);
    fprintf(file,"\n");
    return;
} 

//
// FUNCTION 
//
// PURPOSE
//
// RETURN VALUE
//
// SIDE EFFECTS
//
// SPECIAL INSTRUCTIONS & NOTES
//

VarioType
GenExpVario2D::getType(void) const
{
	return(general_exponential);
}             

//
// FUNCTION : RatQuadVario2D::RatQuadVario2D
//
// PURPOSE
// RatQuadVario2D class constructor.
//
// RETURN VALUE
//
// SIDE EFFECTS
//
// SPECIAL INSTRUCTIONS & NOTES
//             
RatQuadVario2D::RatQuadVario2D(const double range1,
			       const double range2,
			       const double ang, 
			       const double si,
			       const double po) : 
    Vario2D(range1, range2, ang, si)
{
    assert(po > 0.00);
    power = po;
}



//
// FUNCTION : RatQuadVario2D::~RatQuadVario2D
//
// PURPOSE
// RatQuadVario2D class destructor.
//
// RETURN VALUE
//
// SIDE EFFECTS
//
// SPECIAL INSTRUCTIONS & NOTES
//             
RatQuadVario2D::~RatQuadVario2D()
{
}



//
// FUNCTION : RatQuadVario2D::corr
//
// PURPOSE
// To find the correlation between two points with distance dx and dy
// for a rational quadratic variogram function.
//
// RETURN VALUE
// The correlation.
//
// SIDE EFFECTS
//
// SPECIAL INSTRUCTIONS & NOTES
// There exists two overloaded versions,
// one with "int" and one with "double" input parameters.
// The power of the variogram function must be set in the constructor.
//             
double 
RatQuadVario2D::corr(	const double dx,
			const double dy) const
{
    double dist = corrDistance(dx,dy);
    double scal = pow(20.0,(1.0/power)) - 1.0;
    return 1.0/pow(1.0 + scal*dist*dist,power);
}

double 
RatQuadVario2D::corr(	const int dx,
			const int dy) const
{
    double dist = corrDistance(dx,dy);
    double scal = pow(20.0,(1.0/power)) - 1.0;
    return 1.0/pow(1.0 + scal*dist*dist,power);
}
 
//
// FUNCTION: RatQuadVario2D::write
//
// PURPOSE: Write type and parameters to file
//
void 
RatQuadVario2D::write(FILE* file)const
{
    fprintf(file,"%s ", "rational quadratic");
    writeRange(file);
    fprintf(file," %f ",power);
    fprintf(file,"\n");
    return;
} 

//
// FUNCTION 
//
// PURPOSE
//
// RETURN VALUE
//
// SIDE EFFECTS
//
// SPECIAL INSTRUCTIONS & NOTES
//

VarioType
RatQuadVario2D::getType(void) const
{
	return(ratquad);
}      

//
// FUNCTION : WhiteVario2D::WhiteVario2D
//
// PURPOSE
// WhiteVario2D class constructor.
//
// RETURN VALUE
//
// SIDE EFFECTS
//
// SPECIAL INSTRUCTIONS & NOTES
//             
WhiteVario2D::WhiteVario2D(const double range1,
			   const double range2,
			   const double ang, 
			   const double si) : 
    Vario2D(range1, range2, ang, si)
{
    TOL = 0.000001;
}



//
// FUNCTION : WhiteVario2D::~WhiteVario2D
//
// PURPOSE
// WhiteVario2D class destructor.
//
// RETURN VALUE
//
// SIDE EFFECTS
//
// SPECIAL INSTRUCTIONS & NOTES
//             
WhiteVario2D::~WhiteVario2D()
{
}



//
// FUNCTION : WhiteVario2D::corr
//
// PURPOSE
// To find the correlation between two points with distance dx and dy
// for a white noise variogram function.
//
// RETURN VALUE
// The correlation.
//
// SIDE EFFECTS
//
// SPECIAL INSTRUCTIONS & NOTES
// There exists two overloaded versions,
// one with "int" and one with "double" input parameters.
//
double 
WhiteVario2D::corr(	const double dx,
			const double dy) const
{
    if(isZero(dx,TOL) && isZero(dy,TOL))
	return 1.0;
    else
	return 0.0;
} 

double 
WhiteVario2D::corr(	const int dx,
			const int dy) const
{
    if(dx == 0 && dy == 0)
	return 1.0;
    else
	return 0.0;
} 
 
//
// FUNCTION: WhiteVario2D::write
//
// PURPOSE: Write type and parameters to file
//
void
WhiteVario2D::write(FILE* file)const
{
    fprintf(file,"%s ", "white noise");
    writeRange(file);
    fprintf(file,"\n");
    return;
} 

//
// FUNCTION 
//
// PURPOSE
//
// RETURN VALUE
//
// SIDE EFFECTS
//
// SPECIAL INSTRUCTIONS & NOTES
//

VarioType
WhiteVario2D::getType(void) const
{
	return(whitenoise);
}      

//
// FUNCTION : Sph2Vario2D::Sph2Vario2D
//
// PURPOSE
// Sph2Vario2D class constructor.
//
// RETURN VALUE
//
// SIDE EFFECTS
//
// SPECIAL INSTRUCTIONS & NOTES
//             
Sph2Vario2D::Sph2Vario2D(const double range1,
			 const double range2,
			 const double ang, 
			 const double si) : 
    Vario2D(range1, range2, ang, si)
{
}



//
// FUNCTION : Sph2Vario2D::~Sph2Vario2D
//
// PURPOSE
// Sph2Vario2D class destructor.
//
// RETURN VALUE
//
// SIDE EFFECTS
//
// SPECIAL INSTRUCTIONS & NOTES
//             
Sph2Vario2D::~Sph2Vario2D()
{
}



//
// FUNCTION: Sph2Vario2D::corr
//
// PURPOSE
// To find the correlation between two points for a 2-dimensional
// spherical variogram function.
//
// RETURN VALUE
// The correlation.
//
// SIDE EFFECTS
//
// SPECIAL INSTRUCTIONS & NOTES
// There exists two overloaded versions,
// one with "int" and one with "double" input parameters.
//
double 
Sph2Vario2D::corr(	const double dx,
			const double dy) const
{
  double dist = corrDistance(dx,dy);

  if(dist < 1.0)
      return 1.0 - 2.0 * (dist*sqrt(1.0 - dist*dist) + asin(dist))/PI;
  else
      return 0.0;
}	/* end of Sph2Vario2D::corr */

double 
Sph2Vario2D::corr(	const int dx,
			const int dy) const
{
  double dist = corrDistance(dx,dy);

  if(dist < 1.0)
      return 1.0 - 2.0 * (dist*sqrt(1.0 - dist*dist) + asin(dist))/PI;
  else
      return 0.0;
}	/* end of Sph2Vario2D::corr */

//
// FUNCTION: Sph2Vario2D::write
//
// PURPOSE: Write type and parameters to file
//
void 
Sph2Vario2D::write(FILE* file)const
{
    fprintf(file,"%s ", "spherical2");
    writeRange(file);
    fprintf(file,"\n");
    return;
} 

//
// FUNCTION 
//
// PURPOSE
//
// RETURN VALUE
//
// SIDE EFFECTS
//
// SPECIAL INSTRUCTIONS & NOTES
//

VarioType
Sph2Vario2D::getType(void) const
{
	return(spherical2);
}      

//
// FUNCTION : Sph5Vario2D::Sph5Vario2D
//
// PURPOSE
// Sph5Vario2D class constructor.
//
// RETURN VALUE
//
// SIDE EFFECTS
//
// SPECIAL INSTRUCTIONS & NOTES
//             
Sph5Vario2D::Sph5Vario2D(const double range1,
			 const double range2,
			 const double ang, 
			 const double si) : 
    Vario2D(range1, range2, ang, si)
{
}



//
// FUNCTION : Sph5Vario2D::~Sph5Vario2D
//
// PURPOSE
// Sph5Vario2D class destructor.
//
// RETURN VALUE
//
// SIDE EFFECTS
//
// SPECIAL INSTRUCTIONS & NOTES
//             
Sph5Vario2D::~Sph5Vario2D()
{
}



//
// FUNCTION: Sph5Vario2D::corr
//
// PURPOSE
// To find the correlation between two points for a 5-dimensional
// spherical variogram function.
//
// RETURN VALUE
// The correlation.
//
// SIDE EFFECTS
//
// SPECIAL INSTRUCTIONS & NOTES
// There exists two overloaded versions,
// one with "int" and one with "double" input parameters.
//
double 
Sph5Vario2D::corr(	const double dx,
			const double dy) const
{
  double dist = corrDistance(dx,dy);

  if(dist < 1.0)
      return 1.0 - dist * (1.875 - dist*dist * (1.25 - 0.375*dist*dist));
  else
      return 0.0;
} 

double 
Sph5Vario2D::corr(	const int dx,
			const int dy) const
{
  double dist = corrDistance(dx,dy);

  if(dist < 1.0)
      return 1.0 - dist * (1.875 - dist*dist * (1.25 - 0.375*dist*dist));
  else
      return 0.0;
} 

//
// FUNCTION: Sph5Vario2D::write
//
// PURPOSE: Write type and parameters to file
//
void 
Sph5Vario2D::write(FILE* file)const
{
    fprintf(file,"%s ", "spherical5");
    writeRange(file);
    fprintf(file,"\n");
    return;
} 

//
// FUNCTION 
//
// PURPOSE
//
// RETURN VALUE
//
// SIDE EFFECTS
//
// SPECIAL INSTRUCTIONS & NOTES
//

VarioType
Sph5Vario2D::getType(void) const
{
	return(spherical5);
}      

//
// FUNCTION: WhiteVario2D::isZero
//
// PURPOSE
// Tests wheter a double-value is sufficiently close
// to zero to declare it to be zero.
//
// RETURN VALUE
// True:"1" or false:"0".
//
// SIDE EFFECTS
//
// SPECIAL INSTRUCTIONS & NOTES
//
int 
WhiteVario2D::isZero(const double dist,
			 const double tol) const
{
    if( -tol < dist && dist < tol)
	return 1;
    else
	return 0;
} 



//
// FUNCTION: Vario2D::correlationTransf
//
// PURPOSE 
// Transform the local parameters for range into 
// rectangular box (0,nx, 0,ny) from (0,xsize,0,ysize).
// Calls the function corrFactors for calculating
// some local variables.
//
// RETURN VALUE
// void
//
// SIDE EFFECTS
//
// SPECIAL INSTRUCTIONS & NOTES
//
void 
Vario2D::correlationTransf(int nx, int ny, 
				double xsize, double ysize) 
{ 
	if(!transformed)
	{
		range *= ((double) nx) / xsize;
		subRange *= ((double) ny) / ysize;
		corrFactors();
		transformed = 1;
   	}	
}



//
// FUNCTION: Vario2D::correlationInvTransf
//
// PURPOSE
// Transform the parameters for range from
// rectangular box (0,nx, 0,ny) to (0,xsize,0,ysize).
// Calls the function corrFactors for calculating
// some local variables.
//
// RETURN VALUE
// void
//
// SIDE EFFECTS
//
// SPECIAL INSTRUCTIONS & NOTES
//
void 
Vario2D::correlationInvTransf(int nx, int ny, 
				   double xsize, double ysize) 
{
 	if(transformed)
	{
		range *= xsize/((double) nx);
		subRange *= ysize/((double) ny);
		corrFactors();
		transformed = 0;
    	}
}

Vario2D::Vario2D(Vario2D &vario2D)
{
   range = vario2D.range;
   subRange = vario2D.subRange;
   angle = vario2D.angle;
   sill = vario2D.sill;
   txx = vario2D.txx;
   tyy = vario2D.tyy;
   txy = vario2D.txy;
   transformed  = vario2D.transformed;
}











