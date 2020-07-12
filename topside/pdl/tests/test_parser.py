import topside as top

def test_valid_file():
    file = top.File('topside/pdl/example.yaml')

    parsed = top.Parser([file])

    assert len(parsed.components) == 6
    for component in parsed.components:
        assert component.is_valid()
