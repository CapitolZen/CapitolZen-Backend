from datetime import datetime
from pytz import UTC

from capitolzen.meta.states import AVAILABLE_STATES


def iterate_states(manager, manager_task):
    for state in AVAILABLE_STATES:
        if not manager(state.name).is_updating():
            manager_task.delay(state.name)
    return True


def time_convert(time):
    if isinstance(time, str):
        return UTC.localize(datetime.strptime(time, '%Y-%m-%d %I:%M:%S'))
    try:
        return UTC.localize(time)
    except ValueError:
        # Already a non-naive datetime
        return time
