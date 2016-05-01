#!python
#-*- coding:utf8 -*-

'''
Created on 20160221
Main Class for PPD Spider and Auto-bid
System Name: Pai Pai Bao (PPBao)
@author: Xiaoqi Yang
'''
from biz.PPDHtmlParser import PPDHtmlParser
from dao.PPDDAO import PPDDAO
from dao.PPDLoanDAO import PPDLoanDAO
from dao.PPDUserDAO import PPDUserDAO
from dao.UniversityDAO import UniversityDAO
from dao.MyBidDAO import MyBidDAO
from dao.PPBaoUserDAO import PPBaoUserDAO
from dao.BlackListDAO import BlackListDAO
from spider.PPDBlacklist import PPDBlacklist
from spider.PPDSpider import PPDSpider
from biz.AutoBid import AutoBid
from util.PPBaoUtil import PPBaoUtil
import logging
from datetime import datetime
from datetime import date
from datetime import timedelta
from time import sleep
import random
import traceback
from sys import argv
from util.PPBaoConfig import PPBaoConfig
from biz.BidStrategyPlus import BidStrategyPlus


class PPBao(object):
    # TO BE Implemented
    config_files = []
    ppddao = None
    NOBID  = False
    ppdloginids  = [] # 
    ppdid_to_pwd = {}
    ppdid_to_spider = {}
    ppdid_to_bidstrategy = {}
    ppdid_to_userid = {} # 18616856236 -> pdu2517233537
    ppdid_to_leftmoney = {}
    ppd_parser = None
    
    def __init__(self, config_files):
        if isinstance(config_files, str) == True: 
            self.config_files = (config_files,)
        elif isinstance(config_files, list) == True or isinstance(config_files, tuple) == True:
            self.config_files = config_files
        else:
            print "Failed to init PPBao! Wrong PPBao Config file!"
            exit (-1)
        self.ppdloginids  = []
        self.ppdid_to_pwd =  {}
        self.ppdid_to_spider =  {}
        self.ppdid_to_leftmoney = {}
        self.ppdid_to_bidstrategy = {}
        self.ppd_parser = None
        
    def init(self):
        for conf in self.config_files:
            ppbao_config = PPBaoConfig(conf)
            ppdloginid,dbhost,dbuser,dbpwd,dbname = ppbao_config.read_ppbao_config()

            # Only do this when ppddao is None as those are common to all PPBao Users
            if (self.ppddao == None):
                PPBaoUtil.init_logging('new', ppbao_config.logdir)
                logging.info("Welcome to PPBao System!")
                logging.info("Developed By Xiaoqi Ouyang. All Rights Reserved@2016-2017")
                logging.info("PPBao Config: %s,%s,%s,%s,%s" % (ppdloginid,dbhost,dbuser,dbpwd,dbname))
                ''' Init DB Modules '''
                self.ppddao = PPDDAO({'host':dbhost,'username':dbuser,'password':dbpwd,'database':dbname})
                dbok   = self.ppddao.connect()
                if dbok == False:
                    logging.error("Error: Not able to connect to MySQL! Please Fix it. Exiting now")
                    exit (1)
                ppbaouserdao = PPBaoUserDAO(self.ppddao)
            # The below statements need to be done for each user
            (ppduserid_db,ppdpasswd) = ppbaouserdao.get_ppduserid_and_passwd(ppdloginid)
            if (ppduserid_db is None or ppdpasswd is None):
                logging.error("Error: Not able to get PPDAI loginid/passwd for %s. Invalid PPBao User!! Exiting!" %(ppdloginid))
                exit (2)
            self.ppdloginids.append(ppdloginid)
            self.ppdid_to_pwd[ppdloginid] = ppdpasswd
            strategy_plus = BidStrategyPlus(ppbao_config)
            self.ppdid_to_bidstrategy[ppdloginid] = strategy_plus
            spider = PPDSpider(ppdloginid, ppbao_config)
            self.ppdid_to_spider[ppdloginid] = spider
                
        self.ppd_parser = PPDHtmlParser()
        self.autobid = AutoBid()
        self.loandao = PPDLoanDAO(self.ppddao)
        self.userdao = PPDUserDAO(self.ppddao)
        self.mybiddao = MyBidDAO(self.ppddao)
        self.blacklistdao = BlackListDAO(self.ppddao)
        university_to_rank = UniversityDAO(self.ppddao).get_university_ranks()
        if university_to_rank is None:
            logging.error("Error: Not able to query DB to get University Information. Exiting now")
            exit (3)
        else:
            PPBaoUtil.set_university_to_rank(university_to_rank)
            pass
    
    def connect_to_ppdai(self):
        for ppdid in self.ppdloginids:
            ppdpwd = self.ppdid_to_pwd[ppdid]
            spider = self.ppdid_to_spider[ppdid]
            logging.info("Logging for %s ..." % (ppdid))
            (opener, ppduserid) = spider.login_until_success(ppdid, ppdpwd) 
            if (opener == None or ppduserid == None):
                logging.error("Error: Not able to get opener or PPDAI Username is None! Exit...")
                exit(4)
            else:
                self.ppdid_to_userid[ppdid] = ppduserid
            sleep(random.randint(2,6))
    
    def run(self):
        rd  = 1  # Round
        error_count = 0 # This record down how many errors we have during the run.
        last_url    = PPDSpider.get_login_url()  # This is used to record the last URL to use as Referer
        mybid_list  = [] # mybid list
        ppd_main_id = self.ppdloginids[0]
        spider = self.ppdid_to_spider[ppd_main_id]
        loanids_in_memory = self.loandao.get_last_2_days_loanids()
        while (1):
            ''' 20160304: Add AutoLogin after 20 Errors so as we can recover from unexpected error/exceptions '''
            loanids_in_this_round = []
            if error_count >= 20:
                self.connect_to_ppdai()
                sleep(random.randint(5,20))
            for risk in [spider.riskmiddle]: # 20160307: remove: spider.risksafe as I already bid more than 3000 for 12/12 Peibiao 
                try: 
                    first_page_url = spider.build_loanpage_url(risk, 1)
                    count, pages,firstpage_loanurl_list, skipped = spider.get_pages(first_page_url, last_url)
                    last_url = first_page_url
                    old_loans, new_loans, skipped_loans = (0, 0, skipped) # to record how many old/new and skipped loans in this round
                    if count == 0:
                        logging.info("No Loan of risktype %s is available. Next..." % risk)
                        sleep(random.randint(1,4))
                        continue;
                    elif count < 0: # -1 means we encountered an error
                        logging.error("Error: Not able to open %s to get total loans and pages.")
                        error_count += 5;
                        continue;
                    else:
                        logging.info("****** Round %d ****** Total Loans: %d (%d pages). Checking..." % (rd, count, pages))
                        sleep(random.randint(1,2))
    
                    ''' Notice range (1,2) will only returns 1, so need pages +1 '''
                    for index in range(1,pages+1):
                        if (index > 1): 
                            pageurl = spider.build_loanpage_url(risk, index)
                            logging.debug("Open page url: %s" % (pageurl))
                            skipped, loanurls = spider.get_loan_list_urls(pageurl,last_url)
                            last_url = pageurl
                            if (loanurls is None):
                                error_count += 1
                                st = random.randint(2,7)
                                logging.error("Can't get loanurls. Error Count(%d). Ignore and Continue in %d seconds. Check it Later!" % (error_count, st))
                                sleep(st)
                                continue
                            skipped_loans += skipped
                        else:
                            pageurl = spider.build_loanpage_url(risk, 1)
                            last_url = pageurl
                            loanurls = firstpage_loanurl_list
                            logging.debug(loanurls)
                        for loanurl in loanurls: 
                            loanid = spider.get_loanid_from_url(loanurl)
                            if loanid is None:
                                error_count += 1
                                st = random.randint(1,5)
                                logging.error("Not able to get loanid from %s.Continue in %d seconds." % (loanurl, st))
                                sleep(st)
                                continue
                            
                            loanids_in_this_round.append(loanid)
                            if (loanid in loanids_in_memory):
                                logging.debug("Loanid %d is already in DB. Ignore." % (loanid))
                                old_loans += 1
                                continue
                            else:
                                new_loans += 1
                                logging.debug("New Loan list: %d" % (loanid))
        
                                html = spider.open_loan_detail_page(loanurl, pageurl)
                                last_url = loanurl
                                if (html is None):
                                    error_count += 1
                                    st = random.randint(2,7)
                                    logging.error("Can't open %s. Error Count:%d. Ignore and Continue in %d seconds." %(loanurl, error_count, st))
                                    sleep(st)
                                    continue
    
                                now = datetime.now() # Record Down the current datetime
                                ppdloan, ppduser, mymoney = self.ppd_parser.parse_loandetail_html(loanid, now, html)
                                if ppdloan == None:
                                    if mymoney == None: # if it's -1,then it's just we're too slow as the loan is 100% completed, no error.
                                        error_count += 2
                                        logging.error("ErrorCount(%d): Not able to parse  HTML to get ppdloan. DO CHECK IT. Ignore and Continue for now!" % (error_count))
                                    sleep(random.randint(1,5))
                                    continue
                                else:
                                    self.ppdid_to_leftmoney[ppd_main_id] = mymoney
                                for ppdid in self.ppdloginids:
                                    ppduserid     = self.ppdid_to_userid[ppdid]
                                    # AutoBid
                                    ifbid, bidmoney, reason = self.ppdid_to_bidstrategy[ppdid].check_by_strategy(ppdloan)
                                                                        
                                    if ((bidmoney is not None) and (self.ppdid_to_leftmoney.has_key(ppdid)) and (self.ppdid_to_leftmoney[ppdid] < bidmoney)):
                                        logging.warn("%s: NOT ENOUGH MONEY in My Account to Bid(%d<%d). Will Run without BID!!!" % (ppdid, mymoney, bidmoney))
                                        logging.info("%s: No Money to Bid for %d: %s" % (ppdid, loanid, reason))
                                    elif ifbid == True:
                                        if loanid not in mybid_list:
                                            mybid_list.append(loanid)
                                        logging.warn("%s: Bid Loanid %d with Money %d (MyAccount Left:%4.2f). Reason: %s" %(ppdid, loanid, bidmoney, mymoney, reason))
                                        ppdloan.score = bidmoney
                                        if self.NOBID == True:
                                            ppdloan.bid = 0 # override to 0
                                            self.mybiddao.insert_bid_record(loanid, now, 0, ppduserid, "NoBidMode:" + reason)
                                        else:
                                            # Actually bid for it
                                            (actual_bid_money, mymoney_left) = self.autobid.bid(self.ppdid_to_spider[ppdid].opener, loanid, ppdloan.maturity, bidmoney, reason)
                                            if actual_bid_money > 0:
                                                self.mybiddao.insert_bid_record(loanid, now, actual_bid_money, ppduserid, reason)
                                                logging.info("DONE!!! Bid %d for loanid %d!!!" % (actual_bid_money, loanid))
                                            else:
                                                logging.warn("Bid Failed. No Worries. let's keep going!")
                                            if (mymoney_left > 0):
                                                self.ppdid_to_leftmoney[ppdid] = mymoney_left
                                            ppdloan.bid = actual_bid_money  
                                        sleep(random.randint(1,4))                                      
                                    else:
                                        if ppdid == ppd_main_id:
                                            logging.info("%s: NoBid for %d: %s" %(ppduserid, loanid, reason))                                    
        
                                # Write to MYSQL
                                loanids_in_memory.append(loanid)
                                self.loandao.insert(ppdloan)
                                self.userdao.insert_if_not_exists(ppduser)
                                # If we can reach here, means everything is fine. We shall reset error_count = 0
                                error_count = 0
                                if ppdloan.loanrate < 10: # No need to check more Loans as we've sorted the pages
                                    sleep(random.randint(1,3))
                                    break
                                else:
                                    sleep(random.randint(1,3))
                        sleep(random.randint(1,4))
                    # End of parsing all the pages
                    logging.info("Parsed %d loans: new_loans(%d), old_loans(%d), skipped_loans(%d)" % (len(loanids_in_this_round), new_loans, old_loans, skipped_loans))
                except Exception, e:
                    error_count += 1
                    logging.error("Un-Caught Error!!! Continue with next round - Please do Check IT!! %r" %(e))
                    traceback.print_exc()
                    sleep(random.randint(6,12))
            
                                # Reset loanids_in_memory as we don't need to keep history old loanids. 
            ''' Seems there is a BUG which will cause duplicate BIDs if we reset loanids in memory everytime'''
            ''' Probably caused by ppdai not stable caused it read the page url fail and miss some Loans '''
            ''' Solution is to only reset on Round 1!!! '''
            if (rd == 1 and len(loanids_in_this_round) > 1):
                loanids_in_memory = loanids_in_this_round
            if (rd == 1 or (rd % 400 == 0)):
                sleep(1)
                logging.info("Updating Black List...")
                self.update_black_list()
            if (rd % 20 == 0):
                rdint = random.randint(20,60) # Sleep more time on every 20 round.
            elif (rd % 100 == 0):
                rdint = random.randint(30,90)
            elif (rd % 400 == 0):
                rdint = random.randint(90,600)
            else:
                rdint = random.randint(6,20)
            logging.info("****** Done Round %d ****** Sleep for %d seconds before next run." % (rd, rdint))
            rd += 1
            sleep(rdint)
        # End of while(1)
    
    def update_black_list(self):
        today = date.today()
        for ppdid in self.ppdloginids:
            ppduserid   = self.ppdid_to_userid[ppdid]
            spider      = self.ppdid_to_spider[ppdid]
            logging.info("Checking black list for %s ..." % (ppduserid))
            blacklist_worker = PPDBlacklist(spider)
            blacklists = blacklist_worker.get_blacklist(ppduserid)
            for blackloan in blacklists:
                blackloan.ppbaouserid = ppduserid
                # Set Date
                overdue_date = today + timedelta(days = (1-blackloan.overdue_days))
                blackloan.overdue_date = overdue_date;
                logging.info("Black List: " + blackloan.get_summary()) 
            self.blacklistdao.update_blacklist(ppduserid, blacklists)
            logging.info("All Blacklist Info have been updated/inserted into DB now!!")
            
            logging.info("Update Profit Summary for %s..." %(ppdid))
            myprofit = blacklist_worker.get_myprofit(today, ppduserid)
            logging.info("Profit Summary:" + myprofit.get_summary())
            self.blacklistdao.update_myprofit(myprofit)
            logging.info("Profit Info has been updated into DB.")
# MAIN
if __name__ == '__main__':
    '''
    1. Login 
    2. Get List of Loans
    3. For each Loan:
        If it's a New Loan(In Memory/DB Check), apply the strategy to see if it's good enough for bid
        If it's good for bid, 
            bid it
            record down into MYSQL mybid 
        Record the Loan information and User information into MYSQL
    4. Sleep an round time and continue with step 2
    '''
    
    #ppbao = PPBao(("conf/ppbao.18616856236.config","conf/ppbao.18616027065.config"))
    #ppbao = PPBao(("conf/ppbao.18616027065.config",))
    ppbao = PPBao(("conf/ppbao.18616856236.config",))
    ppbao.init()
    ppbao.connect_to_ppdai()
    ppbao.run()