#!/usr/bin/env python3
"""Oracle ILOM util functions"""
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>

# License: GNU General Public License v2

from typing import Any, Dict, NamedTuple, Optional, Tuple
from datetime import datetime, timedelta, timezone


Levels = Optional[Tuple[float, float]]


class Perfdata(NamedTuple):
    """normal monitoring performance data"""
    value: float
    levels_upper: Levels
    levels_lower: Levels


def _try_convert_to_float(value: str) -> Optional[float]:
    if value is None:
        return None
    try:
        value = float(value)
        if value == 0.0:
            return None
        return value
    except ValueError:
        return None


def process_oracle_ilom_perfdata(entry: Dict[str, Any]):
    """Oracle ILOM performance data to monitoring performance data"""
    reading = None
    precision = pow(10, int(entry.sensor_exponent))
    reading = int(entry.sensor_value_str) * precision
    if reading is None:
        return None

    min_warn = _try_convert_to_float(entry.sensor_lower_warn_value)
    if min_warn:
        min_warn = min_warn * precision
    min_crit = _try_convert_to_float(entry.sensor_lower_crit_value)
    if min_crit:
        min_crit = min_crit * precision
    min_fatal = _try_convert_to_float(entry.sensor_lower_fatal_value)
    if min_fatal:
        min_fatal = min_fatal * precision
    upper_warn = _try_convert_to_float(entry.sensor_upper_warn_value)
    if upper_warn:
        upper_warn = upper_warn * precision
    upper_crit = _try_convert_to_float(entry.sensor_upper_crit_value)
    if upper_crit:
        upper_crit = upper_crit * precision
    upper_fatal = _try_convert_to_float(entry.sensor_upper_fatal_value)
    if upper_fatal:
        upper_fatal = upper_fatal * precision

    if min_crit is None and min_fatal is not None:
        min_crit = min_fatal

    if upper_crit is None and upper_fatal is not None:
        upper_crit = upper_fatal

    if min_warn is None and min_crit is not None:
        min_warn = min_crit

    if upper_warn is None and upper_crit is not None:
        upper_warn = upper_crit

    if min_warn is not None and min_crit is None:
        min_crit = float("-inf")

    if upper_warn is not None and upper_crit is None:
        upper_crit = float("inf")

    def optional_tuple(warn: Optional[float], crit: Optional[float]) -> Levels:
        assert (warn is None) == (crit is None)
        if warn is not None and crit is not None:
            return ("fixed", (warn, crit))
        return None

    return Perfdata(
        reading,
        levels_upper=optional_tuple(upper_warn, upper_crit),
        levels_lower=optional_tuple(min_warn, min_crit),
    )


def convert_date_and_time(dt_str):
    """Parse SNMP DateAndTime OCTET STRING to human readable format"""
    try:
        data = dt_str.encode('latin-1')
        # Parse DateAndTime bytes
        year = int.from_bytes(data[0:2], 'big')
        month = data[2]
        day = data[3]
        hour = data[4]
        minute = data[5]
        second = data[6]
        decisecond = data[7]

        # Default: no timezone
        tz = None
        if len(data) == 11:
            direction = data[8]
            tz_hours = data[9]
            tz_minutes = data[10]
            offset = timedelta(hours=tz_hours, minutes=tz_minutes)
            if direction == 0x2D:  # '-'
                offset = -offset
            tz = timezone(offset)

        micro = decisecond * 100_000
        dt = datetime(year, month, day, hour, minute, second, micro, tzinfo=tz)
        return dt.isoformat()
    except (ValueError, IndexError):
        return dt_str
