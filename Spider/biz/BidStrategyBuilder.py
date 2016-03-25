#-*- coding: utf8 -*-
'''
Created on 2016 Mar 21st

@author: Administrator
'''

import re
import logging
from util.PPBaoUtil import PPBaoUtil

class BidStrategyBuilder(object):
    '''
    classdocs
    '''
    ppdrate_list = []
    urank_start = -1
    urank_end = -1
    edu_level_list = []
    first_loan_flag = False
    return_ontime_min = -1
    overdue_limit = -1
    new_total_loan = -1
    gender = None
    age_start = -1
    age_end = -1
    bid_money = -1
    strategy_str = None

    def __init__(self, strategy_str):
        '''
        Constructor
        '''
        ''' NOTICE: Default Codec in ppbao_config is GBK, so need to transfer to utf8 here '''
        ''' Bug&Fix: 20160323: Need to initialize in PPBao, otherwise, edu_level_list will contain every levels '''
        self.ppdrate_list = []
        self.urank_start = -1
        self.urank_end = -1
        self.edu_level_list = []
        self.first_loan_flag = False
        self.return_ontime_min = -1
        self.overdue_limit = -1
        self.new_total_loan = -1
        self.gender = None
        self.age_start = -1
        self.age_end = -1
        self.bid_money = -1
        self.strategy_str = strategy_str.decode('gbk').encode('utf8')
        self.build_bid_strategy_from_str()
        #print "AA: " + self.strategy_str
    
    def get_strategy_str(self):
        return self.strategy_str
        
    def build_bid_strategy_from_str(self):          
        slist = re.split(';',self.strategy_str)
        for criteria in slist:
            m = re.match('ppdrate\((\S+)\)', criteria)
            if (m is not None):
                self.ppdrate_list = re.split(',', m.group(1))
            m = re.match('univerity_rank\((\S+)\)', criteria)
            if (m is not None):
                urank_start, urank_end = re.split(",", m.group(1))
                self.urank_start = int(urank_start)
                self.urank_end = int(urank_end)
            m = re.match('education_level\((\S+)\)', criteria)
            if (m is not None):
                edu_level_list = re.split(",", m.group(1))
                for edu in edu_level_list:
                    #print "Edu: %s" % (edu)
                    self.edu_level_list.append(edu)
            m = re.match('history_return\((\S+)\)', criteria)
            if (m is not None):
                first_loan_flag, return_ontime, overdue = re.split(",", m.group(1))
                self.first_loan_flag = True if (first_loan_flag == 'True') else False                
                self.return_ontime_min = int(return_ontime)
                self.overdue_limit = int(overdue)
            m = re.match('new_total_loan\((\S+)\)', criteria)
            if (m is not None):
                self.new_total_loan = int(m.group(1))
            m = re.match('gender\((\S+)\)', criteria)
            if (m is not None):
                self.gender = m.group(1) #.decode('gbk').encode('utf-8')
            m = re.match('age\((\S+)\)', criteria)
            if (m is not None):
                age_start, age_end = re.split(",", m.group(1))
                self.age_start = int(age_start)
                self.age_end = int(age_end)
            m = re.match('bid_money\((\S+)\)', criteria)
            if (m is not None):
                self.bid_money = int(m.group(1))
    
    def get_strategy_summary(self):
        summary = "%s, %s" % (self.ppdrate_list[0], self.urank_start, self.edu_level_list[0])
        return summary 
    
    def check_by_strategy(self, ppdloan):
        if (self.check_university_rank(ppdloan, self.urank_start, self.urank_end) and
            self.check_education_level(ppdloan, self.edu_level_list) and
            self.check_history_return(ppdloan, self.first_loan_flag, self.return_ontime_min, self.overdue_limit) and
            self.check_new_total_loan(ppdloan, self.new_total_loan) and
            self.check_gender(ppdloan, self.gender) and
            self.check_age(ppdloan, self.age_start, self.age_end)):
            logging.info("Strategy Matches! Bid %d for %d!\nPPDloan Summary: %s\nStrategy Matched: %s" % (self.bid_money, ppdloan.loanid, ppdloan.get_loan_summary(), self.strategy_str))
            return (True, self.bid_money, ppdloan.get_loan_summary())
        else:
            #logging.info("Return 0 for %d!\nPPDloan Summary: %s\nStrategy Matched: %s" % (ppdloan.loanid, ppdloan.get_loan_summary(), self.strategy_str))
            return (False, 0, ppdloan.get_loan_summary())
    
    def check_university_rank(self, ppdloan, rank_start, rank_limit):
        ''' if university rank is <=n, return true '''
        rank = PPBaoUtil.get_university_rank(ppdloan)
        if rank >= rank_start and rank <= rank_limit:
            return True 
        else:
            return False
    
    def check_education_level(self, ppdloan, edu_level_list):
        ''' if education_level in edu_level_list, return true '''
        if (ppdloan.ppduser.education_level in edu_level_list):
            #logging.info("Matched!: %s" % ppdloan.ppduser.education_level)
            #logging.info(edu_level_list)
            return True
        else:
            #logging.info("Not Match: %s" % ppdloan.ppduser.education_level)
            #logging.info(edu_level_list)
            return False
    
    def check_new_total_loan(self, ppdloan, limit):
        ''' if education_level in edu_level_list, return true '''
        new_total_loan = ppdloan.money + ppdloan.history_left_loan - ppdloan.history_left_lend
        return True if (new_total_loan <= limit) else False
    
    def check_history_return(self, ppdloan, first_loan_flag, return_ontime_limit, overdue_limit):
        ''' First_loan: True / False'''
        ''' Notice, any loan with overdue > 15 days are automatically ignored (return FALSE) '''
        if ppdloan.history_total_loan == 0: 
            return True if first_loan_flag == True else False
        if ppdloan.history_overdue_mt15d > 0:
            return False
        if ppdloan.history_return_ontime >= return_ontime_limit and ppdloan.history_overdue_in15d <= overdue_limit:
            return True
        else:
            return False

    
    def check_age(self, ppdloan, age_start, age_end):
        if ppdloan.age >= age_start and ppdloan.age <= age_end:
            return True
        else:
            return False
    
    
    def check_gender(self, ppdloan, gender):
        if (ppdloan.ppduser.gender == gender):
            return True
        else:
            return False
    