#-*- coding:utf-8 -*-
'''
Created on 2016 Mar 6th. 
Modified on Mar 8th.

@author: Administrator
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
import logging
import os
from datetime import date
from datetime import datetime
from time import sleep
import random
import traceback
from sys import argv
from spider import PPDLogin
import gzip
from StringIO import StringIO
from util.PPBaoUtil import PPBaoUtil
import urllib
import urllib2

def init_logging(ppdid):
    today = date.today().isoformat()
    logfile = "D:/ppdai/Test.%s.%s.log" % (ppdid, today)
    i = 1
    while os.path.exists(logfile):
        logfile = "D:/ppdai/Test.%s.%s.%d.log" % (ppdid, today, i)
        i += 1
    logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename=logfile,
                filemode='a')
    #����һ��StreamHandler����INFO������ߵ���־��Ϣ��ӡ����׼���󣬲�������ӵ���ǰ����־�������#
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s %(levelname)-4s %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)

def step0_open_loan(opener, loanid):
    loanurl = "http://invest.ppdai.com/loan/info?id=%d" % (loanid)
    headers = {"Accept-Encoding": "gzip, deflate, sdch",
               "Host": "invest.ppdai.com",
               'Accept':'*/*',
               'Cache-Control':'max-age=0',
               "Accept-Language": "zh-CN,zh;q=0.8,en;q=0.6",           
               "Upgrade-Insecure-Requests": "1",
               "Referer": "http://invest.ppdai.com/loan/list_riskmiddle_s5_p2?Rate=0",
               "Connection": "keep-alive"
    }
    opener = PPBaoUtil.add_headers(opener, headers)
    response = opener.open(loanurl, None, 10)
    html = PPBaoUtil.get_html_from_response(response)
    logging.debug("Get Response: %s", html)
    response_headers = response.info()
    for head in response_headers:
        logging.info("%s:%s" % (head, response_headers[head]))
    return loanurl
    
def step1_open_actionlog(opener, loanid):
    url = "http://invest.ppdai.com/common/actionlog"
    headers = {"Origin":"http://invest.ppdai.com",
               "Accept-Encoding": "gzip, deflate",
               "Host": "invest.ppdai.com",
               "Accept-Language": "zh-CN,zh;q=0.8,en;q=0.6",
               "Content-Type": "application/x-www-form-urlencoded",
               "Accept": "*/*",
               "Referer": "http://invest.ppdai.com/loan/info?id=%d" % (loanid),
               "X-Requested-With": "XMLHttpRequest",
               "Connection": "keep-alive",
               "Content-Length": "109"
    }
    post_data = {"useraction":"VisitRecord",
                 "functionname":'%E6%95%A3%E6%A0%87%E6%8A%95%E6%A0%87',
                 "remark":'%E6%95%A3%E6%A0%87'+"%d+++++" %(loanid)
    }
    opener = PPBaoUtil.add_headers(opener, headers)
    upost_data = urllib.urlencode(post_data)
    response = opener.open(url, upost_data, 10)
    html = PPBaoUtil.get_html_from_response(response)
    logging.debug("Get Response: %s", html)
    response_headers = response.info()
    for head in response_headers:
        logging.info("%s:%s" % (head, response_headers[head]))

def step2_get_bidloan(opener, maturity, loanid, money):
    loanurl = "http://invest.ppdai.com/bid/info?source=2&listingId=%d" % (loanid) \
            + '%20%20%20%20&title=&date=' + "%d" %(maturity) + '%20%20%20%20&UrlReferrer=1&money=' + "%d" %(money)
    headers = {"Accept-Encoding": "gzip, deflate, sdch",
               "Host": "invest.ppdai.com",
               "Accept-Language": "zh-CN,zh;q=0.8,en;q=0.6",           
               "Upgrade-Insecure-Requests": "1",
               "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
               "Referer": "http://invest.ppdai.com/loan/info?id=%d" % (loanid),
               "Connection": "keep-alive"
    }
    opener = PPBaoUtil.add_headers(opener, headers)
    response = opener.open(loanurl, None, 10)
    html = PPBaoUtil.get_html_from_response(response)
    logging.debug("Get Response: %s", html)
    response_headers = response.info()
    for head in response_headers:
        logging.info("%s:%s" % (head, response_headers[head]))
    return loanurl

def step3_bid(opener, maturity, loanid, money):
    loanurl = "http://invest.ppdai.com/bid/info?source=2&listingId=%d" % (loanid) + '%20%20%20%20&title=&date=' + "%d" %(maturity) + '%20%20%20%20&UrlReferrer=1&money=' + "%d" %(money)
    bidurl  = "http://invest.ppdai.com/Bid/Bid"
    bid_info = {"Reason":'', "Amount":money, "ListingId":loanid, "UrlReferrer":"1", "SubListType":'0'}
    headers = {"Origin": "http://invest.ppdai.com",
               "Accept-Encoding": "gzip, deflate",
               "Host": "invest.ppdai.com",
               "Accept-Language": "zh-CN,zh;q=0.8,en;q=0.6",
               "Content-Type": "application/x-www-form-urlencoded",
               "Accept": "*/*",
               "Referer": loanurl,
               "X-Requested-With": "XMLHttpRequest",
               "Connection": "keep-alive",
               "Content-Length": "63"
    }
    upost_data = urllib.urlencode(bid_info)
    opener = PPBaoUtil.add_headers(opener, headers)
    response = opener.open(bidurl, upost_data, 10)
    html = PPBaoUtil.get_html_from_response(response)
    logging.info("Get Response: %s", html)
    response_headers = response.info()
    for head in response_headers:
        logging.info("%s:%s" % (head, response_headers[head]))
        
def step4_open_loan(opener, maturity, loanid, money):
    loanurl = "http://invest.ppdai.com/loan/info?id=%d" % (loanid)
    refer_url = "http://invest.ppdai.com/bid/info?source=2&listingId=%d" % (loanid) + '%20%20%20%20&title=&date=' + "%d" %(maturity) + '%20%20%20%20&UrlReferrer=1&money=' + "%d" %(money)
    headers = {"Accept-Encoding": "gzip, deflate, sdch",
               "Host": "invest.ppdai.com",
               "Accept-Language": "zh-CN,zh;q=0.8,en;q=0.6",           
               "Upgrade-Insecure-Requests": "1",
               "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
               "Referer": refer_url,
               "Connection": "keep-alive"
    }
    opener = PPBaoUtil.add_headers(opener, headers)
    response = opener.open(loanurl, None, 10)
    html = PPBaoUtil.get_html_from_response(response)
    logging.debug("Get Response: %s", html)
    response_headers = response.info()
    for head in response_headers:
        logging.info("%s:%s" % (head, response_headers[head]))
    return loanurl
    
def stepx_status(opener, loanurl):
    url = "http://ac.ppdai.com/status?v=2014"
    headers = {"Accept-Encoding": "gzip, deflate, sdch",
               "Host": "invest.ppdai.com",
               "Accept-Language": "zh-CN,zh;q=0.8,en;q=0.6",
               "Upgrade-Insecure-Requests": "1",
               "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
               "Referer": loanurl,
               "Connection": "keep-alive"
    }
    
'''    
if __name__ == '__main__':
    
    ppdloginid = '18616856236'
    ppdpasswd  = 'Oyxq270'
    init_logging(ppdloginid)
    (opener,cookie) = Login2.init_opener('D:/ppPPDLoginst_cookie.txt')
    Login2.before_login(ppdloPPDLoginppdpasswd, opener)
    Login2.print_cookie(cookiPPDLogin  logging.info("LOGIN!!")
    Login2.login(ppdloginid,pPPDLoginwd, opener)
    Login2.print_cookie(cookiPPDLogin  logging.info("Open Lend Page!!")
    Login2.open_lend(opener)PPDLoginogin2.print_cookie(cookiPPDLogin  sleep(3)
    loanid = 9666807
    maturity = 12
    bidmoney = 50
    step0_open_loan(opener, loanid)
    step1_open_actionlog(opener, loanid)
    step2_get_bidloan(opener, maturity, loanid, bidmoney)
    Login2.print_cookie(cookiPPDLogin  sleep(1)
    logging.info("Step 3: Bid!!")
    step3_bid(opener, maturity,loanid, bidmoney)
    logging.info("Step 4: Open Loan Page!!")
    Login2.print_cookie(cookiPPDLogin  sleep(1)
    logging.info("Open Loan to check!")
    step4_open_loan(opener, maturity ,loanid, bidmoney)
    Login2.print_cookie(cookiPPDLogin  sleep(1)
    # Verify if I can still open other loans
    loanids = (9658513, 9655930)
    for loanid in loanids:
        logging.info("Opening Loan %d" % (loanid))
        step0_open_loan(opener, loanid)
        Login2.print_cookie(cookiPPDLogin      sleep(5)
    
    logging.info("SUCCESS!!!")
    '''  
    
'''
    ppdloginid = '18616856236'
    ppdpasswd  = 'Oyxq270'
    init_logging(ppdloginid)
    spider = PPDSpider(ppdloginid)
    parser = PPDHtmlParser()
   
    (opener, ppduserid) = spider.login(ppdloginid, ppdpasswd) 
    if opener == None:
        logging.error("Error: Not able to login to PPDAI(www.ppdai.com). Exit...")
        exit(3)
    if (ppduserid == None):
        logging.error("Error: Not able to get PPDAI Username or is not consistent with that in DB! Exit...")
        exit(4)
    
    spider.print_cookie()
    sleep(random.randint(1,5))
    logging.info("open account/lend")
    html = spider.open_page('http://invest.ppdai.com/account/lend', 'https://ac.ppdai.com/User/Login?message=&Redirect=')
    spider.print_cookie()
    logging.info("End of Cookies!!!")
    logging.info("%s", html)
'''
    
    