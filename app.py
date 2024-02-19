from flask import Flask
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

app = Flask(__name__)

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
def home():
    return render_template("base.html")




@app.route("/Administrator")
def Administrator():
    return render_template("Administrator_Interface.html")

@app.route("/Junior")
def Junior():
    sql = """
            select d1.driver_id,d1.first_name,d1.surname, d1.date_of_birth,d1.age, ifnull(concat(d2.first_name,' ',d2.surname),'') as caregiver
            from driver as d1 left join driver as d2
            on d1.caregiver = d2.driver_id
            where d1.age between 12 and 25
            order by age desc, surname
            """
    connection = getCursor()
    connection.execute(sql)
    junior = connection.fetchall()
    return render_template("Junior.html",junior_list = junior)



@app.route("/DriverSearch")
def DriverSearch():
   return render_template("DriverSearch.html")


@app.route("/searchdetail",methods=['POST'])
def searchdetail():

    drivername = request.form.get('searchname')

    if drivername:

        sql = f"""select d.driver_id,surname,first_name ,
                c.model, c.drive_class,
                cs.name as course_name, r.run_num,
                r.seconds,
                case when r.cones = 0 then ' '
                when r.cones is Null then ' '
                else r.cones end,
                case when r.wd =0 then '' else 'wd' end,
                round((r.seconds+ifnull(r.cones,0)*5+ifnull(r.wd,0)*10),2) as total_time
                from driver as d 
                left join car as c on d.car = c.car_num
                left join run as r on d.driver_id = r.dr_id
                left join course as cs on r.crs_id = cs.course_id
                where surname like '%{drivername}%' or first_name like '%{drivername}%'"""
        
        connection = getCursor()
        connection.execute(sql)
        rundetail = connection.fetchall()

        
        driverdetail = f"""select driver_id,first_name,surname,model,drive_class
                       from driver as d 
                       left join car as c on d.car = c.car_num
                       where surname like '%{drivername}%' or first_name like '%{drivername}%'
                       """
        connection = getCursor()
        connection.execute(driverdetail)
        driverdetail = connection.fetchall()
        return render_template("Namesearch.html",run_detail =rundetail,driver_detail = driverdetail)
    
    else:
        rundetail = []
        return render_template("Namesearch.html",run_detail =rundetail)




@app.route("/Edit")
def Edit():
    id = """
            SELECT driver_id,first_name,surname FROM driver;
          """
    courseid = """
               Select course_id from course;
               """
    runnum = """
               select distinct run_num from run;
             """
    
    connection = getCursor()
    connection.execute(id)
    idList = connection.fetchall()

    connection = getCursor()
    connection.execute(courseid)
    courseList = connection.fetchall()

    connection = getCursor()
    connection.execute(runnum)
    runnum = connection.fetchall()

    return render_template("Edit.html",id_list = idList,course_list=courseList,run_num=runnum)


@app.route("/Editdetail",methods=['POST'])
def Editdetail():

    driverid = request.form.get('driverid')
    courseid = request.form.get('courseid')
    runnum = request.form.get('runnum')
    
    sql = f"""select ifnull(seconds,0),ifnull(cones,0),wd from run
             where dr_id ={driverid} and crs_id = "{courseid}" and run_num = {runnum}
          """
    connection = getCursor()
    connection.execute(sql)
    detail = connection.fetchall()

    name = f"""select first_name,surname FROM driver
             where driver_id ={driverid} 
          """
    connection = getCursor()
    connection.execute(name)
    name = connection.fetchall()

    return render_template("Editdetail.html",run_detail = detail,driverid=driverid,name=name,courseid=courseid,runnum=runnum)


@app.route("/Editruns",methods=['POST'])
def Editruns():
    driverid = request.form.get('driverid')
    courseid = request.form.get('courseid')
    runnum = request.form.get('runnum')
    newtime = request.form.get('newtime')
    newcone = request.form.get('newcone') 
    newwd = request.form.get('newwd') 
    
    sql = f"""
          update run set seconds = {newtime},
          cones = {newcone}, wd = {newwd}
          where dr_id ={driverid} and crs_id = "{courseid}" and run_num = {runnum}
          """
    connection = getCursor()
    connection.execute(sql)
   
    sql1 =  f"""select dr_id,first_name,surname, crs_id,run_num,
                seconds,cones,wd from run
                left join driver on run.dr_id =driver.driver_id
                where dr_id ={driverid} and crs_id = "{courseid}" and run_num = {runnum}
           """
    
    connection = getCursor()
    connection.execute(sql1)
    editresult = connection.fetchall()
    return render_template("Editruns.html",edit_result = editresult)




