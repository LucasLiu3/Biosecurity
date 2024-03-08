
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

# http://localhost:5000/gardeners - this will be the gardeners list page, we only need GET method.
@app.route("/gardeners")
def gardeners():

    # in login page, the session has stored loggined and role,
    # since only admin and staff could see gardeners list.
    # if loggined is ture and role is admin or staff, then would going to detail page of gardners
    if 'loggedin' in session and (session['role'] =='admin' or session['role']=='staff'):

        username = session['username']
        role = session['role']

        cursor = getCursor()
        cursor.execute('SELECT * FROM gardener')
        gardeners = cursor.fetchall()  

        return render_template('detail.html',role=role,gardeners=gardeners,username=username)
    
    return render_template('base.html')
    
# http://localhost:5000/staff - this will be the staff list page, we only need GET method.
@app.route("/staff")
def staff():
     
     # if loggined is ture and role is admin, then would go to detail page of staff
     if 'loggedin' in session and session['role'] =='admin':

        
        cursor = getCursor()
        cursor.execute(f"""SELECT * FROM employee where (username != 'admin' or username is NULL) order by staff_id""")
        staff = cursor.fetchall()

        return render_template('detail.html',staffs=staff)
    
     return render_template('base.html')


# http://localhost:5000/update/<role>/<id> - this will be the update page for garnders and staff, we need GET and POST methods.
@app.route("/update/<role>/<id>",methods=['GET','POST'])
def update(role,id):

    # in POST method
    if request.method == 'GET':

        # when update role is gardener, based on the id from route, collecting data of this id from database,going to update page.
        if role =='gardener':
            cursor = getCursor()
            cursor.execute(f"""select * from gardener where gardener_id ='{id}'""")
            gardener = cursor.fetchone()
            return render_template('update.html',gardener = gardener)
        
        # when update role is staff, based on the id from route, collecting data of this id from database,going to update page.
        if role == 'staff':
            cursor = getCursor()
            cursor.execute(f"""select * from employee where staff_id ='{id}'""")
            staff = cursor.fetchone()
            return render_template('update.html',staff = staff)
    
    # in POST method
    if request.method =='POST':
        
        # when the update role is gardener.
        if role =='gardener':

            # collect the detail input from form submit
            firstname = request.form.get('firstname')
            lastname = request.form.get('lastname')
            email = request.form.get('email')
            phone = request.form.get('phone')
            address = request.form.get('address')

            # and in gardener table, update the detail of this id with the updated input details.
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
        
        # when the update role is staff.
        if role =='staff':

             # collect the detail input from form submit
            firstname = request.form.get('firstname')
            lastname = request.form.get('lastname')
            email = request.form.get('email')
            phone = request.form.get('phone')

            # and in employee table, update the detail of this id with the updated input details.
            cursor = getCursor()
            cursor.execute(f"""UPDATE employee 
                    SET first_name = '{firstname}',
                        last_name = '{lastname}',
                        email = '{email}', 
                        work_phone_number = '{phone}'
                    WHERE staff_id = '{id}'""")
            connection.commit()
            return redirect(url_for('staff'))

# http://localhost:5000/delete/<role>/<id> - this will be the delete page for garnders and staff, we only need GET method.
@app.route("/delete/<role>/<id>")
def delete(role,id):
    
    # if role is gardener, delete the data of this id in gardener table.
    if role =='gardener':
        cursor = getCursor()
        cursor.execute(f"""delete from gardener where gardener_id ='{id}'""")
        connection.commit()
        return redirect(url_for('gardeners'))
    
    # if role is staff, delete the data of this id in employee table.
    if role =='staff':
        cursor = getCursor()
        cursor.execute(f"""delete from employee where staff_id ='{id}'""")
        connection.commit()
        return redirect(url_for('staff'))

# http://localhost:5000/delete/<role>/ - this will be the add new detail for garnders or staff, we need GET and POST methods.
@app.route("/add/<role>",methods=['POST','GET'])
def add(role):
    
    # in GET method
    if request.method == 'GET':

        # if role is gardener, then going to add new gardener page. 
        if role =='gardener':
            return render_template('addinformation.html',gardener=role)
        
        # if role is staff, then going to add new staff page. 
        if role == 'staff':
            return render_template('addinformation.html',staff=role)


    # in POST method
    if request.method=='POST':

        # if role is gardener.
        if role =='gardener':

            # collect input date from submitted form
            firstname = request.form.get('firstname')
            lastname = request.form.get('lastname')
            email = request.form.get('email')
            phone = request.form.get('phone')
            address =request.form.get('address')
            date = request.form.get('date')

            # in gardener table, insert a new gardener detail data.
            cursor = getCursor()
            cursor.execute(f"""insert into gardener (first_name, last_name, email, phone_number,address,date_joined, status, username)
                         values ('{firstname}','{lastname}','{email}','{phone}','{address}','{date}','active',NULL);
                         """)
            connection.commit()
            
            # redirect to gardeners list page
            return redirect(url_for('gardeners'))
        

        # if role is staff.
        if role == 'staff': 

            # collect input date from submitted form
            firstname = request.form.get('firstname')
            lastname = request.form.get('lastname')
            email = request.form.get('email')
            phone = request.form.get('phone')
            date = request.form.get('date')
            position = request.form.get('position')
            department = request.form.get('department')

            # in employee table, insert a new staff detail data.
            cursor = getCursor()
            cursor.execute(f"""insert into employee (first_name, last_name, email, work_phone_number,hire_date,position,department, status, username)
                         values ('{firstname}','{lastname}','{email}','{phone}','{date}','{position}','{department}','active',NULL);
                         """)
            connection.commit()

            #redirect to staff list page
            return redirect(url_for('staff'))