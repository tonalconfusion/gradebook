from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re

app = Flask(__name__)


app.secret_key = 'secret_key'

#Database credentials
app.config['MYSQL_HOST'] = 'us-cdbr-east-02.cleardb.com'
app.config['MYSQL_USER'] = 'bfe1210a3e42e3'
app.config['MYSQL_PASSWORD'] = '0955563a'
app.config['MYSQL_DB'] = 'heroku_cfa98b126baf0f6'
# Intialize MySQL
mysql = MySQL(app)

#redirect to login
@app.route("/")
def index():
	return redirect(url_for("login"))

@app.route("/login", methods=['GET', 'POST'])
def login():
	msg = ''
	if request.method == 'POST' and 'name' in request.form and 'password' in request.form:
		name = request.form['name']
		password = request.form['password']
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		sql = ("SELECT * FROM students WHERE name = %s AND password = %s")
		values = (name, password)
		cursor.execute(sql, values)
		account = cursor.fetchone()
		if account:
			session['loggedin'] = True
			session['id'] = account['id']
			session['username'] = account['name']
			return redirect(url_for("home"))
		else:
			msg = 'Incorrect username/password'


	return render_template('index.html', msg=msg)


@app.route('/teacher_login', methods=['GET', 'POST'])
def teacher_login():
	if request.method == "POST" and 'name' in request.form and 'password' in request.form:
		name = request.form['name']
		password = request.form['password']
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		sql = ("SELECT * FROM teachers WHERE name = %s AND password = %s")
		values = (name, password)
		cursor.execute(sql, values)
		account = cursor.fetchone()
		if account:
			session['loggedin'] = True
			session['id'] = account['id']
			session['username'] = account['name']
			return redirect(url_for("teacher_home"))

	return render_template('teacher_login.html')

@app.route('/home')
def home():
	if 'loggedin' in session:
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute("SELECT * FROM students INNER JOIN grades ON students.id = grades.studentid WHERE studentid = %s", (session['id'],))
		data = cursor.fetchall()   
		session['class1'] = data[0]['class']
		session['class2'] = data[1]['class']
		session['class3'] = data[2]['class']
		session['class4'] = data[3]['class']
		cursor.execute("SELECT class_id FROM assignments RIGHT JOIN grades ON grades.id = assignments.class_id WHERE studentid= %s", (session['id'],))
		data1 = cursor.fetchall()

		def convert(x):
			n = []
			c = 0
			for i in x:
				c += 1
			for i in range(0, c):
				n.append(x[i]['class_id'])
			return n
				
		o = convert(data1)

		def occurence(x):
			freq = {}
			for item in x:
				if (item in freq):
					freq[item] += 1
				else:
					freq[item] = 1
			return freq

		n = occurence(list(o))
		p = list(n.keys())

		session['id1'] = p[0]
		session['id2'] = p[1]
		session['id3'] = p[2]
		session['id4'] = p[3]

		return render_template('home.html', name=session['username'], value=data)
	else:
		return redirect(url_for('login'))

@app.route('/teacher_home')
def teacher_home():
	if 'loggedin' in session:
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)


		db = MySQLdb.connect("us-cdbr-east-02.cleardb.com", "bfe1210a3e42e3", "0955563a", "heroku_cfa98b126baf0f6")
		cur = db.cursor()
		cursor.execute("SELECT * FROM grades INNER JOIN teachers ON teachers.id = grades.subject_id INNER JOIN students ON grades.studentid = students.id WHERE teachers.id=%s", (session['id'],))
		students1 = cursor.fetchall()
		cursor.execute("SELECT COUNT(*) FROM grades INNER JOIN teachers ON teachers.id = grades.subject_id INNER JOIN students ON grades.studentid = students.id WHERE teachers.id=%s", (session['id'],))
		count1 = cursor.fetchall()
		count1 = count1[0]['COUNT(*)']
		#for i in range(0, count1):
		#	class_id1 = students1[i]['id']
		print(students1[1]['id'])
		return render_template('teacher_home.html', name=session['username'], students=students1, count=count1)

	else:
		return redirect(url_for('teacher_login'))
@app.route('/logout')
def logout():
	session.pop('loggedin', None)
	session.pop('id', None)
	session.pop('username', None)
	return redirect(url_for('login'))

@app.route('/teacher_assign')
def teacher_assign():
	cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
	class_id = request.args.get('id')
	studentid = request.args.get('id1')
	cursor.execute("SELECT * FROM grades INNER JOIN teachers ON teachers.id = grades.subject_id INNER JOIN students ON grades.studentid = students.id INNER JOIN assignments ON grades.id = assignments.class_id WHERE studentid=%s AND grades.id=%s", (studentid, class_id))
	data2 = cursor.fetchall()

	cursor.execute("SELECT COUNT(*) FROM grades INNER JOIN teachers ON teachers.id = grades.subject_id INNER JOIN students ON grades.studentid = students.id INNER JOIN assignments ON grades.id = assignments.class_id WHERE studentid=%s AND grades.id=%s", (studentid, class_id))
	count = cursor.fetchall()
	count = count[0]['COUNT(*)']
	return render_template("teacher_class.html", data=data2, count=count)


@app.route('/add_assignment', methods=['GET', 'POST'])
def add_assignment():
	db = MySQLdb.connect("us-cdbr-east-02.cleardb.com", "bfe1210a3e42e3", "0955563a", "heroku_cfa98b126baf0f6")
	cur = db.cursor()
	if request.method == "POST" and 'aname' in request.form:
		aname = request.form['aname']
		
	return render_template('add_assignment.html')


