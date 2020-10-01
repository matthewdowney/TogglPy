#!/usr/bin/python
from operator import itemgetter as i
from TogglPy import Toggl
import datetime
import sys
import argparse

import urllib2
import json

import credentials
import os

API_KEY = credentials.data['API_KEY']
WORKSPACE_ID = credentials.data['WORKSPACE_ID']
USER_AGENT = credentials.data['USER_AGENT']

toggl = Toggl()

toggl.setAPIKey(API_KEY)

# Something like this next line would be ideal but it's not currently easy to access task IDs.
# (The only way I currently know how is to create a new task using the API and get the ID from the return value.
#  See readme for an example of how to do this.)


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def multikeysort(items, columns):
    comparers = [
        ((i(col[1:].strip()), -1) if col.startswith('-') else (i(col.strip()), 1))
        for col in columns
    ]

    def comparer(left, right):
        comparer_iter = (
            cmp(fn(left), fn(right)) * mult
            for fn, mult in comparers
        )
        return next((result for result in comparer_iter if result), 0)
    return sorted(items, cmp=comparer)


def roundTime(dt=None, roundTo=60):
    """Round a datetime object to any time laps in seconds
    dt : datetime.datetime object, default now.
    roundTo : Closest number of seconds to round to, default 1 minute.
    Author: Thierry Husson 2012 - Use it as you want but don't blame me.
    """
    if dt == None:
        dt = datetime.datetime.now()
    seconds = (dt.replace(tzinfo=None) - dt.min).seconds
    rounding = (seconds+roundTo/2) // roundTo * roundTo
    return dt + datetime.timedelta(0, rounding-seconds, -dt.microsecond)


