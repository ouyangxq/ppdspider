# coding:utf-8
'''
Created on 2016年3月20日

@author: Administrator
'''

class PPDBlackLoan(object):
    '''
    classdocs
    '''
    loanid = -1
    loan_title = None
    ppbaouserid = None
    loanuserid = None
    bid_money = -1
    returned_money = -1
    overdue_money = -1 
    overdue_days = -1
    history_max_overdue_days = -1
    overdue_date = "None"
    return_date  = None
    

    def __init__(self):
        '''
        Constructor
        '''
    def get_summary(self):
        
        summary = "%d,\"%s\",\"%s\",\"%s\",%d,%4.2f,%4.2f,%d,%d" % (self.loanid, self.loan_title, \
                  self.ppbaouserid, self.loanuserid, self.bid_money, self.returned_money, self.overdue_money, self.overdue_days, \
                  self.history_max_overdue_days)
        if self.overdue_date is not None and self.overdue_date != 'None':
            sql_date = self.overdue_date.isoformat()
            summary += ",%s" % (sql_date)
        return summary
    
    def get_sql_insert_statement(self):
        sql_date = self.overdue_date.isoformat()
        db_stat = "insert into blacklist (loanid, ppbaouserid, loanuserid, loantitle, bid_money, returned_money, overdue_money,overdue_days,history_max_overdue_days, overdue_date) values (%d,\"%s\",\"%s\",\"%s\",%d,%4.2f,%4.2f,%d,%d,\"%s\")" % (self.loanid, \
                  self.ppbaouserid, self.loanuserid, self.loan_title, self.bid_money, self.returned_money, self.overdue_money, self.overdue_days, \
                  self.history_max_overdue_days, sql_date)
        return db_stat
    
    def update_black_days(self):
        db_stat = "update blacklist set overdue_days=%d where loanid=%d and ppbaouserid=\"%s\"" % (self.overdue_days, self.loanid, self.ppbaouserid)
        return db_stat
    
    def clear_black_record_on_return(self, today):
        today_iso = today.isoformat()
        db_stat = "update blacklist set return_date=\"%s\" where loanid=%d and ppbaouserid=\"%s\"" % (today_iso, self.loanid, self.ppbaouserid)
        return db_stat 
    