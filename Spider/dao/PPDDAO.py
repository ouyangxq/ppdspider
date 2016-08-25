#!python
#-*- coding:utf-8 -*-

'''
Created on 2016年2月20日

@author: Administrator
'''
import MySQLdb
import logging
import re

class PPDDAO(object):
    '''
    classdocs
    '''
    host = 'localhost'
    username = 'NA'
    password = 'NA'
    database = 'NA'
    dbconn = None
    dbcursor = None
    

    def __init__(self, params):
        '''
        Constructor
        '''
        self.host = params['host']
        self.username = params['username']
        self.password = params['password']
        self.database = params['database']
    
    def connect(self):
        try:
            self.dbconn = MySQLdb.connect(host=self.host, user=self.username, passwd=self.password, \
                                          db=self.database,charset="utf8")
            self.dbcursor = self.dbconn.cursor()
            return True
        except:
            logging.error("Not able to connect to MYSQL Database! Make sure MYSQL service is running!!")
            return False
    
    def disconnect(self):
        if self.dbconn != None:
            self.dbconn.close()
            
    def execute(self, sql_stat):
        if (self.dbconn == None):
            logging.error( "Error: NO DB Handler. Please call connect function first") 
            return False
        try:            
            result = self.dbcursor.execute(sql_stat)
            if result:
                logging.debug("DB Execution Succeed: %s" % (sql_stat))
                self.dbconn.commit()
                return True
            else:
                logging.debug("DB Execution-No Result for: %s" % (sql_stat))
                return False
        except MySQLdb.MySQLError, e:
            error_msg = "%r" % (e)
            logging.error("Failed to execute: %s - %s" % (sql_stat, error_msg))
            if (re.match("OperationalError(2006",error_msg)):
                logging.warn("Reconnecting to MySQL...")
                self.connect()
                result = self.dbcursor.execute(sql_stat)
                if result:
                    logging.debug("DB Execution Succeed: %s" % (sql_stat))
                    self.dbconn.commit()
                    return True
                else:
                    logging.debug("DB Execution-No Result for: %s" % (sql_stat))
                    return False
            return False
            