import os
import unittest

import gspread
from oauth2client.service_account import ServiceAccountCredentials
from toggl.TogglPy import Toggl

#this test demonstrates how to link up the toggl API into a google sheet
#in order to do this, you'll need to first setup your google account developer environment
#to do this, you can follow the instructions here: http://tinaja.computer/2017/10/27/gspread.html
#additional information about the spread API here: https://github.com/burnash/gspread

#as such, to run this test you'll need to define the following env variables
#TOGGL_API_KEY : your toggl api key
#WORKSPACE_ID: a workspace id that you'd like to dump data for
#KEYFILE: the full path to your google suite keyfile (keep this secret/safe!)
#SHEET_URL: the url of the google sheet you are writing to

class Toggl2GSuiteTest(unittest.TestCase):
    def setUp(self):
        self.api_key = os.environ['TOGGL_API_KEY']
        self.toggl = Toggl()
        self.toggl.setAPIKey(self.api_key)

    # see https://stackoverflow.com/questions/19153462/get-excel-style-column-names-from-column-number
    LETTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

    @staticmethod
    def excel_style(row, col):
        """ Convert given row and column number to an Excel-style cell name. """
        result = []
        while col:
            col, rem = divmod(col - 1, 26)
            result[:0] = Toggl2GSuiteTest.LETTERS[rem]
        return ''.join(result) + str(row)

    def test_toggl2gsuite(self):
        # have to do this year by year
        data = {
            'workspace_id': os.environ['WORKSPACE_ID'],
        }
        y = self.toggl.getDetailedReport(data)


        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            os.environ['KEYFILE'],
            ['https://spreadsheets.google.com/feeds'])

        client = gspread.authorize(credentials)
        sheet = client.open_by_url(os.environ['SHEET_URL'])
        worksheet = sheet.get_worksheet(0)

        wrote_header = False
        columns_to_write = ['user', 'updated', 'start', 'end', 'client', 'project', 'description', 'is_billable',
                            'billable']
        cell_row = 0
        for row_idx, rec in enumerate(y['data']):
            if wrote_header == False:
                for col_idx, header in enumerate(columns_to_write):
                    worksheet.update_acell(Toggl2GSuiteTest.excel_style(row_idx + 1, col_idx + 1), header)
                wrote_header = True
            for col_idx, header in enumerate(columns_to_write):
                worksheet.update_acell(Toggl2GSuiteTest.excel_style(row_idx + 2, col_idx + 1), rec[header])

if __name__ == '__main__':
    unittest.main()
