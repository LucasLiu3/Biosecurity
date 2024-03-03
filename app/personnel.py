
from app import app

from flask import session
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
import re
import mysql.connector
import connect
from flask_hashing import Hashing


hashing = Hashing(app)
app.config['SECRET_KEY'] = '5203'

dbconn = None
connection = None

def getCursor():
    global dbconn
    global connection
    connection = mysql.connector.connect(user=connect.dbuser, \
    password=connect.dbpass, host=connect.dbhost, \
    database=connect.dbname, autocommit=True)
    dbconn = connection.cursor()
    return dbconn


@app.route("/gardeners")
def gardeners():

    if 'loggedin' in session and (session['role'] =='admin' or session['role']=='staff'):

        username = session['username']
        role = session['role']

        cursor = getCursor()
        cursor.execute('SELECT * FROM gardener')
        gardeners = cursor.fetchall()  

        return render_template('detail.html',role=role,gardeners=gardeners,username=username)
    
    return render_template('base.html')
    
    
@app.route("/staff")
def staff():

     if 'loggedin' in session and session['role'] =='admin':

        
        cursor = getCursor()
        cursor.execute(f"""SELECT * FROM employee where (username != 'admin' or username is NULL) order by staff_id""")
        staff = cursor.fetchall()

        return render_template('detail.html',staffs=staff)
    
     return render_template('base.html')



@app.route("/update/<role>/<id>",methods=['GET','POST'])
def update(role,id):

    if request.method == 'GET':

        if role =='gardener':
            cursor = getCursor()
            cursor.execute(f"""select * from gardener where gardener_id ='{id}'""")
            gardener = cursor.fetchone()
            return render_template('update.html',gardener = gardener)
        if role == 'staff':
            cursor = getCursor()
            cursor.execute(f"""select * from employee where staff_id ='{id}'""")
            staff = cursor.fetchone()
            return render_template('update.html',staff = staff)
        
    if request.method =='POST':
        
        if role =='gardener':
            firstname = request.form.get('firstname')
            lastname = request.form.get('lastname')
            email = request.form.get('email')
            phone = request.form.get('phone')
            address = request.form.get('address')

            cursor = getCursor()
            cursor.execute(f"""UPDATE gardener 
                    SET first_name = '{firstname}',
                        last_name = '{lastname}',
                        email = '{email}', 
                        phone_number = '{phone}',
                        address = '{address}'
                    WHERE gardener_id = '{id}'""")
            connection.commit()
            return redirect(url_for('gardeners'))
        
        if role =='staff':
            firstname = request.form.get('firstname')
            lastname = request.form.get('lastname')
            email = request.form.get('email')
            phone = request.form.get('phone')

            cursor = getCursor()
            cursor.execute(f"""UPDATE employee 
                    SET first_name = '{firstname}',
                        last_name = '{lastname}',
                        email = '{email}', 
                        work_phone_number = '{phone}'
                    WHERE staff_id = '{id}'""")
            connection.commit()
            return redirect(url_for('staff'))

@app.route("/delete/<role>/<id>")
def delete(role,id):
    
    if role =='gardener':
        cursor = getCursor()
        cursor.execute(f"""delete from gardener where gardener_id ='{id}'""")
        connection.commit()
        return redirect(url_for('gardeners'))
    
    if role =='staff':
        cursor = getCursor()
        cursor.execute(f"""delete from employee where staff_id ='{id}'""")
        connection.commit()
        return redirect(url_for('staff'))
    
@app.route("/add/<role>",methods=['POST','GET'])
def add(role):
    
    if request.method == 'GET':
        if role =='gardener':
            return render_template('addinformation.html',gardener=role)
        
        if role == 'staff':
            return render_template('addinformation.html',staff=role)


    if request.method=='POST':

        if role =='gardener':
            firstname = request.form.get('firstname')
            lastname = request.form.get('lastname')
            email = request.form.get('email')
            phone = request.form.get('phone')
            address =request.form.get('address')
            date = request.form.get('date')

            cursor = getCursor()
            cursor.execute(f"""insert into gardener (first_name, last_name, email, phone_number,address,date_joined, status, username)
                         values ('{firstname}','{lastname}','{email}','{phone}','{address}','{date}','active',NULL);
                         """)
            connection.commit()
            return redirect(url_for('gardeners'))
        
        if role == 'staff': 
            firstname = request.form.get('firstname')
            lastname = request.form.get('lastname')
            email = request.form.get('email')
            phone = request.form.get('phone')
            date = request.form.get('date')
            position = request.form.get('position')
            department = request.form.get('department')

            cursor = getCursor()
            cursor.execute(f"""insert into employee (first_name, last_name, email, work_phone_number,hire_date,position,department, status, username)
                         values ('{firstname}','{lastname}','{email}','{phone}','{date}','{position}','{department}','active',NULL);
                         """)
            connection.commit()

            return redirect(url_for('staff'))