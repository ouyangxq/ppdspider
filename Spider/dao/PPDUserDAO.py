#!python
#-*- coding:utf-8 -*-
'''
Created on 2016年2月20日

@author: Administrator
'''
import logging

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
        if self.if_a_new_user(ppduser.userid):
            db_stat = ppduser.get_db_insert_statement()
            logging.info("Adding a new user to DB: %s" %(ppduser.userid))
            result  = self.dao.execute(db_stat)
            return result
        else:
            return True
    
    def if_a_new_user(self,userid):
        db_stat = "select userid from ppduser where userid=\"%s\"" % (userid)
        result  = self.dao.dbcursor.execute(db_stat)  # If in, return True, else, False
        # If result ==1, then this user is already exists. 
        if (result == 1):
            return False
        else:
            return True