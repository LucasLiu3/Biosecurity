
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



@app.route("/")
def base():
    return render_template("base.html")


@app.route('/login', methods=['GET', 'POST'])
def login():

    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        user_password = request.form['password']

        cursor = getCursor()
        cursor.execute('SELECT * FROM account WHERE username = %s', (username,))
        account = cursor.fetchone()
    
        if account is not None:
            password = account[2]
            role=account[4]
            if hashing.check_value(password, user_password, salt='abcd'):
                session['loggedin'] = True
                session['username'] = account[1]
                session['role'] =role
                return redirect(url_for('home'))
            else:
                msg = 'Incorrect password!'
        else:
            msg = 'Incorrect username'
    return render_template('base.html', msg=msg)

@app.route('/logout')
def logout():
   session.pop('loggedin', None)
   session.pop('username', None)
   return redirect(url_for('login'))


# http://localhost:5000/register - this will be the registration page, we need to use both GET and POST requests
@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST':

        if 'username' in request.form and 'password' in request.form and 'email' in request.form:
            username = request.form['username']
            password = request.form['password']
            email = request.form['email']
            cursor = getCursor()
            cursor.execute('SELECT * FROM account WHERE username = %s', (username,))
            account = cursor.fetchone()
            if account:
                msg = 'Account already exists!'
            elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                msg = 'Invalid email address!'
            elif not re.match(r'[A-Za-z0-9]+', username):
                msg = 'Username must contain only characters and numbers!'
            elif not username or not password or not email:
                msg = 'Please fill out the form!'
            else:
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

            return redirect(url_for('home'))

    return render_template('register.html', msg=msg)




