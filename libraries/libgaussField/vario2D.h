// PURPOSE
//
// - Declare the pure abstract Vario2D base class and its derived classes: 
//    ExpVario2D, SphVario2D, GauVario2D, RatQuadVario2D, Sph2Vario2D,
//    Sph5Vario2D and WhiteVario2D.
// - Declare the NestedVario2D class.
//
// SPECIAL INSTRUCTIONS & NOTES
//
//

#ifndef VARIO2D_H
#define VARIO2D_H

#define DEFAULT_ANGLE  0.0
#define DEFAULT_SILL   1.0
#define DEFAULT_POWER  1.0


#include <cmath>
#include <iostream>
#include <cstdio>
class Vario2D;
enum VarioType {exponential, spherical, gaussian, general_exponential,
		ratquad, spherical2, spherical5, whitenoise};




class Vario2D
{
    	public:

    				Vario2D(const double range1,
	    				const double range2,
	    				const double ang = DEFAULT_ANGLE,
	    				const double si = DEFAULT_SILL);
                                Vario2D(Vario2D &vario2D);
    		virtual 	~Vario2D(); 
    		virtual double 	corr(const double dx, const double dy) const = 0;
    		virtual double 	corr(const    int dx, const    int dy) const = 0;
    		double	 	vario(const double dx, const double dy) const;
    		virtual void	write(FILE * file) const = 0;
		inline double 	corrDistance(const double dx, const double dy) const;
    		inline double 	corrDistance(const    int dx, const    int dy) const;
    		inline double 	getRange(void) const;
    		inline double 	getSubRange(void) const;
    		inline double 	getAngle(void) const ;
    		void 		correlationTransf(int nx, int ny, 
			   			double xsize, double ysize);
    		void 		correlationInvTransf(int nx, int ny, 
			      			double xsize, double ysize);
		virtual VarioType getType(void) const = 0;
		virtual double	getPower(void) const = 0;

	protected:
		inline void	writeRange(FILE* file) const;

    	private:
  
    		double 		range;
    		double 		subRange;
    		double 		angle;
    		double 		sill;
    		double		txx;
    		double		tyy;
    		double		txy;
		int		transformed;
    		void		corrFactors();
};


class ExpVario2D : public Vario2D
{
    	public: 
    				ExpVario2D(const double range1,
	       				const double range2,
	       				const double ang = DEFAULT_ANGLE, 
	       				const double si = DEFAULT_SILL);
    				~ExpVario2D();
    		double 		corr(const double dx, const double dy) const;
    		double 		corr(const int    dx, const int    dy) const;
		VarioType 	getType(void) const;
                double		getPower(void) const {std::cout << "Error calling getPower\n"; return(0);}
		void            write(FILE* file) const;
};	

class SphVario2D : public Vario2D
{
    	public:
    				SphVario2D(const double range1,
	       				const double range2,
	       				const double ang = DEFAULT_ANGLE, 
	       				const double si = DEFAULT_SILL);
    				~SphVario2D();
    		double 		corr(const double dx, const double dy) const;
    		double 		corr(const    int dx, const    int dy) const;
          	VarioType 	getType(void) const;
                double		getPower(void) const {std::cout << "Error calling getPower\n";return(0);}
                void            write(FILE* file) const;
};

class GauVario2D : public Vario2D
{
    	public:
    				GauVario2D(const double range1,
	       				const double range2,
	       				const double ang = DEFAULT_ANGLE, 
	       				const double si = DEFAULT_SILL);
    				~GauVario2D();
    		double 		corr(const double dx, const double dy) const;
    		double 		corr(const    int dx, const    int dy) const;
       		VarioType 	getType(void) const;
                double		getPower(void) const {std::cout << "Error calling getPower\n";return(0);}
		void            write(FILE* file) const;
};                                                      

class GenExpVario2D : public Vario2D
{
    	public: 
    				GenExpVario2D(	const double range1, 
		  			const double range2, 
		 			const double ang = DEFAULT_ANGLE,
		  			const double si = DEFAULT_SILL,
		  			const double po = DEFAULT_POWER);
    				~GenExpVario2D();
    		double 		corr(const double dx, const double dy) const;
    		double 		corr(const    int dx, const    int dy) const;
    		VarioType 	getType(void) const;
		double		getPower(void) const {return(power);} 
                void            write(FILE* file) const;
    private:
    		double		power;
};	

