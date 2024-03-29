import os
import unittest

from toggl.TogglPy import Toggl

# these tests assume three  things:
#
# first, that you have two environment variables defined
# TOGGL_API_KEY
# WORKPSPACE_ID
#
# second, that you are able to able to reach Toggl's live REST API.
#
# finally, the test_putTimeEntry() will likely fail unless you have 1) a Client "Self" and 2) Project "Self" defined.
# and 3) some Pomodoros completed in your time entries.
# this is because these are acceptance tests that are hitting my personal Toggl repo, where I do all three
# of the above defined
#


class TogglPyTests(unittest.TestCase):

    def setUp(self):
        self.api_key = os.environ['TOGGL_API_KEY']
        if self.api_key is None:
            raise Exception("Unable to execute api tests without an api key")

        self.workspace_id = os.environ['WORKSPACE_ID']
        if self.workspace_id is None:
            raise Exception("Unable to execute api tests without a workspace key to query")

        self.toggl = Toggl()
        self.toggl.setAPIKey(self.api_key)

    def test_connect(self):
        response = self.toggl.request("https://api.track.toggl.com/api/v8/clients")
        self.assertIsNotNone(response)

    def test_putTimeEntry(self):
        request_args = {
            'workspace_id': self.workspace_id,
        }
        entries = self.toggl.getDetailedReport(request_args)
        # for this tests I'm tagging my Pomodoro Entries
        missing_projects = [r for r in entries['data'] if r['project'] is None and 'Pomodoro' in r['description']]
        me = missing_projects[0]
        me_id = me['id']  # remember for later

        # I've tagged my pomodoro entries as Self/Self
        cp = self.toggl.getClientProject("Self", "Self")
        project_id = cp['data']['id']
        me['pid'] = project_id

        # his is the new stuff
        response = self.toggl.putTimeEntry({"id": me_id, "pid": project_id})
        self.assertIsNotNone(response)
        self.assertIn('data', response)
        self.assertEqual(response['data']['pid'], project_id)

    def test_getDetailedReportCSV(self):
        data = {
            'workspace_id': self.workspace_id,
        }
        csvfile = 'data.csv'
        self.toggl.getDetailedReportCSV(data, csvfile)
        self.assertTrue(os.path.isfile(csvfile))
        os.remove(csvfile)

        data = self.toggl.getDetailedReportCSV(data)
        self.assertIsNotNone(data)

    def test_getDetailedReport(self):
        data = {
            'workspace_id': self.workspace_id,
        }
        d = self.toggl.getDetailedReport(data)
        self.assertIsNotNone(d)
        self.assertGreater(len(d.keys()), 0)
        fields = ['total_count', 'total_currencies', 'total_billable', 'data']
        for f in fields:
            self.assertIn(f, d.keys())
        data = d['data']
        self.assertGreater(len(data), 0)
        dr = data[0]
        self.assertIn('client', dr)
        self.assertIn('start', dr)
        self.assertIn('end', dr)
        self.assertIn('task', dr)
        self.assertIn('user', dr)
        self.assertIn('project', dr)


if __name__ == '__main__':
    unittest.main()
