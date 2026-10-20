# APS XML Model File Reference

## Introduction

This document describes the APS (Adaptive Pluri-Gaussian Simulation) XML model format used by APS-Facies.
It consolidates all currently implemented XML syntax observed from APS example models and is intended as
reference for users, developers, FMU workflows, and future maintenance.

# APSModel

```xml
<APSModel version="1.0">
```

Observed supported versions:

```text
1.0
1.1
```

## Top-level Structure

```text
APSModel
├── JobName (optional)
├── Preview (optional)
├── Optimization (optional)
├── JobSettings (optional, v1.1)
├── SelectedZonesAndRegions (optional)
├── RMSProjectName
├── RMSWorkflowName (optional)
├── GridModelName
├── ZoneParamName
├── RegionParamName (optional)
├── ResultFaciesParamName
├── PrintInfo (optional)
├── SeedFile (optional)
├── WriteSeeds (optional)
├── MainFaciesTable
└── ZoneModels
```

# Preview

```xml
<Preview
    zoneNumber="1"
    regionNumber="0"
    crossSectionType="IJ"
    crossSectionRelativePos="0.5"
    scale="1.0"
    resolution="Normal"/>
```

# Optimization

```xml
<Optimization>
    <UseMemoization>1</UseMemoization>
    <MemoizationResolution>100</MemoizationResolution>
</Optimization>
```

# JobSettings

```xml
<JobSettings>
    <FmuSettings/>
    <RunSettings/>
    <TransformationSettings>0</TransformationSettings>
    <LogSetting>1</LogSetting>
</JobSettings>
```

## FmuSettings

### FmuMode

```text
OFF = ordinary mode
NOFIELDS = FMU uncertainty parameter mode
FIELDS = FMU assisted history matching mode
```

### ExchangeMode

```text
SIMULATE = always simulate/export GRFs
AUTO = use _ERT_ITERATION_NUMBER to switch between export/import
```

### FileFormat

```text
roff
```

### UpdateGRF

```xml
<UpdateGRF>
  <ErtBoxGrid>ERTBOX</ErtBoxGrid>
  <ExportErtBoxGrid>YES</ExportErtBoxGrid>
  <ExchangeMode>SIMULATE</ExchangeMode>
  <FileFormat>roff</FileFormat>
  <ExtrapolationMethod>repeat_layer_mean</ExtrapolationMethod>
</UpdateGRF>
```

### ExtrapolationMethod

```text
repeat_layer_mean
extend_layer_mean
constant
column_extrapolation
layer_average
```

### Additional FMU settings

```xml
<UseResidualFields>YES</UseResidualFields>
<UseNonStandardFMU>NO</UseNonStandardFMU>
<ExportConfigFiles>YES</ExportConfigFiles>
```

## RunSettings

MaxFractionNotNormalised and ToleranceLimitProbability control automatic probability normalization.

```xml
<RunSettings>
    <MaxFractionNotNormalised>0.1</MaxFractionNotNormalised>
    <ToleranceLimitProbability>0.2</ToleranceLimitProbability>
</RunSettings>
```

## TransformationSettings

```text
0 = Empirical transformation
1 = CDF transformation
```

## LogSetting

```text
0=OFF
1=ON
2=VERBOSE
3=VERY_VERBOSE
```

# MainFaciesTable

```xml
<MainFaciesTable blockedWell="BW" blockedWellLog="Facies">
```

Valid forms include:

```xml
blockedWell="BW" blockedWellLog="Facies"
blockedWell="" blockedWellLog=""
blockedWell="BW" blockedWellLog=""
```

## Facies

```xml
<Facies name="Channel">
   <Code>10</Code>
</Facies>
```

Facies names are arbitrary and codes only need to be unique.

# Zone Models

```xml
<Zone number="1">
```

or

```xml
<Zone number="1" regionNumber="2">
```

Zone numbering does not need to be sequential.

# GridLayout

Grid layout for a zone in the geomodel:

```text
BaseConform
Proportional
TopConform
```

# Facies Probabilities

## Constant

Inside `Zone`, set `UseConstProb` and provide probabilities for the zone's facies under `FaciesProbForModel`. Each facies name must also be defined in `MainFaciesTable`.

```xml
<UseConstProb>1</UseConstProb>
<FaciesProbForModel>
    <Facies name="F1"><ProbCube>0.4</ProbCube></Facies>
    <Facies name="F2"><ProbCube>0.6</ProbCube></Facies>
</FaciesProbForModel>
```

## Probability Cube

Use the same hierarchy with `UseConstProb` set to `0` and RMS property names instead of numeric probabilities:

