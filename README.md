# TogglPy

[![Latest PyPI version](https://img.shields.io/pypi/v/TogglPy.svg)](https://pypi.org/project/TogglPy/)

TogglPy is a python library for interacting with the [Toggl API](https://github.com/toggl/toggl_api_docs).

# Features
* Make requests against any (Toggl) API endpoint with request data as a dictionary
* Generate and save PDFs of summary, weekly, or detailed reports
* Fetch reports as JSON
* Get all workspaces or all clients
* Get a specific workspace or client, by ID or name
* Query projects, by client, or by a single name
* Add custom time entries

# Setup
+ Install the project with pip:
```shell
pip install -U TogglPy
```
+ Import the content: 
```python
from toggl.TogglPy import Toggl
```
+ Create a Toggl object: 
```python
toggl = Toggl()
```
+ Authenticate either by Toggl credentials OR using [your personal API token](https://toggl.com/app/profile):
	+ If trying to access any of the [Reports API](https://github.com/matthewdowney/TogglPy#generating-pdf-reports) endpoints, [you need to use](https://github.com/toggl/toggl_api_docs/blob/master/reports.md#authentication) your personal API token
```python
toggl.setAuthCredentials('<EMAIL>', '<PASSWORD>') 
```
OR:
```python
toggl.setAPIKey('<API-TOKEN>') 
```


# I learn best by examples:
### Manual GET requests against any Toggl endpoint:
```python
from toggl.TogglPy import Toggl

# create a Toggl object and set our API key 
toggl = Toggl()
toggl.setAPIKey("mytogglapikey")

response = toggl.request("https://api.track.toggl.com/api/v8/clients")

# print the client name and ID for each client in the response
# list of returned values can be found in the Toggl docs:
# https://github.com/toggl/toggl_api_docs/blob/master/chapters/clients.md
for client in response:
    print("Client name: %s  Client ID: %s" % (client['name'], client['id']))
```
Or, if you want to add some data to your request:
```python
data = {
    'id': 42,
    'some_key': 'some_value',
    'user_agent': 'TogglPy_test',
}   
response = toggl.request("https://api.track.toggl.com/api/v8/some/endpoint", parameters=data)
```

### Making a POST request to any Toggl endpoint:
```python

data = { 
    "project": 
        { 
            "name": "some project", 
            "wid":777, 
            "template_id":10237, 
            "is_private":true, 
            "cid":123397 
        }
    }

response = toggl.postRequest("https://api.track.toggl.com/api/v8/projects", parameters=data)

```


### Generating PDF reports:
**Must** authenticate with your personal API token to use these endpoints.
```python
# specify that we want reports from this week
data = {
    'workspace_id': 0000, # see the next example for getting a workspace ID
    'since': '2015-04-27',
    'until': '2015-05-03',
}

# download one of each type of report for this time period
toggl.getWeeklyReportPDF(data, "weekly-report.pdf")
toggl.getDetailedReportPDF(data, "detailed-report.pdf")
toggl.getSummaryReportPDF(data, "summary-report.pdf")
```

### Finding workspaces and clients
This will print some raw data that will give you all the info you need to identify clients and workspaces quickly:
```python
print(toggl.getWorkspaces())
print(toggl.getClients())
```
If you want to clean it up a little replace those print statements with
```python
for workspace in toggl.getWorkspaces():
    print("Workspace name: %s\tWorkspace ID:%s" % (workspace['name'], workspace['id']))
for client in toggl.getClients():
    print("Client name: %s\tClient ID:%s" % (client['name'], client['id']))
```
If you want to find a specific client or workspace:
```python
john_doe = toggl.getClient(name="John Doe")
personal = toggl.getWorkspace(name="Personal")

print("John's client ID is %s" % john_doe['id'])
print("The workspace ID for 'Personal' is %s" % personal['id'])
```
The reverse can also be done; use `.getClient(id=0000)` or `.getWorkspace(id=000)` to find items by ID.

### Starting New Timer

```python
# You can get your project PID in toggl.com->Projects->(select your project)
# and copying the last number of the url
myprojectpid = 10959693
toggl.startTimeEntry("my description", myprojectpid)
```

### Stopping Current Timer

```python
currentTimer = currentRunningTimeEntry()
stopTimeEntry(currentTimer['data']['id'])
```

### Creating a custom time entry

```python
# Create a custom entry for today, of a 9 hour duration, starting at 10 AM:
toggl.createTimeEntry(hourduration=9, projectname='GoogleDrive', hour=10)

# Or speed up the query process and provide the client's name:
toggl.createTimeEntry(hourduration=9, projectname='GoogleDrive', clientname='Google', hour=10)

# Provide *month* and/or *day* too for specific dates:
toggl.createTimeEntry(hourduration=9, projectname='GoogleDrive', clientname='Google', month=1, day=31, hour=10)

# Automate missing time entries!
for day in (29, 30, 31):
	toggl.createTimeEntry(hourduration=9, projectname='someproject', day=day, hour=10)
```
	
### Automate daily records
```python
# toggle_entry.py
import datetime
if datetime.datetime.today().weekday() not in (4, 5):
	toggl.createTimeEntry(hourduration=9, projectname='someproject', hour=10)
```
#### Add your daily records as a cron job:
```shell
(crontab -l ; echo "0 22 * * * toggl_entry.py")| crontab -
```
