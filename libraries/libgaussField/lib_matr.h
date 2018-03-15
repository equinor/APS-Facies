
/* External functions */

#ifdef __cplusplus
extern "C"
{
#endif


extern void lib_matr_update_var(double *i_obs, int i_n, int i_np,
                           double *x_mu, double **x_var);
extern void lib_matr_downdate_var(double *i_obs, int i_n, int i_np,
				  double *x_mu, double **x_var);
extern void lib_matr_exp(double **i_mat,int i_n,double i_exp,
                         double **o_mat);
extern void lib_matr_prod(double **i_mat1,double **i_mat2,
                          int i_n1,int i_n2,int i_n3,
                          double **o_mat);
extern void lib_matr_prodmatvec(double **i_mat, double *i_vec, int i_n1,
				int i_n2, double *o_vec);
extern void lib_matr_eigen(double **i_mat,int i_n,
                            double **o_eigvec,double *o_eigval, int *o_error);
extern void lib_matr_eigenvalues(double **i_mat, int i_n, double *o_eigval,
				 int *o_error);
extern void lib_matr_add(double **i_y, int i_n1, int i_n2, double **x_x);
extern void lib_matr_addvec(double *i_y, int i_n, double *x_x);
extern void lib_matr_subtract(double **i_x, double **i_y, int i_n1, int i_n2,
			      double **o_z);
extern void lib_matr_subtractvec(double *i_x, double *i_y, int i_n,
				 double *i_z);
extern int lib_matr_cholesky(int i_dim, double **x_mat);
extern void lib_matr_axeqb(int i_dim, double **i_mat, double *x_vec);

#ifdef __cplusplus
}
#endif
