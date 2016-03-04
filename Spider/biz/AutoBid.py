#-*- coding: utf-8 -*-
'''
Created on 20160221

@author: Administrator
'''
import urllib
import re
import logging

class AutoBid(object):
    '''
    Bid for good loans
    '''
    bid_response_pattern = re.compile('.*"ListingId":.*?"UrlReferrer":"1","Money":\d+,"Amount":(\d+),"', re.S)

    def __init__(self):
        '''
        Constructor
        '''
        pass
        
    def bid(self, opener, loanid, money, reason):
        '''
        bid for good loan
        '''
        logging.debug("Biding for Loanid %d with money %d. Reason: %s" %(loanid, money, reason))
        bid_info = {"Reason":'', "Amount":money, "ListingId":loanid, "UrlReferrer":"1", "SubListType":'0'}
        bid_post_data = urllib.urlencode(bid_info)
        bid_url = "http://invest.ppdai.com/Bid/Bid" 
        referer = "http://invest.ppdai.com/bid/info?source=2&listingId=%d" % (loanid) + '%20%20%20%20&title=&date=12%20%20%20%20&' + "UrlReferrer=1&money=%d" % (money)
        opener.addheaders.append(('Referer', referer))
        opener.addheaders.append(('Host','invest.ppdai.com'))
        opener.addheaders.append(('Origin','invest.ppdai.com'))
        opener.addheaders.append(('Accept','*/*'))
        opener.addheaders.append(('Connection','keep-alive'))
        opener.addheaders.append(('Cache-Control','max-age=0'))
        opener.addheaders.append(('User-Agent','Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.73 Safari/537.36'))
        response = opener.open(bid_url,bid_post_data)
        html_str = response.read()
        # Check html_str to see if it's good. 
        logging.info("Response:: %s" %(html_str))
        actual_mountm = re.search(self.bid_response_pattern, html_str)
        if actual_mountm is None:
            logging.warn("Bid Response Pattern is not matched. Check it")
            return -1
        else:
            actual = int(actual_mountm.group(1))
            logging.info("Actual Bid: %d" % (actual))
            return actual