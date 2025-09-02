---
title: Conditional probabilities given facies
---
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
