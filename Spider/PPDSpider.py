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

class PPDaiSpider(object):

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
    
    # Patterns:
    pattern_user_basic_info = re.compile('<div class="lendDetailTab w1000center">.*?<div class="lendDetailTab_tabContent">.*?' 
                                    + '<table class="lendDetailTab_tabContent_table1">.*?<tr>.*?</tr>.*?<tr>.*?' 
                                    + '<td>(\S*?)</td>.*?<td>(\S+)</td>.*?<td>(\S+?)</td>.*?<td>(\S+?)</td>.*?' 
                                    + '<td>(.*?)</td>.*?<td>.*?(\S+).*?</td>.*?<td>(.*?)</td>.*?</tr>.*?</table>', re.S)
    pattern_education_cert = re.compile("<p class='clearfix'><i class='xueli'></i>学历认证：（毕业学校：(\S+)，学历：(\S+)，学习形式：(\S+)）</p>",re.S)
    pattern_loan_history = re.compile('<h3>拍拍贷统计信息</h3>.*?<p>历史统计</p>.*?<p>正常还清：(\d+).*?次，逾期还清\(1-15\)：(\d+).*?次，逾期还清\(>15\)：(\d+).*次 </p>' +
                          '.*?共计借入：<span class="orange">&#165;(\S+)</span>.*?待还金额：<span class="orange">&#165;(\S+)</span>' + 
                         '.*?待收金额： <span class="orange">.*?&#165;(\S+).*?</span>.*?</p>', re.S)
    
    pattern_loanrate_info = re.compile('<div class="newLendDetailInfoLeft">.*?<a href="http://help.ppdai.com/Home/List/12" target="_blank" class="altQust">' 
                                   + '<span title="魔镜等级：AAA至F等级依次降低，等级越高逾期率越低。点击等级了解更多。" class="creditRating (\S+)"></span></a>.*?'
                                   + '<a href="http://www.ppdai.com/user/\S+" class="username">(\S+)</a>.*?'
                                   + '<div class="newLendDetailMoneyLeft">.*?<dt>借款金额：</dt>.*?<dd><em>&yen;</em>(\S+?)</dd>.*?'
                                   + '<dt>年利率：</dt>.*?<dd>(\S+?)<em>%</em></dd>.*?'
                                   + '<dt>期限：</dt>.*?<dd>(\d+) <em>个月</em></dd>', re.S)
    
    def __init__(self):
        self.login_url = "https://ac.ppdai.com/User/Login?redirect="
        self.cookie_file = "ppdai_cookie.txt" # File to store cookies to be used for all connections
    
    def login(self, username, password):

        login_info = {"UserName":username, "Password":password}
        login_data = urllib.urlencode(login_info)
        cookie = cookielib.MozillaCookieJar(self.cookie_file)
        handler = urllib2.HTTPCookieProcessor(cookie)
        opener  = urllib2.build_opener(handler)
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        opener.open(self.login_url, login_data)
        cookie.save(ignore_discard=True, ignore_expires=True)
        #for item in cookie:
        #    print "Name = " + item.name + " - Value=" + item.value
        self.opener = opener
        return opener
    
    # Use this function to check what are the URLs
    def build_loanpage_url(self, risktype, pageindex):
        url = "http://invest.ppdai.com/loan/list_%s_s0_p%d" % (risktype, pageindex)
        return url
    
    
    def get_loan_list_urls (self, loan_url):
        " This function is to analsysis the Loan List page and return a list of links point to the detailed loan info page"
        response = opener.open(loan_url)
        html_str = response.read() 
        pattern  = re.compile('<div class="w230 listtitle">.*?<a class="title ell" target="_blank" href="(.*?)" title="(.*?)">.*?</a>', re.S)
        items    = re.findall(pattern, html_str)
        result_list = []
        for item in items:
            result_list.append(item[0])
        return result_list
    
    def get_loan_details (self, loan_url):
        " Main Function - to get the loan details so as to do further analysis"
        response = self.opener.open(loan_url)
        html = response.read()
        loaninfo = None
        
        " Get Basic information "
        items    = re.findall(self.pattern_user_basic_info, html)
        if items is not None:
            for item in items:
                loaninfo = LoanInfo({"date":'20160219', 'sex':item[1], 'age':item[2], 
                                 'marriage':item[3], 'education':item[4], 'house':item[5], 'car':item[6]})
        
        " Get Loan Rate & Userid"
        loi = re.findall(self.pattern_loanrate_info, html)
        for item in loi:
            ppdrate, userid, money, loanrate, loan_duration = [item[0], item[1], item[2], item[3], item[4]]
            loaninfo.userid = userid
            loaninfo.money  = money.replace(',','')
            loaninfo.loanrate = loanrate
            loaninfo.ppdrate = ppdrate
            loaninfo.loan_duration = loan_duration
            
        
        "Get Certificates"
        certs = re.findall(self.pattern_education_cert, html)
        if len(certs) > 0:
            for cert in certs:
                loaninfo.add_education_cert(cert[0], cert[1], cert[2])
        
        "Get Loan History"
        hist = re.findall(self.pattern_loan_history, html)
        if hist != None and len(hist) == 1:
            loan_hist_data = hist[0]
            loan_hist = LoanHistory(int(loan_hist_data[0]), int(loan_hist_data[1]), int(loan_hist_data[2]),
                                    float(loan_hist_data[3].replace(',','')), float(loan_hist_data[4].replace(',','')), 
                                    float(loan_hist_data[5].replace(',','')))
            loaninfo.add_loan_hist(loan_hist)
        else:
            print "Not Able to get Loan History - Check the HTML source code to see if it has been changed by PPDAI!\n" 
        
        return loaninfo         

    # Get Number of Pages of loans
    def get_pages(self, loan_url):
        response = opener.open(loan_url)
        html_str = response.read()
        loan_count_pattern = re.compile('<span class="fr">共找到 <em class="cfe8e01">(\d+)</em> 个标的</span>', re.S)
        m = re.search(loan_count_pattern, html_str)
        loan_count = -1
        if m is not None:
            loan_count = int(m.group(1))
            if (loan_count == 0):
                print "0 Loans detected"
                return (0, 0)
            elif (loan_count <= 10):
                print "%d loans detected"
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
        
# main
if __name__ == '__main__':
    today = date.today()
    cnt = 0
    spider = PPDaiSpider()
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