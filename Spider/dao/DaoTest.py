#!python
#-*- coding: utf-8 -*-
'''
Created on 2016年2月21日

@author: Administrator
'''
import unittest
from dao.PPDDAO import PPDDAO
from ds.PPDLoan import *
from ds.PPDUser import *
from dao.PPDLoanDAO import PPDLoanDAO
from dao.PPDUserDAO import PPDUserDAO
from datetime import date

class Test(unittest.TestCase):

    def test_db_connection(self):
        ppddao = PPDDAO({'host':'localhost','username':'xiaoqi','password':'XiaoqiDB.1','database':'ppdai'})
        dbok   = ppddao.connect()
        ppddao.disconnect()
        self.assertTrue(dbok, "Unable to connect to DB.")
    
    def test_insert_ppdloan(self):
        ppddao = PPDDAO({'host':'localhost','username':'xiaoqi','password':'XiaoqiDB.1','database':'ppdai'})
        ppddao.connect()
        ppdloan_dao = PPDLoanDAO(ppddao)
        today = date.today()
        ppdloan = PPDLoan({'loanid':8822451, 'date':today, 'loanrate':7.0, 'ppdrate':'AAA', \
                           'money':3000, 'maturity':12, 'userid':'pdu6310825153', 'age': 46})
        ppduser = PPDUser({'userid':'pdu6310825153', 'gender': '男', 'age': 46, 'marriage': '已婚', \
                           'house': '自住无按揭', 'car': '有', 'education_level': '本科'})
        ppdloan.set_ppduser(ppduser)
        ppdloan.set_history_info(1, 0, 0, 30000, 29419.12, 108230.77)
        result = ppdloan_dao.insert(ppdloan)
        ppddao.disconnect()
        self.assertFalse(result, "Insert Duplicate records. ")

    def test_fetch_loanids(self):
        ppddao = PPDDAO({'host':'localhost','username':'xiaoqi','password':'XiaoqiDB.1','database':'ppdai'})
        ppddao.connect()
        ppdloan_dao = PPDLoanDAO(ppddao)
        today = date.today()
        loanids = ppdloan_dao.get_loanids_by_date(today)
        print loanids;
        self.assertTrue(len(loanids)>=1)

    def test_insert_ppduser(self):
        ppddao = PPDDAO({'host':'localhost','username':'xiaoqi','password':'XiaoqiDB.1','database':'ppdai'})
        ppddao.connect()
        ppduser_dao = PPDUserDAO(ppddao)

        ppduser = PPDUser({'userid':'pdu6310825153', 'gender': '男', 'age': 46, 'marriage': '已婚', \
                           'house': '自住无按揭', 'car': '有', 'education_level': '本科'})
       
        result = ppduser_dao.insert_if_not_exists(ppduser)
        ppddao.disconnect()
        self.assertTrue(result, "Unable to Update ppduser table.")

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()