import sys

from application.application import Application


if __name__ == '__main__':
    app = Application(sys.argv)

    if not app.ready():
        sys.exit(1)

    sys.exit(app.run())
