
import os
import unittest
import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from TogglPy import Toggl


class Toggl2GSuiteTest(unittest.TestCase):

    def setUp(self):
        self.api_key = os.environ['TOGGL_API_KEY']
        self.toggl = Toggl()
        self.toggl.setAPIKey(self.api_key)


    def test_connect(self):
        response = self.toggl.request("https://www.toggl.com/api/v8/clients")
        self.assertTrue( response is not None )

    #see https://stackoverflow.com/questions/19153462/get-excel-style-column-names-from-column-number
    LETTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

    @staticmethod
    def excel_style(row, col):
        """ Convert given row and column number to an Excel-style cell name. """
        result = []
        while col:
            col, rem = divmod(col - 1, 26)
            result[:0] = Toggl2GSuiteTest.LETTERS[rem]
        return ''.join(result) + str(row)

    def test_get_csv(self):
        #have to do this year by year
        data = {
            'workspace_id' : 1543644,
            'since': '2016-01-01',
            'until': '2016-12-31'
        }
        y1 = self.toggl.getDetailedReport(data)

        data = {
            'workspace_id' : 1543644,
            'since': '2017-01-01',
            'until': datetime.datetime.today().strftime('%Y-%m-%d')
        }
        y2 = self.toggl.getDetailedReport(data)

        y = y1['data']+y2['data']

        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            os.environ['KEYFILE'],
            ['https://spreadsheets.google.com/feeds'])

        client = gspread.authorize(credentials)
        sheet = client.open_by_url(os.environ['SHEET_URL'])
        worksheet = sheet.get_worksheet(0)

        wrote_header = False
        columns_to_write = ['user', 'updated', 'start', 'end', 'client', 'project', 'description', 'is_billable',  'billable']
        for row_idx, rec in enumerate(y):
            if wrote_header == False:
                for col_idx, header in enumerate(columns_to_write):
                    worksheet.update_acell(Toggl2GSuiteTest.excel_style(row_idx+1, col_idx+1), header)
                wrote_header = True
            else:
                for col_idx, header in enumerate(columns_to_write):
                    worksheet.update_acell(Toggl2GSuiteTest.excel_style(row_idx+1,col_idx+1), rec[header])

       # {u'updated': u'2017-11-03T15:09:18-07:00', u'task': None, u'end': u'2017-11-03T15:09:19-07:00',
        # u'description': u'', u'project_color': u'0', u'tags': [], u'is_billable': False, u'pid': None, u'cur': u'USD',
        # u'project': None, u'start': u'2017-11-03T14:44:19-07:00', u'client': None, u'user': u'Lyle', u'billable': 0.0,
        # u'tid': None, u'project_hex_color': None, u'dur': 1500000, u'use_stop': True, u'id': 723388484,
        # u'uid': 2334312}