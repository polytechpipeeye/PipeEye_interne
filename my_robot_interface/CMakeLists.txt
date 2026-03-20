cmake_minimum_required(VERSION 3.8)
project(my_robot_interface)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)

# Cette partie génère le code Python/C++ à partir de ton fichier .msg
rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/LedControl.msg"
)

ament_package()
