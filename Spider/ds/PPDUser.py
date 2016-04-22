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
        db_stat = "insert into ppduser values (\"%s\",\"%s\",%d,\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d)" \
                        % (self.userid, self.gender, self.age, self.marriage, self.house,self.car,self.education_level, \
                          self.education_university, self.education_type, self.ren_hang_trust_cert, self.idcard_cert, \
                          self.hukou_cert, self.alipay_cert, self.job_cert, self.shebao_gjj_cert, self.bank_details_cert, \
                          self.taobao_seller_cert, self.relative_cert, self.shouru_cert, self.getihu_cert)
        return db_stat
        