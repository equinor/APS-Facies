---
title: Probability logs
---
For facies interpretation without uncertainties, blocked well set of facies logs can be used.
Probability logs will then be defined as logs with probability value 1 if the facies is present and 0 if not present.
In this case we assume that $P(\text{modelled facies} \mid \text{interpreted facies}) = 1$ if modelled facies is equal to interpreted facies and $0$ if not.

If facies interpretation is not certain, but a conditional probability for it is specified such that $P(\text{modelled facies} \mid \text{interpreted facies})$ is known for all modelled facies and interpreted facies, it is possible to assign a probability reflecting uncertainty in the facies interpretation of the blocked well facies log.

Some help scripts from the APS toolbox is available for this task, see APS toolbox -> Probability logs.

Example of a blocked well facies log and overprinted by the probability log (with value 0 or 1) for one of the facies types.

![](assets/images/d564dee105ddcf02fdacd5e144f3a70acb8aafa478c17624a2817290a9345965.png)

If blocked well grid cells are larger than typical length of facies intervals in the original facies log, it is possible to calculate the volume fraction of facies from facies logs in each blocked well grid cells and use the volume fraction of each facies as the facies probability for the blocked well grid cells.

## Facies log

## Conditional probabilities given facies

If the facies interpretation is uncertain or the facies log is a blocked well facies log where the majority rule is applied to pick the upscaled facies type from the original facies log, the blocked well facies probability may not have to be 0 or 1.

Alternative approaches here can be:

- Estimate volume fraction of each facies from fine scale facies log within each blocked well grid cell and use the fraction as facies probability for that grid cell.

- Use the RMS well blocking for facies logs and assign a conditional probability for modelled facies given the interpreted facies.

### Example with conditional probability specification
Example of use of conditional facies probability can be interpretation of two types of sand facies where core data can distinguish between them, but log data have problems distinguishing between the two sand facies.
Assume a case where interpreted facies types are: $\text{sand}$, $\text{sand}_A$, $\text{sand}_B$.
If the user wants to model facies $\text{sand}_A$ and $\text{sand}_B$ but from logs only facies $\text{sand}$ can be interpreted, specification like this may be an alternative:

For measured depth intervals with logs only the probability log values are defined by:

$$\begin{eqnarray}
    P(\text{modelled facies sand}_A \mid \text{interpreted facies sand}) = PA \\
    P(\text{modelled facies sand}_B \mid \text{interpreted facies sand}) = PB \\
\end{eqnarray}$$

where $PA + PB = 1$ and $0 < PA < 1$ and $0 < PB < 1$ is estimated or specified by user.


For measured depth intervals with high certainty (e.g. cored intervals) where $\text{sand}_A$ and $\text{sand}_B$ are interpreted:

$$\begin{eqnarray}
    P(\text{modelled facies sand}_A \mid \text{interpreted facies sand}_A) = 1 \\
    P(\text{modelled facies sand}_B \mid \text{interpreted facies sand}_A) = 0 \\
\end{eqnarray}$$

and

$$\begin{eqnarray}
    P(\text{modelled facies sand}_A \mid \text{interpreted facies sand}_B) = 0 \\
    P(\text{modelled facies sand}_B \mid \text{interpreted facies sand}_B) = 1 \\
\end{eqnarray}$$
