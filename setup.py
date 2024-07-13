from setuptools import setup, find_packages, Extension
from setuptools.command.build_ext import build_ext
import sys
import os

class GetPybindInclude(object):
    def __init__(self, user=False):
        self.user = user

    def __str__(self):
        import pybind11
        return pybind11.get_include(self.user)

ext_modules = [
    Extension(
        'emulators.emulator_module',
        ['cpp/bindings/emulator_bindings.cpp', 'cpp/src/chip8_emulator.cpp'],
        include_dirs=[
            'cpp/include',
            GetPybindInclude(),
            GetPybindInclude(user=True)
        ],
        language='c++'
    ),
]

setup(
    name='Emulation-Simulation',
    version='0.1.0',
    author='Priyanshu Pansari',
    author_email='Priyanshu.Pansari@gmail.com',
    description='A retro game emulator framework with Python bindings for AI research',
    long_description='',
    ext_modules=ext_modules,
    install_requires=['pybind11>=2.4', 'numpy','pygame'],
    setup_requires=['pybind11>=2.4'],
    cmdclass={'build_ext': build_ext},
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    zip_safe=False,
    python_requires=">=3.6",
)