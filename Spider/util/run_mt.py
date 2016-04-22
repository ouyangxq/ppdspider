'''
Created on 2016 Apr 6th

@author: Administrator
'''

import threading
from sys import argv
import logging
from spider.PPDSpider import PPDSpider
from dao.PPDDAO import PPDDAO
from dao.PPBaoUserDAO import PPBaoUserDAO
from dao.BlackListDAO import BlackListDAO
from datetime import date
from datetime import timedelta
from time import sleep
from util.PPBaoConfig import PPBaoConfig
from util.PPBaoUtil import PPBaoUtil

def init_dao(dbhost, dbuser, dbpwd, dbname):
        # Init DB Modules
    ppddao = PPDDAO({'host':dbhost,'username':dbuser,'password':dbpwd,'database':dbname})
    dbok   = ppddao.connect()
    if dbok == False:
        logging.error("Error: Not able to connect to MySQL! Please Fix it. Exiting now")
        exit (1)
    ppbaouserdao = PPBaoUserDAO(ppddao)
    return (ppddao, ppbaouserdao)

def init_ppbao(ppbao_config_file, ppbaouserdao):
    # Initialize
    ppbao_config = PPBaoConfig(ppbao_config_file)
    ppdloginid,dbhost,dbuser,dbpwd,dbname = ppbao_config.read_ppbao_config()
    PPBaoUtil.init_logging(ppdloginid,ppbao_config.logdir)
    logging.info("Welcome to PPBao System - Update BlackList Utility!")
    logging.info("Developed By Xiaoqi Ouyang. All Rights Reserved@2016-2017")
    logging.info("PPBao Config: %s,%s,%s,%s,%s" % (ppdloginid,dbhost,dbuser,dbpwd,dbname))

    (ppduserid_db,ppdpasswd) = ppbaouserdao.get_ppduserid_and_passwd(ppdloginid)
    if (ppduserid_db is None or ppdpasswd is None):
        logging.error("Error: Not able to get PPDAI loginid/passwd for %s. Invalid PPBao User!! Exiting!" %(ppdloginid))
        exit (2)

    # Login to PPDAI!
    spider = PPDSpider(ppdloginid, ppbao_config)
    (opener, ppduserid) = spider.login(ppdloginid, ppdpasswd) 
    if (ppduserid == None or ppduserid != ppduserid_db):
        logging.error("Error: Not able to get PPDAI Username or is not consistent with that in DB! Exit...")
        exit(4)
    
    return (ppduserid, spider)

def open_blacklist_page(opener, page):
    if (page == 1):
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
            opener = PPBaoUtil.add_headers(opener, headers)
            response = opener.open(url,None,15)
            html_str = PPBaoUtil.get_html_from_response(response)
            response.close()
            return html_str;
        except Exception,e:
            logging.error("On OpenPage - Caught Exception %r" %(e))
            return None
    else:
        print "Not supported for test"

if __name__ == '__main__':
    ppbao_config = PPBaoConfig("../conf/ppbao.me.config")
    ppdloginid,dbhost,dbuser,dbpwd,dbname = ppbao_config.read_ppbao_config()
    PPBaoUtil.init_logging(ppdloginid,ppbao_config.logdir)
    ppddao, ppbaouserdao = init_dao(dbhost,dbuser,dbpwd,dbname)
    spiders = []
    for conf in ('18616856236', '18616027065'):
        file = "../conf/ppbao.%s.config" % (conf)
        print "File: %s" % (file)
        ppduserid, spider = init_ppbao(file, ppbaouserdao)
        spiders.append(spider)
        sleep(5)
    
    for spider in spiders:
        logging.info("Opened HTML for ....")
        html = open_blacklist_page(spider.opener, 1)

        logging.debug(html)
        sleep (5)
    