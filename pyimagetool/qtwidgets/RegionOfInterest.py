#import sys
import pyqtgraph as pg
import numpy as np

import PyQt5 as pq5

from pyqtgraph.Qt import QtGui, QtCore

from PyQt5.QtWidgets import QMessageBox
from pyimagetool.DataMatrix import RegularDataArray
from pyimagetool.DataModel import ValueLimitedModel
from typing import Dict, List, Tuple, Union



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
        self._reduced_data = None
        self.roi = None

        #ROI position coordinates (pos is in scaled units, ind is index)
        self.pos1 = (0,0)
        self.ind1 = (0,0)
        self.pos2 = (0,0)
        self.ind2 = (0,0)
        self.pos3 = (0,0)
        self.ind3 = (0,0)
        self.pos4 = (0,0)
        self.ind4 = (0,0)

        #1D norm variable
        self.norm1_mode = 0
        self.norm1_axis = 0
        self.norm1_x0 = 0
        self.norm1_x1 = 0
        self.norm1_p0 = 0
        self.norm1_p1 = 0
        #2D norm variable
        self.norm2_mode = 0
        self.norm2_axis = 0
        self.norm2_x0 = 0
        self.norm2_x1 = 0
        self.norm2_p0 = 0
        self.norm2_p1 = 0


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
        self.get_coord_index()
        x1_index = self.ind1[0]
        x2_index = self.ind2[0]
        y1_index = self.ind1[1]
        y4_index = self.ind4[1]

        reduced_data = self._img_data[x1_index:x2_index, y1_index:y4_index]
        self._reduced_data = reduced_data
        
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
        debug = False

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

        self.pos1 = (x1,y1)
        self.ind1 = (x1_index,y1_index)
        self.pos2 = (x2,y2)
        self.ind2 = (x2_index,y2_index)
        self.pos3 = (x2,y3)
        self.ind3 = (x3_index,y3_index)
        self.pos4 = (x4,y4)
        self.ind4 = (x4_index,y4_index)
       
        pos_coord = ((x1,y1),(x2,y2),(x3,y3),(x4,y4))
        pos_index = ((x1_index,x2_index),(y1_index,y4_index))


        return (pos_coord, pos_index)


    def stats(self,verbose=True):
        """
        returns ROI center, size, position 
                max, min and mean of the data within the roi (reduced data)
        """
        reduced_data = self._reduce_data
        stats_dict={}
        stats_dict['img'] = reduced_data
        stats_dict['position'] = self.roi.pos()
        stats_dict['size'] = self.roi.size()

        stats_dict['img_max']  = np.max(reduced_data)
        stats_dict['img_min']  = np.min(reduced_data)
        stats_dict['img_mean']  = np.mean(reduced_data)
        stats_dict['img_sum']  = np.sum(reduced_data)
        
        stats_dict['max_1']  = np.max(reduced_data,1)
        stats_dict['max_0']  = np.max(reduced_data,0)
        stats_dict['min_1']  = np.min(reduced_data,1)
        stats_dict['min_0']  = np.min(reduced_data,0)
        stats_dict['avg_1']  = np.mean(reduced_data,1)
        stats_dict['avg_0']  = np.mean(reduced_data,0)

        stats_dict['']  = None
        stats_dict['']  = None
        stats_dict['']  = None

        
                
        #return position,size,reduced_data_min, reduced_data_max, reduced_data_mean
        return stats_dict

    def export(self):
        print('exporting roi')
        return self._reduce_data

    def stats_message(self):
        stats_dict = self.stats()
        position = stats_dict['position']
        size = stats_dict['size']
        img_min = stats_dict['img_min']
        img_max = stats_dict['img_max']
        img_mean = stats_dict['img_mean']
        
        message = f" Position: {position}\n Size: {size}\n Max: {img_max}\n Min: {img_min}\n Mean: {img_mean}"
        return message

    
        
    def norm_data(self,norm_type,axisNum):
        """
        return numpy array of data that has been normalized
        axisNum = 0,1 
        """
        norm_list = ['by_mean','to_one','by_max']
        stats_dict = self.stats()
        norm_img = np.empty_like(self._reduce_data)

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



    def update_data(self,action_name):
        '''
        
        '''
        if 'crop' in action_name:
            img = self._reduce_data
        elif 'norm' in action_name:
            img = self.norm_data(action_name)

        return img
  