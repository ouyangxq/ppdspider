#-*- coding: utf8 -*-
'''
Created on 2016 Mar 21st

@author: Administrator
'''

import re
import logging
from util.PPBaoUtil import PPBaoUtil
from util.BestBidMoney import BestBidMoney

class BidStrategyBuilder(object):
    '''
    classdocs
    '''
    any = 'any'
    no  = 'no'
    yes = 'yes'
    ppdrate_list = []
    loanrate_list = []
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
    has_highrate_loan_history = False
    has_lt1000_loan_history = False
    bid_money = -1
    strategy_str = None
    history_left_loan = -1
    lt_history_max_loan = -1
    bidmoney_range_start = -1
    bidmoney_range_end   = -1
    has_one_cert_list = []
    has_certs_list = []
    left_lend = -1
    strategy_name = ""

    def __init__(self, strategy_name, strategy_str):
        '''
        Constructor
        '''
        ''' NOTICE: Default Codec in ppbao_config is GBK, so need to transfer to utf8 here '''
        ''' Bug&Fix: 20160323: Need to initialize in PPBao, otherwise, edu_level_list will contain every levels '''
        ''' 20160331: By Default, set them to accept 'any' so as to simplify the definition in ppbao.config '''
        self.ppdrate_list = ['A', 'B', 'C', 'D', 'E']
        self.loanrate_list = [18,19, 20, 21, 22, 23, 24]
        self.urank_start = -1
        self.urank_end = -1
        self.edu_level_list = ['博士研究生','硕士研究生','研究生及以上', '本科']
        self.first_loan_flag = True
        self.return_ontime_min = -1
        self.overdue_limit = -1
        self.new_total_loan = -1
        self.gender = self.any
        self.age_start = 16 
        self.age_end = 60
        self.left_lend = -1
        self.bidmoney_range_start = -1
        self.bidmoney_range_end   = -1
        self.check_highrate_loan_history_flag = False
        self.check_lt1000_loan_history_flag = False
        self.check_shandian_loan_flag = False
        self.history_left_loan = -1
        self.lt_history_max_loan = -1
        self.has_one_cert_list = []
        self.has_certs_list = []
        self.bid_money = -1
        self.strategy_name = strategy_name
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
            m = re.match('loanrate\((\S+)\)', criteria)
            if (m is not None):
                rate_list = re.split(',', m.group(1))
                self.loanrate_list = []
                for rate in rate_list:                    
                    self.loanrate_list.append(float(rate))
            m = re.match('urank\((\S+)\)', criteria)
            if (m is not None):
                urank_start, urank_end = re.split(",", m.group(1))
                self.urank_start = int(urank_start)
                self.urank_end = int(urank_end)
            m = re.match('bid_range\((\S+)\)', criteria)
            if (m is not None):
                bid_money_start, bid_money_end = re.split(",", m.group(1))
                self.bidmoney_range_start = int(bid_money_start)
                self.bidmoney_range_end = int(bid_money_end)
            m = re.match('education_level\((\S+)\)', criteria)
            if (m is not None):
                edu_level_list = re.split(",", m.group(1))
                self.edu_level_list = []
                for edu in edu_level_list:
                    #print "Edu: %s" % (edu)
                    self.edu_level_list.append(edu)
            m = re.match('has_one_cert\((\S+)\)', criteria)
            if (m is not None):
                certs = re.split(",", m.group(1))
                self.has_one_cert_list = []
                for cert in certs:
                    #print "Edu: %s" % (edu)
                    self.has_one_cert_list.append(cert)
            m = re.match('history_return\((\S+)\)', criteria)
            if (m is not None):
                first_loan_flag, return_ontime, overdue = re.split(",", m.group(1))
                self.first_loan_flag = True if (first_loan_flag == 'True') else False                
                self.return_ontime_min = int(return_ontime)
                self.overdue_limit = int(overdue)
            m = re.match('new_total_loan\((\S+)\)', criteria)
            if (m is not None):
                self.new_total_loan = int(m.group(1))
            m = re.match('left_lend\((\S+)\)', criteria)
            if (m is not None):
                self.left_lend = int(m.group(1))
            m = re.match('history_leftloan\((\S+)\)', criteria)
            if (m is not None):
                self.history_left_loan = int(m.group(1)) #.decode('gbk').encode('utf-8')
            m = re.match('lt_hmaxloan\((\S+)\)', criteria)
            if (m is not None):
                self.lt_history_max_loan = int(m.group(1)) 
            m = re.match('gender\((\S+)\)', criteria)
            if (m is not None):
                self.gender = m.group(1) #.decode('gbk').encode('utf-8')
            m = re.match('age\((\S+)\)', criteria)
            if (m is not None):
                age_start, age_end = re.split(",", m.group(1))
                self.age_start = int(age_start)
                self.age_end = int(age_end)
            m = re.match('has_highrate_loan_history\((\S+)\)', criteria)
            if (m is not None):
                value = m.group(1)
                self.check_highrate_loan_history_flag = True if (value == self.no) else False
            m = re.match('has_lt1000_loan_history\((\S+)\)', criteria)
            if (m is not None):
                value = m.group(1)
                self.check_lt1000_loan_history_flag = True if (value == self.no) else False
            m = re.match('has_certs\((\S+)\)', criteria)
            if (m is not None):
                certs = re.split(",", m.group(1))
                self.has_certs_list = []
                for cert in certs:
                    #print "Edu: %s" % (edu)
                    self.has_certs_list.append(cert)
            m = re.match('shandian_loan\((\S+)\)', criteria)
            if (m is not None):
                value = m.group(1)
                self.check_shandian_loan_flag = True if (value == self.no) else False
            m = re.match('bid_money\((\S+)\)', criteria)
            if (m is not None):
                self.bid_money = int(m.group(1))
    
    def get_strategy_summary(self):
        summary = "%s,%d, %s, %d, %d" % (self.ppdrate_list[0], self.urank_start, self.edu_level_list[0], self.overdue_limit, self.return_ontime_min)
        return summary 
    
    def check_by_strategy(self, ppdloan):
        if (self.check_university_rank(ppdloan) and
            self.check_ppdrate(ppdloan) and
            self.check_loanrate(ppdloan) and
            self.check_education_level(ppdloan) and
            self.check_history_return(ppdloan) and
            self.check_history_left_loan(ppdloan) and
            self.check_history_max_loan(ppdloan) and
            self.check_new_total_loan(ppdloan) and
            self.check_gender(ppdloan) and
            self.check_age(ppdloan) and
            self.check_highrate_loan_history(ppdloan) and
            self.check_shandian_loan(ppdloan) and
            self.check_left_lend(ppdloan) and
            self.check_certificates(ppdloan)):
            actual_bid_money = 0
            if (self.bid_money != -1):
                actual_bid_money = self.bid_money
            elif (self.bidmoney_range_start != -1 and self.bidmoney_range_end != -1):
                actual_bid_money = BestBidMoney.get_best_bid_money(ppdloan.loanrate, ppdloan.maturity, self.bidmoney_range_start, self.bidmoney_range_end)
                #logging.info("GetBestBidMoney: LoanRate(%d),Month(%d),bid_range(%d,%d) - BestBid: %d" %(ppdloan.loanrate, ppdloan.maturity, self.bidmoney_range_start, self.bidmoney_range_end, actual_bid_money))
            else:
                logging.warn("PPBaoConfig Error: No bid_money and bid_range defined!! NO BID!! Strategy: %s" % (self.strategy_str))
                return (False, 0, "NoBid defined in Config: %s" % ppdloan.get_loan_summary, None)
            logging.info("Strategy Matches! Bid %d for %d!\nPPDloan Summary: %s\nStrategy Matched: %s: %s" % (actual_bid_money, ppdloan.loanid, ppdloan.get_loan_summary(), self.strategy_name, self.strategy_str))
            return (True, actual_bid_money, ppdloan.get_loan_summary(), self)
        else:
            #logging.info("No match from Strategy: %s" % (self.strategy_str))
            return (False, 0, ppdloan.get_loan_summary(), None)
    
    def check_university_rank(self, ppdloan):
        ''' if university rank is <=n, return true, -1 means no check on university_rank '''
        if (self.urank_start == -1 and self.urank_end == -1):
            return True
        rank = PPBaoUtil.get_university_rank(ppdloan.ppduser)
        if rank >= self.urank_start and rank <= self.urank_end:
            return True 
        else:
            return False
    
    def check_education_level(self, ppdloan):
        ''' if education_level in edu_level_list, return true '''
        if (self.edu_level_list[0] == self.any):
            return True if ppdloan.ppduser.education_university != 'NULL' else False
        else:
            return True if (ppdloan.ppduser.education_level in self.edu_level_list) else False
    
    def check_new_total_loan(self, ppdloan):
        # -1 means not defined and can be any value
        return True if (self.new_total_loan == -1 or ppdloan.new_total_loan <= self.new_total_loan) else False
    
    def check_left_lend(self, ppdloan):
        # -1 means not defined and can be any value
        return True if (self.left_lend == -1 or ppdloan.history_left_lend >= self.left_lend) else False
    
    def check_history_return(self, ppdloan):
        ''' First_loan: True / False'''
        ''' Notice, any loan with overdue > 15 days are automatically ignored (return FALSE) '''
        if ppdloan.history_total_loan == 0 and ppdloan.history_left_loan == 0: 
            return True if self.first_loan_flag == True else False
        if ppdloan.history_overdue_mt15d > 0:
            return False
        if ppdloan.history_return_ontime >= self.return_ontime_min and ppdloan.history_overdue_in15d <= self.overdue_limit:
            return True
        else:
            return False

    def check_age(self, ppdloan):
        return True if (ppdloan.age >= self.age_start and ppdloan.age <= self.age_end) else False
    
    def check_gender(self, ppdloan):
        return True if (self.gender == self.any or ppdloan.ppduser.gender == self.gender) else False

    def check_highrate_loan_history(self,ppdloan):
        if (self.check_highrate_loan_history_flag == True and ppdloan.has_30or36rate_loan_history == 1):
            return False
        else:
            return True
    
    def check_lt1000_loan_history(self,ppdloan):
        if (self.check_lt1000_loan_history_flag == True and ppdloan.has_lt1000_loan_history == 1): 
            return False
        else:
            return True
    
    def check_shandian_loan(self,ppdloan):
        if (self.check_shandian_loan_flag == True and ppdloan.is_shandian_loan == 1):
            return False
        else:
            return True
        
    def check_ppdrate(self, ppdloan):
        return True if (ppdloan.ppdrate in self.ppdrate_list) else False
    
    def check_loanrate(self, ppdloan):
        return True if (ppdloan.loanrate in self.loanrate_list) else False
    
    def check_history_left_loan(self, ppdloan):
        return True if (self.history_left_loan == -1 or (ppdloan.history_left_loan-ppdloan.history_left_lend) <= self.history_left_loan) else False
    
    def check_history_max_loan(self, ppdloan):
        if (self.lt_history_max_loan == -1 or ppdloan.history_total_loan == 0):
            return True
        diff = ppdloan.history_highest_total_loan - ppdloan.new_total_loan
        #print "Diff: %d" % (diff)
        return True if diff >= self.lt_history_max_loan else False
    
    def check_certificates(self, ppdloan):
        return self.check_has_one_cert(ppdloan) and self.check_has_certs(ppdloan)
                    
    def check_has_one_cert(self, ppdloan): 
        if len(self.has_one_cert_list) > 0:
            for cert in self.has_one_cert_list:
                # (学生证,支付宝,户口,银行流水,工作,社保);
                if ((cert == '银行流水' and ppdloan.ppduser.bank_details_cert == 1) or
                    (cert == '支付宝' and ppdloan.ppduser.alipay_cert == 1) or
                    (cert == '户口' and ppdloan.ppduser.hukou_cert == 1) or
                    (cert == '社保' and ppdloan.ppduser.shebao_gjj_cert == 1) or
                    (cert == '工作' and ppdloan.ppduser.shebao_gjj_cert == 1) or
                    (cert == '收入' and ppdloan.ppduser.shebao_gjj_cert == 1) or
                    (cert == '征信' and ppdloan.ppduser.shebao_gjj_cert == 1) or
                    (cert == '手机' and ppdloan.ppduser.mobile_cert == 1) or
                    (cert == '学生证' and ppdloan.ppduser.student_cert == 1)):
                    return True
            #　if reaches here, then no certificate matched
            return False
        return True
    
    def check_has_certs(self, ppdloan):
        if len(self.has_certs_list) > 0:
            for cert in self.has_certs_list:
                if ((cert == '银行流水' and ppdloan.ppduser.bank_details_cert == 0) or
                    (cert == '支付宝' and ppdloan.ppduser.alipay_cert == 0) or
                    (cert == '户口' and ppdloan.ppduser.hukou_cert == 0) or
                    (cert == '社保' and ppdloan.ppduser.shebao_gjj_cert == 0) or
                    (cert == '工作' and ppdloan.ppduser.shebao_gjj_cert == 0) or
                    (cert == '收入' and ppdloan.ppduser.shebao_gjj_cert == 0) or
                    (cert == '征信' and ppdloan.ppduser.shebao_gjj_cert == 0) or
                    (cert == '学生证' and ppdloan.ppduser.student_cert == 0) or
                    (cert == '手机' and ppdloan.ppduser.mobile_cert == 0) or
                    (cert == '身份证' and ppdloan.ppduser.idcard_cert == 0)):
                    return False
            # If reaches here, means all are matched.
            return True
        else:
            return True
                    