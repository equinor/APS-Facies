---
title: Extrapolate 3D custom trend in ERTBOX
---
When using user defined trends (`RMS_PARAM` or `RMS_TRENDMAP`) which is defined in the geomodel, APS has to copy this from the geomodel to the ERTBOX grid.
The following steps will be done by APS:

- Copy RMS 3D continuous parameter for trend from geomodel grid to ERTBOX grid

- Fill the grid cells in the ERTBOX grid that was not filled after the trend was copied from the geomodel.

- Calculate a discrete 3D parameter for the ERTBOX with value 1 for grid cells that are copied from the geomodel grid and 0 for the grid cells that are not (but filled by APS)

- Alternative ways of filling in undefined grid cell values for the trend:
    - Assign a constant
    - Alternative extrapolation methods

The user can choose between various extrapolation methods like:- Assigning constant value

- Extrapolated upwards or downwards column by column from the nearest defined grid cell in that column

- Extrapolated by using layer average

- Extrapolate by repeating the values that are defined in opposite order (mirror extrapolation)

It will only be for grid cells close to the zone border for zones with top or base conform griding that the extrapolation may have any effect.
ERT will in the update step make linear combinations of the realization vectors.
To avoid mixing real physical grid cell values with unphysical values from grid cells that are not present in some realization,
the extrapolated values are a better choice than to assign unrealistic values like `0`,
`NaN` or similar since the extrapolated values may be used in linear combination in the update step in ERT.

![](db0d2aadf31517960f2ee4b25ea971862569eb359543cefc26c065107641affe.png)
