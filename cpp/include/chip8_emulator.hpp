// File: cpp/include/chip8_emulator.hpp

#pragma once
#include "base_emulator.hpp"
#include <array>

class CHIP8Emulator : public BaseEmulator {
public:
    CHIP8Emulator();
    ~CHIP8Emulator() override = default;

    bool load_rom(const std::string& rom_path) override;
    void step() override;
    void get_frame(uint8_t* buffer, size_t buffer_size) const override;
    void set_input(const std::vector<bool>& input_state) override;
    std::vector<uint8_t> get_state() const override;
    void set_state(const std::vector<uint8_t>& state) override;
    static constexpr size_t getMemorySize() { return MEMORY_SIZE; }
    static constexpr size_t getRegisterCount() { return REGISTER_COUNT; }
    static constexpr size_t MEMORY_SIZE = 4096;
    static constexpr size_t REGISTER_COUNT = 16;
    static constexpr size_t STACK_SIZE = 16;
    static constexpr size_t SCREEN_WIDTH = 64;
    static constexpr size_t SCREEN_HEIGHT = 32;   
private:
    std::array<uint8_t, MEMORY_SIZE> memory;
    std::array<uint8_t, REGISTER_COUNT> V;
    uint16_t I;
    uint16_t PC;
    std::array<uint16_t, STACK_SIZE> stack;
    uint8_t SP;
    uint8_t delay_timer;
    uint8_t sound_timer;
    std::array<bool, SCREEN_WIDTH * SCREEN_HEIGHT> display;
    std::array<bool, 16> keypad;

    void initialize();
    void execute_instruction();

public:
    static constexpr size_t STATE_SIZE = MEMORY_SIZE + REGISTER_COUNT + 2 + 2 + STACK_SIZE * 2 + 1 + 1 + 1 + SCREEN_WIDTH * SCREEN_HEIGHT / 8 + 2;
};