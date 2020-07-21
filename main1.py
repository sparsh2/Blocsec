# run on your system
# new file
#test

import socket
import requests
import threading
import json
import datetime
import time
import netifaces as ni
import random
import pymongo
import hashlib
from blockchain import Blockchain
import sys
import _thread
 
ip = "http://192.168.43.168:5000"

page = "/ul"
login_p = '/logi'
logout_p = '/logout'
data = {
    'num' : '1'
}


sport = 0
ssockets = []
chain_set=[]
 
lap = [12340,12341,12342,12344,12345,12346,12347]
 
user_count = len(lap)

message_queue=[]

# Login
def login(user):
    d = {
        'uname' : user
    }
    r = requests.post(url = ip+login_p, data = d)
    return r.text
 
def logout():
    print(threading.get_ident())
    r = requests.post(url = ip+logout_p,data={'luname':myuname})
    print('Successfully Logged out from server')
    cclose()
    print('Successfully Closed all sockets')
    try:
        _thread.interrupt_main()
    except KeyboardInterrupt:
        try:
            _thread.interrupt_main()
        except KeyboardInterrupt:
            pass
        pass
    _thread.interrupt_main()
    print('returning')
 
def get_active_users():
    r = requests.post(url = ip+page, data = data)
    user_list = r.text.split()
    return user_list
 
def handle_transaction(msg):
    send_all(blockchain.new_transaction(msg['sender'],msg['receiver'],msg['message'],msg['id'])[1])

def handle_randnum(msg):
    blockchain.update_transactions(msg)

def handle_blockchain_request(blockchain_request):
    # mybl=mydb.test.find({})
    # bllt=[]
    # for el in mybl:
    #     bllt.append(el)
    bllt=blockchain.get_blockchain()
    print(bllt)
    a={'msg-type':'blockchain','blockchain':bllt}
    send_msg(a,blockchain_request['sip'])

def handle_blockchain(received_blockchain):
    global chain_set
    received_blockchain=received_blockchain['blockchain']
    chain_set.append(blockchain)

def handle_msg(msg):
    print(threading.get_ident())
    try:
        if(msg['msg-type']=='transaction'):
            handle_transaction(msg)
        elif(msg['msg-type']=='random_number'):
            handle_randnum(msg)
        elif(msg['msg-type']=='blockchain_request'):
            handle_blockchain_request(msg)
        elif(msg['msg-type']=='blockchain'):
            handle_blockchain(msg)
    except Exception as e:
        print(e)

def dl():
    print('dl is created')
    port=5001
    sdl = socket.socket()
    sdl.bind(('',port))
    sdl.listen(5)
    while(True):
        c,addr = sdl.accept()
        hval='hey'
        hval=json.dumps(hval).encode('utf-8')
        c.send(hval)
        nt = json.loads(c.recv(1024).decode('utf-8'))

        if 'logout' in nt.keys():
            logout()
            c.close()
            _thread.interrupt_main()
            return
        else:
            print(threading.get_ident())
            print('received transaction from html')
            temp=blockchain.new_transaction(nt['sender'],nt['receiver'],nt['message'])
            send_all(temp[0])
            send_all(temp[1])        
            c.close()

def socket_listen(soc, port):
    print('listening on')
    print(port)
    soc.bind(('', port))
    soc.listen()
 
    while True:
        c, addr = soc.accept()
        val='connected'
        val=json.dumps(val).encode('utf-8')
        c.send(val)
        msg = c.recv(1024)
        msg=json.loads(msg.decode('utf-8'))
        print('received')
        print(msg)
        val='received'
        val=json.dumps(val).encode('utf-8')
        c.send(val)
        handle_msg(msg)
        c.close()


def init():
    global sport,me,myuname
    myuname=sys.argv[1]
    sport=int(login(myuname))
    global ssockets
    ssockets = [socket.socket(socket.AF_INET, socket.SOCK_STREAM) for _ in range(user_count)]

    me = str(ni.ifaddresses('wlan0')[ni.AF_INET][0]['addr'])
    print(me)
    print('sport')
    print(sport)
    
    c1 = -1
    for soc in ssockets:
        c1 += 1
        if(lap[c1] == sport):
            continue
        threading.Thread(target = socket_listen,args = (soc, lap[c1])).start()

    threading.Thread(target=dl).start()
    threading.Thread(target=b_send_msg).start()
    global blockchain
    blockchain = Blockchain(sys.argv[1])
    threading.Thread(target=chek).start()
    
def send_msg(msg,sip):
    global message_queue
    message_queue.append([msg,sip])

def b_send_msg():
    global message_queue
    while(True):
        if(len(message_queue)!=0):
            m1=message_queue.pop(0)
            a_send_msg(m1[0],m1[1])


def a_send_msg(msg,sip):
    # if(msg=='close'):
    #     cclose()
 
    # if(msg == 'logout'):
    #     logout()
    
    soc = socket.socket()
    # print('portszz')
    # print(sip)
    # print(sport)
    soc.connect((sip,sport))

    s1=json.loads(soc.recv(1024).decode('utf-8'))
    msg=json.dumps(msg).encode('utf-8')
    print('sending')
    print(msg)
    soc.send(msg)
    rs=json.loads(soc.recv(1024).decode('utf-8'))
    # print(rs)
    soc.close()
    return rs

def send_all(msg):
    ul1=get_active_users()
    rsl=[]
    for us in ul1:
        if(us != me):
            print(us,me)
            rsl.append(send_msg(msg,us))
    return rsl

def cclose():
    for s in ssockets:
        s.close()

def get_majority_element(n_list):
    fr=0
    me=-1
    for el in n_list:
        if type(me)==type(el) and me==el:
            fr=fr+1
        else:
            fr=fr-1
        if fr==0 or -1:
            me=el
    fr=0
    fl=False
    for el in n_list:
        if el==me:
            fr=fr+1
    if fr>len(n_list)/2:
        fl=True
    return me,fl

def validate_and_update(update_necessary=True):
    global chain_set,me
    print(me)
    sm=blockchain.valid_chain()
    if sm==False or update_necessary:
        blockchain.update_state=True
        # u1=mydb.test.find({})
        # l1=[]
        # for el in u1:
        #     l1.append(el)
        chain_set.append(blockchain.get_blockchain())
        print(chain_set)
        send_all({'msg-type':'blockchain_request','sip':me})
        nu=get_active_users()
        blockchain.clear_blockchain()
        blockchain.create_genesis_block()
        while len(chain_set)!=nu:
            pass
        if len(chain_set)==1:
            blockchain.update_state=False
            return
        maxl=[len(el) for el in chain_set]
        maxl,is_there=get_majority_element(maxl)
        if if_there==False:
            maxl=min([len(el) for el in chain_set])
        for el in range(1,maxl):
            blockchain.insert_block(get_majority_element([el1[el] for el1 in chain_set])[0])
        chain_set=[]
        blockchain.update_state=False

def chek():
    global blockchain
    while True:
        if len(blockchain.mineadd)!=0 and blockchain.update_state==False:
            # sm=blockchain.valid_chain()
            # print('valid chain')
            # print(sm)
            # if sm:
            #     temp=blockchain.mineadd.pop()
            #     blockchain.mine(temp)
            # else:
            #     blockchain.update_chain()
            # validate_and_update(1)
            temp=blockchain.mineadd.pop()
            blockchain.mine(temp)

        time.sleep(0.5)



init()