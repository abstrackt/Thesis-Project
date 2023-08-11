# Create visualizer

import platform
if platform.system() != 'Windows':
    import PySide2.QtSvg # Must import this before fast due to conflicting symbols
import fast # Must import FAST before rest of pyside2
from PySide2.QtWidgets import *
from PySide2.QtCore import Qt
from shiboken2 import wrapInstance
from optparse import OptionParser
import random as rd
import functools
import keyboard
import os
import SimpleITK as sitk

renderers = []
active = []

def generate_masks(in_path) :
    
    out_path = os.path.join(in_path, "mhd")
    
    if not os.path.exists(out_path) :
        os.makedirs(out_path)
    
    for file in os.listdir(in_path):
        if not (os.path.exists(os.path.join(out_path, file.replace(".nii.gz", ".mhd")))):
            if os.path.isfile(os.path.join(in_path, file)) and ".nii.gz" in file :
                img = sitk.ReadImage(os.path.join(in_path, file))

                path = os.path.join(out_path, file.replace(".nii.gz", ".mhd"))
                scale_filter = sitk.ShiftScaleImageFilter()
                scale_filter.SetScale(100)
                res = scale_filter.Execute(img)

                minmax_filter = sitk.MinimumMaximumImageFilter()
                minmax_filter.Execute(img)

                if minmax_filter.GetMaximum() != 0 :
                    sitk.WriteImage(res, path)

def import_segment(x, segdir, window) :
    print(x)
    
    importer = fast.ImageFileImporter.create(os.path.join(segdir, x))

    extraction = fast.SurfaceExtraction\
            .create(threshold=50)\
            .connect(importer)

    r = rd.uniform(0.5, 1);
    g = rd.uniform(0.5, 1);
    b = rd.uniform(0.5, 1);

    mesh = extraction.runAndGetOutputData()

    renderer = fast.TriangleRenderer\
            .create(color=fast.Color(r, g, b))\
            .connect(mesh)
    
    renderers.append(renderer)
    active.append(True)

    window.connect(renderer)
    
def toggle_segment_alpha(i, window):
    print(i)
    window.removeAllRenderers()
    window.connect(renderers[i])
    active[i] = True
    renderers[i].setOpacity(0, 1)
    
    changed = []
    
    for j in range(0, len(renderers)):
        if i != j and active[j]:
            window.connect(renderers[j])
            if not keyboard.is_pressed('q'):
                active[j] = False
                renderers[j].setOpacity(0, 0.05) 
                changed.append(j)
    
    for j in range(0, len(renderers)):
        if i != j and not active[j] and j not in changed:
            window.connect(renderers[j])
            renderers[j].setOpacity(0, 0.05)    
            
def reset_segment_alpha():
    for j in range(0, len(renderers)):
        renderers[j].setOpacity(0, 1)
        active[j] = True
            
    
def toggle_segment(i, window):
    return lambda: toggle_segment_alpha(i, window)

def main():
    parser = OptionParser()
    parser.add_option('-i', '--input', action='store', dest='input')
    (options, args) = parser.parse_args()
    
    if (len(args) != 0 or options.input == ''):
        print("Usage: python meshing.py -i <input_path>")
        return
    
    generate_masks(options.input)
    
    # Create FAST Pipeline and window
    window = fast.SimpleWindow3D.create(width=1024, height=512)\

    # Get the underlying QtWidget of the FAST window and convert it to pyside2
    mainWidget = wrapInstance(int(window.getWidget()), QWidget)

    # Create GUI in Qt
    layout = mainWidget.layout()
    menuWidget = QWidget()
    layout.addWidget(menuWidget)
    menuLayout = QVBoxLayout()
    menuWidget.setLayout(menuLayout)
    menuLayout.setAlignment(Qt.AlignTop)
    menuWidget.setFixedWidth(400)

    # Create segment list
    widget = QWidget()   

    seglist = QVBoxLayout()
    seglist.setAlignment(Qt.AlignTop)

    scroll = QScrollArea()
    scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
    scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    scroll.setWidgetResizable(True)

    segdir = os.path.join(options.input, "mhd");
    
    files = os.listdir(segdir)

    idx = 0

    for i in range(0, len(files)) :
        if os.path.isfile(os.path.join(segdir, files[i])) and ".mhd" in files[i] :
            elem_button = QPushButton(files[i][:-4])
            elem_button.clicked.connect(toggle_segment(idx, window))
            import_segment(files[i], segdir, window)
            seglist.addWidget(elem_button)
            idx += 1

    widget.setLayout(seglist)
    scroll.setWidget(widget)

    reset = QPushButton("Reset view")
    reset.clicked.connect(lambda: reset_segment_alpha())

    menuLayout.addWidget(reset)
    menuLayout.addWidget(scroll)

    reset = QPushButton(files[i][:-4])

    # Run everything!
    window.run()

if __name__ == "__main__":
    main()