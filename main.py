from flask import Flask,session,render_template,request
import mysql.connector
import socket
import datetime

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  passwd="",
  database="blocksec"
)
mycursor = mydb.cursor()
print(mydb) 

mycursor.execute('DELETE from users')
mydb.commit()

app = Flask(__name__)
app.secret_key='secret'

@app.route('/')
def h1():
	return render_template('home.html')

@app.route('/logout',methods=['POST'])
def logout():
	mycursor.execute('SELECT * FROM users WHERE uname=(%s)',(request.form.get('luname'),))
	logged_in_users = mycursor.fetchall()
	print(session)
	if len(logged_in_users)!=0:
		mycursor.execute('DELETE FROM users WHERE uname = (%s) ',(request.form.get('luname'),))
		mydb.commit()
		# session.pop(session['username'],None)
	return render_template('home.html')

@app.route('/logi',methods=['POST'])
def logi():
	users=['u1','u2','u3','u4']
	n1=request.form.get('uname')
	# print(request.headers['X-Real-IP'])
	# print(request.headers)
	print(request.remote_addr)
	if n1 in users:
		try:
			session['username']=n1
			print(session['username'])
			portte=-1
			mycursor.execute('select port from uports where uname=%s',(n1,))
			portte=mycursor.fetchall()[0][0]
			mycursor.execute("INSERT INTO users VALUES (%s,%s)",(n1,request.remote_addr,))
			mydb.commit()
		except Exception as E:
			print(E)
			return str(portte)
		return str(portte)
	return 'FUCK OFF'


@app.route('/ul',methods=['POST'])
def ul():
	n1=request.form.get('num')
	ans=''
	if n1=='1':
		mycursor.execute('SELECT * FROM users')
		row=mycursor.fetchall()
		for el in row:
			ans+=el[1]+' '
		return ans
	return 'FUCK OFF!!!!'
@app.route('/curd',methods=['GET'])
def curd():
	return str(datetime.datetime.now())

if __name__=='__main__':
	app.run()
