from flask import Flask, render_template, request, redirect, url_for, session
from flask_bootstrap import Bootstrap
import MySQLdb
import os
from math import sqrt
from sklearn import neighbors
from os import listdir
from os.path import isdir, join, isfile, splitext
import shutil
import pickle
from PIL import Image, ImageFont, ImageDraw, ImageEnhance
import face_recognition
from face_recognition import face_locations
from face_recognition.face_recognition_cli import image_files_in_folder
from datetime import datetime, timedelta
from pytz import timezone
import xlsxwriter
import pandas as pd
from glob import glob
from flask_mail import Mail, Message
from io import BytesIO
import base64
import os
# import lable_image


import face_recognition
import cv2
import numpy as np
import os
import pandas as pd
import time
from sql_func import df_to_sql
from sql_display import *
from faculty_id import *
import faculty_id
import sql_display
import sql_func
# from sql_display import sql_percent
# from sql_display import append_sql

import mysql.connector as connection
from sqlalchemy import create_engine
import pymysql
import pandas as pd
import mysql

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



app = Flask(__name__, static_folder="static")

# mail settings

app.config.update(
    DEBUG=True,
    # Email settings
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=465,
    MAIL_USE_SSL=True,
    MAIL_USERNAME='college1118@gmail.com',
    MAIL_PASSWORD='yog12345',
    MAIL_DEFAULT_SENDER='college1118@gmail.com'
)
mail = Mail(app)

# declaring timezone then creating custom date format

india = timezone('Asia/Kolkata')
date = str(datetime.now(india))[:10] + "@" + str(datetime.now())[11:13] + "hrs"
date1 = str(datetime.now(india))[:10]

# getting the location of root directory of the webapp

APP_ROOT = os.path.dirname(os.path.abspath(
    __file__))  # D:\Mini_Project\Attendance_without_sql\Face-Recognition-Based-Attendance-System-master\teacher_site

APP_ROOT1 = APP_ROOT.split(
    'teacher_site')  # D:\\Mini_Project\\Attendance_without_sql\\Face-Recognition-Based-Attendance-System-master\\

# connection with mysql database using python package MySQLdb

conn = MySQLdb.connect(host="localhost", user="root", password="@Tanmay2611", db="attendance")


@app.route('/', methods=['GET', 'POST'])
def select():
    return render_template("select.html")


