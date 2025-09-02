---
title: Implementation
---
The APS plugin is implemented using the plugin functionality in RMS.
The [`rmsapi`](https://www.aspentech.com/en/products/sse/aspen-rms) is used together with [`xtgeo`](https://github.com/equinor/xtgeo) to exchange data between the plugin, RMS and ERT.

The basic algorithm is based on the published [APS algorithms (B. Sebacher et al.)](https://doi.org/10.1016/j.petrol.2017.08.038), but some extensions are also implemented:

- Use of trends in GRF's

- Multiple overlay facies ( special case of extending the truncation map to $2+N$ dimensional cube)

- Support for using APS in ERT as part of RMS workflows run as forward models.

- Optimization of calculation of truncation maps / cubes
