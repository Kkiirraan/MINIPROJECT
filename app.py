from flask import Flask,request,render_template,redirect,jsonify,json,url_for,session,Response
from json import JSONDecodeError
from datetime import datetime
from jinja2.exceptions import TemplateNotFound
import mysql.connector
import bcrypt
import inspect
import traceback
import time


mydb=mysql.connector.connect(host="localhost",user="root",password="Kiranvijayan@2002",database="MINIPROJECT")
mycursor=mydb.cursor()
result=0


app=Flask(__name__)
app.secret_key = 'kiran'   
app.config['TEMPLATES_AUTO_RELOAD'] = True


@app.route('/')
def home():
    noallot = session.pop('noallot','')
    allot = session.pop('allot','')
    incorrectdate = session.pop('incorrectdate', '')
    return render_template('home.html',logged_in=False,incorrectdate=incorrectdate,allot=allot,noallot=noallot)


@app.route('/login',methods=['GET','POST'])
def login():
    noaccount = session.pop('noaccount', '')
   
    return render_template('login.html', logged_in=False,noaccount=noaccount)

@app.route('/dashboard',methods=['GET','POST'])
def dashboard():
    
    if 'id' in session:
        return render_template('dashboard.html', logged_in=True)
    else:
        return redirect(url_for('login'))
    
    
@app.route('/add',methods=['GET','POST'])
def add():
    roomadd=session.pop('roomadd','') 
    wrongdate = session.pop('wrongdate', '')
    if 'id' in session:
        return render_template('addroom.html', logged_in=True,wrongdate=wrongdate,roomadd=roomadd)
    else:
        return redirect(url_for('login'))

@app.route('/signin',methods=['GET','POST'])
def signin():
    doesnotmatch = session.pop('doesnotmatch', '')
    incorrectid= session.pop('incorrectid', '')
    incorrectdate= session.pop('incorrectdate','')
    accountalready=session.pop('accountalready','')
    
    return render_template('signup.html',doesnotmatch=doesnotmatch,incorrectid=incorrectid,incorrectdate=incorrectdate,accountalready=accountalready)

@app.route('/signup',methods=['GET','POST'])
def signup():

    if request.method=='POST':
        name=request.form.get('username')
        id=request.form.get('id')
        dob=request.form.get('dob')
        try:
           dob = datetime.strptime(dob, '%d-%m-%Y').strftime('%Y-%m-%d')
        except ValueError:
            session['incorrectdate'] = "Please enter the date in the format DD-MM-YYYY"
            return redirect('/signin')   
        
        
        phone=request.form.get('phone')
        email=request.form.get('email')
        password=request.form.get('password')
        confirm_password=request.form.get('confirm_password')
        fcolor=request.form.get('fcolor')
        bgroup=request.form.get('bgroup')
        siblings=request.form.get('siblings')
        cinema=request.form.get('cinema')
        if not name or not id or not dob or not phone or not fcolor or not bgroup or not siblings or not cinema or not email or not password or not confirm_password:
            return "not got the data"
        elif confirm_password != password:
            session['doesnotmatch'] = "Passwords do not match"
            return redirect('/signin')
        else:
            session.pop('doesnotmatch', None)
            try:
                 mycursor.execute('SELECT t_id FROM teachers_details WHERE t_name=%s AND t_dob=%s',(name,dob))
                 result=mycursor.fetchone()
                 mydb.commit()
            except mysql.connector.Error as e:
                return "Exception error: {}".format(e)
             
            if result is None or id != result[0]:
                session['incorrectid']="Sign in failed incorrect details"
                return redirect('/signin')
            else:
                 mycursor.execute('SELECT t_id FROM signup_details WHERE t_name=%s AND t_dob=%s',(name,dob))
                 result=mycursor.fetchone()
                 mydb.commit()
                 if result is None:
                   salts=bcrypt.gensalt()
                   hashed_password = bcrypt.hashpw(password.encode('utf-8'), salts)
                 
                   sql='INSERT INTO signup_details (t_id,t_name,t_dob,phone,email,password,color,bgroup,siblings,cinema) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
                   val=(id,name,dob,phone,email,hashed_password,fcolor,bgroup,siblings,cinema)
                 
                   mycursor.execute(sql,val)
                   mydb.commit()
                   
                   return render_template('signupsucess.html')
                 else:
                     session['accountalready']="Account already exist please login"
                     return redirect('/signin')  
          
