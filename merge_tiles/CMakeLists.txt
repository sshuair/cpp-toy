cmake_minimum_required(VERSION 3.5)

project(merge_tile)

# 
find_package(OpenCV)
include_directories( ${OpenCV_INCLUDE_DIRS} )



add_subdirectory(
    ${CMAKE_CURRENT_LIST_DIR}/thirdparty/SQLiteCpp
)

add_executable(main src/main.cpp)

target_link_libraries(main
    SQLiteCpp
    sqlite3
    pthread
    dl
    ${OpenCV_LIBS}
)