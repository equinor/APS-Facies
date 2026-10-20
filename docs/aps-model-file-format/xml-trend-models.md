# APS Trend Models

## Overview

Trend models introduce deterministic spatial variation into Gaussian random fields (GRFs). A trend is defined inside a Gaussian field definition.

```xml
<GaussField name="GRF1">
    <Trend>
        ...
    </Trend>
</GaussField>
```

Supported trend types where 4 first are analytical parameterized trends while the last two take as input user defined trends.

```text
Linear3D
Elliptic3D
Hyperbolic3D
EllipticCone3D
RMSTrendMap
RMSParameter
```

# Common Trend Parameters

Analytical trend models may use the following sub-keywords:

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

## Parameter descriptions

| Parameter         | Description                                                          |
| ----------------- | -------------------------------------------------------------------- |
| azimuth           | Trend orientation in map view. Depositional direction                |
| directionStacking | Stacking direction selector (Progradation, Retrogradation)           |
| stackAngle        | Dip/stacking angle                                                   |
| curvature         | Curvature parameter used by elliptic and hyperbolic trends           |
| migrationAngle    | Migration angle used by Hyperbolic3D                                 |
| origin_x          | Trend origin X coordinate                                            |
| origin_y          | Trend origin Y coordinate                                            |
| origin_z_simbox   | Trend origin Z coordinate in simulation-box coordinates              |
| origintype        | Origin interpretation (Absolute coordinates or relative coordinates) |

Origin types:

```xml
<origintype>Relative</origintype>
```

and

```xml
<origintype>Absolute</origintype>
```

Coordinates are typically interpreted relative to simulation-box dimensions when Relative is used and relative to the global (UTM) coordinates when absolute is used.

# Linear3D

Creates a linear trend. Angles are in degrees.

```xml
<Trend>
  <Linear3D>
    <azimuth>45.0</azimuth>
    <directionStacking>1</directionStacking>
    <stackAngle>10.0</stackAngle>
  </Linear3D>
</Trend>
```

Typical parameters:

```xml
<azimuth>
<directionStacking>
<stackAngle>
```

# Elliptic3D

Creates an elliptical shaped trend in map view (x,y).

```xml
<Trend>
  <Elliptic3D>
    <azimuth>180.0</azimuth>
    <directionStacking>1</directionStacking>
    <stackAngle>15.0</stackAngle>
    <curvature>1.5</curvature>
    <origin_x>0.5</origin_x>
    <origin_y>0.5</origin_y>
    <origin_z_simbox>0.5</origin_z_simbox>
    <origintype>Relative</origintype>
  </Elliptic3D>
</Trend>
```

Typical parameters.

```xml
<azimuth>
<stackAngle>
<curvature>
<origin_x>
<origin_y>
<origin_z_simbox>
<origintype>
```

# Hyperbolic3D

Creates a channel like trend using a hyperbolic trend geometry.

```xml
<Trend>
  <Hyperbolic3D>
    <azimuth>315.0</azimuth>
    <directionStacking>1</directionStacking>
    <stackAngle>10.0</stackAngle>
    <curvature>1.25</curvature>
    <migrationAngle>45.0</migrationAngle>
    <origin_x>0.5</origin_x>
    <origin_y>0.5</origin_y>
    <origin_z_simbox>0.5</origin_z_simbox>
  </Hyperbolic3D>
</Trend>
```

Additional keyword:

```xml
<migrationAngle>
```

# EllipticCone3D

Elliptic cone trend model.

```xml
<Trend>
  <EllipticCone3D>
    <azimuth>315.0</azimuth>
    <directionStacking>1</directionStacking>
    <stackAngle>10.0</stackAngle>
    <curvature>1.0</curvature>
    <origin_x>0.5</origin_x>
    <origin_y>0.5</origin_y>
    <origin_z_simbox>0.5</origin_z_simbox>
    <relativeSize>0.5</relativeSize>
  </EllipticCone3D>
</Trend>
```

Unique keyword:

```xml
<relativeSize>
```

| Parameter    | Description                  |
| ------------ | ---------------------------- |
| relativeSize | Relative cone size parameter |

# RMSTrendMap

Uses an RMS trend map (2D) defined by the user.

```xml
<Trend>
  <RMSTrendMap>
    <TrendMapName>APS_trend_map</TrendMapName>
    <TrendMapZone>A</TrendMapZone>
  </RMSTrendMap>
</Trend>
```

## Keywords

```xml
<TrendMapName>
<TrendMapZone>
```

| Parameter    | Description                   |
| ------------ | ----------------------------- |
| TrendMapName | RMS trend map name            |
| TrendMapZone | RMS trend map zone identifier |

`TrendMapZone` must name an existing zone in the RMS project's Zones container. `TrendMapName` must name a non-empty surface representation belonging to that zone.

# RMSParameter

Uses an RMS 3D parameter directly as a trend field.

```xml
<Trend>
  <RMSParameter>
    <TrendParamName>CustomTrendForGRF</TrendParamName>
  </RMSParameter>
</Trend>
```

## Keywords

```xml
<TrendParamName>
```

| Parameter      | Description                                |
| -------------- | ------------------------------------------ |
| TrendParamName | RMS parameter used directly as trend field |

# Relative Standard Deviation

Relative standard deviation of the residual GRF relative to the trend.
The smaller the more dominant is the trend, the larger the more dominates the simulated GRF for the residual field.

```xml
<RelStdDev>0.05</RelStdDev>
```

Allowed values are non-negative values, typically from 0 to 0.5

# FMU Support

Trend parameters may be marked as updatable by FMU.
The kw value follows a predefined standard for the naming of APS model parameters.

Examples:

```xml
<azimuth kw="APS_...">
<stackAngle kw="APS_...">
<curvature kw="APS_...">
<migrationAngle kw="APS_...">
<origin_x kw="APS_...">
<origin_y kw="APS_...">
<origin_z_simbox kw="APS_...">
<RelStdDev kw="APS_...">
```

Example:

```xml
<migrationAngle kw="APS_3_0_GF_GF1_TREND_MIGRATIONANGLE">
    9.28
</migrationAngle>
```
