#define CATCH_CONFIG_MAIN
#include "catch.hpp"
#include "chip8_emulator.hpp"

TEST_CASE("CHIP8Emulator initialization", "[chip8]") {
    CHIP8Emulator emulator;

    SECTION("Memory is zeroed after initialization") {
    std::vector<uint8_t> state = emulator.get_state();
    REQUIRE(state.size() >= CHIP8Emulator::getMemorySize());
    
    // Check that the first 512 bytes (0x200) are zero
    for (int i = 0; i < 0x200; ++i) {
        INFO("Memory at index " << i << " is not zero");
        REQUIRE(state[i] == 0);
    }
}

    SECTION("Program counter is set to 0x200 after initialization") {
        std::vector<uint8_t> state = emulator.get_state();
        uint16_t pc = (state[CHIP8Emulator::getMemorySize() + CHIP8Emulator::getRegisterCount()] << 8) |
                      state[CHIP8Emulator::getMemorySize() + CHIP8Emulator::getRegisterCount() + 1];
        INFO("Program counter is " << pc << ", expected 0x200");
        REQUIRE(pc == 0x200);
    }
}

// ... rest of the test cases ...

TEST_CASE("CHIP8Emulator instruction execution", "[chip8]") {
    CHIP8Emulator emulator;

    SECTION("0x00E0 - CLS instruction clears the display") {
        // Set some pixels in the display
        std::vector<uint8_t> state = emulator.get_state();
        for (size_t i = CHIP8Emulator::getMemorySize() + CHIP8Emulator::getRegisterCount() + 7; i < state.size() - 2; ++i){ 
            state[i] = 0xFF;
        }
        emulator.set_state(state);

        // Manually set the CLS instruction in memory
        state[0x200] = 0x00;
        state[0x201] = 0xE0;
        emulator.set_state(state);


        // Check if display is cleared
        state = emulator.get_state();
        for (size_t i = CHIP8Emulator::getMemorySize() + CHIP8Emulator::getRegisterCount() + 7; i < state.size() - 2; ++i) { 
            INFO("Display pixel at index " << i << " is not cleared");
            REQUIRE(state[i] == 0);
        }
    }
}