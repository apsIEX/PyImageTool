from pyqtgraph.Qt import QtCore, QtWidgets
from functools import partial
from typing import Union
import pyqtgraph as pg
import numpy as np
import warnings

from pyimagetool.widgets import TabsWidget
from pyimagetool.PGImageTool import PGImageTool
from pyimagetool.DataMatrix import RegularDataArray

from pyimagetool.cmaps.CMap import  default_cmap

try:
    import xarray as xr
    DataType = Union[RegularDataArray, np.array, xr.DataArray]
except ImportError:
    xr = None
    DataType = Union[RegularDataArray, np.array]


"""
ImageTool instance  
    tool => pyimagetool.ImageTool()
    tool.pg_win => pyimagetool.PGImageTool.PGImageTool()
    tools.pg_widget => pyqtgraph.Qt.QtWidgets.QWidget()
    tool.tabs_widget => pyimagetool.widgets.TabsWidget()

"""

class ImageTool(QtWidgets.QWidget):
    LayoutSimple = PGImageTool.LayoutSimple
    LayoutComplete = PGImageTool.LayoutComplete
    LayoutRaster = PGImageTool.LayoutRaster

    def __init__(self, data: DataType, layout: int = PGImageTool.LayoutSimple, parent=None):
        """Create an ImageTool QWidget.
        :param data: A RegularDataArray, numpy.array, or xarray.DataArray
        :param layout: An int that defines the layout. See PGImageTool for layout definitions
        :param parent: QWidget that will be this widget's parent
        """
        super().__init__(parent)
        # Warn user about nan
        if hasattr(data, 'values'):
            d = data.values
        else:
            d = data
        if np.any(np.isnan(d)):
            warnings.warn('Input data contains NaNs. All NaN will be set to 0.')
            d[np.isnan(d)] = 0
        # Create data
        self.data: RegularDataArray = RegularDataArray(data)
        #dictionary of all local variable 
        self.vars = {'it_layout': layout,
                     'cmap_name': default_cmap,
                     'cmap_reverse':False,
                     'cmap_gamma':1
                     } 

        # Create tabs and ImageTool PyQt Widget
        self.tabs_widget = TabsWidget(self.data, parent=self)
        self.pg_widget = QtWidgets.QWidget()  # widget to hold pyqtgraph graphicslayout
        self.pg_widget.setLayout(QtWidgets.QVBoxLayout())
        self.pg_win = PGImageTool(self.data, layout=layout)  # the pyqtgraph graphicslayout
        self.pg_widget.layout().addWidget(self.pg_win)
        # Build the layout
        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().addWidget(self.tabs_widget)
        self.layout().addWidget(self.pg_win)
        # Create status bar
        self.status_bar = QtWidgets.QStatusBar(self)
        self.status_bar.showMessage("Initialized")
        self.layout().addWidget(self.status_bar)
        # Connect signals and slots
        self.mouse_move_proxy = pg.SignalProxy(self.pg_win.mouse_hover, rateLimit=30, slot=self.update_status_bar)
        self.build_handlers()
        # TODO: update to QT 5.14 and use textActivated signal instead
        self.tabs_widget.colors_tab.reverse_cmap_checkbox.clicked.connect(self.set_all_cmaps_reverse)
        self.tabs_widget.colors_tab.cmap_combobox.currentTextChanged.connect(self.set_all_cmaps_name)#here
        self.tabs_widget.colors_tab.gamma_slider.valueChanged.connect(self.set_all_gamma_spinbox_slot)
        self.tabs_widget.colors_tab.gamma_spinbox.valueChanged.connect(self.set_all_gamma_slider_slot)

        self.tabs_widget.info_tab.transpose_request.connect(self.transpose_data)

    def update_status_bar(self, msg: tuple):
        """Slot for mouse move signal"""
        self.status_bar.showMessage(msg[0])

    def build_handlers(self):
        # Connect index spin box to model
        # -------------------------------
        def update_spinbox_view(spinbox: QtWidgets.QSpinBox, i: int):
            spinbox.blockSignals(True)
            spinbox.setValue(i)
            spinbox.blockSignals(False)

        for i, sb in enumerate(self.tabs_widget.info_tab.cursor_i):
            sb.valueChanged.connect(partial(self.pg_win.cursor.set_index, i))
            self.pg_win.cursor.index[i].value_set.connect(partial(update_spinbox_view, sb))

        # Connect coordinate spin box to model
        # ------------------------------------
        def control_doublespinbox(doublespinbox: QtWidgets.QDoubleSpinBox, handler):
            handler(doublespinbox.value())

        def update_doublespinbox_view(doublespinbox: QtWidgets.QDoubleSpinBox, v: float):
            doublespinbox.blockSignals(True)
            doublespinbox.setValue(v)
            doublespinbox.blockSignals(False)

        for i, dsb in enumerate(self.tabs_widget.info_tab.cursor_c):
            dsb.editingFinished.connect(partial(control_doublespinbox, dsb,
                                                partial(self.pg_win.cursor.set_pos, i)))
            self.pg_win.cursor.pos[i].value_set.connect(partial(update_doublespinbox_view, dsb))

        # Connect binwidth to model
        # -------------------------
        for i, sb in enumerate(self.tabs_widget.bin_tab.bin_i):
            sb.valueChanged.connect(partial(self.pg_win.cursor.set_binwidth_i, i))
            self.pg_win.cursor.binwidth[i].value_set.connect(partial(self.update_binwidth_index_view,
                                                                     sb, i))

        for i, dsb in enumerate(self.tabs_widget.bin_tab.bin_c):
            dsb.editingFinished.connect(partial(control_doublespinbox, dsb,
                                                partial(self.pg_win.cursor.set_binwidth, i)))
            self.pg_win.cursor.binwidth[i].value_set.connect(partial(update_doublespinbox_view, dsb))

    def update_binwidth_index_view(self, spinbox, i, newvalue):
        spinbox.blockSignals(True)
        spinbox.setValue(round(newvalue/self.data.delta[i]))
        spinbox.blockSignals(False)

    def reset(self):
        layout = QtWidgets.QBox.Layout()
        self.tabs_widget.reset(self.data)
        self.pg_win.reset(self.data)

    def set_all_cmaps_reverse(self,reverse):
        self.vars['cmap_reverse'] = reverse
        self.set_all_cmaps()
    
    def set_all_cmaps_name(self,cmap_name):
        self.vars['cmap_name'] = cmap_name
        self.set_all_cmaps()
       
    def set_all_cmaps(self):
        print('ImageTool.set_all_cmaps: ',self.vars['cmap_name'],self.vars['cmap_reverse'],self.vars['cmap_gamma'])
        self.pg_win.load_ct(self.vars['cmap_name'],self.vars['cmap_reverse'],self.vars['cmap_gamma'])

    def set_all_gamma_spinbox_slot(self, spinbox_value):
        self.tabs_widget.colors_tab.gamma_spinbox.blockSignals(True)
        self.tabs_widget.colors_tab.gamma_spinbox.setValue(10**(spinbox_value/20))
        self.tabs_widget.colors_tab.gamma_spinbox.blockSignals(False)
        self.vars['cmap_gamma'] = 10**(spinbox_value/20)
        self.pg_win.load_ct(self.vars['cmap_name'],self.vars['cmap_reverse'],self.vars['cmap_gamma'])

    def set_all_gamma_slider_slot(self,slider_value):
        self.tabs_widget.colors_tab.gamma_slider.blockSignals(True)
        self.tabs_widget.colors_tab.gamma_slider.setValue(round(20*np.log10(self.tabs_widget.colors_tab.gamma_spinbox.value())))
        self.tabs_widget.colors_tab.gamma_slider.setValue(round(20*np.log10(self.tabs_widget.colors_tab.gamma_spinbox.value())))

        self.tabs_widget.colors_tab.gamma_slider.blockSignals(False)
        self.vars['cmap_gamma'] =  self.tabs_widget.colors_tab.gamma_spinbox.value()
        self.pg_win.load_ct(self.vars['cmap_name'],self.vars['cmap_reverse'],self.vars['cmap_gamma'])

    def transpose_data(self, tr):
        self.data = self.data.transpose(tr)
        self.reset()

    def keyReleaseEvent(self, e):
        if e.key() == QtCore.Qt.Key_Shift:
            self.pg_win.shift_down = False
        else:
            e.ignore()

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Shift:
            self.pg_win.shift_down = True
            self.pg_win.set_crosshair_to_mouse()
        else:
            e.ignore()

    def get(self, plot: str):
        """Get a slice of the data shown in ImageTool.

        :param plot: should be one of ``x``, ``y``, ``z``, ``xy``, ``zy``, ``xt``, etc. depending on the plotted data
        :type plot: str
        :return: If returning an image, will return RegularDataArray. Otherwise, returns a tuple of x, y
        """
        # TODO: make plot items display RegularDataArray and consistently return a RegularDataArray
        plot = plot.lower()
        if plot in self.pg_win.imgs.keys():
            return self.pg_win.imgs[plot].data
        elif plot in self.pg_win.lineplots_data.keys():
            p = self.pg_win.lineplots_data[plot]
            if p[1] == 'h':
                return p[0].xData, p[0].yData
            else:
                return p[0].yData, p[0].xData
        else:
            legalvalues = list(self.pg_win.imgs.keys()) + list(self.pg_win.lineplots_data.keys())
            raise ValueError(f'plot {plot} not found in this ImageTool. Should be one of {legalvalues}')
