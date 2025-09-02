---
title: Trends in GRF
---
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
