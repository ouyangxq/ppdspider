#!python
#-*- coding:utf-8 -*-

'''
Created on 2016年2月20日

@author: Administrator
'''
import MySQLdb
import logging

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
            logging.error("Not able to connect to MYSQL Database! Make sure MYSQL services are running!!")
            return False
    
    def disconnect(self):
        if self.dbconn != None:
            self.dbconn.close()
            
    def execute(self, sql_stat):
        if (self.dbconn == None):
            print "Error: NO DB Handler. Please call connect function first" 
            return False
        try:
            logging.info("DB Executing: %s" % (sql_stat))
            result = self.dbcursor.execute(sql_stat)
            if result:
                logging.info("DB Update Succeed.")
                self.dbconn.commit()
                return True
            else:
                logging.debug("Not Result for: %s" % (sql_stat))
                return False
        except MySQLdb.MySQLError, e:
            logging.error("Failed to execute: %s - %r" % (sql_stat, e))
            return False
            