from typing import List, Any

import mysql.connector as connection
from sqlalchemy import create_engine
import pymysql
import pandas as pd
import mysql
from sqlalchemy import exc


def sql_show(fac_code, date_attend, subject):
    # Credentials to database connection
    hostname = "localhost"
    dbname = "Attendance"
    uname = "root"
    pwd = "@Tanmay2611"

    # db_connection_str = 'mysql+pymysql://root:{pwd}@localhost:3306/Attendance'.format(pwd=pwd) db_connection =
    # create_engine(db_connection_str) df = pd.read_sql("SELECT * FROM final_attendance WHERE Fac_id = '{fac}' AND
    # date_of_attendance = '{doa}' AND Subject = '{sub}'".format( fac=fac_code, doa=date_attend, sub=subject ),
    # con=db_connection) reviews = df.to_dict('list') print(reviews) return(reviews)

    reviews = []
    cnx = mysql.connector.connect(host=hostname, user=uname, password=pwd, db=dbname, )
    cursor = cnx.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM final_attendance WHERE Fac_id = '{fac}' AND date_of_attendance = '{doa}' AND Subject = '{sub}' ORDER BY roll_id".format(
            fac=fac_code,
            doa=date_attend,
            sub=subject))
    for row in cursor:
        reviews.append(row)

    return reviews

def count_append(subject_id):
    hostname = "localhost"
    dbname = "Attendance"
    uname = "root"
    pwd = "@Tanmay2611"

    # db_connection_str = 'mysql+pymysql://root:{pwd}@localhost:3306/Attendance'.format(pwd=pwd) db_connection =
    # create_engine(db_connection_str) df = pd.read_sql("SELECT * FROM final_attendance WHERE Fac_id = '{fac}' AND
    # date_of_attendance = '{doa}' AND Subject = '{sub}'".format( fac=fac_code, doa=date_attend, sub=subject ),
    # con=db_connection) reviews = df.to_dict('list') print(reviews) return(reviews)

    reviews = []
    cnx = mysql.connector.connect(host=hostname, user=uname, password=pwd, db=dbname, )
    cursor = cnx.cursor(dictionary=True)
    cursor.execute(
        "UPDATE lecture_count set Count = Count+1 where Subject = '{sub}';".format(
            sub=subject_id))
    cursor.commit()
    cnx.close()
    return 0


def sql_percent(Sr_Num, subject, count):
    # Credentials to database connection
    hostname = "localhost"
    dbname = "Attendance"
    uname = "root"
    pwd = "@Tanmay2611"

    Rno = []
    for i in Sr_Num:
        qry = "SELECT roll_id FROM final_attendance WHERE Sr_No = {Sr}".format(Sr=i)
        mydb = connection.connect(host=hostname, user=uname, passwd=pwd, database=dbname)
        cursor = mydb.cursor()
        cursor.execute(qry)
        for row in cursor:
            a = row[0]
            Rno.append(a)

    percentage = []

    for roll_num in Rno:
        query = "SELECT DISTINCT COUNT(Sr_No) FROM final_attendance WHERE roll_id = '{rno}' AND Subject = '{sub}'".format(
            rno=roll_num,
            sub=subject
        )
        cursor = mydb.cursor()  # create a cursor to execute queries
        a = cursor.execute(query)
        for row in cursor:
            a = row
            a = a[0]
        percent = round(a * 100 / count, 2)
        percentage.append(percent)
    mydb.close()
    return percentage


def append_sql(df):
    # hostname = "localhost"
    # dbname = "Attendance"
    # uname = "root"
    pwd = "@Tanmay2611"

    df = df.dropna(self, axis=0, how="all", thresh=None, subset=None, inplace=True)

    db_connection_str = 'mysql+pymysql://root:{pwd}@localhost:3306/Attendance'.format(pwd=pwd)
    cnx = create_engine(db_connection_str)

    df.to_sql('final_attendance', con=cnx, if_exists='append', index=False)
    return 0

def sql_show_student(user_name, subject):

    # Credentials to database connection
    hostname = "localhost"
    dbname = "Attendance"
    uname = "root"
    pwd = "@Tanmay2611"

    reviews1 = []
    cnx = mysql.connector.connect(host=hostname, user=uname, password=pwd, db=dbname, )
    cursor = cnx.cursor(dictionary=True)
    cursor.execute("SELECT roll_id FROM final_attendance WHERE Name = '{name}'".format(
        name=user_name))
    for row in cursor:
        reviews1.append(row)
    roll_num = reviews1[0]['roll_id']
    cnx.close()

    reviews = []
    cnx = mysql.connector.connect(host=hostname, user=uname, password=pwd, db=dbname, )
    cursor = cnx.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM final_attendance WHERE roll_id = '{roll}' AND Subject = '{sub}' ORDER BY roll_id".format(
            roll = roll_num,
            sub=subject))
    for row in cursor:
        reviews.append(row)
    cnx.close()

    return reviews


