// File: cpp/src/chip8_emulator.cpp

#include "chip8_emulator.hpp"
#include <fstream>
#include <stdexcept>
#include <cstring>
#include <random>
#include <chrono>


CHIP8Emulator::CHIP8Emulator() {
    initialize();
}

void CHIP8Emulator::initialize() {
    std::fill(memory.begin(), memory.end(), 0);
    std::fill(V.begin(), V.end(), 0);
    I = 0;
    PC = 0x200;  // Programs typically start at 0x200
    std::fill(stack.begin(), stack.end(), 0);
    SP = 0;
    delay_timer = 0;
    sound_timer = 0;
    std::fill(display.begin(), display.end(), false);
    std::fill(keypad.begin(), keypad.end(), false);

    // Load fontset
    static const uint8_t fontset[80] = {
        0xF0, 0x90, 0x90, 0x90, 0xF0, // 0
        0x20, 0x60, 0x20, 0x20, 0x70, // 1
        0xF0, 0x10, 0xF0, 0x80, 0xF0, // 2
        0xF0, 0x10, 0xF0, 0x10, 0xF0, // 3
        0x90, 0x90, 0xF0, 0x10, 0x10, // 4
        0xF0, 0x80, 0xF0, 0x10, 0xF0, // 5
        0xF0, 0x80, 0xF0, 0x90, 0xF0, // 6
        0xF0, 0x10, 0x20, 0x40, 0x40, // 7
        0xF0, 0x90, 0xF0, 0x90, 0xF0, // 8
        0xF0, 0x90, 0xF0, 0x10, 0xF0, // 9
        0xF0, 0x90, 0xF0, 0x90, 0x90, // A
        0xE0, 0x90, 0xE0, 0x90, 0xE0, // B
        0xF0, 0x80, 0x80, 0x80, 0xF0, // C
        0xE0, 0x90, 0x90, 0x90, 0xE0, // D
        0xF0, 0x80, 0xF0, 0x80, 0xF0, // E
        0xF0, 0x80, 0xF0, 0x80, 0x80  // F
    };
    std::copy(std::begin(fontset), std::end(fontset), memory.begin());
}

bool CHIP8Emulator::load_rom(const std::string& rom_path) {
    std::ifstream file(rom_path, std::ios::binary | std::ios::ate);
    if (!file.is_open()) {
        return false;
    }

    std::streamsize size = file.tellg();
    file.seekg(0, std::ios::beg);

    if (size > MEMORY_SIZE - 0x200) {
        return false;
    }

    file.read(reinterpret_cast<char*>(memory.data() + 0x200), size);
    return true;
}

void CHIP8Emulator::step() {
    execute_instruction();
    if (delay_timer > 0) {
        --delay_timer;
    }
    if (sound_timer > 0) {
        --sound_timer;
    }
}

void CHIP8Emulator::get_frame(uint8_t* buffer, size_t buffer_size) const {
    if (buffer_size != SCREEN_WIDTH * SCREEN_HEIGHT) {
        throw std::invalid_argument("Invalid buffer size");
    }
    for (size_t i = 0; i < buffer_size; ++i) {
        buffer[i] = display[i] ? 255 : 0;
    }
}

void CHIP8Emulator::set_input(const std::vector<bool>& input_state) {
    if (input_state.size() != 16) {
        throw std::invalid_argument("Invalid input state size");
    }
    std::copy(input_state.begin(), input_state.end(), keypad.begin());
}

std::vector<uint8_t> CHIP8Emulator::get_state() const {
    std::vector<uint8_t> state;
    state.reserve(STATE_SIZE);
    
    state.insert(state.end(), memory.begin(), memory.end());
    state.insert(state.end(), V.begin(), V.end());
    state.push_back(I >> 8);
    state.push_back(I & 0xFF);
    state.push_back(PC >> 8);
    state.push_back(PC & 0xFF);
    for (auto s : stack) {
        state.push_back(s >> 8);
        state.push_back(s & 0xFF);
    }
    state.push_back(SP);
    state.push_back(delay_timer);
    state.push_back(sound_timer);
    
    for (size_t i = 0; i < display.size(); i += 8) {
        uint8_t byte = 0;
        for (size_t j = 0; j < 8 && i + j < display.size(); ++j) {
            byte |= (display[i + j] ? 1 : 0) << j;
        }
        state.push_back(byte);
    }
    
    uint16_t keypad_state = 0;
    for (size_t i = 0; i < 16; ++i) {
        keypad_state |= (keypad[i] ? 1 : 0) << i;
    }
    state.push_back(keypad_state >> 8);
    state.push_back(keypad_state & 0xFF);
    
    return state;
}

