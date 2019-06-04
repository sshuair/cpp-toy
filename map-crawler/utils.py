import rasterio
from rasterio import Affine
from rasterio.crs import CRS
from fire import Fire
import mercantile

LEVEL_RESLUTION=dict([
(0, 156543.03392800014),
(1, 78271.51696399994),
(2, 39135.75848200009),
(3, 19567.87924099992),
(4, 9783.93962049996),
(5, 4891.96981024998),
(6, 2445.98490512499),
(7, 1222.992452562495),
(8, 611.4962262813797),
(9, 305.74811314055756),
(10, 152.87405657041106),
(11, 76.43702828507324),
(12, 38.21851414253662),
(13, 19.10925707126831),
(14, 9.554628535634155),
(15, 4.77731426794937),
(16, 2.388657133974685),
(17, 1.1943285668550503),
(18, 0.5971642835598172),
(19, 0.29858214164761665),
(20, 0.14929107082380833),
(21, 0.07464553541190416),
(22, 0.03732276770595208),
(23, 0.01866138385297604),
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


def define_crs(in_fp, out_fp, tl_row, tl_col, zoom_level, out_format='GTiff', compress='JPEG'):
    with rasterio.open(in_fp) as src:
        out_data = src.read()
        out_meta = src.meta.copy()
    
    out_meta['driver'] = out_format
    out_meta['crs'] = CRS(init='epsg:3857')
    out_meta['transform'] = tile_affine(tl_row, tl_col, zoom_level)
    out_meta['compress'] = compress

    with rasterio.open(out_fp,'w', **out_meta) as dst:
        dst.write(out_data)

if __name__ == "__main__":
    def_crs('/Users/sshuair/github/cpp-toy/google-map-crawler/map_tiles/10_856_385.jpg',
    '/Users/sshuair/github/cpp-toy/google-map-crawler/map_tiles/10_856_385.tif',
    385, 856, 
    )