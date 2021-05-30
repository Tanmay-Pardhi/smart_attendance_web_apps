import flask
import pandas as pd
import os
from flask import Flask
app = Flask(__name__, static_folder="excel")
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
print(APP_ROOT)
APP_ROOT1 = APP_ROOT.split('teacher_site')
print(APP_ROOT1)
a = APP_ROOT1[0] + os.sep + "student_db" + os.sep + "people_db.xlsx"
print(a)
#df = pd.read_excel(APP_ROOT1[0] + os.sep + "student_db" + os.sep + "people_db.xlsx")
#print(df)