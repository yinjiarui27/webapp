from flask import Flask, render_template, request
from pymysql import connections
import os
import boto3
import re
from config import *

app = Flask(__name__)

bucket = custombucket
region = customregion

db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb

)
output = {}
table = 'employee'


@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('AddEmp.html')


@app.route("/about", methods=['POST'])
def about():
    return render_template('www.intellipaat.com')


@app.route("/addemp", methods=['POST'])
def AddEmp():
    emp_id = request.form['emp_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    pri_skill = request.form['pri_skill']
    location = request.form['location']
    emp_image_file = request.files['emp_image_file']

    insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    if emp_image_file.filename == "":
        return "Please select a file"

    try:

        cursor.execute(insert_sql, (emp_id, first_name, last_name, pri_skill, location))
        db_conn.commit()
        emp_name = "" + first_name + " " + last_name
        # Uplaod image file in S3 #
        emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file.jpg"
        s3 = boto3.resource('s3')

        try:
            print("Data inserted in MySQL RDS... uploading image to S3...")
            s3.Bucket(custombucket).put_object(Key=emp_image_file_name_in_s3, Body=emp_image_file)
            bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
            s3_location = (bucket_location['LocationConstraint'])

            if s3_location is None:
                s3_location = ''
            else:
                s3_location = '-' + s3_location

        except Exception as e:
            return str(e)

    finally:
        cursor.close()

    print("all modification done...")
    return render_template('AddEmpOutput.html', name=emp_name)

@app.route("/getemp", methods=['POST', 'GET'])
def GetEmp():
    return render_template('GetEmp.html')

@app.route("/fetchdata", methods=['GET', 'POST'])
def FectchData():
    emp_id = request.form['emp_id']

    select_sql = "SELECT * from employee WHERE empid = %s"
    cursor = db_conn.cursor()

    if emp_id == "":
        return "Please enter an id"

    cursor.execute(select_sql, emp_id)
    result = cursor.fetchall()
    print(result)

    if len(result) == 0:
        return "Please enter a valid id"

    s3 = boto3.resource('s3')
    my_bucket = s3.Bucket(custombucket)
    bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
    emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file.jpg"

    img_url = ""
    for my_bucket_object in my_bucket.objects.all():
        print(my_bucket_object.key)
        img_name = my_bucket_object.key
        id_num = re.findall(r'\d+', img_name)
        if id_num[0] == emp_id:
            img_url = "https://registeremployee.s3.ap-southeast-1.amazonaws.com/" + emp_image_file_name_in_s3

    return render_template('GetEmpOutput.html', id = emp_id, fname = result[0][1], lname = result[0][2],
                            interest = result[0][3], location = result[0][4], image_url = img_url)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
