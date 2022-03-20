# Store this code in 'app.py' file

from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
from datetime import date
import MySQLdb.cursors
import re


app = Flask(__name__)


app.secret_key = 'roger that'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'pro'

mysql = MySQL(app)

@app.route('/')
@app.route('/login', methods =['GET', 'POST'])
def login():
	msg = ''
	if request.method == 'POST' and 'useremail' in request.form and 'password' in request.form:
		useremail = request.form['useremail']
		password = request.form['password']
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute('SELECT * FROM users WHERE email = % s AND password = % s', (useremail, password, ))
		account = cursor.fetchone()
		if account:
			session['loggedin'] = True
			session['id'] = account['id']
			session['useremail'] = account['email']
			msg = 'Logged in successfully !'
			return render_template('index.html', msg = msg)
		else:
			msg = 'Incorrect email / password !'
	return render_template('login.html', msg = msg)

@app.route('/task')
def task():
	if session.get('loggedin'):
		return render_template('index.html')
	else:
		return redirect(url_for('login'))

@app.route('/logout')
def logout():
	session.pop('loggedin', None)
	session.pop('id', None)
	session.pop('useremail', None)
	return redirect(url_for('login'))

@app.route('/register', methods =['GET', 'POST'])
def register():
	msg = ''
	if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form :
		username = request.form['username']
		password = request.form['password']
		email = request.form['email']
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute('SELECT * FROM users WHERE username = % s', (username, ))
		account = cursor.fetchone()
		if account:
			msg = 'Account already exists !'
		elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
			msg = 'Invalid email address !'
		elif not re.match(r'[A-Za-z0-9]+', username):
			msg = 'Username must contain only characters and numbers !'
		elif not username or not password or not email:
			msg = 'Please fill out the form !'
		else:
			cursor.execute('INSERT INTO users VALUES (NULL, % s, % s, % s)', (username, password, email, ))
			mysql.connection.commit()
			msg = 'You have successfully registered !'
	elif request.method == 'POST':
		msg = 'Please fill out the form !'
	return render_template('register.html', msg = msg)

@app.route('/bookrequest')
def bookrequest():
	if session.get('loggedin'):
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute('SELECT * FROM books')
		books = cursor.fetchall()
		return render_template('issuebookrequest.html', books = books)

@app.route('/bookrequests', methods =['GET', 'POST'])
def bookrequests():
	if session.get('loggedin'):
		if request.method == 'POST' and 'book_id' in request.form and 'user_id' in request.form:
			book_id = request.form['book_id']
			user_id = request.form['user_id']
			cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
			cursor.execute('INSERT INTO request VALUES (NULL, % s, % s)', (user_id, book_id,))
			mysql.connection.commit()
			msg = 'Book request sent successfully !'
			return render_template('index.html', msg = msg)
	return redirect(url_for('login'))

@app.route('/issuedbooklist', methods =['GET', 'POST'])
def issuedbooklist():
	if session.get('loggedin'):
		user_id = session['id']
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute('SELECT * FROM issue WHERE user_id = % s', (user_id, ))
		issuedbooks = cursor.fetchall()
		return render_template('issuedbooklist.html', issuedbooks = issuedbooks)
	return redirect(url_for('login'))



@app.route('/admin/', methods =['GET', 'POST'])
def adlogin():
	msg=''
	if session.get('adloggedin'):
		return redirect(url_for('dashboard'))
	if request.method == 'POST' and 'ademail' in request.form and 'adpswd' in request.form:
		ademail = request.form['ademail']
		adpswd = request.form['adpswd']
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute('SELECT * FROM admin WHERE email = % s AND password = % s', (ademail, adpswd, ))
		account = cursor.fetchone()
		if account:
			session['adloggedin'] = True
			session['adid'] = account['id']
			session['ademail'] = account['email']
			msg = 'Logged in successfully !'
			return render_template('admin/dashboard.html', msg = msg)
		else:
			msg = 'Incorrect username / password !'
	return render_template('admin/index.html', msg = msg)

@app.route('/admin/dashboard/')
def dashboard():
	if session.get('adloggedin'):
		return render_template('admin/dashboard.html')
	return redirect(url_for('adlogin'))

@app.route('/admin/addbook/', methods =['GET', 'POST'])
def addbook():
	msg=''
	if session.get('adloggedin'):
		if request.method == 'POST' and 'abname' in request.form and 'abdesc' in request.form and 'abcount' in request.form:
			abname = request.form['abname']
			abdesc = request.form['abdesc']
			abcount = request.form['abcount']
			cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
			cursor.execute('INSERT INTO books VALUES (NULL, % s, % s, % s)', (abname, abdesc, abcount, ))
			mysql.connection.commit()
			msg = 'Book added successfully !'
			return render_template('admin/dashboard.html', msg = msg)
		return render_template('admin/addbook.html', msg = msg)
	return redirect(url_for('adlogin'))

