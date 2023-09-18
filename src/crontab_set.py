from crontab import CronTab
import sys
from spreadsheet import *
from database_connection import *
from spreadsheet import SpreadsheetHandler
from extraction import Extraction


def set_cron_job(cell,mode,spreadsheet_id):
    extraction = Extraction()
    cron = CronTab(user='mys')
    cron.remove_all(comment=f'extraction from wb into {spreadsheet_id}')
    job = cron.new(command=f'cd /var/www/triviaa-wb && /var/www/triviaa-wb/venv/bin/python3  src/extraction.py {mode} {spreadsheet_id}',
                   comment=f'extraction from wb into {spreadsheet_id}')
    number,measurement = cell.split(" ")
    if mode == "partial":
        extraction.partial_extract(spreadsheet_id)
    elif mode == "full":
        extraction.extract_all(spreadsheet_id)
    if "час" in measurement:
        job.every(number).hour()
    elif ("дн" in measurement) or (measurement == "день"):
        job.every(number).day()
    else:
        job.minute.every(5)
    cron.write()
    for job in cron:
        print(job)



if __name__ == '__main__':
    time = sys.argv[1]
    mode = sys.argv[2]
    spreadsheet_id = sys.argv[3]
    set_cron_job(time,mode,spreadsheet_id)
