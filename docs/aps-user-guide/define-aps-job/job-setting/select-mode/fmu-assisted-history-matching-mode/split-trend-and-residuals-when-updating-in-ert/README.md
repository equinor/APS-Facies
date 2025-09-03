---
title: Split trend and residuals when updating in ERT
---
When running APS in AHM mode, GRF fields (with optionally trends) is updated by ERT,
and APS will use the updated GRF fields to calculate updated facies realization.
APS will not use any updates of APS parameters other than those related to the truncation rules.
To enable use of updated trend parameters,
this option will let ERT update trend parameters from APS and the residual fields of the GRF's that has trends.
When running APS the following will happen:

- APS will read APS parameters (if any) from `global_variables.yml`

- APS will import the residual GRF fields updated by ERT

- APS will calculate a trend using the updated APS parameters related to the trend

- APS will combine the calculated trend with imported residual GRF's from ERT to get GRF's with trend

- APS will apply truncation using the GRF's with trend

![](assets/images/4b5ddc01e8d6a64b648d643c91deb35755e34b95409f1961ab197059afb074b6.png)
