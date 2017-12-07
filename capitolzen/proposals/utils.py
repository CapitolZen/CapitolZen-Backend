from datetime import datetime
from pytz import UTC

from django.conf import settings
from django.apps import apps

from capitolzen.document_analysis.summarize import summarize_text

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


def summarize(content):
    if content is None:
        return ""
    return summarize_text(content)


def normalize_bill_data(wrapper_list, time_format='%m/%d/%Y'):
    """
    Take a list of wrappers and standardize data for output purposes
    returns a flattened dict of data for wrappers
    :param wrapper_list:
    :param time_format:
    :return dict:
    """
    output = []
    for w in wrapper_list:
        if getattr(w.bill, 'last_action_date', False):
            action_time = datetime.strptime(w.bill.last_action_date, '%Y-%m-%d %H:%M:%S')
        else:
            action_time = None
        data = {
            "state_id": w.bill.state_id,
            "state": w.bill.state,
            "id": str(w.id),
            "sponsor": w.display_sponsor,
            "summary": w.display_summary,
            "status": w.bill.remote_status,
            "position": w.position,
            "position_detail": w.position_detail,
            "last_action_date": action_time.strftime(time_format),
            "remote_url": w.bill.remote_url,
            "link": "%s/bills/%s" % (settings.APP_FRONTEND, str(w.bill.id))
        }

        output.append(data)
    return output
