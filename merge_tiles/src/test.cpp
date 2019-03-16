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
    const string db_path = "../data/google.sqlite";

    const int merge_num = 10; //行、列方向各自合并多少图片

    try
    {
        SQLite::Database db(db_path);

        // 查询出最大与最小的行列号
        int min_row_id = 0, max_row_id = 0, min_col_id = 0, max_col_id = 0;
        string query_sql = "SELECT * FROM cache limit 1";
        SQLite::Statement query_stat(db, query_sql);
        while (query_stat.executeStep())
        {
            int level = query_stat.getColumn(0);
            const string img_type = query_stat.getColumn(3);
            string img_blob = query_stat.getColumn(4);

            //将blob转为vector，然后转为cv2的mat类型
            std::vector<BYTE> vectordata(img_blob.begin(), img_blob.end());
            cv::Mat data_mat(vectordata, true);
            cv::Mat image(cv::imdecode(data_mat, 1)); //put 0 if you want greyscale

            
            for (int i =0; i<5; ++i)
            {
                auto dst = cv::Mat(cv::Size(1024, 1024), CV_8UC3);
                image.copyTo(dst(cv::Rect(256*(i+1), 256*(i+1), image.cols, image.rows)));
                
                cv::imwrite( to_string(i) + "_aa.jpg", dst);
                dst = Mat::zeros(1024, 1024, CV_8UC3);
                // dst.release();
            }
        }
    }
    catch (exception &e)
    {
        std::cout << "exception: " << e.what() << std::endl;
    }
    return 0;
}
