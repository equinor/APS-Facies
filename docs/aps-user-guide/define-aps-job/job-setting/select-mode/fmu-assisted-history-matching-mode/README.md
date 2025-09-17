---
title: FMU assisted history matching mode
---

![](assets/images/fdd7e9d30009a95b0ea964b523b50bba08002abb08b7ff2c9de33f35fabfc2bc.png)

This mode is suitable when running APS in an RMS project in ERT where ERT update the GRF fields that is used by APS.
This mode requires that APS and ERT exchange GRF fields.
This mode requires:

- Specification of a help grid to exchange fields (GRF's) with ERT. This grid is called ERTBOX grid

- That APS deliver initial realizations of GRF's to ERT

- That APS will read and use updated versions of the GRF's to calculate updated facies realization.

The workflow is as follows when running APS:

- If ERT iteration = 0 which means that initial ensemble of realizations is created in the ERT FORWARD model when running RMS:
    - APS will read the `global_variables.yml` file that is created by ERT
    - APS will check if any of the APS parameters that are enabled to be updated in APS GUI is available in `global_variables.yml` file.
    - APS will use the parameter values it get from ERT from `global_variables.yml` file to simulate the GRF's and apply the truncation rules to get a facies realization.
    - The APS simulation of the GRF's will be done in the ERTBOX grid and copied back to the geogrid before truncation is applied.
    - The GRF's simulated in the ERTBOX grid will also be exported to files to be used by the FIELD keyword in ERT configuration file.
    - ERT will after the FORWARD model is finished for iteration = 0 in ERT run, update the GRF fields specified in the FIELD keyword in ERT by conditioning to available observations. ERT will also update the parameters in the `global_variables.yml` file including the APS model parameters in that file.
    - If ERT iteration &gt; 0 which means that ERT will run FORWARD model using the updated ensemble of realizations of parameters, the following will happen when APS job is run in RMS as a part of the FORWARD model in ERT:
    - APS will read the `global_variables.yml` file that is updated by ERT.
    - APS will read the updated GRF's from file into ERTBOX and further into the geomodel.
    - APS will use updated parameters related to truncation rules (if any) and apply the truncation rule on the updated version of the GRF fields that was imported from ERT.
    - APS will update the facies realization in RMS
    - NOTE: Since APS will not run the GRF simulation again, but use the updated GRF fields from ERT, it will not apply any of the APS parameters related to simulation of GRF fields, but only the APS parameters related to the truncation rule if they are specified to be updated by ERT.

![](assets/images/3fd81875fe98f5e91767accc1c0fd4da36d1de03bcbab8a879fb8bd6a961cea6.png)

The figure show the data flow when running APS as part of RMS in forward model in ERT for iteration=0.
The steps are:
(1) update APS model by using parameters read from `global_variables.yml` file,
(2) simulate GRF's,
(3) export simulated GRF's to files readable by ERT,
(4) copy the simulated GRF's from ERTBOX to geomodel grid,
(5) check facies probabilities,
(6) apply truncations and create/update facies realization parameter in RMS.
