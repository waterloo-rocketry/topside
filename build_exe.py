import platform
from os import path

from cx_Freeze import setup, Executable

from topside import release_info

here = path.abspath(path.dirname(__file__))

base = None
icon = 'application/resources/icon.png'

if platform.system() == 'Windows':
    base = 'Win32GUI'
    icon = 'application/resources/icon.ico'

target = Executable(
    script='main.py',
    targetName='Topside',
    base=base,
    icon=icon
)

build_exe_opts = {
    'include_files': ['application/resources']
}

setup(
    name=release_info.name,
    version=release_info.version,
    description=release_info.description,
    executables=[target],
    options={
        'build_exe': build_exe_opts
    }
)
