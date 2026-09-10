---
title: Normalisation
---

The sum of facies probabilities must add up to 1 in each individual grid cell within a zone.
A normalisation must be done as the last step in the preparation of facies probabilities.

Since the normalization must be done separately per zone (and per zone and region if regions also are used),
a script to do that is available from the APS toolbox.

see [APS Toolbox -> Check normalization](/aps-toolbox/check-normalisation-of-facies-probabilities.md) of facies probabilities.

When running the normalization check (and possibly calculate normalized facies probabilities), there is an option to either overwrite the input facies probability files or create new files with normalized facies probabilities. If new files are created, they will get the same name as the input (unnormalized) facies probability files but with the addition of "_norm" in the file name.

APS code will also, to be sure, check the normalization and complain if the input is too far away from being normalized according to the same criteria as used in the utility for normalization.

Note: It is recommended that the user normalize the input facies probabilities and QC this and not let APS code do the normalization internally since it will then be more difficult to detect errors in input facies probabilities.
