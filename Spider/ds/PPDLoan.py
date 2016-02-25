'''
Created on 2016/02/20
This Module is the data structure for PPDLoan information
Notice the user information are stored in PPDUser
@author: Administrator
'''
#-*- coding:utf-8 -*-

from PPD import PPD

TableDefinition = '''
     loanid integer not null primary key,
     date date not null,
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
    date = None
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
    
    def __init__(self, params):
        '''
        Constructor
        '''
        PPD.__init__(self, 'ppdloan')
        self.loanid     = params['loanid']
        self.ppdrate    = params['ppdrate']
        self.loanrate   = params['loanrate']
        self.money      = params['money']
        self.maturity   = params['maturity']
        self.userid     = params['userid'] 
        self.date       = params['date']
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
    
    def get_db_insert_statement(self):
        date_db = self.date.isoformat()
        db_stat = "insert into ppdloan values (%d,\"%s\",\"%s\",%4.1f,%d,%d,\"%s\",\"%s\",%d,%d,%d,%d,%d,%6.2f,%6.2f)" % (self.loanid, \
                    date_db,self.ppdrate,self.loanrate,self.money,self.maturity,self.userid,self.loantitle, \
                    self.age,self.history_return_ontime,self.history_overdue_in15d,self.history_overdue_mt15d, \
                    self.history_total_loan,self.history_left_loan,self.history_left_lend)
        return db_stat
    