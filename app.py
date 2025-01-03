from flask import Flask,request,render_template,redirect,jsonify,json,url_for,session,Response,make_response,get_flashed_messages
from json import JSONDecodeError
from datetime import datetime
from jinja2.exceptions import TemplateNotFound
import mysql.connector
import bcrypt
import inspect
import traceback
import time
from flask_mail import Mail,Message
import random



mydb=mysql.connector.connect(host="",user="",password="",database="",auth_plugin="")
mycursor=mydb.cursor()
result=0


app=Flask(__name__)
app.secret_key = 'kiran'   
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SESSION_REFRESH_EACH_REQUEST'] = True

app.config['MAIL_SERVER']="smtp.gmail.com"
app.config['MAIL_PORT']=587
app.config['MAIL_USE_TLS']=True
app.config['MAIL_USERNAME']=""
app.config['MAIL_PASSWORD']=""
mail=Mail(app)

@app.route('/')
def home():
    
    return render_template('home.html',logged_in=False)

@app.route('/successsignin',methods=['POST','GET'])
def successlog():
    
    
    return render_template('signupsucess.html')
@app.route('/login',methods=['GET','POST'])
def login():
    noaccount = session.pop('noaccount', '')
   
    return render_template('login.html', logged_in=False,noaccount=noaccount)

@app.route('/dashboard',methods=['GET','POST'])
def dashboard():
    
    if 'id' in session:
        print(id)
        return render_template('dashboard.html', logged_in=True)
    else:
        return redirect(url_for('login'))
    
    
@app.route('/add',methods=['GET','POST'])
def add():
    
    if 'id' in session:
        return render_template('addroom.html', logged_in=True)
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
        data = request.get_json()
        name=data['username']
        id=data['id']
        dob=data['dob']
        try:
           dob = datetime.strptime(dob, '%d-%m-%Y').strftime('%Y-%m-%d')
        except ValueError:
            response = {'incorrectdate': 'Please enter the date in the format DD-MM-YYYY'}
            return jsonify(response)
            session['incorrectdate'] = "Please enter the date in the format DD-MM-YYYY"
            return redirect('/signin')   
        
        
        phone=data['phone']
        email=data['email']
        password=data['password']
        confirm_password=data['confirm_password']
        fcolor=data['fcolor']
        bgroup=data['bgroup']
        siblings=data['siblings']
        cinema=data['cinema']
        session['name']=name
        session['id']=id
        session['dob']=dob
        session['phone']=phone
        session['email']=email
        session['fcolor']=fcolor
        session['bgroup']=bgroup
        session['siblings']=siblings
        session['cinema']=cinema
        
        
        if not name or not id or not dob or not phone or not fcolor or not bgroup or not siblings or not cinema or not email or not password or not confirm_password:
            return "not got the data"
        elif confirm_password != password:
            response = {'doesnotmatch': 'Password do not match'}
            return jsonify(response)
            
        else:
            try:
                 mycursor.execute('SELECT t_id FROM teachers_details WHERE t_name=%s AND t_dob=%s',(name,dob))
                 result=mycursor.fetchone()
                 mydb.commit()
            except mysql.connector.Error as e:
                return "Exception error: {}".format(e)
             
            if result is None or id != result[0]:
                response = {'incorrectid': 'Sign in failed incorrect details'}
                return jsonify(response)
                
            else:
                 mycursor.execute('SELECT t_id FROM signup_details WHERE t_name=%s AND t_dob=%s',(name,dob))
                 result=mycursor.fetchone()
                 mydb.commit()
                 if result is None:
                   salts=bcrypt.gensalt()
                   hashed_password = bcrypt.hashpw(password.encode('utf-8'), salts)
                   session['hashed_password']=hashed_password
                   """sql='INSERT INTO signup_details (t_id,t_name,t_dob,phone,email,password,color,bgroup,siblings,cinema) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
                   val=(id,name,dob,phone,email,hashed_password,fcolor,bgroup,siblings,cinema)
                 
                   mycursor.execute(sql,val)
                   mydb.commit()"""
                   otp_code=random.randint(1000,9999)
                   session['otp_code']=otp_code
                   try:
                            mail.send_message(
                                subject="OTP for your Flask app",
                                sender="flask717@gmail.com",
                                recipients=[email],
                                body="Your OTP is: {otp}".format(otp=otp_code),
                                )
                            
                            response = {"redirect": True}
                            return jsonify(response)
                            return render_template('signupsucess.html')
                   except:
                           response={'accountalready':'Network issue'}    
                 else:
                     response = {'accountalready': 'Account already exists'}
                     return jsonify(response)
       
