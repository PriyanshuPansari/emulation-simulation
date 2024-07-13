// File: cpp/bindings/emulator_bindings.cpp

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/numpy.h>
#include "chip8_emulator.hpp"

namespace py = pybind11;

PYBIND11_MODULE(emulator_module, m) {
    py::class_<CHIP8Emulator>(m, "CHIP8Emulator")
        .def(py::init<>())
        .def("load_rom", &CHIP8Emulator::load_rom)
        .def("step", &CHIP8Emulator::step)
        .def("get_frame", [](const CHIP8Emulator& self) {
            std::vector<uint8_t> frame(64 * 32);
            self.get_frame(frame.data(), frame.size());
            return py::array_t<uint8_t>({32, 64}, frame.data());
        })
        .def("set_input", &CHIP8Emulator::set_input)
        .def("get_state", &CHIP8Emulator::get_state)
        .def("set_state", &CHIP8Emulator::set_state);
}