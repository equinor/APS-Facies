---
title: Set parameters for simulating GRF
---

The settings for GRF consists of a previewer and various settings related to the variogram and trends.
When using APS in FMU settings with ERT (Ensemble Reservoir Tool),
it is possible to activate/deactivate which model parameter that can be modified by ERT through the file for global variables.

The local previewer for GRF has the option to draw new realization
(The dice icon, :fontawesome-solid-dice:),
update the preview image after parameters are changed (the circular arrow icon, :fontawesome-solid-refresh:),
and change grid size for preview (the gears icon, :fontawesome-solid-gears:).

![](b3061d535861ac5f45f8649d2e096a8597a10c24c6604b8ead919bf13309b89d.png)

The number of Gaussian Random fields are per default two, but when using overlay facies, this number must be increased.
The GRF field specification:

- Variogram (spatial correlation type)

- Correlation ranges

- Anisotropy direction (Direction for main range)

- Dip direction (The dip for main range direction)

- Optional, specify trends:
    - Select trend type
    - Select associated parameter settings

Use the previewer for the GRF fields to check the effect of the settings:

- **Preview grid orientation**:
  Note the orientation of the preview is rotated relative to the geomodel grid such that the local Y direction or J direction of the grid is vertical.
  This is to save space in previewer.
  For instance, if the geomodel grid is rotated 30 degrees anti-clock wise,
  the preview view of it will be rotated 30 degrees clockwise.

- Preview can be very useful when specifying trends for GRF fields.

- Note that trend type `RMS_PARAM` and `RMS_TRENDMAP` does not have any preview functionality implemented.

**Always check the facies realization in RMS after running the APS job**:

- Remember that any trends in probability cubes are not shown in the previewer.