@app.route("/Add")      
def Add():
    car = """
            select car_num,model,drive_class drive_class from car
          """
    
    connection = getCursor()
    connection.execute(car)
    carList = connection.fetchall()
    
    max_date = (datetime.today() -timedelta(days=(12 * 365)+3)).strftime('%Y-%m-%d')
    min_date = (datetime.today() -timedelta(days=((26 * 365)+5))).strftime('%Y-%m-%d')

    return render_template("Add.html",car_list =carList, maxdate= max_date,mindate=min_date)


@app.route("/Adddriver",methods=['POST'])  
def Adddriver():

  
    firstname = request.form.get('firstname')
    surname = request.form.get('surname')
    birthdate= request.form.get('birthdate')
    caregiver = request.form.get('caregiver')
    carclass = request.form.get('carclass')
    Age = request.form.get('age')

    rundetail = f"""select distinct crs_id,run_num from run"""
    connection = getCursor()
    connection.execute(rundetail)
    rundetail = connection.fetchall()

    if firstname and surname and birthdate:

        if Age and int(Age) >16:


                sql= f"""insert into driver (first_name,surname,date_of_birth,age,car)
                    values ('{firstname}','{surname}','{birthdate}',{Age},{carclass})
                """
            
                connection = getCursor()
                connection.execute(sql)
                

                idsql= f"""select driver_id from driver where  first_name = '{firstname}' and surname = '{surname}'"""
                connection = getCursor()
                connection.execute(idsql)
                newid = connection.fetchall()
                newid = int(newid[-1][-1])
                newrun =   f"""
                            insert into run (dr_id,crs_id,run_num,seconds,cones,wd)
                            values ({newid},'A',1,NULL,NULL,0),({newid},'A',2,NULL,NULL,0),
                            ({newid},'B',1,NULL,NULL,0),({newid},'B',2,NULL,NULL,0),
                            ({newid},'C',1,NULL,NULL,0),({newid},'C',2,NULL,NULL,0),
                            ({newid},'D',1,NULL,NULL,0),({newid},'D',2,NULL,NULL,0),
                            ({newid},'E',1,NULL,NULL,0),({newid},'E',2,NULL,NULL,0),
                            ({newid},'F',1,NULL,NULL,0),({newid},'F',2,NULL,NULL,0);
                            """
                
                connection = getCursor()
                connection.execute(newrun)
            
                new = f"""select * from driver where first_name = '{firstname}' and surname = '{surname}'"""

                connection = getCursor()
                connection.execute(new)
                add = connection.fetchall()

                return render_template("Adddriver.html",add_list =add,run_detail= rundetail)

        elif Age and (12<=int(Age)<=16):

                sql= f"""insert into driver (first_name,surname,date_of_birth,age,caregiver,car)
                    values ('{firstname}','{surname}','{birthdate}',{Age},{caregiver},{carclass})
                """
            
                connection = getCursor()
                connection.execute(sql)
                

                idsql= f"""select driver_id from driver where  first_name = '{firstname}' and surname = '{surname}'"""
                connection = getCursor()
                connection.execute(idsql)
                newid = connection.fetchall()
                newid = int(newid[-1][-1])
                newrun =   f"""
                            insert into run (dr_id,crs_id,run_num,seconds,cones,wd)
                            values ({newid},'A',1,NULL,NULL,0),({newid},'A',2,NULL,NULL,0),
                            ({newid},'B',1,NULL,NULL,0),({newid},'B',2,NULL,NULL,0),
                            ({newid},'C',1,NULL,NULL,0),({newid},'C',2,NULL,NULL,0),
                            ({newid},'D',1,NULL,NULL,0),({newid},'D',2,NULL,NULL,0),
                            ({newid},'E',1,NULL,NULL,0),({newid},'E',2,NULL,NULL,0),
                            ({newid},'F',1,NULL,NULL,0),({newid},'F',2,NULL,NULL,0);
                            """
                
                connection = getCursor()
                connection.execute(newrun)
            
                new = f"""select * from driver where first_name = '{firstname}' and surname = '{surname}'"""

                connection = getCursor()
                connection.execute(new)
                add = connection.fetchall()

                return render_template("Adddriver.html",add_list =add,run_detail= rundetail)

        else:
            birthday = datetime.strptime(birthdate,"%Y-%m-%d")
            current_date = datetime.now()
            age = current_date.year - birthday.year - ((current_date.month, current_date.day) < (birthday.month, birthday.day))
            
            birthdate = datetime.strptime(birthdate,"%Y-%m-%d").date()

            carsql = """
                select car_num,model,drive_class drive_class from car
            """

            connection = getCursor()
            connection.execute(carsql)
            carList = connection.fetchall()

            caregiversql = """
                        select driver_id, first_name,surname from driver
                        where age is null
                        """
            connection = getCursor()
            connection.execute(caregiversql)
            caregiverlist = connection.fetchall()

            return render_template("AddAge.html",First_name=firstname,Surname=surname,Birthday= birthdate,age=age,caregiver_list=caregiverlist,car_list=carList)


    elif firstname and surname and carclass:

        sql = f"""insert into driver (first_name,surname,car)
                 values ('{firstname}','{surname}','{carclass}')
              """
        connection = getCursor()
        connection.execute(sql)

        
        idsql= f"""select driver_id from driver where  first_name = '{firstname}' and surname = '{surname}'"""
        connection = getCursor()
        connection.execute(idsql)
        newid = connection.fetchall()
    
        newid = int(newid[-1][-1])  
        
        newrun =   f"""
                    insert into run (dr_id,crs_id,run_num,seconds,cones,wd)
                    values ({newid},'A',1,NULL,NULL,0),({newid},'A',2,NULL,NULL,0),
                    ({newid},'B',1,NULL,NULL,0),({newid},'B',2,NULL,NULL,0),
                    ({newid},'C',1,NULL,NULL,0),({newid},'C',2,NULL,NULL,0),
                    ({newid},'D',1,NULL,NULL,0),({newid},'D',2,NULL,NULL,0),
                    ({newid},'E',1,NULL,NULL,0),({newid},'E',2,NULL,NULL,0),
                    ({newid},'F',1,NULL,NULL,0),({newid},'F',2,NULL,NULL,0);
                    """
        
        connection = getCursor()
        connection.execute(newrun)

        new = f"""select * from driver where first_name = '{firstname}' and surname = '{surname}'"""
        connection = getCursor()
        connection.execute(new)
        add = connection.fetchall()
        
        return render_template("Adddriver.html",add_list =add,run_detail= rundetail)
        


