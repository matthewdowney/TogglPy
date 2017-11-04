import os
import unittest
from TogglPy import Toggl

#these tests assume that you have two environment variables defined
#TOGGL_API_KEY
#WORKPSPACE_ID


class TogglPyTests(unittest.TestCase):

    def setUp(self):
        self.api_key      = os.environ['TOGGL_API_KEY']
        if self.api_key is None:
            raise Exception("Unable to execute api tests without an api key")

        self.workspace_id = os.environ['WORKSPACE_ID']
        if self.workspace_id is None:
            raise Exception("Unable to execute api tests without a workspace key to query")

        self.toggl        = Toggl()
        self.toggl.setAPIKey(self.api_key)

    def test_connect(self):
        response = self.toggl.request("https://www.toggl.com/api/v8/clients")
        self.assertTrue(response is not None)

    def test_getDetailedReportCSV(self):
        data = {
            'workspace_id': self.workspace_id,
        }
        csvfile = 'data.csv'
        self.toggl.getDetailedReportCSV(data, csvfile)
        self.assertTrue(os.path.isfile(csvfile))
        os.remove(csvfile)

        data = self.toggl.getDetailedReportCSV(data)
        self.assertTrue(data is not None)


    def test_getDetailedReport(self):
        data = {
            'workspace_id': self.workspace_id,
        }
        d = self.toggl.getDetailedReport(data)
        self.assertTrue(d is not None)
        print(d)
        self.assertTrue(len(d.keys()) > 0 )
        fields = ['total_count', 'total_currencies', 'total_billable', 'data']
        for f in fields:
            self.assertTrue(f in d.keys())
        data = d['data']
        self.assertTrue(len(data)>0)
        dr = data[0]
        self.assertTrue('client' in dr)
        self.assertTrue('start' in dr)
        self.assertTrue('end' in dr)
        self.assertTrue('task' in dr)
        self.assertTrue('user' in dr)
        self.assertTrue('project' in dr)

if __name__ == '__main__':
    unittest.main()