@app.route('/admin/adduser/', methods =['GET', 'POST'])
def adduser():
	msg=''
	if session.get('adloggedin'):
		if request.method == 'POST' and 'auname' in request.form and 'auemail' in request.form and 'aupswd' in request.form:
			auname = request.form['auname']
			auemail = request.form['auemail']
			aupswd = request.form['aupswd']
			cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
			cursor.execute('INSERT INTO users VALUES (NULL, % s, % s, % s)', (auname, aupswd, auemail, ))
			mysql.connection.commit()
			msg = 'User added successfully !'
			return render_template('admin/dashboard.html', msg = msg)
		return render_template('admin/adduser.html', msg = msg)
	return redirect(url_for('adlogin'))

@app.route('/admin/booklist/')
def booklist():
	if session.get('adloggedin'):
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute('SELECT * FROM books')
		books = cursor.fetchall()
		return render_template('admin/booklist.html', books = books)
	return redirect(url_for('adlogin'))

@app.route('/admin/updatebook/', methods=['GET', 'POST'])
def updatebook():
	if session.get('adloggedin'):
		bookid = request.args.get('bookid')
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute('SELECT * FROM books WHERE id = % s', (bookid, ))
		bookdata = cursor.fetchone()
		return render_template('admin/updatebook.html', bookdata = bookdata)
	return redirect(url_for('adlogin'))

@app.route('/admin/updatebooks/', methods=['GET', 'POST'])
def updatebooks():
	msg=''
	if session.get('adloggedin'):
		if request.method == 'POST' and 'abname' in request.form and 'abdesc' in request.form and 'abcount' in request.form and 'abid' in request.form:
			ubname = request.form['abname']
			ubdesc = request.form['abdesc']
			ubcount = request.form['abcount']
			ubid = request.form['abid']
			cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
			cursor.execute('UPDATE books SET name = % s, description = % s, count = % s WHERE id = % s', (ubname, ubdesc, ubcount, ubid, ))
			mysql.connection.commit()
			msg = 'Book updated successfully !'
		return render_template('admin/dashboard.html', msg = msg)
	return redirect(url_for('adlogin'))

@app.route('/admin/deletebook/')
def deletebook():
	if session.get('adloggedin'):
		bookid = request.args.get('bookid')
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute('DELETE FROM books WHERE id = % s', (bookid, ))
		mysql.connection.commit()
		return redirect(url_for('booklist'))
	return redirect(url_for('adlogin'))

@app.route('/admin/userslist/')
def userslist():
	if session.get('adloggedin'):
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute('SELECT * FROM users')
		users = cursor.fetchall()
		return render_template('admin/userslist.html', users = users)
	return redirect(url_for('adlogin'))

@app.route('/admin/updateuser/')
def updateuser():
	if session.get('adloggedin'):
		userid = request.args.get('userid')
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute('SELECT * FROM users WHERE id = % s', (userid, ))
		userdata = cursor.fetchone()
		return render_template('admin/updateuser.html', userdata = userdata)
	return redirect(url_for('adlogin'))

@app.route('/admin/updateusers/', methods=['GET', 'POST'])
def updateusers():
	msg=''
	if session.get('adloggedin'):
		if request.method == 'POST' and 'aupname' in request.form and 'aupemail' in request.form and 'auppswd' in request.form and 'aupid' in request.form:
			aupname = request.form['aupname']
			aupemail = request.form['aupemail']
			auppswd = request.form['auppswd']
			aupid = request.form['aupid']
			cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
			cursor.execute('UPDATE users SET username = % s, password = % s, email = % s WHERE id = % s', (aupname, auppswd, aupemail, aupid, ))
			mysql.connection.commit()
			msg = 'User updated successfully !'
		return render_template('admin/dashboard.html', msg = msg)
	return redirect(url_for('adlogin'))

@app.route('/admin/deleteuser/')
def deleteuser():
	if session.get('adloggedin'):
		userid = request.args.get('userid')
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute('DELETE FROM users WHERE id = % s', (userid, ))
		mysql.connection.commit()
		return redirect(url_for('userslist'))
	return redirect(url_for('adlogin'))

