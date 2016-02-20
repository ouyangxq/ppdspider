set names gbk;
create database ppdai;
use ppdai;

# A big table for all Loan related information
create table ppdloan (
     loanid integer not null primary key,
     date date not null,
     ppdrate char(3) not null,
     loanrate FLOAT(4,2) not null,
     money integer not null,
     maturity integer not null,
     userid char(15) not null,
     loantitle varchar(30),
     gender varchar(4) not null,
     age integer not null,
     history_return_ontime integer not null,
     history_overdue_in15d integer not null,
     history_overdue_mt15d integer not null,
     history_total_loan integer not null,
     history_left_loan double(10,2) not null,
     history_total_lend double(10,2) not null
);

create table ppduser (
     userid char(15) not null primary key,
     gender varchar(4) not null,
 	 age int not null,
     marriage varchar(4),
     house varchar(10),
     car varchar(5),
     education_level varchar(10),
     education_university varchar(20) DEFAULT NULL,
     education_type varchar(10) DEFAULT NULL,
	 ren_hang_trust_cert char(1) DEFAULT NULL,
	 idcard_cert char(1)  DEFAULT NULL,
	 hukou_cert char(1) DEFAULT NULL,
	 alipay_cert char(1) DEFAULT NULL,
	 job_cert char(1) DEFAULT NULL,
	 shebao_gjj_cert char(1) DEFAULT NULL,
	 bank_details_cert char(1) DEFAULT NULL,
	 taobao_seller_cert char(1) DEFAULT NULL,
	 relative_photo_cert char(1) DEFAULT NULL
)          
     

# My Bid records
# All loan related information are in ppdloan table
create table mybid (
	loanid integer not null primary key,
	date date not null,
	money integer not null,
	reason varchar(30)
);