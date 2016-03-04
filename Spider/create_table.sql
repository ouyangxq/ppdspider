set names gbk;
create database ppdai;
use ppdai;

# for all Loan related information
create table ppdloan (
     loanid integer not null primary key,
     date date not null,
     ppdrate char(3) not null,
     loanrate FLOAT(4,2) not null,
     money integer not null,
     maturity integer not null,
     userid char(15) not null,
     loantitle varchar(30),
     age integer not null,
     history_return_ontime integer not null,
     history_overdue_in15d integer not null,
     history_overdue_mt15d integer not null,
     history_total_loan integer not null,
     history_left_loan double(10,2) not null,
     history_left_lend double(10,2) not null
);
alter table ppdloan add column datetime datetime not null;

# User information
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
)          
# Test
insert into ppduser values ('pdu2517', 'male', 34, 'married', 'yes', 'no', 'master', 'xidian', 'normal', 0, 1, 0, 0,0,0,0,0,0)     

# My Bid records
# All loan related information are in ppdloan table
create table mybid (
	loanid integer not null primary key,
	date date not null,
	money integer not null,
	reason varchar(60)
);
# Add DateTime in DB TO record down when the bid happened. 
alter table mybid add column datetime datetime not null;

create table university (
	name varchar(25) not null primary key,
	rank int,
	score float(4,2),
	type varchar(8) not null,
	location varchar (8) not null,
	pici varchar (10) not null
)
