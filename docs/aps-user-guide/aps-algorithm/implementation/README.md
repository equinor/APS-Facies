---
title: Implementation
---
The APS plugin is implemented using the plugin functionality in RMS.
The [`rmsapi`](https://www.aspentech.com/en/products/sse/aspen-rms) is used together with [`xtgeo`](https://github.com/equinor/xtgeo) to exchange data between the plugin, RMS and ERT.

The basic algorithm is based on the published [APS algorithms (B. Sebacher et al.)](https://doi.org/10.1016/j.petrol.2017.08.038), but some extensions are also implemented:

- Use of trends in GRF's

- Multiple overlay facies ( special case of extending the truncation map to $2+N$ dimensional cube)

- Support for using APS in ERT as part of RMS workflows run as forward models.

- Optimization of calculation of truncation maps / cubes

## Trends in GRF

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

## Overlay facies

The overlay facies (facies eroding into other facies called background facies)
is implemented by introducing additional GRF's corresponding to higher dimensions of the truncation cube.
The total number of GRF's used is $2 + N$ where the first two are used to define the background facies while the other $N$ GRF's are used to define overlay facies.

The algorithm ensures that specified facies probabilities are satisfied in the sense that the volume fractions of the truncation cube for the various facies match the specified facies probabilities.

## Optimised truncation map/cube calculation

To speed up the algorithm, calculation of truncation maps are optimized:

- Reduce the number of calculations of truncation maps by grouping all grid cells having almost the same facies probability distribution together and use the same truncation map/cube for all of them instead of re-calculating the same truncation map many times.

- Numpy vectorization of all calculations as far a possible.

These optimisations are most effective when the facies probability distribution vary slowly over the reservoir zone or is more or less constant. Rapid and very random variation of facies probabilities will reduce the possibility to find many grid cells with almost the same facies probability distribution and will therefore increase the number of different truncation maps/cubes needed.
