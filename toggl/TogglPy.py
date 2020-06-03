"""
TogglPy is a non-cluttered, easily understood and implemented
library for interacting with the Toggl API.
"""
import json  # parsing json data
import math
import sys
import time
from base64 import b64encode
from datetime import datetime

# for making requests
# backward compatibility with python2
cafile = None
if sys.version[0] == "2":
    from urllib import urlencode
    from urllib2 import urlopen, Request
else:
    from urllib.parse import urlencode
    from urllib.request import urlopen, Request
    try:
        import certifi
        cafile = certifi.where()
    except ImportError:
        pass


# --------------------------------------------
# Class containing the endpoint URLs for Toggl
# --------------------------------------------
class Endpoints():
    WORKSPACES = "https://www.toggl.com/api/v8/workspaces"
    CLIENTS = "https://www.toggl.com/api/v8/clients"
    PROJECTS = "https://www.toggl.com/api/v8/projects"
    TASKS = "https://www.toggl.com/api/v8/tasks"
    REPORT_WEEKLY = "https://toggl.com/reports/api/v2/weekly"
    REPORT_DETAILED = "https://toggl.com/reports/api/v2/details"
    REPORT_SUMMARY = "https://toggl.com/reports/api/v2/summary"
    START_TIME = "https://www.toggl.com/api/v8/time_entries/start"
    TIME_ENTRIES = "https://www.toggl.com/api/v8/time_entries"
    CURRENT_RUNNING_TIME = "https://www.toggl.com/api/v8/time_entries/current"

    @staticmethod
    def STOP_TIME(pid):
        return "https://www.toggl.com/api/v8/time_entries/" + str(pid) + "/stop"