@app.after_request
def set_response_headers(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response



@app.route('/teacher', methods=['GET', 'POST'])
def shashwat():
    return render_template("index_teacher.html", title="Faculty login")


@app.route('/student', methods=['GET', 'POST'])
def index1():
    return render_template("index_student.html", title="Student login")


@app.route('/task_student', methods=['GET', 'POST'])
def login1():
    print(APP_ROOT)
    print(APP_ROOT1[0])
    user = str(request.form["user"])
    session['user'] = user
    paswd = str(request.form["password"])
    username = user.split(".", 1)[0]
    username = str(username)
    print(username)
    print(type(username))
    cursor = conn.cursor()
    result = cursor.execute("SELECT * from student_login where binary username=%s and binary password=%s",
                            [user, paswd])
    if (result == 1):
        return render_template("task_student.html", uname=username)
    else:
        return render_template("index_student.html", title="Student Login", msg="The username or password is incorrect")


@app.after_request
def set_response_headers(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


@app.route('/task_teacher', methods=['GET','POST'])
def login():
    print(APP_ROOT)
    print(APP_ROOT1[0])
    user = str(request.form["user"])
    session['user'] = user
    paswd = str(request.form["password"])
    username = user.split(".", 1)[0]
    username = str(username)
    print(username)
    print(type(username))
    cursor = conn.cursor()
    result = cursor.execute("SELECT * from teacher_login where binary username=%s and binary password=%s",
                            [username, paswd])
    if (result == 1):
        return render_template("task_teacher.html", uname=username)
    else:
        return render_template("index_teacher.html", title="Faculty Login", msg="The username or password is incorrect")


@app.after_request
def set_response_headers(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


@app.route('/upload_redirect', methods=['GET', 'POST'])
def upload_redirect():
    if (os.path.isfile(
            APP_ROOT + "/image.jpeg")):  ##D:\Mini_Project\Attendance_without_sql\Face-Recognition-Based-Attendance-System-master\teacher_site/image.jpeg
        os.remove(APP_ROOT + "/image.jpeg")
    return render_template("upload.html")


@app.route("/upload", methods=['GET', 'POST'])
def upload():
    try:

        faculty_id = str(request.form["faculty_id"])
        session['faculty_id'] = faculty_id
        subject_id = str(request.form["select_subject"])
        faculty_id = str(faculty_id)
        print(faculty_id)
        print(subject_id)

        #count_append(subject_id)


        video_capture = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        known_face_encodings = []
        known_face_roll_no = []
        face_locations = []
        face_encodings = []
        face_names = []
        process_this_frame = True
        attendance_record = set([])
        roll_record = {}

        # Rows in log file

        name_col = []
        roll_no_col = []
        time_col = []
        date_col = []
        fac_col = []
        sub_col = []

        df = pd.read_excel(APP_ROOT1[0] + os.sep + "student_db" + os.sep + "people_db.xlsx")

        for key, row in df.iterrows():
            roll_no = row['roll_no']
            name = row['name']
            image_path = row['image']
            roll_record[roll_no] = name
            student_image = face_recognition.load_image_file(
                APP_ROOT1[0] + os.sep + "student_db" + os.sep + image_path)
            student_face_encoding = face_recognition.face_encodings(student_image)[0]
            known_face_encodings.append(student_face_encoding)
            known_face_roll_no.append(roll_no)

        while True:
            # Grab a single frame of video
            ret, frame = video_capture.read()

            # Resize frame of video to 1/4 size for faster face recognition processing
            small_frame = cv2.resize(frame, (0, 0), fx=1, fy=1)

            # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
            rgb_small_frame = small_frame[:, :, ::-1]

            # Only process every other frame of video to save time
            if process_this_frame:
                # Find all the faces and face encodings in the current frame of video
                face_locations = face_recognition.face_locations(rgb_small_frame)
                face_encodings = face_recognition.face_encodings(
                    rgb_small_frame, face_locations)

                face_names = []
                for face_encoding in face_encodings:
                    # See if the face is a match for the known face(s)
                    matches = face_recognition.compare_faces(
                        known_face_encodings, face_encoding, tolerance=0.5)
                    name = "Unknown"

                    # # If a match was found in known_face_encodings, just use the first one.
                    # if True in matches:
                    #     first_match_index = matches.index(True)
                    #     name = known_face_roll_no[first_match_index]

                    # Or instead, use the known face with the smallest distance to the new face
                    face_distances = face_recognition.face_distance(
                        known_face_encodings, face_encoding)
                    best_match_index = np.argmin(face_distances)
                    if matches[best_match_index]:
                        roll_no = known_face_roll_no[best_match_index]
                        # add this to the log
                        name = roll_record[roll_no]
                        name = name[:-4]
                        if roll_no not in attendance_record:
                            attendance_record.add(roll_no)
                            print(name, roll_no)
                            name_col.append(name)
                            roll_no_col.append(roll_no)
                            curr_time = time.localtime()
                            curr_clock = time.strftime("%H:%M:%S", curr_time)
                            time_col.append(curr_clock)
                            attendance_date = date1
                            fac_id = faculty_id
                            sub_id = subject_id
                            date_col.append(str(attendance_date))
                            fac_col.append(str(fac_id))
                            sub_col.append(str(sub_id))

                    face_names.append(name)

            process_this_frame = not process_this_frame

            # Display the results
            for (top, right, bottom, left), name in zip(face_locations, face_names):
                # Scale back up face locations since the frame we detected in was scaled to 1/4 size
                # top *= 2
                # right *= 2
                # bottom *= 2
                # left *= 2

                # Draw a box around the face
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

                # Draw a label with a name below the face
                cv2.rectangle(frame, (left, bottom - 35),
                              (right, bottom), (0, 0, 255), cv2.FILLED)
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(frame, name, (left + 6, bottom - 6),
                            font, 1.0, (255, 255, 255), 1)

            # Display the resulting image
            cv2.imshow('Video', frame)

            # Hit 'x' on the keyboard to quit!
            if cv2.waitKey(1) & 0xFF == ord('x'):
                break

        # print(name_col)
        # print(roll_no_col)
        # print(time_col)

        # Printing to log file

        data = {'Fac_id': fac_col, 'Subject': sub_col, 'Name': name_col, 'roll_id': roll_no_col}

        # curr_time = time.localtime()
        # curr_clock = time.strftime("%c", curr_time)
        # curr_clock = curr_clock.replace(" ", "").replace(':', '_')

        # month = curr_clock[3:6]
        # day = curr_clock[0:3]
        # month = month.lower()
        # day = day.lower()

        # log_file_name = faculty_id + "_" + subject_id + "_" + curr_clock[6:8] + "_" + month + "_" + curr_clock[16:21]+
        # ".xslx" log_file_name1 = faculty_id + "_" + subject_id + "_" + curr_clock[6:8] + "_" + month + "_" +
        # curr_clock[16:21] + curr_clock + append_df_to_excel(log_file_name, data)

        df = pd.DataFrame(data)
        # filepath = "attendance_record/"+log_file_name
        # df.to_excel(filepath, index = False)
        df_to_sql(df)

        # Release handle to the webcam
        video_capture.release()
        cv2.destroyAllWindows()
        return render_template("task_teacher.html", msg="Attendance Marked, Check it using View Report button")
    except:
        return render_template("upload.html", msg="Camera Not Working")


@app.after_request
def set_response_headers(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


@app.route('/view_report', methods=['GET', 'POST'])
def view_report():
    return render_template("excel.html")


@app.route('/view_attendance', methods=['POST'])
def view_report1():
    return render_template("attendance_student.html")


# view route to download excel files


@app.route('/view', methods=['POST'])
def view():
    # test_append = str(request.form['folder_name'])
    # session['test_append'] = test_append

    user_name = str(session.get('user'))
    print(user_name)
    fac_code = faculty_id.get_fac_id(user_name)
    print(fac_code)

    date_attend = str(request.form['fname'])
    date_attend = date_attend.replace("-", "")
    print(date_attend)

    subject = request.form['subject_name']
    # time = request.form['ftime']
    # time = time[:2]
    # print(time)

    reviews = sql_display.sql_show(fac_code, date_attend, subject)
    Sr_Num = []
    for i in range(len(reviews)):
        a = reviews[i]['Sr_No']
        Sr_Num.append(a)

    hostname = "localhost"
    dbname = "Attendance"
    uname = "root"
    pwd = "@Tanmay2611"

    qry = "SELECT Count FROM lecture_count WHERE Subject = '{Sub}'".format(Sub=subject)
    mydb = connection.connect(host=hostname, user=uname, passwd=pwd, database=dbname)
    cursor = mydb.cursor()
    cursor.execute(qry)
    count = []
    for row in cursor:
        count.append(row)
    count1 = count[0][0]
    count.clear()
    print(count1)
    print(count)
    mydb.close()

    perc = sql_display.sql_percent(Sr_Num, subject, count1)
    print(perc)

    for e1, e2 in zip(reviews, perc):
        e1['Percentage'] = e2

    # return render_template("files.html", msg=final_excel, df=df, date=excel_date + "@" + time + "hrs")
    return render_template('results.html', reviews=reviews, perc=perc)


@app.route('/view_student', methods=['POST'])
def view1():
    user_name = str(session.get('user'))
    print(user_name)

    subject = request.form['subject_name']

    reviews = sql_display.sql_show_student(user_name, subject)
    Sr_Num = []
    for i in range(len(reviews)):
        a = reviews[i]['Sr_No']
        Sr_Num.append(a)

    hostname = "localhost"
    dbname = "Attendance"
    uname = "root"
    pwd = "@Tanmay2611"

    qry = "SELECT Count FROM lecture_count WHERE Subject = '{Sub}'".format(Sub=subject)
    mydb = connection.connect(host=hostname, user=uname, passwd=pwd, database=dbname)
    cursor = mydb.cursor()
    cursor.execute(qry)
    count = []
    for row in cursor:
        count.append(row)
    count1 = count[0][0]
    count.clear()
    mydb.close()

    perc = sql_display.sql_percent(Sr_Num, subject, count1)
    print(perc)

    for e1, e2 in zip(reviews, perc):
        e1['Percentage'] = e2

    # return render_template("files.html", msg=final_excel, df=df, date=excel_date + "@" + time + "hrs")
    return render_template('results.html', reviews=reviews, perc=perc)


@app.route('/excel/<path:filename>', methods=['POST'])
def download(filename):
    return send_from_directory(directory='excel', filename=filename)


# route to send emails to parents and students

@app.route('/send_mail', methods=['POST'])
def send_mail():
    test_append = str(request.form['folder_name'])
    teacher_name = str(session.get('user'))
    excel_dir = APP_ROOT + "/excel/" + test_append + "/" + teacher_name + "/"
    excel_date = request.form['fname']
    time = request.form['ftime']
    time = time[:2]
    final_send = glob(excel_dir + "/" + excel_date + "@" + time + "*.xlsx")[0]
    print(final_send)
    df = pd.read_excel(final_send)
    roll_id = list(df['Roll Id'])
    print(type(roll_id))
    print(roll_id)
    cursor = conn.cursor()
    for i in range(len(roll_id)):
        cursor.execute("SELECT student_email,parent_email from student_login where binary roll_id=%s", [roll_id[i]])
        email = list(cursor.fetchone())
        print(type(email[1]))
        print(email[0])
        print(email[1])
        msg = Message('Auto Generated', recipients=[email[0], email[1]])
        msg.body = "Hi.. " + roll_id[i] + " is present for the lecture of " + "Prof. " + str(
            teacher_name.split('.', 1)[0]) + ", which is held on " + excel_date + "@" + time + "hrs"
        msg.html = "Hi.. " + roll_id[i] + " is present for the lecture of " + "Prof. " + str(
            teacher_name.split('.', 1)[0]) + ", which is held on " + excel_date + "@" + time + "hrs"
        mail.send(msg)
    return "<h1>mail sent<h1>"


@app.route('/update', methods=['POST'])
def update():
    test_append = str(request.form['excel_folder'])
    print(test_append)
    teacher_name = str(session.get('user'))
    print(teacher_name)
    excel_dir = APP_ROOT + "/excel/"
    print(excel_dir)
    for file in request.files.getlist("updated_excel"):
        print(file)
        filename = file.filename
        print(filename)
        destination = "/".join([excel_dir, filename])
        print(destination)
        file.save(destination)
    df = pd.read_csv(destination)
    append_sql(df)

    return render_template("excel.html", msg="updated successfully")


@app.route('/calculate', methods=['POST'])
def calculate():
    test_append = str(request.form['final_class'])
    print(test_append)
    teacher_name = str(session.get('user'))
    print(teacher_name)
    excel_root = APP_ROOT + "/excel/" + test_append + "/" + teacher_name + "/"
    print(excel_root)
    excel_names = os.listdir(excel_root)
    print(excel_names)
    for i in range(len(excel_names)):
        if excel_names[i].startswith("."):
            os.remove(excel_root + excel_names[i])
        else:
            if os.path.isdir(excel_root + excel_names[i]):
                shutil.rmtree(excel_root + excel_names[i], ignore_errors=False, onerror=None)
    excel_names = os.listdir(excel_root)

    if (excel_names == []):
        return render_template("excel.html", msg1="No excel files found")

    for i in range(len(excel_names)):
        excel_names[i] = excel_root + excel_names[i]
    print(type(excel_names))
    # read them in
    excels = [pd.ExcelFile(name) for name in excel_names]
    # turn them into dataframes
    frames = [x.parse(x.sheet_names[0], header=None, index_col=None) for x in excels]
    # delete the first row for all frames except the first
    # i.e. remove the header row -- assumes it's the first
    frames[1:] = [df[1:] for df in frames[1:]]
    # concatenate them..
    combined = pd.concat(frames)
    if not os.path.isdir(excel_root + "final/"):
        os.mkdir(excel_root + "final/")
    final = excel_root + "final/"
    print(final)
    # write it out
    combined.to_excel(final + "final.xlsx", header=False, index=False)

    # below code is to find actual repetative blocks

    workbook = pd.ExcelFile(final + "final.xlsx")
    df = workbook.parse('Sheet1')
    sample_data = df['Roll Id'].tolist()
    print(sample_data)
    # a dict that will store the poll results
    results = {}
    for response in sample_data:
        results[response] = results.setdefault(response, 0) + 1
    finaldf = (pd.DataFrame(list(results.items()), columns=['Roll Id', 'Total presenty']))
    finaldf = finaldf.sort_values("Roll Id")
    print(finaldf)
    writer = pd.ExcelWriter(final + "final.xlsx")
    finaldf.to_excel(writer, 'Sheet1', index=False)
    workbook = writer.book
    worksheet = writer.sheets['Sheet1']
    worksheet.set_column(0, 1, 20)
    writer.save()
    final = final + "final.xlsx"
    session['final'] = final
    final = final[91:]
    return viewfinal(final)


def viewfinal(final):
    test_append = str(session.get('test_append'))
    final_path = str(session.get('final'))
    df = pd.read_excel(final_path)
    df.index += 1
    return render_template("files.html", msg=final, course=test_append, df=df)

@app.route('/change_profile', methods=['POST'])
def changeprofile():
    return render_template("select.html")

@app.route('/changetask', methods=['GET', 'POST'])
def changetask():
    return render_template("task_teacher.html")


@app.route('/changetaskstudent', methods=['POST'])
def changetask1():
    return render_template("task_student.html")


@app.route('/logout', methods=['POST'])
def logout():
    return render_template("index_teacher.html", title="Faculty Login", msg1="Logged out please login again")

@app.route('/logout_student', methods=['POST'])
def logout1():
    return render_template("index_student.html", title="Student Login", msg1="Logged out please login again")


@app.route('/hello', methods=['POST'])
def hello():
    data_url = request.values['imageBase64']
    data_url = data_url[22:]
    im = Image.open(BytesIO(base64.b64decode(data_url)))
    print(type(im))
    im.save('image.jpeg')
    filepath = APP_ROOT + "/" + "image.jpeg"
    var = lable_image.function(filepath)
    print(var)
    for i in range(len(var)):
        if (var[i] > 0.8):
            os.remove(filepath)
    return ''


if (__name__ == '__main__'):
    app.secret_key = 'super secret key'
    app.run(port=4545, debug=True)
