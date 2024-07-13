message(STATUS "Configuring tests...")

# Add the test executable
add_executable(test_chip8_emulator test_chip8_emulator.cpp)

# Include directories
target_include_directories(test_chip8_emulator PRIVATE 
    ${CMAKE_CURRENT_SOURCE_DIR}/include # For catch.hpp
    ${CMAKE_SOURCE_DIR}/cpp/include  # For chip8_emulator.hpp
)

# Link libraries
target_link_libraries(test_chip8_emulator PRIVATE chip8_core)

# Add the test
add_test(NAME test_chip8_emulator COMMAND test_chip8_emulator)
set_tests_properties(test_chip8_emulator PROPERTIES ENVIRONMENT "CTEST_OUTPUT_ON_FAILURE=1")