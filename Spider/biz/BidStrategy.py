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
from random import random
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
            logging.error("Internal Error: Parameter is not with right type")
            return (False, 0, "Internal Error: Bad Type")
        logging.debug("Running BidStrategy Check for ppdloan %d" % (ppdloan.loanid))
        if (ppdloan.loanrate <= 18):
            ''' 20160320: Change to bid for Rate>=19 only to maximum profits '''
            reason  = ppdloan.get_loan_summary()
            return (False, 0, "LoanRate(%4.2f<=18),%s" %(ppdloan.loanrate,reason))
        # Check if it's AA and if ppdrate >=11
        if (ppdloan.ppdrate == 'AA'):
            return self.AA_strategy(ppdloan)
        elif (ppdloan.ppdrate == 'A'):
            return self.A_stragegy(ppdloan)
        elif (ppdloan.ppdrate == 'B'):
            return self.B_strategy(ppdloan)
        elif ppdloan.ppdrate == 'C':
            return self.C_strategy(ppdloan)
        elif ppdloan.ppdrate == 'D':
            return self.D_strategy(ppdloan)
        else:
            ppdloan.score = 0
            ppdloan.bid   = 0
            return (False, 0, "NoBid:PPDai Rate(%s) is too low which is not in current scope." % (ppdloan.ppdrate))
            
    def AA_strategy(self, ppdloan):
        if ppdloan.ppdrate != 'AA':
            return (False, 0, 'Internel Error: Bad ppdrate: %s - not meet AA Strategy Requirement' %(ppdloan.ppdrate))
        if ppdloan.loanrate > 11:
            ''' Seems PPDai will block me if I bid too many (kuku9991 bid 52 everytime) '''
            ''' This is to give other poeple more opportunity for Peibiao, so change from 199 to 69'''
            actual_bid = 100
            ppdloan.score = actual_bid
            ppdloan.bid   = actual_bid
            return (True, actual_bid, "Bid(%d),Rate(AA),Loan(%d,%d,%d)" %(actual_bid, ppdloan.money, ppdloan.loanrate, ppdloan.maturity))
        else:
            actual_bid = 50
            ppdloan.score = actual_bid
            ppdloan.bid   = actual_bid
            #logging.info("Detected AA Loan %d with Rate %4.2f. Ignore it as we're trying to hit Rate>11% only." % (ppdloan.loanid, ppdloan.loanrate))
            return (True, 50, "Bid(50),Rate(AA),Loan(%d,%d,%d)" %(ppdloan.loanrate, ppdloan.money, ppdloan.loanrate, ppdloan.maturity))
            # If we want to be more aggressive. Change this. 
            #bid_money = 50
            #return (True, bid_money, "Bid(%d) - Rate(AA),Loan(%d,%4.2f,%d)" %(bid_money, ppdloan.money, ppdloan.loanrate, ppdloan.maturity))
    
    def A_stragegy(self,ppdloan):
        if ppdloan.ppdrate != 'A':
            return (False, 0, 'Internal Error: Bad ppdrate: %s - not meet A Strategy Requirement' %(ppdloan.ppdrate))
        base_point     = 58
        ''' 5, 3, 1, 2 are some random numbers for now. Will think it through and adjust '''
        university_point = 5*self.university_strategy(ppdloan)
        history_point    = 3*self.history_strategy(ppdloan)
        money_point      = 2*self.money_strategy(ppdloan)
        age_point        = self.age_strategy(ppdloan)
        title_point      = 2*self.title_strategy(ppdloan)
        gender_point     = self.gender_strategy(ppdloan)
        cert_point       = self.cert_strategy(ppdloan)
        score   = base_point + university_point + history_point + money_point + age_point + title_point + gender_point + cert_point
        reason  = ppdloan.get_loan_summary()
        if (title_point < self.P2):
            reason += ",闪电借款标"
        logging.debug("score(%d) = base(%d) + university(%d) + history(%d) + money(%d)+age(%d)+title(%d)+gender(%d)+other_certs(%d)" % (score, base_point, university_point, history_point, money_point, age_point, title_point, gender_point, cert_point))
        
        if score > 59:
            if university_point >= 5*self.P0: # Very good university
                actual_bid = (82 if money_point >= self.P2 else 72 )
            if ppdloan.ppduser.education_level == '研究生及以上':
                actual_bid = (68 if money_point >= self.P2 else 59 )
            elif university_point >= 5*self.P1: # Good university
                actual_bid = (60 if money_point >= self.P2 else 50 )
            elif self.get_new_total_loan(ppdloan) > 15000:
                logging.info("No Bid for Rate A - new total loan(%d)>15000" % (self.get_new_total_loan(ppdloan)))
                actual_bid = 0
            elif ppdloan.ppduser.education_university != 'NULL' and money_point >= self.P2:
                actual_bid = 52
        elif score <= 55: 
            ''' very bad A? '''
            ''' 20160306: No Bid for bad A '''
            logging.info("No Bid for Rate A - Score(%d)<=55" % (score))
            actual_bid = 0
        elif title_point >= self.P2 and ppdloan.ppduser.education_university != 'NULL' :
            actual_bid = 50
        else:
            actual_bid = 0
        ppdloan.score = score
        ppdloan.bid   = actual_bid
        if (actual_bid < 50):
            ''' 20160306: No Bid for bad A '''
            return (False,0,"NoBid for A Loan!Score(%d),%s" %(score, reason))
        else:
            return (True, actual_bid, "Bid/Score(%d/%d),%s" %(actual_bid, score, reason) )
    
    def B_strategy (self, ppdloan):
        if ppdloan.ppdrate != 'B':
            return (False, 0, 'Internel Error: Bad ppdrate: %s - not meet B Strategy Requirement' %(ppdloan.ppdrate))
        base_point     = 54   
        ''' XXX:  This NEED TO BE CHANGED - CHECK: 9056315 / 9056911 '''
        university_point = 5*self.university_strategy(ppdloan)
        history_point    = 3*self.history_strategy(ppdloan)
        money_point      = 2*self.money_strategy(ppdloan)
        age_point        = 2*self.age_strategy(ppdloan)
        title_point      = 2*self.title_strategy(ppdloan)
        gender_point     = self.gender_strategy(ppdloan)
        cert_point       = self.cert_strategy(ppdloan)
        reason       = ppdloan.get_loan_summary()
        if (title_point < self.P2):
            reason += ",闪电借款标"
        score   = base_point + university_point + history_point + money_point + age_point + title_point + gender_point + cert_point
        new_total_loan = self.get_new_total_loan(ppdloan)
        ppdloan.score = score
        logging.debug("score(%d) = base(%d) + university(%d) + history(%d) + money(%d)+age(%d)+title(%d)+gender(%d)+other_certs(%d)" % (score, base_point, university_point, history_point, money_point, age_point, title_point, gender_point, cert_point))
        if score < 53:
            ppdloan.bid = 0
            return (False, 0, "Score(%d<53) - %s" %(score, reason))
        else:
            if (university_point > 5*self.P0):
                ''' For Top 10 University, Bid 69 '''
                actual_bid = (69 if (new_total_loan < 15000 or money_point >= self.P2) else 62)
            elif (university_point >= 5*self.P0):
                ''' For Top 10-26 University, Bid 59 '''
                actual_bid = (66 if (new_total_loan < 10000 or money_point >= self.P2) else 56)
            elif university_point >= 5*self.P1 and ppdloan.ppduser.education_level == '研究生及以上':
                actual_bid = (62 if money_point >= self.P2 else 56 )
            elif university_point >= 5*self.P1 and ppdloan.ppduser.education_level == '本科':
                actual_bid = (56 if (money_point >= self.P2 and history_point >= self.P2) else 51)
            elif ppdloan.ppduser.education_type == '普通' and ppdloan.ppduser.education_level == '研究生及以上' and history_point >=self.P2:
                actual_bid = 56
            elif self.get_new_total_loan(ppdloan) > 12000:
                logging.info("No Bid for new total loan(%d)>12000" % (self.get_new_total_loan(ppdloan)))
                actual_bid = 0
            elif ppdloan.ppduser.education_type == '普通' and ppdloan.ppduser.education_level == '本科' and history_point >=self.P2:
                actual_bid = 51
            elif history_point >= self.P1 and age_point >= self.P2 and money_point >= self.P1 and ppdloan.ppduser.education_university != 'NULL':
                ''' 20160303: Add money_point check to avoid bid for those who loan too much '''
                actual_bid = 50
            elif ppdloan.history_total_loan == 0 and ppdloan.ppduser.education_type == '普通' and age_point >= self.P2:
                ''' 20160301: IF it's a first loan, and has a degree (no matter good or bad) and in good age, bid 50'''
                actual_bid = 50
            elif score >= 53 and university_point <= self.P2 and history_point >= self.P1 and money_point >= self.P1  and ppdloan.ppduser.education_university != 'NULL':
                logging.info("Bid 50 for Loan without Good university but has very good history and money point! (Points: %d,%d,%d)" % (university_point, history_point, money_point))
                actual_bid = 50
            else:
                actual_bid = 0
                
            ppdloan.bid = actual_bid
            if actual_bid >= 50:
                return (True, actual_bid, "Bid/Score(%d/%d),%s" %(actual_bid, score, reason))
            else:
                return (False,0, "Score(%d),%s" %(score, reason))
    
    def C_strategy (self, ppdloan):
        if ppdloan.ppdrate != 'C':
            return (False, 0, 'Internel Error: Bad ppdrate: %s - not meet C Strategy Requirement' %(ppdloan.ppdrate))
        base_point     = 52  
        university_point = 3*self.university_strategy(ppdloan)
        history_point    = 2*self.history_strategy(ppdloan)
        money_point      = 3*self.money_strategy(ppdloan) 
        age_point        = 1*self.age_strategy(ppdloan)
        title_point      = 1*self.title_strategy(ppdloan)
        gender_point     = self.gender_strategy(ppdloan)
        cert_point       = self.cert_strategy(ppdloan)
        reason  = ppdloan.get_loan_summary()
        if (title_point < self.P2):
            reason += ",闪电借款标"
        score   = base_point + university_point + history_point + money_point + age_point + title_point + gender_point + cert_point
        new_total_loan = self.get_new_total_loan(ppdloan)
        actual_bid = 0
        logging.debug("score(%d) = base(%d) + university(%d) + history(%d) + money(%d)+age(%d)+title(%d)+gender(%d)+other_certs(%d)" % (score, base_point, university_point, history_point, money_point, age_point, title_point, gender_point, cert_point))
        ''' If score > 50, it means it's either a new loan, or from money_point perspective, it's a good bid, which is quite important for C & D Rate'''
        if score >= 51: 
            ''' Recheck using University'''
            if (university_point > 3*self.P0):
                ''' For Top 10 University, Bid 69 '''
                actual_bid = (69 if (new_total_loan < 15000 or money_point >= self.P2) else 62)
            elif (university_point >= 3*self.P0):
                ''' For Top 10-26 University, Bid 59 '''
                actual_bid = (59 if (new_total_loan < 12000 or money_point >= self.P2) else 52)
            elif history_point >= self.P2:
                ''' Else, check history records as well '''
                if ppdloan.history_return_ontime == 0 and ppdloan.history_left_loan == 0 and ppdloan.ppduser.education_type == '普通':
                    actual_bid = (53 if (university_point >= 3*self.P1 ) else 50)
                elif university_point >= 3*self.P1:
                    actual_bid = (54 if (money_point >= self.P2) else 51)
                elif university_point >= self.P2 and history_point>=self.P2 and money_point>=self.P2:
                    actual_bid = (52 if (age_point >= self.P1 and gender_point>=self.P2) else 50)
                elif (ppdloan.ppduser.education_university != 'NULL' and new_total_loan <= 9000 and ppdloan.history_left_loan <= 10 and ppdloan.history_return_ontime >= 10):
                    # Changed on 20160307
                    # Changed on 20160318 to have history_return_ontime and history_left_loan condition
                    logging.info("Bid 50 for a good C Loan as the score(%d) is really good, with University(%s),NewTotalLoan(%d)" %(score, ppdloan.ppduser.education_university, new_total_loan))
                    actual_bid = 50
                elif ppdloan.history_left_loan == 0 and ppdloan.ppduser.education_type == '普通':
                    logging.info("Bid 50 for loan without any history loans and good score (%d)" % (score))
                    actual_bid = 50
                else:
                    logging.info("NO Bid for %d(score:%d) as it doesn't match the bid strategy (loan too much or no good university)!" % (ppdloan.loanid, score))
                    actual_bid = 0
            elif score >= 54 and (ppdloan.ppduser.education_university != 'NULL' and (money_point >= self.P1 and new_total_loan < 9000)):
                actual_bid = 50
            else:
                actual_bid = 0
        else:
            actual_bid = 0
        ppdloan.score = score
        ppdloan.bid = actual_bid
        if actual_bid < 50:
            return (False, 0, "Score(%d),%s" %(score, reason))
        else:
            logging.info("Bid for %s Loan!! Bid/Score(%d/%d) - %s" %(ppdloan.ppdrate, actual_bid, score, reason))
            return (True, actual_bid, "Bid/Score(%d/%d) - %s" %(actual_bid, score, reason))
            #return (True, 50, "Bid/Score(50/%d) - %s" %(50, actual_bid, reason))
            
    def D_strategy (self, ppdloan):
        if ppdloan.ppdrate != 'D':
            return (False, 0, 'Internel Error: Bad ppdrate: %s - not meet D Strategy Requirement' %(ppdloan.ppdrate))
        base_point     = 51 # Change to 51 to allow first loan with not good age can pass the check. 
        university_point = 3*self.university_strategy(ppdloan)
        history_point    = 2*self.history_strategy(ppdloan)
        money_point      = 3*self.money_strategy(ppdloan) 
        age_point        = 1*self.age_strategy(ppdloan)
        title_point      = 1*self.title_strategy(ppdloan)
        gender_point     = self.gender_strategy(ppdloan) 
        cert_point       = self.cert_strategy(ppdloan)
        reason  = ppdloan.get_loan_summary()
        if (title_point < self.P2):
            reason += ",闪电借款标"
        score   = base_point + university_point + history_point + money_point + age_point + title_point + gender_point + cert_point
        actual_bid = 0
        logging.debug("score(%d) = base_point(%d) + university_point(%d) + history_point(%d) + money_point(%d) + age_point(%d) + title_point(%d)" % (score, base_point, university_point, history_point, money_point, age_point, title_point))
        ''' If score > 50, it means it's either a new loan, or from money_point perspective, it's a good bid, which is quite important for C & D Rate'''
        if score >= 50: 
            ''' Recheck using University'''
            if (university_point >= 3*self.P0):
                ''' For Top 26 University, Bid 58/52 '''
                actual_bid = 58 if (money_point >= self.P2) else 52
            elif history_point >= self.P2:
                ''' Else, check history records as well '''
                if ppdloan.history_return_ontime == 0 and ppdloan.history_left_loan == 0 and university_point >= 3*self.P2:
                    actual_bid = (51 if (university_point >= 3*self.P1 ) else 50)
                if university_point >= 3*self.P1:
                    actual_bid = (53 if (money_point >= self.P1) else 50)
                elif university_point >= self.P2:
                    if history_point>=self.P2 and money_point>=self.P2 and self.get_new_total_loan(ppdloan)<9500:
                        actual_bid = 50
                    elif score >=52 and (self.get_new_total_loan(ppdloan) < 8000):
                        logging.info("Bid 50 for a good D with new total_loan(%d) less than 8000, university(%s)" % (self.get_new_total_loan(ppdloan), ppdloan.ppduser.education_university))
                        actual_bid = 50
                elif (ppdloan.ppduser.education_university != 'NULL' and self.get_new_total_loan(ppdloan) < 7000 and ppdloan.history_left_loan <= 10 and ppdloan.history_return_ontime >= 10):
                        logging.info("Bid 50 for a good D with history_Left_loan 0, history_return_ontime(%d),new total_loan(%d) less than 6000, university(%s)" % (ppdloan.history_return_ontime, self.get_new_total_loan(ppdloan), ppdloan.ppduser.education_university))
                        actual_bid = 50
                else:
                    logging.info("NO Bid for %d(score:%d) as it doesn't match the bid strategy (loan too much(>8000) or no good university)!" % (ppdloan.loanid, score))
                    actual_bid = 0
            else:
                logging.info("NO Bid for %d(score:%d) as History Point(%d) is too low!!" % (ppdloan.loanid, score, history_point))
                actual_bid = 0
        else:
            actual_bid = 0
        ppdloan.score = score
        ppdloan.bid = actual_bid
        if actual_bid < 50:
            return (False, 0, "Score(%d),%s" %(score, reason))
        else:
            logging.info("Bid for %s Loan!! Bid/Score(%d/%d),%s" %(ppdloan.ppdrate, actual_bid, score, reason))
            return (True, actual_bid, "Bid/Score(%d/%d),%s" %(actual_bid, score, reason))
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
        if (ppdloan.ppduser.education_university == 'NULL') or (ppdloan.ppduser.education_level not in ('本科','研究生及以上','研究生')) \
                or ppdloan.ppduser.education_type != '普通':            
            return self.P3
        university = ppdloan.ppduser.education_university
        #university = unicode(university) # Already set in PPDLoan
        
        if university in self.university_to_rank.keys():
            rank = self.university_to_rank[university]
            logging.debug("%s found in University DB. Rank: %d" % (university, rank))
            if rank <= 10:
                return 2*self.P0
            elif rank <= 26:
                return self.P0
            elif (ppdloan.ppdrate == 'A' or ppdloan.ppdrate == 'B'):
                ''' @20160304: Change to Top 200 for 'A' or 'B' Loans '''
                return self.P1 if (rank <= 150) else (self.P2 if (rank <= 700) else self.P3)
            elif (ppdloan.ppdrate == 'C' or ppdloan.ppdrate == 'D' or ppdloan.ppdrate == 'E'):
                ''' @20160303: Change to Top 100 to further limit the bid scope and improve bid quality '''
                ''' @20160317: Change to 0-120-400- '''
                return self.P1 if (rank <= 120) else (self.P2 if (rank <= 600) else self.P3)
            else:
                return self.P3
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
    
    def get_new_total_loan(self, ppdloan):
        return ppdloan.history_left_loan + ppdloan.money - ppdloan.history_left_lend
    
    def money_strategy(self, ppdloan):
        '''
        history_total_loan/history_left_loan/history_left_lend/ Loan money for this time
        P1: left_loan + money - left_lend < total_loan*0.5
        P2: First loan, or left_loan + money - left_lend < total_loan*0.8
        P3: left_loan + money - left_lend < total_loan*1.2
        P4: money > 12000
        '''
        new_total_loan = self.get_new_total_loan(ppdloan)
        if ((ppdloan.ppdrate == 'C' or ppdloan.ppdrate == 'D') and ppdloan.money > 10000):
            ''' No Bid for C/D Loan that ask for more than 10000 '''
            return self.P4
        elif ((ppdloan.ppdrate != 'A') and (ppdloan.money % 100 != 0) and new_total_loan):
            ''' 20160304: 投那些金额整百整千, 如果穷到尾数几十块 甚至几块钱 也要借的人 反正要么是骗尽每一块钱 要么就是穷疯了 '''
            logging.debug("Return P3 for those with moeny/100 != 0 - PPDRate/Money(%s/%d)" % (ppdloan.ppdrate, ppdloan.money))
            return self.P3
        elif (new_total_loan < ppdloan.history_total_loan * 0.5):
            if (new_total_loan > 13000):
                # Limit the total Loan to be less than 12000
                return self.P2
            else:
                return self.P1
        elif ppdloan.history_total_loan == 0 and ppdloan.history_left_loan == 0:
            ''' 20160303: add check for ppdloan.history_left_loan == 0 as there are rare cases that
             loaner didn't return anything but requested another loan, which is pretty bad... '''
            return self.P2
        elif (ppdloan.ppdrate == 'B' and ppdloan.money >= 12000):
            ''' No Bid for B Loan that ask for more than 12000 '''
            return self.P4
        elif (ppdloan.ppdrate == 'A' and ppdloan.money >= 15000):
            ''' No Bid for A Loan that ask for more than 15000 '''
            return self.P4
        elif new_total_loan < ppdloan.history_total_loan * 0.7:
            return self.P2
        elif new_total_loan < ppdloan.history_total_loan * 1.2:
            return self.P3
        else:
            return self.P4

    
    def age_strategy(self, ppdloan):
        '''
        P1: age between 28 to 35
        P2: age between 26 to 38
        P3: rest of them
        '''
        if (ppdloan.age >= 28 and ppdloan.age <= 35):
            return self.P1
        elif (ppdloan.age >= 26 and ppdloan.age <= 38):
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
         
    def gender_strategy(self,ppdloan):
        '''男 :0, 女:1'''
        if (ppdloan.ppduser.gender == '男'):
            return self.P2
        elif (ppdloan.ppduser.gender == '女'):
            return self.P1
        else:
            logging.warn("Gender(%s) not Male or Female. Really!!?" % (ppdloan.ppduser.gender))
            return self.P3
    
    def cert_strategy(self, ppdloan):
        cert_points = 0
        if ppdloan.ppduser.bank_details_cert == 1:
            cert_points += 1
        if ppdloan.ppduser.ren_hang_trust_cert == 1:
            cert_points += 1    
        return cert_points