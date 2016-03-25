'''
Created on 2016 Mar 20

@author: Administrator
'''

import logging
from datetime import date

class BlackListDAO(object):
    '''
    classdocs
    '''
    ppddao = None

    def __init__(self, dao):
        '''
        Constructor
        '''
        self.ppddao = dao
        
    def update_blacklist(self, ppbaouserid, blacklist):
        # Blacklist is instance of PPDBlackLoan
        existing_list = self.get_existing_blacklist(ppbaouserid)
        for blackloan in blacklist:
            " Now all loanids are for ppbaouserid, so we can just compare it"
            if blackloan.loanid in existing_list:
                update_stat = blackloan.update_black_days()
                existing_list.remove(blackloan.loanid)
                self.ppddao.execute(update_stat)
            else:
                insert_stat = blackloan.get_db_insert_statement()
                self.ppddao.execute(insert_stat)
        ''' If any item left in existing_list, that must has been payed back '''
        today = date.today().isoformat()
        for loanid in existing_list:
            sql = "update blacklist set return_date=\"%s\" where loanid=%d and ppbaouserid=\"%s\"" % (today, loanid, ppbaouserid)
            self.ppddao.execute(sql)
            
    
    def get_existing_blacklist(self, ppbaouserid):
        sql = "select loanid from blacklist where ppbaouserid=\"%s\" and return_date is NULL" % (ppbaouserid)
        logging.info("Get Existing Blacklist: %s" % (sql))
        black_loanid_list = []
        if (self.ppddao.execute(sql)):
            results = self.ppddao.dbcursor.fetchall()
            for item in results:
                black_loanid_list.append(item[0])
        else:
            logging.warn("No History BLack Loan List for User %s" % ppbaouserid)
        
        return black_loanid_list
                
                