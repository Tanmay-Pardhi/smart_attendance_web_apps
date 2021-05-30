from sqlalchemy import create_engine
import pandas as pd
import mysql.connector as connection

def df_to_sql(df):

    # Credentials to database connection
    hostname = "localhost"
    dbname = "Attendance"
    uname = "root"
    pwd = "@Tanmay2611"

    mydb = connection.connect(host=hostname, database=dbname, user=uname, password = pwd, auth_plugin='mysql_native_password')
    cursor = mydb.cursor()
    for index, row in df.iterrows():
        print(row['Fac_id'])
        print(row['Subject'])
        print(row['Name'])
        print(row['roll_id'])
        cursor.execute("INSERT INTO final_attendance (Fac_id,Subject,Name,roll_id) VALUES ('{fac}', '{sub}', '{name}', {roll})".format(
                       fac = row['Fac_id'],
                       sub = row['Subject'],
                       name = row['Name'],
                       roll = row['roll_id']))

    mydb.commit()
    cursor.close()
    mydb.close()

