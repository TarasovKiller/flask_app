from mysql.connector import connect, Error
from datetime import datetime
import time
from spreadsheet import *
from dotenv import load_dotenv
import os

load_dotenv()
WB_TOKEN = os.environ.get('WB_TOKEN')
HOST = os.environ.get('DB_HOST')
USER = os.environ.get('DB_USER')
PASSWORD = os.environ.get('DB_PASSWORD')
DATABASE = os.environ.get('DB_DATABASE')

def select_where_date(date_from):
    date = date_from
    try:
        with connect(
                host=HOST,
                user=USER,
                password=PASSWORD,
                database=DATABASE
        ) as connection:
            cursor = connection.cursor()
            sql = f"SELECT product_name,supplier_article,nm_id,created_date,look,text,valuation,images FROM reviews WHERE created_date >= '{date}' ORDER BY created_date DESC"
            cursor.execute(sql)
            res = cursor.fetchall()
            values = list(map(lambda x: list(x), res))
            return values


    except Error as e:
        print(e)


def select_all():
    try:
        with connect(
                host=HOST,
                user=USER,
                password=PASSWORD,
                database=DATABASE
        ) as connection:
            cursor = connection.cursor()
            sql = "SELECT product_name,supplier_article,nm_id,created_date,look,text,valuation,images FROM reviews ORDER BY created_date DESC"
            cursor.execute(sql)
            res = cursor.fetchall()
            return list(map(lambda x: list(x), res))


    except Error as e:
        print(e)


def select_no_answer():
    try:
        with connect(
                host=HOST,
                user=USER,
                password=PASSWORD,
                database=DATABASE
        ) as connection:
            cursor = connection.cursor()
            sql = "SELECT review_id,created_date,valuation,supplier_article,look,user_name,text,images FROM reviews " \
                  "WHERE is_answered = 0 " \
                  "ORDER BY created_date DESC"
            cursor.execute(sql)
            res = cursor.fetchall()
            return list(map(lambda x: list(x), res))


    except Error as e:
        print(e)


def test():
    try:
        with connect(
                host=HOST,
                user=USER,
                password=PASSWORD,
                database=DATABASE
        ) as connection:
            cursor = connection.cursor()
            sql = "SELECT * FROM reviews"
            cursor.execute(sql)
            connection.commit()
            return "Success"
    except Error as e:
        raise e


def insert_into_reviews(values):
    try:
        with connect(
                host=HOST,
                user=USER,
                password=PASSWORD,
                database=DATABASE
        ) as connection:
            cursor = connection.cursor()
            delete_all = "DELETE FROM reviews;"
            cursor.execute(delete_all)
            print("delete query is done")
            drop_id = "ALTER TABLE reviews AUTO_INCREMENT = 1;"
            cursor.execute(drop_id)
            print("alter query is done")
            sql = "INSERT INTO reviews VALUES(null,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);"
            cursor.executemany(sql, values)
            connection.commit()
    except Error as e:
        print(e)

def update_isAnswer(review_id):
    try:
        with connect(
                host=HOST,
                user=USER,
                password=PASSWORD,
                database=DATABASE
        ) as connection:
            cursor = connection.cursor()
            sql = f"UPDATE reviews SET is_answered=1 WHERE review_id =%s;"
            cursor.execute(sql, [review_id])
            connection.commit()
    except Error as e:
        print(e)

if __name__ == '__main__':
    pass