@app.route("/Driver")
def Driver():
    return render_template("Driver_Interface.html")

@app.route("/listcourses")
def listcourses():
    connection = getCursor()
    connection.execute("SELECT * FROM course;")
    courseList = connection.fetchall()
    return render_template("courselist.html", course_list = courseList)


@app.route("/Search")
def Search():
    connection = getCursor()
    connection.execute("SELECT driver_id,concat(first_name,' ',surname) FROM driver;")
    drivername = connection.fetchall()
    return render_template("Search.html",driver_name = drivername)

@app.route("/listdrivers")
def listdrivers():
    sql  ="""
            select d.driver_id, d.first_name, d.surname,ifnull(date_of_birth,''), ifnull(d.age,''),ifnull(d.caregiver,''),c.model, c.drive_class 
            from driver as d left join car as c 
            on d.car = c. car_num 
            order by surname,first_name;
            """
    connection = getCursor()
    connection.execute(sql)
    driverList = connection.fetchall()
   
    return render_template("driverlist.html", driver_list = driverList)   

@app.route("/rundetail",methods=['POST','GET'])
def rundetail():
    Search = request.form.get('drivername')
    listdrivers = request.args.get('driverid')

    if Search:                 
        sql = f"""select d.driver_id,first_name,surname,
                c.model, c.drive_class,
                cs.name as course_name, r.run_num,r.seconds,
                case when r.cones = 0 then ' '
                when r.cones is Null then ' '
                else r.cones end,
                case when r.wd =0 then '' else 'wd' end,
                round((r.seconds+ifnull(r.cones,0)*5+ifnull(r.wd,0)*10),2) as total_time
                from driver as d 
                left join car as c on d.car = c.car_num
                left join run as r on d.driver_id = r.dr_id
                left join course as cs on r.crs_id = cs.course_id
                where d.driver_id = {Search};"""
        connection = getCursor()
        connection.execute(sql)
        rundetail = connection.fetchall()

        connection = getCursor()
        connection.execute("SELECT driver_id,concat(first_name,' ',surname) FROM driver;")
        drivername = connection.fetchall()

        driverdetail = f"""select driver_id,first_name,surname,model,drive_class
                       from driver as d 
                       left join car as c on d.car = c.car_num
                       where driver_id = {Search};
                       """
        connection = getCursor()
        connection.execute(driverdetail)
        driverdetail = connection.fetchall()
        return render_template("Rundetail.html",run_detail =rundetail,driver_name = drivername,driver_dertail = driverdetail)
    
    elif listdrivers:
        sql = f"""select d.driver_id, first_name,surname,
                c.model, c.drive_class,
                cs.name as course_name, r.run_num,r.seconds,
                case when r.cones = 0 then ' '
                when r.cones is Null then ' '
                else r.cones end,
                case when r.wd =0 then '' else 'wd' end,
                round((r.seconds+ifnull(cones,0)*5+ifnull(r.wd,0)*10),2) as total_time
                from driver as d 
                left join car as c on d.car = c.car_num
                left join run as r on d.driver_id = r.dr_id
                left join course as cs on r.crs_id = cs.course_id
                where d.driver_id = {listdrivers}
                """
        connection = getCursor()
        connection.execute(sql)
        rundetail = connection.fetchall()

        driverdetail = f"""select driver_id,first_name,surname,model,drive_class
                       from driver as d 
                       left join car as c on d.car = c.car_num
                       where d.driver_id = {listdrivers}
                       """
        connection = getCursor()
        connection.execute(driverdetail)
        driverdetail = connection.fetchall()
        return render_template("Rundetail.html",run_detail =rundetail,driver_dertail = driverdetail)
 

