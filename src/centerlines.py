import os
from vmtk import pypes


def centerline(in_path, out_path):
    args = (f"vmtksurfacereader -ifile {in_path} "
            f"--pipe vmtkcenterlines "
            f"--pipe vmtkcenterlineattributes "
            f"--pipe vmtkbranchextractor -ofile {out_path}")

    res = pypes.PypeRun(args)


def centerdist(in_path, out_path):
    args = (f"vmtksurfacereader -ifile {in_path} "
            "--pipe vmtkcenterlines -endpoints 1 "
            "--pipe vmtkdistancetocenterlines -useradius 1 "
            f"--pipe vmtksurfacenormals -ofile {out_path}")

    res = pypes.PypeRun(args)


def branched(in_path, cl_path, out_path):
    args = (f"vmtkbranchclipper -ifile {in_path} -centerlinesfile {cl_path} "
            f"-groupidsarray GroupIds "
            f"-radiusarray MaximumInscribedSphereRadius "
            f"-blankingarray Blanking "
            f"--pipe vmtkdistancetocenterlines -useradius 1 "
            f"--pipe vmtksurfacenormals -ofile {out_path}")

    res = pypes.PypeRun(args)


def metrics(in_path, cl_path, out_path):
    args = (f"vmtkbranchmetrics -ifile {in_path} -centerlinesfile {cl_path} "
            f"-abscissasarray Abscissas "
            f"-normalsarray ParallelTransportNormals "
            f"-groupidsarray GroupIds "
            f"-centerlineidsarray CenterlineIds "
            f"-tractidsarray TractIds "
            f"-blankingarray Blanking "
            f"-radiusarray MaximumInscribedSphereRadius "
            f"-ofile {out_path}")

    res = pypes.PypeRun(args)
