from flask import Flask, render_template,request,session,redirect,url_for
from flaskext.mysql  import MySQL
#import unittest
app = Flask(__name__)
#setup connection
mysql = MySQL()	
app.config['MYSQL_DATABASE_USER'] = 'root' #database username
app.config['MYSQL_DATABASE_PASSWORD'] = '' #database password
app.config['MYSQL_DATABASE_DB'] = 'moodle' #database db
app.config['MYSQL_DATABASE_HOST'] = 'localhost' #database host
mysql.init_app(app) 
app.secret_key = 'kappa' #secret key for sessions

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico') #sets the html icon
#------------------------------------------------------Catches random paths and redirects them
@app.route('/', defaults={'path': ''}) 
@app.route('/<path:path>') 
def catch_all(path):
	if session.get('logged_in') == True: #if user is logged in redirect to main site
		if session.get('role') == "1": #if role is student
			return student() #main student
		else: #else admin
			return view_assignments() #main admin
	else:
		return render_template('signin.html',title = "Sign in") #if not redirect to login
#------------------------------------------------------Login to the platform
@app.route('/login', methods=['GET', 'POST']) 
def login():
	cursor = mysql.connect().cursor() #setting cursor
	if request.method == "POST" : #if method is post which means button is clicked
		cursor.execute("SELECT * from user where username='" + request.form['username'] + "' and password='" + request.form['password'] + "'") #query 
		data = cursor.fetchone() #fetch an entry if there are many
		if data is None: #if no data exists
			message="Logged in failed" #log in failed
		else: #if data exists set sessions
			session['logged_in'] = True 
			session['username'] = request.form['username']
			session['role'] = data[4]
			session['name'] = data[2]
			session['surname'] = data[3]
			return redirect(url_for('catch_all')) #redirect to main
		return render_template('signin.html',title = "Sign in",message="Login Failed") #redirect to login since to user found 
#------------------------------------------------------Add Student
@app.route('/create_student', methods=['GET', 'POST']) 
def create_student():
	if not check(): #if role is student or logged in is false
			print "Access failed redirect to main" #print to console
			return redirect(url_for('catch_all')) #redirect to main
	cursor = mysql.connect().cursor() #set cursor
	if request.method == "POST" : #if button is clicked 
		cursor.execute("SELECT * from user where username='" + request.form['username'] + "'") #query
		data = cursor.fetchone() #get one select
		if data is None: #if data is none so username doesnt exist
			cursor.execute('''INSERT INTO user(username,password,name,surname,role) VALUES (%s,%s,%s,%s,%s)''',(request.form['username'],request.form['password'],request.form['fname'],request.form['lname'],1) ) #query
			return render_template('create_student.html',message="Student created",title="Create Student") #return student created
		else:
			return render_template('create_student.html',message = "Username " + request.form['username']+ " already exists",title="Create student") #return username already exists
	else:
		return render_template('create_student.html',title="Create Student") #return default
#------------------------------------------------------Update student	
@app.route('/update_student' , methods=['GET','POST'])
def update_student():
	if not check():
		print "Access failed redirect to main" #print to console
		return redirect(url_for('catch_all'))
	cursor = mysql.connect().cursor()
	cursor.execute("SELECT * from user WHERE role=1 order by username")
	status='disabled'
	if request.method == "POST":
		if request.form['option'] == '0': #select username	
			status =''
			cursor2 = mysql.connect().cursor()
			cursor2.execute("SELECT * from user where username='"+request.form['username']+"'")
			data = cursor2.fetchone()
			return render_template('update_student.html',title="Update student",data=cursor.fetchall(),status=status,user=data[0],password=data[1],fname=data[2],lname=data[3],student_username=data[0])
		if request.form['option'] == '1':
			cursor.execute("UPDATE `user` SET `username`='"+request.form['username']+"',`password`='"+request.form['password']+"',`name`='"+request.form['fname']+"',`surname`='"+request.form['lname']+"' WHERE username='"+request.form['student_username']+"'")
			cursor.execute("SELECT * from user WHERE role=1 order by username")
			return render_template('update_student.html',title="Update student",data=cursor.fetchall(),status=status,message="Student updated")
	else:
		return render_template('update_student.html',title="Update student",data=cursor.fetchall(),status=status)
#------------------------------------------------------Delete student
@app.route('/delete_student', methods=['GET', 'POST']) 
def delete_student():
	if not check():
		print "Access failed redirect to main" #print to console
		return redirect(url_for('catch_all'))
	cursor = mysql.connect().cursor()
	if request.method == "POST" :
		cursor.execute("Delete from user where username='" + request.form['username'] + "'")
		cursor.execute("Delete from student_class where student_username='" + request.form['username'] + "'")
		cursor.execute("SELECT * from user WHERE role=1 order by username")
		return render_template('delete_student.html',data=cursor.fetchall(),messages=request.form['username'] + " deleted",title="Delete Student")
	else:
		cursor.execute("SELECT * from user WHERE role=1 order by username")
		return render_template('delete_student.html',data=cursor.fetchall(),title="Delete Student")
