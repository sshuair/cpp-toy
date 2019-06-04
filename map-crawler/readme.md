```
Docstring:   影像数据爬虫脚本, 注意爬取某个级别时请先删除其它级别文件

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
    

Usage:       mapcrawler.py ZOOM_LEVEL LB_COORD RT_COORD [OUT_DIR] [OUT_FILENAME] [PROVIDER] [MERGE_TILES]
             mapcrawler.py --zoom-level ZOOM_LEVEL --lb-coord LB_COORD --rt-coord RT_COORD [--out-dir OUT_DIR] [--out-filename OUT_FILENAME] [--provider PROVIDER] [--merge-tiles MERGE_TILES]
```