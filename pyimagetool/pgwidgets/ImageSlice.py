from functools import partial

import numpy as np

import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtWidgets, QtCore

from PyQt5.QtWidgets import QMessageBox

from pyimagetool.DataMatrix import RegularDataArray
from pyimagetool.cmaps.CMap import CMap, default_cmap
from pyimagetool.pgwidgets import ImageBase
from pyimagetool.CMapEditor import CMapDialog
from pyimagetool.qtwidgets.RegionOfInterest import imgROI


class ImageSlice(ImageBase):

    def __init__(self, dat: RegularDataArray = None, **kwargs):
        """2D image view with extra features.

        :param lut: Name of colormap to initialize with
        :type lut: str
        """
        super().__init__(dat, **kwargs)

        # -------------
        # Colormap menu
        # -------------
        self.cmap_menu = QtWidgets.QMenu('Color Map')
        # Reset colormap
        self.cmap_reset_action = QtWidgets.QAction('Reset')
        self.cmap_reset_action.triggered.connect(self.cmap_reset)
        self.cmap_menu.addAction(self.cmap_reset_action)
        # Reverse Colormap
        self.cmap_reverse_action = QtWidgets.QAction('Reverse Colormap')
        self.cmap_reverse_action.triggered.connect(self.cmap_reverse)
        self.cmap_menu.addAction(self.cmap_reverse_action)


        # -------------
        # ROI menu
        # -------------
        self.imgROI = imgROI()
        self.roi_menu = QtWidgets.QMenu('ROI Map')

        self.roi_test_stat = QtWidgets.QAction('Stats')
        self.roi_test_stat.triggered.connect(self.showDialog_roi_stats)
        self.roi_menu.addAction(self.roi_test_stat)

        self.roi_export_action = QtWidgets.QAction('Export')
        self.roi_export_action.triggered.connect(self.roi_export_method)
        self.roi_menu.addAction(self.roi_export_action)

        self.menu.addMenu(self.roi_menu)

        # Scale to view
        self.cmap_to_view_action = QtWidgets.QAction('Scale to view')
        self.cmap_to_view_action.triggered.connect(self.cmap_to_range)
        self.cmap_menu.addAction(self.cmap_to_view_action)
        
        # Change colormap
        self.change_cmap_menu = QtWidgets.QMenu('Change colormap')
        self.change_cmap_actions = []
        def callback_prototype(imgbase, cmap_name=default_cmap):
            ct = CMap().load_ct(cmap_name)
            imgbase.baselut = ct
            imgbase.set_lut(ct)
        for name in CMap().cmaps:
            action = QtWidgets.QAction(name)
            action.triggered.connect(partial(callback_prototype, self, name))
            self.change_cmap_actions.append(action)
            self.change_cmap_menu.addAction(action)
        self.cmap_menu.addMenu(self.change_cmap_menu)

        # Edit colormap
        self.edit_cmap_action = QtWidgets.QAction('Edit Color Map')
        self.edit_cmap_action.triggered.connect(self.edit_cmap)
        self.cmap_menu.addAction(self.edit_cmap_action)
        self.menu.addMenu(self.cmap_menu)

        self.cmap_editor = QtWidgets.QWidget() #AP removed comment to run
        # everything that will happen in edit cmap comes from the Class CMapEditor
        #maybe it should be written as self.cmap_CMapEditor()
        self.build_cmap_form()

    def edit_cmap(self):
        dialog = CMapDialog(self.data)
        r = dialog.exec()
        if r == 1:
            lut = dialog.widget.get_lut()
            self.img.setLookupTable(lut)

    def build_cmap_form(self):        
        pass

    def cmap_reset(self):
        self.img.setLookupTable(self.baselut)
        self.img.setLevels([np.min(self.data.values), np.max(self.data.values)])

    def cmap_reverse(self):
        colors = self.lut
        colors_r = np.array(list(reversed(colors)))
        print(colors[0],colors_r[0])
        self.img.setLookupTable(colors_r)

    def roi_export_method(self):
            print("export button works")
            self.imgROI.export()
            #self.imgROI.norm_data()
        
   
    def cmap_to_range(self):
        [[xmin, xmax], [ymin, ymax]] = self.vb.viewRange()
        mat = self.data.sel(slice(xmin, xmax), slice(ymin, ymax)).values
        if mat.size < 2:
            return
        self.img.setLevels([np.min(mat), np.max(mat)])

    def showDialog_roi_stats(self):
        msgBox = QMessageBox()
        message = self.imgROI.stats_message()
        msgBox.setText(message)
        msgBox.setWindowTitle("QMessageBox ROI Stats")
        msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        msgBox.buttonClicked.connect(msgButtonClick)

        returnValue = msgBox.exec()
        if returnValue == QMessageBox.Ok:
            print('OK clicked')
   
def msgButtonClick(i):
   print("Button clicked is:",i.text())

def test():
    import sys
    from pyimagetool.data import triple_cross_2d, arpes_data_2d
    app = QtGui.QApplication([])

    window = QtWidgets.QWidget()
    layout = QtWidgets.QVBoxLayout()
    window.setLayout(layout)
    pg_view = pg.GraphicsLayoutWidget(window)
    image_slice1 = ImageSlice(triple_cross_2d())
    image_slice2 = ImageSlice(arpes_data_2d())
    pg_view.addItem(image_slice1)
    pg_view.addItem(image_slice2)

    layout.addWidget(pg_view)

    window.resize(400, 400)
    window.show()

    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()