@app.route('/profile')
def profile():
	if 'loggedin' in session:
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute("SELECT * FROM students WHERE id=%s", (session['id'],))
		account = cursor.fetchone()
		return render_template("profile.html", account=account, username=session['username'])
	return redirect(url_for('login'))


@app.route('/class_grades0', methods=['GET', 'POST'])
def class_grade0():
	cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
	cursor.execute("SELECT * FROM assignments INNER JOIN grades ON grades.id = assignments.class_id WHERE studentid = %s AND class_id = %s", (session['id'], session.get('id1', None)))
	data1 = cursor.fetchall()   


	cursor.execute("SELECT COUNT(*) FROM assignments INNER JOIN grades ON grades.id = assignments.class_id WHERE studentid = %s AND class_id = %s", (session['id'], session.get('id1', None)))
	amount1 = cursor.fetchall()
	amount1 = amount1[0]['COUNT(*)']

	def average(x):
		n=0
		for i in range(0, x):
			n += int(data1[i]['grade'])
		if x > 0:
			n=n/x
		else:
			return 0
		return n

	db = MySQLdb.connect("us-cdbr-east-02.cleardb.com", "bfe1210a3e42e3", "0955563a", "heroku_cfa98b126baf0f6")
	cur = db.cursor()
	average1 = average(amount1)
	cur.execute("UPDATE grades SET grade=%s WHERE id=%s AND studentid=%s", (average1, session.get('id1', None), session['id']))
	db.commit()
	print(average1)
	if amount1 >= 1:
		return render_template("class0.html", data=data1, amount=amount1)
	else:
		return "NONE"

@app.route('/class_grades1', methods=['GET', 'POST'])
def class_grade1():
	cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

	cursor.execute("SELECT * FROM assignments INNER JOIN grades ON grades.id = assignments.class_id WHERE studentid = %s AND class_id = %s", (session['id'], session.get('id2', None)))
	data1 = cursor.fetchall()

	cursor.execute("SELECT COUNT(*) FROM assignments INNER JOIN grades ON grades.id = assignments.class_id WHERE studentid = %s AND class_id = %s", (session['id'], session.get('id2', None)))
	amount1 = cursor.fetchall()
	amount1 = amount1[0]['COUNT(*)']

	def average(x):
		n=0
		for i in range(0, x):
			n += int(data1[i]['grade'])
		if n > 0:
			n=n/x
		return n
	db = MySQLdb.connect("us-cdbr-east-02.cleardb.com", "bfe1210a3e42e3", "0955563a", "heroku_cfa98b126baf0f6")
	cur = db.cursor()
	average1 = average(amount1)
	cur.execute("UPDATE grades SET grade=%s WHERE id=%s AND studentid=%s", (average1, session.get('id2', None), session['id']))
	db.commit()
	if amount1 >= 1:
		return render_template("class1.html", data=data1, amount=amount1)
	else:
		return "NONE"

@app.route('/class_grades2', methods=['GET', 'POST'])
def class_grade2():
	cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

	cursor.execute("SELECT * FROM assignments INNER JOIN grades ON grades.id = assignments.class_id WHERE studentid = %s AND class_id = %s", (session['id'], session.get('id3', None)))
	data1 = cursor.fetchall()

	cursor.execute("SELECT COUNT(*) FROM assignments INNER JOIN grades ON grades.id = assignments.class_id WHERE studentid = %s AND class_id = %s", (session['id'], session.get('id3', None)))
	amount1 = cursor.fetchall()
	amount1 = amount1[0]['COUNT(*)']
	def average(x):
		n=0
		for i in range(0, x):
			n += int(data1[i]['grade'])
		if x > 0:
			n=n/x
		return n
	db = MySQLdb.connect("us-cdbr-east-02.cleardb.com", "bfe1210a3e42e3", "0955563a", "heroku_cfa98b126baf0f6")
	cur = db.cursor()
	average1 = average(amount1)
	cur.execute("UPDATE grades SET grade=%s WHERE id=%s AND studentid=%s", (average1, session.get('id3', None), session['id']))
	db.commit()
	if amount1 >= 1:
		return render_template("class2.html", data=data1, amount=amount1)
	else:
		return "NONE"

@app.route('/class_grades3', methods=['GET', 'POST'])
def class_grade3():
	cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

	cursor.execute("SELECT * FROM assignments INNER JOIN grades ON grades.id = assignments.class_id WHERE studentid = %s AND class_id = %s", (session['id'], session.get('id4', None)))
	data1 = cursor.fetchall()

	cursor.execute("SELECT COUNT(*) FROM assignments INNER JOIN grades ON grades.id = assignments.class_id WHERE studentid = %s AND class_id = %s", (session['id'], session.get('id4', None)))
	amount1 = cursor.fetchall()
	amount1 = amount1[0]['COUNT(*)']
	def average(x):
		n=0
		for i in range(0, x):
			n += int(data1[i]['grade'])
		if x > 0:
			n=n/x
		return n
	db = MySQLdb.connect("us-cdbr-east-02.cleardb.com", "bfe1210a3e42e3", "0955563a", "heroku_cfa98b126baf0f6")
	cur = db.cursor()
	average1 = average(amount1)
	cur.execute("UPDATE grades SET grade=%s WHERE id=%s AND studentid=%s", (average1, session.get('id4', None), session['id']))
	db.commit()
	if amount1 >= 1:
		return render_template("class3.html", data=data1, amount=amount1)
	else:
		return "NONE"


