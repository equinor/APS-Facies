---
title: Select ERTBOX grid model
---
APS can generate the ERTBOX grid if it does not exist. Be sure to specify a number of layers that are large enough to contain the zone with most layers that you intend to model with APS. If the FMU project also model uncertainty of the structural model, be sure that ERTBOX grid is large enough for all realizations of the zone with most layers.![](891be09f64eff5cbaa171177c3e83914cf6ce0db1be2888f6b9809bb60f83595.png)
Note: If the RMS model contains multiple APS jobs, all these jobs should use the same ERTBOX since ERT can only handle one ERTBOX grid (all realizations in ERT must be of the same size).
