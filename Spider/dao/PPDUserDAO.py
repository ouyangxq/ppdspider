#!python
#-*- coding:utf-8 -*-
'''
Created on 2016年2月20日

@author: Administrator
'''
import logging
from ds.PPDUser import PPDUser
from dao.PPDDAO import PPDDAO

class PPDUserDAO(object):
    '''
    classdocs
    '''

    dao = None

    def __init__(self, ppddao):
        '''
        Constructor
        '''
        self.dao = ppddao
        
    def insert_if_not_exists(self, ppduser):
        """ Use Replace so as always to keep the user certificates Up to date"""
        db_stat = ppduser.get_db_insert_statement()
        #logging.info("Adding a new user to DB: %s" %(ppduser.userid))
        result  = self.dao.execute(db_stat)
        return result

    
    def if_a_new_user(self,userid):
        db_stat = "select userid from ppduser where userid=\"%s\"" % (userid)
        result  = self.dao.dbcursor.execute(db_stat)  # If in, return True, else, False
        # If result ==1, then this user is already exists. 
        if (result == 1):
            return False
        else:
            return True
    
    # This is for testing bid strategy with existing DB PPDUsers
    def get_db_ppduser_by_userid(self, userid):
        db_stat = "select * from ppduser where userid=\"%s\"" % (userid)
        if (self.dao.execute(db_stat)):
            data = self.dao.dbcursor.fetchall()
            results = data[0]
            return self.parse_ppduser_db_row(results)
        else:
            logging.error("No PPDUser exists in DB with Name:", userid)
            return None
    
    def parse_ppduser_db_row(self, row_data):
        results = row_data
        ppduser = PPDUser({'userid': results[0], 'gender': results[1], 'age': int(results[2]), 'marriage': results[3], \
                    'house': results[4], 'car': results[5], 'education_level': results[6]}) 
        ppduser.add_education_cert(results[7], results[6], results[8])
        ppduser.ren_hang_trust_cert = results[9]
        ppduser.idcard_cert = results[10]
        ppduser.hukou_cert = results[11]
        ppduser.alipay_cert = results[12]
        ppduser.job_cert = results[13]
        ppduser.shebao_gjj_cert = results[14]
        ppduser.bank_details_cert = results[15]
        ppduser.taobao_seller_cert = results[16]
        ppduser.relative_cert = results[17]
        ppduser.shouru_cert = results[18]
        ppduser.getihu_cert = results[19]
        ppduser.mobile_cert = results[20]            
        ppduser.driver_cert = results[21]
        ppduser.student_cert = results[22]
        return ppduser
    
    def get_all_ppdusers(self):
        db_stat = "select * from ppduser"
        ppduser_hash = {}
        if (self.dao.execute(db_stat)):
            data = self.dao.dbcursor.fetchall()
            for results in data:
                ppduser_hash[results[0]] = self.parse_ppduser_db_row(results)
            return ppduser_hash
        else:
            logging.error("Not able to get PPDUsers")
            return None
    
        
if __name__ == '__main__':

    from dao.UniversityDAO import UniversityDAO
    from util.PPBaoUtil import PPBaoUtil
    ppddao = PPDDAO({'host':'localhost','username':'xiaoqi','password':'XiaoqiDB.1','database':'ppdai'})
    ppddao.connect()
    ppduserdao = PPDUserDAO(ppddao)
    unidao = UniversityDAO(ppddao)
    PPBaoUtil.set_university_to_rank(unidao.get_university_ranks())
    ppduser = ppduserdao.get_db_ppduser_by_userid('pdu26068827');
    print ppduser.to_string()
    ppddao.disconnect()
    
            