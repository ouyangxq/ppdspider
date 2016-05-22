# coding: utf-8
'''

@author: Administrator
'''

#!D://python27/python

#------------------------------------------------
# Deng E Ben Xi Caculator
#
# Author: Xiaoqi Yang
# Date:   Jan 17, 2016
#------------------------------------------------

from sys import argv;
import sys;



class DKMonthlyPay(object):
    "Monthly Payment data structure"
    mid        = 0;
    mpay     = 0;
    benjin     = 0;
    lixi     = 0;
    left     = 0;
    def __init__(self, mid, mpay, benjin, lixi, left):
        self.mid = mid;
        self.mpay = mpay;
        self.benjin = benjin;
        self.lixi = lixi;
        self.left = left;
        
    def get_monthly_pay (self):
        return [self.mid, self.mpay, self.benjin, self.lixi, self.left];
    def get_monthly_pay_str(self):
        return "%d\t%6.4f\t%6.4f\t%6.4f\t%6.4f" % (self.mid, self.mpay, self.benjin, self.lixi, self.left);
        
class BestBidMoneyCalculator(object):
    "My First Class to try something practical"
    _money = 10000        # default money
    _mrate = 0.12        # Monthly Rate
    _month = 12            # Number of months
    _mpay  = 0.0            # monthly pay
    _results = []        # Result list of DKMonthlyPay
    _lixi_total = 0    # Total Lixi
    
    def __init__(self, money, mrate, month):
        self._money = money
        self._mrate = float(mrate/100)
        self._month = month
        self._results = []
        self._lixi_total = 0
    
    def get_monthly_pay(self):
        self._mpay  = (self._money * self._mrate * ((1+ self._mrate) ** self._month)) / ((1+ self._mrate) ** self._month - 1);
        return self._mpay
    
    def calc(self):
        self._mpay  = (self._money * self._mrate * ((1+ self._mrate) ** self._month)) / ((1+ self._mrate) ** self._month - 1);
        #print "(self._money * self._mrate * ((1+ self._mrate) ** self._month)) / ((1+ self._mrate) ** self._month - 1)"
        print "Monthy Pay: %6.4f" % (self._mpay)
        left_money = self._money;
        
        for i in range (self._month):
            lixi = left_money * self._mrate;
            self._lixi_total += lixi;
            benjin = self._mpay - lixi; 
            left_money = left_money * (1 + self._mrate) - self._mpay;
            dk_monthly_pay = DKMonthlyPay(i, self._mpay, benjin, lixi,left_money);
            self._results.append(dk_monthly_pay);

    def get_monthly_payment(self):
        return self._results;
    
    def get_total_lixi(self):
        return self._lixi_total;
    
def calc_debx(money, mrate, month):
    '1. Calculate X - monthly pay number'
    '2. Calculate monthly payment'
    '3. Return monthly payment + total Lixi'
    mpay = (money * mrate * ((1+ mrate) ** month)) / ((1+ mrate) ** month - 1);
    left_money = money;
    lixi_total = 0;
    res = [];

    for i in range (month):
        lixi = left_money * mrate;
        lixi_total += lixi;
        benjin = mpay - lixi; 
        left_money = left_money * (1 + mrate) - mpay;
        res.append("%d\t%6.4f\t%6.4f\t%6.4f\t%6.4f" % (i, mpay, benjin, lixi, left_money));
    return (res, lixi_total);

def get_monthly_pay(money, mrate, month):
    return (money * mrate * ((1+ mrate) ** month)) / ((1+ mrate) ** month - 1)
    

# MAIN FUNCTION
if __name__ == '__main__':
    #print "Rate,BidMoney,Month,MonthlyPay,JieDuan,Actual,BestBid"
    for rate in (16,):
        for month in (12,):
            for money in (50, 51, 52, 53,54, 55, 60, 65, 70,155, 160, 165, 170,240,250,260,270,300,320,330,340,350,360):
                best_bid = money
                best_jieduan = 0.01
                for rmoney in range(money, money+5):
                    monthly_pay = get_monthly_pay(rmoney, float(rate)/1200, month);
                    jieduan = (monthly_pay*10000 % 100) / 10000
                    if (jieduan < best_jieduan):
                        best_jieduan = jieduan
                        best_bid = rmoney
                print "%d,%d,%d,%4.4f" % (rate, month, best_bid, best_jieduan)
            '''
            best_bid_money_list = []
            
            for money in range(50, 80):
                " Need to divide by 1200 (12 * 100) to get the actual Rate"                
                monthly_pay = get_monthly_pay(money, float(rate)/1200, month);
                # Jie Duan - this is the money kept by PPDAI
                jieduan = (monthly_pay*10000 % 100) / 10000
                #bestbid = "YES" if (jieduan <= 0.001) else "NO"
                if jieduan <= 0.001:
                    best_bid_money_list.append((money,jieduan))
                #print "%d,%d,%d,%6.2f,%4.4f,%6.4f,%s" % (rate, money, month, monthly_pay,jieduan,monthly_pay,bestbid)
            for mj in best_bid_money_list:
                m, j = (mj[0], mj[1])
                print "%d,%d,%d,%4.4f" % (rate, month, m, j)
            
            '''
    
    # Monthly Rate
    money = 500
    rate = 0.11
    month = 12
    mrate = float(rate / 12);
    print "==== Calc using Func ===="
    print "No.\tMPay\tBenjin\tLixi\tLeft Benjin";
    res2, lixi_total2 = calc_debx(money, mrate, month);
    for r in res2:
        print r;
    print "\nTotal Lixi: %6.2f" % ( lixi_total2 );
    ''''
    print "\n==== Calc using Class ===="
    print "No.\tMPay\tBenjin\tLixi\tLeft Benjin";
    dkcalc = BestBidMoneyCalculator(money, mrate, month);
    dkcalc.calc();
    for mp in dkcalc.get_monthly_payment():
        print mp.get_monthly_pay_str();
    print "Total Lixi: %6.2f" % (dkcalc.get_total_lixi());
    '''
