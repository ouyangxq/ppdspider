#!python
#-*- coding: utf-8 -*-

'''
Created on 2016年2月27日

@author: Administrator
'''

import MySQLdb
import re
import traceback
from time import sleep

university_csv = "D:/ppdai/china_university2.csv"

def connect_to_db(hostname, username, pwd, database):
    dbconn = MySQLdb.connect(host=hostname, user=username, passwd=pwd, db=database,charset="utf8")
    if dbconn is not None:
        return dbconn
    else:
        print "Not Able to connect to DB!"
        return None

if __name__ == '__main__':
    dbconn = connect_to_db('localhost', 'xiaoqi', 'XiaoqiDB.1', 'ppdai')
    csvfh  = file(university_csv, 'r')
    firstline = csvfh.readline()
    for line in csvfh:
        #print line;
        rank, uname, score, utype, location, pici = re.split(',',line)
        if (re.match('\d+', rank)):
            rank  = int(rank)
            score = float(score)
            pici  = pici.strip().decode('gbk').encode('utf-8')
            uname = uname.decode('gbk').encode('utf-8')
            utype = utype.decode('gbk').encode('utf-8')
            location = location.decode('gbk').encode('utf-8')
            #uname = uname.encode('utf-8')
            #print "%d,%s,%4.2f,%s,%s,%s" % (order, uname, score, utype, location, pici)
            sqlstat = "insert into university (rank, name, score, type,location, pici) values " + \
                    "(%d, \"%s\", %5.2f, \"%s\", \"%s\", \"%s\")" % (rank, uname, score, utype, location, pici)
            try:
                dbconn.cursor().execute(sqlstat)
                dbconn.commit()
                print("Run: %s" % (sqlstat))
            except BaseException,e:
                print "Error: %r" % (e)
                traceback.print_exc()
                exit (-1)
            print sqlstat
            #sleep(1)
        else:
            print "NOt match!"
    csvfh.close()
    