@app.route('/signupotp',methods=['GET','POST'])
def signupotp():
        email=session.get('email')
        return render_template('signupotp.html',email=email) 
    
@app.route('/verifysignupotp',methods=['GET','POST'])
def verifysignupotp():
        if request.method=='POST':
            data = request.get_json()
            otp=data['otp']
            stored_otp=session.get('otp_code')
            if otp==str(stored_otp):
                name=session.get('name')
                id=session.get('id')
                dob=session.get('dob')
                phone=session.get('phone')
                email=session.get('email')
                fcolor=session.get('fcolor')
                bgroup=session.get('bgroup')
                siblings=session.get('siblings')
                hashed_password=session.get('hashed_password')
                cinema=session.get('cinema')
                sql='INSERT INTO signup_details (t_id,t_name,t_dob,phone,email,password,color,bgroup,siblings,cinema) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
                val=(id,name,dob,phone,email,hashed_password,fcolor,bgroup,siblings,cinema)
                 
                mycursor.execute(sql,val)
                mydb.commit()
           
                response = {"redirect":True}
                return jsonify(response)
            else:
                response={"incorrectotp":"WRONG  OTP"}
                return jsonify(response)
      
    
          
@app.route('/log',methods=['GET','POST'])
def log():
  if request.method == 'POST':
    data = request.get_json()
    print(data)
    id=data['id']
    password=data['password'].encode('utf-8')
    
    if not id or not password:
        return "not get data"
    
    try:
        mycursor.execute('SELECT t_id FROM signup_details WHERE t_id=%s',(id,))
        result=mycursor.fetchone()
        mydb.commit()
    except mysql.connector.Error as e:
                return "Exception error: {}".format(e)    
    if result is None or id != result[0]:
                response = {"noaccount": "YOU DOON'T HAVE AN ACCOUNT PLEASE SIGNUP FIRST"}
                return jsonify(response)
            
    else:
                
        mycursor.execute('SELECT password from signup_details WHERE t_id=%s ',(id,))
        result=mycursor.fetchone()
        mydb.commit()
        mycursor.execute('SELECT t_name from signup_details WHERE t_id=%s ',(id,))
        name=mycursor.fetchone()
        name=name[0]
        mydb.commit()
        if result:
             hashed_password = result[0].encode('utf-8')
             if bcrypt.checkpw(password, hashed_password):
                  session['id'] = name.capitalize()
                  print(session['id'])
                  
                  response = {"redirect": True}
                  return jsonify(response)

                  
        
             else:
                 response = {"noaccount": "INCORRECT PASSWORD"}
                 return jsonify(response)

@app.route('/forgotpass',methods=['POST','GET'])
def forgotpass():
    return render_template('forgotpass.html')             
                 
