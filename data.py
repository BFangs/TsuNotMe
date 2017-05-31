from osgeo import gdal
import numpy as np

geo = gdal.Open('imgn38w123_13.img')
bay_data = geo.ReadAsArray()

BAY = {'W': -123.0005555556,
       'E': -121.9994444445,
       'N': 38.00055555556,
       'S': 36.99944444444,
       'steps_x': 10812,
       'steps_y': 10812,
       'incr': 100}
#longitude (west is base)
#latitude (north is base)
