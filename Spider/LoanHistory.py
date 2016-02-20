#!python
#-*- encoding: utf-8 -*-
'''
Created on Feb 12, 2012

@author: Xiaoqi Yang
'''

class LoanHistory(object):
    '''
    A class to describe Loan History
    TimesPayBackOnTime, TimesPayBackL15Days, TimesPayBackMT15Days
    TotalLoan, LeftLoan, TotalLend
    Last Loan Info: Money, Rate, Status, Date
    '''
    TimesPayBackOnTime = TimesPayBackL15Days = TimesPayBackMT15Days = -1
    TotalLoan = LeftLoan = TotalLend = 0

    def __init__(self, TimesPayBackOnTime, TimesPayBackL15Days, TimesPayBackMT15Days, TotalLoan, LeftLoan, TotalLend):
        '''
        Constructor
        '''
        self.TimesPayBackOnTime = TimesPayBackOnTime
        self.TimesPayBackL15Days = TimesPayBackL15Days
        self.TimesPayBackMT15Days = TimesPayBackMT15Days
        self.TotalLoan = TotalLoan
        self.TotalLend = TotalLend
        self.LeftLoan  = LeftLoan
    
    def to_str(self):
        s = "%d,%d,%d,%6.2f,%6.2f,%6.2f" % (self.TimesPayBackOnTime, self.TimesPayBackL15Days, self.TimesPayBackMT15Days, 
                                   self.TotalLoan, self.LeftLoan, self.TotalLend)
        return s
    

if __name__ == '__main__':
    gbkstring = '''
 <h3>拍拍贷统计信息</h3>
                        <p>历史统计</p>
                        <p>正常还清：62 次，逾期还清(1-15)：0 次，逾期还清(>15)：0 次 </p>
                        <p>
                            共计借入：<span class="orange">&#165;354,929</span>，
                            待还金额：<span class="orange">&#165;207,453.96</span>，
                            待收金额： <span class="orange">
&#165;357,804.52                            </span>
                        </p>
'''

    import re
    pattern = re.compile('<h3>拍拍贷统计信息</h3>.*?<p>历史统计</p>.*?<p>正常还清：(\d+).*?次，逾期还清\(1-15\)：(\d+).*?次，逾期还清\(>15\)：(\d+).*次 </p>' +
                      '.*?共计借入：<span class="orange">&#165;(\S+)</span>.*?待还金额：<span class="orange">&#165;(\S+)</span>' + 
                     '.*?待收金额： <span class="orange">.*?&#165;(\S+).*?</span>.*?</p>', re.S)

    items = re.findall(pattern, gbkstring)
    if items != None and len(items) > 0:
        for item in items:
            loan_hist = LoanHistory(int(item[0]), int(item[1]), int(item[2]), 
                                    float(item[3].replace(',','')),float(item[4].replace(',','')), float(item[5].replace(',','')))
            print loan_hist.to_str()
    else:
        print "No Match!"