@app.route('/forgot',methods=['POST','GET'])
def forgot():
    if request.method=='POST':
         data=request.get_json()
         id=data['id']
         session['id']=id
         print(id)
         try:
              mycursor.execute('SELECT t_id FROM signup_details WHERE t_id=%s',(id,))
              result=mycursor.fetchone()
              mydb.commit()
              if result is None or id != result[0]:
                  
                response = {"incorrectotp": "YOU DON'T HAVE AN ACCOUNT PLEASE SIGNUP FIRST"}
                return jsonify(response)    
              else:
                  mycursor.execute('SELECT email FROM signup_details WHERE t_id=%s',(id,))
                  email=mycursor.fetchone()
                  mydb.commit()
                  email=email[0]    
                  session['email']=email
                  otp_code=random.randint(1000,9999)
                  session['otp_code']=otp_code
                  
                  mail.send_message(
                                    subject="OTP for your Flask app",
                                    sender="flask717@gmail.com",
                                    recipients=[email],
                                    body="Your OTP is: {otp}".format(otp=otp_code),
                                )
                  response = {"redirect": True}
                  return jsonify(response)
                          
         except:
             return "error" 
          
    return "Invalid request"        
              
@app.route('/enterotp',methods=['POST','GET'])
def enterotp():
    if request.method=='POST':
            data = request.get_json()
            otp=data['otp']
            email=session.get('email')
            stored_otp=session.get('otp_code')
            if otp==str(stored_otp):
                response = {"redirect": True}
                return jsonify(response)
            else:
                response={"incorrectotp":"WRONG  OTP"}
                return jsonify(response)
@app.route('/entermailotp',methods=['GET','POST'])
def entermailotp():
  email=session.get('email')  
  return render_template('enterotp.html',email=email)    
            
@app.route('/resetpassword',methods=['POST','GET'])
def resetpassword():
    return render_template('resetpass.html')    


@app.route('/newpassword',methods=['GET','POST'])
def newpassword():
     if request.method=='POST':
         data=request.get_json()
         password=data['password']
         confirmpassword=data['confirmpassword']  
         if password == confirmpassword:
            email=session.get('email')
            id=session.get('id')
            salts=bcrypt.gensalt()
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), salts)
            mycursor.execute('UPDATE signup_details SET password=%s WHERE t_id=%s',(hashed_password,id,))
            email=mycursor.fetchone()
            mydb.commit()
            response={"redirect":True}
            return jsonify(response)
         else:
             response={"noaccount":"Password does not match"}
             return jsonify(response)
         
         
@app.route('/resetsuccess',methods=['GET','POST'])
def resetsuccess():
    return render_template('resetsuccess.html')         
                  
@app.route('/logout', methods=['POST'])
def logout():
    session.pop('id', None)
    return redirect((url_for('login')))                 

@app.route('/addroom', methods=['GET', 'POST'])
def addroom():
    
    if request.method == 'POST':
        data = request.get_json()
        exam_date = data['exam_date']
        exam_time = data['exam_time']
        mer = data['dropdown']
        dept = data['dept']
        no_room = data['no_room']
        no_bstd = data['no_bstd']
        no_bench = data['no_bench']
        tot_std = data['tot_std']
        if exam_date is None:
            response = {'wrongdate': 'Please enter the date in the format DD-MM-YYYY'}
            return jsonify(response)
        else:
            try:
               exam_date = datetime.strptime(exam_date, '%d-%m-%Y').strftime('%Y-%m-%d')
            except ValueError:
              response = {'wrongdate': 'Please enter the date in the format DD-MM-YYYY'}
              return jsonify(response)
              

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
                      response = {'roomadd': 'ROOM ADDED SUCCESSFULLY'}
                      return jsonify(response)
                   except Exception as e:
                      return "Error adding room: {}".format(str(e))
                 else:
                     response = {'roomadd': 'ROOM ALREADY EXISTS'}
                     return jsonify(response)
    else:
        return "Invalid request"
    
    

@app.route('/viewroom',methods=['GET','POST'])
def list_rooms():
    if 'id' in session:
        mycursor.execute("SELECT * FROM room_details;")
        rooms = mycursor.fetchall()
        
        mydb.commit()
        for r in rooms:
            print(r[8])
            print(r[7])
            
            break
        return render_template('viewroom.html',logged_in=True,rooms=rooms)
        
    else:
        return redirect(url_for('login'))

