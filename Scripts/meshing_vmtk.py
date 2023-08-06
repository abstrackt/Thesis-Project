import SimpleITK as sitk
import os
from optparse import OptionParser
from totalsegmentator.python_api import totalsegmentator
from vmtk import pypes
from vmtk import vmtkscripts
import numpy as np
from stl import mesh as stmesh
 
def segmentation(file_name):
    infile = file_name;
    outdir = "tmp/segmentations/";
 
    if not os.path.exists(outdir) :
        os.makedirs(outdir)
 
    totalsegmentator(infile, outdir)
 
    indir = "tmp/segmentations/";
    outdir = "tmp/segmentations/mhd/";
 
    if not os.path.exists(outdir) :
        os.makedirs(outdir)
 
    for file in os.listdir(indir):
        if os.path.isfile(indir + file) and ".nii.gz" in file :
            img = sitk.ReadImage(indir + file)
 
            path = outdir + file.replace(".nii.gz", ".mhd")
            scale_filter = sitk.ShiftScaleImageFilter()
            scale_filter.SetScale(100)
            res = scale_filter.Execute(img)
 
            minmax_filter = sitk.MinimumMaximumImageFilter()
            minmax_filter.Execute(img)
 
            if minmax_filter.GetMaximum() != 0 :
                sitk.WriteImage(res, path)
            
def export_mesh(out_path, files):
    verts = []
    faces = []
 
    offset = 0
 
    for file in files:
        indir = "tmp/segmentations/mhd/"
        outdir = "tmp/meshes/"
        
        if not os.path.exists(indir + file + ".mhd"):
            continue
            
        if not os.path.exists(outdir):
            os.makedirs(outdir)
        
        args = "vmtkimagereader -ifile " + indir + file + ".mhd" + " " +\
               "--pipe vmtklevelsetsegmentation " +\
               "--pipe vmtkmarchingcubes -i @.o " +\
               "--pipe vmtksurfaceclipper -i @.o " +\
               "--pipe vmtksurfacesmoothing -i @.o -passband 0.1 -iterations 30 " +\
               "--pipe vmtksurfacesubdivision -i @.o -method butterfly " +\
               "--pipe vmtksurfacewriter -i @.o -ofile ./tmp/meshes/" + file + ".stl"
               
        res = pypes.PypeRun(args)
    
def main():
    parser = OptionParser()
    parser.add_option('-i', '--input', action='store', dest='input')
    parser.add_option('-o', '--output', action='store', dest='output', default='./')
    parser.add_option('-c', '--class', action='append', dest='seg_class')
    (options, args) = parser.parse_args()
    
    if (len(args) != 0 or options.input == '' or len(options.seg_class) == 0):
        print("Usage: python meshing.py -i <input_path> -o <output_path> (default ./) -c <class_1> -c <class_2>...")
        return
    
    #segmentation(options.input) 
    export_mesh(options.output, options.seg_class)
              
if __name__ == "__main__":
    main()