class RatQuadVario2D : public Vario2D
{
    	public: 
    				RatQuadVario2D(const double range1, 
		   			const double range2, 
		   			const double ang = DEFAULT_ANGLE,
		   			const double si = DEFAULT_SILL,
		   			const double po = DEFAULT_POWER);
    				~RatQuadVario2D();
    		double 		corr(const double dx, const double dy) const;
    		double 		corr(const    int dx, const    int dy) const;
    		VarioType 	getType(void) const;
		double		getPower(void) const {return(power);}
                void            write(FILE* file) const;
    private:
    		double		power;
};


class Sph2Vario2D : public Vario2D
{
    public:
    				Sph2Vario2D(const double range1,
					const double range2,
					const double ang = DEFAULT_ANGLE, 
					const double si = DEFAULT_SILL);
    				~Sph2Vario2D();
    		double 		corr(const double dx, const double dy) const;
    		double 		corr(const    int dx, const    int dy) const;
    		VarioType 	getType(void) const;
                double		getPower(void) const {std::cout << "Error calling getPower\n";return(0);}
                void            write(FILE* file) const;
};

class Sph5Vario2D : public Vario2D
{
    public:
    				Sph5Vario2D(const double range1,
	       				const double range2,
	       				const double ang = DEFAULT_ANGLE, 
	       				const double si = DEFAULT_SILL);
    				~Sph5Vario2D();
    		double 		corr(const double dx, const double dy) const;
    		double 		corr(const    int dx, const    int dy) const;
    		VarioType 	getType(void) const;
                double		getPower(void) const {std::cout << "Error calling getPower\n";return(0);}
		void            write(FILE* file) const;

};


class WhiteVario2D : public Vario2D
{
    public:
    				WhiteVario2D(const double range1,
	       				const double range2,
	       				const double ang = DEFAULT_ANGLE, 
	       				const double si = DEFAULT_SILL);
    				~WhiteVario2D();
   		double 		corr(const double dx, const double dy) const;
    		double 		corr(const    int dx, const    int dy) const;
    		VarioType 	getType(void) const;
                double		getPower(void) const {std::cout << "Error calling getPower\n";return(0);}
		void            write(FILE* file) const;
    private:
    		double TOL;
    		int 		isZero(const double ,const double ) const;
};



//
// FUNCTION : corrDistance  
//
// PURPOSE
//
// Compute normalized distance between to points
// with interdistance dx, dy. Anisotrophy factors and
// rotation of the anisotrophy ellipsis is taken into
// account. For double and int variables
//
// RETURN VALUE
//
// SIDE EFFECTS 
// 
//
// SPECIAL INSTRUCTIONS & NOTES There exists two overloaded versions,
//       one for grid node inputs (int) and one for general input (double)
//             

inline double 
Vario2D::corrDistance(	const double dx,
			const double dy) const
{
    	return sqrt(txx*dx*dx + tyy*dy*dy + txy*dx*dy);
} 

inline double 
Vario2D::corrDistance(	const int dx,
			const int dy) const 
{
    	return  sqrt(txx*dx*dx + tyy*dy*dy + txy*dx*dy);
} 


//
// FUNCTION: Vario2D::getAngle
//
// PURPOSE: 
// To return the angle value.
//
// RETURN VALUE: 
// angle
//
// SIDE EFFECTS: 
//
// SPECIAL INSTRUCTIONS & NOTES: 
//
inline double 
Vario2D::getAngle(void) const 
{
    	return angle;
} 



//
// FUNCTION: Vario2D::getRange
//
// PURPOSE: 
// To return the range value.
//
// RETURN VALUE: 
// range
//
// SIDE EFFECTS: 
//
// SPECIAL INSTRUCTIONS & NOTES: 
//
inline  double 
Vario2D::getRange(void) const
{
    	return range;
} 

//
// FUNCTION: Vario2D::getSubRange
//
// PURPOSE
// To return the subRange value.
//
// RETURN VALUE
// subRange
//
// SIDE EFFECTS: 
//
// SPECIAL INSTRUCTIONS & NOTES: 
//
inline  double 
Vario2D::getSubRange(void) const
{
    	return subRange;
} 

//
// FUNCTION: Vario2D::writeRange
//
// PURPOSE: Write type and range parameters to file
//
// RETURN VALUE
//
// SIDE EFFECTS: 
//
// SPECIAL INSTRUCTIONS & NOTES: 
//
inline void 
Vario2D::writeRange(FILE* file)const
{
    	fprintf(file," %f %f %f ",
	    range,subRange,angle);
    	return;
} 

#endif
