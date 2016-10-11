#--------------------------------------------------------------
# TogglPy is a non-cluttered, easily understood and implemented
# library for interacting with the Toggl API.
#--------------------------------------------------------------

# for making requests
# backward compatibility with python2
import sys
if sys.version[0] == "2":
    from urllib import urlencode
    from urllib2 import urlopen, Request
else:
    from urllib.parse import urlencode
    from urllib.request import urlopen, Request


from base64 import b64encode
# parsing json data
import json

#---------------------------------------------
# Class containing the endpoint URLs for Toggl
#---------------------------------------------
class Endpoints():
    WORKSPACES = "https://www.toggl.com/api/v8/workspaces"
    CLIENTS = "https://www.toggl.com/api/v8/clients"
    REPORT_WEEKLY = "https://toggl.com/reports/api/v2/weekly"
    REPORT_DETAILED = "https://toggl.com/reports/api/v2/details"
    REPORT_SUMMARY = "https://toggl.com/reports/api/v2/summary"
    START_TIME = "https://www.toggl.com/api/v8/time_entries/start"
    @staticmethod
    def STOP_TIME(pid):
        return "https://www.toggl.com/api/v8/time_entries/" + str(pid) + "/stop"
    CURRENT_RUNNING_TIME = "https://www.toggl.com/api/v8/time_entries/current"

