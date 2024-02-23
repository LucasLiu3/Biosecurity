from flask import Flask, session
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
import re
from datetime import datetime
import mysql.connector
from mysql.connector import FieldType
import connect
from datetime import datetime,timedelta
from flask_hashing import Hashing


app = Flask(__name__)
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

@app.route("/")
def base():
    return render_template("base.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    # Output message if something goes wrong...

    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        user_password = request.form['password']

        # Check if account exists using MySQL
        cursor = getCursor()
        cursor.execute('SELECT * FROM account WHERE username = %s', (username,))
        # Fetch one record and return result
        account = cursor.fetchone()
        print(account)
        if account is not None:
            password = account[2]
            role=account[4]
            if hashing.check_value(password, user_password, salt='abcd'):
            # If account exists in accounts table 
            # Create session data, we can access this data in other routes
                session['loggedin'] = True
                session['username'] = account[1]
                session['role'] =role
                # Redirect to home page
                return redirect(url_for('home'))
            else:
                #password incorrect
                msg = 'Incorrect password!'
        else:
            # Account doesnt exist or username incorrect
            msg = 'Incorrect username'
    # Show the login form with message (if any)
    return render_template('base.html', msg=msg)

@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('username', None)
   # Redirect to login page
   return redirect(url_for('login'))


# http://localhost:5000/register - this will be the registration page, we need to use both GET and POST requests
@app.route('/register', methods=['GET', 'POST'])
def register():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST':

        if 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access
            username = request.form['username']
            password = request.form['password']
            email = request.form['email']
            # Check if account exists using MySQL
            cursor = getCursor()
            cursor.execute('SELECT * FROM account WHERE username = %s', (username,))
            account = cursor.fetchone()
            # If account exists show error and validation checks
            if account:
                msg = 'Account already exists!'
            elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                msg = 'Invalid email address!'
            elif not re.match(r'[A-Za-z0-9]+', username):
                msg = 'Username must contain only characters and numbers!'
            elif not username or not password or not email:
                msg = 'Please fill out the form!'
            else:
                # Account doesnt exists and the form data is valid, now insert new account into accounts table
                hashed = hashing.hash_value(password, salt='abcd')
                cursor.execute('INSERT INTO account (username, password, email) VALUES (%s, %s, %s)', (username, hashed, email,))
                connection.commit()
                session['loggedin'] = True
                session['username'] = username
                session['role'] ='gardener'

                return render_template('register.html', username=username,email=email)
        
        else:

            username = session['username']
            firstname= request.form.get('firstname')
            lastname = request.form.get('lastname')
            email = request.form.get('email')
            phone = request.form.get('phone')
            address = request.form.get('address')

            cursor = getCursor()
            cursor.execute(f"""insert into gardener (first_name, last_name, email, phone_number,address,date_joined, status, username)
                         values ('{firstname}','{lastname}','{email}','{phone}','{address}',CURDATE(),'active','{username}');
                         """)
            connection.commit()

            return redirect(url_for('home',username=username))

    return render_template('register.html', msg=msg)

@app.route("/home")
def home():
   
   if 'loggedin' in session:
       username = session['username']
       role = session['role']
       return render_template("home.html",role=role,username=username)

   return render_template('base.html')


@app.route("/profile", methods=['GET', 'POST'])
def profile():

    if 'loggedin' in session:
        username = session['username']
        role = session['role']

        if role != 'gardener':
            cursor = getCursor()
            cursor.execute('SELECT * FROM employee WHERE username = %s', (username,))
            # Fetch one record and return result
            details = cursor.fetchone()
        else:
            cursor = getCursor()
            cursor.execute('SELECT * FROM gardener WHERE username = %s', (username,))
            # Fetch one record and return result
            details = cursor.fetchone()

        if request.method == 'GET':
            return render_template("profile.html",role=role, details=details,username=username)


        if request.method =='POST':

            if request.form.get('curpassword'):
                msgPassword=''
                curpassword = request.form.get('curpassword')
                hashed = hashing.hash_value(curpassword, salt='abcd')

                newPassword = request.form.get('newpassword')
                confirmPassword = request.form.get('conpassword')

                cursor = getCursor()
                cursor.execute('SELECT password FROM account WHERE username = %s', (username,))
                # Fetch one record and return result
                oldPassword = cursor.fetchone()[0]
                
                if hashed == oldPassword:
                    
                    if newPassword != confirmPassword:
                        msgPassword = 'New password and confirmed password should be same'
                        return render_template("profile.html",role=role, details=details,username=username,msgPassword=msgPassword)
                    else:
                        
                        hasedNewPassword = hashing.hash_value(newPassword, salt='abcd')

                        cursor.execute( f"""update account set password = '{hasedNewPassword}' where username = '{username}';""")
                        connection.commit()
                        
                        msgPassword ='Password updated successfully!'

                        return render_template("profile.html",role=role, details=details,username=username,msgPassword=msgPassword)
                else:
                    msgPassword = 'Current Password is not correct!'
                    return render_template("profile.html",role=role, details=details,username=username,msgPassword=msgPassword)

            else:

                firstname = request.form.get('firstname')
                lastname = request.form.get('lastname')
                email = request.form.get('email')
                phone = request.form.get('phone')
                address = request.form.get('address')

                if role =='gardener':
                    cursor.execute( f"""update gardener set first_name = '{firstname}', last_name = '{lastname}', email = '{email}', phone_number ='{phone}' ,address = '{address}' where username = '{username}';""")
                    connection.commit()
                    cursor.execute( f"""update account set email = '{email}' where username = '{username}';""")
                    connection.commit()
    
                else: 
                    cursor.execute( f"""update employee set first_name = '{firstname}', last_name = '{lastname}', email = '{email}', work_phone_number ='{phone}' where username = '{username}'; """)
                    connection.commit()
                    cursor.execute( f"""update account set email = '{email}' where username = '{username}';""")
                    connection.commit()
                    
                details = ['',firstname,lastname,email,phone,address]
                msgInfo = 'information updated successfully!'

                return render_template('profile.html',details=details,role=role,username=username,msgInfo=msgInfo)

    return render_template('base.html')


@app.route("/gardeners")
def gardeners():

    if 'loggedin' in session:

         if request.method == 'GET':
            role = session['role']

            cursor = getCursor()
            cursor.execute('SELECT * FROM gardener')
            # Fetch one record and return result
            gardeners = cursor.fetchall()  

    
            return render_template('information.html',role=role,gardeners=gardeners)
    
    return render_template('base.html')
    
    
@app.route("/staff")
def staff():

     if 'loggedin' in session:

        if request.method == 'GET':
            cursor = getCursor()
            cursor.execute(f"""SELECT * FROM employee where (username != 'admin' or username is NULL) order by staff_id""")
            # Fetch one record and return result
            staff = cursor.fetchall()


            return render_template('information.html',staffs=staff)
    
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
         
