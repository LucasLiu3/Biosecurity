
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

# http://localhost:5000/home/ - this will be the home page, we need GET method.

@app.route("/home")
def home():

   if 'loggedin' in session:
       username = session['username']
       role = session['role']
       
       #based on the role, the home page would show different function buttons
       return render_template("home.html",role=role,username=username)

   return render_template('base.html')



# http://localhost:5000/profile/ - this will be the profile page, we need GET and POST methods.
@app.route("/profile", methods=['GET', 'POST'])
def profile():


    if 'loggedin' in session:
        username = session['username']
        role = session['role']


        if role != 'gardener':
            # fetch staff detail from employee table
            cursor = getCursor()
            cursor.execute('SELECT * FROM employee WHERE username = %s', (username,))
            details = cursor.fetchone()
        else:
            # fetch gardener detail from gardener table
            cursor = getCursor()
            cursor.execute('SELECT * FROM gardener WHERE username = %s', (username,))
            details = cursor.fetchone()

        # in GET method
        if request.method == 'GET':
            
            # going to profile update page.
            return render_template("profile.html",role=role, details=details,username=username)


        # in POST method
        if request.method =='POST':
            
            # if request includes curpassword means the user is chaning his password
            if request.form.get('curpassword'):
                msgPassword=''

                # collect input data from profile update page, and hashing it.
                curpassword = request.form.get('curpassword')
                hashed = hashing.hash_value(curpassword, salt='abcd')

                # collect newpassword and confirmpassword from submitted form
                newPassword = request.form.get('newpassword')
                confirmPassword = request.form.get('conpassword')

                # based on username, collect his old hashed password from database
                cursor = getCursor()
                cursor.execute('SELECT password FROM account WHERE username = %s', (username,))
                oldPassword = cursor.fetchone()[0]
                
                # compare input hashed password with hashed password in database
                if hashed == oldPassword:
                    
                    # if hased passwords are matched, then compare the input new password and input confirmed password
                    if newPassword != confirmPassword:

                        # if those passwords are not matched, then create error passage and goes back to profile update page.
                        msgPassword = 'New password and confirmed password should be same'
                        return render_template("profile.html",role=role, details=details,username=username,msgPassword=msgPassword)
                    else:

                        # if those passwords are matched, then hashed the new password
                        # and in accout table, update the username's password with new hased password
                        # last create successful message and go to profile update page.
                        hasedNewPassword = hashing.hash_value(newPassword, salt='abcd')

                        cursor.execute( f"""update account set password = '{hasedNewPassword}' where username = '{username}';""")
                        connection.commit()
                        
                        msgPassword ='Password updated successfully!'

                        return render_template("profile.html",role=role, details=details,username=username,msgPassword=msgPassword)
                else:

                    # if hased passwords are not matched, then create error message and gose back to profile update page.
                    msgPassword = 'Current Password is not correct!'
                    return render_template("profile.html",role=role, details=details,username=username,msgPassword=msgPassword)
                
            # if request does not include curpassword, then going to personal detail update part
            else:

                # collect personal new detail input from submitted form
                firstname = request.form.get('firstname')
                lastname = request.form.get('lastname')
                email = request.form.get('email')
                phone = request.form.get('phone')
                address = request.form.get('address')

                # if role is gardener, then in gardener table, update the new detail for the username
                if role =='gardener':
                    cursor.execute( f"""update gardener set first_name = '{firstname}', last_name = '{lastname}', email = '{email}', phone_number ='{phone}' ,address = '{address}' where username = '{username}';""")
                    connection.commit()
                    cursor.execute( f"""update account set email = '{email}' where username = '{username}';""")
                    connection.commit()

                # if role is staff, then in employee table, update the new detail for the username
                else: 
                    cursor.execute( f"""update employee set first_name = '{firstname}', last_name = '{lastname}', email = '{email}', work_phone_number ='{phone}' where username = '{username}'; """)
                    connection.commit()
                    cursor.execute( f"""update account set email = '{email}' where username = '{username}';""")
                    connection.commit()
                    
                details = ['',firstname,lastname,email,phone,address]
                msgInfo = 'Information updated successfully!'

                # going back to profile update page, showing the new detail and successful message.
                return render_template('profile.html',details=details,role=role,username=username,msgInfo=msgInfo)

    return render_template('base.html')