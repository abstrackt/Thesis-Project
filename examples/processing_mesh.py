from CTMesh.meshing import export_stl, boundary_layer_vmr, sample_voronoi_points, surface_to_numpy
from CTMesh.centerlines import centerline
import matplotlib.pyplot as plt
import math
import numpy as np
from scipy.stats import gaussian_kde

mesh_dict = surface_to_numpy("./centerline.vtp")

pts = mesh_dict['Points']
tris = mesh_dict['CellData']['CellPointIds']

# Create a new figure and set up a 3D axis
fig = plt.figure()
ax = plt.axes(computed_zorder=False, projection='3d')
ax.set_aspect('equal', adjustable='box')

# Extract the x, y, and z coordinates from the vertices
xdata = [p[0] for p in pts]
ydata = [p[1] for p in pts]
zdata = [p[2] for p in pts]

# Plot the mesh surface
ax.plot_trisurf(xdata, ydata, zdata, triangles=tris, alpha=0.2)

centerline_dict = surface_to_numpy("./centerline.vtk")

centerline = centerline_dict['Points']

xdata = [p[0] for p in centerline if not math.isnan(p[0])]
ydata = [p[1] for p in centerline if not math.isnan(p[1])]
zdata = [p[2] for p in centerline if not math.isnan(p[2])]

ax.plot(xdata, ydata, zdata)

# Get Voronoi samples along the centerline
voronoi_points = sample_voronoi_points("./centerline.vtk", 1, flat=True, adaptive=True, sample_scaling=0.05)

xdata = [p[0] for p in voronoi_points if not math.isnan(p[0])]
ydata = [p[1] for p in voronoi_points if not math.isnan(p[1])]
zdata = [p[2] for p in voronoi_points if not math.isnan(p[2])]

arr = np.vstack([xdata, ydata, zdata])
k = gaussian_kde(arr)(arr)

ax.scatter3D(xdata, ydata, zdata, c=k, alpha=0.4)

plt.show()