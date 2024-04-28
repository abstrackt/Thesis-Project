import os
from random import random

import gmsh
import sys
import math

import numpy as np
from vmtk import pypes
from vmtk import vmtkscripts

def export_stl(in_path, out_path):
    verts = []
    faces = []
 
    offset = 0

    args = "vmtkimagereader -ifile " + in_path + " " +\
           "--pipe vmtklevelsetsegmentation " +\
           "--pipe vmtkmarchingcubes -i @.o " +\
           "--pipe vmtksurfaceclipper -i @.o " +\
           "--pipe vmtksurfacesmoothing -i @.o -passband 0.05 -iterations 30 " +\
           "--pipe vmtksurfacesubdivision -i @.o -method butterfly " +\
           "--pipe vmtksurfacewriter -i @.o -ofile " + out_path

    res = pypes.PypeRun(args)


def export_3d(in_path):
    gmsh.initialize(sys.argv)

    gmsh.merge(in_path)
    gmsh.model.mesh.classifySurfaces(math.pi, True, True)
    gmsh.model.mesh.createGeometry()

    gmsh.option.setNumber('Geometry.ExtrudeReturnLateralEntities', 0)

    gmsh.model.geo.extrudeBoundaryLayer(gmsh.model.getEntities(2), [4], [1.0], True)

    e = gmsh.model.geo.extrudeBoundaryLayer(gmsh.model.getEntities(2), [4], [-1.0], True, True)

    top_ent = [s for s in e if s[0] == 2]
    top_surf = [s[1] for s in top_ent]

    gmsh.model.geo.synchronize()
    bnd_ent = gmsh.model.getBoundary(top_ent)
    bnd_curv = [c[1] for c in bnd_ent]

    loops = gmsh.model.geo.addCurveLoops(bnd_curv)
    for l in loops:
        top_surf.append(gmsh.model.geo.addPlaneSurface([l]))

    gmsh.model.geo.addVolume([gmsh.model.geo.addSurfaceLoop(top_surf)])
    gmsh.model.geo.synchronize()

    gmsh.option.setNumber('Mesh.Algorithm', 1)
    gmsh.option.setNumber('Mesh.MeshSizeFactor', 0.1)

    if '-nopopup' not in sys.argv:
        gmsh.fltk.run()

    gmsh.finalize()


def surface_to_numpy(in_file):
    reader = vmtkscripts.vmtkSurfaceReader()
    np_adpt = vmtkscripts.vmtkSurfaceToNumpy()

    reader.InputFileName = in_file
    reader.Execute()
    np_adpt.Surface = reader.Surface
    np_adpt.Execute()

    mesh_dict = np_adpt.ArrayDict

    return mesh_dict


def numpy_to_surface(mesh_dict, out_file):
    surf_adpt = vmtkscripts.vmtkNumpyToSurface()
    surf_adpt.ArrayDict = mesh_dict
    surf_adpt.Execute()

    writer = vmtkscripts.vmtkSurfaceWriter()
    writer.Surface = surf_adpt.Surface
    writer.OutputFileName = out_file
    writer.Execute()


def _smooth_array(array, neighbors):
    new_array = np.empty(array.shape)
    print(neighbors[0:10])
    for i in range(0, len(neighbors)):
        total = 0
        for index in neighbors[i]:
            total += array[index]
        if len(neighbors[i]) > 0:
            total /= len(neighbors[i])
        else:
            total = array[i]
        new_array[i] = total
    print(array[0:10])
    print(new_array[0:10])
    return new_array


def _random_three_vector():
    phi = random() * np.pi*2
    costheta = np.random.uniform(-1, 1)

    theta = np.arccos(costheta)
    x = np.sin(theta) * np.cos(phi)
    y = np.sin(theta) * np.sin(phi)
    z = np.cos(theta)
    return np.array([x, y, z])


def _perpendicular_vector(v):
    if v[1] == 0 and v[2] == 0:
        if v[0] == 0:
            raise ValueError('zero vector')
        else:
            return np.cross(v, [0, 1, 0])
    return np.cross(v, [1, 0, 0])


def _rotation_matrix(axis, theta):
    axis = np.asarray(axis)
    axis = axis / math.sqrt(np.dot(axis, axis))
    a = math.cos(theta / 2.0)
    b, c, d = -axis * math.sin(theta / 2.0)
    aa, bb, cc, dd = a * a, b * b, c * c, d * d
    bc, ad, ac, ab, bd, cd = b * c, a * d, a * c, a * b, b * d, c * d
    return np.array([[aa + bb - cc - dd, 2 * (bc + ad), 2 * (bd - ac)],
                     [2 * (bc - ad), aa + cc - bb - dd, 2 * (cd + ab)],
                     [2 * (bd + ac), 2 * (cd - ab), aa + dd - bb - cc]])


