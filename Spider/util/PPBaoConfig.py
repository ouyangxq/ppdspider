# coding: utf-8
'''
Created on 2016 Mar 21st

@author: Administrator
'''

import re
from sys import argv

class PPBaoConfig(object):
    '''
    classdocs
    '''
    strategy_ppdrate_list = []
    strategy_loanrate_list = []
    bid_strategy_strlist = []
    bid_strategy_hash    = {}
    ppdloginid = None
    dbhost = None
    dbuser = None
    dbpwd = None
    dbname = None
    logdir = None
    ppbao_config = None

    def __init__(self, config):
        '''
        Constructor
        '''
        self.strategy_ppdrate_list = []
        self.strategy_loanrate_list = []
        self.bid_strategy_strlist = []
        self.bid_strategy_hash = {}
        self.ppdloginid = None
        self.ppbao_config = config
        
    
    def read_ppbao_config(self):
        try:
            fh = file(self.ppbao_config,'r')
            for line in fh:
                line = line.rstrip()
                if(re.match('#', line) or re.match('^\s*$', line)):
                    # This is a comment line, ignore. 
                    continue
                item,value = re.split('=', line, maxsplit=2)
                if (item == 'PPDUser'):
                    self.ppdloginid = value
                elif (item == 'PPBao_DBHost'):
                    self.dbhost = value
                elif (item == 'PPBao_DBUser'):
                    self.dbuser = value
                elif (item == 'PPBao_DBPassword'):
                    self.dbpwd = value
                elif (item == 'PPBAO_DBName'):
                    self.dbname = value
                elif (item == 'Logdir'):
                    self.logdir = value
                elif (item == 'Strategy_PPDRate'):
                    self.strategy_ppdrate_list = re.split(',', value);
                elif (item == 'Strategies'):
                    # XXX: TO be implemented.
                    pass
                elif (item == 'Strategy_LoanRate'):
                    self.strategy_loanrate_list = re.split(',', value)
                elif (re.match('S\d', item) or re.match("\S+Strategy", item)):
                    self.bid_strategy_strlist.append(value)
                    self.bid_strategy_hash[item] = value
                else:
                    print "Unrecognized/Ignored Config item: %s=%s" % (item, value)
            return (self.ppdloginid,self.dbhost,self.dbuser,self.dbpwd,self.dbname)
        except IOError, e:
            print "Not able to parse PPBao Config file: %r" % (e)
            return None
    
    def print_strategies(self):
        for strategy in self.bid_strategy_strlist:
            print "Strategy in PPBaoConfig: " + strategy.decode('gbk').encode('utf-8')

if __name__ == '__main__':
    ppbao_config_file = None
    
    if (len(argv) == 1):
        ppbao_config_file = "../conf/ppbao.me.config"
    elif (len(argv) == 2):
        me,ppbao_config_file = argv
    else:
        print "Error: More than 1 argument is provided!"
        print "Usage: python PPBao.py <ppbao_config_file>"
        exit (-1)

    # Initialize
    ppbao_config = PPBaoConfig(ppbao_config_file)
    ppdloginid,dbhost,dbuser,dbpwd,dbname = ppbao_config.read_ppbao_config()
    ppbao_config.print_strategies()