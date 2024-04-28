import os
from vmtk import pypes


def centerline(in_path, out_path):
    verts = []
    faces = []

    args = "vmtksurfacereader -ifile " + in_path + " --pipe vmtkcenterlines -ofile " + out_path + " --pipe vmtkrenderer --pipe vmtksurfaceviewer -opacity 0.25 --pipe vmtksurfaceviewer -i @vmtkcenterlines.voronoidiagram -array MaximumInscribedSphereRadius --pipe vmtksurfaceviewer -i @vmtkcenterlines.o"

    res = pypes.PypeRun(args)


def centerdist(in_path, out_path):
    args = "vmtksurfacereader -ifile " + in_path + " --pipe vmtkcenterlines -endpoints 1 --pipe vmtkdistancetocenterlines -useradius 1 --pipe vmtksurfacenormals -ofile " + out_path

    res = pypes.PypeRun(args)
