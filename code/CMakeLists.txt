cmake_minimum_required(VERSION 3.23.2)
project(AddPDFs)

if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE Release)
endif()

set(CMAKE_CXX_FLAGS "-Wall -Wextra -Werror")
set(CMAKE_CXX_FLAGS_DEBUG "-g")
set(CMAKE_CXX_FLAGS_RELEASE "-O3")

add_executable(addPdfs.exe add_pdfs.cpp)

set_target_properties(addPdfs.exe PROPERTIES
    CXX_STANDARD 17
    CXX_STANDARD_REQUIRED TRUE
)