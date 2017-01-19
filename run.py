#!/usr/bin/python
from TogglPy import Toggl
import datetime
import sys
import argparse

toggl = Toggl()

toggl.setAPIKey('10768746f747204579627f3e37edc929') 

data = {
    'workspace_id': 334400,
    'user_agent': 'mike@mikeybeck.com',
    'page': 1,
    'tag_ids': '', # Setting to 0 actually filters OUT entries WITH tags.. Documentation incorrect?
    'client_ids': ''
}

# Something like this next line would be ideal but it's not currently easy to access task IDs.
# (The only way I currently know how is to create a new task using the API and get the ID from the return value.
#  See readme for an example of how to do this.)
#tags_to_report = 'billable' # If you have a tag for billable hours and wish to report on them, set it here.
# Instead of the above line, tag IDs are taken as arguments.



class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


from operator import itemgetter as i

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
   if dt == None : dt = datetime.datetime.now()
   seconds = (dt.replace(tzinfo=None) - dt.min).seconds
   rounding = (seconds+roundTo/2) // roundTo * roundTo
   return dt + datetime.timedelta(0,rounding-seconds,-dt.microsecond)

def formatDuration(duration):
    durHours = str(duration.seconds//3600)
    durMins = str((duration.seconds//60)%60)
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
    desc="""This program provides some basic command line Toggl reporting."""
    epilog="""Based on Matthew Downey's TogglPy library (https://github.com/matthewdowney/TogglPy/).
    This script: credit (C) Mikey Beck https://mikeybeck.com."""
    parser = argparse.ArgumentParser(description=desc,epilog=epilog)
    parser.add_argument("--period",help="Time period to report on. Usage:  --period startdate enddate [where startdate & enddate take the format yyyy-mm-dd, e.g. 2017-05-23] (Or do not provide this argument, to report on the current month)",nargs=2,required=False)
    parser.add_argument("--tagids",help="Tag IDs to report on.  Do not provide this argument to ignore tags.",nargs='*',required=False)
    parser.add_argument("--clientids",help="Client IDs to report on.  Do not provide this argument to report on all clients.",nargs='*',required=False)
    parser.add_argument("--nocolors",help="Prints plain output, useful if piping to a file",action="store_true",required=False)
    parser.add_argument("--debug",help="Prints debugging info",action="store_true",required=False)
   

    x=parser.parse_args()

    global terminalColors

    terminalColors = True

    if x.nocolors:
        terminalColors = False # Display colors in the terminal.  Set to false for clean output (e.g. if piping to a file).
        

    if x.period:
        data['since'] = x.period[0]
        data['until'] = x.period[1]
    else:
        data['since'] = datetime.date.today().replace(day=1) #First day of current month
        data['until'] = last_day_of_month(datetime.date.today()) #Last day of current month
        print colorText(bcolors.WARNING, "No time period specified.  Reporting on current month.")

    if x.tagids:
        for tagid in x.tagids:
            data['tag_ids'] += tagid + "," # Trailing comma doesn't matter so this is ok

    if x.clientids:
        for clientid in x.clientids:
            data['client_ids'] += clientid + "," # Trailing comma doesn't matter so this is ok

    if x.debug:
        print data


    detailedData = toggl.getDetailedReport(data)

    totalTime = 0
    num_items = 0

    item_count = detailedData['total_count']

    print str(item_count) + " entries"

    detailedData2 = dict(detailedData)

    while item_count > 0:
        # This bit is required if there is more than one page
        for timeentry in detailedData['data']:
 #           if tags_to_report:
 #               if tags_to_report in timeentry['tags']:
 #                   print timeentry
 #                   print ""
 #                   detailedData2.update(timeentry)
 #           else:
 #               print timeentry
 #               print ""
 #               detailedData2.update(timeentry)
            detailedData2.update(timeentry)


            totalTime += timeentry['dur']
            num_items += 1
            item_count -= 1

            if num_items % 50 == 0: #Page through data (there are 50 items per page)
                data['page'] += 1
                detailedData = toggl.getDetailedReport(data)
                #print "page " + str(data['page'])



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
            print "\t" + colorText(bcolors.OKBLUE, timeentry['project'])
            #print "\t" + timeentry['project'] 

        start = roundTime(datetime.datetime.strptime(timeentry['start'], '%Y-%m-%dT%H:%M:%S+13:00'),roundTo=5*60) #13:00 is the timezone.  Might need to change this
        end = roundTime(datetime.datetime.strptime(timeentry['end'], '%Y-%m-%dT%H:%M:%S+13:00'),roundTo=5*60)
        duration = abs(end - start)
        projDuration += duration
        duration = formatDuration(duration)
        #Format start & end datetimes
        start = start.strftime('%d/%m/%Y %I:%M%p') 
        end = end.strftime('%I:%M%p')

        print "\t" + start + " - " + end + " (" + duration + ") " + timeentry['description']

        client = timeentry['client']
        project = timeentry['project']

    print colorText(bcolors.HEADER, "\tProject Duration: " + formatDuration(projDuration)) # Print duration of last project



if __name__ == "__main__":
   main(sys.argv[1:])