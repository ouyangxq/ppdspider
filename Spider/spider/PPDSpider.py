#!python
#-*- coding:utf-8 -*-
'''
@author: Xiaoqi Ouyang
Date: Feb 12, 2016
Description: A Network Spider to get PPDAI loan information so as to decide which list to invest.
'''

import urllib
import urllib2
import re
import cookielib
from datetime import date
from time import sleep
from LoanInfo import LoanInfo
from LoanHistory import LoanHistory
import logging
from urllib2 import HTTPError


class PPDSpider(object):

    login_url = None
    safe_loanlist_url = None
    medium_risk_loanlist_url = None
    high_risk_loanlist_url = None
    cookie_file = "ppdai_cookie.txt" # File to store cookies to be used for all connections
    opener = None
    risktype = ['safe', 'riskmiddle', 'riskhigh']
    safe_page_url = 'http://invest.ppdai.com/loan/list_safe_s0_p5?Rate=0'
    highrisk_page_url = 'http://invest.ppdai.com/loan/list_riskhigh_s0_p2?Rate=0'
    mediumrisk_page_url = 'http://invest.ppdai.com/loan/list_riskmiddle_s0_p2?Rate=0'
    loanid_url_pattern = re.compile('.*info\?id=(\d+)')
    
    def __init__(self):
        self.login_url = "https://ac.ppdai.com/User/Login?redirect="
        self.cookie_file = "ppdai_cookie.txt" # File to store cookies to be used for all connections
    
    def login(self, username, password):
        login_info = {"UserName":username, "Password":password}
        login_data = urllib.urlencode(login_info)
        cookie = cookielib.MozillaCookieJar(self.cookie_file)
        handler = urllib2.HTTPCookieProcessor(cookie)
        opener  = urllib2.build_opener(handler)
        #urllib2.install_opener(opener)
        opener.addheaders = [('User-agent', 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.73 Safari/537.36')]
        logging.info("Logging to www.ppdai.com...")
        try:
            response = opener.open(self.login_url, login_data)
            html = response.read()
            #response.close()
            logging.info("Get Response: %s" %(html))
            logging.info("Successfully Logged into PPDAI!")
            cookie.save(ignore_discard=True, ignore_expires=True)
            for item in cookie:
                logging.debug("Name = " + item.name + " - Value=" + item.value)
            self.opener = opener
            return opener
        except urllib2.URLError, e:
            logging.error("URLError: Not Able to Login to PPDAI! - Error: %r" % (e))
            return None
        except urllib2.HTTPError, e:
            logging.error("HTTPError: Not Able to login to PPDAI!- Error: %d" % (e.code))
            return None
            
    
    # Use this function to check what are the URLs
    def build_loanpage_url(self, risktype, pageindex):
        url = "http://invest.ppdai.com/loan/list_%s_s0_p%d" % (risktype, pageindex)
        return url
    
    
    def get_loan_list_urls (self, loan_url):
        " This function is to analsysis the Loan List page and return a list of links point to the detailed loan info page"
        try: 
            response = self.opener.open(loan_url)
            html_str = response.read() 
            response.close()
            
            pattern  = re.compile('<div class="w230 listtitle">.*?<a class="title ell" target="_blank" href="(.*?)" title="(.*?)">.*?</a>', re.S)
            items    = re.findall(pattern, html_str)
            result_list = []
            for item in items:
                result_list.append(item[0])
            return result_list
        except HTTPError, e:
            logging.error("Failed to open page: %s - Reason: %r" %( loan_url, e))
            return None

    def open_page(self,url):
        '''
        Try to Open page and return the HTML String for further analysis
        '''
        try: 
            response = self.opener.open(url)
            html_str = response.read()
            response.close()
            return html_str
        except urllib2.URLError, e:
            logging.error("Not able to open %s, %r" % (url, e))
            return None
    
    # Get Number of Pages of loans
    def get_pages(self, loan_url):
        try:
            response = self.opener.open(loan_url)
            html_str = response.read()
            response.close()
            loan_count_pattern = re.compile('<span class="fr">共找到 <em class="cfe8e01">(\d+)</em> 个标的</span>', re.S)
            m = re.search(loan_count_pattern, html_str)
            loan_count = -1
            if m is not None:
                loan_count = int(m.group(1))
                if (loan_count == 0):
                    print "0 Loans detected"
                    return (0, 0)
                elif (loan_count <= 10):
                    print "%d loans detected" % (loan_count)
                    return (loan_count, 1)
                else:
                    pass # Continue to check the pages
            
            page_pattern = re.compile("<div class='pager'><span class='pagerstatus'>共(\d+)页", re.S)
            m =  re.search(page_pattern, html_str)
            if m is not None:
                return (loan_count, int(m.group(1)))
            else:
                print "Not Match the Page Pattern."
                return (loan_count, -1)
        except HTTPError, e:
            logging.error("Failed to get pages. Ignore and Continue,but do Check it: HTTPError: %r" %(e))
            return (0,0)
    
    def get_loanid_from_url(self, url):
        m = re.match(self.loanid_url_pattern, url)
        if m is not None:
            return int(m.group(1))
        else:
            return None
        
            
# main
if __name__ == '__main__':
    today = date.today()
    cnt = 0
    spider = PPDSpider()
    opener = spider.login('18616856236', 'Oyxq270') 
    loanids_in_memory = []
    sround = 0
    rf = open("ppd_result.%s.txt" % (today), 'a')
    rf.write('ID,' + LoanInfo.get_header_str(None) + "\n")
    rf.close()
    while (1):
        sround += 1
        print "*** Round %d ***" % (sround)
        for risk in spider.risktype:
            #for risk in ['riskmiddle']:
            rf = open("ppd_result.%s.txt" % (today), 'a')
            first_page_url = spider.build_loanpage_url(risk, 1)
            count, pages = spider.get_pages(first_page_url)
            url_pattern = re.compile('.*info\?id=(\d+)')
            for index in range(1,pages):
                pageurl = spider.build_loanpage_url(risk, index)
                loanurls = spider.get_loan_list_urls(pageurl)
                for loanurl in loanurls: 
                    m = re.search(url_pattern, loanurl)
                    loanid = 0
                    if (m is not None):
                        loanid = int(m.group(1))
                    if (loanid in loanids_in_memory):
                        continue
                    else:
                        loanids_in_memory.append(loanid)
                        print "New Loan list: %d" % (loanid),
                        cnt += 1
                        rf.write("%d," % (loanid))
                        loan = spider.get_loan_details(loanurl)
                        print loan.to_str()
                        rf.write(loan.to_str() + "\n")
                        #sleep(1)
            rf.close()
            sleep(60)
    print "Loan Count: %d" % (cnt)
    print "Enjoy! Good Job!"