#!python
#-*- coding:utf-8 -*-

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
import logging
import os
from datetime import date
from datetime import datetime
from time import sleep
import random
import traceback
from sys import argv


def init_logging(ppdid):
    today = date.today().isoformat()
    logfile = "D:/ppdai/ppbao.%s.%s.log" % (ppdid, today)
    i = 1
    while os.path.exists(logfile):
        logfile = "D:/ppdai/ppbao.%s.%s.%d.log" % (ppdid, today, i)
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


# MAIN
if __name__ == '__main__':
    '''
    1. Login 
    2. Get List of Loans
    3. For each Loan:
        If it's a New Loan(In Memory/DB Check), apply the strategy to see if it's good enough for bid
        If it's good for bid, 
            try to bid it
            record down into MYSQL mybid 
        Record the Loan information and User information into MYSQL
    4. Sleep an round time and continue with step 2
    '''
 
    if (len(argv) == 1):
        ppdloginid = '18616856236'
    elif (len(argv) == 2):
        me,ppdloginid = argv
    else:
        print "Error: More than 1 argument is provided!"
        print "Usage: python PPBao.py <ppdai_user_id>"
        exit (-1)
    # Initialize
    init_logging(ppdloginid)
    logging.info("Entering into PPBao System. Developed By Xiaoqi Ouyang.")
    logging.info("All Rights Reserved@2016-2017")

    # Init DB Modules
    ppddao = PPDDAO({'host':'localhost','username':'xiaoqi','password':'XiaoqiDB.1','database':'ppdai'})
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
        
    # Keep loain is in memory for expire_time, then read it from DB.
    loanids_in_memory = loandao.get_last_2_days_loanids()
    logging.debug(loanids_in_memory)

    # Login to PPDAI!
    spider = PPDSpider(ppdloginid)
    parser = PPDHtmlParser()
   
    (opener, ppduserid) = spider.login(ppdloginid, ppdpasswd) 
    if opener == None:
        logging.error("Error: Not able to login to PPDAI(www.ppdai.com). Exit...")
        exit(3)
    if (ppduserid == None or ppduserid != ppduserid_db):
        logging.error("Error: Not able to get PPDAI Username or is not consistent with that in DB! Exit...")
        exit(4)
    # Initialize Strategy & AutoBid Components
    strategy = BidStrategy(university_to_rank)
    autobid  = AutoBid()

    ''' We're ready to play the game to have FUN now!!! ''' 
    sleep(random.randint(2,6))
    rd  = 0  # Round
    error_count = 0 # This record down how many errors we have during the run.
    while (1):
        ''' 20160304: Add AutoLogin after 20 Errors '''
        sleep(random.randint(30,60))
        if error_count >= 20:
            logging.warn("PPBAO: We've encountered %d errors. We'll re-login to continue!" % (error_count))
            (opener, ppduserid) = spider.login(ppdloginid, ppdpasswd) 
            if opener == None:
                logging.error("Not able to login after %d Errors. Check it! Exit..." % (error_count))
                exit(3)
            error_count = 0
            sleep(random.randint(5,20))
        for risk in [spider.risksafe, spider.riskmiddle]:
            try: 
                first_page_url = spider.build_loanpage_url(risk, 1)
                count, pages,firstpage_loanurl_list = spider.get_pages(first_page_url)
                if count == 0:
                    logging.info("No Loan of risktype %s is available. Next..." % risk)
                    sleep(random.randint(1,5))
                    continue;
                else:
                    logging.info("Count of Loans for %s: %d" % (risk, count))
                    sleep(random.randint(1,3))
                # Reset Pages to not get too many unuseful DATA
                if ((risk == spider.risksafe or risk == spider.riskhigh) and pages > 2):
                    ''' for riskhigh and safe, only query the first 2 pages as we already sorted them by Rate'''
                    pages = 2
                #elif pages > 16:
                #    ''' for riskmiddle, only query the first 7 pages as we already sort them by PPD Rate'''
                #    pages = 16
                ''' Notice range (1,2) will only returns 1 '''
                for index in range(1,pages):
                    if (index > 1): 
                        pageurl = spider.build_loanpage_url(risk, index)
                        logging.debug("Open page url: %s" % (pageurl))
                        loanurls = spider.get_loan_list_urls(pageurl)
                        if (loanurls is None):
                            error_count += 1
                            logging.error("Can't get loanurls. Ignore and Continue. Check it Later!")
                            break
                    else:
                        pageurl = spider.build_loanpage_url(risk, 1)
                        loanurls = firstpage_loanurl_list
                    for loanurl in loanurls: 
                        loanid = spider.get_loanid_from_url(loanurl)
                        if loanid is None:
                            error_count += 1
                            logging.error("Not able to get loanid from %s" % (loanurl))
                            continue
                        
                        if (loanid in loanids_in_memory):
                            logging.debug("Loanid %d is already in DB. Ignore." % (loanid))
                            continue
                        else:
                            logging.info("New Loan list: %d" % (loanid))
    
                            html = spider.open_page(loanurl, pageurl)
                            if (html is None):
                                error_count += 1
                                logging.error("Can't open %s - Please Check it. Ignore and Continue" %(loanurl))
                                continue
                            loanids_in_memory.append(loanid)
                            now = datetime.now() # Record Down the current datetime
                            ppdloan, ppduser, mymoney = parser.parse_loandetail_html(loanid, now, html)
                            if (ppdloan == None):
                                error_count += 1
                                logging.error("Not able to parse the HTML to get ppdloan. DO CHECK IT. Ignore and Continue for now!")
                                continue;
                            # AutoBid
                            ifbid,bidmoney, reason = strategy.check(ppdloan)
                            if ((bidmoney is not None) and (mymoney < bidmoney)):
                                logging.warn("NOT ENOUGH MONEY in My Account to Bid. WIll Run without BID!!!")
                            elif ifbid == True:
                                logging.warn("ATTENTION: Bid Loanid %d with Money %d (MyAccount Left:%4.2f) - Reason: %s" %(loanid, bidmoney, mymoney, reason))
                                # Actually bid for it
                                actual_bid_money = autobid.bid(spider.opener, loanid, bidmoney, reason)
                                if actual_bid_money > 0:
                                    mybiddao.insert_bid_record(loanid, now, actual_bid_money, ppduserid, reason)
                                    logging.info("DONE!!! Bid %d for loanid %d!!!" % (actual_bid_money, loanid))
                                else:
                                    logging.warn("Possibly FAILED. Check the loan page to see if the bid is succcessful! Check the Page Pattern again!")
                                
                                sleep(random.randint(2,6))
                                (opener, ppduserid) = spider.login(ppdloginid, ppdpasswd) 
                                if opener == None:
                                    logging.error("Not able to login after AutoBid. Check it! Exit...")
                                    exit(3)
                                "RESET error_count if we bid it successfully"
                                error_count = 0
                            else:
                                logging.info("BidStragegy Check: FALSE for %d. Reason: %s" %(loanid, reason))
    
                            # Write to MYSQL
                            loandao.insert(ppdloan)
                            userdao.insert_if_not_exists(ppduser)
                            if ppdloan.loanrate < 10:
                                break
                            else:
                                sleep(random.randint(2,5))
                    sleep(random.randint(3,5))
            except Exception, e:
                error_count += 1
                logging.error("Un-Caught Error!!!Check IT!! %r", e)
                traceback.print_exc()
                #logging.info("Sleep 300 seconds before proceeding with next action(Login again and recheck!");
                #sleep(300)
                #spider.login(ppdloginid,ppdpasswd)
                sleep(random.randint(5,10))
        rd += 1
        if (rd % 20 == 0):
            rdint = random.randint(30,60) # Sleep more time on every 20 round.
        elif (rd % 100 == 0):
            rdint = random.randint(70,180)
        elif (rd % 400 == 0):
            rdint = random.randint(150,600)
        else:
            rdint = random.randint(8,30)
        logging.info(" ****** Done Round %d ****** Sleep for %d seconds before next run." % (rd, rdint))
        sleep(rdint)
    # This will never run - need an elegant way to exit the program.
    ppddao.disconnect()