'''
Created on 2016 May 20th

@author: Administrator
'''
import re
from datetime import date
import datetime
import logging
from datetime import timedelta

class PPBaoFollower(object):
    '''
    classdocs
    '''
    follow_users = ['kuku9991','pdu01242438', 'pdu2433714758', 'pdu01242438','jiangmg520','pdu3551882477','pdu4267041750', 'pdu1638762174']
    pattern_loanid = '<td><a  href="\/list\/(\d+)" target="_blank" class="c39a1ea"'
    pattern_latest_date = '<time datetime="(\d+)\/(\d+)\/(\d+) \d+:\d+:\d+" class="age">'
    referer_url  = "http://www.ppdai.com/account/lend"
    spider = None


    def __init__(self, spider):
        '''
        Constructor
        '''
        self.spider = spider
    
    def get_follow_users(self):
        return self.follow_users;
    
    def get_follow_user_url(self, userid):
        return "http://www.ppdai.com/user/%s" % (userid)
        
    def get_latest_loanid_list(self, userid):
        url = self.get_follow_user_url(userid)
        html = self.spider.open_page(url, self.referer_url)
        if (html is None):
            logging.error("Failed to get HTML source of user %s's bid" % (userid))
            return []
        loanids = re.findall(self.pattern_loanid, html)
        idlist = []
        for loanid in loanids:
            loanid = int(loanid)
            idlist.append(loanid)
        m = re.search(self.pattern_latest_date, html)
        if (m is not None):
            (year, month, day) = (int(m.group(1)), int(m.group(2)), int(m.group(3)))
            dt = datetime.date(year,month, day)
            today = date.today()
            two_days_ago = today + timedelta(days = -2)
            if (two_days_ago > dt):
                ''' Just return an empty list if the user has not bid for long time '''
                logging.info("CheckFollowers: Remove User(%s) from the list as last bid date is %s" % (userid, dt.isoformat()))
                self.follow_users.remove(userid)
                return []
        return idlist
        
        