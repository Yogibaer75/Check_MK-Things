#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2019 tribe29 GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from typing import Union, Tuple, Optional, TypedDict
from cmk.base.plugins.agent_based.agent_based_api.v1 import (
    check_levels,
    Result,
    State as state,
)
from cmk.base.plugins.agent_based.agent_based_api.v1.type_defs import (
    CheckResult,
)

StatusType = int
LevelModes = str

TwoLevelsType = Tuple[Optional[float], Optional[float]]
FourLevelsType = Tuple[
    Optional[float], Optional[float], Optional[float], Optional[float]
]
LevelsType = Union[TwoLevelsType, FourLevelsType]
FanParamDict = TypedDict(
    "TempParamDict",
    {
        "levels": TwoLevelsType,
        "levels_lower": TwoLevelsType,
        "device_levels_handling": LevelModes,
    },
    total=False,
)
FanParamType = Union[None, TwoLevelsType, FourLevelsType, FanParamDict]


def _validate_levels(
    levels: Optional[Tuple[Optional[float], Optional[float]]] = None,
) -> Optional[Tuple[float, float]]:
    if levels is None:
        return None

    warn, crit = levels
    if warn is None or crit is None:
        return None

    return warn, crit


def check_fan(
    reading: float,
    params: FanParamType,
    *,
    dev_levels: Optional[Tuple[float, float]] = None,
    dev_levels_lower: Optional[Tuple[float, float]] = None,
    dev_status: Optional[StatusType] = None,
    dev_status_name: Optional[str] = None,
) -> CheckResult:
    """This function checks the fan value against specified levels and issues a warn/cirt
    message. Levels can be supplied by the user or the device. The user has the possibility to configure
    the preferred levels. Additionally, it is possible to check temperature trends.

    Args:
        reading (Number): The numeric fan rpm value itself.
        params (dict): A dictionary giving the user's configuration. See below.
        dev_levels (Optional[LevelsType]): The upper levels (warn, crit)
        dev_levels_lower (Optional[LevelsType]): The lower levels (warn, crit)
        dev_status (Optional[StatusType]): The status according to the device itself.
        dev_status_name (Optional[str]): The device's own name for the status.

    Configuration:
        The parameter "params" may contain user configurable settings with the following keys:
            - levels -- Upper levels, user defined.
            - levels_lower -- Lower levels, user defined.
            - device_levels_handling -- One of the following modes:
                - usrdefault (default) -- Use user's levels, if not there use device's levels.
                - usr -- Always use user's levels. Ignore device's levels.
                - devdefault -- Use device's levels, if not there use user's levels.
                - dev -- Always use device's levels. Ignore users's levels.
                - best -- Report the least critical status of user's and device's levels.
                - worst -- Report the most critical status of user's and device's levels.

    GUI:
         - cmk/gui/plugins/wato/check_parameters/fan.py

    """

    # User levels are already in Celsius
    usr_levels_upper = _validate_levels(params.get("levels"))
    usr_levels_lower = _validate_levels(params.get("levels_lower"))
    dev_levels_upper = dev_levels
    dev_levels_lower = dev_levels_lower

    device_levels_handling = params.get("device_levels_handling", "usrdefault")

    usr_result, usr_metric = check_levels(
        value=reading,
        metric_name="fan",
        levels_upper=usr_levels_upper,
        levels_lower=usr_levels_lower,
        label="Speed",
        render_func=lambda fan: "%.0f rpm" % fan,
    )

    assert isinstance(usr_result, Result)

    dev_result, dev_metric = check_levels(
        value=reading,
        metric_name="fan",
        levels_upper=dev_levels_upper,
        levels_lower=dev_levels_lower,
        label="Speed",
        render_func=lambda fan: "%.0f rpm" % fan,
    )

    assert isinstance(dev_result, Result)

    usr_results = [usr_result]
    dev_results = [dev_result]

    if dev_status is not None:
        dev_results.append(
            Result(
                state=state(dev_status),
                notice="State on device: %s" % dev_status_name,
            )
        )

    if device_levels_handling == "usr":
        yield usr_metric
        yield from usr_results
        yield Result(state=state.OK, notice="Configuration: only use user levels")
        return

    if device_levels_handling == "dev":
        yield dev_metric
        yield from dev_results
        yield Result(state=state.OK, notice="Configuration: only use device levels")
        return

    if device_levels_handling == "usrdefault":
        if usr_levels_upper is not None or usr_levels_lower is not None:
            yield usr_metric
            yield from usr_results
            suffix = "(used user levels)"

        elif dev_levels_upper is not None or dev_levels_lower is not None:
            yield dev_metric
            yield from dev_results
            suffix = "(used device levels)"

        else:
            yield usr_metric
            yield from usr_results
            suffix = "(no levels found)"

        yield Result(
            state=state.OK,
            notice="Configuration: prefer user levels over device levels %s" % suffix,
        )

        return

    if device_levels_handling == "devdefault":
        if dev_levels_upper is not None or dev_levels_lower is not None:
            yield dev_metric
            yield from dev_results
            suffix = "(used device levels)"

        elif usr_levels_upper is not None or usr_levels_lower is not None:
            yield usr_metric
            yield from usr_results
            suffix = "(used user levels)"

        else:
            yield dev_metric
            yield from dev_results
            suffix = "(no levels found)"

        yield Result(
            state=state.OK,
            notice="Configuration: prefer device levels over user levels %s" % suffix,
        )

        return

    if device_levels_handling == "worst":
        usr_overall_state = state.worst(*(result.state for result in usr_results))
        dev_overall_state = state.worst(*(result.state for result in dev_results))
        worst_state = state.worst(usr_overall_state, dev_overall_state)

        if usr_overall_state == worst_state:
            yield usr_metric
            yield from usr_results
        else:
            yield dev_metric
            yield from dev_results

        yield Result(state=state.OK, notice="Configuration: show most critical state")

        return

    if device_levels_handling == "best":
        usr_overall_state = state.worst(*(result.state for result in usr_results))
        dev_overall_state = state.worst(*(result.state for result in dev_results))
        best_state = state.best(usr_overall_state, dev_overall_state)

        if usr_overall_state == best_state:
            yield usr_metric
            yield from usr_results
        else:
            yield dev_metric
            yield from dev_results

        yield Result(state=state.OK, notice="Configuration: show least critical state")

        return
