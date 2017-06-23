#ifndef _draw2DGaussField_
#define _draw2DGaussField_
extern "C"
{
float *draw2DGaussField(int nx, int ny, double xsize, double ysize,
                     int type,unsigned int iseed,
                     double range1,double range2,double angle,double power, int debugPrint=0);
}
#endif
