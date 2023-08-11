import SimpleITK as sitk
import os
from optparse import OptionParser
from vmtk import pypes
from vmtk import vmtkscripts
import numpy as np
from stl import mesh as stmesh
 
def preprocess(folder_name, classes):
    if not os.path.exists(folder_name) :
        os.makedirs(folder_name)
 
    in_path = folder_name;

    img = None
    tmp = None
    
    for item in classes:     
        if os.path.exists(os.path.join(in_path, item + ".nii.gz")) :
            if img == None:
                img = sitk.ReadImage(os.path.join(in_path, item + ".nii.gz"))
            else:
                tmp = sitk
                tmp = sitk.ReadImage(os.path.join(in_path, item + ".nii.gz"))
                lor = sitk.OrImageFilter()
                img = lor.Execute(tmp, img)
                
                
    if img != None:            
        old_spacing = img.GetSpacing()
        spacing = [1.5, 1.5, 1.5]
        size = img.GetSize()
        direction = img.GetDirection()
        origin = img.GetOrigin()

        ratio = [old_spacing[0] / spacing[0], old_spacing[1] / spacing[1], old_spacing[2] / spacing[2]]

        new_size = [int(size[0] * ratio[0]), int(size[1] * ratio[1]), int(size[2] * ratio[2])];

        resample = sitk.ResampleImageFilter()
        resample.SetOutputSpacing(spacing)
        resample.SetSize(new_size)
        resample.SetOutputDirection(direction)
        resample.SetOutputOrigin(origin)
        resample.SetTransform(sitk.Transform())
        resample.SetDefaultPixelValue(img.GetPixelIDValue())

        img = resample.Execute(img)

        scale_filter = sitk.ShiftScaleImageFilter()
        scale_filter.SetScale(100)
        img = scale_filter.Execute(img)

        minmax_filter = sitk.MinimumMaximumImageFilter()
        minmax_filter.Execute(img)

        directory = os.path.join(in_path, "mhd")
        path = os.path.join(directory, "image.mhd")
        
        if minmax_filter.GetMaximum() != 0 :
            if not os.path.exists(directory) :
                os.makedirs(directory)
            
            sitk.WriteImage(img, path)
            
def export_mesh(in_path, out_path):
    verts = []
    faces = []
 
    offset = 0
 
    if os.path.exists(os.path.join(in_path, "mhd", "image.mhd")):
        print ("The file does not exist")

        if not os.path.exists(out_path):
            os.makedirs(out_path)

        args = "vmtkimagereader -ifile " + os.path.join(in_path, "mhd", "image.mhd") + " " +\
               "--pipe vmtklevelsetsegmentation " +\
               "--pipe vmtkmarchingcubes -i @.o " +\
               "--pipe vmtksurfaceclipper -i @.o " +\
               "--pipe vmtksurfacesmoothing -i @.o -passband 0.05 -iterations 30 " +\
               "--pipe vmtksurfacesubdivision -i @.o -method butterfly " +\
               "--pipe vmtksurfacewriter -i @.o -ofile " + os.path.join(out_path, "model.stl")

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
    
    preprocess(options.input, options.seg_class) 
    
    print("Preprocessing finished, now exporting mesh");
    
    export_mesh(options.input, options.output)
              
if __name__ == "__main__":
    main()