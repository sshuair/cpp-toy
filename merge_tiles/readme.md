## Merge Tiles

合并零碎的地图瓦片到一个大文件中。

## 说明
爬取下来的瓦片存储在sqlite3中，表名为`cache`，具体格式如下：
![](./assets/tile-in-sqlite.png)


- 第一步：合并文件为jpeg
- 第二部：将大的jpeg定义投影


