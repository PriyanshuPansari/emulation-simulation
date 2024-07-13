# File: CMakeLists.txt

cmake_minimum_required(VERSION 3.12)
project(chip8_emulator VERSION 1.0.0 LANGUAGES CXX)
# In your main CMakeLists.txt, add this line:
set(CMAKE_CTEST_ARGUMENTS "--output-on-failure")
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
project(emulation_simulation)
# Find Python
find_package(Python COMPONENTS Interpreter Development)
# find_package(Catch2 2 REQUIRED)
# Add pybind11
find_package(pybind11 REQUIRED)

# Include directories
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/cpp/include)

# Add library for CHIP-8 emulator
add_library(chip8_core OBJECT
    cpp/src/chip8_emulator.cpp
)
set_property(TARGET chip8_core PROPERTY POSITION_INDEPENDENT_CODE ON)

# Add Python module
pybind11_add_module(emulator_module
    cpp/bindings/emulator_bindings.cpp
    $<TARGET_OBJECTS:chip8_core>
)

# No need to link chip8_core separately now
# target_link_libraries(emulator_module PRIVATE chip8_core)

# Link the Python module with the CHIP-8 core library
target_link_libraries(emulator_module PRIVATE chip8_core)

# Set output directory for the Python module
set_target_properties(emulator_module PROPERTIES
    LIBRARY_OUTPUT_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/src/emulators
)

# Add tests (optional, but recommended)
enable_testing()
add_subdirectory(tests)