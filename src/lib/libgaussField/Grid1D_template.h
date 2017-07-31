// PURPOSE Template for definition of 1 dimensional grid or array
//
//
// SPECIAL INSTRUCTIONS & NOTES
//         Compilation option HP_UX must be used for HP
//         Compilation option ARRAY_RANGECHECK should be used
//         in debug phase and not if optimal performace is wanted.  
//



#ifndef GRID1D_TEMPLATE_H
#define GRID1D_TEMPLATE_H


#include <assert.h>
#include "lib_message.h"

template<class T>
class Grid1D
{
 public:
  Grid1D();
  Grid1D(int nx);
  Grid1D(int istart, int iend);
  Grid1D(const Grid1D<T> &grid);
  Grid1D(const Grid1D<T> *grid);
  ~Grid1D();

  T& operator()(int i);
  Grid1D<T> &operator=(const Grid1D<T> &grid);
  Grid1D<T> &operator=(const T& t);
  void redefine(int nx);
  void redefine(int istart, int iend);
  void assign(const T* t);
    

  const T& operator()(int i) const;
  int xdim() const;
  int xstart() const;
  int xend() const;
  const T* getArray(void) const;

 private:
  int nxdim;
  int nxstart,nxend;
  T *array;
  void checkAllocation(void)const;
  void checkIndex(int i)const;
};

// Note that if HP is specified all functions are not inline, in other case
// all functions are inline except the constructors and destructor.


#ifdef HP_UX    
template<class T> void Grid1D<T>::
checkAllocation(void)const
{
  if(!array){
    moduleError(ALLOC,"Grid1D",
		"%s\n%s %d",
		"Not enough memory space for allocating",
		"a 1 dimensional array of size: ",nxdim);
  }
  return;
}      

template<class T> void Grid1D<T>::
checkIndex(int i)const
{
  if(i < nxstart || i > nxend){
    moduleError(KERNEL,"Grid1D",
		"%s\n%s %d %s%d%s%d%s",
		"Error in Grid1D: Index out of bounds",
		"First  index: ",i," should be in [",nxstart,",",nxend,"]");
  }
  return;
}


template <class T> T& Grid1D<T>::
operator()(int i)
{
#ifdef ARRAY_RANGECHECK
  checkIndex(i);
#endif

  return array[i-nxstart];
}


template<class T> const T& Grid1D<T>::
operator()(int i) const
{
#ifdef ARRAY_RANGECHECK
  checkIndex(i);
#endif

  return array[i-nxstart];
}


template<class T> void Grid1D<T>::
redefine(int nx)
{
  nxdim = nx;
  nxstart = 0;
  nxend   = nxdim -1;

  if(array != 0) delete[] array;
  if(nxdim > 0)
  {
    array = new T[nxdim];
    checkAllocation();
  }
  else
  {
    array = 0;
  }
  return;
}

template<class T> void  Grid1D<T>::
redefine(int istart, int iend)
{

  nxstart = istart;
  nxend   = iend;
  assert(!(nxend - nxstart < 0));
  nxdim = nxend - nxstart + 1;

  if(array != 0) delete[] array;
  if(nxdim > 0)
  {
    array = new T[nxdim];
    checkAllocation();
  }
  else
  {
    array = 0;
  }
  return;
}

template<class T> Grid1D<T> & Grid1D<T>::
operator=(const Grid1D<T> &grid)
{
  if(nxdim != grid.nxdim ){
    printf("\nError in Grid1D: Grid dimensions are not equal in assignment\n");
    return *this;
  }

  assert(array);
  for(int index =0 ; index < nxdim; index++){
    array[index] = grid.array[index];
  }
  return *this;
}


