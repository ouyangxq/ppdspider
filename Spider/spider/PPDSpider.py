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
    
    risksafe = 'safe'
    riskmiddle = 'riskmiddle'
    riskhigh   = 'riskhigh'
    risktype = [risksafe, riskmiddle, riskhigh]
    
    safe_page_url = 'http://invest.ppdai.com/loan/list_safe_s0_p5?Rate=0'
    highrisk_page_url = 'http://invest.ppdai.com/loan/list_riskhigh_s5_p2?Rate=0'
    mediumrisk_page_url = 'http://invest.ppdai.com/loan/list_riskmiddle_s0_p2?Rate=0'
    loanid_url_pattern = re.compile('.*info\?id=(\d+)')
    loanid_rul_pattern2 = re.compile("http://www.ppdai.com/list/(\d+)")
    loanid_pattern  = re.compile('<div class="w230 listtitle">.*?<a class="title ell" target="_blank" href="(.*?)" title="(.*?)">.*?</a>', re.S)
    loan_count_pattern = re.compile('<span class="fr">共找到 <em class="cfe8e01">(\d+)</em> 个标的</span>', re.S)
    page_pattern = re.compile("<div class='pager'><span class='pagerstatus'>共(\d+)页", re.S)
    
    def __init__(self,loginid):
        self.login_url = "https://ac.ppdai.com/User/Login?redirect="
        self.cookie_file = "ppdai_cookie.%s.txt" %(loginid) # File to store cookies to be used for all connections
    
    def login(self, username, password):
        login_info = {"UserName":username, "Password":password}
        login_data = urllib.urlencode(login_info)
        cookie = cookielib.MozillaCookieJar(self.cookie_file)
        handler = urllib2.HTTPCookieProcessor(cookie)
        opener  = urllib2.build_opener(handler)
        urllib2.install_opener(opener)
        opener.addheaders = [('User-agent', 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.73 Safari/537.36')]
        logging.info("Logging to www.ppdai.com...")
        try:
            opener.addheaders.append(('Host','ac.ppdai.com'))
            opener.addheaders.append(('Referer','https://ac.ppdai.com/User/Login?message=&Redirect='))
            opener.addheaders.append(('Accept','*/*'))
            opener.addheaders.append(('Connection','keep-alive'))
            response = opener.open(self.login_url, login_data)
            '''
            req = urllib2.Request(self.login_url,login_data)
            req.add_header('Origin', 'https://ac.ppdai.com')
            req.add_header('Accept-Encoding', 'gzip, deflate')
            req.add_header('Host', 'ac.ppdai.com')
            req.add_header('Accept-Language', 'zh-CN,zh;q=0.8,en;q=0.6')
            req.add_header('User-Agent','Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.73 Safari/537.36')
            req.add_header('Content-Type','application/x-www-form-urlencoded')
            req.add_header('Accept','*/*')
            req.add_header('Referer','https://ac.ppdai.com/User/Login?message=&Redirect=')
            req.add_header('X-Requested-With','XMLHttpRequest')
            req.add_header('Connection','keep-alive')
            # req.add_header('Content-Length','76')
            response = urllib2.urlopen(req)
            '''
            html = response.read()
            response.close()
            #response.close()
            logging.info("Get Response: %s" %(html))
            logging.info("Successfully Logged into PPDAI!")
            cookie.save(ignore_discard=True, ignore_expires=True)
            ppduserid = 'None'
            for item in cookie:
                logging.debug("Name = " + item.name + " - Value=" + item.value)
                if (item.name == 'ppd_uname'):
                    ppduserid = item.value
                    logging.info("PPD Username: %s" % (ppduserid))
            self.opener = opener
            return (opener,ppduserid)
        except urllib2.URLError, e:
            logging.error("URLError: Not Able to Login to PPDAI! - Error: %r" % (e))
            return None
        except urllib2.HTTPError, e:
            logging.error("HTTPError: Not Able to login to PPDAI!- Error: %d" % (e.code))
            return None
            
    
    # Use this function to check what are the URLs
    def build_loanpage_url(self, risktype, pageindex):
        if (risktype == self.risksafe):
            ''' sort by Interest Rate '''
            url = "http://invest.ppdai.com/loan/list_Safe_s3_p%d?monthgroup=&rate=0&didibid=&listingispay=" % (pageindex)
        elif risktype == self.riskmiddle:
            ''' Sort by PPDai Rate '''
            url = "http://invest.ppdai.com/loan/list_RiskMiddle_s5_p%d?monthgroup=&rate=0&didibid=&listingispay=" % (pageindex)
        else:
            url = "http://invest.ppdai.com/loan/list_RiskHigh_s5_p%d?monthgroup=&rate=0&didibid=&listingispay=" % (pageindex)
        return url
    
    
    def get_loan_list_urls (self, loan_url):
        " This function is to analsysis the Loan List page and return a list of links point to the detailed loan info page"
        try:
            ''' 
            req = urllib2.Request(loan_url)
            req.add_header('Origin', 'http://invest.ppdai.com')
            req.add_header('Accept-Encoding','gzip, deflate, sdch')
            req.add_header('Host','invest.ppdai.com')
            req.add_header('User-Agent','Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.73 Safari/537.36')
            req.add_header('Accept','*/*')
            req.add_header('Connection','keep-alive')
            req.add_header('Referer', 'http://invest.ppdai.com/loan/list_riskmiddle_s5_p1?Rate=0')
            req.add_header('Cache-Control','max-age=0')
            req.add_header('Accept-Language','zh-CN,zh;q=0.8,en;q=0.6')
            response = urllib2.urlopen(req,None,10)
            '''
            self.opener.addheaders.append(('Origin', 'http://invest.ppdai.com'))
            self.opener.addheaders.append(('Host','invest.ppdai.com'))
            self.opener.addheaders.append(('Referer','http://invest.ppdai.com/loan/list_riskmiddle_s5_p1?Rate=0'))
            self.opener.addheaders.append(('Accept','*/*'))
            self.opener.addheaders.append(('Connection','keep-alive'))
            self.opener.addheaders.append(('Cache-Control','max-age=0'))
            self.opener.addheaders.append(('User-Agent','Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.73 Safari/537.36'))
            response = self.opener.open(loan_url,None,7)
            
            html_str = response.read() 
            response.close()
            return self.get_loanurllist_from_page_html(html_str)
        except HTTPError, e:
            logging.error("Failed to open page: %s - Reason: %r" %( loan_url, e))
            return None

    def get_loanurllist_from_page_html(self, html_str):
        items    = re.findall(self.loanid_pattern, html_str)
        result_list = []
        for item in items:
            result_list.append(item[0])
        return result_list
        
    def open_page(self,url,referer_url):
        '''
        Try to Open page and return the HTML String for further analysis
        '''
        try:
            ''' 
            req = urllib2.Request(url)
            req.add_header('Origin', 'http://invest.ppdai.com')
            req.add_header('Accept-Encoding','gzip, deflate, sdch')
            req.add_header('Host','invest.ppdai.com')
            req.add_header('User-Agent','Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.73 Safari/537.36')
            req.add_header('Accept','*/*')
            req.add_header('Connection','keep-alive')
            req.add_header('Referer', referer_url)
            req.add_header('Cache-Control','max-age=0')
            req.add_header('Accept-Language','zh-CN,zh;q=0.8,en;q=0.6')
            response = urllib2.urlopen(req,None,10)
            '''
            self.opener.addheaders.append(('Origin', 'http://invest.ppdai.com'))
            self.opener.addheaders.append(('Host','invest.ppdai.com'))
            self.opener.addheaders.append(('Referer',referer_url))
            self.opener.addheaders.append(('Accept','*/*'))
            self.opener.addheaders.append(('Connection','keep-alive'))
            self.opener.addheaders.append(('Cache-Control','max-age=0'))
            self.opener.addheaders.append(('User-Agent','Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.73 Safari/537.36'))
            response = self.opener.open(url,None,5)
            html_str = response.read()
            response.close()
            return html_str
        except urllib2.URLError, e:
            logging.error("Not able to open %s, %r" % (url, e))
            return None
    
    # Get Number of Pages of loans
    def get_pages(self, loan_url):
        try:
            '''
            req = urllib2.Request(loan_url)
            req.add_header('Accept-Encoding','gzip, deflate, sdch')
            req.add_header('Accept-Language','zh-CN,zh;q=0.8,en;q=0.6')
            req.add_header('Host','invest.ppdai.com')
            req.add_header('User-Agent','Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.73 Safari/537.36')
            req.add_header('Accept','text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8')
            req.add_header('Connection','keep-alive')
            req.add_header('Referer', 'http://invest.ppdai.com/loan/list_riskmiddle_s5_p1?Rate=0')
            req.add_header('Cache-Control','max-age=0')
            response = urllib2.urlopen(req,None,20)
            '''
            self.opener.addheaders.append(('Host','invest.ppdai.com'))
            self.opener.addheaders.append(('Referer','http://invest.ppdai.com/loan/list_riskmiddle_s5_p1?Rate=0'))
            self.opener.addheaders.append(('Accept','text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'))
            self.opener.addheaders.append(('Connection','keep-alive'))
            self.opener.addheaders.append(('Cache-Control','max-age=0'))
            self.opener.addheaders.append(('User-Agent','Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.73 Safari/537.36'))
            response = self.opener.open(loan_url,None,10)
            html_str = response.read()
            response.close()
            
            m = re.search(self.loan_count_pattern, html_str)
            loan_count = -1
            loanurl_list = []
            if m is not None:
                loanurl_list = self.get_loanurllist_from_page_html(html_str)
                loan_count = int(m.group(1))
                if (loan_count == 0):
                    logging.info("0 Loans detected")
                    return (0, 0,loanurl_list)
                elif (loan_count <= 10):
                    logging.debug("%d loans detected" % (loan_count))
                    return (loan_count, 1,loanurl_list)
                else:
                    pass # Continue to check the pages
            
            m =  re.search(self.page_pattern, html_str)
            if m is not None:
                return (loan_count, int(m.group(1)),loanurl_list)
            else:
                logging.debug(html_str)
                logging.error( "Not Match the Page Pattern.")
                return (loan_count, -1,loanurl_list)
        except HTTPError, e:
            logging.error("Failed to get pages. Ignore and Continue,but do Check it: HTTPError: %r" %(e))
            return (0,0,[])
    
    def get_loanid_from_url(self, url):
        m = re.match(self.loanid_url_pattern, url)
        if m is not None:
            return int(m.group(1))
        else:
            m2 = re.match(self.loanid_rul_pattern2, url)
            if m2 is not None:
                return int(m2.group(1))
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