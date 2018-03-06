//
// PURPOSE Template for definition of 2 dimensional grid or array
//
//
// SPECIAL INSTRUCTIONS & NOTES
//         Compilation option HP_UX must be used for HP
//         Compilation option ARRAY_RANGECHECK should be used
//         in debug phase and not if optimal performace is wanted.
//
//


#ifndef GRID2D_TEMPLATE_H
#define GRID2D_TEMPLATE_H

#include "lib_message.h"

template<class T>
class Grid2D
{
 public:
  Grid2D();
  Grid2D(int nx,int ny);
  Grid2D(int istart, int iend, int jstart, int jend);
  Grid2D(const Grid2D<T> &grid);
  Grid2D(const Grid2D<T> *grid);
  ~Grid2D();

  T& operator()(int i,int j);
  Grid2D<T> &operator=(const Grid2D<T> &grid);
  Grid2D<T> &operator=(const T& t);
  void redefine(int nx, int ny);
  void redefine(int istart, int iend, int jstart, int jend);

  const T& operator()(int i,int j) const;

  int xdim() const;
  int ydim() const;
  int xstart() const;
  int xend() const;
  int ystart() const;
  int yend() const;
  const T* getArray(void) const;

 private:
  int nxdim,nydim;
  int nxstart,nxend,nystart,nyend;
  T *array;
  void checkAllocation(void)const;
  void checkIndex(int i, int j)const;
};


#ifdef HP_UX

//  Here the functions are not inline

template<class T> void Grid2D<T>::
checkAllocation(void)const
{
  if(!array){
    moduleError(ALLOC,"Grid2D",
		"%s\n%s %d",
		"Not enough memory space for allocating",
		"a 2 dimensional array of size: ",nxdim*nydim);
  }
  return;
}

template<class T> void Grid2D<T>::
checkIndex(int i, int j)const
{
  if(i < nxstart || i > nxend ||
     j < nystart || j > nyend){
    moduleError(KERNEL,"Grid2D",
		"%s\n%s %d %s%d%s%d%s\n%s %d %s%d%s%d%s",
		"Error in Grid2D: Index out of bounds",
		"First  index: ",i," should be in [",nxstart,",",nxend,"]",
		"Second index: ",j," should be in [",nystart,",",nyend,"]");
  }
  return;
}


template<class T> void Grid2D<T>::
redefine(int nx, int ny)
{
  nxdim = nx;
  nydim = ny;
  nxstart = 0;
  nystart = 0;
  nxend   = nxdim -1;
  nyend   = nydim -1;
  if(array != 0) delete[] array;
  if(nxdim*nydim > 0)
  {
    array = new T[nxdim*nydim];
    checkAllocation();
  }
  else
  {
    array = 0;
  }
  return;
}

template<class T> void  Grid2D<T>::
redefine(int istart, int iend, int jstart, int jend)
{
  nxstart = istart;
  nystart = jstart;
  nxend   = iend;
  nyend   = jend;
  assert(!(nxend - nxstart < 0));
  assert(!(nyend - nystart < 0));
  nxdim = nxend - nxstart + 1;
  nydim = nyend - nystart + 1;

  if(array != 0) delete[] array;
  if(nxdim*nydim > 0)
  {
    array = new T[nxdim*nydim];
    checkAllocation();
  }
  else
  {
    array = 0;
  }
  return;
}

template<class T> Grid2D<T> & Grid2D<T>::
operator=(const Grid2D<T> &grid)
{
  if(nxdim != grid.nxdim ||
     nydim != grid.nydim ){
    printf("\nError in Grid2D: Grid dimensions are not equal in assignment\n");
    return *this;
  }

  assert(array);
  for(int index =0 ; index < nxdim*nydim; index++){
    array[index] = grid.array[index];
  }
  return *this;
}

template<class T> Grid2D<T> & Grid2D<T>::
operator=(const T& t)
{
  assert(array);
  for(int index =0 ; index < nxdim*nydim; index++){
    array[index] = t;
  }
  return *this;
}

