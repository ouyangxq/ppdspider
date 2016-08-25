#-*- coding: utf-8 -*-
'''
Created on 20160221

@author: Administrator
'''
import urllib
import re
import logging
from time import sleep
from util.PPBaoUtil import PPBaoUtil
import random
import traceback

class AutoBid(object):
    '''
    Bid for good loans
    '''
    bid_response_pattern = re.compile('.*"ListingId":.*?"UrlReferrer":"1","Money":\d+,"Amount":(\d+).*Message":"投标成功","', re.S)
    actual_bid_pattern = re.compile("已投 &#165;(\d+), 占 ")
    pattern_current_progress = re.compile('<span id="process" style="width:\s+(\S+?);"></span>')
    pattern_myaccount_left = re.compile('账户余额：\s+<em id="accountTotal">&#165;(\S+?)</em>',re.S)
    
    def __init__(self):
        '''
        Constructor
        '''
        pass    
               
    def step0_open_loan(self, opener, loanid):
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
        #logging.debug("Get Response: %s", html)
        response_headers = response.info()
        for head in response_headers:
            logging.debug("%s:%s" % (head, response_headers[head]))
        return loanurl
        
    def step1_open_actionlog(self, opener, loanid):
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
        #response_headers = response.info()
        #for head in response_headers:
        #    logging.info("%s:%s" % (head, response_headers[head]))
    
    def step2_get_bidloan(self, opener, maturity, loanid, money):
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
        #logging.debug("Get Response: %s", html)
        response_headers = response.info()
        #for head in response_headers:
        #    logging.info("%s:%s" % (head, response_headers[head]))
        return loanurl
    
    def step3_bid(self, opener, maturity, loanid, money):
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
        response = opener.open(bidurl, upost_data, 15)
        html = PPBaoUtil.get_html_from_response(response)
        #logging.debug("Get Response: %s", html)
        response_headers = response.info()
        for head in response_headers:
            logging.debug("%s:%s" % (head, response_headers[head]))
            
    def step4_check_bid_result(self, opener, maturity, loanid, money):
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
        response = opener.open(loanurl, None, 15)
        html = PPBaoUtil.get_html_from_response(response)
        #logging.debug("Get Response: %s", html)
        #response_headers = response.info()
        #for head in response_headers:
        #    logging.debug("%s:%s" % (head, response_headers[head]))
        m = re.search(self.actual_bid_pattern, html)
        if (m is not None):
            logging.info("Bid %s successfully!!!" % (m.group(1)))
            actual_bid = int(m.group(1))
        else:
            progress_m = re.search(self.pattern_current_progress, html)
            if progress_m is not None and progress_m.group(1) == '100%':
                logging.warn("Bid Failed: It's Already 100% completed! We're too late!")
            else: 
                logging.warn("Not match ActualBid Pattern. Most likely Bid is not successful! Do Check it")
            actual_bid = -1
        # -1 means not parsed from html
        mymoney = -1
        ac = re.search(self.pattern_myaccount_left, html)
        if (ac is not None):
            mymoney = float(ac.group(1).replace(',',''))
            #logging.info("My Account Left: %4.2f" % (mymoney))
        return (actual_bid, mymoney)
    
    def bid(self, opener, loanid, maturity, bidmoney):
        try: 
            self.step0_open_loan(opener, loanid)
            self.step1_open_actionlog(opener, loanid)
            self.step2_get_bidloan(opener, maturity, loanid, bidmoney)
            sleep(random.randint(1,2))
            logging.info("Step 3: Bid!!")
            self.step3_bid(opener, maturity,loanid, bidmoney)
            logging.info("Step 4: Open Loan Page!!")
        except Exception, e:
            logging.error("Failed to Bid %d with money(%d). Error: %r" %(loanid, bidmoney, e))
            traceback.print_exc()
            return (-1, -1)
        # 20160511: Split into 2 step as if it only failed in 2nd step, bid is most likely successful
        try:
            sleep(random.randint(1,4))
            #logging.info("Open Loan to check!")
            return self.step4_check_bid_result(opener, maturity ,loanid, bidmoney)
        except Exception, e:
            logging.error("Error on Checking the Bid Result for %d with money(%d). Reason: %r" %(loanid, bidmoney, e))
            return (bidmoney, -1)
        