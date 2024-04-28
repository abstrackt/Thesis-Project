import os
import SimpleITK as sitk
from totalsegmentator.python_api import totalsegmentator as ts


def segment_masks(in_path, out_dir=None):
    if out_dir is not None:
        out_dir = os.path.join(in_path, "mhd")

    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    for file in os.listdir(in_path):
        if not (os.path.exists(os.path.join(out_dir, file.replace(".nii.gz", ".mhd")))):
            if os.path.isfile(os.path.join(in_path, file)) and ".nii.gz" in file:
                img = sitk.ReadImage(os.path.join(in_path, file))

                path = os.path.join(out_dir, file.replace(".nii.gz", ".mhd"))
                scale_filter = sitk.ShiftScaleImageFilter()
                scale_filter.SetScale(100)
                res = scale_filter.Execute(img)

                minmax_filter = sitk.MinimumMaximumImageFilter()
                minmax_filter.Execute(img)

                if minmax_filter.GetMaximum() != 0:
                    sitk.WriteImage(res, path)


def segment_refine(folder_name, classes, fx, fy, fz):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    in_path = folder_name

    img = None

    for item in classes:
        if os.path.exists(os.path.join(in_path, item + ".nii.gz")):
            if img is None:
                img = sitk.ReadImage(os.path.join(in_path, item + ".nii.gz"))
            else:
                tmp = sitk.ReadImage(os.path.join(in_path, item + ".nii.gz"))
                lor = sitk.OrImageFilter()
                img = lor.Execute(tmp, img)

    if img is not None:
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

        img = sitk.Flip(img, [fx, fy, fz])

        directory = os.path.join(in_path, "mhd")
        path = os.path.join(directory, "image.mhd")

        if minmax_filter.GetMaximum() != 0:
            if not os.path.exists(directory):
                os.makedirs(directory)

            sitk.WriteImage(img, path)


def segment(in_path, out_path):
    if not os.path.exists(out_path):
        os.makedirs(out_path)

    ts(in_path, out_path)
    