@app.route('/log',methods=['GET','POST'])
def log():
    id=request.form.get('id')
    password=request.form.get('password').encode('utf-8')
    
    if not id or not password:
        return "not get data"
    
    try:
        mycursor.execute('SELECT t_id FROM signup_details WHERE t_id=%s',(id,))
        result=mycursor.fetchone()
        mydb.commit()
    except mysql.connector.Error as e:
                return "Exception error: {}".format(e)    
    if result is None or id != result[0]:
                session['noaccount']="YOU DOON'T HAVE AN ACCOUNT PLEASE SIGNUP FIRST"
                return redirect('/login')
    else:
                
        mycursor.execute('SELECT password from signup_details WHERE t_id=%s ',(id,))
        result=mycursor.fetchone()
        mydb.commit()
        if result:
             hashed_password = result[0].encode('utf-8')
             if bcrypt.checkpw(password, hashed_password):
                  session['id'] = id
                  return redirect(url_for('dashboard'))
                  
        
             else:
                 session['noaccount']="INCORRECT PASSWORD"
                 return redirect('/login')
                   
              
@app.route('/logout', methods=['POST'])
def logout():
    session.pop('id', None)
    return redirect((url_for('login')))                 

@app.route('/addroom', methods=['GET', 'POST'])
def addroom():
    response = Response()
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    if request.method == 'POST':
        exam_date = request.form.get('exam_date')
        exam_time = request.form.get('exam_time')
        mer = request.form.get('dropdown')
        dept = request.form.get('dept')
        no_room = request.form.get('no_room')
        no_bstd = request.form.get('no_bstd')
        no_bench = request.form.get('no_bench')
        tot_std = request.form.get('tot_std')

        if exam_date is None:
            session['wrongdate'] = "Please enter the date in the format DD-MM-YYYY"
            return redirect('/addroom')
        else:
            try:
               exam_date = datetime.strptime(exam_date, '%d-%m-%Y').strftime('%Y-%m-%d')
            except ValueError:
              session['wrongdate'] = "Please enter the date in the format DD-MM-YYYY"
              return redirect('/wrongedate')

            if not exam_date or not exam_time or not mer or not dept or not no_room or not no_bstd or not no_bench or not tot_std:
              return "Did not receive all the required data"
            else:
                
                 mycursor.execute('SELECT * FROM room_details WHERE e_date=%s AND mer=%s AND dept=%s AND room_no=%s',(exam_date,mer,dept,no_room,))
                 result=mycursor.fetchone()
                 mydb.commit()
                 if result is None:
                   status=0
                   sql = 'INSERT INTO room_details(e_date,e_time,mer,dept,room_no,std_bench,no_bench,tot_allot,status) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s);'
                   val = (exam_date, exam_time, mer, dept, no_room, no_bstd, no_bench, tot_std,status)

                   try:
                      mycursor.execute(sql, val)
                      mydb.commit()
                      session['roomadd'] = "Room added successfully"
                      return redirect('/addroomsuccess')
                   except Exception as e:
                      return "Error adding room: {}".format(str(e))
                 else:
                     session['roomadd'] = "Room already exists"
                     return redirect('/addroomsuccess')
    else:
        return "Invalid request"
    
    
@app.route('/wrongedate')
def wrongedate():
    return redirect('/add')

@app.route('/addroomsuccess')
def addroomsuccess():
    return redirect('/add')



