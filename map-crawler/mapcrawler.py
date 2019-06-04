import mercantile
from concurrent.futures import ThreadPoolExecutor
import requests
import fire
import os
from io import BytesIO
import shutil
import base64
from PIL import Image
import numpy as np
from tqdm import tqdm
import rasterio
from rasterio.crs import CRS

from config import defaults_provider
from utils import tile_affine


def crawl_tiles(request_url, save_path, x, y, z):
    print(request_url, save_path)
    r = requests.get(request_url, stream=True)
    if r.status_code==200:
        bites = BytesIO(r.content)
        arr = np.array(Image.open(bites))
        out_meta={}
        out_meta['driver']='JPEG'
        out_meta['crs'] = CRS(init='epsg:3857')
        out_meta['transform'] = tile_affine(y, x, z)
        out_meta['count']=3
        out_meta['dtype']='uint8'
        out_meta['width']=256
        out_meta['height']=256
        print(arr.shape)
        with rasterio.open(save_path, 'w', **out_meta) as dst:
            dst.write(arr.transpose().swapaxes(2,1))
    else:
        print('未解析正确的url: {}'.format(request_url))


def main(zoom_level, lb_coord, rt_coord, 
        out_dir='./map_tiles', 
        out_filename='merged.tif', 
        provider='google-images-offset',
        merge_tiles=True,
):
    """影像数据爬虫脚本, 注意爬取某个级别时请先删除其它级别文件
    
    Arguments:
        zoom_level {int} -- 所要爬取的级别,
        lb_coord {tuple} -- left bottom 左下角经纬度坐标，例如(140.0, 39.0)
        rt_coord {tuple} -- top right 右上角经纬度坐标，例如(140.1, 39.2)
    
    Keyword Arguments:
        out_dir {str} -- 存储路径 (default: {'./map_tiles'})
        out_filename {str} -- 最终结果名称 (default: {'merged.tif'})
        provider {str} -- 爬取哪家的数据  (default: {'google-images'})
                        google-images-no-offset
                        google-map-no-offset
                        google-images-offset
                        google-map-offset
        
    """
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    #1. crawl the tiles
    if provider in defaults_provider.keys():
        url = defaults_provider[provider]
    elif not provider.startswith('http'):
        raise ValueError('{} 不合法'.format(provider))
    else:
        url = provider

    # 1.1 计算最大和最小行列号
    min_x, max_y, _ = mercantile.tile(lb_coord[0], lb_coord[1], zoom_level)
    max_x, min_y, _ = mercantile.tile(rt_coord[0], rt_coord[1], zoom_level)
    tiles_urls = []
    for tile_x in tqdm(range(min_x, max_x+1)):
        for tile_y in range(min_y, max_y+1):
            file_name = os.path.join(out_dir, '{}_{}_{}.jpg'.format(zoom_level, tile_x, tile_y))
            if os.path.exists(file_name):
                continue
            tiles_urls.append((url.format(x=tile_x, y=tile_y, z=zoom_level), file_name, tile_x, tile_y, zoom_level))

    with ThreadPoolExecutor(max_workers=1) as executor:
        executor.map(lambda p: crawl_tiles(*p), tiles_urls)

    #2. merge tiles use gdal_merge.py
    if not merge_tiles:
        exit
    
    import subprocess
    from pathlib import Path
    from glob import glob
    exts = [".jpg", ".tiff", '.tif']
    imagelist = list((str(i) for i in map(Path, glob(os.path.join(out_dir,'*'))) if i.suffix.lower() in exts and not i.stem.startswith(".")))

    merge_command = 'gdal_merge.py -o {} -of GTiff '.format(out_filename) + ' '.join(imagelist)
    print(merge_command)
    subprocess.call(merge_command, shell=True)


if __name__ == "__main__":
    fire.Fire(main)