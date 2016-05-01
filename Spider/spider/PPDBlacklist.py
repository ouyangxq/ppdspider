# coding: utf-8
'''
Created on 2016年3月20日

@author: Administrator
'''

import re
from util.PPBaoUtil import PPBaoUtil
import urllib2
import logging
from ds.PPDBlackLoan import PPDBlackLoan
from time import sleep
from ds.MyProfit import MyProfit

class PPDBlacklist(object):
    '''
    classdocs
    '''
    blacklist_url = "http://invest.ppdai.com/account/blacklist"
    # Userid, loanid, overdued, returned, bidmoney, overdue_days, history_overdue_days
    blackloan_patter = re.compile('<tr>.*?<td><span class="c39a1ea dib">(\S+?)</span>.*?' +
                                  '<span listingid="(\d+?)"\s+?listingtitle="(\S+?)" class=.*?' +
                                  '</span>.*?</td>.*?<td>&#165;(.*?) / &#165;(.*?) / &#165;(\d+?).\d+</td>.*?' +                                
                                  '.*?<td>(\d+)\s*?天（(\d+)\s*?天） </td>', re.S)
    page_pattern = re.compile("<div class='pager'><span class='pagerstatus'>共(\d+)页</span>")
    
    pattern_profits = re.compile('<div class="my-f-r-d-top">累计收益</div>\s+?<div class="my-f-r-d-bt"><span style="font-size: 19px;">¥</span>\s*(\S+?)</div>\s+</div>\s+' +
                                 '<div class="my-f-r-detail br-lr fl">.*?</div>\s+<div class="my-f-r-detail fl">\s+' +
                                 '<div class="my-f-r-d-top">待收收益</div>\s+?<div class="my-f-r-d-bt"><span style="font-size: 19px;">¥</span>\s*(\S+?)</div>', re.S)
    
    pattern_blacklist_summary = re.compile('共(\d+)个列表，逾期本金/已还金额/投标金额：&#165;(\S+?)元&nbsp;/&nbsp;&#165;(\S+?)元&nbsp;/&nbsp;&#165;(\S+?)元')
    
    ppdspider = None
    blacklist = []
    realized_profits = 0.0
    unrealized_profits = 0.0
    num_of_blacklist = 0
    toubiao_money = 0
    returned_money = 0.0
    yuqi_money = 0.0
    max_loss_money = 0.0
    min_profits = 0.0
    html_str = None
    
    def __init__(self, ppdspider):
        '''
        Constructor
        '''
        self.ppdspider = ppdspider
        self.blacklist = []
        self.realized_profits = 0.0
        self.unrealized_profits = 0.0
        self.num_of_blacklist = 0
        self.toubiao_money = 0
        self.returned_money = 0.0
        self.yuqi_money = 0.0
        self.max_loss_money = 0.0
        self.min_profits = 0.0
        self.html_str = None
    
    def open_blacklist_page(self, page):
        try:
            if (page > 1):
                url = "http://invest.ppdai.com/account/blacklist?PageIndex=%d&IsCalendarRequest=0" % (page)
                refid = page - 1
                referer = "http://invest.ppdai.com/account/blacklist?PageIndex=%d&IsCalendarRequest=0" % (refid)
            else:
                url = "http://invest.ppdai.com/account/blacklist?UserName=&LateDayTo=1&LateDayFrom=&ListingTitle="
                referer = "http://invest.ppdai.com/account/lend"
            headers = {
                'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Upgrade-Insecure-Requests':'1',
                'Accept-Language':'zh-CN,zh;q=0.8,en;q=0.6',
                'Host':'invest.ppdai.com',
                'Accept-Encoding':'gzip, deflate, sdch',
                'User-Agent':'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.73 Safari/537.36',
                'Connection':'keep-alive'    
            }
            opener = PPBaoUtil.add_headers(self.ppdspider.opener, headers)
            response = opener.open(url,None,15)
            html_str = PPBaoUtil.get_html_from_response(response)
            response.close()
            return html_str;
        except urllib2.URLError, e:
            logging.error("Not able to open %s, %r" % (self.blacklist_url, e))
            return None
        except Exception,e:
            logging.error("On OpenPage %s - Caught Exception %r" %(self.blacklist_url,e))
            return None
    
    " Get Black List " 
    def get_blacklist(self, ppbaouserid):
        html_str = self.open_blacklist_page(1)
        self.html_str = html_str # Only set this for Page 1
        blacklist = PPDBlacklist.parse_blacklist(html_str, ppbaouserid)
        
                    #exit (-1)
        m = re.search(self.page_pattern, html_str);
        if m is not None:
            pages = int(m.group(1))
            logging.info("Got %d pages of black loans!!" % (pages))
            for pageindex in range(2, pages+1): # notice 
                sleep(5)
                html = self.open_blacklist_page(pageindex)
                blist = PPDBlacklist.parse_blacklist(html, ppbaouserid)
                for ele in blist:
                    blacklist.append(ele)
        return blacklist;
    
    " Get Profits"
    def get_myprofit(self, date, ppbaouserid):
        profitm = re.search(self.pattern_profits, self.html_str)
        myprofit = MyProfit(date, ppbaouserid)
        if profitm is not None:
            realized, unrealized = profitm.groups()
            myprofit.set_profit(float(realized.replace(',', '')), float(unrealized.replace(',', '')))
            logging.info("Realized Profit: %6.2f - Unrealized: %6.2f" % (myprofit.realized_profits, myprofit.unrealized_profits))
        else:
            logging.error("Not Aable to get Profits!! Failed to parse BlackList Loan Page!!")
            exit (-1)
        blacklist_summarym = re.search(self.pattern_blacklist_summary, self.html_str)
        if blacklist_summarym is not None:
            num_of_bloan, yuqi, returned, toubiao = blacklist_summarym.groups()
            myprofit.set_blacklist(int(num_of_bloan), float(toubiao.replace(',','')), float(returned.replace(',', '')), float(yuqi.replace(',','')))
        else: 
            logging.warn("Not Aable to get Black Loan Summary!! Failed to parse BlackList Loan Page!! Assume NONE for now!")
        return myprofit
    
    @staticmethod
    def parse_blacklist(html, ppbaouserid):
        black_loans = re.findall(PPDBlacklist.blackloan_patter, html)
        black_loan_list = []
        for item in black_loans:
            userid, loanid, loan_title, overdued_money, returned_money, bidmoney, overdue_days, history_overdue_days = item
            blackloan = PPDBlackLoan()
            blackloan.bid_money = int(bidmoney)
            blackloan.history_max_overdue_days = int(history_overdue_days)
            blackloan.loanid = int(loanid)
            blackloan.loan_title = loan_title
            blackloan.loanuserid = userid
            blackloan.overdue_days = int(overdue_days)
            blackloan.returned_money = float(returned_money)
            blackloan.overdue_money = float(overdued_money)
            blackloan.ppbaouserid = ppbaouserid
            black_loan_list.append(blackloan)
            logging.info("Summary: " + blackloan.get_summary())
        logging.info("Find %d black loans" %(len(black_loan_list)))
        return black_loan_list


'''
# Pattern Sample
<tr>
                            <td><span class="c39a1ea dib">pdu3544614263</span>
                                <span listingid="8746447" listingtitle="pdu3544614263首次借款（wap专享）" class="my-hn-user showDetail">
                                    <em class="file_close" id="file_8746447"  style="display:none"></em>
                                </span>
                            </td>
                            <td>&#165;3.76 / &#165;0.00 / &#165;50.00</td>
                            <td><a href="javascript:void(0)" class="c39a1ea" onclick="openWindow(19672274) ">提供催收线索</a></td>
                            <td>1 天（0 天） </td>

                            <td>81%</td>
                            <td>

                                <span class="my-hn-mark" onclick="showDetail(19672274, 1, 8746447) "></span>


                            </td>
                        </tr>

'''  