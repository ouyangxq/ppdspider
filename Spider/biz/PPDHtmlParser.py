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
    status_normal   = 0 
    status_under_evaluation = 1
    status_invalid  = 2
    status_completed = 3
    
    # Patterns:
    pattern_user_basic_info = re.compile('<div class="lendDetailTab w1000center">.*?<div class="lendDetailTab_tabContent">.*?' 
                                    + '<table class="lendDetailTab_tabContent_table1">.*?<tr>.*?</tr>.*?<tr>.*?' 
                                    + '<td>(\S*?)</td>.*?<td>(\S+)</td>.*?<td>(\S+?)</td>.*?<td>(\S+?)</td>.*?' 
                                    + '<td>(.*?)</td>.*?<td>.*?(\S+).*?</td>.*?<td>(.*?)</td>.*?</tr>.*?</table>', re.S)
    pattern_education_cert = re.compile("<p class='clearfix'><i class='xueli'></i>.*?认证：（毕业学校：(\S+)，学历：(\S+)，学习形式：(\S*?)）</p>",re.S)

    pattern_loan_history = re.compile('<h3>拍拍贷统计信息</h3>.*?<p>历史统计</p>.*?<p>正常还清：(\d+).*?次，逾期还清\(1-15\)：(\d+).*?次，逾期还清\(>15\)：(\d+).*次 </p>' +
                          '.*?共计借入：<span class="orange">&#165;(\S+)</span>.*?待还金额：<span class="orange">&#165;(\S+)</span>' + 
                         '.*?待收金额： <span class="orange">.*?&#165;(\S+).*?</span>.*?</p>', re.S)
    
    pattern_loanrate_info = re.compile('<div class="newLendDetailInfoLeft">.*?<a href="http://help.ppdai.com/Home/List/12" target="_blank" class="altQust">' 
                                   + '<span title="魔镜等级：AAA至F等级依次降低，等级越高逾期率越低。点击等级了解更多。" class="creditRating (\S+)"></span></a>.*?'
                                   + '<a href="http://www.ppdai.com/user/\S+" class="username">(\S+)</a>.*?'
                                   + '<div class="newLendDetailMoneyLeft">.*?<dt>借款金额：</dt>.*?<dd><em>&yen;</em>(\S+?)</dd>.*?'
                                   + '<dt>年利率：</dt>.*?<dd>(\S+?)<em>%</em></dd>.*?'
                                   + '<dt>期限：</dt>.*?<dd>(\d+) <em>个月</em></dd>', re.S)
    pattern_current_progress = re.compile('<span id="process" style="width:\s+(\S+?);"></span>')
    pattern_myaccount_money  = re.compile('<div class="inputbox">.*?<p class="accountinfo clearfix">.*?账户余额.*?<em id="accountTotal">&#165;(\S+?)</em>',re.S)
    title_pattern = re.compile('<div class="newLendDetailbox">.*?<h3 class="clearfix">.*?<span class="" tt="\d+">(\S+?)</span>', re.S)
    job_cert_pattern = re.compile('稳定工作证明')
    benk_detail_pattern = re.compile('个人常用银行流水')
    getihu_pattern = re.compile('个体户证明')
    hukou_cert_pattern = re.compile("<p class='clearfix'><i class='hukou'></i>户口所在地")
    shouru_cert_pattern = re.compile("收入证明")
    id_card_pattern = re.compile(".*?身份证的.*?照片")
    ren_hang_trust_cert_pattern = re.compile("征信认证")
    shebao_gjj_cert_pattern = re.compile("社保(\/)?公积金")
    zhifubao_cert_pattern = re.compile("支付宝账户信息")
    student_cert_pattern = re.compile("学生证或一卡通正反面")
    driver_cert_pattern = re.compile("机动车行驶证")
    
    # PPDRate, UserId, money, loanrate, maturity, datetime
    pattern_history_loan2 = re.compile('<a href="http://help.ppdai.com/Home/List/12" target="_blank" class="altQust">.*?'
                                    + '<span title="魔镜等级：.*?class="creditRating (\S+)"></span></a>.*?' 
                                    + '<a href="http://www.ppdai.com/user/\S+" class="username">(\S+?)</a>.*?' 
                                    + '<div class="newLendDetailMoneyLeft">.*?<dt>借款金额：</dt>.*?<dd><em>&yen;</em>(\S+?)</dd>.*?' 
                                    + '<dt>年利率：</dt>.*?<dd>(\S+?)<em>%</em></dd>.*?'
                                    + '<dt>期限：</dt>.*?<dd>(\d+?)\s*?<em>个月</em></dd>.*?'
                                    + '结束时间：.*?<span class="countdown_row countdown_amount" id="leftTime">(\S+?)</span>', re.S)
    
    ''' TBD: Filter the history Loan detail (Rate and Money) and use that in BidStrategy 
    - We shall not bid any loan that has history Loan Rate as 30% or 36% '''
    pattern_all_history_loan = re.compile('<p>历史借款</p>.*?<table class="lendDetailTab_tabContent_table1">.*?<tr>.*?</tr>(.*?)</table>', re.S);
    pattern_history_loan = re.compile('<tr>\s+<td>\s+(\d+).*?</td>.*?<td style="text-align: left">\s+<a href=".*?</a>\s+</td>\s+?<td>\s+?(\S+)%\s+?</td>\s+<td>.*?&#165;(\S+?)\s+</td>\s+<td>\s+(\S+?)\s+</td>\s+<td>\s+?(\S+)\s+?</td>\s+</tr>', re.S)
    pattern_history_loan_retuan_dates = re.compile('xAxis: \{.*?categories: \[(.*?)\],', re.S)
    pattern_history_loandetail_chart = re.compile("name: '负债曲线',\s+data: \[\s+(.*?)\s+\]\s+\}", re.S)
    pattern_status_normal = re.compile('借款余额：')
    pattern_status_under_estimation = re.compile('(正在评估中)|(正在预审中)')
    pattern_status_invalid = re.compile('(403 Forbidden)|(投标已结束)')
    pattern_status_completed = re.compile('借款成功')
    pattern_ppdrate = re.compile('class="creditRating (\S+)"')
    pattern_good_bidders = re.compile('(kuku9991)|(jiangmg520)')
    
    def __init__(self):
        '''
        Constructor
        '''
        pass
        
    def get_loan_status (self, loanid, html):
        '''
        Valid Loan status: normal(0), under_evaluation(1), invalid(2)
        '''
        if (re.search(self.pattern_status_normal, html)):
            return self.status_normal
        elif (re.search(self.pattern_status_completed, html)):
            return self.status_completed
        elif (re.search(self.pattern_status_under_estimation, html)):
            return self.status_under_evaluation
        elif (re.search(self.pattern_status_invalid, html)):
            return self.status_invalid
        else:
            logging.info("Error: get_loan_status: Not able to match the status for loanid: %d. Assume it's invalid." % (loanid))
            return self.status_invalid
    
    def get_loan_ppdrate(self, loanid, html):
        m = re.search(self.pattern_ppdrate, html)
        if m is not None:
            return m.group(1)
        else:
            logging.info("Error: get_loan_ppdrate: not able to match the patter for loanid: %d. " % (loanid))
            return None
        
        
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
            if (progress == '100%'):
                logging.debug("Loan %d is already fully completed. Continue to parse other loans" % (loanid))
                ''' set my money to be -1 to indicate this is 100% completed loan '''
                return (None, None, -1)
            
        " Get Basic information "
        m = re.search(self.pattern_user_basic_info, html)
        if m is None:
            if (re.search('<div class="newbidstatus_lb">投标已结束</div>', html) is not None):
                logging.warn("Loan %d is Aborted by PPDAI. No Check further. Continue." % (loanid))
                return (None, None, -1)
            else:
                logging.error("Error 2: Not able to get user basic info! PPDai Loan Detail Page pattern has been changed! Check/Modify it and retry")
                logging.debug(html)
                return (None, None, None)
        else:
            other,gender, age, marriage, education_level, house, car = m.groups()
            age = int(age)

        " Get Loan Rate & Userid"
        um = re.search(self.pattern_loanrate_info, html)
        if um is None:
            logging.error("Error 3: Not able to get LoanRate/Userid!PPDai Loan Detail Page pattern has been changed! Check/Modify it and retry")
            logging.debug(html)
            return (None,None,None)
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
        ppdloan.set_loantitle(title)
        
        " 20160306: Set Other Certificates "
        ppduser.job_cert = 1 if re.search(self.job_cert_pattern, html) else 0        
        ppduser.shouru_cert = 1 if re.search(self.shouru_cert_pattern, html) else 0        
        ppduser.hukou_cert = 1 if re.search(self.hukou_cert_pattern, html) else 0        
        ppduser.ren_hang_trust_cert = 1 if re.search(self.ren_hang_trust_cert_pattern,html) else 0        
        ppduser.shebao_gjj_cert = 1 if re.search(self.shebao_gjj_cert_pattern, html) else 0        
        ppduser.idcard_cert = 1 if re.search(self.id_card_pattern, html) else 0        
        ppduser.bank_details_cert = 1 if re.search(self.benk_detail_pattern, html) else 0
        ppduser.getihu_cert = 1 if (re.search(self.getihu_pattern, html)) else 0
        ppduser.alipay_cert = 1 if re.search(self.zhifubao_cert_pattern, html) else 0
        ppduser.student_cert = 1 if re.search(self.student_cert_pattern, html) else 0
        ppduser.driver_cert = 1 if re.search(self.driver_cert_pattern, html) else 0
        
        gbm = re.search(self.pattern_good_bidders, html)
        if gbm is not None:
            ppdloan.set_source('kuku9991') 
        
        (IfHas30or36RateLoan, IfHasLessThan1000Loan) = self.check_history_loan(ppdloan, html)
        ppdloan.has_30or36rate_loan_history = 1 if IfHas30or36RateLoan == True else 0
        ppdloan.has_lt1000_loan_history = 1 if IfHasLessThan1000Loan == True else 0
        
        " Parse History Total Loans "
        m2 = re.search(self.pattern_history_loandetail_chart, html)
        if (m2 is not None):
            history_total_loan_slist = re.findall('(\S+?),\s*', m2.group(1))
            flist = []
            for i in range(0,len(history_total_loan_slist)-1):
                flist.append(float(history_total_loan_slist[i]))
            """ This is to filter the history max loan by remove the duplication return dates that I noticed
            Basically what happened is the loaner can loan a lot but he or she has to pay the previous loan first (can't withdraw to his bank account directly)
            So it's not a valid max history loan per say, so add an extra logic to deal with it. 
            """
            m3 = re.search(self.pattern_history_loan_retuan_dates, html)
            if (m3 is not None):
                history_return_dates = re.findall('\s*"(\d+\/\d+\/\d+)",', m3.group(1))
                if len(history_return_dates) == len(history_total_loan_slist):
                    (max_hloan, mdate) = (flist[0], history_return_dates[0])
                    for i in range(1, len(flist)):
                        #logging.debug("HistoryDate: %s: %d" % (history_return_dates[i], flist[i]) )
                        if (max_hloan < flist[i]):
                            max_hloan = flist[i]
                            mdate = history_return_dates[i]
                        elif mdate == history_return_dates[i]:
                            logging.debug("Set Max History Loan for %d from %d to %d as date(%s) is same." % (loanid, max_hloan, flist[i], mdate))
                            max_hloan = flist[i]
                        else:
                            pass
                    
                    ppdloan.history_highest_total_loan = max_hloan
                else:
                    ppdloan.history_highest_total_loan = max(flist)
            else:
                ppdloan.history_highest_total_loan = max(flist)
            ppdloan.new_total_loan = float(history_total_loan_slist[-1]) # -1 means the last one
        else:
            ''' means not able to get the history high '''
            ppdloan.history_highest_total_loan = 0 if ppdloan.history_total_loan == 0 else -1
            ppdloan.new_total_loan = ppdloan.money
        return (ppdloan,ppduser,mymoney)
    

    def check_history_loan(self, ppdloan, html):
        '''
        Parse History loan Detail page content to get the loan details in PPDLoan / PPDUser data structure
        Return: Notice we'll only get very limited information with the history loan page
        Return: IfHas30or36RateLoan, IfHasLessThan1000Loan
        '''

        m = re.search(self.pattern_all_history_loan, html)
        IfHas30or36RateLoan = False
        IfHasLessThan1000Loan = False
        if (m is None):
            if ppdloan.history_total_loan != 0:
                logging.warn("No able to parse History Loan for %d." % (ppdloan.loanid))
            return (IfHas30or36RateLoan, IfHasLessThan1000Loan)
        history_loans_html = m.group(1)
        #print html
        items = re.findall(self.pattern_history_loan, history_loans_html)
        for item in items:
            #9873318 8.02 9,000 成功 2016/3/19
            #9870912 7.12 6,000 已撤回 2016/3/19
            lid, lrate, lmoney, lstatus, ldate = item[0],item[1], item[2], item[3], item[4];
            lid = int(lid)
            lrate = float(lrate)
            lmoney = int(lmoney.replace(',', ''))
            lyear, lmonth, lday = re.split('/', ldate)
            ''' TO BE Enhanced '''
            if lrate >= 30:
                IfHas30or36RateLoan = True
            if lmoney < 1000:
                IfHasLessThan1000Loan = True
                
        return (IfHas30or36RateLoan, IfHasLessThan1000Loan)
                