
# coding: utf-8
'''
Created on 2016年5月14日

@author: Administrator
'''
from dao.UniversityDAO import UniversityDAO
from dao.PPDDAO import PPDDAO
from dao.PPDUserDAO import PPDUserDAO
from dao.PPDLoanDAO import PPDLoanDAO
from util.PPBaoUtil import PPBaoUtil
from util.PPBaoConfig import PPBaoConfig
from biz.BidStrategyPlus import BidStrategyPlus
import logging
from time import sleep

import sys
reload(sys)
sys.setdefaultencoding('utf8')
    
class BidStrategyRegression(object):
    ppbao_config = None
    loandao = None
    userdao = None
    bid_strategy = None
    date_to_bids  = {}
    date_to_loans = {}
    strategy_to_bids = {}
    
    def __init__(self, config):
        ppbao_config = PPBaoConfig(config)
        ppdloginid,dbhost,dbuser,dbpwd,dbname = ppbao_config.read_ppbao_config()
        PPBaoUtil.init_logging('test_bid_strategy', ppbao_config.logdir)
        ppddao = PPDDAO({'host':dbhost,'username':dbuser,'password':dbpwd,'database':dbname})
        ppddao.connect()
        self.loandao = PPDLoanDAO(ppddao)
        self.userdao = PPDUserDAO(ppddao)
        unidao = UniversityDAO(ppddao)
        PPBaoUtil.set_university_to_rank(unidao.get_university_ranks())
        self.bid_strategy = BidStrategyPlus(ppbao_config)
        self.date_to_bids = {}
    
    def check_one_loan(self, loanid):
        ppdloan = self.loandao.get_db_ppdloan_by_loanid(loanid, self.userdao)
        ifbid, bidmoney, reason, bid_strategy = self.bid_strategy.check_by_strategy(ppdloan)
        if (ifbid == True):
            print "Bid! %s - %s" %(ppdloan.get_loan_summary(), bid_strategy.strategy_name)
        else:
            print "No Bid: %s" % (ppdloan.get_loan_summary())
    
    
    def post_run(self):
        self.loandao.dao.disconnect()

if __name__ == '__main__':
    bsr = BidStrategyRegression("../conf/ppbao.18616856236.config")
    bsr.check_one_loan(12198488)
    bsr.post_run()