from flask import Flask, render_template, request, redirect, url_for, session
import MySQLdb
import os

app = Flask(__name__)

APP_ROOT = os.path.dirname(os.path.abspath(__file__)) # Saves the path of the app.py file in APP_ROOT variable
print(APP_ROOT)

connection = MySQLdb.connect(host = "localhost", user = "root", password = "@Tanmay2611", db = "attendance")

@app.route('/')
def index():
    return render_template("index.html", title = "Admin Login")
@app.after_request
def set_response_headers(response):
    response.headers['Cache-control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'mo-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/login', methods = ['POST'])
def login():
    user = str(request.form["user"])
    password = str(request.form["password"])
    cursor = connection.cursor()
    result = cursor.execute("SELECT * FROM admin_login where binary username=%s and binary password = %s", [user, password])
    if(result == 1):
        return render_template("task.html")
    else:
        return render_template("index.html", title = "Admin Login", msg = "The Username and/or password is incorrect")

@app.route('/register_teacher', methods = ['POST'])
def register_teacher():
    return render_template("signup.html", title = "SignUp")
@app.after_request
def set_response_headers(response):
    response.headers['Cache-control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'mo-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/signup', methods = ['POST'])
def signup():
    user = str(request.form["user"])
    password = str(request.form["password"])
    email = str(request.form["email"])
    cursor = connection.cursor()
    result = cursor.execute("SELECT * FROM teacher_login where binary username = %s", [user])
    print(result)
    if(result == 1):
        return render_template("signup.html", title = "SignUp Teacher", uname = user, msg = "already present")
    else:
        cursor.execute("INSERT INTO teacher_login (username, password, email) VALUES(%s, %s, %s)", (user, password, email))
        connection.commit()
        return render_template("signup.html", title = "SignUp", msg = "successfully signedup", uname = user)

@app.route('/student', methods = ['POST'])
def file_upload():
    return render_template("upload.html")

@app.route('/signup_student', methods=['POST'])
def signup_student():
    user = str(request.form["student_name"])
    password = str(request.form["password"])
    email = str(request.form["student_email"])
    roll_number = str(request.form["roll_id"])
    email1 = str(request.form["parent_email"])
    cursor = connection.cursor()
    result = cursor.execute("SELECT * FROM student_login where binary username = %s", [user])
    print(result)
    if (result == 1):
        return render_template("signup.html", title="SignUp", uname=user, msg="already present")
    else:
        cursor.execute("INSERT INTO student_login (username, password, student_email, parent_email, roll_id) VALUES(%s, %s, %s, %s, %s)",
                        (user, password, email, email1, roll_number))
        connection.commit()
        return render_template("signup.html", title="SignUp", msg="successfully signedup", uname=user)

@app.route("/upload", methods = ["POST"])
def upload():
    target = os.path.join(APP_ROOT, "student_db/")
    if not os.path.isdir(target):
        os.mkdir(target)
    classfolder = str(request.form['class_folder'])
    session['classfolder']= classfolder
    #target1 = os.path.join(target, str(request.form["class_folder"])+"/")
    #session['target1']=target1
    for file in request.files.getlist("file"):
        print(file)
        filename = str(request.form['name_student'])
        filename = filename + ".jpg"
        filename = filename.replace(' ', '_')
        destination = "/".join([target, filename])
        print(destination)
        file.save(destination)
    return render_template("upload.html", msg1 = "File uploaded successfully")



@app.route("/changetask", methods = ['POST'])
def changetask():
    return render_template("task.html")

@app.route('/logout', methods=['POST'])
def logout():
    return render_template("index.html", title="Admin Login", msg = "Logged out, please login again")

if(__name__ == '__main__'):
    app.secret_key = 'secretkey'
    app.run(port = 8000, debug = True)