def boundary_layer(in_file, out_file):
    mesh_dict = surface_to_numpy(in_file)

    pts = mesh_dict['Points']
    dist = mesh_dict['PointData']['DistanceToCenterlines']
    norm = mesh_dict['PointData']['Normals']
    scal = mesh_dict['PointData']['Scalars_']
    tris = mesh_dict['CellData']['CellPointIds']

    point_count = pts.shape[0]
    new_pts = np.empty(pts.shape)

    print(pts.shape)

    # Iterate over all points in the mesh and extrude them along normals while scaling extrustion
    for i in range(0, point_count):
        vert = pts[i]
        new_vert = vert - norm[i] * dist[i] * 0.2
        new_pts[i] = new_vert

    mesh_dict['Points'] = np.append(pts, new_pts, axis=0)

    print(mesh_dict['Points'].shape)

    face_count = tris.shape[0]
    new_faces = np.empty(tris.shape)

    print(tris.shape)

    # Iterate over all faces of the mesh and connect them
    for i in range(0, face_count):
        face = tris[i]
        new_face = np.empty(face.shape)
        new_face[0] = face[0] + point_count
        new_face[1] = face[1] + point_count
        new_face[2] = face[2] + point_count
        new_faces[i] = new_face

    mesh_dict['CellData']['CellPointIds'] = np.append(tris, new_faces, axis=0)

    print(mesh_dict['CellData']['CellPointIds'].shape)

    mesh_dict['PointData']['DistanceToCenterlines'] = np.append(dist, dist, axis=0)
    mesh_dict['PointData']['Normals'] = np.append(norm, norm, axis=0)
    mesh_dict['PointData']['Scalars_'] = np.append(scal, scal, axis=0)

    numpy_to_surface(mesh_dict, out_file)


def boundary_layer_vmr(in_file, out_file):
    mesh_dict = surface_to_numpy(in_file)

    pts = mesh_dict['Points']
    dist = mesh_dict['PointData']['DistanceToCenterlines']
    tris = mesh_dict['CellData']['CellPointIds']
    norm = mesh_dict['PointData']['Normals']

    point_count = pts.shape[0]
    face_count = tris.shape[0]

    neighbors = [set() for i in range(0, point_count)]

    for i in range(0, face_count):
        for a in range(0, 3):
            for b in range(0, 3):
                neighbors[tris[i][a]].add(tris[i][b])

    point_count = pts.shape[0]
    new_pts = np.empty(pts.shape, dtype=np.float32)

    # Distance field smoothing
    for i in range(0, 15):
        dist = _smooth_array(dist, neighbors)

    # Iterate over all points in the mesh and extrude them along normals while scaling extrustion
    for i in range(0, point_count):
        vert = pts[i]
        new_vert = vert - norm[i] * math.pow(dist[i], 2) * 0.02
        new_pts[i] = new_vert

    face_count = tris.shape[0]
    new_faces = np.empty(tris.shape, dtype=np.int64)

    print(tris.shape)

    # Iterate over all faces of the mesh and connect them
    for i in range(0, face_count):
        face = tris[i]
        new_face = [0, 0, 0]
        new_face[0] = int(face[0] + point_count)
        new_face[1] = int(face[1] + point_count)
        new_face[2] = int(face[2] + point_count)
        new_faces[i] = new_face

    new_dict = {}

    new_dict['Points'] = np.append(pts, new_pts, axis=0)
    new_dict['PointData'] = {}
    new_dict['PointData']['Normals'] = np.append(norm, norm, axis=0)
    new_dict['CellData'] = {}

    new_dict['CellData']['CellPointIds'] = np.append(tris, new_faces, axis=0)

    numpy_to_surface(new_dict, out_file)


def sample_voronoi_points(centerline_file, n_per_point, flat=False, adaptive=False, sample_scaling=0.05):
    mesh_dict = surface_to_numpy(centerline_file)

    voronoi_points = []

    pts = mesh_dict['Points']
    rad = mesh_dict['PointData']['MaximumInscribedSphereRadius']
    edges = mesh_dict['CellData']['CellPointIds']

    for i in range(0, len(edges)):
        branch = edges[i]
        for j in range(1, len(branch)):
            axis = pts[branch[j]] - pts[branch[j - 1]]
            norm = np.linalg.norm(axis)
            if not math.isnan(norm) and not math.isinf(norm):
                axis /= norm
                vec = _perpendicular_vector(axis)
                R = rad[branch[j]]
                samples = n_per_point
                if adaptive:
                    samples /= R * sample_scaling
                    samples = math.ceil(samples)
                for k in range(0, samples):
                    r = R * math.sqrt(random())
                    if flat:
                        theta = random() * 2 * math.pi
                        pt = np.dot(_rotation_matrix(axis, theta), r*vec)
                        pt += pts[branch[j]]
                        voronoi_points.append(pt)
                    else:
                        pt = pts[branch[j]] + r * _random_three_vector()
                        voronoi_points.append(pt)

    return voronoi_points
