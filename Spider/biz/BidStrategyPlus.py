#-*- coding: utf8 -*-
'''
Created on 2016年3月21日

@author: Administrator
'''

import re
from biz.BidStrategyBuilder import BidStrategyBuilder
import logging
from sys import argv
from util.PPBaoConfig import PPBaoConfig

import sys
reload(sys)
sys.setdefaultencoding('utf8')

class BidStrategyPlus(object):
    '''
    classdocs
    '''
    bid_strategy_hash = {}
    bid_strategy_names = []
    
    def __init__(self, ppbao_config):
        '''
        Constructor
        '''
        self.bid_strategy_hash = {}
        self.bid_strategy_names = ppbao_config.bid_strategy_hash.keys();
        self.bid_strategy_names.sort()
        for strategy_name in self.bid_strategy_names:
            bs = BidStrategyBuilder(strategy_name, ppbao_config.bid_strategy_hash[strategy_name])
            self.bid_strategy_hash[strategy_name] = bs
            logging.info("%s: %s" % (strategy_name, bs.get_strategy_str()))
    
    def get_bid_strategy_hash(self):
        return self.bid_strategy_hash
    
    def check_by_strategy(self, ppdloan):
        for strategy_name in self.bid_strategy_names:
            (ifbid, money, reason, bs) = self.bid_strategy_hash[strategy_name].check_by_strategy(ppdloan)
            if (ifbid == True and money > 0):
                return (ifbid, money, reason, bs)
        #logging.info("No Bid for %d as no Strategy match this Loan!" % (ppdloan.loanid))
        return (False, 0, ppdloan.get_loan_summary(), None)
