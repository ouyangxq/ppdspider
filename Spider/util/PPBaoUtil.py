#-*- coding:utf-8 -*-
'''
Created on 2016年3月12日
A Class with some common utility functions
@author: Administrator
'''

import gzip
from StringIO import StringIO
import logging
import re
from datetime import date
import os

class PPBaoUtil(object):
    '''
    classdocs
    '''

    university_to_rank = None
    
    def __init__(self, params):
        '''
        Constructor
        '''
        pass
    
    @staticmethod
    def init_logging(ppdid, logdir):
        today = date.today().isoformat()
        logfile = "%s/ppbao.%s.%s.log" % (logdir, ppdid, today)
        i = 1
        while os.path.exists(logfile):
            logfile = "%s/ppbao.%s.%s.%d.log" % (logdir, ppdid, today, i)
            i += 1
        logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename=logfile,
                    filemode='a')
        #定义一个StreamHandler，将INFO级别或更高的日志信息打印到标准错误，并将其添加到当前的日志处理对象#
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        
        formatter = logging.Formatter('%(asctime)s %(levelname)-4s %(message)s')
        console.setFormatter(formatter)
        logging.getLogger('').addHandler(console)
    
    @staticmethod
    def set_university_to_rank(university_to_rank):
        PPBaoUtil.university_to_rank = university_to_rank
    
    @staticmethod
    def get_university_rank(ppduser):
        # Only return Rank for those who have "Normal" Education Type
        # Notice this method shall only be called after set_univeristy_to_rank
        if (ppduser.education_university == 'NULL'):
            return -2 # None
        elif (ppduser.education_type != u'普通' and ppduser.education_type != u'研究生' and ppduser.education_type != u''):
            return -3 # means 夜大，函授，自考，成人
        elif ppduser.education_level == u'专科' or ppduser.education_level == u'专科(高职)':
            return -1 # 专科
        university = ppduser.education_university
        university = unicode(university)
        if university in PPBaoUtil.university_to_rank.keys():
            return PPBaoUtil.university_to_rank[university]
        else:
            ''' 20160322: Treat 独立学院  和 大学一样，收费更高，学生更有钱！！群里普遍反应逾期反而更少！！'''
            ''' As university is unicoded, so need to match with u"" pattern as well!! '''
            m = re.match(u"(\S+(大学|学院))\S+(学院|分校)", university)
            if (m is not None):
                uni = m.group(1)
                if uni in PPBaoUtil.university_to_rank.keys():
                    rank = PPBaoUtil.university_to_rank[uni]
                    ''' 20160324: Limit this to top 10 university as  they have very high quality independent college '''  
                    if rank <= 3:
                        return rank;
                    elif rank < 50:
                        ''' 20160502: Treat Independent Colleage as University Rank 120 for rank<50 universities '''
                        return 120
                    else:
                        #logging.debug("Ignore Independent College for now as it's not top 10: %s,Rank %d" % (university, rank))
                        pass
            # For all other cases. return -1
            return -1
    
    @staticmethod
    def get_html_from_response(response):
        info = response.info()
        html = response.read()
        if info.get('Content-Encoding') == 'gzip':
            buf = StringIO(html)
            f = gzip.GzipFile(fileobj=buf)
            return f.read()
        else:
            return html
    
    @staticmethod    
    def print_cookie(cookie):
        for ck in cookie:
            logging.info("Cookie:: %s=%s" %(ck.name,ck.value)) 
    
    @staticmethod
    def add_headers(opener, header_hash):
        opener.addheaders = [('User-agent', 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.73 Safari/537.36')]
        for header in header_hash:
            opener.addheaders.append((header, header_hash[header]))
        return opener