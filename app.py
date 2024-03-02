import os
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
         


@app.route("/guide")
def guide():

    cursor = getCursor()
    cursor.execute(f"""select * from weed """)
    weeds = cursor.fetchall()
    role=session['role']
    newWeeds = []
    for weed in weeds:

        weed= list(weed)
        newWeeds.append(weed)

    for newWeed in newWeeds:
        newWeed[-1] = newWeed[-1].split(',')

    return render_template('weed.html',weeds=newWeeds,role=role)


@app.route("/guide/detail/<id>")
def detail(id):

    role = session['role']
    cursor = getCursor()
    cursor.execute(f"""select * from weed where weed_id = {id}""")
    weed = cursor.fetchone()

    if weed[4].startswith('d') and weed[5].startswith('i') and weed[6].startswith('c'):
        impactFile = f'./static/weeds/{weed[1]}/{weed[5]}'
        with open(impactFile,'r') as file:
            impact = file.read()

        descriptionFile = f'./static/weeds/{weed[1]}/{weed[4]}'
        with open(descriptionFile,'r') as file:
            description = file.read()

        controlFile = f'./static/weeds/{weed[1]}/{weed[6]}'
        with open(controlFile,'r') as file:
            control = file.read()
        
        imagefile = weed[-1].split(',')

        return render_template('weedDetail.html',role=role,weed=weed,impact=impact,description=description,control=control,imagefile=imagefile)

    else:
        imagefile = weed[-1].split(',')
        return render_template('weedDetail.html',role=role,weed=weed,imagefile=imagefile)


@app.route("/guide/add",methods=['POST','GET'])
def guideAdd():

    if request.method=='GET':

        return render_template('weedAdd.html')
    
    if request.method == 'POST':

        common_name = request.form.get('commonname')
        weed_type = request.form.get('type')
        scientific_name = request.form.get('scientific')
        description = request.form.get('description')
        impacts = request.form.get('impacts')
        control_methods = request.form.get('control')

     
        new_folder_path = os.path.join('static', 'weeds', common_name)
        os.makedirs(new_folder_path, exist_ok=True)

        image_folder_path = os.path.join('static', 'weeds', common_name,'images')
        os.makedirs(image_folder_path, exist_ok=True)

        uplaoded_images = request.files.getlist('images')

        image_str = ''
        for image in uplaoded_images:
            image.save(os.path.join(image_folder_path,image.filename))
            if image_str:
                image_str+= ',' + image.filename
            else:
                image_str += image.filename

        cursor = getCursor()
        cursor.execute(f"""insert into weed (common_name, weed_type, scientific_name, description,impacts,control_methods,images)
                         values ('{common_name}','{weed_type}','{scientific_name}','{description}','{impacts}','{control_methods}','{image_str}');
                         """)
        connection.commit()

        return redirect(url_for('guide'))
    

@app.route("/guide/update/<id>",methods=['POST','GET'])
def guideUpdate(id):

    cursor = getCursor()
    cursor.execute(f"""select * from weed where weed_id = {id} """)
    weed = cursor.fetchone()

    if request.method == 'GET':

        if weed[4].startswith('d') and weed[5].startswith('i') and weed[6].startswith('c'):
            impactFile = f'./static/weeds/{weed[1]}/{weed[5]}'
            with open(impactFile,'r') as file:
                impact = file.read()

            descriptionFile = f'./static/weeds/{weed[1]}/{weed[4]}'
            with open(descriptionFile,'r') as file:
                description = file.read()

            controlFile = f'./static/weeds/{weed[1]}/{weed[6]}'
            with open(controlFile,'r') as file:
                control = file.read()
            
            imagefile = weed[-1].split(',')

            return render_template('weedUpdate.html',weed=weed,impact=impact,description=description,control=control,imagefile=imagefile)

        else:
            imagefile = weed[-1].split(',')
            return render_template('weedUpdate.html',weed=weed,imagefile=imagefile)

        
    
    if request.method =='POST':
  

        common_name = request.form.get('commonname')
        weed_type = request.form.get('type')
        name = request.form.get('scientific')
        description = request.form.get('description')
        impacts = request.form.get('impacts')
        control = request.form.get('control')
        image = request.form.get('image')


        old_fold = f'./static/weeds/{weed[1]}'
        new_fold = f'./static/weeds/{common_name}'
        if os.path.exists(old_fold):
            os.rename(old_fold, new_fold)
        
        imagefile = weed[-1].split(',')
        imagefile.remove(image)
        imagefile.insert(0,image)

        images = ','.join(imagefile)

        
        cursor = getCursor()
        cursor.execute(f"""UPDATE weed 
                    SET common_name = '{common_name}',
                        weed_type = '{weed_type}',
                        scientific_name = '{name}', 
                        description = '{description}',
                        impacts = '{impacts}',
                        control_methods ='{control}',
                        images ='{images}'
                    WHERE weed_id = '{id}'""")
        connection.commit()

        return redirect(url_for(f'detail',id=id))
    
@app.route("/guide/delete/<id>",methods=['POST','GET'])
def guideDelete(id):

    cursor = getCursor()
    cursor.execute(f"""delete from weed where weed_id ='{id}'""")
    connection.commit()
    return redirect(url_for('guide'))