---
title: Check ERT iteration and simulate/export or import GRF fields
---
In this model APS will check the `_ERT_ITERATION_NUMBER` environment variable which is defined by ERT.
This variable contains the iteration number in ES-MDA in ERT.
Depending on the iteration number,
the APS job will and simulate and export GRF's to file if iteration is $0$ and import updated GRF's from ERT if $\text{iteration number} > 0$.

![](assets/images/32f187acc0179e1fe1f62ff2bb0e1d9d506fd4cf311be72466526af7dbb8b16d.png)
