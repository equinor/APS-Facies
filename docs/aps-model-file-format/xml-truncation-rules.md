# APS Truncation Rules

## Overview

Truncation rules convert Gaussian random field (GRF) values into facies.

Supported truncation models:

```text
Trunc2D_Angle
Trunc2D_Cubic
Trunc3D_Bayfill
```

A truncation rule is defined within a zone model:

```xml
<TruncationRule>
    ...
</TruncationRule>
```

# Common Concepts

## nGFields

Defines the total number of Gaussian fields used by the truncation model.

```xml
<Trunc2D_Angle nGFields="4">
```

```xml
<Trunc2D_Cubic nGFields="2">
```

```xml
<Trunc3D_Bayfill nGFields="3">
```

## AlphaFields

Lists Gaussian fields used by the truncation rule.

```xml
<AlphaFields>GRF1 GRF2</AlphaFields>
```

```xml
<AlphaFields>GRF1 GRF2 GRF3</AlphaFields>
```

The ordering is significant.

## BackGroundModel

```xml
<BackGroundModel> ... </BackGroundModel>
```

This keyword define two Alpha fields and which facies is defined by the truncation map
defined by the two alpha axes. This keyword is common for all truncation rule and is required.

# Trunc2D_Angle

Defines facies polygons using orientation angles and subdivide the unit square truncation map into disjoint polygons.

## Structure

```xml
<Trunc2D_Angle nGFields="2">/
    <BackGroundModel>
        <AlphaFields>GRF1 GRF2</AlphaFields>
        <UseConstTruncParam>1</UseConstTruncParam>
        <Facies name="Sand">
            <Angle>45.0</Angle>
            <ProbFrac>1.0</ProbFrac>
        </Facies>
        <Facies name="Shale">
            <Angle>-45.0</Angle>
            <ProbFrac>1.0</ProbFrac>
        </Facies>
    </BackGroundModel>
</Trunc2D_Angle>
```

## Keywords

### Facies

```xml
<Facies name="Sand">
```

Defines one truncation polygon.

### Angle

```xml
<Angle>45.0</Angle>
```

Polygon orientation. Possible values for the angle is from -180 degrees to 180 degrees.

### ProbFrac

```xml
<ProbFrac>1.0</ProbFrac>
```

Probability fraction allocated to the facies for the polygon. If all polygons have a unique facies, this will be 1.0.
If two or more polygons are associated to the same facies, the probability fraction must be a fraction and the sum over
all polygons associated to the same facies must be 1. This fraction defines how large proportion of the facies probability
is allocated to each polygon. For instance if a facies has probability 0.7 and there are two polygons with this facies
with fraction 0.2 and 0.8, then the facies probability or area of the two polygons in the truncation map are 0.7 * 0.2 and 0.7 * 0.8

### UseConstTruncParam

Keyword used under keyword BackGroundModel for truncation rule Trunc2D_Angle.
It is 1 if the angles are constants and 0 if the angles are 3D parameters with a trend.
Only constant is implemented in the GUI so far.

```xml
<UseConstTruncParam>1</UseConstTruncParam>
```

# Trunc2D_Cubic

Hierarchical (nested) subdivision of truncation map. There can be a total of 3 levels.

## Structure

```xml
<Trunc2D_Cubic nGFields="2">
    <BackGroundModel>
        <AlphaFields>GRF1 GRF2</AlphaFields>
        <L1 direction="V">
            <ProbFrac name="A">1.0</ProbFrac>
            <L2>
                <ProbFrac name="B">1.0</ProbFrac>
                <ProbFrac name="C">1.0</ProbFrac>
            </L2>
        </L1>
    </BackGroundModel>
</Trunc2D_Cubic>
```

## Hierarchy Levels

The three levels are specified with the keywords where L2 always is within L1 and L3 is always inside L2.

```xml
<L1>
<L2>
<L3>
```

## Direction Attribute

```xml
direction="V"
direction="H"
```

| Value | Meaning                |
| ----- | ---------------------- |
| V     | Vertical subdivision   |
| H     | Horizontal subdivision |

## ProbFrac

Specify facies name for each polygon and the probability fraction.

```xml
<ProbFrac name="A">1.0</ProbFrac>
```

### Attributes

| Attribute | Description                  |
| --------- | ---------------------------- |
| name      | Facies assigned to partition |

### Value

Probability fraction allocated to the polygon. The probability fraction is always 1.0 if there is a unique facies for each polygon, but if there are multiple polygons with the same facies, the probability fraction must sum up to 1.0 over all polygons with the same facies.

## Ordering Rules

The hierarchy is specified first by level 1, L1 keyword with an attribute direction. Within this the probFrac keyword with facies name as attribute and value equal to the probability fraction is specified. Level 2, L2 keyword may follow in the same way and level 3, L3 keyword inside L2 again like e.g. this:

```xml
<L1 direction="H">
    <ProbFrac name="F1"> 0.4 </ProbFrac>
    <L2>
        <ProbFrac name="F2"> 1.0 </ProbFrac>
        <L3>
            <ProbFrac name="F3"> 1.0 </ProbFrac>
            <ProbFrac name="F1"> 0.6 </ProbFrac>
        </L3>
    </L2>
</L1>
```