@app.route('/viewroom',methods=['GET','POST'])
def list_rooms():
    if 'id' in session:
        mycursor.execute("SELECT * FROM room_details;")
        rooms = mycursor.fetchall()
        
        mydb.commit()
        return render_template('viewroom.html',logged_in=True,rooms=rooms)
        
    else:
        return redirect(url_for('login'))

@app.route('/allot/<string:e_date>/<string:mer>/<string:dept>/<string:room_no>', methods=['GET', 'POST'])
def allot(e_date, mer, dept, room_no):
    duplicate=session.pop('duplicate','')
    if 'id' in session:
        mycursor.execute("SELECT * FROM room_details WHERE e_date=%s AND mer=%s AND dept=%s AND room_no=%s", (e_date,mer,dept,room_no,))
        room = mycursor.fetchall()
        if room:
            bench_count = room[0][6]
            student_count = room[0][7]
            student_list = []
            details=""
            for i in range(student_count):
                student_list.append(f"Student {i+1}")
            return render_template('allot.html',logged_in=True, room=room, bench_count=bench_count, student_count=student_count, student_list=student_list,details=details,duplicate=duplicate)    
        else:
            return "room not found" 
    else:    
        return redirect(url_for('login'))
    
    
    
@app.route('/deleteroom/<string:e_date>/<string:mer>/<string:dept>/<string:room_no>', methods=['GET', 'POST'])
def deleteroom(e_date, mer, dept, room_no):
    if 'id' in session:
        delete_query = "DELETE FROM room_details WHERE e_date = %s AND mer = %s AND dept = %s AND room_no = %s"
        values = (e_date, mer, dept, room_no)
        mycursor.execute(delete_query, values)
        mydb.commit()
        delete_query = "DELETE FROM alloted_details WHERE date = %s AND mer = %s AND dept = %s AND roomno = %s"
        values = (e_date, mer, dept, room_no)
        mycursor.execute(delete_query, values)
        mydb.commit()
        mycursor.execute("SELECT * FROM room_details")
        rooms = mycursor.fetchall()
        mydb.commit()
        return render_template('viewroom.html', logged_in=True,rooms=rooms)
    else:
        return redirect(url_for('login'))

@app.route('/add_data', methods=['POST','GET'])
def add_data():
    try:
        data = request.get_json()
        print(data)
        print(data['students'])
        students = data["students"]
        if data is not None:
            room_number = data["room_number"]
            dept = data["dept"]
            date = data["date"]
            Time = data["time"]
            mer = data["mer"]
            
            max_seat_no = 0   
            for i in students:
                    clas = i['class']
                    to = i['to']
                    fro = i['from'] 
                    print(clas)
                    print(to)
                    print(fro)
                    if clas and to and fro is not None:  
                     mycursor.execute("SELECT reg_no,name,roll_no FROM student_details WHERE branch=%s AND roll_no BETWEEN %s AND %s;", (clas,fro, to))
                     st = mycursor.fetchall()
                     time.sleep(.000000001)
                     print(st)
                     clas_count = 0
                     seat_no = max_seat_no + 1
                     print(seat_no)
                     for j in st:
                        reg_no = j[0]
                        name = j[1]
                        rollno = j[2]
                        mycursor.execute("SELECT MAX(seatno) FROM alloted_details WHERE dept=%s AND roomno = %s;", (dept, room_number,))
                        result = mycursor.fetchall()
                        time.sleep(.000000001)
                        print(result[0][0])
                        if result[0][0] is not None:
                              max_seat_no = result[0][0] + 1
                              print(max_seat_no)
                        sql = 'INSERT INTO alloted_details(date,time,mer,reg_no,name,rollno,seatno,dept,roomno) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s);'
                        val = (date, Time, mer, reg_no, name, rollno, seat_no, dept, room_number)
                        mycursor.execute(sql, val)
                        time.sleep(.000000001)
                        mydb.commit()
                        seat_no += 1
                        print(seat_no)
              
                     clas_count += 1
                     mycursor.execute("UPDATE room_details SET status= 1 WHERE e_date=%s AND mer=%s AND dept=%s AND room_no=%s;", (date,mer,dept,room_number,))
                     result = mycursor.fetchone()
                     time.sleep(.00000000001)
                     mydb.commit()
            session['duplicate'] = "sucess"
            duplicate = session['duplicate']
            print(duplicate)
                 #print(render_template('duplicate.html', logged_in=True, duplicate=duplicate))
                #return render_template('duplicate.html', logged_in=True, duplicate=duplicate)
            return "success"
                
        else:
            return jsonify({'success': False, 'error': 'No data received'})
    except JSONDecodeError as e:
        return "invalid method"



