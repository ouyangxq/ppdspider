# coding: utf-8
'''
Created on 20160220
PPDUser Module
@author: Administrator
'''

from PPD import PPD

userTableDef = '''
     userid char(15) not null primary key,
     gender varchar(4) not null,
     age int not null,
     marriage varchar(4),
     house varchar(10),
     car varchar(5),
     education_level varchar(10),
     education_university varchar(20) DEFAULT NULL,
     education_type varchar(10) DEFAULT NULL,
     ren_hang_trust_cert BOOLEAN DEFAULT FALSE,
     idcard_cert BOOLEAN DEFAULT FALSE,
     hukou_cert BOOLEAN DEFAULT FALSE,
     alipay_cert BOOLEAN DEFAULT FALSE,
     job_cert BOOLEAN DEFAULT FALSE,
     shebao_gjj_cert BOOLEAN DEFAULT FALSE,
     bank_details_cert BOOLEAN DEFAULT FALSE,
     taobao_seller_cert BOOLEAN DEFAULT FALSE,
     relative_cert BOOLEAN DEFAULT FALSE,
     shouru_cert BOOLEAN DEFAULT FALSE
'''

class PPDUser(PPD):
    '''
    classdocs
    '''
    userid = 'NA'
    gender = None
    age    = -1
    marriage = None
    house  = None
    car    = None
    education_level    = None
    education_university = 'NULL'
    education_type     = 'NULL'
    ren_hang_trust_cert    = 0
    idcard_cert        = 0
    hukou_cert         = 0
    alipay_cert        = 0
    job_cert           = 0
    shebao_gjj_cert    = 0
    bank_details_cert  = 0
    taobao_seller_cert = 0
    relative_cert      = 0
    shouru_cert        = 0
    getihu_cert        = 0
    student_cert       = 0
    driver_cert        = 0
    mobile_cert        = 0
    video_cert         = 0

    def __init__(self, params):
        '''
        Constructor
        '''
        PPD.__init__(self, 'ppduser')
        self.userid = params['userid']
        self.gender = params['gender']
        self.age    = params['age']
        self.marriage = params['marriage']
        self.house  = params['house']
        self.car    = params['car']
        self.education_level    = params['education_level']
         
    def add_education_cert(self, university,education_level, education_type):
        self.education_university = unicode(university)
        self.education_level      = education_level
        self.education_type       = education_type
    
    def get_db_insert_statement(self):
        db_stat = "REPLACE into ppduser values (\"%s\",\"%s\",%d,\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d)" \
                        % (self.userid, self.gender, self.age, self.marriage, self.house,self.car,self.education_level, \
                          self.education_university, self.education_type, self.ren_hang_trust_cert, self.idcard_cert, \
                          self.hukou_cert, self.alipay_cert, self.job_cert, self.shebao_gjj_cert, self.bank_details_cert, \
                          self.taobao_seller_cert, self.relative_cert, self.shouru_cert, self.getihu_cert, self.mobile_cert, self.driver_cert,self.student_cert)
        return db_stat
    
    def to_string(self):
        from util.PPBaoUtil import PPBaoUtil
        rank = PPBaoUtil.get_university_rank(self)
        summary = "Edu(%s,%s,%s,%d),%s" \
            % (self.education_university, \
               self.education_level, self.education_type, rank, self.gender)
        certs = None
        if self.getihu_cert == 1:
            certs = ",Cert(个体户" if certs is None else (certs + ",个体户")
        if self.bank_details_cert == 1:
            certs = ",Cert(银行流水" if certs is None else (certs + ",银行流水")
        if self.job_cert == 1:
            certs = ",Cert(工作" if certs is None else (certs + ",工作")
        if self.ren_hang_trust_cert == 1:
            certs = ",Cert(征信" if certs is None else (certs + ",征信")
        if self.shouru_cert == 1:
            certs = ",Cert(收入" if certs is None else (certs + ",收入")
        if self.alipay_cert == 1:
            certs = ",Cert(支付宝" if certs is None else (certs + ",支付宝")
        if self.student_cert == 1:
            certs = ",Cert(学生证" if certs is None else (certs + ",学生证")
        if self.shebao_gjj_cert == 1:
            certs = ",Cert(社保" if certs is None else (certs + ",社保")
        if self.driver_cert == 1:
            certs = ",Cert(驾驶证" if certs is None else (certs + ",驾驶证")
        if self.hukou_cert == 1:
            certs = ",Cert(户口" if certs is None else (certs + ",户口")
        certs = ",Cert(NA)" if certs is None else (certs + ")")
        summary += certs
        return summary  