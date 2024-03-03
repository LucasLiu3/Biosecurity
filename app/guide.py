

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