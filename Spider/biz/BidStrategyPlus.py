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
    bid_strategy_list = []
    
    def __init__(self, ppbao_config):
        '''
        Constructor
        '''
        self.ppbao_config = ppbao_config
        for strategy_str in ppbao_config.bid_strategy_strlist:
            bs = BidStrategyBuilder(strategy_str)
            self.bid_strategy_list.append(bs)
            #print "Print: %s" % (bs.strategy_str)
            logging.info("Strategy: %s" % (bs.strategy_str))
    
    def check_by_strategy(self, ppdloan):
        for strategy in self.bid_strategy_list:
            (ifbid, money, reason) = strategy.check_by_strategy(ppdloan)
            if (ifbid == True and money > 0):
                return (ifbid, money, reason)
        logging.debug("No Bid for %d as no Strategy match this Loan!" % (ppdloan.loanid))
        return (False, 0, ppdloan.get_loan_summary())
