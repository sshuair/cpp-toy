import rasterio
from rasterio import Affine
from rasterio.crs import CRS
from fire import Fire
import mercantile

LEVEL_RESLUTION=dict([
(17, 1.1943285668550503)
])
    

# 两种方法：
# 1. 用rasterio r+ 直接打开追加，但是这种方法数据量太大

def tile_affine(tile_row, tile_col, level):
    '''
    a = width of a pixel
    b = row rotation (typically zero)
    c = x-coordinate of the upper-left corner of the upper-left pixel
    d = column rotation (typically zero)
    e = height of a pixel (typically negative)
    f = y-coordinate of the of the upper-left corner of the upper-left pixel

    reference: https://www.perrygeo.com/python-affine-transforms.html

    Arguments:
        tile_row {int} -- or y in Cartesian coordinate system
        tile_col {int} -- or x in Cartesian coordinate system
    '''
    a = LEVEL_RESLUTION[level]
    b = 0
    c, f = mercantile.xy(*mercantile.ul(tile_col,tile_row, level))
    d = 0
    e = -LEVEL_RESLUTION[level]

    return Affine(a,b,c,d,e,f)


def define_crs(in_fp, out_fp, tl_row, tl_col, zoom_level, out_format='JPEG', compress='JPEG'):
    with rasterio.open(in_fp) as src:
        out_data = src.read()
        out_meta = src.meta.copy()
    
    out_meta['driver'] = 'GTiff'
    out_meta['crs'] = CRS(init='epsg:3857')
    out_meta['transform'] = tile_affine(tl_row, tl_col, zoom_level)
    out_meta['compress'] = compress

    with rasterio.open(out_fp,'w', **out_meta) as dst:
        dst.write(out_data)



if __name__ == "__main__":
    Fire(define_crs)

