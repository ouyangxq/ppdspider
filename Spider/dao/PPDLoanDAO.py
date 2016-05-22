#!python
#-*- coding:utf-8 -*-
'''
Created on 2016年2月20日

@author: Administrator
'''
import logging
from datetime import date
from datetime import timedelta
from ds.PPDLoan import PPDLoan

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
            #logging.debug("Insert LoanInfo: %d is already in DB.")
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
        return self.get_last_n_days_loanids(2)
    
    def get_last_n_days_loanids(self, ndays):
        today = date.today();
        ndays_ago = today + timedelta(days = -ndays)
        ndays_ago_iso = ndays_ago.isoformat()
        db_stat = "select loanid from ppdloan where datetime>=\"%s\"" %(ndays_ago_iso)
        result  = self.dao.execute(db_stat)
        if result == False:
            logging.warn("Get Existing LoanIDs of Last %d days: No Result!!!" % (ndays))
            return []
        else:
            data = self.dao.dbcursor.fetchall()
            loanids = []
            for loanid in data:
                loanids.append(loanid[0])
            return loanids
        
    def get_db_ppdloan_by_loanid(self, loanid, userdao):
        db_stat = "select loanid, ppdrate,loanrate,money,maturity,userid,age,history_return_ontime, " \
                    "history_overdue_in15d,history_overdue_mt15d,history_total_loan,history_left_loan, " \
                    "history_left_lend, datetime, loantitle,score, bid, has_30or36rate_loan_history, " \
                    "new_total_loan, history_highest_total_loan " \
                    " from ppdloan where loanid=%d" % (loanid)
        
        if (self.dao.execute(db_stat)):
            # The data are fetched as list of list
            data = self.dao.dbcursor.fetchall()
            results = data[0]
            userid = results[5]
            #dt = datetime.strptime(results[13], "%Y-%m-%d %X")
            # It seems it will return datetime directly for MYSQL datetime type
            dt = results[13]
            
            ppdloan = PPDLoan({'loanid':loanid, 'datetime':dt, 'loanrate':float(results[2]), 'ppdrate':results[1], \
                           'money':int(results[3]), 'maturity':int(results[4]), 'userid':userid, 'age': int(results[6])})
            ppduser = userdao.get_db_ppduser_by_userid(userid)
            ppdloan.ppduser = ppduser
            ppdloan.loantitle = results[14]
            ppdloan.set_history_info(int(results[7]), int(results[8]), int(results[9]), int(results[10]), int(results[11]), int(results[12]))
            ppdloan.has_30or36rate_loan_history = int(results[17])
            ppdloan.new_total_loan = int(results[18])
            ppdloan.history_highest_total_loan = int(results[19])
            return ppdloan
        else:
            logging.error("No ppdloan in DB found for loanid %d" % (loanid))
            return None
    
    def get_ppdloans_by_ndays(self, ndays, userdao):
        today = date.today();
        ndays_ago = today + timedelta(days = -ndays)
        ndays_ago_iso = ndays_ago.isoformat()
        ppduser_hash = userdao.get_all_ppdusers()
        if ppduser_hash is None:
            logging.info("Not able to get ppduser. Exit...")
            return None
        db_stat = "select loanid, ppdrate,loanrate,money,maturity,userid,age,history_return_ontime, " \
                        "history_overdue_in15d,history_overdue_mt15d,history_total_loan,history_left_loan, " \
                        "history_left_lend, datetime, loantitle,score, bid, has_30or36rate_loan_history,new_total_loan, history_highest_total_loan " \
                        " from ppdloan where datetime>\"%s\"" % (ndays_ago_iso)
        ppdloan_list = []
            
        if (self.dao.execute(db_stat)):
                # The data are fetched as list of list
            data = self.dao.dbcursor.fetchall()
            for results in data:
                userid = results[5]
                #dt = datetime.strptime(results[13], "%Y-%m-%d %X")
                # It seems it will return datetime directly for MYSQL datetime type
                dt = results[13]
                    
                ppdloan = PPDLoan({'loanid':results[0], 'datetime':dt, 'loanrate':float(results[2]), 'ppdrate':results[1], \
                                   'money':int(results[3]), 'maturity':int(results[4]), 'userid':userid, 'age': int(results[6])})
                if ppduser_hash.has_key(userid) == False:
                    continue
                ppduser = ppduser_hash[userid]
                ppdloan.ppduser = ppduser
                ppdloan.loantitle = results[14]
                ppdloan.set_history_info(int(results[7]), int(results[8]), int(results[9]), int(results[10]), int(results[11]), int(results[12]))
                ppdloan.has_30or36rate_loan_history = int(results[17])
                ppdloan.new_total_loan = int(results[18])
                ppdloan.history_highest_total_loan = int(results[19])
                ppdloan_list.append(ppdloan)
            return ppdloan_list
        else:
            logging.error("No ppdloan in DB found for in last %d days" % (ndays))
            return None
                    
                    
if __name__ == '__main__':
    from dao.UniversityDAO import UniversityDAO
    from dao.PPDDAO import PPDDAO
    from dao.PPDUserDAO import PPDUserDAO
    from util.PPBaoUtil import PPBaoUtil
    import sys
    reload(sys)
    sys.setdefaultencoding('utf8')

    ppddao = PPDDAO({'host':'localhost','username':'xiaoqi','password':'XiaoqiDB.1','database':'ppdai'})
    ppddao.connect()
    loandao = PPDLoanDAO(ppddao)
    userdao = PPDUserDAO(ppddao)
    unidao = UniversityDAO(ppddao)
    PPBaoUtil.set_university_to_rank(unidao.get_university_ranks())
    loan = loandao.get_db_ppdloan_by_loanid(12000659, userdao)
    print loan.get_loan_summary()
    ppddao.disconnect()