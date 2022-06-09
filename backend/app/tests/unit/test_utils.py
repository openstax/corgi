import pytest

from tests.utils import validate_datetime

@pytest.mark.unit
@pytest.mark.nondestructive
@pytest.mark.parametrize("date_str", [("20220411.192702")])
def test_validate_datetime_string_is_correct(date_str):
    # GIVEN: A correct datetime string
    
    # WHEN: The string is validated
    is_date = validate_datetime(date_str)

    # THEN: The string can be converted to python datetime obj
    assert is_date


@pytest.mark.unit
@pytest.mark.nondestructive
@pytest.mark.parametrize("date_str", [("a")])
def test_validate_datetime_string_is_incorrect(date_str):
    # GIVEN: An incorrect datetime string
    
    # WHEN: The string is validated
    is_date = validate_datetime(date_str)

    # THEN: The string can be converted to python datetime obj
    assert not is_date