```xml
<UseConstProb>0</UseConstProb>
<FaciesProbForModel>
    <Facies name="F1"><ProbCube>Prob_F1</ProbCube></Facies>
    <Facies name="F2"><ProbCube>Prob_F2</ProbCube></Facies>
</FaciesProbForModel>
```

## Probability Trend

A probability-trend property uses the same structure and `UseConstProb` value as a probability cube.
This define if the specified trend is a constant value or a name of a 3D property parameter.

# Gaussian Fields

```xml
<GaussField name="GRF1">
    <Vario name="EXPONENTIAL">
        <MainRange>1000.0</MainRange>
        <PerpRange>500.0</PerpRange>
        <VertRange>10.0</VertRange>
        <AzimuthAngle>0.0</AzimuthAngle>
        <DipAngle>0.0</DipAngle>
    </Vario>
    <SeedForPreview>12345</SeedForPreview>
</GaussField>
```

Names are arbitrary identifiers.

## Variogram Models

Supported:

```text
GAUSSIAN
EXPONENTIAL
GENERAL_EXPONENTIAL
MATERN32
MATERN52
SPHERICAL
```

### Common Parameters

```xml
<MainRange>
<PerpRange>
<VertRange>
<AzimuthAngle>
<DipAngle>
```

### GENERAL_EXPONENTIAL

```xml
<Power>1.6</Power>
```

## Trends

Supported trend types:

```text
Linear3D
Elliptic3D
Hyperbolic3D
EllipticCone3D
RMSTrendMap
RMSParameter
```

### Linear3D

```xml
<Trend>
 <Linear3D>
 </Linear3D>
</Trend>
```

### Elliptic3D

```xml
<Trend>
 <Elliptic3D>
 </Elliptic3D>
</Trend>
```

### Hyperbolic3D

```xml
<Trend>
 <Hyperbolic3D>
 </Hyperbolic3D>
</Trend>
```

### EllipticCone3D

```xml
<Trend>
 <EllipticCone3D>
   <relativeSize>0.5</relativeSize>
 </EllipticCone3D>
</Trend>
```

### RMSTrendMap

```xml
<Trend>
 <RMSTrendMap>
   <TrendMapName>TrendMap</TrendMapName>
   <TrendMapZone>A</TrendMapZone>
 </RMSTrendMap>
</Trend>
```

### RMSParameter

```xml
<Trend>
 <RMSParameter>
   <TrendParamName>CustomTrend</TrendParamName>
 </RMSParameter>
</Trend>
```

### Common Trend Parameters

```xml
origintype supports Relative and Absolute.
RelStdDev=0 means trend-only realization.
RMSTrendMap expands a 2D trend map through the zone.
RMSParameter uses RMS 3D parameter directly.
```

Keywords:

```xml
<azimuth>
<directionStacking>
<stackAngle>
<curvature>
<migrationAngle>
<origin_x>
<origin_y>
<origin_z_simbox>
<origintype>
```

Origin types:

```text
Relative
Absolute
```

## RelStdDev

```xml
<RelStdDev>0.0</RelStdDev>
```

Zero is valid.

# FMU Keywords

Any numeric parameter may expose an FMU keyword:

```xml
<MainRange kw="APS_..."></MainRange>
```

Examples include:

```xml
<MainRange kw="...">
<PerpRange kw="...">
<VertRange kw="...">
<AzimuthAngle kw="...">
<DipAngle kw="...">
<azimuth kw="...">
<stackAngle kw="...">
<curvature kw="...">
<migrationAngle kw="...">
<origin_x kw="...">
<origin_y kw="...">
<origin_z_simbox kw="...">
<RelStdDev kw="...">
```

# Truncation Rules

Supported:

```text
Trunc2D_Angle
Trunc2D_Cubic
Trunc3D_Bayfill
```

## Trunc2D_Angle

```xml
<Trunc2D_Angle nGFields="2">
```

```xml
<Facies name="A">
   <Angle>-50.0</Angle>
   <ProbFrac>1.0</ProbFrac>
</Facies>
```

## Trunc2D_Cubic

Hierarchy nodes:

```xml
<L1>
<L2>
<L3>
```

Directions:

```xml
direction="V"
direction="H"
```

`ProbFrac` and nested level elements may be interleaved, but their XML order determines the spatial order of subdivisions in the truncation map.

## Trunc3D_Bayfill

```xml
<Trunc3D_Bayfill nGFields="3">
```

Roles:

```xml
<Floodplain>
<Subbay>
<WBF>
<BHD>
<Lagoon>
```

