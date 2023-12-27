
from flask import Flask, render_template, request, redirect, url_for,flash
import secrets
from pymysql import connections
import os
import boto3
from config import *

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

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
table = 'student'


@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('AddStu.html')


@app.route("/about", methods=['GET'])
def about():
    return render_template('www.facebook.com')

@app.route("/update", methods=['GET'])
def update():
    return render_template('update_stu.html')


@app.route("/getstudent", methods=['GET'])
def getstudent():
    return render_template('GetStu.html')

@app.route("/deletestudent", methods=['GET'])
def deletestudent():
    return render_template('delete.html')


##########################################################################################################################################
#adding info of student ........

@app.route("/addstu", methods=['POST'])
def AddStu():
    stu_id = request.form['stu_id']
    first_name = request.form['first_name']

    stu_image_file = request.files['stu_image_file']

    insert_sql = "INSERT INTO student VALUES (%s, %s,)"
    cursor = db_conn.cursor()

    if stu_image_file.filename == "":
        return "Please select a file"

    try:

        cursor.execute(insert_sql, (stu_id, first_name))
        db_conn.commit()
        stu_name = "" + first_name
        # Uplaod image file in S3 #
        # stu_image_file_name_in_s3 = "stu-id-" + str(stu_id) + "_image_file"
        # s3 = boto3.resource('s3')

        # try:
        #     print("Data inserted in MySQL RDS... uploading image to S3...")
        #     s3.Bucket(custombucket).put_object(Key=stu_image_file_name_in_s3, Body=stu_image_file)
        #     bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
        #     s3_location = (bucket_location['LocationConstraint'])

        #     if s3_location is None:
        #         s3_location = ''
        #     else:
        #         s3_location = '-' + s3_location

        #     object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
        #         s3_location,
        #         custombucket,
        #         stu_image_file_name_in_s3)

        # except Exception as e:
        #     return str(e)

    finally:
        cursor.close()

    print("all modification done...")
    return render_template('AddStuOutput.html', name=stu_name)

#############################################################################################################################################3


# updating the student if it present in the data base ....

# updating the student if it present in the data base ....

@app.route("/updatestu", methods=['POST'])
def UpdateStu():
    # Retrieve the student information from the form
    stu_id = request.form['stu_id']
    first_name = request.form['first_name']
    

    cursor = db_conn.cursor()

    try:
        # Check if student with given ID already exists
        cursor.execute("SELECT * FROM student WHERE stu_id = %s", (stu_id,))
        existing_student = cursor.fetchone()

        if existing_student:
            # Student with the same ID exists, update the record
            update_sql = "UPDATE student SET first_name = %s WHERE stu_id = %s"
            cursor.execute(update_sql, (first_name,  stu_id))
            db_conn.commit()

            stu_name = f"{first_name}"
            return render_template('AddStuOutput.html', name=stu_name)
        else:
            # flash("Invalid: Student ID not found.", 'error')
            return render_template('AddStuOutput.html', name=stu_name)

    finally:
        cursor.close()




#######################################################################################################################
        
#getting the data from the database.
@app.route("/display_data", methods=['POST'])
def display_data():
    stu_id = request.form.get('stu_id', type=int)
    if stu_id is not None:
        cursor = db_conn.cursor()
        try:
            # Fetch data for the specific student ID
            cursor.execute("SELECT * FROM student WHERE stu_id = %s", (stu_id,))
            student_data = cursor.fetchone()
            print(stu_id , student_data)
            if student_data:
                # Render the HTML template with the student data
                print("fetch successfully")
                return render_template('GetStuOutput.html', data=student_data)
            else:
                error_message = f"Student with ID {stu_id} not found."
                # flash('Error: Something went wrong!', 'error')
                return redirect(url_for('getstudent', error_message=error_message))

        finally:
            cursor.close()
    else:
        error_message = f"Please Enter a Valid Student Id."
        # flash("Enter a Valid Id", 'error')
        return redirect(url_for('getstudent', error_message=error_message))
    
##############################################################################################################################################
#delete entry
@app.route("/delete", methods=['POST'])
def DeleteStu():
    # Retrieve the student ID from the form
    stu_id = request.form['stu_id']

    cursor = db_conn.cursor()

    try:
        # Check if student with given ID exists
        cursor.execute("SELECT * FROM student WHERE stu_id = %s", (stu_id,))
        existing_student = cursor.fetchone()

        if existing_student:
            # Student with the given ID exists, delete the record
            delete_sql = "DELETE FROM student WHERE stu_id = %s"
            cursor.execute(delete_sql, (stu_id,))
            db_conn.commit()

            return render_template('AddStuOutput.html', name=stu_id)
        else:
            # flash("student id is not found", 'error')
            return render_template('delete.html', name=stu_id)

    finally:
        cursor.close()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
