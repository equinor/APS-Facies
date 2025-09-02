---
title: Trends from geological interpretations
---
An example of a workflow based on 3D deterministic facies interpretation:

- Draw facies maps for each zone or set of layers based on available data

- Save as 8-bit bitmap files

- Convert to RMS readable map file format

- Import into RMS

- Use RMS trend modelling to create 3D deterministic facies parameter for the relevant zones.

- Alternative A:

  - Estimate facies volume fractions per zone for each facies

  - Use trends on GRF files in APS to get a depositional direction

  - Use estimated facies volume fractions per zone per facies as constant trends for facies probabilities parameters

  - Condition the constant facies probability parameters on probability logs using RMS petrosim

  - Normalize the facies probability parameters per zone

  - QC of the process and result

- Alternative B:
    - Define conditional facies probability for modelled facies given interpreted facies for all modelled and interpreted facies for all zones to be modelled.
    - Apply the conditional facies probabilities to generate trend for facies probabilities
    - Condition the trends to probability logs using RMS petrosim
    - Normalize the facies probability parameters per zone
    - QC of the process and result
