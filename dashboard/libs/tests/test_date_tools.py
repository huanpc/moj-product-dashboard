from datetime import date, datetime

from dateutil.rrule import MONTHLY, YEARLY
import pytest

from dashboard.libs.date_tools import (
    get_workdays, get_workdays_list, get_bank_holidays, get_overlap,
    parse_date, to_datetime, slice_time_window, dates_between)


@pytest.mark.parametrize("start_date, end_date, expected", [
    ('2016-04-28', '2016-04-28', 1),  # same working day
    ('2016-04-30', '2016-04-30', 0),  # same weekend day
    ('2016-04-27', '2016-04-29', 3),  # just work days
    ('2016-04-27', '2016-04-30', 3),  # one weekend day
    ('2016-04-27', '2016-05-01', 3),  # two weekend days
    ('2016-04-27', '2016-05-02', 3),  # two weekend days plus a bank holiday
    ('2016-01-01', '2016-01-31', 20),  # Jan 2016
    ('2016-02-01', '2016-02-28', 20),  # Feb 2016
])
def test_get_workdays(start_date, end_date, expected):
    workdays = get_workdays(parse_date(start_date), parse_date(end_date))
    assert workdays == expected


@pytest.mark.parametrize("start_date, end_date, expected", [
    ('2016-04-28', '2016-04-28', ['2016-04-28']),  # same working day
    ('2016-04-30', '2016-04-30', []),  # same weekend day
    ('2016-04-27', '2016-04-29',
     ['2016-04-27', '2016-04-28', '2016-04-29']),  # just work days
    ('2016-04-27', '2016-04-30',
     ['2016-04-27', '2016-04-28', '2016-04-29']),  # one weekend day
    ('2016-04-27', '2016-05-01',
     ['2016-04-27', '2016-04-28', '2016-04-29']),  # two weekend days
    ('2016-04-27', '2016-05-02',
     ['2016-04-27', '2016-04-28', '2016-04-29']),  # plus a bank holiday
])
def test_get_workdays_list(start_date, end_date, expected):
    workdays = get_workdays_list(parse_date(start_date), parse_date(end_date))
    assert workdays == [parse_date(day) for day in expected]


@pytest.mark.parametrize("day", [
    '2015-12-28',  # boxing day (substitue day)
    '2016-05-02',  # may day
    '2016-05-30',  # spring bank holiday
    '2016-08-29',  # summer bank holiday (England)
    '2016-12-27',  # christmas day (substitue day)
])
def test_get_bank_holidays_good_days(day):
    assert parse_date(day) in get_bank_holidays(), \
        '{} is a bank holiday!'.format(day)


@pytest.mark.parametrize("day", [
    '2016-04-01',  # april fools day
    '2016-08-01',  # summer bank holiday (Scotland)
])
def test_get_bank_holidays_bad_days(day):
    assert parse_date(day) not in get_bank_holidays()


@pytest.mark.parametrize(
    "start_date0, end_date0, start_date1, end_date1, expected", [
        # no overlap
        ('2016-01-01', '2016-01-31', '2015-12-01', '2015-12-31', None),
        ('2015-12-01', '2015-12-31', '2016-01-01', '2016-01-31', None),
        # one time window is part of the other
        ('2015-12-01', '2016-01-31', '2015-12-31', '2016-01-01',
         ('2015-12-31', '2016-01-01')),
        # intersection is part of both time windows
        ('2015-12-01', '2016-01-01', '2015-12-31', '2016-01-31',
         ('2015-12-31', '2016-01-01')),
    ])
def test_get_overlap(start_date0, end_date0, start_date1, end_date1, expected):
    overlap = get_overlap((parse_date(start_date0), parse_date(end_date0)),
                          (parse_date(start_date1), parse_date(end_date1)))
    if expected:
        expected = parse_date(expected[0]), parse_date(expected[1])
    assert expected == overlap


@pytest.mark.parametrize(
    "start_date0, end_date0, start_date1, end_date1", [
        # time window0 start date > end date
        ('2016-01-31', '2016-01-01', '2015-12-01', '2015-12-31'),
        # time window1 start date > end date
        ('2015-12-01', '2015-12-31', '2016-01-31', '2016-01-01'),
    ])
def test_get_overlap_value_error(start_date0, end_date0,
                                 start_date1, end_date1):
    with pytest.raises(ValueError):
        get_overlap((parse_date(start_date0), parse_date(end_date0)),
                    (parse_date(start_date1), parse_date(end_date1)))


# TODO more tests!
def test_slice_time_window():
    start_date = date(2015, 1, 2)
    end_date = date(2015, 12, 31)
    sliced = slice_time_window(start_date, end_date, 'MS')
    assert sliced[0] == (date(2015, 1, 2), date(2015, 1, 31))
    assert sliced[-1] == (date(2015, 12, 1), date(2015, 12, 31))


def test_to_datetime():
    assert to_datetime(date(2015, 12, 1)) == datetime(2015, 12, 1, 0, 0, 0)


@pytest.mark.parametrize("start_date, end_date, frequency, bymonthday, expected", [
    (date(2015, 1, 2), date(2015, 3, 3), MONTHLY, 2,
     [date(2015, 1, 2), date(2015, 2, 2), date(2015, 3, 2)]),

    (date(2015, 1, 31), date(2015, 3, 31), MONTHLY, 31,
     [date(2015, 1, 31), date(2015, 2, 28), date(2015, 3, 31)]),

    (date(2015, 1, 29), date(2015, 3, 31), MONTHLY, 29,
     [date(2015, 1, 29), date(2015, 2, 28), date(2015, 3, 29)]),

    (date(2015, 1, 2), date(2017, 3, 3), YEARLY, None,
     [date(2015, 1, 2), date(2016, 1, 2), date(2017, 1, 2)]),

    (date(2015, 1, 30), date(2017, 3, 3), YEARLY, None,
     [date(2015, 1, 30), date(2016, 1, 30), date(2017, 1, 30)]),
])
def test_slice_on_date(start_date, end_date, frequency, bymonthday, expected):
    dates = dates_between(start_date, end_date, frequency,
                          bymonthday=bymonthday)
    assert dates == expected
