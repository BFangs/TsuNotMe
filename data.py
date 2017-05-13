from osgeo import gdal
import numpy as np

geo = gdal.Open('imgn38w123_13.img')
arr = geo.ReadAsArray()
print repr(arr)

np.save("data.npy", arr)


