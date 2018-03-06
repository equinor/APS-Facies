
/*F:utl_malloc*

________________________________________________________________

		utl_malloc
________________________________________________________________

Name:		utl_malloc: Mmatrix_5d, Fmatrix_5d, Mmatrix_4d, Fmatrix_4d, Mmatrix_3d, Fmatrix_3d, Mmatrix_2d, Fmatrix_2d, Mmatrix_1d, Fmatrix_1d - allocates memory for various purposes
Syntax:		
        | #include <utl.h>
        | void *Mmatrix_1d( int start, int last,
	|       int element_size,  int clear)
        | void *Mmatrix_2d( int row_start,  int row_last,
	|       int col_start,  int col_last,
	|       int element_size,  int clear)
	| void *Mmatrix_3d( int x_start, int x_last
	|       int y_start, int y_last,
	|       int z_start, int z_last,
	|       int element_size, int clear)
	| void *Mmatrix_4d( int x_start, int x_last,
	|       int y_start, int y_last,
	|       int z_start, int z_last,
	|       int t_start, int t_last,
	|       int element_size, int clear)
	| void *Mmatrix_5d( int x_start, int x_last,
	|       int y_start, int y_last,
	|       int z_start, int z_last,
	|       int t_start, int t_last,
	|       int v_start, int v_last,
	|       int element_size, int clear)
	| void *Fmatrix_1d(void *array)
	| void *Fmatrix_2d( void * matrix, void *rows)
	| void *Fmatrix_3d(void *cube, void *matrix, void *array)
	| void *Fmatrix_4d(void *4dbox, void *cube, void *matrix, void *array)
	| void *Fmatrix_5d(void *5dbox, void *4dbox, void *cube,
        |                  void *matrix, void *array)

Description: These are various memory (de)allocation routines, all of them
  using malloc (or calloc).   'element_size' is the size of the elements to
  be allocated; i.e sizeof(int) for integers. 'clear' is one if the
  array or matrix is to be filled by  zeroes.


  Mmatrix_1d returns a pointer to an array of (last - start + 1) elements.
  After the call
  | a = Mmatrix_1d(1,4,sizeof(int),1)
  a[1] will be the first integer element of the array, a[4] will be the
  last. All elements will be initialized to 0.

  Mmatrix_2d will return a pointer to a two-dimensional
  rectangular matrix allocated
  in one chunk of memory. 'row_start' and 'row_last' indicates first and last
  element of the rows.

  Mmatrix_3d will return a pointer to a three-dimensional rectangular cube
  allocated in one chunk of memory. 'x_start', 'x_last', 'y_start', 'y_last',
  'z_start' and 'z_last' gives the dimension of the cube.

  Mmatrix_4d will return a pointer to a four-dimensional rectangular 'box'
  allocated in one chunk of memory. 'x_start', 'x_last', 'y_start', 'y_last',
  'z_start', 'z_last', 't_start' and 't_last' gives the dimension of the box.

  Mmatrix_5d will return a pointer to a five-dimensional rectangular 'box'
  allocated in one chunk of memory. 'x_start', 'x_last', 'y_start', 'y_last',
  'z_start', 'z_last', 't_start', 't_last','v_start' and 'v_last'
  gives the dimension of the box.

  Fmatrix_1d frees the memory allocated by Mmatrix_1d. The adress of the
  first dataelement must be supplied.

  Fmatrix_2d frees the memory a||ocated by Mmatrix_2d. Parameters
  are adress of first matrix element, and adress of first row. See
  the example section for usage.

  Fmatrix_3d frees the memory allocated by Mmatrix_3d. Parameters are adress
  of first cube element, adress of first matrix element, and adress of first
  row.

  Fmatrix_4d frees the memory allocated by Mmatrix_4d. Parameters are adress
  of first box element, adress of first cube element, adress of first matrix
  element, and adress of first row.

  Fmatrix_5d frees the memory allocated by Mmatrix_5d. Parameters are adress
  of first 5box element, adress of first 4box element, adress of first cube
  element, adress of first matrix element, and adress of first row.

Return value: A suitable pointer  is returned. If no storage
 was available, or if routine deallocates memory, returns NULL.
 All Fmatrix routines return NULL.
Diagnosis: Writes error to standard error if malloc(1) or calloc(1)
returned error status NULL.
Examples:
 | double **a;
 |    Allocte room for a [0..2][0..8] double precision matrix
 | a = Mmatrix_2d(0,2,0,8,sizeof(double),1);
 |    Free a.
 | a = Fmatrix_2d( &a[0][0], &a[0]);
Linking: cc progname.c -lutl
Restrictions: Assumes all pointers have the same size (ok on decstations
 and suns).
Hints: Always use row_start and col_start = 0: It will save you problems in
the long run. If you insist on offsets, remember to use
  &array[row_start, col_start] if the address of the first element is needed.
Bugs: Compilers and lint might complain about mixing of data-types. Just
      ignore them.
________________________________________________________________

*/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "utl.h"

