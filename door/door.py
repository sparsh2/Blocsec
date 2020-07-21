from flask import Flask,session,render_template,request
import socket
import json
import netifaces as ni
import time
import _thread

app = Flask(__name__)
app.secret_key='secret'



@app.route('/')
def h1():
	return render_template('transaction.html')

@app.route('/generate_new_transaction', methods=['POST'])
def h2():
    global s
    tr={
        'sender':request.form.get('sender'),
        'receiver':request.form.get('receiver'),
        'message':request.form.get('message'),
    }
    s = socket.socket()	
    port = 5001
    s.connect((str(ni.ifaddresses('wlan0')[ni.AF_INET][0]['addr']),port))
    print(json.loads(s.recv(1024).decode('utf-8')))
    tr = json.dumps(tr).encode('utf-8')
    s.send(tr)
    s.close()
    time.sleep(3)
    return render_template('transaction.html')

@app.route('/logout', methods=['POST'])
def h3():
    global s
    tr={
        'logout':1,
    }
    s = socket.socket()	
    port = 5001
    s.connect((str(ni.ifaddresses('wlan0')[ni.AF_INET][0]['addr']),port))
    # print(json.loads(s.recv(1024).decode('utf-8')))
    tr = json.dumps(tr).encode('utf-8')
    s.send(tr)
    s.close()
    try:
        _thread.interrupt_main()
    except KeyboardInterrupt:
        _thread.interrupt_main()
        pass
    _thread.interrupt_main()
    return render_template('transaction.html')



if __name__=='__main__':
    app.run(host='127.0.0.1', port='5002')
