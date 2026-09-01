---
title: Estimate and create blocked well probability logs from original facies logs
---

## Utility script to create blocked well probability logs by estinmating volume fractions from original facies logs

**Description**
: Python script to create both facies probability logs on original facies log scale and for blocked wells.
Estimate probability of each facies within each blocked well grid cell from original facies log.
The method is to calculate the fraction of each facies that is present within each blocked well grid cell and use that as the estimate of facies probability.
The main difference between this approach and the script that create probability logs from blocked well facies logs is that it takes into account the facies
fraction within each blocked well grid cell instead of first blocking the facies log. Blocking the facies log uses the _majority_ rule which means that
the facies with largest volume fraction will 'win' and the blocked well grid cell will be assigned to that facies.

**Dependency**
: The API `rmsapi` following the RMS installation and the python module `aps.toolbox` following the APS plugin installation.

**Input**
: Original scale facies logs, blocked well set for grid model, well names, facies names and other model parameter settings.

**Output**
: One blocked logs and original scale well logs for facies probabilities per facies.

**Usage of the probability logs**
: A probability log containing only 0 or 1 can be used to condition probability cubes to reproduce blocked well facies logs 100% while
probabilities between 0 and 1 represents uncertainties in blocked well facies.

### Alternative ways to implement the use of this script

The utility script `prob_logs_from_original_facies_logs.py`:

- Make your own Python script and specify the keyword `model_file_name` and a yml model file specifying the input.

!!! NOTE

    Use the Python script as a Python job in RMS since it applies the API `rmsapi` from RMS.

### Steps in the algorithm that calculates the blocked well probability logs:

**First probability logs on original facies log scale is created.**
: Probability logs on same scale/resolution as the original facies logs are created and made available together with the other well logs.
This step will per default assign 1 or 0 or missing code for points along the well path.
For instance, if facies A, B and C are present in the zone, and A and B are chosen to be modelled facies for the zone, the probability log for
facies A will get value 1 for points along the well path where facies log has facies A and 0 for points where facies log has facies B and missing code for
points where facies code is C. For the probability log for facies B it is the opposite way around with value 1 where B is present and 0 where A is present.

**Option to merge original facies together.**
: No new facies log will be created but the combination of multiple facies codes is used
when creating the probability logs on original scale. The specified name for the combined facies will be used in the name for the facies probability log.
For instance, if original facies codes are 1 for facies A1 and 2 for facies A2 are
to be treated as the same modelled facies A, the user can specify that these two facies codes represents the same new facies A when calculating probability logs.

**Option to use conditional probabilities**
: This option is an alternative way to define probability logs on original facies log scale.
For the example with two modelled facies A and B, this means that instead of assigning 1 for modelled facies A (denoted by $A_{m}$)
where facies A is observed in the log (denoted by $A_{l}$), the probability for facies $A_{m}$ can be specified depending on the observed facies
in the facies log. The user can specify the conditional probabilities $P(A_{m} | A_{l})$ and $P(A_{m} | B_{l})$.
In this case with $A_{m}$ and $B_{m}$ as modelled facies, the probabilities must be normalized such that

    $P(A_{m} | A_{l}) + P(B_{m} | A_{l}) = 1$<br>
    $P(A_{m} | B_{l}) + P(B_{m} | B_{l}) = 1$<br>

There can of course be more facies in the facies log than number of modelled facies,
but the conditional probabilities given the observed/interpreted facies must be normalized.

**Well blocking.**
: When probability logs in original facieslog scale is defined,
the method will use blocked well upscaling with arithmetic average to calculate
blocked well probability logs from original scale probability logs. So, if the original probability logs contains 1 or 0
for each individual well path point, the upscaled value for the facies probabilities will be the fraction or proportion
of the original facies within each blocked well grid cell. If conditional probabilities are used for original scale probability logs, the
blocked well probability logs will contain the average probability of each facies within each blocked well grid cell.

**Option to use bias weighting in well blocking.**
: It is possible to specify _bias weighting_ with original facies log.
This means that when calculating the average of the facies probability within a blocked well cell using arithmetic average,
it is possible with bias weighting to assign different weights to each point along the well path for the original scale
facies probability logs depending on the original facies for that point. This bias weighting is the same as the one that is available in RMS
if the user wants to upscale a petrophysical log for a blocked well grid cell by assigning higher weight to some facies relative to other facies.
This bias weighting can be used to increase probability of important facies having low volume fraction but significant effect on fluid flow like
thin shale barriers.

**Option to use majority weighting using facies with largest probability.**
: The last option in well blocking of facies probability logs is to assign the facies probability
to the blocked well to 1 for the facies with max probability. This option is similar to the alternative to first block the facies log and then
assign probability to the facies in the blocked well grid cell to 1 and 0 to the other blocked well probability logs.

