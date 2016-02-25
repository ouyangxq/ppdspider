'''
Created on 20160220

@author: Administrator
'''
from ds import PPD
class MyBid(PPD):
    '''
    classdocs
    '''
    loanid = None
    date = None
    money = -1
    reason = "Possibly Good Bid"
    def __init__(self, params):
        '''
        Constructor
        '''
        self.loanid = params['loanid']
        self.date   = params['date']
        self.money  = params['money']
        self.reason = params['reason']
        
    def get_db_insert_statement(self):
        db_stat = "insert into mybid values(%d, %s, %d, %s)" % (self.loanid, self.date, self.money, self.reason)
        return db_stat