void CHIP8Emulator::set_state(const std::vector<uint8_t>& state) {
size_t expected_size = MEMORY_SIZE + REGISTER_COUNT + 2 + 2 + STACK_SIZE * 2 + 1 + 1 + 1 + SCREEN_WIDTH * SCREEN_HEIGHT / 8 + 2;
    if (state.size() != expected_size) {
        throw std::invalid_argument("Invalid state size");
    }

    size_t offset = 0;

    // Restore memory
    std::copy(state.begin() + offset, state.begin() + offset + MEMORY_SIZE, memory.begin());
    offset += MEMORY_SIZE;

    // Restore registers
    std::copy(state.begin() + offset, state.begin() + offset + REGISTER_COUNT, V.begin());
    offset += REGISTER_COUNT;

    // Restore I
    I = (state[offset] << 8) | state[offset + 1];
    offset += 2;

    // Restore PC
    PC = (state[offset] << 8) | state[offset + 1];
    offset += 2;

    // Restore stack
    for (size_t i = 0; i < STACK_SIZE; ++i) {
        stack[i] = (state[offset] << 8) | state[offset + 1];
        offset += 2;
    }

    // Restore SP
    SP = state[offset++];

    // Restore timers
    delay_timer = state[offset++];
    sound_timer = state[offset++];

    // Restore display
    for (size_t i = 0; i < SCREEN_WIDTH * SCREEN_HEIGHT; i += 8) {
        uint8_t byte = state[offset++];
        for (size_t j = 0; j < 8 && i + j < display.size(); ++j) {
            display[i + j] = (byte & (1 << j)) != 0;
        }
    }

    // Restore keypad
    uint16_t keypad_state = (state[offset] << 8) | state[offset + 1];
    for (size_t i = 0; i < 16; ++i) {
        keypad[i] = (keypad_state & (1 << i)) != 0;
    }
}
   

