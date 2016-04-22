#-*- coding:utf-8 -*-
'''
Created on 2016年2月28日

@author: Administrator
'''

import unittest
from dao.PPDDAO import PPDDAO
from dao.UniversityDAO import UniversityDAO
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

class UniversityDAOTest(unittest.TestCase):
    '''
    classdocs
    '''

    def test_query_university_table(self):
        ppddao = PPDDAO({'host':'localhost','username':'xiaoqi','password':'XiaoqiDB.1','database':'ppdai'})
        ppddao.connect()
        university_to_rank = UniversityDAO(ppddao).get_university_ranks()
        ppddao.disconnect()
        self.assertTrue(university_to_rank is not None)
        
    def test_university_in_db(self):
        ppddao = PPDDAO({'host':'localhost','username':'xiaoqi','password':'XiaoqiDB.1','database':'ppdai'})
        ppddao.connect()
        university_to_rank = UniversityDAO(ppddao).get_university_ranks()
        ppddao.disconnect()
        university = '上海大学'
        #for char in university:
        #    print "%s" % (char)
        #univeristy = u"%s" %(university)
        #university = u"%s" %(university)
        print university
        find = 0
        for uni in university_to_rank:
            if uni == university:
                print "%s: %d - %s" % (uni, university_to_rank[uni], university)
                find = 1
        self.assertTrue(university in university_to_rank.keys())
        
        
        