/* static char * cvs_id="$Id: utl_malloc.c 283 2017-05-12 13:48:09Z olia $"; */  /* ensures version in .a file */

void *Mmatrix_1d(  int i_first,
		   int i_last,
		   int i_element_size,
		   int i_clear)
{
  int elements;
  char *a;			/* because we will do pointer-arithmetic */

  elements = i_last - i_first + 1;
  if (i_clear)
    a =  (char *)calloc( (unsigned)elements, (unsigned)i_element_size );
  else
    a =  (char *)malloc( (unsigned) elements * i_element_size );
  if (!a)
    {
      fprintf(stderr," Allocation failure in Mmatrix_1d()\n");
      return(NULL);
    }
		/* move the pointer backwards so a[i_first] is first element*/
  a -= i_first * i_element_size;
  return a;
}				/* end of Mmatrix_1d */

void *Mmatrix_2d(int i_row_min,
		   int i_row_max,
		   int i_col_min,
		   int i_col_max,
		   int i_element_size,
		   int i_clear)
{
  int i, cols, rows;
  char **m;			/* because we will do pointer-arithmetic */
  char *p;			

  cols = i_col_max - i_col_min + 1;
  rows = i_row_max - i_row_min + 1;
  /* Allocate pointers to rows. Allocate one more row to be able to NULL
     terminate it.  */
  m = (char **) malloc( (unsigned) (rows +1) * sizeof(void *) );
  if (!m)
    {
      fprintf(stderr," Allocation failure 1 in Mmatrix_2d()\n");
      return(NULL);
    }

  /* Allocate the matrix */
  if (i_clear)
    *m = (char *) calloc( (unsigned) rows * cols, (unsigned) i_element_size );
  else
    *m = (char *) malloc( (unsigned)rows * cols * i_element_size );
  if (!*m)
    {
      fprintf(stderr," Allocation failure 2 in Mmatrix_2d()\n");
      return(NULL);
    }

  p = *m;			/* p is current row */
  m -= i_row_min;

  /* Initialize rowpointers */
  for (i = i_row_min; i <= i_row_max; i++, p += cols*i_element_size)
  {
    m[i] = p;
    m[i] -= i_col_min*i_element_size;
  }
  /* NULL terminated rowpointer_array: This will crash the program if
     m[i_row_max + 1][x] is adressed.
  */
  m[i_row_max + 1] = NULL;

  /* Return pointer to array of pointers to rows */
  return m;
}				/* end of Mmatrix_2d */


void *Mmatrix_3d(int i_x_min,
		   int i_x_max,
		   int i_y_min,
		   int i_y_max,
		   int i_z_min,
		   int i_z_max,
		   int i_element_size,
		   int i_clear)
{
  int i, j, xs, ys, zs;
  char ***m;			/* because we will do pointer-arithmetic */
  char *p;

  xs = i_x_max - i_x_min + 1;
  ys = i_y_max - i_y_min + 1;
  zs = i_z_max - i_z_min + 1;

/* Allocate pointers to lines in the z-direction. This is done by making a
   xs*ys matrix of pointers. */
  m = (char ***) Mmatrix_2d(i_x_min,i_x_max+1,i_y_min,i_y_max+1,sizeof(void *),0);

  if (!m) {
    fprintf(stderr, "Allocation failure 1 in Mmatrix_3d()\n");
    return(NULL);
  }

/* Allocate the cube: */
  if (i_clear)
    m[i_x_min][i_y_min] = (char *) calloc((unsigned) xs*ys*zs, (unsigned) i_element_size);
  else
    m[i_x_min][i_y_min] = (char *) malloc((unsigned) xs*ys*zs*i_element_size);

  if (!(m[i_x_min][i_y_min]) ) {
    fprintf(stderr, "Allocation failure 2 in Mmatrix_3d()\n");
    return(NULL);
  }

  p = m[i_x_min][i_y_min];

  for (i = i_x_min; i<= i_x_max; i++)
    for (j = i_y_min; j<=i_y_max; j++) {
      m[i][j] = p;
      m[i][j] = m[i][j] - i_z_min * i_element_size;
      p = p + zs*i_element_size;
    }

  for (i=i_x_min; i<=i_x_max; i++)
    m[i][i_y_max+1] = NULL;

  for (i=i_y_min; i<=i_y_max; i++)
    m[i_x_max+1][i] = NULL;

  return m;
}                                /*End of Mmatrix_3d */


