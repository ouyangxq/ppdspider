'''
@author: Xiaoqi Yang
'''

import urllib
import urllib2
import re
import cookielib
from datetime import date
from time import sleep
from LoanInfo import LoanInfo
from LoanHistory import LoanHistory
from spider.PPDSpider import PPDSpider



if __name__ == '__main__':
    loanid = '8672508'
    money = '50'
    spider = PPDSpider()
    opener = spider.login('18616856236', 'Oyxq270')
    #"text": "Reason=&Amount=50&ListingId=8726000&UrlReferrer=1&SubListType=0",
    bid_info = {"Reason":'', "Amount":money, "ListingId":loanid, "UrlReferrer":"1", "SubListType":'0'}
    bid_post_data = urllib.urlencode(bid_info)
    bid_url = "http://invest.ppdai.com/Bid/Bid" 
    opener.addheaders = [('Referer', 'http://invest.ppdai.com/bid/info?source=2&listingId='+loanid+'%20%20%20%20&title=&date=12%20%20%20%20&UrlReferrer=1&money=' + money)]
    response = opener.open(bid_url,bid_post_data)
    html_str = response.read()
    print html_str