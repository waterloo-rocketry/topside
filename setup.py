import platform
from os import path

from setuptools import setup, find_packages
from cx_Freeze import setup, Executable

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# cx_Freeze configuration

base = None
icon = 'application/resources/icon.png'

if platform.system() == 'Windows':
    base = 'Win32GUI'
    icon = 'application/resources/icon.ico'

target = Executable(
    script='main.py',
    targetName='OperationsSimulator',
    base=base,
    icon=icon
)

build_exe_opts = {
    'include_files': ['application/resources']
}

setup(
    name='operations_simulator',
    version='0.1.0',
    description='A simulator for rocket launch operations',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/waterloo-rocketry/operations-simulator',
    author='Waterloo Rocketry',
    license='MIT',
    classifiers=[
        'License :: OSI Approved :: MIT License',
    ],
    packages=find_packages(exclude=['application']),
    executables=[target],
    options={
        'build_exe': build_exe_opts
    }
)
