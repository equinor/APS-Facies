---
title: Probability trends
---

The basic input to make probability trends are typically:

- Geological conceptual model:
  - Which facies are interpreted
  - Facies relationship
  - Depositional directions and interpretation of lateral and vertical facies proportions
  - Stacking pattern
- Estimates of seismic facies probabilities and its relation to geological facies:
  - seismic inversions
  - seismic scale versus geological facies
  - Fluid distribution and relation between geological facies within different fluids and seismic response and interpreted seismic facies.
- Well logs and distribution of facies volume fractions:
  - Vertical proportion curves
  - Lateral volume fraction trends from well to well

Convert a deterministic 3D facies interpretation into a probability trend:

- A possible way to map a deterministic facies interpretation into a probability trend is to specify and apply conditional probabilities for modelled facies given interpreted facies like $P(\text{modelled facies} \space M \mid \text{interpreted facies} \space F)$

## Trends from geological interpretations

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
