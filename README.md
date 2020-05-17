## Topside: Technical Operations Procedures Simulator & Integrated Development Environment

Waterloo Rocketry's operations simulator is a tool for modelling and simulating rocket launch systems and procedures.

#### Requirements

If you just want to use or develop the Topside core libraries, Python 3.7 or newer is required. If you want to build a standalone application, currently _only_ Python 3.7 releases are supported, as PyInstaller requires <=3.7 and dataclasses require >=3.7.

Required Python packages can be installed using `pip install -r requirements.txt`.

#### Building a standalone application

The `tools/` directory contains two scripts for building a standalone application: `build_cxfreeze.sh` and `build_pyinstaller.sh`. However, currently only the PyInstaller build is functional due to upstream bugs in the interaction between SciPy, cx_Freeze, and Cython.

Building a standalone application should be as simple as running `build_pyinstaller.sh`. The resulting application can be found at `dist/Topside/Topside.exe`.
