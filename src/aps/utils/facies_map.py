import numpy as np


def create_facies_map(gauss_fields, truncation_rule, use_code=False):
    grid_sizes = set(gf.field.size for gf in gauss_fields)
    assert len(grid_sizes) == 1
    num_grid_cells = grid_sizes.pop()
    facies = np.zeros(num_grid_cells, int)
    facies_fraction = {}
    # Find one realization to get the grid size
    alpha_coord = np.zeros(len(gauss_fields), np.float32)
    for i in range(num_grid_cells):
        for m in range(len(gauss_fields)):
            item = gauss_fields[m]
            alpha_realization = item.field
            alpha_coord[m] = alpha_realization[i]
        facies_code, facies_index = truncation_rule.defineFaciesByTruncRule(alpha_coord)

        facies[i] = facies_code if use_code else facies_index + 1
        if facies_index not in facies_fraction:
            facies_fraction[facies_index] = 0
        facies_fraction[facies_index] += 1
    return facies, facies_fraction


def create_facies_map_vectorized(gauss_fields, truncation_rule, use_code=False):
    grid_sizes = set(gf.field.size for gf in gauss_fields)
    assert len(grid_sizes) == 1
    num_grid_cells = grid_sizes.pop()
    facies_fraction = {}
    # Find one realization to get the grid size
    alpha_coord_vectors = np.zeros((num_grid_cells, len(gauss_fields)), np.float32)
    for m in range(len(gauss_fields)):
        item = gauss_fields[m]
        alpha_realization = item.field
        alpha_coord_vectors[:, m] = np.asarray(alpha_realization)
    facies_code_vector, facies_index_vector = (
        truncation_rule.defineFaciesByTruncRule_vectorized(alpha_coord_vectors)
    )
    if use_code:
        facies = facies_code_vector
    else:
        facies = facies_index_vector + 1
        for i in range(num_grid_cells):
            facies_index = facies_index_vector[i]
            if facies_index not in facies_fraction:
                facies_fraction[facies_index] = 0
            facies_fraction[facies_index] += 1
    return facies, facies_fraction
