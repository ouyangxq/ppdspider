#!python
#-*- coding:utf-8 -*-

'''
Created on 2016/02/11
@author: Xiaoqi Yang
'''


CERTIFICATE = ("education", "trust", "zhifubao", "student_card", "job_cert", "wangdian")

class LoanInfo(object):
    '''
    This is a class to represent the Loan Detailed information, includes:
    Basic Info: date, sex, age, marriage, education,house,car
    Third Party Certificated: education_cert, trust_cert
    PPDAI certificated: idcard, zhifubao, student_card,job
    classdocs
    '''
    date = None
    sex  = None
    age  = None
    marriage = None
    education = None
    house = None
    car   = None
    education_university = None
    education_level = None
    education_type = None
    trust_cert = None
    trust_cert_source = None
    idcard = None
    zhifubao = None
    student_card = None
    job_cert = None
    other_cert = []
    loan_hist = None # LoanHistory
    ppdrate = "DD"   #PPDai Rate AAA - D
    loanrate = None
    money = None
    loan_duration = None
    

    def __init__(self, params):
        '''
        Constructor
        '''
        self.date = params['date']
        self.sex  = params['sex']
        self.marriage = params['marriage']
        self.age = params['age']
        self.education = params['education']
        self.house = params['house']
        self.car = params['car']
    
    def add_education_cert (self, university, level, education_type):
        self.education_university = university
        self.education_level = level
        self.education_type  = education_type
        
    def add_cert(self,cert,cert_value):
        if cert in CERTIFICATE:
            if (cert == 'zhifubao'):
                self.zhifubao = True
            elif (cert == 'education_cert'):
                self.education_cert = True
                self.education_university = cert_value
            elif cert == 'trust_cert':
                self.trust_cert = True
                self.trust_cert_source = cert_value
            else:
                print "TO Be Added: %s" % (cert)
        else:
            self.other_cert.append(cert)
    
    def add_loan_hist(self,loan_hist):
        self.loan_hist = loan_hist
    
    @staticmethod
    def get_header_str(self):
        return "日期, 性别, 年龄 , 婚姻状况, 教育程度,房,车,历史还清次数,逾期15天内还清,逾期15以上,累计借入,未还金额,累计待收,毕业学校,学历,学习形式,魔镜等级,借款数量,借款利率,借款期限"
    
    def to_str(self):
        loanstr = "%s,%s,%s,%s,%s,%s,%s" % (self.date, self.sex, self.age, self.marriage, self.education, self.house, self.car)
        if (self.loan_hist != None):
            loanstr += "," + self.loan_hist.to_str()
        else:
            loanstr += ",,,,,,"
        if (self.education_university != None):
            loanstr += ",%s,%s,%s" %(self.education_university, self.education_level, self.education_type)
        else:
            loanstr += ",,,"
        if (self.ppdrate != None):
            loanstr += ",%s,%s,%s,%s" % (self.ppdrate, self.money, self.loanrate, self.loan_duration)
        else:
            loanstr += ",,,,"
        return loanstr
         
if __name__ == '__main__':
    
    loan_info = LoanInfo({"date":'20151230', 'sex':'男', 'age':'32', 'marriage':'是', 
                          'education':'本科','house':'是', 'car':'否'})
    loan_info.add_cert("zhifubao", None)
    loan_info.add_cert("education_cert","西安电子科技大学")
    loan_info.add_cert("trust_cert", "人行征信认证")
    print loan_info.to_str()