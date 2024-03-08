
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


# 
@app.route("/")
def base():
    return render_template("base.html")


# http://localhost:5000/login - this will be the login page, we need to use both GET and POST requests
@app.route('/login', methods=['GET', 'POST'])
def login():

    msg = ''

    # if the request is Post and the username and password have been input by user, system would check their input data with data in database to check the authentication of this username
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        user_password = request.form['password']
        
        # based on username input by user to fecth the data of this username from database
        cursor = getCursor()
        cursor.execute('SELECT * FROM account WHERE username = %s', (username,))
        account = cursor.fetchone()
    
        # if username exits, then check the password is correct or not.
        if account is not None:
            password = account[2]
            role=account[4]

            # if the input password and password in database are matched in hasing method,
            # then session would store the loggedin, username, role for this username, and redirct to home page.
            if hashing.check_value(password, user_password, salt='abcd'):
                session['loggedin'] = True
                session['username'] = account[1]
                session['role'] =role
                return redirect(url_for('home'))
            
            # if password is incrorrect, will create the error message
            else:
                msg = 'Incorrect password!'

        # if username is incrorrect, will create the error message
        else:
            msg = 'Incorrect username'

    # when the request method is GET or if the usernmame is not exit or the password is incorrect, then going to the login page and show the error message.
    return render_template('base.html', msg=msg)


# http://localhost:5000/logout, session would delete the loggedin, username and role, and redirect to login page.
@app.route('/logout')
def logout():
   session.pop('loggedin', None)
   session.pop('username', None)
   session.pop('role', None)
   return redirect(url_for('login'))


# http://localhost:5000/register - this will be the registration page, we need to use both GET and POST requests
@app.route('/register', methods=['GET', 'POST'])
def register():

    msg = ''

    # when request method is POST situation
    if request.method == 'POST':
        
        # in the POST method, if user has input the username,password,email and submit the form
        # system will goes into this process
        if 'username' in request.form and 'password' in request.form and 'email' in request.form:
            username = request.form['username']
            password = request.form['password']
            email = request.form['email']

            # based on the username input by user to fetch the data about this username from database.
            cursor = getCursor()
            cursor.execute('SELECT * FROM account WHERE username = %s', (username,))
            account = cursor.fetchone()

            pattern = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$')

            # if username exits, then create the error message 
            if account:
                msg = 'Account already exists!'
            
            # if email does not meet the standard, then creat the error message
            elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                msg = 'Invalid email address!'

            # if username does not meet the standard, then will create the error message
            elif not re.match(r'[A-Za-z0-9]+', username):
                msg = 'Username must contain only characters and numbers!'

            # if user does not fill any detail about the register, then will create the error message
            elif not username or not password or not email:
                msg = 'Please fill out the form!'

            # if password does not meet the input standard, then will create  the error message. 
            elif len(password) <8 and not re.match(pattern,password):
                msg = 'Password should be 8 characters long and different character types'

            # if all standards are met and username is not exit, then hashing the password of this username
            # and in accout table, insert the new data for this usernmae
            # last, session stores the loggedin, username, role(as a new gardener the role would be gardener), then going to register page for personal detail input. 
            else:
                hashed = hashing.hash_value(password, salt='abcd')
                cursor.execute('INSERT INTO account (username, password, email) VALUES (%s, %s, %s)', (username, hashed, email,))
                connection.commit()
                session['loggedin'] = True
                session['username'] = username
                session['role'] ='gardener'

                return render_template('register.html', username=username,email=email)
        
        # if system does not receive any request, then will going to personal detail register page.  
        else:


            username = session['username']
            firstname= request.form.get('firstname')
            lastname = request.form.get('lastname')
            email = request.form.get('email')
            phone = request.form.get('phone')
            address = request.form.get('address')

            # system will collect details about this username, and in gardener table in database inserting new data about this username
            # last redirect to home page. 
            cursor = getCursor()
            cursor.execute(f"""insert into gardener (first_name, last_name, email, phone_number,address,date_joined, status, username)
                         values ('{firstname}','{lastname}','{email}','{phone}','{address}',CURDATE(),'active','{username}');
                         """)
            connection.commit()

            return redirect(url_for('home'))
    
    # When request method is GET, then going to register page directly.
    return render_template('register.html', msg=msg)