@app.route('/allot/<string:e_date>/<string:mer>/<string:dept>/<string:room_no>', methods=['GET', 'POST'])
def allot(e_date, mer, dept, room_no):
    
    if 'id' in session:
        duplicate=session.pop('duplicate','')
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
 if 'id' in session: 
      try:
        data = request.get_json()
        students = data["students"]
        if data is not None:
            room_number = data["room_number"]
            dept = data["dept"]
            date = data["date"]
            etime = data["time"]
            mer = data["mer"]
            mycursor.execute("SELECT * FROM room_details WHERE e_date=%s AND mer=%s AND dept=%s AND room_no=%s", (date,mer,dept,room_number,))
            room = mycursor.fetchall()
           
            time.sleep(.000000001)
            max_seat_no = 0
            for i in students:
                  to = i['to']
                  fro = i['from'] 
                  max_seat_no = max_seat_no+((int(to)-(int(fro)))+1)
            if max_seat_no>room[0][7]:
                return f"Exeeds Capacity of the room you can allot upto {room[0][7]}"  
            else:
             max_seat_no=0
                     
             for i in students:
                  clas = i['class']
                  to = i['to']
                  fro = i['from'] 
                  if clas and to and fro is not None:  
                     mycursor.execute("SELECT reg_no,name,roll_no,branch FROM student_details WHERE branch=%s AND roll_no BETWEEN %s AND %s;", (clas,fro, to))
                     st = mycursor.fetchall()
                     if not st:
                         return "Odd Sem cannot be Allot"
                     else:
                      time.sleep(.000000001)
                      #print(st)
                      seat_no = max_seat_no + 1
                      #print(seat_no)
                      for j in st:
                        reg_no = j[0]
                        name = j[1]
                        rollno = j[2]
                        br=j[3]
                        mycursor.execute("SELECT MAX(seatno) FROM alloted_details WHERE dept=%s AND roomno = %s;", (dept, room_number,))
                        result = mycursor.fetchall()
                        time.sleep(.000000001)
                        if result[0][0] is not None:
                              max_seat_no = result[0][0] + 1
                              
                        mycursor.execute("SELECT flag,name,reg_no FROM alloted_details WHERE etime = %s AND mer = %s AND reg_no=%s;", (etime,mer,reg_no,))
                        flg = mycursor.fetchall()
                        time.sleep(.000000001)
                        
                        if not flg:
                           sql = 'INSERT INTO alloted_details(date,etime,mer,reg_no,name,rollno,seatno,dept,roomno) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s);'
                           val = (date, etime, mer, reg_no, name, rollno, seat_no, dept, room_number)
                           mycursor.execute(sql, val)
                           time.sleep(.000000001)
                           mydb.commit()
                           seat_no += 1
                           
                           mycursor.execute("UPDATE alloted_details SET flag= 1 WHERE date=%s AND etime=%s AND mer=%s  AND reg_no=%s AND name=%s;", (date,etime,mer,reg_no,name,))
                           result = mycursor.fetchone()
                           time.sleep(.00000000001)
                           mydb.commit()
                           mycursor.execute("UPDATE room_details SET status= 1 WHERE e_date=%s AND mer=%s AND dept=%s AND room_no=%s;", (date,mer,dept,room_number,))
                           result = mycursor.fetchone()
                           time.sleep(.00000000001)
                           mydb.commit()
                    
                        else:
                         for item in flg:
                          
                          if item[0] == 0:      
                           sql = 'INSERT INTO alloted_details(date,etime,mer,reg_no,name,rollno,seatno,dept,roomno) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s);'
                           val = (date, etime, mer, reg_no, name, rollno, seat_no, dept, room_number)
                           mycursor.execute(sql, val)
                           time.sleep(.000000001)
                           mydb.commit()
                           seat_no += 1
                           
                           mycursor.execute("UPDATE alloted_details SET flag= 1 WHERE date=%s AND etime=%s AND mer=%s  AND reg_no=%s AND name=%s;", (date,etime,mer,reg_no,name,))
                           result = mycursor.fetchone()
                           time.sleep(.00000000001)
                           mydb.commit()
                           mycursor.execute("UPDATE room_details SET status= 1 WHERE e_date=%s AND mer=%s AND dept=%s AND room_no=%s;", (date,mer,dept,room_number,))
                           result = mycursor.fetchone()
                           time.sleep(.00000000001)
                           mydb.commit()
                          else:
                             delete_query = "DELETE FROM alloted_details WHERE date = %s AND mer = %s AND dept = %s AND roomno = %s"
                             values = (date, mer, dept,room_number)
                             mycursor.execute(delete_query, values)
                             mydb.commit() 
                             time.sleep(.00000000001)
                             mycursor.execute("UPDATE room_details SET status= 0 WHERE e_date=%s AND mer=%s AND dept=%s AND room_no=%s;", (date,mer,dept,room_number,))
                             result = mycursor.fetchone()
                             time.sleep(.00000000001)
                             mydb.commit()
                             return f"Aready alloted for {item[1]} of class {br}"  
        return "success"             
      except JSONDecodeError as e:
        return "invalid method"
 else:   
        
        return redirect(url_for('login'))
    
        
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
        print(bench)
        print()
        mydb.commit()
        b=int(bench[0][0])
        print(b)
        mycursor.execute("SELECT no_bench FROM room_details WHERE e_date=%s AND mer=%s AND dept=%s AND room_no=%s", (e_date,mer,dept,room_no,))
        no_bench=mycursor.fetchall()
        mydb.commit()
        a=int(no_bench[0][0])
        print(a)
        if room:
            
            
            return render_template('allotedstddetails.html',logged_in=True,rooms=room,b=b,a=a)  
        else:
            room=""
            return render_template('allotedstddetails.html',logged_in=True,nota="SEAT IS NOT ALLOTED YET",rooms=room,b=b)
    else:    
        return redirect(url_for('login'))    