# ------------------------------------------------------
# Class containing the necessities for Toggl interaction
# ------------------------------------------------------
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

    # ------------------------------------------------------------
    # Auxiliary methods
    # ------------------------------------------------------------

    def decodeJSON(self, jsonString):
        return json.JSONDecoder().decode(jsonString)

    # ------------------------------------------------------------
    # Methods that modify the headers to control our HTTP requests
    # ------------------------------------------------------------
    def setAPIKey(self, APIKey):
        '''set the API key in the request header'''
        # craft the Authorization
        authHeader = APIKey + ":" + "api_token"
        authHeader = "Basic " + b64encode(authHeader.encode()).decode('ascii').rstrip()

        # add it into the header
        self.headers['Authorization'] = authHeader

    def setAuthCredentials(self, email, password):
        authHeader = '{0}:{1}'.format(email, password)
        authHeader = "Basic " + b64encode(authHeader.encode()).decode('ascii').rstrip()

        # add it into the header
        self.headers['Authorization'] = authHeader

    def setUserAgent(self, agent):
        '''set the User-Agent setting, by default it's set to TogglPy'''
        self.user_agent = agent

    # -----------------------------------------------------
    # Methods for directly requesting data from an endpoint
    # -----------------------------------------------------

    def requestRaw(self, endpoint, parameters=None):
        '''make a request to the toggle api at a certain endpoint and return the RAW page data (usually JSON)'''
        if parameters is None:
            return urlopen(Request(endpoint, headers=self.headers), cafile=cafile).read()
        else:
            if 'user_agent' not in parameters:
                parameters.update({'user_agent': self.user_agent})  # add our class-level user agent in there
            # encode all of our data for a get request & modify the URL
            endpoint = endpoint + "?" + urlencode(parameters)
            # make request and read the response
            return urlopen(Request(endpoint, headers=self.headers), cafile=cafile).read()

    def request(self, endpoint, parameters=None):
        '''make a request to the toggle api at a certain endpoint and return the page data as a parsed JSON dict'''
        return json.loads(self.requestRaw(endpoint, parameters).decode('utf-8'))

    def postRequest(self, endpoint, parameters=None, method='POST'):
        '''make a POST request to the toggle api at a certain endpoint and return the RAW page data (usually JSON)'''
        if method == 'DELETE':  # Calls to the API using the DELETE mothod return a HTTP response rather than JSON
            return urlopen(Request(endpoint, headers=self.headers, method=method), cafile=cafile).code
        if parameters is None:
            return urlopen(Request(endpoint, headers=self.headers, method=method), cafile=cafile).read().decode('utf-8')
        else:
            data = json.JSONEncoder().encode(parameters)
            binary_data = data.encode('utf-8')
            # make request and read the response
            return urlopen(
                Request(endpoint, data=binary_data, headers=self.headers, method=method), cafile=cafile
            ).read().decode('utf-8')

    # ---------------------------------
    # Methods for managing Time Entries
    # ---------------------------------

    def startTimeEntry(self, description, pid=None, tid=None):
        '''starts a new Time Entry'''

        data = {
            "time_entry": {
                "created_with": self.user_agent,
                "description": description
            }
        }
        if pid:
            data["time_entry"]["pid"] = pid

        if tid:
            data["time_entry"]["tid"] = tid

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

    def createTimeEntry(self, hourduration, description=None, projectid=None, projectname=None,
                        taskid=None, clientname=None, year=None, month=None, day=None, hour=None,
                        billable=False, hourdiff=-2):
        """
        Creating a custom time entry, minimum must is hour duration and project param
        :param hourduration:
        :param description: Sets a descripton for the newly created time entry
        :param projectid: Not required if projectname given
        :param projectname: Not required if projectid was given
        :param taskid: Adds a task to the time entry (Requirement: Toggl Starter or higher)
        :param clientname: Can speed up project query process
        :param year: Taken from now() if not provided
        :param month: Taken from now() if not provided
        :param day: Taken from now() if not provided
        :param hour: Taken from now() if not provided
        :return: response object from post call
        """
        data = {
            "time_entry": {}
        }

        if not projectid:
            if projectname and clientname:
                projectid = (self.getClientProject(clientname, projectname))['data']['id']
            elif projectname:
                projectid = (self.searchClientProject(projectname))['data']['id']
            else:
                print('Too many missing parameters for query')
                exit(1)

        if description:
            data['time_entry']['description'] = description

        if taskid:
            data['time_entry']['tid'] = taskid

        year = datetime.now().year if not year else year
        month = datetime.now().month if not month else month
        day = datetime.now().day if not day else day
        hour = datetime.now().hour if not hour else hour

        timestruct = datetime(year, month, day, hour + hourdiff).isoformat() + '.000Z'
        data['time_entry']['start'] = timestruct
        data['time_entry']['duration'] = hourduration * 3600
        data['time_entry']['pid'] = projectid
        data['time_entry']['created_with'] = 'NAME'
        data['time_entry']['billable'] = billable

        response = self.postRequest(Endpoints.TIME_ENTRIES, parameters=data)
        return self.decodeJSON(response)

    def putTimeEntry(self, parameters):
        if 'id' not in parameters:
            raise Exception("An id must be provided in order to put a time entry")
        id = parameters['id']
        if type(id) is not int:
            raise Exception("Invalid id %s provided " % (id))
        endpoint = Endpoints.TIME_ENTRIES + "/" + str(id)  # encode all of our data for a put request & modify the URL
        data = json.JSONEncoder().encode({'time_entry': parameters})
        request = Request(endpoint, data=data, headers=self.headers)
        request.get_method = lambda: "PUT"

        return json.loads(urlopen(request).read())

    # ----------------------------------
    # Methods for getting workspace data
    # ----------------------------------
    def getWorkspaces(self):
        '''return all the workspaces for a user'''
        return self.request(Endpoints.WORKSPACES)

    def getWorkspace(self, name=None, id=None):
        '''return the first workspace that matches a given name or id'''
        workspaces = self.getWorkspaces()  # get all workspaces

        # if they give us nothing let them know we're not returning anything
        if name is None and id is None:
            print("Error in getWorkspace(), please enter either a name or an id as a filter")
            return None

        if id is None:  # then we search by name
            for workspace in workspaces:  # search through them for one matching the name provided
                if workspace['name'] == name:
                    return workspace  # if we find it return it
            return None  # if we get to here and haven't found it return None
        else:  # otherwise search by id
            for workspace in workspaces:  # search through them for one matching the id provided
                if workspace['id'] == int(id):
                    return workspace  # if we find it return it
            return None  # if we get to here and haven't found it return None

    def getWorkspaceProjects(self, id):
        """
        Return all of the projects for a given Workspace
        :param id: Workspace ID by which to query
        :return: Projects object returned from endpoint
        """

        return self.request(Endpoints.WORKSPACES + '/{0}'.format(id) + '/projects')

    # -------------------------------
    # Methods for getting client data
    # -------------------------------

    def getClients(self):
        '''return all clients that are visable to a user'''
        return self.request(Endpoints.CLIENTS)

    def getClient(self, name=None, id=None):
        '''return the first workspace that matches a given name or id'''
        clients = self.getClients()  # get all clients

        # if they give us nothing let them know we're not returning anything
        if name is None and id is None:
            print("Error in getClient(), please enter either a name or an id as a filter")
            return None

        if id is None:  # then we search by name
            for client in clients:  # search through them for one matching the name provided
                if client['name'] == name:
                    return client  # if we find it return it
            return None  # if we get to here and haven't found it return None
        else:  # otherwise search by id
            for client in clients:  # search through them for one matching the id provided
                if client['id'] == int(id):
                    return client  # if we find it return it
            return None  # if we get to here and haven't found it return None

    def getClientProjects(self, id, active='true'):
        """
        :param id: Client ID by which to query
        :param active: possible values true/false/both. By default true. If false, only archived projects are returned.
        :return: Projects object returned from endpoint
        """
        return self.request(Endpoints.CLIENTS + '/{0}/projects?active={1}'.format(id, active))

    def searchClientProject(self, name):
        """
        Provide only a projects name for query and search through entire available names
        WARNING: Takes a long time!
                 If client name is known, 'getClientProject' would be advised
        :param name: Desired Project's name
        :return: Project object
        """
        for client in self.getClients():
            try:
                for project in self.getClientProjects(client['id']):
                    if project['name'] == name:
                        return project
            except Exception:
                continue

        print('Could not find client by the name')
        return None

    def getClientProject(self, clientName, projectName):
        """
        Fast query given the Client's name and Project's name
        :param clientName:
        :param projectName:
        :return:
        """
        for client in self.getClients():
            if client['name'] == clientName:
                cid = client['id']

        if not cid:
            print('Could not find such client name')
            return None

        for projct in self.getClientProjects(cid):
            if projct['name'] == projectName:
                pid = projct['id']

        if not pid:
            print('Could not find such project name')
            return None

        return self.getProject(pid)

    # --------------------------------
    # Methods for getting PROJECTS data
    # --------------------------------
    def getProject(self, pid):
        '''return all projects that are visable to a user'''
        return self.request(Endpoints.PROJECTS + '/{0}'.format(pid))

    def getProjectTasks(self, pid, archived=False):
        """
        return all tasks of a given project
        :param pid: Project ID
        :param archived: choose wether to fetch archived tasks or not
        """
        return self.request(Endpoints.PROJECTS + '/{0}'.format(pid) + '/tasks')

    # --------------------------------
    # Methods for interacting with TASKS data
    # --------------------------------

    def createTask(self, name, pid, active=True, estimatedSeconds=False):
        """
        create a new task (Requirement: Toggl Starter or higher)
        :param name: Name of the task
        :param pid: Project ID
        :param active: Defines if the task is active or archived, default: active
        :param estimatedSeconds: Estimation for the task in seconds
        """

        data = {}
        data['task'] = {}
        data['task']['name'] = name
        data['task']['pid'] = pid
        data['task']['active'] = active
        data['task']['estimated_seconds'] = estimatedSeconds

        response = self.postRequest(Endpoints.TASKS, parameters=data)
        return self.decodeJSON(response)

    # --------------------------------
    # Methods for getting reports data
    # ---------------------------------
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

    def getDetailedReportPages(self, data):
        '''return detailed report data from all pages for a user'''
        pages_index = 1
        data['page'] = pages_index
        pages = self.request(Endpoints.REPORT_DETAILED, parameters=data)
        try:
            pages_number = math.ceil(pages.get('total_count', 0) / pages.get('per_page', 0))
        except ZeroDivisionError:
            pages_number = 0
        for pages_index in range(2, pages_number + 1):
            time.sleep(1)  # There is rate limiting of 1 request per second (per IP per API token).
            data['page'] = pages_index
            pages['data'].extend(self.request(Endpoints.REPORT_DETAILED, parameters=data).get('data', []))
        return pages

    def getDetailedReportPDF(self, data, filename):
        '''save a detailed report as a pdf'''
        # get the raw pdf file data
        filedata = self.requestRaw(Endpoints.REPORT_DETAILED + ".pdf", parameters=data)

        # write the data to a file
        with open(filename, "wb") as pdf:
            pdf.write(filedata)

    def getDetailedReportCSV(self, data, filename=None):
        '''save a detailed report as a csv'''
        # get the raw pdf file data
        filedata = self.requestRaw(Endpoints.REPORT_DETAILED + ".csv", parameters=data)

        if filename:
            # write the data to a file
            with open(filename, "wb") as pdf:
                pdf.write(filedata)
        else:
            return filedata

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

    # --------------------------------
    # Methods for creating, updating, and deleting clients
    # ---------------------------------
    def createClient(self, name, wid, notes=None):
        """
        create a new client
        :param name: Name the client
        :param wid: Workspace ID
        :param notes: Notes for the client (optional)
        """

        data = {}
        data['client'] = {}
        data['client']['name'] = name
        data['client']['wid'] = wid
        data['client']['notes'] = notes

        response = self.postRequest(Endpoints.CLIENTS, parameters=data)
        return self.decodeJSON(response)

    def updateClient(self, id, name=None, notes=None):
        """
        Update data for an existing client. If the name or notes parameter is not supplied, the existing data on the Toggl server will not be changed.
        :param id: The id of the client to update
        :param name: Update the name of the client (optional)
        :param notes: Update the notes for the client (optional)
        """

        data = {}
        data['client'] = {}
        data['client']['name'] = name
        data['client']['notes'] = notes

        response = self.postRequest(Endpoints.CLIENTS + '/{0}'.format(id), parameters=data, method='PUT')
        return self.decodeJSON(response)

    def deleteClient(self, id):
        """
        Delete the specified client
        :param id: The id of the client to delete
        """
        response = self.postRequest(Endpoints.CLIENTS + '/{0}'.format(id), method='DELETE')
        return response