//
// FUNCTION: getArray
//
// PURPOSE Returns the pointer to the internal one-dimensional
//         array. This function should only be used for
//         avoiding copying into a onedimensional array
//         in case that is necessary to use in for instance
//         c library functions.
//
// RETURN VALUE Pointer to the internal array
//
// SIDE EFFECTS
//
// SPECIAL INSTRUCTIONS & NOTES
//
template<class T> const T* Grid2D<T>::
getArray(void) const
{
  return array;
}


template <class T> T& Grid2D<T>::
operator()(int i,int j)
{
#ifdef ARRAY_RANGECHECK
  checkIndex(i,j);
#endif

  return array[i-nxstart + (j-nystart)*nxdim];
}


template<class T>  const T& Grid2D<T>::
operator()(int i,int j) const
{
#ifdef ARRAY_RANGECHECK
  checkIndex(i,j);
#endif

  return array[i-nxstart + (j-nystart)*nxdim];
}



template<class T> int Grid2D<T>::
xdim() const
{
  return nxdim;
}

template<class T> int Grid2D<T>::
ydim() const
{
  return nydim;
}

template<class T> int Grid2D<T>::
xstart() const
{
  return nxstart;
}

template<class T> int Grid2D<T>::
xend() const
{
  return nxend;
}

template<class T> int Grid2D<T>::
ystart() const
{
  return nystart;
}

template<class T> int Grid2D<T>::
yend() const
{
  return nyend;
}


#else

//  Here the functions are inline

template<class T> inline void Grid2D<T>::
checkAllocation(void)const
{
  if(!array){
    moduleError(ALLOC,"Grid2D",
		"%s\n%s %d",
		"Not enough memory space for allocating",
		"a 2 dimensional array of size: ",nxdim*nydim);
  }
  return;
}

template<class T> inline void Grid2D<T>::
checkIndex(int i, int j)const
{
  if(i < nxstart || i > nxend ||
     j < nystart || j > nyend){
    moduleError(KERNEL,"Grid2D",
		"%s\n%s %d %s%d%s%d%s\n%s %d %s%d%s%d%s",
		"Error in Grid2D: Index out of bounds",
		"First  index: ",i," should be in [",nxstart,",",nxend,"]",
		"Second index: ",j," should be in [",nystart,",",nyend,"]");
  }
  return;
}


template<class T> inline void Grid2D<T>::
redefine(int nx, int ny)
{
  nxdim = nx;
  nydim = ny;
  nxstart = 0;
  nystart = 0;
  nxend   = nxdim -1;
  nyend   = nydim -1;
  if(array != 0) delete[] array;
  if(nxdim*nydim > 0)
  {
    array = new T[nxdim*nydim];
    checkAllocation();
  }
  else
  {
    array = 0;
  }
  return;
}

template<class T> inline void  Grid2D<T>::
redefine(int istart, int iend, int jstart, int jend)
{
  nxstart = istart;
  nystart = jstart;
  nxend   = iend;
  nyend   = jend;
  assert(!(nxend - nxstart < 0));
  assert(!(nyend - nystart < 0));
  nxdim = nxend - nxstart + 1;
  nydim = nyend - nystart + 1;

  if(array != 0) delete[] array;
  if(nxdim*nydim > 0)
  {
    array = new T[nxdim*nydim];
    checkAllocation();
  }
  else
  {
    array = 0;
  }
  return;
}

template<class T> inline Grid2D<T> & Grid2D<T>::
operator=(const Grid2D<T> &grid)
{
  if(nxdim != grid.nxdim ||
     nydim != grid.nydim ){
    printf("\nError in Grid2D: Grid dimensions are not equal in assignment\n");
    return *this;
  }

  assert(array);
  for(int index =0 ; index < nxdim*nydim; index++){
    array[index] = grid.array[index];
  }
  return *this;
}

template<class T> inline Grid2D<T> & Grid2D<T>::
operator=(const T& t)
{
  assert(array);
  for(int index =0 ; index < nxdim*nydim; index++){
    array[index] = t;
  }
  return *this;
}

