import operations_simulator as ops


def test_plumbing_engine_exists():
    plumb = ops.PlumbingEngine()
    assert plumb is not None
