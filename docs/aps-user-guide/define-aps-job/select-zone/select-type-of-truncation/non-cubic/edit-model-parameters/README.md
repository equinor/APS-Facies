---
title: Edit model parameters
---
For non-cubic truncation rules, the polygons are in general not rectangular.
The lines that define the boundaries between each polygon is defined by an angle and the sequence they are specified define how the polygons are defined.

The selected template can be edited.
Each line in the table shown below corresponds to a polygon in the truncation map.
Angles for normal vectors normal to the boundary lines between the polygons are specified.
 The example below shows a case with 5 facies and 6 polygons.
When a facies is associated with multiple polygons,
a probability fraction
(how much of the probability associated with a facies is to be assigned to each polygon that belongs to the facies)
is specified.

![](assets/images/b1fe5ebb39c6f416ce4d4e4647f5434f4648892e2c4e6921fcd39dde7a6de8b3.png)


![](assets/images/23f9c6cbea99d53e2d22f6837d5add3a8a69cc12b125d4b6d82a610555bcabb8.png)

The user specify an _angle between the normal vector to the boundary line and the horizontal line_, see figure below.
The algorithm to define the polygons are as follows:

1. The specified polygons are defined in the sequence specified.

2. The boundary line is moved in the normal vector direction until the area fraction (e.g. the green polygon area below) match the probability for the facies associated with the polygon. Then the second boundary line is moved in the normal vector direction until the area of the second polygon match the area fraction for the facies associated with this polygon (e.g. the grey polygon below).

3. The procedure above is repeated for all polygons except the last one. The direction of the normal vectors indicated the direction the boundary line is moved.

4. The last polygon (the blue one in the example below) will fill the remaining area of the unit square.

In the example below the sequence of the boundary lines are:

1. Boundary line number 1 defines green polygon

2. Boundary line number 2 defines grey polygon

3. Boundary line number 3 defines purple polygon

4. Boundary line number 4 defines yellow polygon

5. The remaining area is the blue polygon.

It is clear from this algorithm that the sequence of the specified boundary lines define the geometry of the polygons.

![](assets/images/24bf38c3fcecbfb0446b03e1fa5e25c1e0a87309cf4e9d47b29c564dd30d6f40.png)

The effect of having a slope with angle different from 0 or 90 degrees is to mix the effect of both the GRF corresponding to alpha1 and the GRF corresponding to alpha2.
This can be shown in the figures below where the angle is changed gradually.
Here GRF1 has a linear trend and corresponds to alpha1 (horizontal axis of truncation map) and GRF2 to alpha2.
![](assets/images/b6e673f5d4f5d15a518bf79ec34aeffadaf55d1d32cf57aaa1d4220dbe8ddbf4.png)
