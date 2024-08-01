#import sys
import pyqtgraph as pg
import numpy as np

import PyQt5 as pq5

from pyqtgraph.Qt import QtGui, QtCore
#from pyqtgraph.GraphicsScene.mouseEvents import HoverEvent

#from pyimagetool import PGImageTool
from PyQt5.QtWidgets import QMessageBox
from pyimagetool.DataMatrix import RegularDataArray
#from pyimagetool.cmaps import CMap
from pyimagetool.DataModel import ValueLimitedModel
#from pyimagetool.pgwidgets.BinningLine import BinningLine
#from pyimagetool.pgwidgets.ImageSlice import ImageSlice         ####CIRCULAR IMPORT
from typing import Dict, List, Tuple, Union
from pyimagetool import ImageTool


class imgROI():
    """An object that holds a list of current index and position of the cursor location. Warning: this function
    will raise a list indexing error if you access y, z, or t variables on data which does not have that as a
    dimension.
    """
    
    def __init__(self):    
        """
        :param data: Regular spaced data, which will be used to calculate how to transform axis to coordinate
        for ROI, _pos is minimum position and _size is maximum position
        """
        self._img_data = None #loaded data
        self.roi = None

        #get initial roi position and size

        
        #print('_index',_index)
        #print('_pos',_pos)
        #print('_size_index',_size_index)
        #print('_size_pos',_size_pos)
        
        
        
        #self.roi = pg.ROI((self._index[0],self._index[1]),(self._size_index[0],self._size_index[1]), pen = 'g')

    def set_img_data(self, img_data: RegularDataArray):
        self._img_data = img_data
        _index: List[ValueLimitedModel] = [ValueLimitedModel(0, 0, imax) for imax in np.array(img_data.shape) - 1]
        _pos1: List[ValueLimitedModel] = [ValueLimitedModel(cmin, cmin, cmax)
                                            for cmin, cmax in zip(img_data.coord_min, img_data.coord_max)]
        
        _size_index: List[ValueLimitedModel] = [ValueLimitedModel(0, 0, imin) for imin in np.array(img_data.shape) - 1]
        _pos2: List[ValueLimitedModel] = [ValueLimitedModel(cmax, cmin, cmax)
                                            for cmin, cmax in zip(img_data.coord_min, img_data.coord_max)]
        self.roi = pg.ROI(pos =(_pos1[0].value, _pos1[1].value), size =(_pos2[0].value-_pos1[0].value, _pos2[1].value-_pos1[1].value,), pen = 'g')

    def reduce_data(self):
        """
        getting the roi position and size and then returning the sliced data
        """
        pos_coord, pos_index = self.get_coord_index()
        ((x1,y1),(x2,y2),(x3,y3),(x4,y4)) = pos_coord
        (x1_index,x2_index),(y1_index,y4_index) = pos_index

        reduced_data = self._img_data[x1_index:x2_index, y1_index:y4_index]

        return reduced_data
        
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
 

    def get_coord_index(self):
        """
        gives coordinate points for all four corners of ROI
        gives the index of the coordinate points
        
        returns (pos_coord, pos_index)
            pos_coord = ((x1,y1),(x2,y2),(x3,y3),(x4,y4))
            pos_index = ((x1_index,x2_index),(y1_index,y4_index))
        """
        debug = True
        def find_nearest(arr,val):
            index = np.absolute(arr-val).argmin()
            return index
        
        #   (x1,y1)             (x2,y2)
        #
        #
        #   (x4,y4)             (x3,y3)

        # TOP LEFT CORNER(1)
        x1, y1 = self.roi.pos()
        
        # ABSOLUTE DIFFERENCE IN X AND Y DIRECTION
        #w,h = self._size_pos[0].value, self._size_pos[0].value
        dx = np.absolute(x1 - (x1 + self.roi.size()[0]))
        dy = np.absolute(y1 - (y1 + self.roi.size()[1]))
      
        # TOP RIGHT CORNER (2)
        x2 = x1 + dx
        y2 = y1
        
        # BOTTOM RIGHT CORNER (3)
        x3 = x2
        y3 = y1 + dy
       
        # BOTTOM LEFT CORNER (4)
        x4 = x1
        y4 = y3
        
        #index claculation from loaded data

        x1_index = find_nearest(self._img_data.axes[0], x1)
        
        x2_index = find_nearest(self._img_data.axes[0], x2)
        
        x3_index = find_nearest(self._img_data.axes[0], x3)
        
        x4_index = find_nearest(self._img_data.axes[0], x4)
       
        y1_index = find_nearest(self._img_data.axes[1], y1)
        
        y2_index = find_nearest(self._img_data.axes[1], y2)
        
        y3_index = find_nearest(self._img_data.axes[1], y3)
        
        y4_index = find_nearest(self._img_data.axes[1], y4)
       
        pos_coord = ((x1,y1),(x2,y2),(x3,y3),(x4,y4))
        pos_index = ((x1_index,x2_index),(y1_index,y4_index))


        return (pos_coord, pos_index)


    def stats(self,verbose=True):
        """
        returns ROI center, size, position 
                max, min and mean of the data within the roi (reduced data)
        """
        
        reduced_data = self.reduce_data()
        position = self.roi.pos()
        size = self.roi.size()
        reduced_data_max = np.max(reduced_data)
        reduced_data_min = np.min(reduced_data)
        reduced_data_mean = np.mean(reduced_data.data)
        
        if verbose:
            print("max", reduced_data_max)
            print("min", reduced_data_min)
            print("mean", reduced_data_mean)
                
        return position,size,reduced_data_min, reduced_data_max, reduced_data_mean

    def export(self):
        print('exporting roi')
        return self.reduce_data()
        


    def stats_message(self):
        position,size,reduced_data_min, reduced_data_max, reduced_data_mean = self.stats(verbose=False)

        message = f" Position: {position}\n Size: {size}\n Max: {reduced_data_max}\n Min: {reduced_data_min}\n Mean: {reduced_data_mean}"
        return message

    
        
    def norm_data(self,norm_type):
        """
        return numpy array of data that has been normalized
        """
        norm_list = ['by_mean','to_one','by_max']
        data = self._img_data.data
        if norm_type in norm_list:
            if norm_type == 'by_mean':
                normed_data = data/np.mean(data)
            elif norm_type == 'to_one':
                normed_data = (data-np.min(data))/(np.max(data)-np.min(data))
            elif norm_type == 'by_max':
                normed_data = data / (np.max(data))
            return normed_data 
        else:
            print('not a valid norm_type, choose: ',norm_list)
            return