**Vertical proportion curves for facies probabilities.**
: There is also an option for a specified zone to calculate average grid layer per grid layer of blocked well facies
probability logs to get an estimate of vertical proportion curves (VPC) for the zone. Note that this VPC estimate is based
on the estimated facies probability logs, not directly based on the blocked well facies logs.
The result is written to ascii files and contains one line per grid layer for the zone with the average facies probabilities for all specified wells.

## Additional tools to help visualizing the result

A script with a _yml_ config file input exists for the purpose to read the blocked well facies probability logs from the RMS project
and plot the facies probability logs for each of the specified wells. An option is here also to plot the calculated estimate of
VPC by reading the files and plot it. More about this tool later in this documentation.

## How to use the script **estimate_prob_logs**

- The script is run as an RMS python job. The user will need a small python script to
  assign input (a python dictionary) specifying the name of the yml configuration file.
  It will use rmsapi to access the well logs (the facies logs) and add probability logs to the wells.
  It will automatically create and run rms jobs for well blocking of original scale probability logs to get blocked well probability logs.

- The input to the script will be a configuration file in _yml_ format with a set of
  keywords defining the settings.

- The output will be estimated original scale facies probability logs added to the
  specified wells in the RMS project and blocked well facies probability logs added to the specified blocked well set and grid.

- There is an option to also calculate VPC based on the blocked well facies probability logs.

## Example of a small python script that is to be run in RMS as a python job to run this estimate:

```python
# Test script for prob_logs_from_original_facies_logs.py

from aps.toolbox import prob_logs_from_original_facies_logs
params = {
    'project': project,
    'model_file': '../input/config/aps/estimate_prob_logs_drogon.yml',
}
prob_logs_from_original_facies_logs.run(params)
```

## The specification of the configuration file for the script to estimate blocked well facies probability logs

Example configuration file in yml format:

```yml
# estimate_prob_logs_drogon.yml

EstimateBlockedWellProbLogs:
  OutputPrefix: ProbNew
  DebugLevel: 2

  # Specify which facies to be used in modelling for each zone.
  # Probability logs for these facies will be made and if other facies exists
  # in the facies log within the zone, the probability logs will be set to undefined for them.
  ModellingFaciesPerZone:
    1: Floodplain Channel Crevasse Coal

  SimBoxThicknessPerZone:
    1: 16.9

  ProbFromOriginalFaciesLog:
    # List of well names to include when calculating probability logs.
    # Wildcard notation is possible. The same Trajectory name and
    # log run name will be used for all selected wells.
    Wells:
      [
        '55_33-1',
        '55_33-2',
        '55_33-3',
        '55_33-A-1',
        '55_33-A-2',
        '55_33-A-3',
        '55_33-A-4',
        '55_33-A-5',
        '55_33-A-6',
      ]
    TrajectoryName: 'Drilled trajectory'
    LogRun: log
    FaciesLogName: Facies
    ZoneLogName: Zone
    # Optional keyword MergeFacies. Specified facies names must exist in facies log.
    # For each facies code in the facies log a facies name is specified. If one wants to merge
    # some facies together with other facies, specify the same facies name for multiple facies codes.
    # The merging will not create any new facies log, but will be used when calculating probability logs.
    #MergeFacies:
    # 0: Floodplain
    # 1: Channel
    # 2: Crevasse
    # 5: Coal

    # Optional keyword ProbCondMatrix. Specified facies names must exist in facies log.
    # The conditional probability for modelled facies given zone and intepreted facies.
    # P(modelled_facles | zone, interpreted_facies) is
    # specified by (zone, modelled_facies, interpreted_facies): prob
    # The zone number can be replaced by a * if all zones have the
    # same facies and the same conditional probability can be used.
    # If the ProbCondMatrix is not used, the probability logs will contain 1 or 0 or undefined value.
    ProbCondMatrix:
      (1, Floodplain, Floodplain): 1.0
      (1, Channel, Floodplain): 0.0
      (1, Coal, Floodplain): 0.0
      (1, Crevasse, Floodplain): 0.0

      (1, Floodplain, Channel): 0.0
      (1, Channel, Channel): 1.0
      (1, Coal, Channel): 0.0
      (1, Crevasse, Channel): 0.0

      (1, Floodplain, Coal): 0.0
      (1, Channel, Coal): 0.0
      (1, Coal, Coal): 1.0
      (1, Crevasse, Coal): 0.0

      (1, Floodplain, Crevasse): 0.0
      (1, Channel, Crevasse): 0.0
      (1, Coal, Crevasse): 0.0
      (1, Crevasse, Crevasse): 1.0

  BlockedWellProbLogs:
    GridModelName: Geogrid_Valysar
    ZoneParamName: Zone
    AverageProbLogPrefix: vpc
    BlockedWellZoneLogName: Zone

    # If blocked well zone log does not match the grid zones perfectly,
    # choose to extract a blocked well zone log from a zone parameter and use that instead to avoid
    # blocked well grid cells with undefined values for the probability logs near the zone boundaries.
    # The specified blocked well jobs to use to block the probability logs.
    # The probability logs based on original facies log will be created or updated.
    # There is no need to specify any well blocking for the probability logs. This script
    # will both calculate probability logs on the same scale as the original facies logs,
    # add the probability logs for the selected logs to be blocked and use the arithmetic average
    # method for well blocking of the probability logs. The blocked well jobs will be
    # automatically updated
    BlockedWellJobNames: [bw_valysar_vertical, bw_valysar_horizontal]

    BiasWeighting:
      Floodplain: 1.0
      Channel: 1.0
      Crevasse: 1.0
      Coal: 1.0

    UseOnlyMaxProb: False
```