@app.route('/check',methods=['GET','POST'])
def check():

    if request.method=='POST':
        data = request.get_json()
        print(data)
        reg_no=data['id']
        date=data['date']
        try:
           date = datetime.strptime(date, '%d-%m-%Y').strftime('%Y-%m-%d')
        except ValueError:
            response = {'incorrectdate': 'Please enter the date in the format DD-MM-YYYY'}
            return jsonify(response)
            
        if not reg_no or not date:
                return "not got the data"   
        else:
            if reg_no.startswith("KGR"):
             mycursor.execute("SELECT * FROM alloted_details WHERE date=%s AND reg_no=%s", (date,reg_no,))
             allot = mycursor.fetchall()
             mydb.commit()
             if allot: 
                 return jsonify({'allot': allot})
                 
             else:
                 response = {'noallot': 'SEAT IS NOT ALLOTTED'}
                 return jsonify(response)
                 
            else:
                response = {'no_reg': 'INVALID REGISTER NUMBER'}
                return jsonify(response)
               
        
@app.route('/count',methods=['GET','POST'])
def count():
    if 'id' in session:
        mycursor.execute("SELECT date, etime, mer, COUNT(*) FROM alloted_details GROUP BY date, etime, mer;")
        count = mycursor.fetchall()
        mydb.commit()
        print(count)
        mycursor.execute("SELECT COUNT(*) FROM student_details;")
        remaining = mycursor.fetchall()
        remaining = int(remaining[0][0])
        mydb.commit()
        return render_template('count.html', logged_in=True, count=count, remaining=remaining)
    else:
        return redirect(url_for('login'))
  
    
    
   
        
if __name__=='__main__':
    app.run(debug=True,port=5100)
