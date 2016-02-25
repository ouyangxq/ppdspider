'''
Created on 20160220
A Interface Class for PPDai Spider
Define the common functions without implementation

@author: Administrator
'''

class PPD(object):
    '''
    classdocs
    '''
    name = None

    def __init__(self,name):
        '''
        Constructor
        '''
        self.name = name
    
    def get_db_insert_statement(self):
        return "TO be implemented in Sub-class"