//
// FUNCTION: getArray
//
// PURPOSE Returns the pointer to the internal one-dimensional
//         array. This function should only be used for
//         avoiding copying into a onedimensional array
//         in case that is necessary to use in for instance
//         c library functions.
//
// RETURN VALUE Pointer to the internal array
//
// SIDE EFFECTS
//
// SPECIAL INSTRUCTIONS & NOTES
//
template<class T> inline const T* Grid2D<T>::
getArray(void) const
{
  return array;
}


template <class T> inline T& Grid2D<T>::
operator()(int i,int j)
{
#ifdef ARRAY_RANGECHECK
  checkIndex(i,j);
#endif

  return array[i-nxstart + (j-nystart)*nxdim];
}


template<class T> inline const T& Grid2D<T>::
operator()(int i,int j) const
{
#ifdef ARRAY_RANGECHECK
  checkIndex(i,j);
#endif

  return array[i-nxstart + (j-nystart)*nxdim];
}


template<class T> inline int Grid2D<T>::
xdim() const
{
  return nxdim;
}

template<class T> inline int Grid2D<T>::
ydim() const
{
  return nydim;
}

template<class T> inline int Grid2D<T>::
xstart() const
{
  return nxstart;
}

template<class T> inline int Grid2D<T>::
xend() const
{
  return nxend;
}

template<class T> inline int Grid2D<T>::
ystart() const
{
  return nystart;
}

template<class T> inline int Grid2D<T>::
yend() const
{
  return nyend;
}


#endif


// Constructor
template<class T> Grid2D<T>::
Grid2D(void)
{
  nxdim = nydim = 0;
  nxstart = 0;
  nxend = -1;
  nystart = 0;
  nyend = -1;
  array = 0;
}

// Constructor
template<class T> Grid2D<T>::
Grid2D(int nx, int ny)
{
  nxdim = nx;
  nydim = ny;
  nxstart = 0;
  nystart = 0;
  nxend = nx-1;
  nyend = ny-1;
  if(nxdim*nydim > 0)
  {
    array = new T[nxdim*nydim];
    checkAllocation();
  }
  else
  {
    array = 0;
  }
}

// Constructor
template<class T>  Grid2D<T>::
Grid2D(int istart, int iend, int jstart, int jend)
{
  nxstart = istart;
  nxend = iend;
  nystart = jstart;
  nyend = jend;
  assert(!(nxend - nxstart < 0));
  assert(!(nyend - nystart < 0));

  nxdim = iend - istart +1;
  assert(nxdim);
  nydim = jend - jstart +1;
  assert(nydim);
  if(nxdim*nydim > 0)
  {
    array = new T[nxdim*nydim];
    checkAllocation();
  }
  else
  {
    array = 0;
  }
}

// Copy Constructor
template<class T> Grid2D<T>::
Grid2D(const Grid2D<T> &grid)
{
  nxdim = grid.nxdim;
  nydim = grid.nydim;
  nxstart = grid.nxstart;
  nystart = grid.nystart;
  nxend   = grid.nxend;
  nyend   = grid.nyend;
  if(nxdim*nydim > 0){
      array = new T[nxdim*nydim];
      checkAllocation();
      for(int index = 0; index < nxdim*nydim; index++){
	  array[index] = grid.array[index];
      }
  }
  else {
      array = 0;
  }
}

// Copy Constructor
template<class T> Grid2D<T>::
Grid2D(const Grid2D<T> *grid)
{
  nxdim = grid->nxdim;
  nydim = grid->nydim;
  nxstart = grid->nxstart;
  nystart = grid->nystart;
  nxend   = grid->nxend;
  nyend   = grid->nyend;
  if(nxdim*nydim > 0){
      array = new T[nxdim*nydim];
      checkAllocation();
      for(int index = 0; index < nxdim*nydim; index++){
	  array[index] = grid->array[index];
      }
  }
  else {
      array = 0;
  }
}


// Destructor
template<class T> Grid2D<T>::
~Grid2D()
{
  if(array != 0){
    delete[] array;
  }
}


#endif


