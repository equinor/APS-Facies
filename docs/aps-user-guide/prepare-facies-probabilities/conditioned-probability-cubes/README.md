---
title: Conditioned probability cubes
---
In RMS the petrosim module can be used to condition probability trends on probability logs to ensure that interpreted facies in blocked well logs are honored in APS models.

## RMS petrosim to condition 3D probability parameters

When 3D parameters for facies probability trends are available, it is possible to use that as input to create facies probability cubes.

Note, however, that well conditioning using RMS (kriging) will not guarantee that the resulting facies probability cubes sum up to 1 even though the facies probability logs do that.

A final step to normalize the facies probabilities must be done.
