
# Howto:
#  TOGGL_APIKEY=b58ded522fbe3c7545b3694565fdf122 python3 scripts/clone_toggl_hours_to_another_account.py 2021-05-01 2021-05-31 920770 9680195 163968195 1204988 442482
# See sys.argv refs for arg documentation

import urllib
from toggl.TogglPy import Toggl
import datetime, sys, os

user_agent = 'cloner'

def get_entries(start, end, from_workspace_id, from_user_id):
    toggl = Toggl()

    toggl.setAPIKey(os.getenv('TOGGL_APIKEY'))
    response = toggl.request(f'https://toggl.com/reports/api/v2/details?workspace_id={from_workspace_id}&since={start}&until={end}&user_agent={user_agent}&uid={from_user_id}&include_time_entry_ids=true&user_ids={from_user_id}')
    if response['total_count'] > response['per_page']:
        raise Exception('Paging not supported, results exceed the page')
    for k, v in response.items():
        if k != 'data':
            print(k, v)

    entries = []

    for time_entry in response['data']:
        print(time_entry)
        entries.append(time_entry)
    return entries


def save_entries(entries, workspace_id, user_id, project_id, hourdiff_to_utc):
    toggl = Toggl()

    toggl.setAPIKey(os.getenv('TOGGL_APIKEY'))
    for entry in entries:
        start = entry['start']
        start_date = datetime.datetime.strptime(start, '%Y-%m-%dT%H:%M:%S%z')
        y = start_date.year
        m = start_date.month
        d = start_date.day
        h = start_date.hour
        desc = entry['description']
        print(entry['dur'])
        toggl.createTimeEntry(round(entry['dur']/3600000.0, 1), description=desc, projectid=project_id, year=y,
                              month=m, day=d, hour=h, hourdiff=hourdiff_to_utc)


def main():
    start = sys.argv[1]
    end = sys.argv[2]
    workspace_id = sys.argv[3]
    user_id = sys.argv[4]
    project_id = sys.argv[5]
    hourdiff_to_utc = -3  # Currently hacked to work in EEST DST timezone. BETTER WORKAROUND NEEDED
    from_workspace_id = sys.argv[6]
    from_user_id = sys.argv[7]

    entries = get_entries(start, end, from_workspace_id, from_user_id)
    try:
        save_entries(entries, workspace_id, user_id, project_id, hourdiff_to_utc)
    except urllib.error.HTTPError as e:
        print(e.code)
        print(e.reason)
        print(e)
        print(e.response.content)



if __name__ == '__main__':
    main()
