import os
import numpy as np

names = {
    'ColdWarm': 'cold_warm',
    'RainbowLight': 'rainbow_light',
    'Terrain': 'terrain',
    'BuPu' :'BuPu'
}
def make_igor_cmaps():
    for dirName, subdirList, fileList in os.walk('data'):
        if dirName == '.' + os.sep + 'igor_cmap':
            for filename in fileList:
                kwd = filename[:-4]
                if kwd in names.keys():
                    dat = np.loadtxt(dirName + os.sep + filename, dtype=np.uint8, delimiter='\t')
                    newname = os.path.splitext('.' + os.sep + 'cmaps' + os.sep + names[kwd])[0]
                    print(newname)
                    np.save(newname, dat)
