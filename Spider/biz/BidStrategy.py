#!python
#-*- coding:utf-8 -*-

'''
Created on 20160221
This Class defines the Bid Strategy for Pai Pai Bao (PPBao)
@author: Xiaoqi Yang
'''
import logging
from ds.PPDLoan import PPDLoan
import re
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

class BidStrategy(object):
    '''
    classdocs
    '''
    university_to_rank = None
    # 3 grades
    P0 = 5 # GOOD BID
    P1 = 1
    P2 = 0
    P3 = -1
    P4 = -5 # P4 means NO BID
    shandian_pattern = re.compile('.*的闪电借款')
    
    def __init__(self, university_to_rank):
        '''
        Constructor
        '''
        self.university_to_rank = university_to_rank
    
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
        logging.debug("Running BidStrategy Check for ppdloan %d" % (ppdloan.loanid))
        if (ppdloan.loanrate < 11):
            return (False, 0, "NoBid: Loan Rate (%4.2f < 11)" %(ppdloan.loanrate))
        # Check if it's AA and if ppdrate >=11
        if (ppdloan.ppdrate == 'AA'):
            return self.AA_strategy(ppdloan)
        elif (ppdloan.ppdrate == 'A'):
            return self.A_stragegy(ppdloan)
        elif (ppdloan.ppdrate == 'B'):
            return self.B_strategy(ppdloan)
        elif (ppdloan.ppdrate == 'C' or ppdloan.ppdrate == 'D'):
            return self.CD_strategy(ppdloan)
        else:
            return (False, 0, "NoBid: PPDai Rate(%s) is too low and not in current scope." % (ppdloan.ppdrate))
            
    def AA_strategy(self, ppdloan):
        if ppdloan.ppdrate != 'AA':
            return (False, 0, 'Internel Error: Bad ppdrate: %s - not meet AA Strategy Requirement' %(ppdloan.ppdrate))
        if ppdloan.loanrate > 11:
            ''' Seems PPDai will block me if I bid too many (kuku9991 bid 52 everytime) '''
            ''' This is to give other poeple more opportunity for Peibiao, so change from 199 to 69'''
            bid_money = 69
            return (True, bid_money, "Bid(%d) - Rate(AA),Loan(%d,%4.2f,%d)" %(bid_money, ppdloan.money, ppdloan.loanrate, ppdloan.maturity))
        else:
            #logging.info("Detected AA Loan %d with Rate %4.2f. Ignore it as we're trying to hit Rate>11% only." % (ppdloan.loanid, ppdloan.loanrate))
            return (True, 50, "Bid 50 for LoanRate(%4.2f)- Rate(AA),Loan(%d,%4.2f,%d)" %(ppdloan.loanrate, ppdloan.money, ppdloan.loanrate, ppdloan.maturity))
            # If we want to be more aggressive. Change this. 
            #bid_money = 50
            #return (True, bid_money, "Bid(%d) - Rate(AA),Loan(%d,%4.2f,%d)" %(bid_money, ppdloan.money, ppdloan.loanrate, ppdloan.maturity))
    
    def A_stragegy(self,ppdloan):
        if ppdloan.ppdrate != 'A':
            return (False, 0, 'Internel Error: Bad ppdrate: %s - not meet A Strategy Requirement' %(ppdloan.ppdrate))
        base_point     = 65
        ''' 5, 3, 1, 2 are some random numbers for now. Will think it through and adjust '''
        university_point = 5*self.university_strategy(ppdloan)
        history_point    = 3*self.history_strategy(ppdloan)
        money_point      = 1*self.money_strategy(ppdloan)
        age_point        = 2*self.age_strategy(ppdloan)
        score   = base_point + university_point + history_point + money_point + age_point
        reason       = ppdloan.get_loan_summary()
        logging.debug("Rate A: score(%d) = base_point(%d) + university_point(%d) + history_point(%d) + money_point(%d) + age_point(%d)" % (score, base_point, university_point, history_point, money_point, age_point))
        if score > 65:
            if university_point >= 5*self.P0:
                actual_bid = 82
            if ppdloan.ppduser.education_level == '研究生及以上':
                actual_bid = 76
            elif university_point >= 5*self.P1:
                actual_bid = 68
            else:
                actual_bid = 61
        elif score <= 58: 
            ''' very bad A? '''
            actual_bid = 50
        else:
            actual_bid = 56
        return (True, actual_bid, "Bid/Score(%d/%d) - %s" %(actual_bid, actual_bid, reason) )
    
    def B_strategy (self, ppdloan):
        if ppdloan.ppdrate != 'B':
            return (False, 0, 'Internel Error: Bad ppdrate: %s - not meet B Strategy Requirement' %(ppdloan.ppdrate))
        base_point     = 55   
        ''' XXX:  This NEED TO BE CHANGED - CHECK: 9056315 / 9056911 '''
        university_point = 5*self.university_strategy(ppdloan)
        history_point    = 3*self.history_strategy(ppdloan)
        money_point      = 2*self.money_strategy(ppdloan)
        age_point        = 2*self.age_strategy(ppdloan)
        title_point      = 2*self.title_strategy(ppdloan)
        reason       = ppdloan.get_loan_summary()
        reason      += ",闪电借款标"
        score   = base_point + university_point + history_point + money_point + age_point + title_point;
        
        logging.debug("score(%d) = base_point(%d) + university_point(%d) + history_point(%d) + money_point(%d) + age_point(%d) + title_point(%d)" % (score, base_point, university_point, history_point, money_point, age_point, title_point))
        if score < 52:
            return (False, 0, "NO Bid,Score(%d<52) - %s" %(score, reason))
        else:
            if university_point >= 5*self.P0:
                actual_bid = 72
            elif university_point >= 5*self.P1 and ppdloan.ppduser.education_level == '研究生及以上':
                actual_bid = 68
            elif university_point >= 5*self.P1 and ppdloan.ppduser.education_level == '本科':
                if money_point >= self.P2 and history_point >= self.P2:
                    actual_bid = 58
                else:
                    actual_bid = 52
            elif ppdloan.ppduser.education_type == '普通' and ppdloan.ppduser.education_level == '研究生及以上' and history_point >=self.P2:
                actual_bid = 56
            elif ppdloan.ppduser.education_type == '普通' and ppdloan.ppduser.education_level == '本科' and history_point >=self.P2:
                actual_bid = 51
            elif history_point >= self.P1 and age_point >= self.P2 and money_point >= self.P1:
                ''' 20160303: Add money_point check to avoid bid for those who loan too much '''
                actual_bid = 50
            elif ppdloan.history_total_loan == 0 and ppdloan.ppduser.education_type == '普通' and age_point >= self.P2:
                ''' 20160301: IF it's a first loan, and has a degree (no matter good or bad) and in good age, bid 50'''
                actual_bid = 50
            elif score > 53 and university_point < self.P2 and history_point >= self.P1 and money_point >= self.P1:
                logging.info("Bid 50 for Loan without Good university but has very good history and money point! (Points: %d,%d,%d)" % (university_point, history_point, money_point))
                actual_bid = 50
            else:
                actual_bid = 0
            if actual_bid >= 50:
                return (True, actual_bid, "Bid/Score(%d/%d) - %s" %(actual_bid, score, reason))
            else:
                return (False,0, "Bid/Score(%d/%d) - %s" %(actual_bid, score, reason))
            
    def CD_strategy (self, ppdloan):
        if ppdloan.ppdrate != 'C' and ppdloan.ppdrate != 'D':
            return (False, 0, 'Internel Error: Bad ppdrate: %s - not meet C/D Strategy Requirement' %(ppdloan.ppdrate))
        base_point     = 50  
        university_point = 3*self.university_strategy(ppdloan)
        history_point    = 2*self.history_strategy(ppdloan)
        money_point      = 4*self.money_strategy(ppdloan) 
        age_point        = 1*self.age_strategy(ppdloan)
        title_point      = 3*self.title_strategy(ppdloan)
        reason  = ppdloan.get_loan_summary()
        score   = base_point + university_point + history_point + money_point + age_point + title_point
        actual_bid = 0
        logging.debug("score(%d) = base_point(%d) + university_point(%d) + history_point(%d) + money_point(%d) + age_point(%d) + title_point(%d)" % (score, base_point, university_point, history_point, money_point, age_point, title_point))
        ''' If score > 50, it means it's either a new loan, or from money_point perspective, it's a good bid, which is quite important for C & D Rate'''
        if score >= 51: 
            ''' Recheck using University'''
            if (university_point >= 3*self.P0):
                ''' For Top 26 University, Bid 56 '''
                actual_bid = 56
            elif history_point >= self.P2:
                ''' Else, check history records as well '''
                if university_point >= 3*self.P1:
                    actual_bid = 51
                elif university_point >= self.P2 and age_point >= self.P2 and history_point>=self.P2 and money_point>=self.P2:
                    actual_bid = 50
                else:
                    ''' Current Strategy requires University for all C&D loans. May change it in the future'''
                    actual_bid = 0
            else:
                actual_bid = 0
        else:
            actual_bid = 0
        if actual_bid < 50:
            return (False, 0, "NO Bid,Bid/Score(%d/%d<50) - %s" %(actual_bid, score, reason))
        else:
            logging.info("Bid for %s Loan(OFFICIAL!!!): Bid/Score(%d/%d) - %s" %(ppdloan.ppdrate, actual_bid, score, reason))
            return (True, actual_bid, "Bid/Score(%d/%d) - %s" %(actual_bid, score, reason))
            #return (True, 50, "Bid/Score(50/%d) - %s" %(50, actual_bid, reason))
        
        
    '''
    In all below Strategies by University / By Loan History, etc, we'll define a similar Rate system as Mojing
    * P1: means everything looks very good from this Strategy Check
    * P2: means it's acceptable, but shall not bid too many
    * P3: Failed this Strategy Check
    Those Strategies will then be used by A/B/C/D Strategies
    '''
    def university_strategy (self, ppdloan):
        '''
        P0: Top 26,('本科','研究生及以上'), 学习方式：普通
        P1: In Top 100, ('本科','研究生及以上'), 学习方式：普通
        P2: In Top 500, ('本科','研究生及以上'), 学习方式：普通
        P3: All the rest of them
        '''
        if (ppdloan.ppduser.education_university == 'NULL') or (ppdloan.ppduser.education_level not in ('本科','研究生及以上')) \
                or ppdloan.ppduser.education_type != '普通':
            if (ppdloan.ppduser.education_type == u'普通' and ppdloan.ppduser.education_level == u'本科'):
                logging.debug("WARN: University_Strategy: Shall match unicode instead - (%s, %s, %s)!!!" %(ppdloan.ppduser.education_university, ppdloan.ppduser.education_level, ppdloan.ppduser.education_type))
            return self.P3
        university = ppdloan.ppduser.education_university
        university = unicode(university)
        
        if university in self.university_to_rank.keys():
            rank = self.university_to_rank[university]
            logging.debug("%s found in University DB. Rank: %d" % (university, rank))
            if rank <= 26:
                return self.P0
            elif (ppdloan.ppdrate == 'A' or ppdloan.ppdrate == 'B') and rank <= 150:
                ''' @20160304: Change to Top 200 for 'A' or 'B' Loans '''
                return self.P1
            elif (ppdloan.ppdrate == 'C' or ppdloan.ppdrate == 'D') and rank <= 100:
                ''' @20160303: Change to Top 100 to further limit the bid scope and improve bid quality '''
                return self.P1
            else:
                return self.P2
        else:
            logging.debug("%s not in current University DB" % (university))
            return self.P3
    
    def history_strategy (self, ppdloan):
        '''
        history_return_ontime/history_overdue_in15d/history_overdue_mt15d
        P1: history_return_ontime>7, no overdue
        P2: First Loan, or history_return_ontime>3, at most 1 delay in 15d, 
        P3: All the rest of them
        '''
        if (ppdloan.history_overdue_mt15d > 0):
            return self.P3
        elif (ppdloan.history_overdue_in15d > 0):
            if (ppdloan.history_return_ontime > 7 and ppdloan.history_overdue_in15d == 1):
                ''' can allow 1 time overdue if return times >7 '''
                return self.P2
            elif ppdloan.history_overdue_in15d > 3:
                ''' 20160304: No Bid if overdue_in 15d > 3 times '''
                return self.P4
            else:
                return self.P3
        else:
            if ppdloan.history_total_loan == 0: # For New Loan 
                return self.P2  # A new Loan
            elif ppdloan.history_return_ontime > 4: 
                return self.P1
            else:
                ''' at least it shall has 5 times record, otherwise, it's P3'''
                return self.P3
    
    def money_strategy(self, ppdloan):
        '''
        history_total_loan/history_left_loan/history_left_lend/ Loan money for this time
        P1: left_loan + money - left_lend < total_loan*0.5
        P2: First loan, or left_loan + money - left_lend < total_loan*0.8
        P3: left_loan + money - left_lend < total_loan*1.2
        P4: money > 12000
        '''
        new_total_loan = ppdloan.history_left_loan + ppdloan.money - ppdloan.history_left_lend
        if (new_total_loan < ppdloan.history_total_loan * 0.5):
            return self.P1
        elif ppdloan.history_total_loan == 0 and ppdloan.history_left_loan == 0:
            ''' 20160303: add check for ppdloan.history_left_loan == 0 as there are rare cases that
             loaner didn't return anything but requested another loan, which is pretty bad... '''
            return self.P2
        elif (ppdloan.ppdrate == 'B' and ppdloan.money > 12000):
            ''' No Bid for B Loan that ask for more than 12000 '''
            return self.P4
        elif ((ppdloan.ppdrate == 'C' or ppdloan.ppdrate == 'D') and ppdloan.money > 10000):
            ''' No Bid for C/D Loan that ask for more than 10000 '''
            return self.P4
        elif ((ppdloan.ppdrate != 'A') and (ppdloan.money % 100 != 0)):
            ''' 20160304: 投那些金额整百整千, 如果穷到尾数几十块 甚至几块钱 也要借的人 反正要么是骗尽每一块钱 要么就是穷疯了 '''
            logging.debug("Return ")
            return self.P3
        elif new_total_loan < ppdloan.history_total_loan * 0.7:
            return self.P2
        elif new_total_loan < ppdloan.history_total_loan * 1.2:
            return self.P3
        else:
            return self.P4

    
    def age_strategy(self, ppdloan):
        '''
        P1: age between 28 to 35
        P2: age between 26 to 40
        P3: rest of them
        '''
        if (ppdloan.age >= 28 and ppdloan.age <= 35):
            return self.P1
        elif (ppdloan.age >= 26 and ppdloan.age <= 40):
            return self.P2
        else:
            return self.P3
    
    def title_strategy(self,ppdloan):
        '''
        P3: 闪电借款
        P2: 手机APP用户的借款
        '''
        if ppdloan.loantitle is None:
            return self.P2
        shandian_match = re.match(self.shandian_pattern, ppdloan.loantitle);
        if shandian_match is not None:
            return self.P3
        else:
            return self.P2
         
    