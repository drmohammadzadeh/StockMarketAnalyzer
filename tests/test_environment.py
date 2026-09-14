"""Environment sanity tests."""

def test_environment_import():
    import stock_analyzer
    assert stock_analyzer.__version__ == "1.0.0"
