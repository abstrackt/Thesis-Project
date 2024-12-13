from vmtk import pypes


def view_surface(in_path):
    args = "vmtksurfacereader -ifile " + in_path + " --pipe vmtkrenderer --pipe vmtksurfaceviewer -opacity 0.25"

    res = pypes.PypeRun(args)