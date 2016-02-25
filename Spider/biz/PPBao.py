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
from ds.PPDLoan import PPDLoan
from ds.PPDUser import PPDUser
from dao.PPDDAO import PPDDAO
from dao.PPDLoanDAO import PPDLoanDAO
from dao.PPDUserDAO import PPDUserDAO
from dao.MyBidDAO import MyBidDAO
from spider.PPDSpider import PPDSpider
from biz.AutoBid import AutoBid
import logging
import os
from datetime import date
from time import sleep
import random

def init_logging(today):
    logfile = "D:/ppdai/ppbao.%s.log" % (today)
    i = 1
    while os.path.exists(logfile):
        logfile = "D:/ppdai/ppbao.%s.%d.log" % (today, i)
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
    # Initialize
    today   = date.today()
    init_logging(today)
    logging.info("Entering into PPBao System. Developed By Xiaoqi Ouyang.")
    spider = PPDSpider()
    parser = PPDHtmlParser()
    ppddao = PPDDAO({'host':'localhost','username':'xiaoqi','password':'XiaoqiDB.1','database':'ppdai'})
    dbok   = ppddao.connect()
    if dbok == False:
        logging.error("Not able to connect to MySQL! Please Fix it. Exiting now")
        exit (1)
    loandao = PPDLoanDAO(ppddao)
    userdao = PPDUserDAO(ppddao)
    mybiddao = MyBidDAO(ppddao)
    strategy = BidStrategy()
    autobid  = AutoBid()

    # Login 
    opener = spider.login('18616856236', 'Oyxq270') 
    if opener == None:
        logging.error("Not able to login. Exit...")
        exit(2)
    
    # Keep loain is in memory for expire_time, then read it from DB.
    loanids_in_memory = loandao.get_loanids_by_date(today)
    logging.debug(loanids_in_memory)
    # expire_time = 300 # not in use for now. 
    sleep(5)
    rd  = 0  # Round
    while (1):
        for risk in spider.risktype:
            try: 
                first_page_url = spider.build_loanpage_url(risk, 1)
                count, pages = spider.get_pages(first_page_url)
                if count == 0:
                    logging.info("No Loan of risktype %s is available. Next..." % risk)
                    continue;
                else:
                    logging.info("Count of Loans for %s: %d" % (risk, count))
                for index in range(1,pages):
                    pageurl = spider.build_loanpage_url(risk, index)
                    logging.debug("Open page url: %s" % (pageurl))
                    loanurls = spider.get_loan_list_urls(pageurl)
                    if (loanurls is None):
                        logging.error("Can't get loanurls. Ignore and Continue. Check it Later!")
                        continue
                    for loanurl in loanurls: 
                        loanid = spider.get_loanid_from_url(loanurl)
                        if (loanid in loanids_in_memory):
                            logging.debug("Loanid %d is already in DB. Ignore." % (loanid))
                            continue
                        else:
                            logging.info("New Loan list: %d" % (loanid))
    
                            html = spider.open_page(loanurl)
                            if (html is None):
                                logging.error("Can't open %s - Please Check it. Ignore and Continue" %(loanurl))
                                continue
                            loanids_in_memory.append(loanid)
                            ppdloan, ppduser, mymoney = parser.parse_loandetail_html(loanid, today, html)
                            if (ppdloan == None):
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
                                    mybiddao.insert_bid_record(loanid, today, actual_bid_money, reason)
                                    logging.info("DONE!!! Bid %d for loanid %d!!!" % (actual_bid_money, loanid))
                                    sleep(random.randint(1,4))
                                else:
                                    logging.info("Possibly FAILED. Check the loan page to see if the bid is succcessful! Check the Page Pattern again!")
                                
                                opener = spider.login('18616856236', 'Oyxq270') 
                                if opener == None:
                                    logging.error("Not able to login after AutoBid. Check it! Exit...")
                                    exit(3)
                            else:
                                logging.info("BidStragegy Check Result is FALSE for %d. Reason: %s" %(loanid, reason))
    
                            # Write to MYSQL
                            loandao.insert(ppdloan)
                            userdao.insert_if_not_exists(ppduser)
                            sleep(random.randint(0,2))
            except Exception, e:
                logging.error("Unhandled Error!!!!!!!!!!!!Check IT!! %r", e)
                sleep(1)
        rd += 1
        rdint = random.randint(5,30)
        logging.info("Done Round %d. Sleep for %d seconds before next run." % (rd, rdint))
        sleep(rdint)
    # This will never run - need an elegant way to exit the program.
    ppddao.disconnect()