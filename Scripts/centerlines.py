import SimpleITK as sitk
import os
from optparse import OptionParser
from vmtk import pypes
from vmtk import vmtkscripts
import numpy as np
from stl import mesh as stmesh

def generate_centerline(in_path, out_path):
    verts = []
    faces = []

    args = "vmtksurfacereader -ifile " + in_path + " --pipe vmtkcenterlines --pipe vmtkrenderer --pipe vmtksurfaceviewer -opacity 0.25 --pipe vmtksurfaceviewer -i @vmtkcenterlines.voronoidiagram -array MaximumInscribedSphereRadius --pipe vmtksurfaceviewer -i @vmtkcenterlines.o"

    res = pypes.PypeRun(args)
        
    
def main():
    parser = OptionParser()
    parser.add_option('-i', '--input', action='store', dest='input')
    parser.add_option('-o', '--output', action='store', dest='output', default='./')
    (options, args) = parser.parse_args()
    
    if (len(args) != 0 or options.input == ''):
        print("Usage: python centerlines.py -i <input_path> -o <output_path> (default ./)")
        return
    
    generate_centerline(options.input, options.output) 
              
if __name__ == "__main__":
    main()