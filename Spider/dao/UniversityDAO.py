'''
Created on 2016 Feb 27

@author: Administrator
'''
import logging
import traceback

class UniversityDAO(object):
    '''
    classdocs
    '''
    dao = None

    def __init__(self, dao):
        '''
        Constructor
        '''
        self.dao = dao
        
    def get_university_ranks (self):
        ''' 
        Get a Dictionary of University -> Rank
        Then anything not in Dictionary are not going to be considered from Educational perspective
        '''
        sqlstat = "select name,rank from university"
        university_to_rank = {}
        try:
            result = self.dao.execute(sqlstat);
            if result == False:
                logging.warn("Not Able to query DB to get university Rnaks.: No Result!!!")
                return None
            data = self.dao.dbcursor.fetchall()
            for item in data:
                university = item[0]
                rank       = int(item[1])
                university_to_rank[university] = rank  
            return university_to_rank
        except Exception, e:
            traceback.print_exc()
            logging.error("Caught Exception: %r" %(e))
            return None
    