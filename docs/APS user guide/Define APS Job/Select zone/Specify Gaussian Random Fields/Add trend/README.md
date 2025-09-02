---
title: Add trend
---
Toggle on "Apply trend to field" to use GRF trends.
Select trend type from drop down list.
When using trends,
one need to specify the relative standard deviation of the Gaussian residual field relative to the variability of the trend.

The absolute standard deviation is defined by
 $\text{relative_std_dev} * ( \max(\text{Trend}) - \min(\text{Trend}) )$.

If Relative standard deviation is very small or 0, no gaussian residual field is simulated and the GRF realization is equal to the trend.


An application with 0 relative standard deviation can be to choose the trend type `RMS_PARAM` or `RMS_TRENDMAP` and model the GRF with trend outside of APS instead and import it into APS.
![](9ebe7066e526a07b55b22ae880aacd8fb5480c72e05ef997303c2cd4d1b0ed40.png)
