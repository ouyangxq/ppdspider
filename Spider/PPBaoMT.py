#!python
#-*- coding:utf8 -*-

"""
Created on 20160221
Main Class for PPD Spider and Auto-bid
System Name: Pai Pai Bao (PPBao)
@author: Xiaoqi Yang
"""

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
from threading import Thread
from Queue import Queue
from random import randint
from spider.PPBaoFollower import PPBaoFollower
from spider.PPBaoAdventurer import PPBaoAdventurer


class PPBaoMT(object):
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
    ppdid_to_keepmoney = {} # 18616856236 -> 0
    ppd_parser = None
    error_count = 0
    first_page_url = ''
    spider = ''
    loanids_in_memory = []
    ERRORS_BEFORE_RECONNECT = 160
    PAGES_FOR_ONE_THREAD    = 45
    follower = None
    adventurer = None
    
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
        self.loanids_in_memory = []
        self.new_loans = 0
        self.follower = None
        self.adventurer = None
        
    def init(self):
        """Init all he global variables and components of PPBao System
        Connect to local MySQL DB, and init bid strategies, and spider
        """
        for conf in self.config_files:
            ppbao_config = PPBaoConfig(conf)
            ppdloginid,dbhost,dbuser,dbpwd,dbname = ppbao_config.read_ppbao_config()

            # Only do this when ppddao is None as those are common to all PPBao Users
            if (self.ppddao == None):
                PPBaoUtil.init_logging('new', ppbao_config.logdir)
                logging.info("Welcome to PPBao MT System!")
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
            self.ppdid_to_keepmoney[ppdloginid] = ppbao_config.get_keep_money()
            logging.info("%s: Account Minimal Keep Money: %d" % (ppdloginid, self.ppdid_to_keepmoney[ppdloginid]))
            
        '''
        Just one instance for below members
        '''    
        self.follower = PPBaoFollower(self.ppdid_to_spider[self.ppdloginids[0]])
        self.ppd_parser = PPDHtmlParser()
        self.adventurer = PPBaoAdventurer(self.ppdid_to_spider[self.ppdloginids[-1]], self.ppd_parser)
        self.autobid = AutoBid()
        self.loandao = PPDLoanDAO(self.ppddao)
        self.userdao = PPDUserDAO(self.ppddao)
        self.mybiddao = MyBidDAO(self.ppddao)
        self.blacklistdao = BlackListDAO(self.ppddao)
        self.loanids_in_memory = self.loandao.get_last_n_days_loanids(3)
        university_to_rank = UniversityDAO(self.ppddao).get_university_ranks()
        if university_to_rank is None:
            logging.error("Error: Not able to query DB to get University Information. Exiting now")
            exit (3)
        else:
            PPBaoUtil.set_university_to_rank(university_to_rank)
            pass
    
    def connect_to_ppdai(self):
        """Connect to PPDai for all users 
        Only return when all users are connected, so it's important that all usernames/passwords are correct.
        """
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
            sleep(random.randint(1,6))
    
    def read_ppdai_pages(self, risk, page_start, page_end, loan_queue):
        """Main Function to Check the loans in each PPDai pages. 
        Each thread will run this Function for the pages owned by that thread. 
        """
        last_url = self.first_page_url
        new_loans = 0
        logging.debug("PPDai Page Walker of %d-%d pages started..." % (page_start, page_end))
        for page in range(page_start, page_end):
            pageurl = self.spider.build_loanpage_url(risk, page)
            logging.debug("Open page url: %s" % (pageurl))
            skipped, loanid_to_mobile, loanid_to_xueli = self.spider.get_loanid_list_from_listing_page(pageurl, last_url)
            last_url = pageurl
            if (loanid_to_xueli is None or loanid_to_mobile is None):
                self.error_count += 1
                st = random.randint(2, 7)
                logging.error("Can't get loanids! Error Count(%d). Ignore and Continue in %d seconds. Check it Later!" % (self.error_count, st))
                sleep(st)
                continue
            (new_loan, old_loan) = self.pasrse_loanid_list(loanid_to_mobile.keys(), pageurl, loan_queue, 'page_walker', loanid_to_mobile)
            new_loans += new_loan
            self.new_loans += new_loan
            self.old_loans += old_loan
            # sleep a few seconds after each page is completed.
            sleep(random.randint(1,7))
        logging.debug("PPDai Page Walker for %s %d-%d pages completed. Parsed %d new loans." % (risk, page_start, page_end, new_loans))
    

    def pasrse_loanid_list(self, loanid_list, referer_url, loan_queue, source, loanid_to_mobile=None):
        """This function is to go through the loan details page for each loanid one by one
        Tried to make this be generic as we'll need to use it for both page worker and good ppdai bidder user followers
        """
        (new_loan, old_loan) = (0, 0)
        for loanid in loanid_list:
            loanurl = self.spider.get_loanurl_by_loanid(loanid)
            if (loanid in self.loanids_in_memory):
                #logging.debug("Loanid %d is already in DB. Ignore." % (loanid))
                old_loan += 1
            else:
                new_loan += 1
                logging.debug("New Loan list: %d" % (loanid))
        
                html = self.spider.open_loan_detail_page(loanurl, referer_url)
                referer_url = loanurl
                if (html is None):
                    self.error_count += 1
                    st = random.randint(3,7)
                    logging.error("Can't open %s. Error Count:%d. Ignore and Continue in %d seconds." %(loanurl, self.error_count, st))
                    sleep(st)
                else:
                    now = datetime.now() # Record Down the current datetime
                    ppdloan, ppduser, mymoney = self.ppd_parser.parse_loandetail_html(loanid, now, html)                                
                    if ppdloan == None:
                        if mymoney == None: # if it's -1,then it's just we're too slow as the loan is 100% completed, no error.
                            self.error_count += 2
                            logging.error("ErrorCount(%d): Not able to parse  HTML to get ppdloan. DO CHECK IT. Ignore and Continue for now!" % (self.error_count))
                        sleep(random.randint(3,5))
                    else:
                        # This is what we really need
                        self.ppdid_to_leftmoney[self.ppdloginids[0]] = mymoney
                        if (loanid_to_mobile != None):
                            ppduser.mobile_cert = loanid_to_mobile[loanid]
                        ppdloan.set_source(source)
                        self.loanids_in_memory.append(loanid)
                        loan_queue.put(ppdloan)
                        #logging.info("Put Loan into Queue: %d" % loanid)
                        sleep(random.randint(3,6))
        return (new_loan, old_loan)
    
    def check_and_bid(self, loan_queue):
        """Check the PPDLoan in loan_queue by the Strategies defined for each user, and bid if any strategy is met.
        """
        
        logging.info("PPBao BidThread is started! Ready to work ^_^") 
        while (1):
            if (loan_queue.empty()):
                sleep(random.randint(1,3))
            else:
                try:
                    ppdloan = loan_queue.get(1)
                    for ppdid in self.ppdloginids:
                        ppduserid     = self.ppdid_to_userid[ppdid]
                        # AutoBid
                        ifbid, bidmoney, reason, bid_strategy = self.ppdid_to_bidstrategy[ppdid].check_by_strategy(ppdloan)
                        if ifbid == True and bidmoney > 0:
                            # Reset bidmoney if necessary
                            if ((bidmoney is not None) and (self.ppdid_to_leftmoney.has_key(ppdid)) and ((self.ppdid_to_leftmoney[ppdid]-self.ppdid_to_keepmoney[ppdid]) < bidmoney)):
                                if ((self.ppdid_to_leftmoney[ppdid]-self.ppdid_to_keepmoney[ppdid]) < 50):
                                    ''' 50 is the minimal number to bid '''
                                    logging.warn("%s: NOT ENOUGH MONEY in My Account to Bid(Account Left: %d; Keep: %d; Bid: %d) Will Run without BID!!!" % (ppdid, self.ppdid_to_leftmoney[ppdid], self.ppdid_to_keepmoney[ppdid], bidmoney))
                                    logging.info("%s: No Money to Bid for %d: %s" % (ppdid, ppdloan.loanid, reason))
                                    bidmoney = 0
                                    continue   # No processing further as no money to bid
                                else:
                                    logging.warn("Change to bid %d as we only have this amount of money left in PPDAI Account for %s" %(self.ppdid_to_leftmoney[ppdid], ppduserid))
                                    bidmoney = self.ppdid_to_leftmoney[ppdid] -self.ppdid_to_keepmoney[ppdid]
                                    logging.warn("%s: Bid Loanid %d with Money %d. Reason: %s" %(ppdid, ppdloan.loanid, bidmoney, reason))
                            self.error_count = 0
                            ppdloan.score = bidmoney
                            if self.NOBID == True:
                                ppdloan.bid = 0 # override to 0
                                self.mybiddao.insert_bid_record(ppdloan.loanid, datetime.now(), 0, ppduserid, "NoBidMode:" + reason, bid_strategy.strategy_name)
                            else:
                                ''' 'Actually bid for it!!! '''
                                (actual_bid_money, mymoney_left) = self.autobid.bid(self.ppdid_to_spider[ppdid].opener, ppdloan.loanid, ppdloan.maturity, bidmoney)
                                if actual_bid_money > 0:
                                    self.mybiddao.insert_bid_record(ppdloan.loanid, datetime.now(), actual_bid_money, ppduserid, reason, bid_strategy.strategy_name)
                                    logging.info("DONE Bid %d for loanid %d!!! My Account Left: %4.2f" % (actual_bid_money, ppdloan.loanid, mymoney_left))
                                else:
                                    logging.warn("Bid Failed. No Worries. let's keep going!")
                                if (mymoney_left > 0):
                                    self.ppdid_to_leftmoney[ppdid] = mymoney_left
                                ppdloan.bid = actual_bid_money  
                            sleep(random.randint(1,4))
                        else:
                            if ppdid == self.ppdloginids[0]:
                                #logging.info("%s: NoBid: %d: %s" %(ppduserid, loanid, reason))
                                logging.info("NoBid: %d: %s" %(ppdloan.loanid, reason))
                    
                    #self.error_count = 0
                    self.loandao.insert(ppdloan)
                    self.userdao.insert_if_not_exists(ppdloan.ppduser)
                except Exception, e:
                    logging.error("Encounter Exception in check_and_bid_thread: %r" % (e))
                    traceback.print_exc()
                    sleep(randint(3,6))
        logging.info("BidThread is completed! Hard to get to here as it's using while(1).")
    
    def create_page_worker_threads(self, risk, pages, loan_queue, iteration=30):
        worker_threads = []
        num_of_threads = int(pages / iteration) if (pages % iteration == 0) else int(pages / iteration + 1)
        for i in range (1,num_of_threads+1):
            page_start = (i-1)*iteration +1
            page_end   = pages if (i== num_of_threads) else i*iteration
            worker_thread = Thread(target=self.read_ppdai_pages, args=(risk, page_start, page_end, loan_queue))
            worker_threads.append(worker_thread)
        logging.debug("Created %d PPDai loan page reader threads." % (len(worker_threads)))
        return worker_threads
        
    def check_followers(self, loan_queue):
        rd = 1
        userids = self.follower.get_follow_users()
        logging.info("PPBao CheckFollowers Thread is started! Follow Users are: %s" % (','.join(userids)))
        while (1):
            (new_loans, old_loans) = (0, 0)
            for userid in userids:
                logging.info("Checking latest bids by User %s ..." % (userid))
                try:
                    loanids = self.follower.get_latest_loanid_list(userid)
                    url = self.follower.get_follow_user_url(userid)
                    (new_loan, old_loan) = self.pasrse_loanid_list(loanids, url, loan_queue, userid, None)
                    new_loans += new_loan
                    old_loans += old_loan
                    sleep(random.randint(2,16))
                except Exception,e:
                    logging.error("check_followers_thread: Encounter Exception: %r" %(e))
                    traceback.print_exc()
                    sleep(random.randint(20,60))
            userids = self.follower.get_follow_users()
            random.shuffle(userids)
            sleeptime = random.randint(3,40)
            logging.info(">>>>>> PPBaoFollower - Done Round %d <<<<<< New Loans(%d),Old Loans(%d). Sleep %d seconds before next round." % (rd, new_loans, old_loans, sleeptime))
            rd += 1
            sleep(sleeptime)
    
    def adventure(self, loan_queue):
        rd = 1
        start_loanid = self.loandao.get_latest_loanid_by_ppbaoadventurer() # need a better way to set this one, maybe last bid loanid?
        stop_loanid  = max(self.loanids_in_memory)
        logging.info("PPBao Adventurer Thread is started! Start-Stop loanid: %d - %d" %(start_loanid, stop_loanid))
        while (1):
            stop_loanid  = max(self.loanids_in_memory)
            
            if (start_loanid < stop_loanid):
                logging.info("*** PPBaoAdventurer - Round %d *** Start LoanId(%d). Stop LoanId(%d)" % (rd, start_loanid, stop_loanid))
                last_loanid,new_loanids, under_evaluation_loanids, invalid_loanids = self.adventurer.lets_adventure(loan_queue, start_loanid, self.loanids_in_memory)
                start_loanid = last_loanid
                sleeptime = random.randint(50,180)
                logging.info("*** PPBaoAdventurer - Done Round %d *** Latest LoanId(%d),New Loans(%d),UnderEvaluation(%d),Invalid(%d). Sleep %d seconds before next round." % (rd, last_loanid, new_loanids, under_evaluation_loanids, invalid_loanids, sleeptime))
                rd += 1
            else:
                logging.info("PPBaoAdventurer - Wait for next round as Start Loanid >= Stop Loanid (%d >= %d)" % (start_loanid, stop_loanid))
                sleeptime = random.randint(120,300)

            sleep(sleeptime)
    
    def aa13_checker(self, loan_queue):
        rd = 1
        while (1):
            try:
                self.read_ppdai_pages(self.spider.risksafe, 1, 1, loan_queue)
            except Exception,e:
                self.error_count += 1
                logging.error("Un-Caught Error!!! Continue with next round - Please do Check IT!! %r" %(e))
                traceback.print_exc()
                sleep(random.randint(6,12))
            if (rd % 10 == 0):
                rdint = random.randint(30,60) # Sleep more time on every 20 round.
            elif (rd % 100 == 0):
                rdint = random.randint(60,90)
            elif (rd % 400 == 0):
                rdint = random.randint(90,600)
            else:
                rdint = random.randint(10,30)
            logging.info(">>> AA13Checker: Done Round %d. Sleep %d seconds..." % (rd, rdint))
            rd += 1
            sleep(rdint)
    
    def run(self):
        rd  = 1  # Round
        self.error_count = 0 # This record down how many errors we have during the run.
        self.spider = self.ppdid_to_spider[self.ppdloginids[0]]
        # Shared QUQUE
        loan_queue = Queue(100)

        check_and_bid_thread = Thread(target=self.check_and_bid, args=(loan_queue,), name='check_and_bid_thread')
        check_and_bid_thread.start()
        check_followers_thread = Thread(target=self.check_followers, args=(loan_queue,), name='check_followers_thread')
        check_followers_thread.start()
        #adventure_thread = Thread(target=self.adventure, args=(loan_queue,), name='adventure_thread')
        #adventure_thread.start()
        #aa13_checker_thread = Thread(target=self.aa13_checker, args=(loan_queue,), name='aa13checker_thread')
        #aa13_checker_thread.start()

        while (1):
            ''' 20160304: Add AutoLogin after 20 Errors so as we can recover from unexpected error/exceptions '''
            (self.new_loans, self.old_loans) = (0,0)
            if self.error_count >= self.ERRORS_BEFORE_RECONNECT:
                logging.info("Re-connecting to PPDAI as we have encountered %d Errors/Exceptions." % (self.error_count))
                self.connect_to_ppdai()
                sleep(random.randint(5,20))
                self.error_count = 0
            
            # @Change History
            # 20160307: remove: spider.risksafe as I already bid more than 3000 for 12/12 AA Peibiao
            # 20160625: Remove while and add check for risksafe page 1 for 13% AA loans (defined in bid strategy)
            try:
                risk = self.spider.riskmiddle 
                self.first_page_url = self.spider.build_loanpage_url(risk, 1)
                count, pages,skipped, loanid_to_mobile, loanid_to_xueli = self.spider.get_pages(self.first_page_url, PPDSpider.get_login_url())
                if count == 0:
                    logging.info("No Loan of risktype %s is available. Next..." % risk)
                    sleep(random.randint(10,30))
                    continue
                elif count < 0: # -1 means we encountered an error
                    logging.error("Error: Not able to open %s to get total loans and pages.")
                    self.error_count += 5;
                    sleep(random.randint(10,60))
                    continue
                else:
                    logging.info("****** Round %d ****** Total Loans: %d (%d pages). Checking..." % (rd, count, pages))                    
                    
                # Create threads to read the pages in parallel
                page_reader_threads = []
                page_reader_threads = self.create_page_worker_threads(risk, pages, loan_queue, self.PAGES_FOR_ONE_THREAD)
                for pt in page_reader_threads:
                    pt.start()

                # Wait until all threads are completed. 20160520: add timeout to max half hour.
                for pt in page_reader_threads:
                    pt.join(timeout=1800)
                
                
                logging.info("Parsed new_loans(%d), old_loans(%d), skipped_loans(%d)" % (self.new_loans, self.old_loans,0))
            except Exception, e:
                self.error_count += 1
                logging.error("Un-Caught Error!!! Continue with next round - Please do Check IT!! %r" %(e))
                traceback.print_exc()
                sleep(random.randint(6,12))
            
            if (rd == 10 or rd == 150):
                sleep(1)
                logging.info("Updating Black List...")
                self.update_black_list()
            if (rd % 20 == 0):
                rdint = random.randint(30,60) # Sleep more time on every 20 round.
            elif (rd % 100 == 0):
                rdint = random.randint(30,90)
                # Reconnect once 400 round to avoid "MySQL has gone away error..."
                self.ppddao.disconnect()
                self.ppddao.connect()
            elif (rd % 400 == 0):
                rdint = random.randint(90,600)
            else:
                rdint = random.randint(10,30)
            logging.info("****** Done Round %d ****** Sleep for %d seconds before next run." % (rd, rdint))
            rd += 1
            sleep(rdint)
        # End of while(1)
        """ TODO: It shall never reach here for now, we need to find a more elegant way to exit the program"""
        check_and_bid_thread.join()
        check_followers_thread.join()
        #adventure_thread.join()
        #aa13_checker_thread.join()
    
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
        If it's a New Loan(In Memory/DB Check), apply the strategy to check if it's good enough for bid
        If it's good for bid, 
            bid it
            record into MYSQL DB 
        Record the Loan information and User information into MYSQL
    4. Sleep and continue with step 2
    '''
    
    #ppbao = PPBaoMT(("conf/ppbao.18616856236.config","conf/ppbao.18616027065.config"))
    #ppbao = PPBaoMT(("conf/ppbao.18616027065.config",))
    #ppbao = PPBaoMT(("conf/ppbao.18616856236.config",))
    ppbao = PPBaoMT(("conf/ppbao.me.config",))
    #ppbao = PPBaoMT(("conf/ppbao.me.config","conf/ppbao.ss.config"))
    ppbao.init()
    ppbao.connect_to_ppdai()
    ppbao.run()
