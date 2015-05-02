#TogglPy
TogglPy is a non-cluttered, easily understood and implemented python library for interacting with the [Toggl API](https://github.com/toggl/toggl_api_docs).

#Features
In version 1.0, the first version, there are a few useful features.
* Make requests against any (Toggl) API endpoint with request data as a dictionary
* Generate and save PDFs of summary, weekly, or detailed reports
* Fetch reports as JSON
* Get all workspaces or all clients
* Get a specific workspace or client, by id or name

Next on the list:
* More functions for querying data easily
* Functions to add/change data & start/stop timers

#Examples
###Manual requests against against any Toggl endpoint:
```
from TogglPy import Toggl

# create a Toggl object and set our API key 
toggl = Toggl()
toggl.setAPIKey("mytogglapikey")

response = toggl.request("https://www.toggl.com/api/v8/clients")

# print the client name and id for each client in the response
# list of returned values can be found in the Toggl docs (https://github.com/toggl/toggl_api_docs/blob/master/chapters/clients.md)
for client in reponse:
    print "Client name: %s  Client id: %s" % (client['name'], client['id'])
```
Or, if you want to add some data to your request:
```
data = {
    'id': 42,
    'some_key': 'some_value',
    'user_agent': 'TogglPy_test',
}   
response = toggl.request("https://www.toggl.com/api/v8/some/endpoint", parameters=data)
```

###Generating PDF reports:
```
from TogglPy import Toggl

# create a Toggl object and set our API key 
toggl = Toggl()
toggl.setAPIKey("mytogglapikey")

# specify that we want reports from this week
data = {
    'workspace_id': 0000, # see the next example for getting a workspace id
    'since': '2015-04-27',
    'until': '2015-05-03',
}

# download one of each type of report for this time period
toggl.getWeeklyReportPDF(data, "weekly-report.pdf")
toggl.getDetailedReportPDF(data, "detailed-report.pdf")
toggl.getSummaryReportPDF(data, "summary-report.pdf")
```

###Finding workspaces and clients
This will print some raw data that will give you all the info you need to identify clients and workspaces quickly:
```
from TogglPy import Toggl

# create a Toggl object and set our API key 
toggl = Toggl()
toggl.setAPIKey("mytogglapikey")

print toggl.getWorkspaces()
print toggl.getClients()
```
If you want to clean it up a little replace those print statements with
```
for workspace in toggl.getWorkspaces():
    print "Workspace name: %s\tWorkspace id:%s" % (workspace['name'], workspace['id'])
for client in toggl.getClients():
    print "Client name: %s\tClient id:%s" % (client['name'], client['id'])
```
If you want to find a specific client or workspace:
```
john_doe = toggl.getClient(name="John Doe")
personal = toggl.getWorkspace(name="Personal")

print "John's client id is %s" % john_doe['id']
print "The workspace id for 'Personal' is %s" % personal['id']
```
The reverse can also be done; use `.getClient(id=0000)` or `.getWorkspace(id=000)` to find items by id.
