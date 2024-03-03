
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
            details = cursor.fetchone()
        else:
            cursor = getCursor()
            cursor.execute('SELECT * FROM gardener WHERE username = %s', (username,))
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
                msgInfo = 'Information updated successfully!'

                return render_template('profile.html',details=details,role=role,username=username,msgInfo=msgInfo)

    return render_template('base.html')