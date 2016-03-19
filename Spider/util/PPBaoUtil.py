#-*- coding:utf-8 -*-
'''
Created on 2016年3月12日
A Class with some common utility functions
@author: Administrator
'''

import gzip
from StringIO import StringIO
import logging

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
    def set_university_to_rank(university_to_rank):
        PPBaoUtil.university_to_rank = university_to_rank
    
    @staticmethod
    def get_university_rank(ppdloan):
        # Only return Rank for those who have "Normal" Education Type
        # Notice this method shall only be called after set_univeristy_to_rank
        if (ppdloan.ppduser.education_university == 'NULL') or ppdloan.ppduser.education_type != '普通'  or ppdloan.ppduser.education_level == '专科':
            return -1
        university = ppdloan.ppduser.education_university
        university = unicode(university)
        if university in PPBaoUtil.university_to_rank.keys():
            return PPBaoUtil.university_to_rank[university]
        else:
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