The order of keyword ProbFrac and level keyword can be in any order. Each level can consist of 2 or more subdivisions where one or more
of the subdivisions can be associated to a facies or a new polygon that is further subdivided into new polygons
or associated with a facies. Number of level is maximum 3.

## Repeated Facies

The same facies may occur multiple times within the hierarchy.

## Advanced Example

```xml
<L1 direction="V">
    <L2>
        <ProbFrac name="F1">0.4</ProbFrac>
        <ProbFrac name="F2">1.0</ProbFrac>
    </L2>
    <L2>
        <ProbFrac name="F3">1.0</ProbFrac>
        <L3>
            <ProbFrac name="F4">1.0</ProbFrac>
            <ProbFrac name="F1">0.6</ProbFrac>
        </L3>
    </L2>
</L1>
```

# Trunc3D_Bayfill

Bayfill depositional truncation rule. This is a specific truncation rule initially designed for Bayfill depositions. There are 5 facies.
There are 5 types of facies called roles, and for each role a user specified facies name is associated.

## Structure

```xml
<Trunc3D_Bayfill nGFields="3">
    <BackGroundModel>
        <AlphaFields>GRF1 GRF2 GRF3</AlphaFields>
        <Floodplain>F1</Floodplain>
        <Subbay>F2</Subbay>
        <WBF>F3</WBF>
        <BHD>F4</BHD>
        <Lagoon>F5</Lagoon>
        <SF>0.5</SF>
        <YSF>0.4</YSF>
        <SBHD>0.3</SBHD>
    </BackGroundModel>
</Trunc3D_Bayfill>
```

## Facies Role Keywords

```xml
<Floodplain>
<Subbay>
<WBF>
<BHD>
<Lagoon>
```

| Keyword    | Description                    |
| ---------- | ------------------------------ |
| Floodplain | Floodplain facies              |
| Subbay     | Subbay facies                  |
| WBF        | Wave influenced bayfill facies |
| BHD        | Bayhead delta facies           |
| Lagoon     | Lagoon facies                  |

## Geometry Parameters

### SF

```xml
<SF>0.5</SF>
```

### YSF

```xml
<YSF>0.4</YSF>
```

### SBHD

```xml
<SBHD>0.3</SBHD>
```

These parameters control bayfill geometry.

# Overlay facies which extend the truncation rules into a N-dimensional truncation cube

Overlay facies are evaluated after background truncation. The term, overlay indicates that the facies specified here are put on top of other facies.
The keyword 'OverLayModel' is at the same level as 'BackGroundModel' and extend the truncation rule into a truncation cube.

## Structure

```xml
<OverLayModel>

    <Group>
        ...
    </Group>

</OverLayModel>
```

## Group

A group may contain of definition of which transformed GRF is used for the new facies or new axes of the truncation cube.
Background facies is specified by two alpha fields (transformed GRF fields). Additional new alpha fields can be introduced. For each new alpha,
one can specify overlay facies to be located within one or more background facies. A threshold value subdivide the new alpha value axis
into two intervals where one of the intervals is associated with the overlay facies and the other interval means that no overlay facies
is located and the background facies is kept.The volume defined by the area covered by the background facies the overlay facies is said
to be located within multiplied with the length of the one-dimensional interval along the new alpha axis that is associated with
the overlay facies, represents the facies probability for the overlay facies.
Note that it is possible to have multiple alpha fields to define overlay facies over the same group of background facies.
In this case a priority rule is used and the first one has highest priority and the last one lowest priority.

```xml
<AlphaField>
<BackGround>
<ProbFrac>
```

## AlphaField

```xml
<AlphaField name="GRF3">

    <TruncIntervalCenter>0.2</TruncIntervalCenter>

    <ProbFrac name="OverlayFacies">0.5</ProbFrac>

</AlphaField>
```

### Attribute

```xml
name
```

Gaussian field used for overlay evaluation.

### TruncIntervalCenter

Specifies the center of the 1D interval between 0 and 1 for an alpha field which corresponds to the overlay facies.

```xml
<TruncIntervalCenter>0.2</TruncIntervalCenter>
```

Observed values are arbitrary floating-point value between 0 and 1.

### ProbFrac

```xml
<ProbFrac name="OverlayFacies">0.5</ProbFrac>
```

Probability for an overlay facies.

## BackGround

```xml
<BackGround>Sand</BackGround>
```

Background facies affected by the overlay.

Multiple background facies are allowed:

```xml
<BackGround>F1</BackGround>
<BackGround>F2</BackGround>
<BackGround>F3</BackGround>
```

## Multiple AlphaFields

A group may contain several AlphaFields.

```xml
<Group>
    <AlphaField name="GRF3"/>
    <AlphaField name="GRF5"/>
</Group>
```

## Reuse of AlphaFields

The same Gaussian field may be reused in multiple groups.

## Multiple Groups

```xml
<OverLayModel>

    <Group>...</Group>

    <Group>...</Group>

</OverLayModel>
```
