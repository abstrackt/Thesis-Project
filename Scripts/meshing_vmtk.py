import SimpleITK as sitk
import os
from optparse import OptionParser
from vmtk import pypes
from vmtk import vmtkscripts
import numpy as np
from stl import mesh as stmesh
 
def preprocess(folder_name):
    
    if not os.path.exists(folder_name) :
        os.makedirs(folder_name)
 
    indir = folder_name;
    outdir = folder_name + "/mhd/";
 
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
            
def export_mesh(in_path, out_path, files):
    verts = []
    faces = []
 
    offset = 0
 
    for file in files:
        
        if not os.path.exists(in_path + "/mhd/" + file + ".mhd"):
            continue
            
        if not os.path.exists(out_path):
            os.makedirs(out_path)
        
        args = "vmtkimagereader -ifile " + in_path + "/mhd/" + file + ".mhd" + " " +\
               "--pipe vmtklevelsetsegmentation " +\
               "--pipe vmtkmarchingcubes -i @.o " +\
               "--pipe vmtksurfaceclipper -i @.o " +\
               "--pipe vmtksurfacesmoothing -i @.o -passband 0.1 -iterations 30 " +\
               "--pipe vmtksurfacesubdivision -i @.o -method butterfly " +\
               "--pipe vmtksurfacewriter -i @.o -ofile " + out_path + file + ".stl"
               
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
    
    #preprocess(options.input) 
    
    print("Preprocessing finished, now exporting mesh");
    
    export_mesh(options.input, options.output, options.seg_class)
              
if __name__ == "__main__":
    main()