## Description of the keywords

Following the main keyword **EstimateBlockedWellProbLogs** are the following keywords:

```yml
OutputPrefix: <prefix of new probability logs>
DebugLevel:  <number from 0 to 2 defining amount of output to screen>
ModellingFaciesPerZone:
    <zone_number>: <list of facies names to be used as modelled facies for this zone>
    <zone_number>: <list of facies names to be used as modelled facies for this zone>
    (Multiple zones can be specified, one line per zone)

SimBoxThicknessPerZone:
    <zone_number>: <float number with average simulation box thickness of the zone>
    <zone_number>: <float number with average simulation box thickness of the zone>
    (Multiple zones can be specified, one line per zone and for same set of zones as in ModellingFaciesPerZone>)

ProbFromOriginalFaciesLog:
    Wells: <list of well names>
    TrajectoryName: 'Drilled_trajectory'  (This may be different, check the RMS project)
    LogRun: 'log'                         (This may be different, check the RMS project)
    FaciesLogName: 'Facies'               (This may be different, check the RMS project)
    ZoneLogName: 'Zone'                   (This may be different, check the RMS project)

    MergeFacies:  (Optional. This example show that both code 0 and 6 should be facies Floodplain, 2 and 8 should be Channel)
        0:  Floodplain
        1:  Channel
        2:  Crevasse
        5:  Coal
        6:  Floodplain
        8:  Channel
    ProbCondMatrix: (Specify conditional probability for modelled facies in specified zone given observed facies in log)
        (1,Floodplain, Floodplain): 0.9 (Probability for modelled facies Floodplain for zone 1 given observed facies Floodplain in facies log)
        (1, Channel, Floodplain): 0.0
        (1, Coal, Floodplain): 0.0
        (1, Crevasse, Floodplain): 0.1  (Probability for modelled facies Crevasse for zone 1 given observed facies Floodplain in facies log)
              (Specify this for all zones for all modelled facies given the observed facies)

BlockedWellProbLogs:
    GridModelName: <name of grid model>
    ZoneParamName: <Name of zone parameter for the grid>
    AverageProbLogPrefix: <prefix of name for vertical proportion curves>
    BlockedWellZoneLogName: <Name of blocked well log with zone code for the grid>

BlockedWellJobNames: <List of blocked well JOB names>

BiasWeighting:  (Optional keyword, default is equal weight for each facies)
    <Facies name>: <Relative weight (float number)>
    <Facies name>: <Relative weight (float number)>
    (Multiple lines, one per modelled facies)

UseOnlyMaxProb: <True or False, Default False>
```

## Script to plot the result from the script to estimate blocked well facies probabilities

**Description**
: Plot estimated blocked well facies probability logs and VPC curves using matplotlib.
This script (plot_prob_curves) should be run from a small python script defined as a python job in RMS.
The user will have to specify a small python script to define a python dictionary which is used to specify
the name of the yml configuration file for this script.

**Dependency**
: The API `rmsapi` following the RMS installation and the python module `aps.toolbox` following the APS plugin installation.

**Input**
: Well names, probability log names, zone log name, grid model name and other settings

**Output**
: Visualize probability logs or vertical proportion curves using matplotlib.

Example of the python script to be run as a python job in RMS:

```python
# Test script to plot facies probability logs for blocked wells and optionally VPC curves.
from aps.toolbox import visualize_prob_curves

params = {
    'project': project,
    'model_file_name': '../input/config/aps/plot_prob_curves.yml',
}

visualize_prob_curves.run(params)
```

Example of the configuration file for the plotting script:

Description of keywords:

```yml
Following main keyword PlotProbLogs are:
  PlotEstimatedVPC: <True/False>  (Choose between plotting blocked well facies probability logs or estimated VPC for zone)
  WellList: <list of wellnames>
  ProbLogNames: <list of blocked well probability log names>
  ZoneLogName: <Name of zone log for blocked wells>
  MaxZoneNumber: <zones are assumed to be in increasing order and this is max zone number>
  GridModelName: <Name of grid model>
  BlockedWellSetName: <Name of blocked well set for the grid model>
  AverageProbLogPrefix: <Prefix name for VPC files generated by the estimate prob log script>
  AverageProbLogFilePath: <relative path to where the VPC files are saved>
  ZoneName: <Name of zone>
  Facies: <List of modelled facies>
```
