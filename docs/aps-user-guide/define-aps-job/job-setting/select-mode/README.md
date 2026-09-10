---
title: Select mode
---

Select how APS should interact with ERT:

- Run APS facies update in AHM/ERT: Toggle on this if you want to let ERT draw APS model parameters and update the GRF's in [Ensemble Smoother](https://ert.readthedocs.io/en/latest/theory/ensemble_based_methods.html#ensemble-smoother-es) or [ES-MDA](https://ert.readthedocs.io/en/latest/theory/ensemble_based_methods.html#ensemble-smoother-multiple-data-assimilation-es-mda).

- Only run uncertainty update: Toggle on this if you want to let ERT draw and update APS model parameters.

- If none of the above is toggled on, APS will always use the specified model parameters in the APS GUI and not modify them behind the scenes.

![](assets/images/eeffc698560352f36850cc828efe06427aacc2350a4cb89a2330754d8ac30c29.png)

!!! note

    For more information on ERT, see [ERT's documentation](https://ert.readthedocs.io/en/latest/)
