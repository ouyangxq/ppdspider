#!python
#-*- coding:utf-8 -*-
'''
Created on 20160221

@author: Xiaoqi Yang
'''

import re
import logging
from ds.PPDLoan import PPDLoan
from ds.PPDUser import PPDUser

class PPDHtmlParser(object):
    '''
    HTML Parser: parse the HTML contents and build as PPDLoan / PPDUser Instance
    '''

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
    pattern_current_progress = re.compile('<span id="process" style="width: (\d+)\%')
    pattern_myaccount_money  = re.compile('<div class="inputbox">.*?<p class="accountinfo clearfix">.*?账户余额.*?<em id="accountTotal">&#165;(\S+?)</em>',re.S)
    title_pattern = re.compile('<div class="newLendDetailbox">.*?<h3 class="clearfix">.*?<span class="" tt="\d+">(\S+?)</span>', re.S)
    
    def __init__(self):
        '''
        Constructor
        '''
        pass
        
    def parse_loandetail_html(self, loanid, datetime, html):
        '''
        Parse loan Detail page content to get the loan details in PPDLoan / PPDUser data structure
        Return: ppdloan, ppduser, mymoney
        '''
        "Check current progress"
        m = re.search(self.pattern_current_progress, html)
        if m is None: 
            logging.error("Error 1: PPDai Loan Detail Page pattern has been changed! Not able to get loan progress.")
            return (None, None, None)
        else:
            progress = m.group(1)
            if (progress == 100):
                logging.warn("Loan %s is already 100% completed. Continue to parse other loans")
                return (None, None, None)
            
        " Get Basic information "
        m = re.search(self.pattern_user_basic_info, html)
        if m is None:
            logging.error("Error 2: PPDai Loan Detail Page pattern has been changed! Check/Modify it and retry")
            return (None, None, None)
        else:
            other,gender, age, marriage, education_level, house, car = m.groups()
            age = int(age)

        " Get Loan Rate & Userid"
        um = re.search(self.pattern_loanrate_info, html)
        if um is None:
            print "Error 2: PPDai Loan Detail Page pattern has been changed! Check/Modify it and retry"
            return None
        else:
            ppdrate, userid, money, loanrate, maturity = um.groups()
            money = int(money.replace(',',''))
            maturity = int(maturity)
            loanrate = float(loanrate)
        
        " Build PPDLoan and PPDUser instance"
        ppdloan = PPDLoan({'loanid':loanid, 'datetime':datetime, 'loanrate':loanrate, 'ppdrate':ppdrate, \
                           'money':money, 'maturity':maturity, 'userid':userid, 'age': age})
        ppduser = PPDUser({'userid':userid, 'gender': gender, 'age': age, 'marriage': marriage, \
                           'house': house, 'car': car, 'education_level': education_level}) 
        ppdloan.set_ppduser(ppduser)
        
        "Get Loan History"
        histm = re.search(self.pattern_loan_history, html)
        if histm != None:
            ontime, in15d, mt15d, total_loan, left_loan, left_lend = histm.groups()
            ppdloan.set_history_info(int(ontime), int(in15d), int(mt15d), int(total_loan.replace(',','')), \
                                     float(left_loan.replace(',','')), float(left_lend.replace(',','')))
        else:
            logging.warn("Error: Can't get History Lend information. Ignore it for now. But Please do check it!")   
        
        "Set Certificates"
        certs = re.search(self.pattern_education_cert, html)
        if (certs != None):
            ppduser.add_education_cert(certs.group(1), certs.group(2), certs.group(3))
        
        "My Account Money"
        mymoneym = re.search(self.pattern_myaccount_money, html)
        if mymoneym is not None:
            mymoney = float(mymoneym.group(1).replace(',',''))
        else:
            mymoney = -1
        
        " Loan Title "
        titlem = re.search(self.title_pattern, html)
        if titlem is not None:
            title = titlem.group(1)
        else:
            title = "NA"
        ppdloan.loantitle = title
        
        return (ppdloan,ppduser,mymoney)