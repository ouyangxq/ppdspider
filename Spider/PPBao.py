#!python
#-*- coding:utf8 -*-

'''
Created on 20160221
Main Class for PPD Spider and Auto-bid
System Name: Pai Pai Bao (PPBao)
@author: Xiaoqi Yang
'''
from biz.PPDHtmlParser import PPDHtmlParser
from biz.BidStrategy import BidStrategy
from dao.PPDDAO import PPDDAO
from dao.PPDLoanDAO import PPDLoanDAO
from dao.PPDUserDAO import PPDUserDAO
from dao.UniversityDAO import UniversityDAO
from dao.MyBidDAO import MyBidDAO
from dao.PPBaoUserDAO import PPBaoUserDAO
from spider.PPDSpider import PPDSpider
from biz.AutoBid import AutoBid
from util.PPBaoUtil import PPBaoUtil
import logging
import os
from datetime import date
from datetime import datetime
from time import sleep
import random
import traceback
from sys import argv
from util.PPBaoConfig import PPBaoConfig
from biz.BidStrategyPlus import BidStrategyPlus

def init_logging(ppdid, logdir):
    today = date.today().isoformat()
    logfile = "%s/ppbao.%s.%s.log" % (logdir, ppdid, today)
    i = 1
    while os.path.exists(logfile):
        logfile = "%s/ppbao.%s.%s.%d.log" % (logdir, ppdid, today, i)
        i += 1
    logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename=logfile,
                filemode='a')
    #定义一个StreamHandler，将INFO级别或更高的日志信息打印到标准错误，并将其添加到当前的日志处理对象#
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s %(levelname)-4s %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)


