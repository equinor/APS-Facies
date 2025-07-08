---
title: Select facies log
---
Which facies to use in the model, must be selected by user. All other facies will be ignored.When not using blocked well set and facies log:- Add the facies as you want, assign facies code and name and optionally change the color or the alias name if the facies names are very long and unpractical. The alias for facies names are only used in the GUI, not in the realizations.
When using blocked well set and facies log:- The facies found in the blocked well facies log for the zone is marked with the "eye" icon (observed) and a "screen" icon.

- The facies found in the blocked well facies log but not in the current zone is marked with the "not observed eye icon and the "screen" icon.

- It is also possible to add other facies not found in the facies log if the user expects that not all facies to be modelled are available in the blocked well log.
**Important notice:**
The APS model will not use the facies log to condition the facies realization to the blocked well logs. It will only use the facies log to know which facies is observed and select the facies to be modelled. In APS, the well conditioning must be taken care of by the probability cubes for each facies, and grid cells belonging to blocked well grid cells can be given probability 1 or 0. This must be done in the workflow preparing the probability cubes.![](db7aaf81403660b23b789d76528a4d3491b364ed357a9c18049d528957529139.png)
