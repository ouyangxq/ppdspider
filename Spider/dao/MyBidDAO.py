'''
Created on 20160222

@author: Administrator
'''

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
    
    def insert_bid_record(self, loanid, date, money, reason):
        date_iso = date.isoformat()
        db_stat = "insert into mybid values(%d, \"%s\", %d, \"%s\")" % (loanid, date_iso, money, reason)
        #logging.info("Inserting new loan into DB: %s" %(db_stat))
        result  = self.dao.execute(db_stat)
        return result