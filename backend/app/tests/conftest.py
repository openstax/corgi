# Import fixtures
pytest_plugins = "tests.ui.fixtures.ui"


def get_custom_markers():
    """Function used to register custom markers.

    Define custom markers within this function to register them in pytest
    """
    return (
        "integration: mark tests that are integration tests",
        "smoke: mark tests used for smoke testing",
        "testrail: mark tests used for testrail runs",
        "ui: mark tests used for ui tests",
        "unit: mark tests as a unit test"
    )


def pytest_configure(config):
    for marker in get_custom_markers():
        config.addinivalue_line("markers", marker)