def init_ppbao(argv):
    ''' TO Be implemented '''
    pass

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
    ppbao_config_file = None
    NOBID = False # !!! NOBID Mode until we fix the Spider!!! This is only for testing purpose.
    if (len(argv) == 1):
        ppbao_config_file = "conf/ppbao.config"
    elif (len(argv) == 2):
        me,ppbao_config_file = argv
    else:
        print "Error: More than 1 argument is provided!"
        print "Usage: python PPBao.py <ppbao_config_file>"
        exit (-1)

    # Initialize
    ppbao_config = PPBaoConfig(ppbao_config_file)
    ppdloginid,dbhost,dbuser,dbpwd,dbname = ppbao_config.read_ppbao_config()
    init_logging(ppdloginid, ppbao_config.logdir)
    logging.info("Welcome to PPBao System!")
    logging.info("Developed By Xiaoqi Ouyang. All Rights Reserved@2016-2017")
    logging.info("PPBao Config: %s,%s,%s,%s,%s" % (ppdloginid,dbhost,dbuser,dbpwd,dbname))

    # Init DB Modules
    ppddao = PPDDAO({'host':dbhost,'username':dbuser,'password':dbpwd,'database':dbname})
    dbok   = ppddao.connect()
    if dbok == False:
        logging.error("Error: Not able to connect to MySQL! Please Fix it. Exiting now")
        exit (1)
    ppbaouserdao = PPBaoUserDAO(ppddao)
    (ppduserid_db,ppdpasswd) = ppbaouserdao.get_ppduserid_and_passwd(ppdloginid)
    if (ppduserid_db is None or ppdpasswd is None):
        logging.error("Error: Not able to get PPDAI loginid/passwd for %s. Invalid PPBao User!! Exiting!" %(ppdloginid))
        exit (2)
    loandao = PPDLoanDAO(ppddao)
    userdao = PPDUserDAO(ppddao)
    mybiddao = MyBidDAO(ppddao)
    university_to_rank = UniversityDAO(ppddao).get_university_ranks()
    if university_to_rank is None:
        logging.error("Error: Not able to query DB to get University Information. Exiting now")
        exit (3)
    else:
        PPBaoUtil.set_university_to_rank(university_to_rank)
        
    # Keep loain is in memory for fast processing
    loanids_in_memory = loandao.get_last_2_days_loanids()

    # Login to PPDAI!
    spider = PPDSpider(ppdloginid, ppbao_config)
    parser = PPDHtmlParser()
   
    (opener, ppduserid) = spider.login_until_success(ppdloginid, ppdpasswd) 
    if (ppduserid == None or ppduserid != ppduserid_db):
        logging.error("Error: Not able to get PPDAI Username or is not consistent with that in DB! Exit...")
        exit(4)
    # Initialize Strategy & AutoBid Components
    strategy = BidStrategy(university_to_rank)
    strategy_plus = BidStrategyPlus(ppbao_config)
    autobid  = AutoBid()

    ''' We're ready to have FUN now!!! ''' 
    sleep(random.randint(1,4))
    rd  = 0  # Round
    error_count = 0 # This record down how many errors we have during the run.
    last_url    = spider.get_login_url()  # This is used to record the last URL to use as Referer
    while (1):
        ''' 20160304: Add AutoLogin after 20 Errors so as we can recover from unexpected error/exceptions '''
        if error_count >= 20:
            sleep(random.randint(30,60))
            logging.warn("PPBAO: We've encountered %d errors. We'll re-login to continue!" % (error_count))
            (opener, ppduserid) = spider.login_until_success(ppdloginid, ppdpasswd) 
            if opener == None:
                logging.error("Not able to login after %d Errors. Check it! Exit..." % (error_count))
                exit(3)
            error_count = 0
            sleep(random.randint(5,20))
        for risk in [spider.riskmiddle]: # 20160307: remove: spider.risksafe as I already bid more than 3000 for 12/12 Peibiao 
            try: 
                first_page_url = spider.build_loanpage_url(risk, 1)
                count, pages,firstpage_loanurl_list = spider.get_pages(first_page_url, last_url)
                last_url = first_page_url
                if count == 0:
                    logging.info("No Loan of risktype %s is available. Next..." % risk)
                    sleep(random.randint(1,4))
                    continue;
                elif count < 0:
                    logging.error("Error: Not able to open %s to get total loans and pages.")
                    error_count += 5;
                    continue;
                else:
                    logging.info("Count of Loans in %s: %d. Checking..." % (risk, count))
                    sleep(random.randint(1,3))
                # Reset Pages to not get too many unuseful DATA
                if ((risk == spider.risksafe or risk == spider.riskhigh) and pages > 2):
                    ''' for riskhigh and safe, only query the first 2 pages as we already sorted them by Rate'''
                    pages = 2

                ''' Notice range (1,2) will only returns 1, which means we won't read the last page, which is fine '''
                for index in range(1,pages):
                    if (index > 1): 
                        pageurl = spider.build_loanpage_url(risk, index)
                        logging.debug("Open page url: %s" % (pageurl))
                        loanurls = spider.get_loan_list_urls(pageurl,last_url)
                        last_url = pageurl
                        if (loanurls is None):
                            error_count += 1
                            st = random.randint(2,7)
                            logging.error("Can't get loanurls. Error Count(%d). Ignore and Continue in %d seconds. Check it Later!" % (error_count, st))
                            sleep(st)
                            continue
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
                        
                        if (loanid in loanids_in_memory):
                            logging.debug("Loanid %d is already in DB. Ignore." % (loanid))
                            continue
                        else:
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
                            ppdloan, ppduser, mymoney = parser.parse_loandetail_html(loanid, now, html)
                            if ppdloan == None:
                                if mymoney == None: # if it's -1,then it's just we're too slow as the loan is 100% completed, no error.
                                    error_count += 2
                                    logging.error("ErrorCount(%d): Not able to parse  HTML to get ppdloan. DO CHECK IT. Ignore and Continue for now!" % (error_count))
                                sleep(random.randint(1,5))
                                continue;
                            # AutoBid
                            ifbid,bidmoney, reason = strategy_plus.check_by_strategy(ppdloan)
                            if ((bidmoney is not None) and (mymoney < bidmoney)):
                                logging.warn("NOT ENOUGH MONEY in My Account to Bid(%d<%d). Will Run without BID!!!" % (mymoney,bidmoney))
                                logging.info("No Money to Bid for %d: %s" % (loanid, reason))
                            elif ifbid == True:
                                logging.warn("ATTENTION: Bid Loanid %d with Money %d (MyAccount Left:%4.2f) - Reason: %s" %(loanid, bidmoney, mymoney, reason))
                                ppdloan.score = bidmoney
                                if NOBID == True:
                                    ppdloan.bid = 0 # override to 0
                                    mybiddao.insert_bid_record(loanid, now, 0, ppduserid, "NoBidMode:" + reason)
                                else:
                                    # Actually bid for it
                                    actual_bid_money = autobid.bid(spider.opener, loanid, ppdloan.maturity, bidmoney, reason)
                                    if actual_bid_money > 0:
                                        mybiddao.insert_bid_record(loanid, now, actual_bid_money, ppduserid, reason)
                                        logging.info("DONE!!! Bid %d for loanid %d!!!" % (actual_bid_money, loanid))
                                    else:
                                        logging.warn("Bid Failed. No Worries. let's keep going!")
                                    ppdloan.bid = actual_bid_money
                                
                            else:
                                logging.info("NoBid for %d: %s" %(loanid, reason))
    
                            # Write to MYSQL
                            loanids_in_memory.append(loanid)
                            loandao.insert(ppdloan)
                            userdao.insert_if_not_exists(ppduser)
                            if ppdloan.loanrate < 10: # No need to check more Loans as we've sorted the pages
                                sleep(random.randint(1,4))
                                break
                            else:
                                sleep(random.randint(1,6))
                    sleep(random.randint(1,5))
            except Exception, e:
                error_count += 1
                logging.error("Un-Caught Error!!! Continue with next round - Please do Check IT!! %r" %(e))
                traceback.print_exc()
                sleep(random.randint(6,12))
        rd += 1
        if (rd % 20 == 0):
            rdint = random.randint(20,60) # Sleep more time on every 20 round.
        elif (rd % 100 == 0):
            rdint = random.randint(70,200)
        elif (rd % 400 == 0):
            rdint = random.randint(200,800)
        else:
            rdint = random.randint(6,20)
        logging.info(" ****** Done Round %d ****** Sleep for %d seconds before next run." % (rd, rdint))
        sleep(rdint)
    # This will never run - need an elegant way to exit the program.
    ppddao.disconnect()