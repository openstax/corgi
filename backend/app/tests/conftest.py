import re

import pytest

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
        "unit: mark tests as a unit test",
        "nondestructive: tests using this decorator will run in sensitive environments",
        "sensitive: the url for environments where destructive tests should not be executed"
    )


def pytest_addoption(parser):
    group = parser.getgroup("safety", "safety")
    group.addoption(
        "--destructive",
        action="store_true",
        dest="run_destructive",
        default=False,
        help="include destructive tests (tests not explicitly marked as \'nondestructive\'). (disabled by default).",
    )
    group._addoption('--sensitiveurl',
                    action='store',
                    dest='sensitive_url',
                    default='corgi\.ce\.openstax\.org',
                    metavar='str',
                    help='regular expression for identifying sensitive urls.')


def pytest_configure(config):
    for marker in get_custom_markers():
        config.addinivalue_line("markers", marker)

    if not config.option.run_destructive:
        if config.option.markexpr:
            config.option.markexpr = f"nondestructive and {config.option.markexpr}"
        else:
            config.option.markexpr = "nondestructive"


def pytest_runtest_setup(item):
    sensitive = re.search(item.config.option.sensitive_url, item.config.option.base_url)
    destructive = 'nondestructive' not in item.keywords

    if (sensitive and destructive):
        # Skip the test with an appropriate message
        pytest.skip("This test is destructive and the target URL is" \
                    "considered a sensitive environment. If this test" \
                    "is not destructive add the 'nondestructive' marker.")
