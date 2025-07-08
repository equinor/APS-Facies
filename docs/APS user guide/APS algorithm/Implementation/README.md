---
title: Implementation
---
The APS plugin is implemented using the plugin functionality in RMS. The
**rmsapi**
is used together with
**xtgeo**
to exchange data between the plugin, RMS and ERT.The basic algorithm is based on the published APS algorithms (B. Sebacher et.al), but some extensions are also implemented:- Use of trends in GRF's

- Multiple overlay facies ( special case of extending the truncation map to 2+N dimensional cube)

- Support for using APS in ERT as part of RMS workflows run as forward models.

- Optimization of calculation of truncation maps/cubes