#-------------------------------------------------------
# Class containing the necessities for Toggl interaction
#-------------------------------------------------------
class Toggl():
    # template of headers for our request
    headers = {
        "Authorization": "",
        "Content-Type": "application/json",
        "Accept": "*/*",
        "User-Agent": "python/urllib",
    }

    # default API user agent value
    user_agent = "TogglPy"

    #-------------------------------------------------------------
    # Auxiliary methods
    #-------------------------------------------------------------

    def decodeJSON(self, jsonString):
        return json.JSONDecoder().decode(jsonString)

    #-------------------------------------------------------------
    # Methods that modify the headers to control our HTTP requests
    #-------------------------------------------------------------
    def setAPIKey(self, APIKey):
        '''set the API key in the request header'''
        # craft the Authorization
        authHeader = APIKey + ":" + "api_token"
        authHeader = "Basic " + b64encode(authHeader.encode()).decode('ascii').rstrip()

        # add it into the header
        self.headers['Authorization'] = authHeader

    def setUserAgent(self, agent):
        '''set the User-Agent setting, by default it's set to TogglPy'''
        self.user_agent = agent

    #------------------------------------------------------
    # Methods for directly requesting data from an endpoint
    #------------------------------------------------------

    def requestRaw(self, endpoint, parameters=None):
        '''make a request to the toggle api at a certain endpoint and return the RAW page data (usually JSON)'''
        if parameters == None:
            return urlopen(Request(endpoint, headers=self.headers)).read()
        else:
            if 'user_agent' not in parameters:
                parameters.update( {'user_agent' : self.user_agent,} ) # add our class-level user agent in there
            endpoint = endpoint + "?" + urlencode(parameters) # encode all of our data for a get request & modify the URL
            return urlopen(Request(endpoint, headers=self.headers)).read() # make request and read the response

    def request(self, endpoint, parameters=None):
        '''make a request to the toggle api at a certain endpoint and return the page data as a parsed JSON dict'''
        return json.loads(self.requestRaw(endpoint, parameters))

    def postRequest(self, endpoint, parameters=None):
        '''make a POST request to the toggle api at a certain endpoint and return the RAW page data (usually JSON)'''
        if parameters == None:
            return urlopen(Request(endpoint, headers=self.headers)).read()
        else:
            data = json.JSONEncoder().encode(parameters)
            return urlopen(Request(endpoint, data=data, headers=self.headers)).read() # make request and read the response

    #----------------------------------
    # Methods for managing Time Entries
    #----------------------------------

    def startTimeEntry(self, description, pid):
        '''starts a new Time Entry'''
        data = {
            "time_entry": {
            "description": description,
            "pid": pid,
            "created_with": self.user_agent
            }
        }
        response = self.postRequest(Endpoints.START_TIME, parameters=data)
        return self.decodeJSON(response)

    def currentRunningTimeEntry(self):
        '''Gets the Current Time Entry'''
        response = self.postRequest(Endpoints.CURRENT_RUNNING_TIME)
        return self.decodeJSON(response)

    def stopTimeEntry(self, entryid):
        '''Stop the time entry'''
        response = self.postRequest(Endpoints.STOP_TIME(entryid))
        return self.decodeJSON(response)

    #-----------------------------------
    # Methods for getting workspace data
    #-----------------------------------
    def getWorkspaces(self):
        '''return all the workspaces for a user'''
        return self.request(Endpoints.WORKSPACES)

    def getWorkspace(self, name=None, id=None):
        '''return the first workspace that matches a given name or id'''
        workspaces = self.getWorkspaces() # get all workspaces
        
        # if they give us nothing let them know we're not returning anything
        if name == None and id == None:
            print("Error in getWorkspace(), please enter either a name or an id as a filter")
            return None

        if id == None: # then we search by name
            for workspace in workspaces: # search through them for one matching the name provided
                if workspace['name'] == name:
                    return workspace # if we find it return it
            return None # if we get to here and haven't found it return None
        else: # otherwise search by id
            for workspace in workspaces: # search through them for one matching the id provided
                if workspace['id'] == int(id):
                    return workspace # if we find it return it
            return None # if we get to here and haven't found it return None
    
    #--------------------------------
    # Methods for getting client data
    #--------------------------------
    def getClients(self):
        '''return all clients that are visable to a user'''
        return self.request(Endpoints.CLIENTS)

    def getClient(self, name=None, id=None):
        '''return the first workspace that matches a given name or id'''
        clients = self.getClients() # get all clients
        
        # if they give us nothing let them know we're not returning anything
        if name == None and id == None:
            print("Error in getClient(), please enter either a name or an id as a filter")
            return None

        if id == None: # then we search by name
            for client in clients: # search through them for one matching the name provided
                if client['name'] == name:
                    return client # if we find it return it
            return None # if we get to here and haven't found it return None
        else: # otherwise search by id
            for client in clients: # search through them for one matching the id provided
                if client['id'] == int(id):
                    return client # if we find it return it
            return None # if we get to here and haven't found it return None

    #---------------------------------
    # Methods for getting reports data
    #---------------------------------
    def getWeeklyReport(self, data):
        '''return a weekly report for a user'''
        return self.request(Endpoints.REPORT_WEEKLY, parameters=data)

    def getWeeklyReportPDF(self, data, filename):
        '''save a weekly report as a PDF'''
        # get the raw pdf file data
        filedata = self.requestRaw(Endpoints.REPORT_WEEKLY + ".pdf", parameters=data)

        # write the data to a file
        with open(filename, "wb") as pdf:
            pdf.write(filedata)

    def getDetailedReport(self, data):
        '''return a detailed report for a user'''
        return self.request(Endpoints.REPORT_DETAILED, parameters=data)

    def getDetailedReportPDF(self, data, filename):
        '''save a detailed report as a pdf'''
        # get the raw pdf file data
        filedata = self.requestRaw(Endpoints.REPORT_DETAILED + ".pdf", parameters=data)

        # write the data to a file
        with open(filename, "wb") as pdf:
            pdf.write(filedata)

    def getSummaryReport(self, data):
        '''return a summary report for a user'''
        return self.request(Endpoints.REPORT_SUMMARY, parameters=data)

    def getSummaryReportPDF(self, data, filename):
        '''save a summary report as a pdf'''
        # get the raw pdf file data
        filedata = self.requestRaw(Endpoints.REPORT_SUMMARY + ".pdf", parameters=data)

        # write the data to a file
        with open(filename, "wb") as pdf:
            pdf.write(filedata)

