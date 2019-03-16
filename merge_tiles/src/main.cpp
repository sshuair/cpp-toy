#include <iostream>
#include <string>
#include <vector>
#include <SQLiteCpp/SQLiteCpp.h>
#include <opencv2/opencv.hpp>

using namespace std;
using namespace cv;

typedef unsigned char BYTE;

void get_merged_img(SQLite::Database &db, cv::Mat &dst,  int merge_num, int row, int col)

{
    // cv::Mat dst(cv::Size(256 * merge_num, 256 * merge_num), CV_8UC3);

    for (int mini_row = 0; mini_row < merge_num; ++mini_row)
    {
        for (int mini_col = 0; mini_col < merge_num; ++mini_col)
        {
            string query_sql = "SELECT * FROM cache where row_id=" + std::to_string(row + mini_row) + " and col_id=" + std::to_string(col + mini_col);
            SQLite::Statement query(db, query_sql);
            while (query.executeStep())
            {
                int level = query.getColumn(0);
                const string img_type = query.getColumn(3);
                string img_blob = query.getColumn(4);

                //将blob转为vector，然后转为cv2的mat类型
                std::vector<BYTE> vectordata(img_blob.begin(), img_blob.end());
                cv::Mat data_mat(vectordata, true);
                cv::Mat image(cv::imdecode(data_mat, 1)); //put 0 if you want greyscale

                //将图像拷贝到对应位置
                image.copyTo(dst(cv::Rect(mini_col * 256, mini_row * 256, image.cols, image.rows)));
            }
        }
    }
    // return dst;
}


int main(int argc, char const *argv[])
{
    // const string db_path = "../data/google.sqlite";
    /*
    argv[1]: sqlite 文件所在路径
    argv[2]: 行、列方向各自合并多少图片
    argv[3]: 目标文件夹
    */

    const string db_path = argv[1]; 

    const int merge_num = atoi(argv[2]); //行、列方向各自合并多少图片

    try
    {
        SQLite::Database db(db_path);

        // 查询出最大与最小的行列号
        int min_row_id = 0, max_row_id = 0, min_col_id = 0, max_col_id = 0;
        const string query_stat_sql = "SELECT min(row_id), max(row_id), min(col_id), max(col_id) FROM cache";
        SQLite::Statement query_stat(db, query_stat_sql);
        while (query_stat.executeStep())
        {
            min_row_id = query_stat.getColumn(0);
            max_row_id = query_stat.getColumn(1);
            min_col_id = query_stat.getColumn(2);
            max_col_id = query_stat.getColumn(3);
        }

        //按照给定的merge_num大小进行循环，合成中尺度图片
        std::cout<<"processing..."<<endl;
        for (int row = min_row_id; row <= max_row_id; row += merge_num)
        {
            // 输出进度
            int percent = float(row-min_row_id) / (max_row_id-min_row_id)*100;
            std::cout<<int(percent)<<"%"<<endl;

            for (int col = min_col_id; col <= max_col_id; col += merge_num)
            {
                cv::Mat dst(cv::Size(256*merge_num, 256*merge_num), CV_8UC3);

                // cv::Mat result = get_merged_img(db, merge_num, row, col);
                get_merged_img(db, dst, merge_num, row, col);

                string filename = argv[3] + string("/") + to_string(row) + "_" + to_string(col) + ".tif";
                cv::imwrite(filename, dst);
                dst = Mat::zeros(256*merge_num, 256*merge_num, CV_8UC3);
            }
        }
    }
    catch (exception &e)
    {
        std::cout << "exception: " << e.what() << std::endl;
    }
    return 0;
}
