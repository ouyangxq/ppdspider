'''
Created on 2016 Mar 31st

@author: Administrator
'''
from retest import bid_response_html
'''
create table myprofit (
    date date not null,
    ppbaouserid char(15) not null,
    realized_profits FLOAT(4,2) not null,
    unrealized_profilts FLOAT(4,2) not null,
    blacklist_count int not null,
    blacklist_bid_money int not null,
    blacklist_returned_money FLOAT(4,2) not null,
    blacklist_overdue_money FLOAT(4,2) not null,
    max_loss_money FLOAT(4,2) not null,
    min_profits FLOAT(4,2) not null,
    primary key (date,ppbaouserid)
);
'''
class MyProfit(object):
    '''
    classdocs
    '''
    date = None
    ppbaouserid = None
    realized_profits = 0.0
    unrealized_profits = 0.0
    blacklist_count = 0
    blacklist_bid_money = 0
    blacklist_returned_money = 0.0,
    blacklist_overdue_money = 0.0
    max_loss_money = 0.0
    min_profits = 0.0

    def __init__(self, date, ppbaouserid):
        '''
        Constructor
        '''
        self.date = date
        self. ppbaouserid = ppbaouserid
    
    def set_profit(self, realized, unrealized):
        self.realized_profits = realized
        self.unrealized_profits = unrealized
    
    def set_blacklist(self, count, bid, returned, overdue):
        # Shall be called after realized profit is set
        self.blacklist_bid_money = bid
        self.blacklist_count = count
        self.blacklist_returned_money = returned
        self.blacklist_overdue_money = overdue
        self.max_loss_money = self.blacklist_bid_money - self.blacklist_returned_money
        self.min_profits = self.realized_profits - self.max_loss_money
    
    def get_summary(self):
        s = "Date(%s),User(%s)" % (self.date.isoformat(), self.ppbaouserid)
        s += ",ProfitRealized(%d),UnRealized(%d)" % (self.realized_profits, self.unrealized_profits)
        s += ",BlackListCount(%d),MaxLoss(%d),MinProfit(%d)" % (self.blacklist_count, self.max_loss_money, self.min_profits)
        return s
    
    def get_sql_insert_statement(self):
        sql_date = self.date.isoformat();
        sql_statement = "REPLACE into myprofit (date,ppbaouserid,realized_profits,unrealized_profits," + \
                    "blacklist_count,blacklist_bid_money,blacklist_returned_money,blacklist_overdue_money," + \
                    'max_loss_money,min_profits) values ' + \
                    '("%s", "%s", %4.2f, %4.2f, %d, %d, %4.2f, %4.2f, %4.2f, %4.2f) ' % \
                    (sql_date, self.ppbaouserid, self.realized_profits, self.unrealized_profits, \
                     self.blacklist_count, self.blacklist_bid_money, self.blacklist_returned_money, self.blacklist_overdue_money, \
                     self.max_loss_money, self.min_profits)
        return sql_statement;
        