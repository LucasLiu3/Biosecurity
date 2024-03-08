

from app import app
import os
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

# http://localhost:5000/guide - this will be the guide list page, we need GET method.
@app.route("/guide")
def guide():

    # fetch all data about weeds from database
    cursor = getCursor()
    cursor.execute(f"""select * from weed """)
    weeds = cursor.fetchall()

    # based on the role, weed detail page would shoud different function buttons
    role=session['role']

    # rewrite the weed data
    newWeeds = []
    for weed in weeds:

        weed= list(weed)
        newWeeds.append(weed)

    for newWeed in newWeeds:
        newWeed[-1] = newWeed[-1].split(',')

    return render_template('weed.html',weeds=newWeeds,role=role)

# http://localhost:5000/guide/detail/<id> - this will be the each weed detail page, we need GET method.
@app.route("/guide/detail/<id>")
def detail(id):

    role = session['role']

    #based on the id of the weed from route, fetch data of this weed from database.
    cursor = getCursor()
    cursor.execute(f"""select * from weed where weed_id = {id}""")
    weed = cursor.fetchone()

    # the intial data about the weed contains text files of their description,impact,comtrol method information
    # system would read those files and render to weed detail page
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

    # for those new added weed information, this could render those information from database in weed detail page.
    else:
        imagefile = weed[-1].split(',')
        return render_template('weedDetail.html',role=role,weed=weed,imagefile=imagefile)

# http://localhost:5000/guide/add - this is the adding new weed detail page, we need GET and POST method.
@app.route("/guide/add",methods=['POST','GET'])
def guideAdd():

    # if the request method is GET, then just show the add new weed page.
    if request.method=='GET':

        return render_template('weedAdd.html')
    

    # if the request method is POST
    if request.method == 'POST':
        
        # collect new weed information from submitted form
        common_name = request.form.get('commonname')
        weed_type = request.form.get('type')
        scientific_name = request.form.get('scientific')
        description = request.form.get('description')
        impacts = request.form.get('impacts')
        control_methods = request.form.get('control')

        # create a new fold for this new weed
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

        # in the weed table in database, insert a new data for this added new weed.
        cursor = getCursor()
        cursor.execute(f"""insert into weed (common_name, weed_type, scientific_name, description,impacts,control_methods,images)
                         values ('{common_name}','{weed_type}','{scientific_name}','{description}','{impacts}','{control_methods}','{image_str}');
                         """)
        connection.commit()

        return redirect(url_for('guide'))
    
# http://localhost:5000/guide/update/<id> - this is the update weed detail page, we need GET and POST method.
@app.route("/guide/update/<id>",methods=['POST','GET'])
def guideUpdate(id):

    # fetch the data of the id provied by route
    cursor = getCursor()
    cursor.execute(f"""select * from weed where weed_id = {id} """)
    weed = cursor.fetchone()

    # if the request method is GET
    if request.method == 'GET':

        # if the data is initial data , then read files for this weed
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

        # if the data is new added weed, then just going to update weed page
        else:
            imagefile = weed[-1].split(',')
            return render_template('weedUpdate.html',weed=weed,imagefile=imagefile)

        
    # if the request method is POST
    if request.method =='POST':
  
        # collect input information from submitted form 
        common_name = request.form.get('commonname')
        weed_type = request.form.get('type')
        name = request.form.get('scientific')
        description = request.form.get('description')
        impacts = request.form.get('impacts')
        control = request.form.get('control')
        image = request.form.get('image')

        #change the contents in the fold for this weed
        old_fold = f'./static/weeds/{weed[1]}'
        new_fold = f'./static/weeds/{common_name}'
        if os.path.exists(old_fold):
            os.rename(old_fold, new_fold)
        
        imagefile = weed[-1].split(',')
        imagefile.remove(image)
        imagefile.insert(0,image)

        images = ','.join(imagefile)

        # in weed database, update the new input information for this weed.
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
    
# http://localhost:5000/guide/delete/<id> - this is the delete weed page, we need GET and POST method.

@app.route("/guide/delete/<id>",methods=['POST','GET'])
def guideDelete(id):

    cursor = getCursor()
    cursor.execute(f"""delete from weed where weed_id ='{id}'""")
    connection.commit()

    
    return redirect(url_for('guide'))