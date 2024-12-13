import numpy as np

def norm_axis_shape(data,axis):
    """
    """
    dims = len(data.shape)
    if dims==2:
        axes_list = [(0,1),(1,0)]
        return axes_list
    if dims==3:
        axes_list = [(0,1,2),(1,0,2),(1,2,0)]
        return axes_list
    
def norm_by_area(data,axis=0):
    """
    returns norm_data = data/Area

    data is a numpy array of any shape
    axis is the index for the axis to normalize by
    """
    axes_list = norm_axis_shape(data,axis)
    norm_data = np.transpose(data,axes=axes_list[axis])/np.trapz(data,axis=axis)
    return np.transpose(norm_data,axes=axes_list[-axis])

def norm_by_mean(data,axis=0):
    """
    returns norm_data = data/Area

    data is a numpy array of any shape
    axis is the index for the axis to normalize by
    """
    axes_list = norm_axis_shape(data,axis)
    norm_data = np.transpose(data,axes=axes_list[axis])/np.mean(data,axis=axis)
    return np.transpose(norm_data,axes=axes_list[-axis])
                    

def norm_minus_min(data,axis=0):
    """
    returns norm_data = data - min

    data is a numpy array of any shape
    axis is the index for the axis to normalize by
    """
    axes_list = norm_axis_shape(data,axis)
    norm_data = np.transpose(data,axes=axes_list[axis]) - np.min(data,axis=axis)
    return np.transpose(norm_data,axes=axes_list[-axis])

def norm_minus_min_by_area(data,axis=None):
    """
    returns norm _data = (data - min)/Area

    data is a numpy array of any shape
    axis is the index for the axis to normalize by
    """
    axes_list = norm_axis_shape(data,axis)
    norm_data = (np.transpose(data,axes=axes_list[axis]) - np.min(data,axis))/np.mean(data,axis=axis)             
    return np.transpose(norm_data,axes=axes_list[-axis])
                        
def norm_to_one(data,axis=None):
    """
    returns norm _data = (data - min)/(max - min)

    data is a numpy array of any shape
    axis is the index for the axis to normalize by
    """
    axes_list = norm_axis_shape(data,axis)
    norm_data = (np.transpose(data,axes=axes_list[axis]) - np.min(data,axis=axis))/(np.max(data,axis=axis) - np.min(data,axis=axis))                
    return np.transpose(norm_data,axes=axes_list[-axis])