void *Mmatrix_4d(int i_x_min,
		   int i_x_max,
		   int i_y_min,
		   int i_y_max,
		   int i_z_min,
		   int i_z_max,
		   int i_t_min,
		   int i_t_max,
		   int i_element_size,
		   int i_clear)
{
  int i, j, k, xs, ys, zs, ts;
  char ****m;			/* because we will do pointer-arithmetic */
  char *p;

  xs = i_x_max - i_x_min + 1;
  ys = i_y_max - i_y_min + 1;
  zs = i_z_max - i_z_min + 1;
  ts = i_t_max - i_t_min + 1;

/* Allocate pointers to lines in the t-direction. This is done by making a
   xs*ys*zs matrix of pointers. */
  m = (char ****) Mmatrix_3d(i_x_min,i_x_max+1,i_y_min,i_y_max+1,i_z_min,i_z_max+1,
		 sizeof(void *),0);

  if (!m) {
    fprintf(stderr, "Allocation failure 1 in Mmatrix_4d()\n");
    return(NULL);
  }

/* Allocate the 4d-box: */
  if (i_clear)
    m[i_x_min][i_y_min][i_z_min] = (char *)
      calloc((unsigned) xs*ys*zs*ts, (unsigned) i_element_size);
  else
    m[i_x_min][i_y_min][i_z_min]= (char *) malloc((unsigned) xs*ys*zs*ts*i_element_size);

  if (!(m[i_x_min][i_y_min][i_z_min])) {
    fprintf(stderr, "Allocation failure 2 in Mmatrix_4d()\n");
    return(NULL);
  }

  p = m[i_x_min][i_y_min][i_z_min];

  for (i = i_x_min; i<= i_x_max; i++)
    for (j = i_y_min; j<=i_y_max; j++)
      for (k = i_z_min; k<=i_z_max; k++) {
	m[i][j][k] = p;
	m[i][j][k] = m[i][j][k] - i_t_min * i_element_size;
	p = p + ts*i_element_size;
    }

  for (i=i_x_min; i<=i_x_max; i++)
    for (j=i_y_min; j<=i_y_max; j++)
      m[i][j][i_z_max+1] = NULL;

  for (i=i_x_min; i<=i_x_max; i++)
    for (k=i_z_min; k<=i_z_max; k++)
      m[i][i_y_max+1][k] = NULL;

  for (j=i_y_min; j<=i_y_max; j++)
    for (k=i_z_min; k<=i_z_max; k++)
      m[i_x_max+1][j][k] = NULL;

  return m;
}                                /*End of Mmatrix_4d */


void *Mmatrix_5d(int i_x_min,
		   int i_x_max,
		   int i_y_min,
		   int i_y_max,
		   int i_z_min,
		   int i_z_max,
		   int i_t_min,
		   int i_t_max,
		   int i_v_min,
		   int i_v_max,
		   int i_element_size,
		   int i_clear)
{
  int i, j, k, l, xs, ys, zs, ts, vs;
  char *****m;			/* because we will do pointer-arithmetic */
  char *p;

  xs = i_x_max - i_x_min + 1;
  ys = i_y_max - i_y_min + 1;
  zs = i_z_max - i_z_min + 1;
  ts = i_t_max - i_t_min + 1;
  vs = i_v_max - i_v_min + 1;

/* Allocate pointers to lines in the v-direction. This is done by making a
   xs*ys*zs*ts matrix of pointers. */
  m = (char *****) Mmatrix_4d(i_x_min,i_x_max+1,i_y_min,i_y_max+1,i_z_min,i_z_max+1,
		 i_t_min,i_t_max+1,sizeof(void *),0);

  if (!m) {
    fprintf(stderr, "Allocation failure 1 in Mmatrix_5d()\n");
    return(NULL);
  }

/* Allocate the 5d-box: */
  if (i_clear)
    m[i_x_min][i_y_min][i_z_min][i_t_min] = (char *)
      calloc((unsigned) xs*ys*zs*ts*vs, (unsigned) i_element_size);
  else
    m[i_x_min][i_y_min][i_z_min][i_t_min]= (char *)
           malloc((unsigned) xs*ys*zs*ts*vs*i_element_size);

  if (!m) {
    fprintf(stderr, "Allocation failure 2 in Mmatrix_5d()\n");
    return(NULL);
  }

  p = m[i_x_min][i_y_min][i_z_min][i_t_min];

  for (i = i_x_min; i<= i_x_max; i++)
    for (j = i_y_min; j<=i_y_max; j++)
      for (k = i_z_min; k<=i_z_max; k++)
        for (l = i_t_min; l<=i_t_max; l++) {
	m[i][j][k][l] = p;
	m[i][j][k][l] = m[i][j][k][l] - i_v_min * i_element_size;
	p = p + vs*i_element_size;
    }

  for (i=i_x_min; i<=i_x_max; i++)
    for (j=i_y_min; j<=i_y_max; j++)
      for (k = i_z_min; k<=i_z_max; k++)
        m[i][j][k][i_t_max+1] = NULL;

  for (i=i_x_min; i<=i_x_max; i++)
    for (j=i_y_min; j<=i_y_max; j++)
      for (l=i_t_min; l<=i_t_max; l++)
        m[i][j][i_z_max+1][l] = NULL;

  for (i=i_x_min; i<=i_x_max; i++)
    for (k=i_z_min; k<=i_z_max; k++)
      for (l=i_t_min; l<=i_t_max; l++)
        m[i][i_y_max+1][k][l] = NULL;

  for (j=i_y_min; j<=i_y_max; j++)
    for (k=i_z_min; k<=i_z_max; k++)
      for (l=i_t_min; l<=i_t_max; l++)
        m[i_x_max+1][j][k][l] = NULL;

  return m;
}                                /*End of Mmatrix_5d */


