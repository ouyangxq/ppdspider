#!python
#-*- coding:utf-8 -*-
'''
Created on 2016年2月20日

@author: Administrator
'''
import logging
from datetime import datetime
from datetime import date
from datetime import timedelta

class PPDLoanDAO(object):
    '''
    classdocs
    '''
    dao = None

    def __init__(self, ppddao):
        '''
        Constructor
        '''
        self.dao = ppddao
        
    def insert(self, ppdloan):
        if (self.if_a_new_loan(ppdloan.loanid)):
            db_stat = ppdloan.get_db_insert_statement()
            #logging.info("Inserting new loan into DB: %s" %(db_stat))
            result  = self.dao.execute(db_stat)
            return result
        else:
            logging.debug("Insert LoanInfo: %d is already in DB.")
            return True;
    
    def if_a_new_loan(self,loanid):
        db_stat = "select loanid from ppdloan where loanid=%d" % (loanid)
        result  = self.dao.execute(db_stat)  # If in, return True, else, False
        # Can be simplified by !result
        if (result == False):
            return True
        else:
            return False
    
    def get_last_2_days_loanids(self):
        today = date.today();
        date_iso = today.isoformat()
        two_days_ago = today + timedelta(days = -2)
        two_days_iso = two_days_ago.isoformat()
        db_stat = "select loanid from ppdloan where datetime>=\"%s\"" %(two_days_iso)
        result  = self.dao.execute(db_stat)
        if result == False:
            logging.warn("Get Existing LoanIDs of Last 2 days: No Result!!!")
            return []
        else:
            data = self.dao.dbcursor.fetchall()
            loanids = []
            for loanid in data:
                loanids.append(loanid[0])
            return loanids
    
if __name__ == '__main__':
    from dao.PPDDAO import PPDDAO
    from ds.PPDLoan import PPDLoan
    from ds.PPDUser import PPDUser
    from datetime import date

    ppddao = PPDDAO({'host':'localhost','username':'xiaoqi','password':'XiaoqiDB.1','database':'ppdai'})
    ppddao.connect()
    ppdloan_dao = PPDLoanDAO(ppddao)
    #sql_stat = 'insert into ppdloan (loanid,date,ppdrate,loanrate,money,maturity,userid,loantitle,age,history_return_ontime,history_overdue_in15d,history_overdue_mt15d,history_total_loan,history_left_loan,history_left_lend) values (8822451,"2016-02-21","AAA", 7.0,3000,12,"pdu6310825153","标题",46,1,0,0,30000,29419.12,108230.77)'
    #print "Execute: " + sql_stat
    #ppddao.execute(sql_stat)
    
    today = date.today()
    ppdloan = PPDLoan({'loanid':8822451, 'date':today, 'loanrate':7.0, 'ppdrate':'AAA', \
                           'money':3000, 'maturity':12, 'userid':'pdu6310825153', 'age': 46})
    ppduser = PPDUser({'userid':'pdu6310825153', 'gender': '男', 'age': 46, 'marriage': '已婚', \
                           'house': '自住无按揭', 'car': '有', 'education_level': '本科'})
    ppdloan.set_ppduser(ppduser)
    ppdloan.set_history_info(1, 0, 0, 30000, 29419.12, 108230.77)
    ppdloan.loantitle = "None".decode('gbk').encode('utf-8')
    print ppdloan.get_db_insert_statement()
    result = ppdloan_dao.insert(ppdloan)
    
    
    ppddao.disconnect()
    