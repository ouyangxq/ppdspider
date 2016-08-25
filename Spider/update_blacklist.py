# coding: utf-8
'''
Created on 2016年3月20日

@author: Administrator
'''

from ds.PPDBlackLoan import PPDBlackLoan
from spider.PPDBlacklist import PPDBlacklist
from sys import argv
import logging
from spider.PPDSpider import PPDSpider
from dao.PPDDAO import PPDDAO
from dao.PPBaoUserDAO import PPBaoUserDAO
from dao.BlackListDAO import BlackListDAO
from datetime import date
from datetime import timedelta
from util.PPBaoConfig import PPBaoConfig
from util.PPBaoUtil import PPBaoUtil

def init_ppbao(argv):

    ppbao_config_file = None
    if (len(argv) == 1):
        ppbao_config_file = "conf/ppbao.18616856236.config"
        ppbao_config_file = "conf/ppbao.18616027065.config"
    elif (len(argv) == 2):
        me,ppbao_config_file = argv
    else:
        print "Error: More than 1 argument is provided!"
        print "Usage: python update_blacklist.py <ppbao_config_file>"
        exit (-1)

    # Initialize
    ppbao_config = PPBaoConfig(ppbao_config_file)
    ppdloginid,dbhost,dbuser,dbpwd,dbname = ppbao_config.read_ppbao_config()
    PPBaoUtil.init_logging(ppdloginid,ppbao_config.logdir)
    logging.info("Welcome to PPBao System - Update BlackList Utility!")
    logging.info("Developed By Xiaoqi Ouyang. All Rights Reserved@2016-2017")
    logging.info("PPBao Config: %s,%s,%s,%s,%s" % (ppdloginid,dbhost,dbuser,dbpwd,dbname))

    # Init DB Modules
    ppddao = PPDDAO({'host':dbhost,'username':dbuser,'password':dbpwd,'database':dbname})
    dbok   = ppddao.connect()
    if dbok == False:
        logging.error("Error: Not able to connect to MySQL! Please Fix it. Exiting now")
        exit (1)
    
    ppbaouserdao = PPBaoUserDAO(ppddao)
    blacklistdao = BlackListDAO(ppddao)
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
    
    return (ppduserid, spider, blacklistdao)

''' This is just a utility, no many error handling. please watch out for the output for any exceptions! '''
if __name__ == '__main__':
    (ppduserid, spider, blacklistdao) = init_ppbao(argv)
    blacklist_worker = PPDBlacklist(spider)
    blacklists = blacklist_worker.get_blacklist(ppduserid)
    today = date.today()
    for blackloan in blacklists:
        if (isinstance(blackloan, PPDBlackLoan) is False):
            logging.error("Internal Error: Parameter is not with right type")
            logging.error(blackloan)
            exit (-1)
        blackloan.ppbaouserid = ppduserid
        # Set Date
        overdue_date = today + timedelta(days = (1-blackloan.overdue_days))
        blackloan.overdue_date = overdue_date;
        logging.info("Black List: " + blackloan.get_summary()) 
    blacklistdao.update_blacklist(ppduserid, blacklists)
    logging.info("All Blacklist Info have been updated/inserted into DB now!!")
    
    myprofit = blacklist_worker.get_myprofit(today, ppduserid)
    logging.info("Profits Summary:" + myprofit.get_summary())
    blacklistdao.update_myprofit(myprofit)
    logging.info("Profits Info has been updated into DB.")
    
    
    
        
        
