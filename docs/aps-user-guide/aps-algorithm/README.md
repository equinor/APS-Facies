---
title: APS algorithm
---

## APS algorithm

### Algorithm steps
For each grid block in geomodel zone:

1. Look up the facies probabilities for that grid block ($P(F_1)$, $P(F_2)$, $P(F_3)$, ...)

2. Use the template for the truncation map and rescale the polygons associated with each facies to match the facies probabilities.

3. Look up the transformed gaussian field values (values between 0 and 1) for the grid block (GRF<sub>1</sub>, GRF<sub>2</sub>, ...)

4. Find the polygon in the rescaled truncation map the point with coordinates (GRF<sub>1</sub>, GRF<sub>2</sub>, ...) will be located within.

5. The facies associated with the polygon found will be assigned to the grid block in the facies realization.

### Comments

Step 2 above where the truncation map is rescaled such that the area of the polygons belonging to the various facies match the facies probabilities for the current grid cell, is the adaptive step and the reason why the method is called **A**daptive **P**luri-gaussian **S**imulation.

### Illustration
The figure below illustrates the process.
The upper left grid cell is chosen as an example.
The facies probabilities for this grid cell is $P(F_1) = 0.7$, $P(F_2) = 0.1$ and $P(F_3) = 0.2$ and the sum of the probabilities are normalized to 1.
The transformed version of the simulated GRF's for the same cell is in this example $\text{GRF}_1 = 0.1$ and $\text{GRF}_2 = 0.15$

The different polygons associated with the three facies are rescaled such that the area of each of them have a fraction equal to the facies probabilities.

When using (GRF<sub>1</sub>, GRF<sub>2</sub>) as coordinates to find the polygon, we see here that the point is located in the yellow polygon (rectangle) which is associated with facies F1.
The second example is grid block in lower left corner with probabilities $P(F_1) = 0.5$, $P(F_2) = 0.2$ and $P(F_3) = 0.3$.
The point (GRF<sub>1</sub>, GRF<sub>2</sub>) for this grid block will be located in a polygon belonging to faces F2 marked with red color.

![](assets/images/71308213a804a8e6999d26d344af3d301527c66df4e844aba47876320bb4fab2.png)

## Implementation

The APS plugin is implemented using the plugin functionality in RMS.
The [`rmsapi`](https://www.aspentech.com/en/products/sse/aspen-rms) is used together with [`xtgeo`](https://github.com/equinor/xtgeo) to exchange data between the plugin, RMS and ERT.

The basic algorithm is based on the published [APS algorithms (B. Sebacher et al.)](https://doi.org/10.1016/j.petrol.2017.08.038), but some extensions are also implemented:

- Use of trends in GRF's

- Multiple overlay facies ( special case of extending the truncation map to $2+N$ dimensional cube)

- Support for using APS in ERT as part of RMS workflows run as forward models.

- Optimization of calculation of truncation maps / cubes

### Trends in GRF

The use of trends in GRF's is an extension of the original published APS method.
Trends can be handled in APS by using a different transformation of the GRF fields.
The original version of APS applied the cumulative normal distribution function to map the GRF values into a field having uniform distribution
(also called alpha fields).
When using GRF with trends,
instead all values for the GRF within a realization for a given zone is used to create an empiric cumulative distribution function.
This function is used to map the GRF values with trend into uniform distribution.

The effect of this is that the specified facies probabilities in each individual grid cell is no longer honored,
but the global facies fractions within a zone will still be honored.
The main point of introducing GRF's with trend is to simplify model specifications where facies has clear depositional direction like facies belts.
The use of trends both in probability cubes and GRF's will create realizations with a mixed effect of the trends from both.
It is recommended to carefully check the effect of mixing trends from both or only use trend in either probability cubes or GRF's.

### Overlay facies

The overlay facies (facies eroding into other facies called background facies)
is implemented by introducing additional GRF's corresponding to higher dimensions of the truncation cube.
The total number of GRF's used is $2 + N$ where the first two are used to define the background facies while the other $N$ GRF's are used to define overlay facies.

The algorithm ensures that specified facies probabilities are satisfied in the sense that the volume fractions of the truncation cube for the various facies match the specified facies probabilities.

### Optimised truncation map/cube calculation

To speed up the algorithm, calculation of truncation maps are optimized:

- Reduce the number of calculations of truncation maps by grouping all grid cells having almost the same facies probability distribution together and use the same truncation map/cube for all of them instead of re-calculating the same truncation map many times.

- Numpy vectorization of all calculations as far a possible.

These optimisations are most effective when the facies probability distribution vary slowly over the reservoir zone or is more or less constant. Rapid and very random variation of facies probabilities will reduce the possibility to find many grid cells with almost the same facies probability distribution and will therefore increase the number of different truncation maps/cubes needed.
