from pyimagetool.DataMatrix import RegularDataArray
from pyimagetool.ImageTool import ImageTool
from pyimagetool.PGImageTool import PGImageTool
from pyimagetool.imagetool_wrapper import IT_WRAPPER

__all__ = ['ImageTool', 'RegularDataArray']

tools = IT_WRAPPER()
def imagetool(data):
    from pyqtgraph.Qt import QtCore, QtWidgets, QtGui
    import sys
    app = QtWidgets.QApplication.instance()
    if app is None:
        app = QtGui.QApplication([])
        tool = ImageTool(data, layout=PGImageTool.LayoutComplete)
        tool.show()
        if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
            QtWidgets.QApplication.instance().exec_()
        return tool
    else:
        tool = ImageTool(data, layout=PGImageTool.LayoutComplete)
        tool.show()
        return tool
