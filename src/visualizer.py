# Create visualizer

import platform
import tempfile
from typing import Optional

if platform.system() != 'Windows':
    import PySide2.QtSvg # Must import this before fast due to conflicting symbols
import fast # Must import FAST before rest of pyside2
from PySide2.QtWidgets import *
from PySide2.QtCore import Qt
from shiboken2 import wrapInstance
import random as rd
import keyboard
import os
import SimpleITK as sitk


class SegmentationVisualizer:
    def _import_segment(self, mask_dir, segment):
        print(segment)

        importer = fast.ImageFileImporter.create(os.path.join(mask_dir, segment))

        extraction = fast.SurfaceExtraction \
            .create(threshold=50) \
            .connect(importer)

        r = rd.uniform(0.5, 1);
        g = rd.uniform(0.5, 1);
        b = rd.uniform(0.5, 1);

        mesh = extraction.runAndGetOutputData()

        renderer = fast.TriangleRenderer \
            .create(color=fast.Color(r, g, b)) \
            .connect(mesh)

        self._renderers.append(renderer)
        self._active.append(True)

        self._window.connect(renderer)

    def _reset_segment_alpha(self):
        for j in range(0, len(self._renderers)):
            self._renderers[j].setOpacity(0, 1)
            self._active[j] = True

    def _toggle_segment_alpha(self, i):
        self._window.removeAllRenderers()
        self._window.connect(self._renderers[i])
        self._active[i] = True
        self._renderers[i].setOpacity(0, 1)

        changed = []

        for j in range(0, len(self._renderers)):
            if i != j and self._active[j]:
                self._window.connect(self._renderers[j])
                if not keyboard.is_pressed('q'):
                    self._active[j] = False
                    self._renderers[j].setOpacity(0, 0.05)
                    changed.append(j)

        for j in range(0, len(self._renderers)):
            if i != j and not self._active[j] and j not in changed:
                self._window.connect(self._renderers[j])
                self._renderers[j].setOpacity(0, 0.05)

    def _toggle_segment(self, i):
        return lambda: self._toggle_segment_alpha(i)

    def _generate_masks(self, in_path: str, out_dir: str):
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

    def _show(self):
        self._generate_masks(self.in_path, self.out_path)

        # Create FAST Pipeline and window
        self._window = fast.SimpleWindow3D.create(width=1024, height=512)

        # Get the underlying QtWidget of the FAST window and convert it to pyside2
        main_widget = wrapInstance(int(self._window .getWidget()), QWidget)

        # Create GUI in Qt
        layout = main_widget.layout()
        menu_widget = QWidget(None)
        layout.addWidget(menu_widget)
        menu_layout = QVBoxLayout()
        menu_widget.setLayout(menu_layout)
        menu_layout.setAlignment(Qt.AlignTop)
        menu_widget.setFixedWidth(400)

        # Create segment list
        widget = QWidget()

        seg_list = QVBoxLayout()
        seg_list.setAlignment(Qt.AlignTop)

        scroll = QScrollArea()
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setWidgetResizable(True)

        files = os.listdir(self.out_path)

        idx = 0

        for i in range(0, len(files)):
            if os.path.isfile(os.path.join(self.out_path, files[i])) and ".mhd" in files[i]:
                elem_button = QPushButton(files[i][:-4])
                elem_button.clicked.connect(self._toggle_segment(idx))
                self._import_segment(self.out_path, files[i])
                seg_list.addWidget(elem_button)
                idx += 1

        widget.setLayout(seg_list)
        scroll.setWidget(widget)

        reset = QPushButton("Reset view")
        reset.clicked.connect(lambda: self._reset_segment_alpha())

        menu_layout.addWidget(reset)
        menu_layout.addWidget(scroll)

        self._window .run()

    def show(self):
        if self.out_path is None:
            with tempfile.TemporaryDirectory() as temp_dir:
                self.out_path = temp_dir
                self._show()
            self.out_path = None
        else:
            self._show()

    def __init__(self, in_path: str, out_path: Optional[str] = None):

        self._renderers = []
        self._active = []
        self._window = None
        self.in_path = in_path
        self.out_path = out_path
