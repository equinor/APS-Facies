---
title: Conditional probabilities given facies
---
If the facies interpretation is uncertain or the facies log is a blocked well facies log where the majority rule is applied to pick the upscaled facies type from the original facies log, the blocked well facies probability may not have to be 0 or 1.Alternative approaches here can be:- Estimate volume fraction of each facies from fine scale facies log within each blocked well grid cell and use the fraction as facies probability for that grid cell.

- Use the RMS well blocking for facies logs and assign a conditional probability for modelled facies given the interpreted facies.

**Example with conditional probability specification**Example of use of conditional facies probability can be interpretation of two types of sand facies where core data can distinguish between them, but log data have problems distinguishing between the two sand facies. Assume a case where interpreted facies types are:
_sand, sand_A, sand_B_
. If the user wants to model facies
_sand_A_
and
_sand_B_
 but from logs only facies
_sand_
can be interpreted, specification like this may be an alternative:
For measured depth intervals with logs only the probability log values are defined by: P(modelled facies
_sand_A_
| interpreted facies
_sand_
) = PA P(modelled facies
_sand_B_
| interpreted facies
_sand_
) = PBwhere PA + PB = 1 and 0 < PA < 1 and 0 < PB < 1 is estimated or specified by user.
For measured depth intervals with high certainty (e.g. cored intervals) where
_sand_A_
and
_sand_B_
are interpreted:P(modelled facies
_sand_A_
| interpreted facies
_sand_A_
) = 1P(modelled facies
_sand_B_
| interperted facies
_sand_A_
) = 0andP(modelled facies
_sand_A_
| interpreted facies
_sand_B_
) = 0P(modelled facies
_sand_B_
| interperted facies
_sand_B_
) = 1