void CHIP8Emulator::execute_instruction() {
    // Fetch
    uint16_t opcode = (memory[PC] << 8) | memory[PC + 1];
    PC += 2;

    // Decode and Execute
    switch (opcode & 0xF000) {
        case 0x0000:
            switch (opcode & 0x00FF) {
                case 0x00E0: // CLS
                    std::fill(display.begin(), display.end(), false);
                    break;
                case 0x00EE: // RET
                    PC = stack[--SP];
                    break;
            }
            break;

        case 0x1000: // JP addr
            PC = opcode & 0x0FFF;
            break;

        case 0x2000: // CALL addr
            stack[SP++] = PC;
            PC = opcode & 0x0FFF;
            break;

        case 0x3000: // SE Vx, byte
            if (V[(opcode & 0x0F00) >> 8] == (opcode & 0x00FF))
                PC += 2;
            break;

        case 0x4000: // SNE Vx, byte
            if (V[(opcode & 0x0F00) >> 8] != (opcode & 0x00FF))
                PC += 2;
            break;

        case 0x5000: // SE Vx, Vy
            if (V[(opcode & 0x0F00) >> 8] == V[(opcode & 0x00F0) >> 4])
                PC += 2;
            break;

        case 0x6000: // LD Vx, byte
            V[(opcode & 0x0F00) >> 8] = opcode & 0x00FF;
            break;

        case 0x7000: // ADD Vx, byte
            V[(opcode & 0x0F00) >> 8] += opcode & 0x00FF;
            break;

        case 0x8000:
            switch (opcode & 0x000F) {
                case 0x0000: // LD Vx, Vy
                    V[(opcode & 0x0F00) >> 8] = V[(opcode & 0x00F0) >> 4];
                    break;
                case 0x0001: // OR Vx, Vy
                    V[(opcode & 0x0F00) >> 8] |= V[(opcode & 0x00F0) >> 4];
                    break;
                case 0x0002: // AND Vx, Vy
                    V[(opcode & 0x0F00) >> 8] &= V[(opcode & 0x00F0) >> 4];
                    break;
                case 0x0003: // XOR Vx, Vy
                    V[(opcode & 0x0F00) >> 8] ^= V[(opcode & 0x00F0) >> 4];
                    break;
                case 0x0004: // ADD Vx, Vy
                    {
                        uint16_t sum = V[(opcode & 0x0F00) >> 8] + V[(opcode & 0x00F0) >> 4];
                        V[0xF] = (sum > 255) ? 1 : 0;
                        V[(opcode & 0x0F00) >> 8] = sum & 0xFF;
                    }
                    break;
                case 0x0005: // SUB Vx, Vy
                    V[0xF] = (V[(opcode & 0x0F00) >> 8] > V[(opcode & 0x00F0) >> 4]) ? 1 : 0;
                    V[(opcode & 0x0F00) >> 8] -= V[(opcode & 0x00F0) >> 4];
                    break;
                case 0x0006: // SHR Vx {, Vy}
                    V[0xF] = V[(opcode & 0x0F00) >> 8] & 0x1;
                    V[(opcode & 0x0F00) >> 8] >>= 1;
                    break;
                case 0x0007: // SUBN Vx, Vy
                    V[0xF] = (V[(opcode & 0x00F0) >> 4] > V[(opcode & 0x0F00) >> 8]) ? 1 : 0;
                    V[(opcode & 0x0F00) >> 8] = V[(opcode & 0x00F0) >> 4] - V[(opcode & 0x0F00) >> 8];
                    break;
                case 0x000E: // SHL Vx {, Vy}
                    V[0xF] = (V[(opcode & 0x0F00) >> 8] & 0x80) >> 7;
                    V[(opcode & 0x0F00) >> 8] <<= 1;
                    break;
            }
            break;

        case 0x9000: // SNE Vx, Vy
            if (V[(opcode & 0x0F00) >> 8] != V[(opcode & 0x00F0) >> 4])
                PC += 2;
            break;

        case 0xA000: // LD I, addr
            I = opcode & 0x0FFF;
            break;

        case 0xB000: // JP V0, addr
            PC = (opcode & 0x0FFF) + V[0];
            break;

        case 0xC000: // RND Vx, byte
            {
                static std::mt19937 rng(std::chrono::steady_clock::now().time_since_epoch().count());
                static std::uniform_int_distribution<uint8_t> dist(0, 255);
                V[(opcode & 0x0F00) >> 8] = dist(rng) & (opcode & 0x00FF);
            }
            break;

        case 0xD000: // DRW Vx, Vy, nibble
            {
                uint8_t x = V[(opcode & 0x0F00) >> 8];
                uint8_t y = V[(opcode & 0x00F0) >> 4];
                uint8_t height = opcode & 0x000F;
                V[0xF] = 0;

                for (int row = 0; row < height; row++) {
                    uint8_t sprite_byte = memory[I + row];
                    for (int col = 0; col < 8; col++) {
                        if ((sprite_byte & (0x80 >> col)) != 0) {
                            int index = (y + row) * SCREEN_WIDTH + (x + col);
                            if (index < SCREEN_WIDTH * SCREEN_HEIGHT) {
                                if (display[index]) {
                                    V[0xF] = 1;
                                }
                                display[index] ^= true;
                            }
                        }
                    }
                }
            }
            break;

        case 0xE000:
            switch (opcode & 0x00FF) {
                case 0x009E: // SKP Vx
                    if (keypad[V[(opcode & 0x0F00) >> 8]])
                        PC += 2;
                    break;
                case 0x00A1: // SKNP Vx
                    if (!keypad[V[(opcode & 0x0F00) >> 8]])
                        PC += 2;
                    break;
            }
            break;

        case 0xF000:
            switch (opcode & 0x00FF) {
                case 0x0007: // LD Vx, DT
                    V[(opcode & 0x0F00) >> 8] = delay_timer;
                    break;
                case 0x000A: // LD Vx, K
                    {
                        bool key_pressed = false;
                        for (int i = 0; i < 16; i++) {
                            if (keypad[i]) {
                                V[(opcode & 0x0F00) >> 8] = i;
                                key_pressed = true;
                                break;
                            }
                        }
                        if (!key_pressed)
                            PC -= 2; // Repeat this instruction
                    }
                    break;
                case 0x0015: // LD DT, Vx
                    delay_timer = V[(opcode & 0x0F00) >> 8];
                    break;
                case 0x0018: // LD ST, Vx
                    sound_timer = V[(opcode & 0x0F00) >> 8];
                    break;
                case 0x001E: // ADD I, Vx
                    I += V[(opcode & 0x0F00) >> 8];
                    break;
                case 0x0029: // LD F, Vx
                    I = V[(opcode & 0x0F00) >> 8] * 5; // Each character is 5 bytes long
                    break;
                case 0x0033: // LD B, Vx
                    memory[I] = V[(opcode & 0x0F00) >> 8] / 100;
                    memory[I + 1] = (V[(opcode & 0x0F00) >> 8] / 10) % 10;
                    memory[I + 2] = V[(opcode & 0x0F00) >> 8] % 10;
                    break;
                case 0x0055: // LD [I], Vx
                    for (int i = 0; i <= ((opcode & 0x0F00) >> 8); i++)
                        memory[I + i] = V[i];
                    break;
                case 0x0065: // LD Vx, [I]
                    for (int i = 0; i <= ((opcode & 0x0F00) >> 8); i++)
                        V[i] = memory[I + i];
                    break;
            }
            break;

        default:
            throw std::runtime_error("Unknown opcode: " + std::to_string(opcode));
    }
}