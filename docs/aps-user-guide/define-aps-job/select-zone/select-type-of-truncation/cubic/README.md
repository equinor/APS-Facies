---
title: Cubic
---
If "Cubic" truncation rule is selected, a dropdown list of templates is available.
The icons show the layout of the polygons in the truncation map.
Depending on the number of facies, there will be more or less available templates.
Remember that the horizontal axis of the truncation map corresponds to $\alpha_{1}$
(transformed gaussian field) and vertical axis of $\alpha_{2}$.
Which GRF that corresponds to $\alpha_{1}$ and $\alpha_{2}$ can be selected, but as default $\alpha_{1}$ is transformed GRF<sub>1</sub> and $\alpha_{2}$ is transformed GRF<sub>2</sub>.

The name "Cubic" truncation rule is related to the polygons the truncation map is split into.
In this case the polygons have rectangular shape (two-dimensional when two Alpha's (GRF's) are used)
and rectangular boxes in 3 or more dimensions if overlay facies is used.

## Select template

![](assets/images/25ec5cedc2918e0de4ce8ec42a51046019dd7399da9b945524459784b5e7c61a.png)

## Edit selected template

Editing of selected template for "cubic" truncation rule is possible.

It is possible to:

- split a polygon horizontally or vertically

- join two polygons

- create more polygons than number of facies and associate a facies to multiple polygons

The sequence of figures below show this for one example:

### Example starting with 4 horizontal rectangles
![](assets/images/9454b148375a1adc335eb68337f43c330772226be382c22b01d51b9bbd350c28.png)

### Split the uppermost rectangle. The split is vertical
![](assets/images/ef02a8b405efcbcf06b138e9b1206cf498d277564dda72e19fe95123ae6c30f6.png)

### The right upper rectangle is split again vertically into two
![](assets/images/6646c1cd432166868e74cfbda1735d4ec5b38342e8223b445d938350d34499d8.png)

### Facies is selected for each polygon
Max number of levels of polygons is 3, but there are no limit in number of polygons.
When number of polygons are larger than number of facies such that multiple polygons are associated with the same facies,
the user must specify how the facies probabilities are shared between the polygons associated to the same facies.
Per default the facies probability is shared equally on the polygons

![](assets/images/d8aa03de0bce236e49a3bc81b527e5c14968dc109164225d40e27c413eac18b8.png)

### How the truncation map may look like
![](assets/images/2d1e61f7933f5df93b5592f8bc2643197e53e6dad8a9aaac2dd12cf7ae806630.png)
