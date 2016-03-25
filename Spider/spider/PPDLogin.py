#-*- coding:utf-8 -*-
'''
Created on 2016 Mar 6th. 
Modified on Mar 8th.

@author: Administrator
'''

import logging
import urllib
import urllib2
import cookielib
from util.PPBaoUtil import PPBaoUtil


class PPDLogin(object):
    
    cookie = None
    opener = None
    cookie_file = None

    def __init__(self, cookie_file):
        self.cookie_file = cookie_file
        
    def init_opener(self, cookie_file):
        cookie = cookielib.MozillaCookieJar(cookie_file)
        handler = urllib2.HTTPCookieProcessor(cookie)
        opener  = urllib2.build_opener(handler)
        urllib2.install_opener(opener)
        return (opener,cookie)
    
    def print_cookie(self, cookie):
        for ck in cookie:
            logging.debug("Cookie:: %s=%s" %(ck.name,ck.value))          
    
    def before_login(self, username, password, opener):
        # Step 1:
        url = "https://ac.ppdai.com/User/Login?message=&Redirect="
        #method = 'GET'
        opener.addheaders = [('User-agent', 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.73 Safari/537.36')]
        opener.addheaders.append(('Host','ac.ppdai.com'))
        opener.addheaders.append(('Origin', 'https://ac.ppdai.com'))
        opener.addheaders.append(('Referer', 'https://ac.ppdai.com/User/Login?redirect='))
        opener.addheaders.append(('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'))
        opener.addheaders.append(('Accept-Language', 'zh-CN,zh;q=0.8,en;q=0.6'))
        opener.addheaders.append(('Connection', 'keep-alive'))
        opener.addheaders.append(('Upgrade-Insecure-Requests', '1'))
        response = opener.open(url,None,10)
        html = response.read()
        headers = response.info()
        #logging.info("HTML: %s" %(html))
        for head in headers:
            logging.debug("%s: %s" % (head, headers[head]))
    '''
    def query_risk_control(username):
        url = "https://ac.ppdai.com/User/QueryRiskControl"
        post_data = {"loginAccount": username}
        headers = {
        
                   }
    '''
    
    def login(self, username, password, opener):
        url = "https://ac.ppdai.com/User/Login"
        #method = "POST"
        opener.addheaders = [('User-agent', 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.73 Safari/537.36')]
        opener.addheaders.append(('Host','ac.ppdai.com'))
        opener.addheaders.append(('Origin','https://ac.ppdai.com'))
        opener.addheaders.append(('Referer','https://ac.ppdai.com/User/Login?redirect='))
        opener.addheaders.append(('Accept','*/*'))
        opener.addheaders.append(('Accept-Language','zh-CN,zh;q=0.8,en;q=0.6'))
        opener.addheaders.append(('Connection','keep-alive'))
        opener.addheaders.append(('Content-Type','application/x-www-form-urlencoded'))
        opener.addheaders.append(('X-Requested-With','XMLHttpRequest'))
        opener.addheaders.append(('Content-Length','77'))
        login_info = {"IsAsync":"true","Redirect":"","UserName":username,"Password":password,"RememberMe":"false"}
        login_data = urllib.urlencode(login_info)
        response = opener.open(url, login_data,10)
        logging.info("Get Response: %s", response.read())
        headers = response.info()
        for head in headers:
            logging.debug("%s: %s" % (head, headers[head]))
    
    def open_lend(self, opener):
        url = "http://invest.ppdai.com/account/lend"
        headers = {
                'Host':'invest.ppdai.com',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Encoding':'gzip, deflate, sdch',
                'Accept-Language':'zh-CN,zh;q=0.8,en;q=0.6',
                'Connection':'keep-alive',
                'Upgrade-Insecure-Requests':'1',
        }
        opener = PPBaoUtil.add_headers(opener, headers)
        response = opener.open(url, None,10)
        content = PPBaoUtil.get_html_from_response(response)
        info    = response.info()
        #logging.info("Get Response: %s", data)
        for head in info:
            logging.debug("%s=%s" %(head, info.get(head)))
    
    def open_blacklist(self, opener):
        url = "http://invest.ppdai.com/account/blacklist"
        headers = {
                'Host':'invest.ppdai.com',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Encoding':'gzip, deflate, sdch',
                'Accept-Language':'zh-CN,zh;q=0.8,en;q=0.6',
                'Connection':'keep-alive',
                'Upgrade-Insecure-Requests':'1',
                'Referer':'http://invest.ppdai.com/account/paybacklendreceived'
        }
        opener = PPBaoUtil.add_headers(opener, headers)
        response = opener.open(url, None, 10)
        html = PPBaoUtil.get_html_from_response(response)
        #logging.debug("Get Response: %s", html)
        response_headers = response.info()
        for head in response_headers:
            logging.debug("%s:%s" % (head, response_headers[head]))
    
'''  
if __name__ == '__main__':
    
    ppdloginid = '18616856236'
    ppdpasswd  = 'Oyxq270'
    init_logging(ppdloginid)
    (opener,cookie) = init_opener('D:/ppdai/test_cookie.txt')
    before_login(ppdloginid,ppdpasswd, opener)
    print_cookie(cookie)
    logging.info("LOGIN!!")
    login(ppdloginid,ppdpasswd, opener)
    print_cookie(cookie)
    logging.info("Open Lend Page!!")
    open_lend(opener)
    print_cookie(cookie)
    logging.info("Open Blacklist!!")
    open_blacklist(opener)
    print_cookie(cookie)
'''
    