template<class T>  Grid1D<T> & Grid1D<T>::
operator=(const T& t)
{

  assert(array);
  for(int index =0 ; index < nxdim; index++){
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
template<class T> const T* Grid1D<T>::
getArray(void) const
{
  return array;
}

template<class T> void Grid1D<T>::
assign(const T* t)
{
    assert(t);
    int i;
    for(i = 0; i < nxdim; i++){
	array[i] = t[i];
    }
}

template<class T> int  Grid1D<T>::
xdim() const
{
    return nxdim;
}

template<class T> int  Grid1D<T>::
xstart() const
{
    return nxstart;
}

template<class T> int  Grid1D<T>::
xend() const
{
    return nxend;
}


#else

// Here all functions are inline


template<class T> inline void Grid1D<T>::
checkAllocation(void)const
{
  if(!array){
    moduleError(ALLOC,"Grid1D",
		"%s\n%s %d",
		"Not enough memory space for allocating",
		"a 1 dimensional array of size: ",nxdim);
  }
  return;
}      


template<class T> inline void Grid1D<T>::
checkIndex(int i)const
{
  if(i < nxstart || i > nxend){
    moduleError(KERNEL,"Grid1D",
		"%s\n%s %d %s%d%s%d%s",
		"Error in Grid1D: Index out of bounds",
		"First  index: ",i," should be in [",nxstart,",",nxend,"]");
  }
  return;
}



template <class T> inline T& Grid1D<T>::
operator()(int i)
{
#ifdef ARRAY_RANGECHECK
  checkIndex(i);
#endif

  return array[i-nxstart];
}


template<class T> inline const T& Grid1D<T>::
operator()(int i) const
{
#ifdef ARRAY_RANGECHECK
  checkIndex(i);
#endif

  return array[i-nxstart];
}


template<class T> inline void Grid1D<T>::
redefine(int nx)
{
  nxdim = nx;
  nxstart = 0;
  nxend   = nxdim -1;

  if(array != 0) delete[] array;
  if(nxdim > 0)
  {
    array = new T[nxdim];
    checkAllocation();
  }
  else
  {
    array = 0;
  }
  return;
}

template<class T> inline void  Grid1D<T>::
redefine(int istart, int iend)
{

  nxstart = istart;
  nxend   = iend;
  assert(!(nxend - nxstart < 0));
  nxdim = nxend - nxstart + 1;

  if(array != 0) delete[] array;
  if(nxdim > 0)
  {
    array = new T[nxdim];
    checkAllocation();
  }
  else
  {
    array = 0;
  }
  return;
}

template<class T> inline Grid1D<T> & Grid1D<T>::
operator=(const Grid1D<T> &grid)
{
  if(nxdim != grid.nxdim ){
    printf("\nError in Grid1D: Grid dimensions are not equal in assignment\n");
    return *this;
  }

  assert(array);
  for(int index =0 ; index < nxdim; index++){
    array[index] = grid.array[index];
  }
  return *this;
}


template<class T> inline Grid1D<T> & Grid1D<T>::
operator=(const T& t)
{

  assert(array);
  for(int index =0 ; index < nxdim; index++){
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
template<class T> inline const T* Grid1D<T>::
getArray(void) const
{
  return array;
}

template<class T> inline void Grid1D<T>::
assign(const T* t)
{
    assert(t);
    int i;
    for(i = 0; i < nxdim; i++){
	array[i] = t[i];
    }
}

template<class T> inline int  Grid1D<T>::
xdim() const
{
    return nxdim;
}

template<class T> inline int  Grid1D<T>::
xstart() const
{
    return nxstart;
}

template<class T> inline int  Grid1D<T>::
xend() const
{
    return nxend;
}

#endif


// Constructor
template<class T>  Grid1D<T>::
Grid1D(void)
{
  nxdim =  0;
  nxstart = 0;
  nxend = -1;
  array = 0;
}

// Constructor
template<class T>  Grid1D<T>::
Grid1D(int nx)
{
  nxdim = nx;
  nxstart = 0;
  nxend = nx-1;
  if(nxdim > 0) {
      array = new T[nxdim];
      checkAllocation();
  }
  else {
      array = 0;
  }

}

// Constructor
template<class T>   Grid1D<T>::
Grid1D(int istart, int iend)
{
  nxstart = istart;
  nxend = iend;

  assert(!(nxend - nxstart < 0));

  nxdim = iend - istart +1;
  assert(nxdim);
  if(nxdim > 0){
      array = new T[nxdim];
      checkAllocation();
  }
  else {
      array = 0;
  }

}

// Copy Constructor
template<class T>  Grid1D<T>::
Grid1D(const Grid1D<T> &grid)
{
  nxdim = grid.nxdim;
  nxstart = grid.nxstart;
  nxend   = grid.nxend;
  if(nxdim > 0){
      array = new T[nxdim];
      checkAllocation();
      for(int index = 0; index < nxdim; index++){
	  array[index] = grid.array[index];
      }
  }
  else {
      array = 0;
  }
}

// Copy Constructor
template<class T> Grid1D<T>::
Grid1D(const Grid1D<T> *grid)
{
  nxdim = grid->nxdim;
  nxstart = grid->nxstart;
  nxend   = grid->nxend;
  if(nxdim > 0){
      array = new T[nxdim];
      checkAllocation();
      for(int index = 0; index < nxdim; index++){
	  array[index] = grid->array[index];
      }
  }
  else {
      array = 0;
  }
}

// Destructor
template<class T>  Grid1D<T>::
~Grid1D()
{
  if(array != 0){
    delete[] array;
  }
}



#endif