void *Fmatrix_1d(void *array)
/*
  Frees memory allocated by Mmatrix_1d. Returns 0.
  Example:
     double *m;
     m = Mmatrix_1d(0,5,,sizeof(double),0);
     Fmatrix_1d( &m[0] );
*/
{
  free(array);
  return 0;
}				/* end of Fmatrix_2d */

void *Fmatrix_2d(void * i_matrix,
	       void *i_rows)
/*
  Frees memory allocated by Mmatrix_2d. Returns 0.
  Example:
     double **m;
     m = Mmatrix_2d(0,5,0,5,sizeof(double),0);
     Fmatrix_2d( &m[0][0], &m[0] );
*/
{
  free( i_matrix );
  free( i_rows);
  return 0;
}				/* end of Fmatrix_2d */


void *Fmatrix_3d(void *i_cube,
	       void *i_matrix,
	       void *i_rows)
/* Frees memory allocated by Mmatrix_3d. Returns 0.
   Example:
      double ***m;
      m = Mmatrix_3d(0,5,0,5,0,5,sizeof(double),0);
      m = Fmatrix_3d(&m[0][0][0], &m[0][0],
                                 &m[0]);
*/
{
  free(i_cube);
  free(i_matrix);
  free(i_rows);

  return 0;
}                                /* end of Fmatrix_3d */

void *Fmatrix_4d(void *i_4dbox,
	       void *i_cube,
	       void *i_matrix,
	       void *i_rows)
/* Frees memory allocated by Mmatrix_4d. Returns 0.
   Example:
      double ****m;
      m = Mmatrix_4d(0,5,0,5,0,5,0,5,sizeof(double),0);
      m = Fmatrix_4d(&m[0][0][0][0], &m[0][0][0], &m[0][0], &m[0]);
*/
{
  free(i_4dbox);
  free(i_cube);
  free(i_matrix);
  free(i_rows);

  return 0;
}                                /* end of Fmatrix_4d */

void *Fmatrix_5d(void *i_5dbox,
	       void *i_4dbox,
	       void *i_cube,
	       void *i_matrix,
	       void *i_rows)
/* Frees memory allocated by Mmatrix_5d. Returns 0.
   Example:
      double ****m;
      m = Mmatrix_5d(0,5,0,5,0,5,0,5,0,5,sizeof(double),0);
      m = Fmatrix_5d(&m[0][0][0][0][0], &m[0][0][0][0], &m[0][0][0],
                     &m[0][0], &m[0]);
*/
{
  free(i_5dbox);
  free(i_4dbox);
  free(i_cube);
  free(i_matrix);
  free(i_rows);

  return 0;
}                                /* end of Fmatrix_5d */

#ifdef TESTING
int main()
{
  double ****a, *p;
  int i,j,k,l,n;
  printf("Allokverer en 3x5x4x6 matrise\n"),
  a = Mmatrix_4d(2,4,1,5,3,6,0,5,sizeof(double),0);

  for ( i = 2, n = 1; i <= 4; i++)
    for ( j = 1; j <=5; j++)
      for (k = 3; k <= 6; k++)
	for (l = 0; l<=5; l++, n++)
	  a[i][j][k][l] = n/10.0;

  for (p = &a[2][1][3][0], i = 2; i <=4; i++, printf("\n"))
    for ( j = 1; j <=5; j++, printf("\n"))
      for ( k=3; k <=6; k++, printf("\n"))
	for (l=0; l <=5; l++, p++)
	  printf("%g ",*p);

  printf("\n");
  Fmatrix_4d( &a[2][1][3][0], &a[2][1][3], &a[2][1], &a[2]);
  return(0);
}
#endif