@app.route('/admin/logout/')
def adlogout():
	session.pop('adloggedin', None)
	session.pop('adid', None)
	session.pop('ademail', None)
	return redirect(url_for('adlogin'))

@app.route('/admin/issuebook/')
def issuebook():
	msg = ''
	if session.get('adloggedin'):
		userid = request.args.get('user_id')
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute('SELECT * FROM books')
		books = cursor.fetchall()
		return render_template('admin/issuebook.html', userid = userid, books = books)

@app.route('/admin/issuebooks/', methods=['GET', 'POST'])
def issuebooks():
	if session.get('adloggedin'):
		if request.method == 'POST' and 'book_id' in request.form and 'user_id' in request.form:
			book_id = request.form['book_id']
			user_id = request.form['user_id']
			cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
			cursor.execute('INSERT INTO issue (book_id, user_id, date) VALUES (% s, % s, % s)', (book_id, user_id, date.today()))
			mysql.connection.commit()
			return redirect(url_for('issuedbookslist'))
	return redirect(url_for('adlogin'))

@app.route('/admin/issuedbookslist/')
def issuedbookslist():
	if session.get('adloggedin'):
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute('SELECT * FROM issue')
		issuedbooks = cursor.fetchall()
		return render_template('admin/issuedbookslist.html', issuedbooks = issuedbooks)
	return redirect(url_for('adlogin'))

@app.route('/admin/requestbooklist')
def requestbooklist():
	if session.get('adloggedin'):
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute('SELECT * FROM request')
		requestbooks = cursor.fetchall()
		return render_template('admin/requestbooklist.html', requestbooks = requestbooks)
	return redirect(url_for('adlogin'))

@app.route('/admin/acceptrequest/')
def acceptrequest():
	msg=''
	if session.get('adloggedin'):
		row_id = request.args.get('row_id')
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute('SELECT * FROM request WHERE id = % s', (row_id, ))
		requestdata = cursor.fetchone()
		book_id = requestdata['book_id']
		user_id = requestdata['user_id']
		cursor.execute('INSERT INTO issue (book_id, user_id, date) VALUES (% s, % s, % s)', (book_id, user_id, date.today()))
		mysql.connection.commit()
		cursor.execute('DELETE FROM request WHERE id = % s', (row_id, ))
		mysql.connection.commit()
		msg = 'Request accepted successfully !'
	return render_template('admin/dashboard.html', msg = msg)

@app.route('/admin/rejectrequest/')
def rejectrequest():
	msg=''
	if session.get('adloggedin'):
		row_id = request.args.get('row_id')
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute('DELETE FROM request WHERE id = % s', (row_id, ))
		mysql.connection.commit()
		msg = 'Request rejected successfully !'
	return render_template('admin/dashboard.html', msg = msg)

@app.route('/admin/returnbook/')
def returnbook():
	if session.get('adloggedin'):
		row_id = request.args.get('id')
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute('SELECT * FROM issue WHERE id = % s', (row_id, ))
		issuedata = cursor.fetchone()
	return render_template('admin/returnbook.html', issuedata = issuedata)

@app.route('/admin/returnbooks/', methods=['GET', 'POST'])
def returnbooks():
	if session.get('adloggedin'):
		if request.method == 'POST' and 'id' in request.form:
			id = request.form['id']
			cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
			cursor.execute('DELETE FROM issue WHERE id = % s ', (id, ))
			mysql.connection.commit()
			return redirect(url_for('issuedbookslist'))
	return redirect(url_for('adlogin'))

def getallbooks():
	cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
	cursor.execute('SELECT * FROM books')
	books = cursor.fetchall()
	return books
app.jinja_env.globals.update(getallbooks=getallbooks) 


def getbooknamebyid(id):
	cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
	cursor.execute('SELECT * FROM books WHERE id = % s', (id, ))
	book = cursor.fetchone()
	return book['name']
app.jinja_env.globals.update(getbooknamebyid=getbooknamebyid) 

def getuseremailbyid(id):
	cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
	cursor.execute('SELECT * FROM users WHERE id = % s', (id, ))
	user = cursor.fetchone()
	return user['email']
app.jinja_env.globals.update(getuseremailbyid=getuseremailbyid)

def getfinebyid(id):
	cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
	cursor.execute('SELECT * FROM issue WHERE id = % s', (id, ))
	issuedata = cursor.fetchone()
	issued_date = issuedata['date']
	current_date = date.today()
	days = (current_date - issued_date).days
	if days > 7:
		fine = days * 5
	else:
		fine = 0
	return fine
app.jinja_env.globals.update(getfinebyid=getfinebyid)