@app.route("/overall")
def overall():
 
    sql = """select driver_id, case when age between 12 and 25 then concat(first_name,' ',surname,' (J)') else concat(first_name,' ',surname) end,
            model
            from driver left join car on driver.car = car.car_num"""
    
    sql1= """
            with overall_a as (
            select *, row_number() over(partition by dr_id,crs_id order by case when run_total is null then 2 else 1 end, run_total) as ranking
            from (select dr_id,crs_id,round((seconds+ifnull(cones,0)*5+ifnull(wd,0)*10),2) as run_total
            from run
            order by dr_id,crs_id,run_total) as a 
            )

            select dr_id,round(run_total,2) as course_time from overall_a
            where  ranking = 1
          """
    
    connection = getCursor()
    connection.execute(sql)
    name = connection.fetchall()
    
    connection = getCursor()
    connection.execute(sql1)
    run = connection.fetchall()

    overall = []

    for people in name:
        people = list(people)

        for item in run:
            item = list(item)
            if people[0] == item[0]:
                if item[1] is None:
                    people.append('dnf')
                else:
                    people.append(item[1])

        overall.append(people)
       

    for each in overall:
        sublist= each[3:9]
        total = 0
        for num in sublist:
            if num != 'dnf':
                total+=num
            else:
                total = "NQ"
                break
            total = round(total,2)
        each.append(total)
    
    overall = sorted(overall, key=lambda x: float('inf') if isinstance(x[-1], str) else x[-1])
    
 
    for index, value in enumerate(overall):
        if index == 0:
             value.append('Cup')
        elif 1<=index<=4:   
             value.append("Prize")
        else:
            value.append(" ")   

    return render_template("Overall.html",overall_list = overall)


@app.route("/graph")
def showgraph():

    sql = """with overall_a as (
            select *, row_number() over(partition by dr_id,crs_id order by case when run_total is null then 2 else 1 end, run_total) as ranking
            from (select dr_id,crs_id,round((seconds+ifnull(cones,0)*5+ifnull(wd,0)*10),2) as run_total
            from run
            order by dr_id,crs_id,run_total
            ) as a 
            where run_total is not null
            )

            select dr_id,first_name,surname,
            case when count(crs_id) =6 then round(sum(run_total),2) else 'NQ' end as overall_results from overall_a
            left join driver 
            on overall_a. dr_id = driver.driver_id
            where ranking =1
            group by dr_id
            order by overall_results
            limit 5;"""
                
    connection = getCursor()
    connection.execute(sql)
    overall_list = connection.fetchall()

    bestDriverList = []
    resultsList= []

    for item in overall_list:
        item= list(item)
        name = str(item[0]) + ' '+item[1] +' '+ item[2]+' '
        bestDriverList.append(name)
        resultsList.append(item[3])

    bestDriverList =bestDriverList[::-1]
    resultsList = resultsList[::-1]

    return render_template("top5graph.html", name_list = bestDriverList, value_list = resultsList)

