# TogglPy Documentation
This page will serve as lightweight documentation for TogglPy.

```
NAME
    TogglPy

FILE
    toggl/TogglPy.py

DESCRIPTION
    #--------------------------------------------------------------
    # TogglPy is a non-cluttered, easily understood and implemented
    # library for interacting with the Toggl API.
    #--------------------------------------------------------------

CLASSES
    Toggl
    
    class Toggl
     |  #-------------------------------------------------------
     |  # Class containing the necessities for Toggl interaction
     |  #-------------------------------------------------------
     |  
     |  Methods defined here:
     |  
     |  getClient(self, name=None, id=None)
     |      return the first workspace that matches a given name or id
     |  
     |  getClients(self)
     |      return all clients that are visable to a user
     |  
     |  getDetailedReport(self, data)
     |      return a detailed report for a user
     |  
     |  getDetailedReportPDF(self, data, filename)
     |      save a detailed report as a pdf
     |  
     |  getSummaryReport(self, data)
     |      return a summary report for a user
     |  
     |  getSummaryReportPDF(self, data, filename)
     |      save a summary report as a pdf
     |  
     |  getWeeklyReport(self, data)
     |      return a weekly report for a user
     |  
     |  getWeeklyReportPDF(self, data, filename)
     |      save a weekly report as a PDF
     |  
     |  getWorkspace(self, name=None, id=None)
     |      return the first workspace that matches a given name or id
     |  
     |  getWorkspaces(self)
     |      return all the workspaces for a user
     |
     |  getDetailedReportPages(self, data)
     |      return detailed report data from all pages for a user
     |
     |  getWorkspaceProjects(self, id)
     |      return all of the projects for a given Workspace
     |
     |  request(self, endpoint, parameters=None)
     |      make a request to the toggle api at a certain endpoint and return the page data as a parsed JSON dict
     |  
     |  requestRaw(self, endpoint, parameters=None)
     |      make a request to the toggle api at a certain endpoint and return the RAW page data (usually JSON)
     |  
     |  setAPIKey(self, APIKey)
     |      set the API key in the request header
     |  
     |  setUserAgent(self, agent)
     |      set the User-Agent setting, by default it's set to TogglPy
```
