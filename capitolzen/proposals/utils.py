from capitolzen.meta.states import AVAILABLE_STATES


def iterate_states(manager, manager_task):
    for state in AVAILABLE_STATES:
        if not manager(state.name).is_updating():
            manager_task.delay(state.name)
    return True