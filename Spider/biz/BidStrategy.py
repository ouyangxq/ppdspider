#!python
#-*- coding:utf-8 -*-

'''
Created on 20160221
This Class defines the Bid Strategy for Pai Pai Bao (PPBao)
@author: Xiaoqi Yang
'''
import logging
from ds.PPDLoan import PPDLoan

class BidStrategy(object):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    def check(self, ppdloan):
        '''
        Check the loan if it's worth to bid
        Strategy:  
            * ppdrate: AAA, AA, A, B, C
            * Has University: 
        Return: 
            * ifbid: True (bid), Flase (Nobid)
            * 0 if NoBid, else the money number
            * Reason for Bid or NoBid 
        '''
        if isinstance(ppdloan, PPDLoan) == False:
            logging.error("Internel Error: Parameter is not with right type")
            return (False, 0, "Bad Type")
        # Check if it's AA and if ppdrate >=11
        if (ppdloan.ppdrate == 'AA' and ppdloan.loanrate > 11):
            return (True, 199, "Bid 88 for AA Rate Loan (LoanId:%d, Rate:%d, Maturity: %d) " % (ppdloan.loanid, ppdloan.loanrate, ppdloan.maturity))
        
        if (ppdloan.ppdrate == 'A' and ppdloan.loanrate >= 14):
            return (True, 61, "Bid 61 for A Rate Loan (LoanId:%d, Rate:%d, Maturity: %d) " % (ppdloan.loanid, ppdloan.loanrate, ppdloan.maturity))
        
        logging.debug("Check for ppdloan %d" % (ppdloan.loanid))
        if (ppdloan.loanrate < 10):
            return (False, 0, "NoBid: Loan Rate (%4.2f) < 10" %(ppdloan.loanrate))
        elif (ppdloan.ppdrate in ('C', 'D', 'E', 'F', 'G')):
            return (False, 0, "NoBid: PPD Rate (%s) in C - G. Currently Strategy is for AAA, AA, A, B only" %(ppdloan.ppdrate))
        elif (ppdloan.ppduser.education_level not in ('本科','研究生及以上')):
            return (False, 0, "NoBid: Education level is %s. Current Strategy is for 本科  or 研究生及以上  only" % (ppdloan.ppduser.education_level))
        elif (ppdloan.ppduser.education_type == None or ppdloan.ppduser.education_type != '普通'):
            return (False, 0, "NoBid: Eduation Type is not 普通")
        elif (ppdloan.age < 27 or ppdloan.age > 40):
            return (False, 0, "NoBid: Age (%d) Too young or too old. Current strategy is 27-40" %(ppdloan.age))
        elif (ppdloan.history_overdue_in15d > 2 or ppdloan.history_overdue_mt15d > 0):
            return (False, 0, "NoBid: Bad History - (Overdue within 15 days: %d, Overdue for more than 15 days: %d" % (ppdloan.history_overdue_in15d, ppdloan.history_overdue_mt15d))
        else:
            return (True, 51, "Bid: Meet all requirements: age27-40(%d), good education(%s,%s), good ppdrate(%s), good history(%d,%d)" \
                    % (ppdloan.age, ppdloan.ppduser.education_university, ppdloan.ppduser.education_level, ppdloan.ppdrate, ppdloan.history_return_ontime,ppdloan.history_overdue_in15d))