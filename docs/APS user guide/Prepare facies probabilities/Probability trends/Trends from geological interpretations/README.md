---
title: Trends from geological interpretations
---
An example of a workflow based on 3D deterministic facies interpretation:- Draw facies maps for each zone or set of layers based on available data

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

- Alternative B:<ul style="margin-top: 0mm; margin-bottom: 0mm; list-style-type: disc; "><li style="margin-left: 0pt; margin-right: 0pt; padding-left: 0pt; ">Define conditional facies probability for modelled facies given interpreted facies for all modelled and interpreted facies for all zones to be modelled.</li><li style="margin-left: 0pt; margin-right: 0pt; padding-left: 0pt; ">Apply the conditional facies probabilities to generate trend for facies probabilities</li><li style="margin-left: 0pt; margin-right: 0pt; padding-left: 0pt; ">Condition the trends to probability logs using RMS petrosim</li><li style="margin-left: 0pt; margin-right: 0pt; padding-left: 0pt; ">Normalize the facies probability parameters per zone</li><li style="margin-left: 0pt; margin-right: 0pt; padding-left: 0pt; ">QC of the process and result</li></ul>
