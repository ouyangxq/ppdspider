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
import logging
from urllib2 import HTTPError
import random
from spider.PPDLogin import PPDLogin 
from util.PPBaoUtil import PPBaoUtil

class PPDSpider(object):

    login_url = None
    safe_loanlist_url = None
    medium_risk_loanlist_url = None
    high_risk_loanlist_url = None
    cookie_file = "ppdai_cookie.txt" # File to store cookies to be used for all connections
    opener = None
    cookie = None
    ppdlogin = None
    ppbao_config = None # This is to share the intersted ppd rate and loanrate
    
    risksafe = 'safe'
    riskmiddle = 'riskmiddle'
    riskhigh   = 'riskhigh'
    risktype = [risksafe, riskmiddle, riskhigh]
    '''!!! 20160320: Any Loan ask for more than this number will NOT be parsed !!!'''
    ''' Probably shall put into a slow thread which is just for logging purpose '''
    ''' An fast thread to only scan those with good education background '''
    MAX_LOAN = 12000
    
    login_url     = "https://ac.ppdai.com/User/Login?message=&Redirect="
    safe_page_url = 'http://invest.ppdai.com/loan/list_safe_s0_p5?Rate=0'
    highrisk_page_url = 'http://invest.ppdai.com/loan/list_riskhigh_s5_p2?Rate=0'
    mediumrisk_page_url = 'http://invest.ppdai.com/loan/list_riskmiddle_s0_p2?Rate=0'
    loanid_url_pattern = re.compile('.*info\?id=(\d+)')
    loanid_rul_pattern2 = re.compile("http://www.ppdai.com/list/(\d+)")
    ''' loanid_pattern: PPDRate, LoanURL, Title, Certs '''
    # Change rank="4" to rank="\d" as that's made PPBao only select C biao!!
    loanid_pattern  = re.compile('<a href="http://help.ppdai.com/Home/List/12" target="_blank" rank="\d">.*?<i class="creditRating (\S+?)" title=.*?'
                                 + '<div class="w230 listtitle">.*?<a class="title ell" target="_blank" href="(.*?)" title=".*?">.*?</a>' 
                                 + '.*?</div>.*?<div class="w90 cert" id="cert">(.*?)</div>.*?<div class="w110 brate".*?<span>%</span>.*?'
                                 + '<div class="w90 sum"> <span>&yen;</span>(\S+?)\s*?</div>', re.S)
    loan_count_pattern = re.compile('<span class="fr">共找到 <em class="cfe8e01">(\d+)</em> 个标的</span>', re.S)
    page_pattern = re.compile("<div class='pager'><span class='pagerstatus'>共(\d+)页", re.S)
    certs_xueli_pattern = re.compile("<i class='record' title='学历认证'></i>", re.S)
    certs_mobile_pattern = re.compile("<i class='phone'  title='手机实名认证'></i>", re.S)
    
    def __init__(self,loginid, ppbao_config):
        self.login_url = "https://ac.ppdai.com/User/Login?redirect="
        self.cookie_file = "ppdai_cookie.%s.txt" %(loginid) # File to store cookies to be used for all connections
        self.ppdlogin = PPDLogin(self.cookie_file)
        self.ppbao_config = ppbao_config
        
    def get_login_url(self):
        return self.login_url
    
    def login(self,ppdloginid, ppdpasswd):
        try:
            (opener,cookie) = self.ppdlogin.init_opener(self.cookie_file)
            self.ppdlogin.before_login(ppdloginid,ppdpasswd, opener)
            self.ppdlogin.print_cookie(cookie)
            logging.info("LOGIN!!")
            self.ppdlogin.login(ppdloginid,ppdpasswd, opener)
            self.ppdlogin.print_cookie(cookie)
            logging.info("Open Lend Page!!")
            self.ppdlogin.open_lend(opener)
            #Login2.print_cookie(cookie)
            self.opener = opener
            self.cookie = cookie
            ppduserid = 'None'
            for item in self.cookie:
                logging.debug("Cookie:Name=" + item.name + ",Value=" + item.value)
                if (item.name == 'ppd_uname'):
                    ppduserid = item.value
                    logging.info("PPD Username: %s" % (ppduserid))
            return (opener, ppduserid)
        except urllib2.URLError, e:
            logging.error("URLError: Not Able to Login to PPDAI! - Error: %r" % (e))
            return (None, None)
        except urllib2.HTTPError, e:
            logging.error("HTTPError: Not Able to login to PPDAI!- Error: %d" % (e.code))
            return (None, None)
    
    def login_until_success(self,username, password):
        try: 
            (opener, ppduserid) = self.login(username, password)
            count = 0
            while opener == None:
                count += 1;
                sleep_time = random.randint(20,60)
                if (count % 10 == 0):
                    sleep_time = random.randint(120,300)
                logging.error("Error: Not able to login to PPDAI(www.ppdai.com). Retry in %d seconds! RetryCount(%d)" %(sleep_time, count))
                sleep(sleep_time)
                (opener, ppduserid) = self.login(username, password)
            logging.info("Login to www.ppdai.com Successfully!!!")
            return (opener, ppduserid)
        except Exception, e:
            sleep_time = random.randint(120,600)
            logging.error("Error: Encounter Exception %r on login to PPDAI. Sleep %d seconds before retry..." % (e, sleep_time))
            
            ''' !!! This may cause Infinite Loop!!! '''
            return self.login_until_success(username, password)
        
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
    
    
    def get_loan_list_urls (self, loan_url, referer_url):
        " This function is to analsysis the Loan List page and return a list of links point to the detailed loan info page"
        try:
            self.opener.addheaders = [('User-Agent','Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.73 Safari/537.36')]
            self.opener.addheaders.append(('Origin', 'http://invest.ppdai.com'))
            self.opener.addheaders.append(('Host','invest.ppdai.com'))
            self.opener.addheaders.append(('Accept-Encoding','gzip, deflate, sdch'))
            self.opener.addheaders.append(('Referer',referer_url))
            self.opener.addheaders.append(('Accept','*/*'))
            self.opener.addheaders.append(('Accept-Language','zh-CN,zh;q=0.8,en;q=0.6'))
            self.opener.addheaders.append(('Connection','keep-alive'))
            self.opener.addheaders.append(('Cache-Control','max-age=0'))
            response = self.opener.open(loan_url,None,15)
            html_str = PPBaoUtil.get_html_from_response(response)
            response.close()
            return self.get_loanurllist_from_page_html(html_str)
        except HTTPError, e:
            logging.error("Failed to open page: %s - Reason: %r" %( loan_url, e))
            return None
        except Exception,e:
            logging.error("Open Page to get loan list failed. URL: %s. Error: %r" %(loan_url, e))
            return None

    def get_loanurllist_from_page_html(self, html_str):
        items    = re.findall(self.loanid_pattern, html_str)
        result_list = []
        for item in items:
            # 20160312: only search Loan with Xueli and Mobile certificates 
            ppdrate, loanurl, certs, loan_money_str = (item[0], item[1], item[2], item[3])
            loanmoney = int(loan_money_str.replace(',',''))
            xueli_m = re.search(self.certs_xueli_pattern, certs)
            mobile_m = re.search(self.certs_mobile_pattern, certs)           
            #logging.debug("%s, %s, %s, %s" % (ppdrate, loanurl, title, certs))
            if ((ppdrate in self.ppbao_config.strategy_ppdrate_list) == False):
                logging.debug("Ignore Loan as ppdrate(%s) is not interested(Not in PPBao Config): %s" % (ppdrate, loanurl))
            elif (xueli_m is None) and (mobile_m is None):
                logging.debug("No Xueli and Mobile Cert!! Ignore loan %s" %(loanurl))
            elif (loanmoney >= self.MAX_LOAN):
                logging.debug("Ignore Loan as it ask for more than MAX_LOAN (%d>%d) - %s" % (loanmoney, self.MAX_LOAN, loanurl))
            else:
                result_list.append(loanurl)
                
        return result_list
    
    def open_loan_detail_page(self, loanurl, referer_url):
        try:
            headers = {
                'Referer':referer_url,
                'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Upgrade-Insecure-Requests':'1',
                'Accept-Language':'zh-CN,zh;q=0.8,en;q=0.6',
                'Host':'invest.ppdai.com',
                'Accept-Encoding':'gzip, deflate, sdch',
                'User-Agent':'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.73 Safari/537.36',
                'Connection':'keep-alive'    
            }
            self.opener = PPBaoUtil.add_headers(self.opener, headers)
            response = self.opener.open(loanurl,None,15)
            html_str = PPBaoUtil.get_html_from_response(response)
            response.close()
            return html_str
        except urllib2.URLError, e:
            logging.error("Not able to open %s, %r" % (loanurl, e))
            return None
        except Exception,e:
            logging.error("On OpenPage %s - Caught Exception %r" %(loanurl,e))
            return None
        
    def open_page(self,url,referer_url):
        '''
        Try to Open page and return the HTML String for further analysis
        '''
        try:
            self.opener.addheaders.append(('Origin', 'http://invest.ppdai.com'))
            self.opener.addheaders.append(('Host','invest.ppdai.com'))
            self.opener.addheaders.append(('Referer',referer_url))
            self.opener.addheaders.append(('Accept','*/*'))
            self.opener.addheaders.append(('Connection','keep-alive'))
            self.opener.addheaders.append(('Cache-Control','max-age=0'))
            self.opener.addheaders.append(('Accept-Encoding','gzip, deflate, sdch'))
            self.opener.addheaders.append(('Accept-Language','zh-CN,zh;q=0.8,en;q=0.6'))
            self.opener.addheaders.append(('User-Agent','Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.73 Safari/537.36'))
            response = self.opener.open(url,None,15)
            html_str = PPBaoUtil.get_html_from_response(response)
            response.close()
            return html_str
        except urllib2.URLError, e:
            logging.error("Not able to open %s, %r" % (url, e))
            return None
        except Exception,e:
            logging.error("On OpenPage %s - Caught Exception %r" %(url,e))
            return None
    
    # Get Number of Pages of loans
    def get_pages(self, loan_url, last_url):
        try:
            '''
            headers = {
                'Referer':'http://invest.ppdai.com/loan/list_riskmiddle?monthgroup=&rate=0&didibid=&listingispay=',
                'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Upgrade-Insecure-Requests':'1',
                'Accept-Language':'zh-CN,zh;q=0.8,en;q=0.6',
                'Host':'invest.ppdai.com',
                'Accept-Encoding':'gzip, deflate, sdch',
                'User-Agent':'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.73 Safari/537.36',
                'Connection':'keep-alive'
                }
            self.opener.addheaders = headers
            '''
            self.opener.addheaders = [('User-Agent','Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.73 Safari/537.36')]
            self.opener.addheaders.append(('Referer',last_url))
            self.opener.addheaders.append(('Accept','text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'))
            self.opener.addheaders.append(('Accept-Language','zh-CN,zh;q=0.8,en;q=0.6'))
            self.opener.addheaders.append(('Accept-Encoding','gzip, deflate, sdch'))
            self.opener.addheaders.append(('Connection','keep-alive'))
            self.opener.addheaders.append(('Upgrade-Insecure-Requests','1'))
            logging.debug("OpenURL: %s" % (loan_url))
            response = self.opener.open(loan_url,None,10)
            html_str = PPBaoUtil.get_html_from_response(response)
            response.close()
            #logging.debug("HTML: %s" % (html_str))
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
    
    # Read Histroy Loan
    def open_history_loan(self, loanurl):
        headers = {
                'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Upgrade-Insecure-Requests':'1',
                'Accept-Language':'zh-CN,zh;q=0.8,en;q=0.6',
                'Host':'invest.ppdai.com',
                'Accept-Encoding':'gzip, deflate, sdch',
                'User-Agent':'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.73 Safari/537.36',
                'Connection':'keep-alive',
                'Cache-Control':'max-age=0'  
            }
        self.opener = PPBaoUtil.add_headers(self.opener, headers)
        response = self.opener.open(loanurl,None,10)
        html_str = PPBaoUtil.get_html_from_response(response)
        response.close()
        return html_str