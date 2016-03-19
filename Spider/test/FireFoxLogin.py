#-*- coding: utf-8 -*-
'''
Created on 2016年3月13日

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
from biz.AutoBid import AutoBid
import logging
import os
from datetime import date
from datetime import datetime
from time import sleep
import random
import traceback
from sys import argv
import urllib
import urllib2
import re
import cookielib
import gzip
from StringIO import StringIO

class FireFoxLogin(object):
    '''
    classdocs
    '''
    username = None
    password = None
    opener = None
    cookie = None
    header_user_agent = [("User-Agent","Mozilla/5.0 (Windows NT 6.1; rv:12.0) Gecko/20100101 Firefox/12.0")]

    def __init__(self, username, password, cookie_file):
        '''
        Constructor
        '''
        self.password = password
        self.username = username
        self.cookie = cookielib.MozillaCookieJar(cookie_file)
        handler = urllib2.HTTPCookieProcessor(self.cookie)
        self.opener  = urllib2.build_opener(handler)
        urllib2.install_opener(self.opener)
    
    def step_1_open_login_page(self):
        url = "https://ac.ppdai.com/User/Login?redirect="
        headers = {
            'Referer': 'https://ac.ppdai.com/User/Login?redirect=',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            "Accept-Encoding":"gzip, deflate, sdch",
            "Host": "ac.ppdai.com",
            'Accept-Language': "zh-cn,zh;q=0.8,en-us;q=0.5,en;q=0.3",
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        self.open_page(url, headers, None)
    

    
    def open_query_risk_control(self):
        url = "https://ac.ppdai.com/User/QueryRiskControl"
        data = {"loginAccount": self.username}
        post_data = urllib.urlencode(data)
        headers = {
            "Accept":"*/*",
            "Accept-Encoding":"gzip,deflate",
            "Accept-Language":"zh-cn,zh;q=0.8,en-us;q=0.5,en;q=0.3",
            "Cache-Control":"no-cache",
            "Connection":"keep-alive",
            "Content-Length":"24",
            "Content-Type":"application/x-www-form-urlencoded;charset=UTF-8",
            "Host":"ac.ppdai.com",
            "Pragma":"no-cache",
            "Referer":"https://ac.ppdai.com/User/Login?redirect=",
            "X-Requested-With":"XMLHttpRequest"
        }
        self.open_page(url, headers, post_data)
    
    def login(self):
        url = "https://ac.ppdai.com/User/Login"
        data = {"IsAsync":"true","Redirect":"","UserName":self.username,"Password":self.password,"RememberMe":"false"}
        post_data = urllib.urlencode(data)
        headers = {
            "Accept":"*/*",
            "Accept-Encoding":"gzip,deflate",
            "Accept-Language":"zh-cn,zh;q=0.8,en-us;q=0.5,en;q=0.3",
            "Cache-Control":"no-cache",
            "Connection":"keep-alive",
            "Content-Length":"77",
            "Content-Type":"application/x-www-form-urlencoded;charset=UTF-8",
            "Host":"ac.ppdai.com",
            "Pragma":"no-cache",
            "Referer":"https://ac.ppdai.com/User/Login?redirect=",
            "X-Requested-With":"XMLHttpRequest"
        }
        self.open_page(url, headers, post_data)
        
    def open_lend(self):
        url = "http://www.ppdai.com/account/lend"
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            "Accept-Encoding":"gzip, deflate",
            "Host": "www.ppdai.com",
            'Accept-Language': "zh-cn,zh;q=0.8,en-us;q=0.5,en;q=0.3",
            'Connection': 'keep-alive',
        }
        self.open_page(url, headers, None)
        invest_url = "http://invest.ppdai.com/account/lend"
        self.open_page(invest_url, headers, None)
        
        
    def add_headers(self, header_hash):
        self.opener.addheaders = self.header_user_agent
        for header in header_hash:
            self.opener.addheaders.append((header, header_hash[header]))
    
    ''' Common funciton to parse response (both normal and gzip format) to get HTML '''
    def get_html_from_response(self, response):
        info = response.info()
        html = response.read()
        if info.get('Content-Encoding') == 'gzip':
            buf = StringIO(html)
            f = gzip.GzipFile(fileobj=buf)
            return f.read()
        else:
            return html
    
    ''' Common function to open pages '''
    def open_page(self, url, headers, data):
        self.add_headers(headers)
        response = self.opener.open(url,data,10)
        html = self.get_html_from_response(response)
        headers = response.info()
        logging.info("HTML: %s" %(html))
        header_str = ""
        for head in headers:
            header_str += "%s: %s\n" %(head, headers[head])
        logging.info("Headers::\n%s" % (header_str))
    
    def print_cookie(self):
        cs = ""
        for ck in self.cookie:
            cs += "%s=%s," %(ck.name,ck.value)
        logging.info("Cookie:: %s" % (cs))

def init_logging(ppdid):
    today = date.today().isoformat()
    logfile = "D:/ppdai/TestLogin.%s.%s.log" % (ppdid, today)
    i = 1
    while os.path.exists(logfile):
        logfile = "D:/ppdai/TestLogin.%s.%s.%d.log" % (ppdid, today, i)
        i += 1
    logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename=logfile,
                filemode='a')
    
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s %(levelname)-4s %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)

            
if __name__ == '__main__':
    ppdid = '18616027065'
    init_logging(ppdid)
    login = FireFoxLogin(ppdid, 'yanjie123', "D:/ppdai/firefox_cookie.txt")
    login.step_1_open_login_page()
    login.print_cookie()
    sleep(2)
    logging.info("Query Risk Control!")
    login.open_query_risk_control()
    login.print_cookie()
    logging.info("Login!!")
    login.login()
    login.print_cookie
    logging.info("Open  Lend!")
    sleep(1)
    login.open_lend()
    pass