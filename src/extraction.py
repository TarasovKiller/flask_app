import gc
import sys
from database_connection import *
from spreadsheet import SpreadsheetHandler
import tracemalloc
from dotenv import load_dotenv
import os

load_dotenv()
SPREADSHEET_ID = os.environ.get('SPREADSHEET_ID')

class Extraction:
    @staticmethod
    def answers_extract(spreadsheet_id=None):
        spreadsheet_id = SPREADSHEET_ID
        spreadsheet = SpreadsheetHandler(spreadsheet_id)
        values = select_no_answer()
        values = list(map(Extraction._map_func_answers, values))
        res_values = list(map(lambda x: x[:2] + [None] + [x[2]] + [None] + x[3:7] + [None, None, None]+x[7:], values))
        first_row = [
            ["ID отзыва", "Дата", "Пол пользователя", "Оценка", "Категория товара", "Артикул", "Характеристика",
             "Имя пользователя",
             "Текст отзыва", "Сгенерировать", "Отправить", "Ответ на отзыв"]]
        spreadsheet.clear_sheet("Ответы!A3:I")
        spreadsheet.clear_sheet("Ответы!K3:K")
        spreadsheet.clear_sheet("Ответы!M3:Q")
        spreadsheet.update_the_row("Ответы!A3", res_values)

    @staticmethod
    def partial_extract(spreadsheet_id=None):
        spreadsheet = SpreadsheetHandler(spreadsheet_id)
        date = spreadsheet.get_start_date()
        values = select_where_date(date)
        values = list(map(Extraction._map_func, values))
        first_row = [["Наименование", "Артикул пост.", "Артикул WB",
                      "Дата", "Вид", "Комментарий", "Оценка"]]
        spreadsheet.clear_sheet("Отзывы",first_row)
        spreadsheet.append_to_sheet(values, "Отзывы!A2")
        spreadsheet = None

        gc.collect()
        return "OK"

    @staticmethod
    def extract_all(spreadsheet_id=None):
        spreadsheet = SpreadsheetHandler(spreadsheet_id)
        values = select_all()
        values = list(map(Extraction._map_func, values))
        first_row = [["Наименование", "Артикул пост.", "Артикул WB",
                      "Дата", "Вид", "Комментарий", "Оценка"]]
        spreadsheet.clear_sheet("Отзывы",first_row)
        spreadsheet.append_to_sheet(values, "Отзывы!A2")
        spreadsheet = None

        gc.collect()
        return "OK"

    @staticmethod
    def _map_func(row):
        result = []
        result += row[:3]
        date_value = ["=DATE(" + row[3].strftime("%Y;%m;%d") + ")"]
        result += date_value
        result += row[4:-1]
        images = row[-1].split(',')

        if images != [''] and images:
            result += list(map(lambda link: f'=IMAGE("{link}")', images))
        return result

    @staticmethod
    def _map_func_answers(row):
        date_index = 1
        result = []
        result += row[:date_index]
        date_value = ["=DATE(" + row[date_index].strftime("%Y;%m;%d") + ")"]
        result += date_value
        result += row[(date_index+1):-1]
        images = row[-1].split(',')

        if images != [''] and images:
            result += list(map(lambda link: f'=IMAGE("{link}")', images))

        return result
if __name__ == '__main__':

    # mode = sys.argv[1]
    # spreadsheet_id = sys.argv[2]
    # extr = Extraction()
    # if mode == "partial":
    #     extr.partial_extract(spreadsheet_id)
    # elif mode == "full":
    #     extr.extract_all(spreadsheet_id)
    Extraction.answers_extract()
