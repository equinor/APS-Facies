---
title: Optimised truncation map/cube calculation
---
To speed up the algorithm, calculation of truncation maps are optimized:

- Reduce the number of calculations of truncation maps by grouping all grid cells having almost the same facies probability distribution together and use the same truncation map/cube for all of them instead of re-calculating the same truncation map many times.

- Numpy vectorization of all calculations as far a possible.

These optimisations are most effective when the facies probability distribution vary slowly over the reservoir zone or is more or less constant. Rapid and very random variation of facies probabilities will reduce the possibility to find many grid cells with almost the same facies probability distribution and will therefore increase the number of different truncation maps/cubes needed.
