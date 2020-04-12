import sys

from application.qt_bridge import Application, Bridge


if __name__ == '__main__':
    bridge = Bridge()
    app = Application(bridge, sys.argv)

    if not app.ready():
        sys.exit(-1)

    sys.exit(app.run())
