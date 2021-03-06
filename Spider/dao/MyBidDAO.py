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
    
    def insert_bid_record(self, loanid, now, money, ppduserid, reason, strategy_name):
        sqlnow = now.strftime('%Y-%m-%d %X')
        db_stat = "replace into mybid (loanid, datetime, money, ppduserid, reason, strategy_name) values(%d, \"%s\", %d, \"%s\", \"%s\", \"%s\")" % (loanid, sqlnow, money, ppduserid, reason, strategy_name)
        #logging.info("Inserting new loan into DB: %s" %(db_stat))
        result  = self.dao.execute(db_stat)
        return result