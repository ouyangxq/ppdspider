# coding: utf-8
'''
Created on 2016年3月23日

@author: Administrator
'''
import unittest
import logging
from sys import argv
from util.PPBaoConfig import PPBaoConfig
from biz.BidStrategyPlus import BidStrategyPlus

def init_logging(ppdid):
    from datetime import date
    import os
    today = date.today().isoformat()
    logfile = "D:/ppdai/ppbao.%s.%s.log" % (ppdid, today)
    i = 1
    while os.path.exists(logfile):
        logfile = "D:/ppdai/ppbao.%s.%s.%d.log" % (ppdid, today, i)
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

class TestBidStrategyPlus(unittest.TestCase):

    def testName(self):

        ppbao_config_file = "../conf/ppbao.me.config"
        # Initialize
        ppbao_config = PPBaoConfig(ppbao_config_file)
        ppdloginid,dbhost,dbuser,dbpwd,dbname = ppbao_config.read_ppbao_config()
        init_logging(ppdloginid)
        ppbao_config.print_strategies()
        bsp = BidStrategyPlus(ppbao_config)
        
        # Init DB Modules
        from dao.PPDDAO import PPDDAO
        from dao.UniversityDAO import UniversityDAO
        from util.PPBaoUtil import PPBaoUtil
        ppddao = PPDDAO({'host':dbhost,'username':dbuser,'password':dbpwd,'database':dbname})
        dbok   = ppddao.connect()
        if dbok == False:
            logging.error("Error: Not able to connect to MySQL! Please Fix it. Exiting now")
            exit (1)
        university_to_rank = UniversityDAO(ppddao).get_university_ranks()
        if university_to_rank is None:
            logging.error("Error: Not able to query DB to get University Information. Exiting now")
            exit (3)
        else:
            PPBaoUtil.set_university_to_rank(university_to_rank)
        
        " Build Test PPDLoan and PPDUser instance"
        from ds.PPDLoan import PPDLoan
        from ds.PPDUser import PPDUser
        from datetime import datetime
        now = datetime.now()
        loanid = '1111111'
        ppdloan = PPDLoan({'loanid':1111111, 'datetime':now, 'loanrate':22, 'ppdrate':'C', \
                           'money':5000, 'maturity':12, 'userid':'pdu2517233537', 'age': 31})
        ppduser = PPDUser({'userid':'pdu2517233537', 'gender': '男', 'age': 31, 'marriage': '已婚', \
                               'house': '有', 'car': '无', 'education_level': '本科'}) 
        ppdloan.set_ppduser(ppduser)
        ppdloan.set_history_info(8,0,0,12000,3000,0)
        ppdloan.history_highest_total_loan = 12000
        
        ppdloan.loantitle = "NA-Test"
        ppduser.add_education_cert('保定学院', '本科', '普通')
        logging.info(ppdloan.get_loan_summary())
        ifbid, money, reason = bsp.check_by_strategy(ppdloan)
        self.assertTrue(ifbid, "No Bid for master??")


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
    
    ''' Test - Shall Put into a separate Test file '''             