#------------------------------------------------------Create class
@app.route('/create_class', methods=['GET','POST'])
def create_class():
	if not check():
		print "Access failed redirect to main" #print to console
		return redirect(url_for('catch_all'))
	cursor = mysql.connect().cursor()
	if request.method == "POST": 
		cursor.execute("SELECT * from class where id='" + request.form['id'] + "'")
		data = cursor.fetchone()
		if data is None:
			cursor.execute('''INSERT INTO class(id,name,description) VALUES (%s,%s,%s)''',(request.form['id'],request.form['name'],request.form['desc']) )
			return render_template('create_class.html',message="class created",title="Create class")
		else:
			return render_template('create_class.html',title="Create class",message="Id "+request.form['id']+" already exists")	
	else:
		return render_template('create_class.html',title="Create class")
#------------------------------------------------------Update class
@app.route('/update_class',methods=['GET','POST'])
def update_class():
	if not check():
		print "Access failed redirect to main" #print to console
		return redirect(url_for('catch_all'))
	status='disabled'
	cursor = mysql.connect().cursor()
	cursor.execute("SELECT * from class order by id")
	if request.method == "POST":
		if request.form['option'] == '0':
			status = ""
			cursor2 = mysql.connect().cursor()
			cursor2.execute("SELECT * from class where id='"+request.form['id']+"'")
			data = cursor2.fetchone()
			return render_template('update_class.html',id_class=request.form['id'],title="Update class",data=cursor.fetchall(),id=data[0],name=data[1],desc=data[2])
		if request.form['option'] == '1':
			cursor.execute("UPDATE `class` SET `id`='"+request.form['id']+"',`name`='"+request.form['name']+"',`description`='"+request.form['desc']+"' WHERE id='"+request.form['id_class']+"'")
			cursor.execute("SELECT * from class order by id")
			return render_template('update_class.html',title="Update class",data=cursor.fetchall(),message="class updated",status=status)
	else:
		return render_template('update_class.html',title="Update class",data=cursor.fetchall(),status=status)
#------------------------------------------------------Create assignment
@app.route('/assignment', methods=['GET','POST'])
def assignment():
	cursor = mysql.connect().cursor()
	if not check():
		print "Access failed redirect to main" #print to console
		return redirect(url_for('catch_all'))
	if request.method == "POST" :
		cursor.execute("SELECT * from assignment where id='" + request.form['id'] + "'")
		data = cursor.fetchone()
		if data is None:
			cursor.execute('''INSERT INTO assignment(id,title,date_to,description,lesson_id) VALUES (%s,%s,%s,%s,%s)''',(request.form['id'],request.form['title'],request.form['date'],request.form['desc'],request.form['class_id']) )
			cursor.execute("SELECT * from class order by id")
			return render_template('assignment.html',data=cursor.fetchall(),message="Assignment created",title="Create class")
		else:
			cursor.execute("SELECT * from class order by id")
			return render_template('assignment.html',title="Assignment",message="Id "+request.form['id']+" already exists",data=cursor.fetchall())
		cursor.execute("SELECT * from class order by id")
		return render_template('assignment.html',title='Assignment',data=cursor.fetchall(),message="Assignment created")
	else:
		cursor.execute("SELECT * from class order by id")
		return render_template('assignment.html',title="Create Assignment",data=cursor.fetchall())
#-----------------------------------------------------View Assignments
@app.route('/view_assignments',methods=['GET','POST'])
def view_assignments():
	cursor = mysql.connect().cursor()
	if not check():
		print "Access failed redirect to main" #print to console
		return redirect(url_for('catch_all'))
	cursor = mysql.connect().cursor()
	cursor.execute("SELECT *,class.name from assignment inner join class WHERE assignment.lesson_id = class.id")
	if request.method == "POST":
		cursor.execute("DELETE FROM assignment WHERE id='" + request.form['option']+ "'")
		cursor.execute("SELECT * from assignment")
		return render_template('view_assignments.html',title="View assignments",data=cursor.fetchall(),message="Assignment "+request.form['option']+" deleted")
	return render_template('view_assignments.html',title="View assignments",data=cursor.fetchall())
#-----------------------------------------------------Update Assignments
@app.route('/update_assignments',methods=['GET','POST'])
def update_assignments():
	status='disabled'
	cursor = mysql.connect().cursor()
	if not check():
		print "Access failed redirect to main" #print to console
		print "kappas"
		return redirect(url_for('catch_all'))
	if request.method == "POST" :

		status=''
		if request.form['option'] == '0':
			status = ""
			cursor2 = mysql.connect().cursor()
			cursor2.execute("SELECT * from assignment where id='"+request.form['id']+"'")
			data = cursor2.fetchone()
			cursor.execute("SELECT * FROM assignment order by id")
			return render_template('update_assignment.html',id_assignment=request.form['id'],title="Update class",data=cursor.fetchall(),id=data[0],titles=data[1],date=data[2],desc=data[3])
		if request.form['option'] == '1':
			status='disabled'
			cursor.execute("UPDATE `assignment` SET `id`='"+request.form['id']+"',`title`='"+request.form['titles']+"',`description`='"+request.form['desc']+"',`date_to`='"+request.form['date']+"' WHERE id='"+request.form['id_assignment']+"'")
			cursor.execute("SELECT * from class order by id")
			cursor.execute("SELECT * FROM assignment order by id")
			return render_template('update_assignment.html',title="Update assignment",data=cursor.fetchall(),message="Assignment updated",status=status)
	else:
		cursor.execute("SELECT * FROM assignment order by id")
		return render_template('update_assignment.html',title="Update Assignment",data = cursor.fetchall(),status=status)
