#include "simGauss2D.h"
#include "lib_message.h"

#include "draw2DGaussField.h"
#include <iostream>
#include "global_def.h"
using namespace std;
float * draw2DGaussField(int nx, int ny, double xsize, double ysize,
                         int type,unsigned int iseed,
                         double range1,double range2,double angle,double power,int debugPrint)
{
        if (debugPrint == 1)
        {       
                cout << "nx: " << nx << endl
                << "ny: " << ny << endl
                << "xsize: " << xsize << endl
                << "ysize: " << ysize << endl
                << "type: " << type << endl
                << "seed: " << iseed << endl      
                << "range1: " << range1 << endl      
                << "range2: " << range2 << endl      
                << "power: " << power << endl      
                << "angle in degree: " << angle << endl;      
        }
        angle = angle*PI/180.0; // In radians

        RandomGenerator ran(iseed);
        SimGaussField2D sim2D(ran);
        Vario2D *vario;
        if(type == 1)
        {
                // Spherical variogram
                vario = new SphVario2D(range1,range2,angle);
        }
        else if(type == 2)
        {
                // Exponential variogram
                vario = new ExpVario2D(range1,range2,angle);
        }
        else if(type == 3)
        {
                // Gaussian variogram
                vario = new GauVario2D(range1,range2,angle);
        }
        else if(type == 4)
        {
                // GenExponential variogram
                vario = new GenExpVario2D(range1,range2,angle,1.0,power);
        }
        else 
        {
                // Not OK
                return NULL;
        }

        
        sim2D.setCorrelation(vario);

        char ** funcName = (char **) calloc(2,sizeof(char *));
        funcName[0] = (char *) calloc(50,sizeof(char));
        char * usage    = (char *) calloc(50,sizeof(char));
        strcpy(funcName[0],"simGauss2D");
        strcpy(usage,"simGauss2D");

        initMessage(1,funcName,usage);
 
//        float *grid = sim2D.drawGridDetailed(nx,ny,xsize,ysize);
        float *grid = sim2D.drawGridStandard(nx,ny,xsize,ysize);

        return grid; // OK
}