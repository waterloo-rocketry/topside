from ..application import Application


def test_application_init():
    # TODO(jacob): Investigate if there's any way to spoof GUI events
    # for controls defined in QML and test GUI interactions.
    app = Application([])
    app.shutdown()
