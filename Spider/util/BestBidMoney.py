'''
Created on Apr 2nd, 2016

@author: Administrator
'''

class BestBidMoney(object):
    '''
    classdocs
    '''
    best_bid = {14: {6: [51, 57, 60, 68, 71, 77, 82], \
                     12:[54, 59, 64, 69, 74, 79, 84]}, \
                15: {6: [50, 55, 62, 67, 72, 77, 82], \
                     12:[50, 55, 60, 65, 70, 78, 80]}, \
                16: {6: [53, 58, 62, 69, 73, 78, 84], \
                     12:[50, 55, 60, 69, 70, 75, 83]}, \
                18: {6: [51, 58, 60, 67, 71, 78, 80, 87], \
                     12:[54, 55, 60, 66, 72, 78, 84, 85]}, \
                19: {6: [50, 55 ,60, 65, 70, 75, 80, 85], \
                     12:[52, 56, 61, 65, 70, 79, 84, 85]}, \
                20: {6: [54, 57, 63, 69, 74, 77, 83, 89], \
                     10:[54, 59, 64, 65, 74, 79, 82, 89], \
                     11:[50, 55, 60, 65, 70, 75, 80, 85], \
                     12:[50, 57, 61, 65, 73, 76, 80, 88]}, \
                21: {12:[52, 58, 62, 68, 74, 78, 84, 87]}, \
                22: {6: [52, 56, 60, 68, 72, 76, 80, 88], \
                     12:[53, 56, 64, 67, 70, 78, 81, 87]}, \
                23: {12:[54, 59, 64, 69, 74, 79, 81, 86]}}

    def __init__(self, params):
        '''
        Constructor
        '''
        pass
    
    @staticmethod
    def get_best_bid_money(loanrate, month, money_range_start, money_range_end):
        ''' 
        If exists a best bid in money range, return it
        else: return money_range_start
        '''
        # No check of money_range_start < money_range_end, but please do follow it!!
        if BestBidMoney.best_bid.has_key(loanrate):
            if BestBidMoney.best_bid[loanrate].has_key(month):
                best_bid_list = BestBidMoney.best_bid[loanrate][month]
                for money in best_bid_list:
                    if money >= money_range_start and money <= money_range_end:
                        return money
        # If No Matches, then return least money in the range
        return money_range_start