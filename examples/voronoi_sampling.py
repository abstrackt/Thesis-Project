from src.meshing import sample_voronoi_points, SamplingType
from scipy.spatial import Delaunay
from stl import mesh
import numpy

from src.utils import volume, distance

points = sample_voronoi_points("output/healthy_centerline.vtp", 500, sampling=SamplingType.Cylinder, adaptive=True)

tri = Delaunay(points)

points = numpy.array(tri.points)

p = tri.points

tris = []

max_tet_volume = 1.0
max_tet_edge_length = 5.0

for s in tri.simplices:
    tet = [p[i] for i in s]
    edge_lengths = [
        distance(tet[0], tet[1]),
        distance(tet[0], tet[2]),
        distance(tet[0], tet[3]),
        distance(tet[1], tet[3]),
        distance(tet[1], tet[2]),
        distance(tet[2], tet[3])
    ]
    if volume(tet[0], tet[1], tet[2], tet[3]) > max_tet_volume or any(t > max_tet_edge_length for t in edge_lengths):
        continue
    tris += [
        [s[0], s[1], s[2]],
        [s[3], s[1], s[2]],
        [s[0], s[3], s[2]],
        [s[0], s[1], s[3]],
    ]

faces = numpy.array(tris)

meshed_stl = mesh.Mesh(numpy.zeros(faces.shape[0], dtype=mesh.Mesh.dtype))
for i, f in enumerate(faces):
    for j in range(3):
        meshed_stl.vectors[i][j] = points[f[j], :]

meshed_stl.save("output/volume_mesh.stl")