def formatDuration(duration):

    seconds = int(duration.total_seconds())  # total_seconds required to prevent periods longer than 24hrs breaking
    durHours = str(seconds//3600)
    durMins = str((seconds//60) % 60)

    if int(durHours) < 10:
        durHours = "0"+durHours
    if int(durMins) < 10:
        durMins = "0"+durMins
    duration = durHours + ":" + durMins
    return duration


def colorText(color, text):
    if text is None:
        text = "*Not specified*"
    if terminalColors:
        return color + text + bcolors.ENDC
    else:
        return text


def last_day_of_month(any_day):
    next_month = any_day.replace(day=28) + datetime.timedelta(days=4)  # this will never fail
    return next_month - datetime.timedelta(days=next_month.day)


def main(argv):
    desc = """This program provides some basic command line Toggl reporting."""
    epilog = """Based on Matthew Downey's TogglPy library (https://github.com/matthewdowney/TogglPy/).
    This script: credit (C) Mikey Beck https://mikeybeck.com."""
    parser = argparse.ArgumentParser(description=desc, epilog=epilog)
    parser.add_argument(
        "--period", help="Time period to report on. Usage:  --period startdate enddate [where startdate & enddate take the format yyyy-mm-dd, e.g. 2017-05-23] (Or do not provide this argument, to report on the current month.  Omit second date to report from first date up to today.)", nargs='*', required=False)
    parser.add_argument(
        "--tags", help="Tags to report on.  Can be names or IDs.  Do not provide this argument to ignore tags.", nargs='*', required=False)
    parser.add_argument(
        "--clients", help="Clients to report on.  Can be names or IDs.  Do not provide this argument to report on all clients.", nargs='*', required=False)
    parser.add_argument("--nocolors", help="Prints plain output, useful if piping to a file",
                        action="store_true", required=False)
    parser.add_argument("--addtags", help="Adds tag to all returned time entries.", nargs='*', required=False)
    parser.add_argument("--removetags", help="Removes tag from all returned time entries.", nargs='*', required=False)
    parser.add_argument("--format", help="Formats output nicely for Mikey's billing purposes",
                        action="store_true", required=False)
    parser.add_argument("--debug", help="Prints debugging info", action="store_true", required=False)

    # Helper commands:
    parser.add_argument("--getclientids", help="Prints client names and IDs only.",
                        action="store_true", required=False)

    data = {
        'workspace_id': WORKSPACE_ID,
        'user_agent': USER_AGENT,
        'page': 1,
        'tag_ids': '',  # Setting to 0 actually filters OUT entries WITH tags.. Documentation incorrect?
        'client_ids': ''
    }

    x = parser.parse_args()

    # Print client names & IDs
    if x.getclientids:

        filename = 'data.json'
        with open(filename, 'r') as f:
            jsondata = json.load(f)

        for client in toggl.getClients():
            print "Client name: %s\t\t ID: %s" % (client['name'], client['id'])
            jsondata['clients'][client['name']] = client['id']  # Add client names & IDs to data.json file

        os.remove(filename)
        with open(filename, 'w') as f:
            json.dump(jsondata, f, indent=4)

        exit()

    if x.addtags or x.removetags:
        timeentryIDs = ""

    '''
curl -v -u API_TOKEN:api_token \
    -H "Content-Type: application/json" \
    -d '{"time_entry":{"tags":["testtaggy","billed"], "tag_action": "add"}}' \
    -X PUT https://www.toggl.com/api/v8/time_entries/TIME_ENTRY_ID
'''

    global terminalColors

    terminalColors = True

    if x.nocolors:
        # Display colors in the terminal.  Set to false for clean output (e.g. if piping to a file).
        terminalColors = False

    if x.period:
        data['since'] = x.period[0]
        try:
            data['until'] = x.period[1]
        except IndexError:
            data['until'] = datetime.datetime.today().strftime('%Y-%m-%d')  # Today
    else:
        data['since'] = datetime.date.today().replace(day=1)  # First day of current month
        data['until'] = last_day_of_month(datetime.date.today())  # Last day of current month
        print colorText(bcolors.WARNING, "No time period specified.  Reporting on current month.")

    if x.tags:
        filename = 'data.json'
        with open(filename, 'r') as f:
            jsondata = json.load(f)

        for tag in x.tags:
            # If digits, assume tag ID.  If chars, assume tag name and look up ID in data.json.
            if tag.isdigit() == True:
                # We have a tag ID
                tagid = tag
            else:
                # We have tag name, get tag ID from data.json.
                tagid = jsondata['tags'][tag]

            data['tag_ids'] += str(tagid) + ","  # Trailing comma doesn't matter so this is ok

    if x.clients:
        filename = 'data.json'
        with open(filename, 'r') as f:
            jsondata = json.load(f)

        for client in x.clients:
            # If digits, assume client ID.  If chars, assume client name and look up ID in data.json.
            if client.isdigit() == True:
                # We have a client ID
                clientid = client
            else:
                # We have client name, get client ID from data.json.
                clientid = jsondata['clients'][client]

            data['client_ids'] += str(clientid) + ","  # Trailing comma doesn't matter so this is ok

    if x.debug:
        print data

    detailedData = toggl.getDetailedReport(data)

    totalTime = 0
    num_items = 0

    item_count = detailedData['total_count']

    print str(item_count) + " entries"

    detailedData2 = dict(detailedData)

    while item_count > 0:
        for timeentry in detailedData['data']:
            if x.debug:
                print timeentry

            if x.addtags or x.removetags:
                timeentryIDs += str(timeentry['id'])+","

            detailedData2.update(timeentry)

            totalTime += timeentry['dur']
            num_items += 1
            item_count -= 1

            if num_items % 50 == 0:  # Page through data (there are 50 items per page)
                data['page'] += 1
                detailedData = toggl.getDetailedReport(data)
                # print "page " + str(data['page'])

    print "Total hours: " + str(round(totalTime / float(3600000), 2))

    sortedData = sorted(detailedData2['data'])
    sortedData = multikeysort(detailedData2['data'], ['client', 'project', 'start'])

    client = ""
    project = ""
    projDuration = datetime.timedelta(0)

    for timeentry in sortedData:

        if project != timeentry['project'] and projDuration != datetime.timedelta(0):
            print colorText(bcolors.HEADER, "\tProject Duration: " + formatDuration(projDuration))
            projDuration = datetime.timedelta(0)
        if client != timeentry['client']:
            print ""
            print colorText(bcolors.OKGREEN, timeentry['client'])
        if project != timeentry['project']:
            print ""
            if x.format:
                print colorText(bcolors.OKBLUE, timeentry['project'])
            else:
                print "\t" + colorText(bcolors.OKBLUE, timeentry['project'])
            # print "\t" + timeentry['project']

        try:
            # 12:00 is the timezone. Required for toggl API to work
            start = roundTime(datetime.datetime.strptime(timeentry['start'], '%Y-%m-%dT%H:%M:%S+12:00'), roundTo=5*60)
            end = roundTime(datetime.datetime.strptime(timeentry['end'], '%Y-%m-%dT%H:%M:%S+12:00'), roundTo=5*60)
        except:
            # 12:00 is the timezone. Required for toggl API to work
            start = roundTime(datetime.datetime.strptime(timeentry['start'], '%Y-%m-%dT%H:%M:%S+13:00'), roundTo=5*60)
            end = roundTime(datetime.datetime.strptime(timeentry['end'], '%Y-%m-%dT%H:%M:%S+13:00'), roundTo=5*60)

        prevDuration = datetime.timedelta(0)
        if 'thisDuration' in locals():
            prevDuration = thisDuration
        thisDuration = abs(end - start)
        projDuration += thisDuration
        duration = formatDuration(thisDuration)
        # Format start & end datetimes
        start = start.strftime('%d/%m/%Y %I:%M%p')
        end = end.strftime('%I:%M%p')

        if x.format:
            try:
                prevDate = datetime.datetime.strptime(timeentry['start'], '%Y-%m-%dT%H:%M:%S+12:00')
            except:
                prevDate = datetime.datetime.strptime(timeentry['start'], '%Y-%m-%dT%H:%M:%S+13:00')
            if 'date' in locals():
                prevDate = date
            try:
                date = datetime.datetime.strptime(timeentry['start'], '%Y-%m-%dT%H:%M:%S+12:00')
            except:
                date = datetime.datetime.strptime(timeentry['start'], '%Y-%m-%dT%H:%M:%S+13:00')

            if date - prevDate > datetime.timedelta(2):
                print ""
            if date - prevDate < datetime.timedelta(0.5) and date - prevDate != datetime.timedelta(0):
                total = formatDuration(thisDuration + prevDuration)
                thisDuration = thisDuration + prevDuration
                print start + " - " + end + " (" + duration + ") Total: (" + total + ")"
            else:
                print start + " - " + end + " (" + duration + ") "
        else:
            print "\t" + start + " - " + end + " (" + duration + ") " + timeentry['description']

        client = timeentry['client']
        project = timeentry['project']

    if x.format:
        print colorText(bcolors.HEADER, "Total: " + formatDuration(projDuration))  # Print duration of last project
    else:
        # Print duration of last project
        print colorText(bcolors.HEADER, "\tProject Duration: " + formatDuration(projDuration))

    # Apply tag to all returned time entries
    if x.addtags:
        tags = x.addtags

        if x.debug:
            print "Tags: " + str(tags)
            print "Time entry IDs: " + timeentryIDs
        timeentryIDs = timeentryIDs[:-1]  # Remove last comma

        toggl.addTags(timeentryIDs, tags)

    # Remove tag from all returned time entries
    if x.removetags:
        tags = x.removetags

        if x.debug:
            print "Tags: " + str(tags)
            print "Time entry IDs: " + timeentryIDs
        timeentryIDs = timeentryIDs[:-1]  # Remove last comma

        toggl.removeTags(timeentryIDs, tags)

    # Apply tag to all returned time entries
    if x.addtags:
        tags = x.addtags

        if x.debug:
            print "Tags: " + str(tags)
            print "Time entry IDs: " + timeentryIDs
        timeentryIDs = timeentryIDs[:-1]  # Remove last comma

        toggl.addTags(timeentryIDs, tags)

    # Remove tag from all returned time entries
    if x.removetags:
        tags = x.removetags

        if x.debug:
            print "Tags: " + str(tags)
            print "Time entry IDs: " + timeentryIDs
        timeentryIDs = timeentryIDs[:-1]  # Remove last comma

        toggl.removeTags(timeentryIDs, tags)


if __name__ == "__main__":
    main(sys.argv[1:])
