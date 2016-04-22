#-*- coding:utf-8 -*-
'''
Created on 2016/02/20
This Module is the data structure for PPDLoan information
Notice the user information are stored in PPDUser
@change: 2016/02/26: change date to datetime 
@author: Administrator
'''

from PPD import PPD
from util.PPBaoUtil import PPBaoUtil
import re

TableDefinition = '''
     loanid integer not null primary key,
     datetime datetime not null,
     ppdrate char(3) not null,
     loanrate FLOAT(4,2) not null,
     money integer not null,
     maturity integer not null,
     userid char(15) not null,
     loantitle varchar(30),
     age integer not null,
     history_return_ontime integer not null,
     history_overdue_in15d integer not null,
     history_overdue_mt15d integer not null,
     history_total_loan integer not null,
     history_left_loan double(10,2) not null,
     history_total_lend double(10,2) not null
'''

class PPDLoan(PPD):
    '''
    data structure for ppdai loan
    '''
    loanid = -1
    datetime = None # Store the datetime that we capture this Loan
    ppdrate = None  # AAA, AA, A, B, C, D, E, F, G
    loanrate = 0.0  # loan rate can be a float. e.g. 20.5
    money = 1       # loan money
    maturity = 1    # in month
    userid   = 'userId'     # normally start with pdu
    loantitle = None
    age  = None
    history_return_ontime = -1
    history_overdue_in15d = -1
    history_overdue_mt15d = -1
    history_total_loan    = 0       # total loan will always be in
    history_left_loan     = 0.0     # left loan can be float
    history_left_lend     = 0.0     # money that this user lend to other people, more is better. 
    ppduser               = None    #Reference to PPDUser
    ''' 20160307: Add score and bid '''
    score                 = 0
    bid                   = 0
    has_30or36rate_loan_history  = 0
    has_lt1000_loan_history = 0
    is_shandian_loan      = 0
    ''' This is an indicator of the risk at some point, 
    if the new_total_loan is much less than history_highest_total_loan, then it's quite possible this will be returned on time 
    '''
    new_total_loan        = 0.0     # New Total Loan
    history_highest_total_loan  = 0.0     # History Highest Loan
    
    shandian_pattern = re.compile('.*的闪电借款')
    
    def __init__(self, params):
        '''
        Constructor
        '''
        PPD.__init__(self, 'ppdloan')
        self.loanid     = params['loanid']
        self.datetime   = params['datetime']
        self.ppdrate    = params['ppdrate']
        self.loanrate   = params['loanrate']
        self.money      = params['money']
        self.maturity   = params['maturity']
        self.userid     = params['userid'] 
        self.age        = params['age']
    
    def set_ppduser(self, ppduser):
        self.ppduser = ppduser
    
    def set_history_info(self, return_ontime, overdue_in15d, overdue_mt15d, total_loan, left_loan, left_lend):
        self.history_return_ontime = return_ontime
        self.history_overdue_in15d = overdue_in15d
        self.history_overdue_mt15d = overdue_mt15d
        self.history_total_loan    = total_loan
        self.history_left_loan     = left_loan
        self.history_left_lend     = left_lend
        self.new_total_loan        = self.money + self.history_left_loan - self.history_left_lend 
    
    def set_loantitle(self, title):
        self.loantitle = title
        if (re.match(self.shandian_pattern, title)):
            self.is_shandian_loan = 1
    
    def get_db_insert_statement(self):
        sql_datetime = self.datetime.strftime("%Y-%m-%d %X")
        db_stat = "insert into ppdloan (loanid, datetime, ppdrate, loanrate, money, maturity, userid, loantitle, age, " + \
                    "history_return_ontime, history_overdue_in15d,history_overdue_mt15d, history_total_loan, history_left_loan, history_left_lend,score,bid, " + \
                    "has_30or36rate_loan_history, has_lt1000_loan_history, new_total_loan, history_highest_total_loan)" + \
                    " values (%d,\"%s\",\"%s\",%4.1f,%d,%d,\"%s\",\"%s\",%d,%d,%d,%d,%d,%6.2f,%6.2f,%d,%d,%d,%d,%6.2f,%6.2f)" % (self.loanid, \
                    sql_datetime,self.ppdrate,self.loanrate,self.money,self.maturity,self.userid,self.loantitle, \
                    self.age,self.history_return_ontime,self.history_overdue_in15d,self.history_overdue_mt15d, \
                    self.history_total_loan,self.history_left_loan,self.history_left_lend,self.score,self.bid, \
                    self.has_30or36rate_loan_history, self.has_lt1000_loan_history, self.new_total_loan, self.history_highest_total_loan)
        return db_stat
    
    def get_loan_summary(self):
        rank = PPBaoUtil.get_university_rank(self)
        summary = "Rate(%s),Loan(%d,%d,%d),Education(%s,%s,%s,%d),History(%d,%d,%d),HistoryLoan(%d,%d,%d,%d,%d),Age(%d),%s" \
            % (self.ppdrate, self.money, self.loanrate, self.maturity,self.ppduser.education_university, \
               self.ppduser.education_level, self.ppduser.education_type, rank, self.history_return_ontime, self.history_overdue_in15d, \
               self.history_overdue_mt15d, self.history_total_loan, self.history_left_loan, self.history_left_lend, self.history_highest_total_loan, self.new_total_loan, self.age, \
               self.ppduser.gender)
        certs = None
        if self.ppduser.getihu_cert == 1:
            certs = ",Cert(个体户" if certs is None else (certs + ",个体户")
        if self.ppduser.bank_details_cert == 1:
            certs = ",Cert(银行流水" if certs is None else (certs + ",银行流水")
        if self.ppduser.job_cert == 1:
            certs = ",Cert(工作" if certs is None else (certs + ",工作")
        if self.ppduser.ren_hang_trust_cert == 1:
            certs = ",Cert(征信" if certs is None else (certs + ",征信")
        if self.ppduser.shouru_cert == 1:
            certs = ",Cert(收入" if certs is None else (certs + ",收入")
        if self.ppduser.alipay_cert == 1:
            certs = ",Cert(支付宝" if certs is None else (certs + ",支付宝")
        if self.ppduser.student_cert == 1:
            certs = ",Cert(学生证" if certs is None else (certs + ",学生证")
        if self.ppduser.driver_cert == 1:
            certs = ",Cert(驾驶证" if certs is None else (certs + ",驾驶证")
        certs = ",Cert(NA)" if certs is None else (certs + ")")
        summary += certs
        if self.is_shandian_loan == 1:
            summary += ",闪电借款"
        return summary