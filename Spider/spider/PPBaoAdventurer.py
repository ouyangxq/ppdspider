'''
Created on 2016 Jun 11th

@author: Xiaoqi Yang
'''

from datetime import datetime
from time import sleep
import logging
import random

class PPBaoAdventurer(object):
    '''
    This class is to explore the loan id(s) that's not published in the page list
    Main idea is to get the current list, and add by 1, check if it's a valid loan, 
    and then send it to check by bid strategies
    '''

    invalid_loanids = []
    under_evaluation_loanids = []
    max_explore = 600   # max explore loanid: start_loanid + X
    max_errors  = 10    #stop to explore more loanids if we encounter more than max_error
    spider      = None
    html_parser = None
    source      = 'PPBaoAdventurer'

    def __init__(self, spider, html_parser):
        '''
        Constructor
        '''
        self.spider = spider
        self.html_parser = html_parser
    
    def lets_adventure(self, loan_queue, start_loanid, loanids_in_memory):
        '''
        Let's Adventure ppdai loanid list that's not published!
        loanid_queue: Shared Queue for check_and_bid thread
        start_loanid: Start loanid to check
        loanids in memory: shared list with page_walker thread
        '''
        errors = 0
        curr_loanid = start_loanid
        stop_loanid = start_loanid + self.max_explore
        referer_url = "http://invest.ppdai.com/account/lend" # initial referer_url
        (new_loanids, under_evaluation_loanids, invalid_loanids) = (0, 0, 0)
        while (curr_loanid <= stop_loanid and errors <= self.max_errors):
            curr_loanid += 1
            if curr_loanid in self.invalid_loanids:
                pass
            elif curr_loanid in self.under_evaluation_loanids:
                pass
            elif curr_loanid in loanids_in_memory:
                pass
            else:
                loanid_url = self.spider.get_loanurl_by_loanid(curr_loanid)
                #logging.info("PPBaoAdventure: Open % to check..." %(curr_loanid))
                page_html = self.spider.open_page(loanid_url,referer_url)
                if (page_html == None):
                    errors += 1
                    sleep(random.randint(1,8))
                    continue
                referer_url = loanid_url
                loan_status = self.html_parser.get_loan_status(curr_loanid, page_html)
                if (loan_status == self.html_parser.status_completed):
                    logging.debug("PPBaoAdventure: Ignore %d as status is completed..." %(curr_loanid))
                elif (loan_status == self.html_parser.status_invalid):
                    self.invalid_loanids.append(curr_loanid)
                    logging.debug("PPBaoAdventure: Ignore %d as status is invalid..." %(curr_loanid))
                    invalid_loanids += 1
                    errors += 1
                elif (loan_status == self.html_parser.status_under_evaluation):
                    self.under_evaluation_loanids.append(curr_loanid)
                    logging.debug("PPBaoAdventure: Ignore %d as status is under_evaluated..." %(curr_loanid))
                    under_evaluation_loanids += 1
                    errors = 0              
                else:
                    new_loanids += 1
                    errors = 0
                    ppdrate = self.html_parser.get_loan_ppdrate(curr_loanid, page_html)
                    if ppdrate is None:
                        pass
                    elif ppdrate not in ['A', 'B', 'C', 'D', 'E']:
                        logging.debug("PPBaoAdventure: Ignore %d as ppd rate is %s" %(curr_loanid, ppdrate))
                    else:
                        logging.debug("PPBaoAdventure: Detected New Loan: %d (rate: %s)" % (curr_loanid, ppdrate))
                        ppdloan, ppduser, mymoney = self.html_parser.parse_loandetail_html(curr_loanid, datetime.now(), page_html)
                        if ppdloan == None:
                            if mymoney == None: # if it's -1,then it's just we're too slow as the loan is 100% completed, no error.
                                logging.error("PPBaoAdventurer: Not able to parse  HTML to get ppdloan for %d!" % (curr_loanid))
                        else:
                            ppdloan.set_source(self.source)
                            loanids_in_memory.append(curr_loanid)
                            loan_queue.put(ppdloan)                        
                sleep(random.randint(1,8))        
                                
        return (curr_loanid, new_loanids, under_evaluation_loanids, invalid_loanids)
        