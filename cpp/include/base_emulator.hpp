// File: cpp/include/base_emulator.hpp

#pragma once
#include <string>
#include <vector>
#include <cstdint>

class BaseEmulator {
public:
    virtual ~BaseEmulator() = default;

    virtual bool load_rom(const std::string& rom_path) = 0;
    virtual void step() = 0;
    virtual void get_frame(uint8_t* buffer, size_t buffer_size) const = 0;
    virtual void set_input(const std::vector<bool>& input_state) = 0;
    virtual std::vector<uint8_t> get_state() const = 0;
    virtual void set_state(const std::vector<uint8_t>& state) = 0;
};