@app.route('/allotdetails',methods=['GET','POST'])
def allotdetails():
    if 'id' in session:
        mycursor.execute("SELECT * FROM room_details;")
        rooms = mycursor.fetchall()
        mydb.commit()
        return render_template('viewalloted.html',logged_in=True,rooms=rooms)
        
    else:
        return redirect(url_for('login'))   
    
    
@app.route('/viewalloteddetails/<string:e_date>/<string:mer>/<string:dept>/<string:room_no>', methods=['GET', 'POST'])
def viewalloteddetails(e_date, mer, dept, room_no):
    if 'id' in session:
        mycursor.execute("SELECT * FROM alloted_details WHERE date=%s AND mer=%s AND dept=%s AND roomno=%s", (e_date,mer,dept,room_no,))
        room = mycursor.fetchall()
        mydb.commit()
        mycursor.execute("SELECT std_bench FROM room_details WHERE e_date=%s AND mer=%s AND dept=%s AND room_no=%s", (e_date,mer,dept,room_no,))
        bench=mycursor.fetchall()
        mydb.commit()
        b=int(bench[0][0])
        mycursor.execute("SELECT no_bench FROM room_details WHERE e_date=%s AND mer=%s AND dept=%s AND room_no=%s", (e_date,mer,dept,room_no,))
        no_bench=mycursor.fetchall()
        mydb.commit()
        a=int(no_bench[0][0])
        print(a)
        if room:
            
            
            return render_template('allotedstddetails.html',logged_in=True,rooms=room,b=b,a=a)  
        else:
            room=""
            return render_template('allotedstddetails.html',logged_in=True,nota="Havent alloted yet",rooms=room,b=b)
    else:    
        return redirect(url_for('login'))    

@app.route('/check',methods=['GET','POST'])
def check():

    if request.method=='POST':
        reg_no=request.form.get('id')
        
        date=request.form.get('date')
        try:
           date = datetime.strptime(date, '%d-%m-%Y').strftime('%Y-%m-%d')
        except ValueError:
            session['incorrectdate'] = "Please enter the date in the format DD-MM-YYYY"
            return redirect('/check') 
        if not reg_no or not date:
                return "not got the data"   
        else:
            mycursor.execute("SELECT * FROM alloted_details WHERE date=%s AND reg_no=%s", (date,reg_no,))
            allot = mycursor.fetchall()
            mydb.commit()
            if allot: 
                session['allot']=allot
                return redirect('/')
            else:
                session['noallot']="SEAT IS NOT ALLOTTED"
                return redirect('/')
        
        
@app.route('/count',methods=['GET','POST'])
def count():
    if 'id' in session:
        mycursor.execute("SELECT COUNT(*) FROM alloted_details;")
        count = mycursor.fetchall()
        count=int(count[0][0])
        mydb.commit()
       
        mycursor.execute("SELECT COUNT(*) FROM student_details;")
        remaining = mycursor.fetchall()
        remaining=int(remaining[0][0])
        mydb.commit()
        return render_template('count.html',logged_in=True,count=count,remaining=remaining)
        
    else:
        return redirect(url_for('login'))      
        
if __name__=='__main__':
    app.run(debug=True)