# 3d_neighbor_removal

# Remove_extra_plants_from_pointcloud

Some pointclouds include parts of multiple plants in them. This code removes
parts of extra plants by performing a DBSCAN on the pointcloud and, if there
are 2 or more large pieces, converting these into polygons and calculating the
area of overlap. If this area is greater than 50%, the pointclouds are
combined. At the end, all clusters aside from the largest are dropped,
returning a cropped pointcloud.
