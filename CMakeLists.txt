cmake_minimum_required(VERSION 3.5)
set(PROJECT_NAME "ignition_assets")
project(${PROJECT_NAME} VERSION 0.1.0)

# Default to C++17
if(NOT CMAKE_CXX_STANDARD)
  set(CMAKE_CXX_STANDARD 17)
endif()

# find dependencies
set(PROJECT_DEPENDENCIES
  ament_cmake
  ros_ign_gazebo
  ros_ign_bridge
)

foreach(DEPENDENCY ${PROJECT_DEPENDENCIES})
  find_package(${DEPENDENCY} REQUIRED)
endforeach()

#============================================================================
# Hooks
ament_environment_hooks("hooks/resource_paths.dsv.in")
ament_environment_hooks("hooks/resource_paths.sh")

#============================================================================


#============================================================================
# Resources
install(DIRECTORY
  worlds
  models
  DESTINATION share/${PROJECT_NAME}
)

#============================================================================

ament_package()
