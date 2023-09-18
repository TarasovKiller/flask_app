import gc
import os
import re

from googleapiclient import discovery
import httplib2
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
import datetime





class SpreadsheetHandler:
    START_DATE = "D23:E23"
    INTERVAL = "D21:E21"
    AUTH_FLAG = "D37:E37"
    CODE = "D36"
    PHONE = "D35:E35"
    AUTH_STATE = "B39:E41"

    def __init__(self, spreadsheet_id=None):
        self.spreadsheet_id = spreadsheet_id
        self.service = self._get_service()
        self.sheet = self.service.spreadsheets()

    def set_spreadsheet_id(self, spreadsheet_id):
        self.spreadsheet_id = spreadsheet_id

    def _get_service(self):
        # path_parent = os.path.dirname(os.getcwd())
        dir_path = os.path.dirname(os.path.abspath(__file__))
        creds_json = os.path.join(dir_path, os.pardir, "credentials.json")

        scopes = ['https://www.googleapis.com/auth/spreadsheets']

        creds_service = ServiceAccountCredentials.from_json_keyfile_name(creds_json, scopes).authorize(httplib2.Http())
        return build('sheets', 'v4', http=creds_service)

    def append_to_sheet(self, values, range):
        request = self.sheet.values().append(spreadsheetId=self.spreadsheet_id,
                                             range=range,
                                             valueInputOption="USER_ENTERED",
                                             insertDataOption="OVERWRITE",
                                             body={"values": values})
        response = request.execute()
        return response

    def clear_sheet(self, range, first_row=None):
        request = self.sheet.values().clear(spreadsheetId=self.spreadsheet_id,
                                            range=range)
        response = request.execute()
        if first_row:
            self.append_to_sheet(first_row, range)
        return response

    def get_start_date(self):
        value = self.get_cell(self.START_DATE)
        date = datetime.datetime.strptime(value, '%d.%m.%Y')
        return date

    def get_cell(self, cell):
        request = self.sheet.values().get(spreadsheetId=self.spreadsheet_id,
                                          range=f"Пункт управления!{cell}")
        response = request.execute()
        value = response['values'][0][0]
        return value

    def get_interval(self):
        value = self.get_cell(self.INTERVAL)
        return value

    def get_list_values(self, range):
        request = self.sheet.values().get(spreadsheetId=self.spreadsheet_id,
                                          range=range,
                                          valueRenderOption="FORMULA",
                                          dateTimeRenderOption="FORMATTED_STRING")
        response = request.execute()
        values = response.get("values", None)
        return values[1:] if values is not None else []

    def slice_by_date(self, values, index_date, date):
        slice_idx = 0
        is_start = False
        is_finish_completely = True
        for i, value in enumerate(values):
            is_start = True
            curr_date = value[index_date]
            curr_date = self.__parse_to_date(curr_date)
            if date > curr_date:
                slice_idx = i
                is_finish_completely = False
                break
        sliced_values = values[slice_idx:] if not (is_start and is_finish_completely) else [[]]
        return sliced_values

    def __parse_to_date(self, line):
        numbers = re.findall(r'\d+', line)
        y, m, d = numbers
        date = datetime.datetime(int(y), int(m), int(d))
        return date

    def refresh_sheet(self, new_values, date_from=None, sheet="Лист1"):
        date = self.get_start_date() if date_from is None else date_from
        values = self.get_list_values("Лист1")
        index_date = 4
        sliced_values = self.slice_by_date(values, index_date, date)
        values = new_values + sliced_values
        self.clear_sheet(sheet)
        self.append_to_sheet(values, sheet)

    def update_state_cell(self, value):
        request = self.sheet.values().update(spreadsheetId=self.spreadsheet_id,
                                             range="Launch!B2",
                                             valueInputOption="USER_ENTERED",
                                             body={"values": [[value]]})
        response = request.execute()
        return response

    def get_auth_flag(self):

        return self.get_cell(self.AUTH_FLAG)

    def get_code(self):

        return self.get_cell(self.CODE)

    def update_auth_flag(self, value):
        return self.update_cell(self.AUTH_FLAG, value)

    def update_code(self, value):
        return self.update_cell(self.CODE, value)

    def get_phone(self):
        return self.get_cell(self.PHONE)

    def update_auth_state(self, value):
        self.update_cell(self.AUTH_STATE, value)

    def update_cell(self, cell, value):
        request = self.sheet.values().update(spreadsheetId=self.spreadsheet_id,
                                             range=f"Пункт управления!{cell}",
                                             valueInputOption="USER_ENTERED",
                                             body={"values": [[value]]})
        response = request.execute()
        return response
    def update_the_row(self,range,values):
        request = self.sheet.values().update(spreadsheetId=self.spreadsheet_id,
                                             range=range,
                                             valueInputOption="USER_ENTERED",
                                             body={"values": values})
        response = request.execute()
        return response
    def batch_update(self):
        body = body = {
            'valueInputOption': 'USER_ENTERED',
            'data': [
                {'range': 'Тест!D2', 'values': [
                    ["Azzrael Code", "YouTube Channel"],
                    ["More about", "Google Sheets API"],
                    ["styling", None, "charts"],
                ]},
                {'range': 'Тест!H4', 'values': [
                    ["Azzrael Code", "YouTube Channel"],
                    ["More about", "Google Sheets API"],
                    ["styling", "formulas", "charts"],
                ]}
            ]
        }
        request = self.sheet.values().batchUpdate(spreadsheetId=self.spreadsheet_id, body=body)
        response = request.execute()
        return response


def main():
    token = ""
    spreadsheet = SpreadsheetHandler(token)
    resp = spreadsheet.batch_update()
    print(resp)


if __name__ == '__main__':
    main()