Parameters:

```xml
<SF>
<YSF>
<SBHD>
```

# Overlay Model

```xml
<OverLayModel>
    <Group>
    </Group>
</OverLayModel>
```

A group may contain:

```xml
<AlphaField>
<BackGround>
<ProbFrac>
```

Multiple AlphaFields are allowed in one group and the same AlphaField may be reused in multiple groups.

# Example model file with multiple overlay facies

This illustrates a model with overlay facies.

```xml
<?xml version="1.0" ?>
<APSModel version="1.1">
  <Preview zoneNumber="1" regionNumber="0" crossSectionType="IJ" crossSectionRelativePos="0.5" scale="1.0" resolution="Normal"/>
  <RMSProjectName> testAPSWorkflow_update.rms15.2.1.0 </RMSProjectName>
  <GridModelName> GridModelFine </GridModelName>
  <ZoneParamName> Zone </ZoneParamName>
  <ResultFaciesParamName> aps_with_overlay_facies </ResultFaciesParamName>
  <JobSettings>
    <FmuSettings>
      <FmuMode>OFF</FmuMode>
    </FmuSettings>
    <RunSettings>
      <MaxFractionNotNormalised>0.1</MaxFractionNotNormalised>
      <ToleranceLimitProbability>0.2</ToleranceLimitProbability>
    </RunSettings>
    <TransformationSettings>0</TransformationSettings>
    <LogSetting>1</LogSetting>
  </JobSettings>
  <MainFaciesTable blockedWell="" blockedWellLog="">
    <Facies name="F1">
      <Code> 1 </Code>
    </Facies>
    <Facies name="F2">
      <Code> 2 </Code>
    </Facies>
    <Facies name="F3">
      <Code> 3 </Code>
    </Facies>
    <Facies name="F4">
      <Code> 4 </Code>
    </Facies>
    <Facies name="F5">
      <Code> 5 </Code>
    </Facies>
    <Facies name="F6">
      <Code> 6 </Code>
    </Facies>
    <Facies name="F7">
      <Code> 7 </Code>
    </Facies>
    <Facies name="F8">
      <Code> 8 </Code>
    </Facies>
  </MainFaciesTable>
  <ZoneModels>
    <Zone number="1">
      <UseConstProb> 1 </UseConstProb>
      <SimBoxThickness> 4.924121201038361 </SimBoxThickness>
      <FaciesProbForModel>
        <Facies name="F1">
          <ProbCube> 0.33333333333333326 </ProbCube>
        </Facies>
        <Facies name="F2">
          <ProbCube> 0.2222222222222222 </ProbCube>
        </Facies>
        <Facies name="F3">
          <ProbCube> 0.1111111111111111 </ProbCube>
        </Facies>
        <Facies name="F4">
          <ProbCube> 0.1111111111111111 </ProbCube>
        </Facies>
        <Facies name="F5">
          <ProbCube> 0.1111111111111111 </ProbCube>
        </Facies>
        <Facies name="F6">
          <ProbCube> 0.1111111111111111 </ProbCube>
        </Facies>
      </FaciesProbForModel>
      <GaussField name="GRF1">
        <Vario name="SPHERICAL">
          <MainRange> 1000.0 </MainRange>
          <PerpRange> 500.0 </PerpRange>
          <VertRange> 5.0 </VertRange>
          <AzimuthAngle> 35.0 </AzimuthAngle>
          <DipAngle> 0.0 </DipAngle>
        </Vario>
        <Trend>
          <Linear3D>
            <azimuth> 35.0 </azimuth>
            <directionStacking> 1 </directionStacking>
            <stackAngle> 2.0 </stackAngle>
          </Linear3D>
        </Trend>
        <RelStdDev> 0.07 </RelStdDev>
        <SeedForPreview> 1764854304363196400 </SeedForPreview>
      </GaussField>
      <GaussField name="GRF2">
        <Vario name="GAUSSIAN">
          <MainRange> 500.0 </MainRange>
          <PerpRange> 500.0 </PerpRange>
          <VertRange> 5.0 </VertRange>
          <AzimuthAngle> 0.0 </AzimuthAngle>
          <DipAngle> 0.0 </DipAngle>
        </Vario>
        <SeedForPreview> 6356633537831649000 </SeedForPreview>
      </GaussField>
      <GaussField name="GRF3">
        <Vario name="GAUSSIAN">
          <MainRange> 500.0 </MainRange>
          <PerpRange> 100.0 </PerpRange>
          <VertRange> 5.0 </VertRange>
          <AzimuthAngle> 35.0 </AzimuthAngle>
          <DipAngle> 0.0 </DipAngle>
        </Vario>
        <SeedForPreview> 9392127180480418000 </SeedForPreview>
      </GaussField>
      <GaussField name="GRF4">
        <Vario name="SPHERICAL">
          <MainRange> 1500.0 </MainRange>
          <PerpRange> 250.0 </PerpRange>
          <VertRange> 5.0 </VertRange>
          <AzimuthAngle> 125.0 </AzimuthAngle>
          <DipAngle> 0.0 </DipAngle>
        </Vario>
        <Trend>
          <Elliptic3D>
            <azimuth> 315.0 </azimuth>
            <directionStacking> 1 </directionStacking>
            <stackAngle> 0.1 </stackAngle>
            <curvature> 1.0 </curvature>
            <origin_x> 1.0 </origin_x>
            <origin_y> 0.5 </origin_y>
            <origin_z_simbox> 0.5 </origin_z_simbox>
            <origintype> Relative </origintype>
          </Elliptic3D>
        </Trend>
        <RelStdDev> 0.05 </RelStdDev>
        <SeedForPreview> 15064812253853028000 </SeedForPreview>
      </GaussField>
      <GaussField name="GRF5">
        <Vario name="GAUSSIAN">
          <MainRange> 1500.0 </MainRange>
          <PerpRange> 500.0 </PerpRange>
          <VertRange> 5.0 </VertRange>
          <AzimuthAngle> 125.0 </AzimuthAngle>
          <DipAngle> 0.0 </DipAngle>
        </Vario>
        <SeedForPreview> 6409082950683197000 </SeedForPreview>
      </GaussField>
      <GaussField name="GRF6">
        <Vario name="SPHERICAL">
          <MainRange> 750.0 </MainRange>
          <PerpRange> 250.0 </PerpRange>
          <VertRange> 5.0 </VertRange>
          <AzimuthAngle> 350.0 </AzimuthAngle>
          <DipAngle> 0.0 </DipAngle>
        </Vario>
        <SeedForPreview> 2982274794537668600 </SeedForPreview>
      </GaussField>
      <GaussField name="GRF7">
        <Vario name="GAUSSIAN">
          <MainRange> 1000.0 </MainRange>
          <PerpRange> 1000.0 </PerpRange>
          <VertRange> 5.0 </VertRange>
          <AzimuthAngle> 0.0 </AzimuthAngle>
          <DipAngle> 0.0 </DipAngle>
        </Vario>
        <SeedForPreview> 4820419087957541000 </SeedForPreview>
      </GaussField>
      <TruncationRule>
        <Trunc2D_Cubic nGFields="7">
          <BackGroundModel>
            <AlphaFields> GRF1 GRF2 </AlphaFields>
            <L1 direction="V">
              <ProbFrac name="F1"> 1.0 </ProbFrac>
              <ProbFrac name="F2"> 1.0 </ProbFrac>
            </L1>
          </BackGroundModel>
          <OverLayModel>
            <Group>
              <AlphaField name="GRF3">
                <TruncIntervalCenter> 0.0 </TruncIntervalCenter>
                <ProbFrac name="F3"> 0.8 </ProbFrac>
              </AlphaField>
              <AlphaField name="GRF4">
                <TruncIntervalCenter> 0.0 </TruncIntervalCenter>
                <ProbFrac name="F4"> 1.0 </ProbFrac>
              </AlphaField>
              <AlphaField name="GRF5">
                <TruncIntervalCenter> 0.0 </TruncIntervalCenter>
                <ProbFrac name="F5"> 1.0 </ProbFrac>
              </AlphaField>
              <BackGround> F1 </BackGround>
            </Group>
            <Group>
              <AlphaField name="GRF6">
                <TruncIntervalCenter> 0.0 </TruncIntervalCenter>
                <ProbFrac name="F6"> 0.5 </ProbFrac>
              </AlphaField>
              <AlphaField name="GRF7">
                <TruncIntervalCenter> 0.0 </TruncIntervalCenter>
                <ProbFrac name="F6"> 0.5 </ProbFrac>
              </AlphaField>
              <AlphaField name="GRF4">
                <TruncIntervalCenter> 0.0 </TruncIntervalCenter>
                <ProbFrac name="F3"> 0.2 </ProbFrac>
              </AlphaField>
              <BackGround> F2 </BackGround>
            </Group>
          </OverLayModel>
        </Trunc2D_Cubic>
      </TruncationRule>
    </Zone>
  </ZoneModels>
</APSModel>
```
