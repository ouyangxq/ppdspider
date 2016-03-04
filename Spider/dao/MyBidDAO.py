'''
Created on 20160222

@author: Administrator
'''
from datetime import datetime

class MyBidDAO(object):
    '''
    classdocs
    '''
    dao = None

    def __init__(self, ppddao):
        '''
        Constructor
        '''
        self.dao = ppddao
    
    def insert_bid_record(self, loanid, now, money, ppduserid, reason):
        sqlnow = now.strftime('%Y-%m-%d %X')
        db_stat = "insert into mybid (loanid, datetime, money, ppduserid, reason) values(%d, \"%s\", %d, \"%s\", \"%s\")" % (loanid, sqlnow, money, ppduserid, reason)
        #logging.info("Inserting new loan into DB: %s" %(db_stat))
        result  = self.dao.execute(db_stat)
        return result