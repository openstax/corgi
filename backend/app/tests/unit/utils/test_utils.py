from tests.utils import validate_datetime


def test_validate_datetime_string_is_correct():
    # GIVEN: A correct datetime string
    date_str = "20220411.192702"
    
    # WHEN: The string is validated
    is_date = validate_datetime(date_str)

    # THEN: The string can be converted to python datetime obj
    assert is_date


def test_validate_datetime_string_is_incorrect():
    # GIVEN: A correct datetime string
    date_str = "a"
    
    # WHEN: The string is validated
    is_date = validate_datetime(date_str)

    # THEN: The string can be converted to python datetime obj
    assert not is_date
