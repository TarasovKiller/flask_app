import os
import time
import sys
from flask import Flask, request
from apiwb import main as run
from database_connection import *
from spreadsheet import SpreadsheetHandler
from crontab_set import set_cron_job
from extraction import Extraction
from apiwb import give_an_answer
from memory_profiler import profile

from datetime import timedelta
from flask import session
import tracemalloc
import psutil
import logging
import os

logging.basicConfig(filename='record.log', level=logging.DEBUG)
process = psutil.Process(os.getpid())
tracemalloc.start()
s = None

app = Flask(__name__)


@app.route("/snapshot")
def snapshot():
    global s
    if not s:
        s = tracemalloc.take_snapshot()
        return "taken snapshot\n"
    else:
        lines = []
        top_stats = tracemalloc.take_snapshot().compare_to(s, 'lineno')
        for stat in top_stats[:5]:
            lines.append(str(stat))
        return "\n".join(lines)





@app.route("/launch", methods=["POST"])
def launch():
    run()
    return "OK"


@app.route('/memory')
def print_memory():
    return {'memory': process.memory_info().rss}


@app.route("/test", methods=["POST"])
def test():
    spreadsheet = request.args.get('spreadsheet')

    return '''<h1>The spreadsheet value is: {}</h1>'''.format(spreadsheet)


@app.route("/extract_all", methods=["POST"])
def extract_all():
    spreadsheet = request.args.get('spreadsheet')
    extr = Extraction()
    extr.extract_all(spreadsheet)
    return "OK"


@app.route("/partial_extract", methods=["POST"])
def partial_extract():
    spreadsheet_id = request.args.get('spreadsheet')
    extr = Extraction()
    extr.partial_extract(spreadsheet_id)
    return "OK"


@app.route("/answers_extract", methods=["POST"])
def answers_extract():
    spreadsheet_id = request.args.get('spreadsheet')
    extr = Extraction()
    extr.answers_extract(spreadsheet_id)
    return "OK"


@app.route("/answer", methods=["POST"])
def answer():
    # text = request.args.get('text')
    review_id = request.args.get('review_id')
    app.logger.debug(f"get {review_id}")
    print(review_id)
    content = request.get_json()
    app.logger.debug(f"get {content}")
    text = content['text']
    give_an_answer(review_id, text)
    update_isAnswer(review_id)
    return "OK"


@app.route("/set_time/partial", methods=["POST"])
def set_time_partial():
    spreadsheet_id = request.args.get('spreadsheet')
    spreadsheet = SpreadsheetHandler(spreadsheet_id)
    interval = spreadsheet.get_interval()
    set_cron_job(interval, "partial", spreadsheet_id)
    return "OK"


@app.route("/set_time/full", methods=["POST"])
def set_time_full():
    spreadsheet_id = request.args.get('spreadsheet')
    spreadsheet = SpreadsheetHandler(spreadsheet_id)
    interval = spreadsheet.get_interval()
    set_cron_job(interval, "full", spreadsheet_id)
    return "OK"


if __name__ == "__main__":
    app.run()