#-----------------------------------------------------Connect class with students
@app.route('/connect_class_student', methods=['GET','POST'])
def connect_class_student():
	if not check():
		print "Access failed redirect to main" #print to console
		return redirect(url_for('catch_all'))
	cursor = mysql.connect().cursor()
	cursor2 = mysql.connect().cursor()
	cursor.execute("SELECT * from user WHERE role=1 order by username")
	cursor2.execute("SELECT * from class order by id")
	if request.method == "POST" :
		cursor.execute('''INSERT INTO student_class(student_username,class_id) VALUES (%s,%s)''',(request.form['student_id'],request.form['class_id']) )
		cursor.execute("SELECT * from user WHERE role=1 order by username")
		return render_template('connect_class_student.html',title="Class-student",data=cursor.fetchall(),data2=cursor2.fetchall(),messages="Connection for student "+request.form['student_id']+" and class "+request.form['class_id']+" successful")
	else:	
		return render_template('connect_class_student.html',title="Class-student",data=cursor.fetchall(),data2=cursor2.fetchall())
#----------------------------------------------------View Classes and delete
@app.route('/view_classes', methods=['GET','POST'])
def view_classes():
	if not check():
		print "Access failed redirect to main" #print to console
		return redirect(url_for('catch_all'))
	cursor = mysql.connect().cursor()
	if request.method == "POST":
		cursor.execute("DELETE from class where id="+request.form['option'])
		cursor.execute("DELETE from assignment where lesson_id="+request.form['option'])
		cursor.execute("DELETE from student_class where class_id="+request.form['option'])
		cursor.execute("SELECT * from class order by id")
		return render_template('view_classes.html',title="View classes",data=cursor.fetchall(),message="Class "+request.form['option']+" deleted")
	cursor.execute("SELECT * from class order by id")
	return render_template('view_classes.html',title="View classes",data=cursor.fetchall())
#-----------------------------------------------------Check connections
@app.route('/check_connection', methods=['GET','POST'])
def check_connection():
	if not check():
		print "Access failed redirect to main" #print to console
		return redirect(url_for('catch_all'))
	cursor = mysql.connect().cursor()	
	if request.method == "POST" :
		if request.form['option'] == "1":
			cursor.execute("DELETE from student_class where student_username='" + request.form['student_username'] + "' and class_id='"+request.form['class_id']+ "'")
		if request.form['option'] == "0":
			cursor.execute("SELECT * from student_class WHERE student_username='"+request.form['student_username']+"' order by student_username")
			return render_template('check_connection.html',data=cursor.fetchall(),title="Connections")
	cursor.execute("SELECT * from student_class order by student_username")
	return render_template('check_connection.html',data=cursor.fetchall(),title="Connections")
#-----------------------------------------------------Student
@app.route('/classes', methods=['GET','POST'])
def student():
	if session.get('role') =="0" or session.get('logged_in') != True:
		print "Access failed redirect to main" #print to console
		return redirect(url_for('catch_all'))
	cursor = mysql.connect().cursor()
	cursor.execute("SELECT class.id,name FROM student_class INNER join class on student_class.class_id = class.id where student_class.student_username='"+session['username']+"' order by class.id")
	if request.method == "POST":
		cursor2 = mysql.connect().cursor()
		cursor2.execute("SELECT assignment.id,assignment.title,assignment.date_to,assignment.description,class.name,class.id FROM `class` INNER JOIN assignment on assignment.lesson_id = class.id where class.id='"+request.form['class']+"' order by assignment.id")
		return render_template('classes.html',data=cursor.fetchall(),title="Classes",data2=cursor2)
	return render_template('classes.html',data=cursor.fetchall(),title="Classes") 

#------------------------------------------------------logout
@app.route('/logout') #once on logout remove session and redirect to login
def logout(): 
	session.pop('logged_in', None) #remove session logged_in
	session.pop('username', None) #remove session username 
	session.pop('name', None) #remove session name
	session.pop('surnmae', None) #remove session surname
	session.pop('role', None)
	return redirect(url_for("catch_all")) #redirect to catch_all
#------------------------------------------------------Permission check
def check():
	if session.get("logged_in") != True or session.get('role') != '0':
		return False
	else:
		return True
#------------------------------------------------------Unittests

if __name__ == '__main__':
    app.run(host= '0.0.0.0' , debug=True) #this is so it can run on the network to view from smartphone

