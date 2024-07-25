#import sys
import pyqtgraph as pg
import numpy as np

#from pyqtgraph.Qt import QtGui, QtCore
#from pyqtgraph.GraphicsScene.mouseEvents import HoverEvent

#from pyimagetool import PGImageTool
from pyimagetool.DataMatrix import RegularDataArray
#from pyimagetool.cmaps import CMap
from pyimagetool.DataModel import ValueLimitedModel
#from pyimagetool.pgwidgets.BinningLine import BinningLine
#from pyimagetool.pgwidgets.ImageSlice import ImageSlice         ####CIRCULAR IMPORT
from typing import Dict, List, Tuple, Union


class ROI(pg.ROI):
    """An object that holds a list of current index and position of the cursor location. Warning: this function
    will raise a list indexing error if you access y, z, or t variables on data which does not have that as a
    dimension.
    """
    def __init__(self, img_data: RegularDataArray):    
        """
        :param data: Regular spaced data, which will be used to calculate how to transform axis to coordinate
        for ROI, _pos is minimum position and _size is maximum position
        """
        self._img_data = img_data #loaded data
        self._reduced_data_ROI = img_data #after slicing roi

        #get initial roi position and size
        _index: List[ValueLimitedModel] = [ValueLimitedModel(0, 0, imax) for imax in np.array(img_data.shape) - 1]
        _pos: List[ValueLimitedModel] = [ValueLimitedModel(cmin, cmin, cmax)
                                              for cmin, cmax in zip(img_data.coord_min, img_data.coord_max)]
        
        _size_index: List[ValueLimitedModel] = [ValueLimitedModel(0, 0, imin) for imin in np.array(img_data.shape) - 1]
        _size_pos: List[ValueLimitedModel] = [ValueLimitedModel(cmax, cmin, cmax)
                                              for cmin, cmax in zip(img_data.coord_min, img_data.coord_max)]
        
        print('_index',_index)
        print('_pos',_pos)
        print('_size_index',_size_index)
        print('_size_pos',_size_pos)
        
        self.roi = pg.ROI(pos =(_index[0].value, _pos[1].value), size =(_size_index[0].value, _size_pos[1].value), pen = 'g')
        
        #self.roi = pg.ROI((self._index[0],self._index[1]),(self._size_index[0],self._size_index[1]), pen = 'g')

    def connectROI(self):
        # roi is the "parent" roi, i is the index of the handle in roi.handles
        self.roi.append(self.roi)
        
    def disconnectROI(self, roi):
        self.rois.remove(roi)

    def reset(self, data=None): #to be modified, copied from cursor
        if data is not None:
            self.data = data
            for i in range(self.data.ndim):
                self._index[i]._lower_lim = 0
                self._index[i]._upper_lim = self.data.shape[i] - 1
                self._pos[i]._lower_lim = self.data.coord_min[i]
                self._pos[i]._upper_lim = self.data.coord_max[i]
        for i in range(self.data.ndim):
            self.set_index(i, 0)

    @property
    def pos(self):
        return self.roi.pos()

    @property
    def size(self):
        return self.roi.size()


    

    def get_roi_xy(self):
        debug = True
        def find_nearest(arr,val):
            index = np.absolute(arr-val).argmin()
            return index
        
        # TOP LEFT CORNER(1)
        #x1,y1 = self._pos[0].value, self._pos[1].value
        x1,y1 = self.roi.pos()
        if debug:
            print('x1,y1',x1,y1)

        # ABSOLUTE DIFFERENCE IN X AND Y DIRECTION
        #w,h = self._size_pos[0].value, self._size_pos[0].value
        dx = np.absolute(x1 - (x1 + self.roi.size()[0]))
        dy = np.absolute(y1 - (y1 + self.roi.size()[1]))
        if debug:
            print('dx,dy',dx,dy)

        # TOP RIGHT CORNER (2)
        x2 = x1 + dx
        y2 = y1
        if debug:
            print('x2,y2',x2,y2)

        # BOTTOM RIGHT CORNER (3)
        x3 = x2
        y3 = y1 + dy
        if debug:
            print('x3,y3',x3,y3)

        # BOTTOM LEFT CORNER (4)
        x4 = x1
        y4 = y3
        if debug:
            print('x4,y4',x4,y4)



        x1_index = find_nearest(self._img_data.axes[0], x1)
        if debug:
            print('x1_index',x1_index)
        x2_index = find_nearest(self._img_data.axes[0], x2)
        if debug:
            print('x2_index',x2_index)
        x3_index = find_nearest(self._img_data.axes[0], x3)
        if debug:
            print('x3_index',x3_index)
        x4_index = find_nearest(self._img_data.axes[0], x4)
        if debug:
            print('x4_index',x4_index)

        y1_index = find_nearest(self._img_data.axes[1], y1)
        if debug:
            print('y1_index',y1_index)
        y2_index = find_nearest(self._img_data.axes[1], y2)
        if debug:
            print('y2_index',y2_index)
        y3_index = find_nearest(self._img_data.axes[1], y3)
        if debug:
            print('y3_index',y3_index)
        y4_index = find_nearest(self._img_data.axes[1], y4)
        if debug:
            print('y4_index',y4_index)
        
  
        return((x1_index,x3_index),(y1_index,y3_index))
       

    

    













# class ROI(pg.ROI):
#     def_init_(self,pos, size): # type: ignore
#     pg.ROI._init_(self,pos,size)

# self.addScaleHandle((1,1), (0,0))

    
# #roi = pg.ROI([10,10], [50,50])
# #roi.setPen(pg.mkPen(color='r', width = 2))
# #roi.setbrush(pg.mkBrush(color = 'b', alpha = 0.5))

# roi = ROI((100,100), (200,200))
 #view = pg.GraphicsView()
# view.addItem(roi)
# """

# '''roi = ROI(pos(-8,14), size =(100,20), pen = 'g')
#    roi.addScalehandle((0.5,1), (0.5,0.5))
#    img_ax.addItem(roi)'''