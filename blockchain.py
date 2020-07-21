import hashlib
import pymongo
import random
from trpool import Pool
import datetime
import time
import json
myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["test"]


class Blockchain:
    def __init__(self,me):
        self.state = 0
        self.chain = []
        self.create_genesis_block()
        self.transactions=Pool()
        self.pending=[]
        self.mineadd=[]
        self.me=me
        self.update_state=False

    def clear_blockchain(self):
        mydb.test.delete_many({})

    def insert_block(self,block):
        mydb.test.insert_one(block)

    def create_genesis_block(self):
        le=mydb.test.find_one({'message':'Genesis','random_num':'0'})
        print(le)
        if le!=None:
            return
        mydb.test.delete_many({})
        genesis = {
            'sender':'',
            'receiver':'',
            '_id':'0',
            'random_num':'0',
            'parent_hash':'0000000000000000',
            'msg-type':'block',
            'message':'Genesis',
        }
        self.insert_block(genesis)

    def get_blockchain(self):
        u1=mydb.test.find({})
        l1=[]
        for el in u1:
            l1.append(el)
        return l1

    def valid_chain(self):
        chain=mydb.test.find({})
        curr_block=chain[0]
        gene_block=chain[0]
        for el in chain:
            if el==gene_block:
                continue
            if hashlib.sha256(json.dumps(curr_block).encode('utf-8')).hexdigest()!=el['parent_hash']:
                return False
            curr_block=el
        
        return True

    def new_transaction(self, sender, receiver, message,idd=0):
        ts = str(datetime.datetime.now())
        if idd!=0:
            ts=idd
        tr={
                'sender': sender,
                'receiver': receiver,
                'message': message,
                'msg-type': 'transaction',
                'id': ts,
        }
        print(tr)
        self.transactions.add(tr)
        rnummsg={
            'id':ts,
            'tid':tr['id'],
            'rnum':random.random(),
            'msg-type':'random_number',
            'me':self.me,
        }
        self.update_transactions(rnummsg)
        print('trrnummsg')
        print(tr)
        print(rnummsg)
        print('transactions')
        print(self.transactions)
        return([tr,rnummsg])

    

    def validate_block(self,block_received):
        temp=block_received
        for el in self.pending:
            if el['tid']==temp['_id'] and min(el['rlist'])==temp['random_num'] and el['traction']['message']==temp['message'] and el['traction']['sender']==temp['sender'] and el['traction']['receiver']==temp['receiver']:
                self.pending.remove(el)
                return True
        return False

    def mine(self,ttbb):
        rn=min(ttbb['rlist'])
        ttbb=ttbb['traction']
        last_block = mydb.test.find().sort([('_id', -1)]).limit(1)[0]
        pahh=hashlib.sha256(json.dumps(last_block).encode('utf-8'))
        block={
            'sender':ttbb['sender'],
            'receiver':ttbb['receiver'],
            '_id':ttbb['id'],
            'random_num':rn,
            'msg-type':'block',
            'message':ttbb['message'],
            'parent_hash':pahh.hexdigest(),
        }
        print('lol')
        print(self.validate_block(block))
        print('lol')
        self.insert_block(block)
        # transaction_hash = hashlib.sha256(block['message'].encode())
        # parent_block_cursor = mydb.blockchain.find().sort([('timestamp', -1)]).limit(1)
        # parent_block_string = parent_block_cursor[0]['sender']+parent_block_cursor[0]['receiver']+parent_block_cursor[0]['timestamp']+parent_block_cursor[0]['random_num']+parent_block_cursor[0]['transaction_hash']+parent_block_cursor[0]['parent_hash']+parent_block_cursor[0]['msg-type']+parent_block_cursor[0]['message']
        # print(parent_block_string)
        # parent_hash = hashlib.sha256(parent_block_string.encode())
        # print(parent_hash.hexdigest())
        # block['transaction_hash'] = transaction_hash
        # block['parent_hash'] = parent_hash
        # mydb.blockchain.insert_one(block)

    def update_transactions(self,msg):
        for el in self.transactions.q:
            if(el['tid']==msg['tid']):
                el['rlist'].append(msg['rnum'])
                
                while self.transactions.see()!=None and len(self.transactions.see()['rlist'])==3:
                    temp=self.transactions.remove()
                    self.pending.append(temp)
                    self.mineadd.append(temp)
                return
        m1={}
        m1['id']=msg['tid']
        m1['msg-type']='transaction'
        self.transactions.add(m1)
        self.update_transactions(msg)
        
    